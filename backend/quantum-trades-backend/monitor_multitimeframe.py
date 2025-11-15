#!/usr/bin/env python3
"""
Monitor Multi-Timeframe em Tempo Real
Magnus Wealth v9.0.0

Monitora múltiplos timeframes e calcula CHiLo em tempo real
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os

# Configurações
TIMEFRAMES = {
    '15m': '15m',
    '30m': '30m',
    '1h': '1h',
    '6h': '6h',
    '8h': '8h',
    '12h': '12h',
    '1d': '1d'
}

# Carregar criptomoedas do portfolio_config.json
from portfolio_manager import PortfolioManager

try:
    portfolio = PortfolioManager()
    CRIPTOS = [{'name': c['name'], 'yahoo': c['yahoo'], 'period': c['period_chilo']} 
               for c in portfolio.obter_criptos_ativas()]
    print(f"✅ Carregadas {len(CRIPTOS)} criptomoedas ativas do portfolio_config.json")
except Exception as e:
    print(f"⚠️ Erro ao carregar portfolio_config.json: {e}")
    print("⚠️ Usando lista padrão de criptomoedas")
    CRIPTOS = [
        {'name': 'Bitcoin', 'yahoo': 'BTC-USD', 'period': 3},
        {'name': 'Ethereum', 'yahoo': 'ETH-USD', 'period': 45},
        {'name': 'Binance Coin', 'yahoo': 'BNB-USD', 'period': 70},
        {'name': 'Solana', 'yahoo': 'SOL-USD', 'period': 7},
        {'name': 'Chainlink', 'yahoo': 'LINK-USD', 'period': 40},
        {'name': 'Uniswap', 'yahoo': 'UNI7083-USD', 'period': 65},
        {'name': 'Algorand', 'yahoo': 'ALGO-USD', 'period': 40},
        {'name': 'VeChain', 'yahoo': 'VET-USD', 'period': 25}
    ]

# Arquivo de períodos otimizados (será gerado pelo coletor)
PERIODOS_FILE = 'ml_data_8anos/resumo_coleta_8anos.json'

class MonitorMultiTimeframe:
    """
    Monitora múltiplos timeframes em tempo real
    """
    
    def __init__(self):
        self.periodos_otimizados = self.carregar_periodos_otimizados()
    
    def carregar_periodos_otimizados(self) -> Dict:
        """
        Carrega períodos otimizados do arquivo gerado pelo coletor
        """
        if os.path.exists(PERIODOS_FILE):
            try:
                with open(PERIODOS_FILE, 'r') as f:
                    dados = json.load(f)
                    
                periodos = {}
                for cripto_data in dados:
                    cripto = cripto_data['cripto']
                    periodos[cripto] = {}
                    
                    for tf, info in cripto_data.get('timeframes', {}).items():
                        periodos[cripto][tf] = info.get('periodo_otimizado', 20)
                
                print(f"✓ Períodos otimizados carregados de {PERIODOS_FILE}")
                return periodos
                
            except Exception as e:
                print(f"⚠️ Erro ao carregar períodos otimizados: {e}")
        
        # Usar períodos padrão se arquivo não existe
        print(f"⚠️ Usando períodos padrão")
        return {}
    
    def buscar_dados_timeframe(self, yahoo_symbol: str, interval: str, period: str = '7d') -> pd.DataFrame:
        """
        Busca dados de um timeframe específico
        """
        try:
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(interval=interval, period=period)
            
            if df.empty:
                return None
            
            df.columns = [c.lower() for c in df.columns]
            return df
            
        except Exception as e:
            print(f"   ❌ Erro ao buscar {yahoo_symbol} ({interval}): {e}")
            return None
    
    def calcular_chilo(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """
        Calcula CHiLo (Custom HiLo) - Modo Activator
        """
        if len(df) < period:
            return df
        
        # Calcular médias móveis
        hima = df['high'].rolling(window=period).mean()
        loma = df['low'].rolling(window=period).mean()
        
        # Inicializar séries
        hilo = pd.Series(index=df.index, dtype=float)
        hilo_state = pd.Series(index=df.index, dtype=int)
        
        # Calcular estado e linha HiLo
        for i in range(period, len(df)):
            close = df['close'].iloc[i]
            hi = hima.iloc[i-1]
            lo = loma.iloc[i-1]
            
            if close > hi:
                state = 1  # BULLISH (verde)
                hilo.iloc[i] = lo
            elif close < lo:
                state = -1  # BEARISH (vermelho)
                hilo.iloc[i] = hi
            else:
                state = 0  # NEUTRO
                hilo.iloc[i] = hilo.iloc[i-1] if i > period else lo
            
            hilo_state.iloc[i] = state
        
        df['hilo'] = hilo
        df['hilo_state'] = hilo_state
        
        return df
    
    def contar_candles_virados(self, df: pd.DataFrame) -> int:
        """
        Conta quantos candles consecutivos estão virados na mesma direção
        """
        if 'hilo_state' not in df.columns or len(df) == 0:
            return 0
        
        estado_atual = df['hilo_state'].iloc[-1]
        
        if estado_atual == 0:
            return 0
        
        # Contar quantos candles anteriores têm o mesmo estado
        count = 1
        for i in range(len(df)-2, -1, -1):
            if df['hilo_state'].iloc[i] == estado_atual:
                count += 1
            else:
                break
        
        return count
    
    def monitorar_cripto(self, cripto: Dict) -> Dict:
        """
        Monitora uma criptomoeda em todos os timeframes
        """
        nome = cripto['name']
        yahoo = cripto['yahoo']
        
        print(f"\n📊 Monitorando {nome}...")
        
        resultado = {
            'cripto': nome,
            'yahoo': yahoo,
            'timestamp': datetime.now().isoformat(),
            'timeframes': {}
        }
        
        # Para cada timeframe
        for tf_name, tf_interval in TIMEFRAMES.items():
            # Obter período otimizado ou usar padrão
            if nome in self.periodos_otimizados and tf_name in self.periodos_otimizados[nome]:
                period = self.periodos_otimizados[nome][tf_name]
            else:
                period = cripto['period']  # Período padrão do diário
            
            # Buscar dados
            df = self.buscar_dados_timeframe(yahoo, tf_interval)
            
            if df is None or len(df) < period:
                print(f"   ⚠️ {tf_name}: Dados insuficientes")
                continue
            
            # Calcular CHiLo
            df = self.calcular_chilo(df, period)
            
            # Estado atual
            estado = int(df['hilo_state'].iloc[-1])
            preco = float(df['close'].iloc[-1])
            
            # Contar candles virados
            candles_virados = self.contar_candles_virados(df)
            
            # Salvar resultado
            resultado['timeframes'][tf_name] = {
                'periodo': period,
                'estado': estado,
                'preco': preco,
                'candles_virados': candles_virados,
                'tendencia': 'Verde' if estado == 1 else ('Vermelho' if estado == -1 else 'Neutro')
            }
            
            print(f"   ✓ {tf_name}: {resultado['timeframes'][tf_name]['tendencia']} ({candles_virados} candles)")
        
        return resultado
    
    def monitorar_todas(self) -> Dict:
        """
        Monitora todas as criptomoedas em todos os timeframes
        """
        print("=" * 80)
        print("MONITOR MULTI-TIMEFRAME - MAGNUS WEALTH v9.0.0")
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        resultados = {}
        
        for cripto in CRIPTOS:
            resultado = self.monitorar_cripto(cripto)
            resultados[cripto['name']] = resultado
        
        print(f"\n✅ Monitoramento concluído: {len(resultados)} criptos")
        
        return resultados
    
    def gerar_features_ml(self, resultado_cripto: Dict) -> Dict:
        """
        Gera features para o modelo ML a partir do monitoramento
        """
        features = {}
        
        for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
            if tf in resultado_cripto['timeframes']:
                tf_data = resultado_cripto['timeframes'][tf]
                features[f'{tf}_estado'] = tf_data['estado']
                features[f'{tf}_candles_virados'] = tf_data['candles_virados']
            else:
                features[f'{tf}_estado'] = 0
                features[f'{tf}_candles_virados'] = 0
        
        return features
    
    def verificar_alinhamento_timeframes(self, resultado_cripto: Dict, min_alinhados: int = 5) -> bool:
        """
        Verifica se timeframes estão alinhados na mesma direção
        
        Args:
            resultado_cripto: Resultado do monitoramento
            min_alinhados: Mínimo de timeframes que devem estar alinhados
        
        Returns:
            True se >= min_alinhados timeframes estão na mesma direção
        """
        estados = []
        
        for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
            if tf in resultado_cripto['timeframes']:
                estado = resultado_cripto['timeframes'][tf]['estado']
                if estado != 0:  # Ignorar neutros
                    estados.append(estado)
        
        if len(estados) < min_alinhados:
            return False
        
        # Verificar se todos são positivos ou todos negativos
        positivos = sum(1 for e in estados if e > 0)
        negativos = sum(1 for e in estados if e < 0)
        
        return positivos >= min_alinhados or negativos >= min_alinhados


def exemplo_uso():
    """
    Exemplo de uso do monitor
    """
    monitor = MonitorMultiTimeframe()
    
    # Monitorar todas as criptos
    resultados = monitor.monitorar_todas()
    
    # Gerar features para ML
    print("\n" + "=" * 80)
    print("FEATURES PARA ML")
    print("=" * 80)
    
    for cripto, resultado in resultados.items():
        features = monitor.gerar_features_ml(resultado)
        alinhado = monitor.verificar_alinhamento_timeframes(resultado)
        
        print(f"\n🪙 {cripto}:")
        print(f"   Timeframes alinhados? {'✅ SIM' if alinhado else '❌ NÃO'}")
        print(f"   Features:")
        for key, value in features.items():
            print(f"      {key}: {value}")


if __name__ == '__main__':
    exemplo_uso()
