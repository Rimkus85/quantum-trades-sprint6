"""
Monitor de Performance - Magnus Wealth v8.3.0
Monitora performance real vs esperada e detecta necessidade de reversão
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

# Configuração
STOP_LOSS_PCT = -5.0  # -5% vs período anterior
DIAS_MONITORAMENTO = 30  # 30 dias de validação

class MonitorPerformance:
    """Monitora performance das mudanças aplicadas"""
    
    def __init__(self):
        self.config_file = '/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/mudancas_monitoradas.json'
        self.mudancas = self._carregar_mudancas()
    
    def _carregar_mudancas(self) -> List[Dict]:
        """Carrega mudanças em monitoramento"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return []
    
    def _salvar_mudancas(self):
        """Salva mudanças em monitoramento"""
        with open(self.config_file, 'w') as f:
            json.dump(self.mudancas, f, indent=2)
    
    def registrar_mudanca(self, cripto: str, yahoo_symbol: str, periodo_anterior: int, 
                         periodo_novo: int, retorno_esperado: float):
        """Registra nova mudança para monitoramento"""
        mudanca = {
            'cripto': cripto,
            'yahoo_symbol': yahoo_symbol,
            'periodo_anterior': periodo_anterior,
            'periodo_novo': periodo_novo,
            'retorno_esperado': retorno_esperado,
            'data_inicio': datetime.now().strftime('%Y-%m-%d'),
            'dias_monitorados': 0,
            'status': 'ATIVO',
            'performance_acumulada': 0.0
        }
        
        self.mudancas.append(mudanca)
        self._salvar_mudancas()
        print(f"✅ {cripto} registrado para monitoramento (30 dias)")
    
    def calcular_chilo(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calcula indicador CHiLo"""
        df['hilo_high'] = df['high'].rolling(window=period).mean()
        df['hilo_low'] = df['low'].rolling(window=period).mean()
        
        df['trend'] = 0
        for i in range(period, len(df)):
            if df['close'].iloc[i] > df['hilo_high'].iloc[i]:
                df.loc[df.index[i], 'trend'] = 1  # Bullish
            elif df['close'].iloc[i] < df['hilo_low'].iloc[i]:
                df.loc[df.index[i], 'trend'] = -1  # Bearish
            else:
                df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
        
        return df
    
    def calcular_performance(self, yahoo_symbol: str, period: int, days: int) -> Dict:
        """Calcula performance de um período específico"""
        try:
            ticker = yf.Ticker(yahoo_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days+period+10)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                return None
            
            df.columns = df.columns.str.lower()
            df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            df = df.dropna()
            
            # Calcular CHiLo
            df = self.calcular_chilo(df, period)
            df = df.iloc[period:].copy()
            df = df.tail(days)
            
            # Calcular retorno
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['returns'] * df['trend'].shift(1)
            
            retorno_total = (1 + df['strategy_returns']).prod() - 1
            retorno_pct = retorno_total * 100
            
            # Contar trades
            df['signal'] = df['trend'].diff()
            num_trades = (df['signal'] != 0).sum()
            
            # Calcular custo
            TAXA_TAKER = 0.0005
            custo_total = num_trades * TAXA_TAKER
            retorno_liquido = (retorno_total - custo_total) * 100
            
            return {
                'retorno_bruto': retorno_pct,
                'retorno_liquido': retorno_liquido,
                'num_trades': num_trades,
                'custo_total': custo_total * 100
            }
        except Exception as e:
            print(f"❌ Erro ao calcular performance: {str(e)[:100]}")
            return None
    
    def monitorar_mudancas(self) -> Dict:
        """Monitora todas as mudanças ativas"""
        resultados = {
            'ok': [],
            'alerta': [],
            'reverter': []
        }
        
        for mudanca in self.mudancas:
            if mudanca['status'] != 'ATIVO':
                continue
            
            # Calcular dias desde início
            data_inicio = datetime.strptime(mudanca['data_inicio'], '%Y-%m-%d')
            dias_passados = (datetime.now() - data_inicio).days
            
            if dias_passados > DIAS_MONITORAMENTO:
                mudanca['status'] = 'CONCLUIDO'
                mudanca['dias_monitorados'] = dias_passados
                resultados['ok'].append({
                    'cripto': mudanca['cripto'],
                    'status': 'VALIDADO',
                    'mensagem': f"Período de monitoramento concluído ({dias_passados} dias)"
                })
                continue
            
            # Calcular performance atual
            perf_novo = self.calcular_performance(
                mudanca['yahoo_symbol'], 
                mudanca['periodo_novo'], 
                dias_passados
            )
            
            perf_anterior = self.calcular_performance(
                mudanca['yahoo_symbol'], 
                mudanca['periodo_anterior'], 
                dias_passados
            )
            
            if not perf_novo or not perf_anterior:
                continue
            
            # Comparar performances
            diferenca = perf_novo['retorno_liquido'] - perf_anterior['retorno_liquido']
            mudanca['performance_acumulada'] = diferenca
            mudanca['dias_monitorados'] = dias_passados
            
            # Verificar stop-loss
            if diferenca <= STOP_LOSS_PCT:
                mudanca['status'] = 'REVERTER'
                resultados['reverter'].append({
                    'cripto': mudanca['cripto'],
                    'periodo_novo': mudanca['periodo_novo'],
                    'periodo_anterior': mudanca['periodo_anterior'],
                    'diferenca': diferenca,
                    'perf_novo': perf_novo['retorno_liquido'],
                    'perf_anterior': perf_anterior['retorno_liquido'],
                    'dias_monitorados': dias_passados,
                    'mensagem': f"🚨 STOP-LOSS ATINGIDO! Diferença: {diferenca:.2f}%"
                })
            elif diferenca < 0:
                resultados['alerta'].append({
                    'cripto': mudanca['cripto'],
                    'periodo_novo': mudanca['periodo_novo'],
                    'periodo_anterior': mudanca['periodo_anterior'],
                    'diferenca': diferenca,
                    'perf_novo': perf_novo['retorno_liquido'],
                    'perf_anterior': perf_anterior['retorno_liquido'],
                    'dias_monitorados': dias_passados,
                    'mensagem': f"⚠️ Performance negativa: {diferenca:.2f}%"
                })
            else:
                resultados['ok'].append({
                    'cripto': mudanca['cripto'],
                    'periodo_novo': mudanca['periodo_novo'],
                    'diferenca': diferenca,
                    'perf_novo': perf_novo['retorno_liquido'],
                    'dias_monitorados': dias_passados,
                    'mensagem': f"✅ Performance positiva: {diferenca:+.2f}%"
                })
        
        self._salvar_mudancas()
        return resultados
    
    def gerar_relatorio(self, resultados: Dict) -> str:
        """Gera relatório de monitoramento"""
        msg = "\n" + "="*60 + "\n"
        msg += "📊 RELATÓRIO DE MONITORAMENTO DE PERFORMANCE\n"
        msg += f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += "="*60 + "\n\n"
        
        # Mudanças OK
        if resultados['ok']:
            msg += "✅ **PERFORMANCE POSITIVA**\n\n"
            for r in resultados['ok']:
                msg += f"🥇 **{r['cripto']}**\n"
                if 'periodo_novo' in r:
                    msg += f"   Período: {r['periodo_novo']}\n"
                    msg += f"   Performance: {r['perf_novo']:+.2f}%\n"
                    msg += f"   Diferença vs anterior: {r['diferenca']:+.2f}%\n"
                    msg += f"   Dias monitorados: {r['dias_monitorados']}/{DIAS_MONITORAMENTO}\n"
                msg += f"   {r['mensagem']}\n\n"
        
        # Alertas
        if resultados['alerta']:
            msg += "⚠️ **ALERTAS** (Performance negativa mas dentro do stop-loss)\n\n"
            for r in resultados['alerta']:
                msg += f"⚠️ **{r['cripto']}**\n"
                msg += f"   Período novo: {r['periodo_novo']}\n"
                msg += f"   Performance novo: {r['perf_novo']:+.2f}%\n"
                msg += f"   Performance anterior: {r['perf_anterior']:+.2f}%\n"
                msg += f"   Diferença: {r['diferenca']:+.2f}%\n"
                msg += f"   Stop-loss: {STOP_LOSS_PCT}%\n"
                msg += f"   Dias monitorados: {r['dias_monitorados']}/{DIAS_MONITORAMENTO}\n"
                msg += f"   {r['mensagem']}\n\n"
        
        # Reversões necessárias
        if resultados['reverter']:
            msg += "🚨 **REVERSÕES NECESSÁRIAS** (Stop-loss atingido)\n\n"
            for r in resultados['reverter']:
                msg += f"🚨 **{r['cripto']}** - REVERTER IMEDIATAMENTE!\n"
                msg += f"   Período atual: {r['periodo_novo']}\n"
                msg += f"   Reverter para: {r['periodo_anterior']}\n"
                msg += f"   Performance atual: {r['perf_novo']:+.2f}%\n"
                msg += f"   Performance anterior: {r['perf_anterior']:+.2f}%\n"
                msg += f"   Diferença: {r['diferenca']:+.2f}% (stop-loss: {STOP_LOSS_PCT}%)\n"
                msg += f"   Dias monitorados: {r['dias_monitorados']}\n"
                msg += f"   {r['mensagem']}\n\n"
        
        # Resumo
        msg += "="*60 + "\n"
        msg += "📊 **RESUMO**\n\n"
        msg += f"   ✅ Performance positiva: {len(resultados['ok'])}\n"
        msg += f"   ⚠️ Alertas: {len(resultados['alerta'])}\n"
        msg += f"   🚨 Reversões necessárias: {len(resultados['reverter'])}\n"
        msg += "="*60 + "\n"
        
        return msg
    
    def limpar_concluidos(self):
        """Remove mudanças concluídas do monitoramento"""
        self.mudancas = [m for m in self.mudancas if m['status'] == 'ATIVO']
        self._salvar_mudancas()

if __name__ == "__main__":
    # Teste do monitor
    monitor = MonitorPerformance()
    
    # Registrar mudanças recentes para monitoramento
    print("Registrando mudanças para monitoramento...")
    
    # Bitcoin: 40 → 3
    monitor.registrar_mudanca('Bitcoin', 'BTC-USD', 40, 3, 11.7)
    
    # Ethereum: 50 → 45
    monitor.registrar_mudanca('Ethereum', 'ETH-USD', 50, 45, 0.95)
    
    # Solana: 45 → 7
    monitor.registrar_mudanca('Solana', 'SOL-USD', 45, 7, 31.48)
    
    print("\nMonitorando performance...")
    resultados = monitor.monitorar_mudancas()
    
    print(monitor.gerar_relatorio(resultados))
