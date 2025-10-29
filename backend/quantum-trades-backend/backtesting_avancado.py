"""
Backtesting Avançado - Magnus Wealth v8.4.0
Walk-forward optimization e simulação de estratégias alternativas
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class BacktestingAvancado:
    """
    Sistema de backtesting com walk-forward optimization
    """
    
    def __init__(self):
        self.TAXA_TAKER = 0.0005  # 0.05% por operação
    
    def calcular_chilo(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calcula CHiLo"""
        df['hilo_high'] = df['high'].rolling(window=period).mean()
        df['hilo_low'] = df['low'].rolling(window=period).mean()
        
        df['trend'] = 0
        for i in range(period, len(df)):
            if df['close'].iloc[i] > df['hilo_high'].iloc[i]:
                df.loc[df.index[i], 'trend'] = 1
            elif df['close'].iloc[i] < df['hilo_low'].iloc[i]:
                df.loc[df.index[i], 'trend'] = -1
            else:
                df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
        
        return df
    
    def backtest_simples(self, df: pd.DataFrame, period: int) -> Dict:
        """
        Backtest simples de um período
        """
        df = df.copy()
        df = self.calcular_chilo(df, period)
        df = df.iloc[period:].copy()
        
        # Calcular retornos
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['returns'] * df['trend'].shift(1)
        
        # Contar trades
        df['signal_change'] = df['trend'].diff()
        num_trades = (df['signal_change'] != 0).sum()
        
        # Calcular métricas
        retorno_total = (1 + df['strategy_returns']).prod() - 1
        custo_total = num_trades * self.TAXA_TAKER
        retorno_liquido = retorno_total - custo_total
        
        # Drawdown
        cumulative = (1 + df['strategy_returns']).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative / running_max) - 1
        max_drawdown = drawdown.min()
        
        # Sharpe
        volatilidade = df['strategy_returns'].std() * np.sqrt(252)
        sharpe = (retorno_liquido * (252/len(df))) / volatilidade if volatilidade > 0 else 0
        
        # Win rate
        trades_df = df[df['signal_change'] != 0].copy()
        if len(trades_df) > 0:
            trades_df['price_entry'] = trades_df['close']
            trades_df['price_exit'] = trades_df['close'].shift(-1)
            trades_df['trade_return'] = (trades_df['price_exit'] - trades_df['price_entry']) / trades_df['price_entry']
            trades_df['win'] = trades_df['trade_return'] > 0
            win_rate = trades_df['win'].sum() / len(trades_df) * 100
        else:
            win_rate = 0
        
        return {
            'retorno_bruto': retorno_total * 100,
            'retorno_liquido': retorno_liquido * 100,
            'num_trades': num_trades,
            'custo_total': custo_total * 100,
            'max_drawdown': max_drawdown * 100,
            'sharpe': sharpe,
            'win_rate': win_rate,
            'volatilidade': volatilidade * 100
        }
    
    def walk_forward_optimization(self, yahoo_symbol: str, periodos: List[int], 
                                  training_days: int = 180, testing_days: int = 90,
                                  num_windows: int = 4) -> Dict:
        """
        Walk-forward optimization
        
        Divide dados em múltiplas janelas:
        - Treina em N dias
        - Testa nos próximos M dias
        - Repete processo avançando no tempo
        """
        print(f"\n🔄 Walk-Forward Optimization: {yahoo_symbol}")
        print(f"   Janelas: {num_windows}")
        print(f"   Treino: {training_days} dias | Teste: {testing_days} dias")
        
        # Buscar dados
        total_days = (training_days + testing_days) * num_windows + 100
        ticker = yf.Ticker(yahoo_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=total_days)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        df.columns = df.columns.str.lower()
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df = df.dropna()
        
        resultados_windows = []
        
        # Para cada janela
        for i in range(num_windows):
            # Definir período de treino e teste
            train_start = i * testing_days
            train_end = train_start + training_days
            test_start = train_end
            test_end = test_start + testing_days
            
            if test_end > len(df):
                break
            
            df_train = df.iloc[train_start:train_end].copy()
            df_test = df.iloc[test_start:test_end].copy()
            
            print(f"\n   Janela {i+1}/{num_windows}:")
            print(f"      Treino: {len(df_train)} dias")
            print(f"      Teste: {len(df_test)} dias")
            
            # Otimizar no período de treino
            melhor_periodo = None
            melhor_score = -999999
            
            for periodo in periodos:
                resultado_train = self.backtest_simples(df_train, periodo)
                if resultado_train:
                    # Score = Retorno líquido / Max Drawdown
                    score = resultado_train['retorno_liquido'] / abs(resultado_train['max_drawdown']) if resultado_train['max_drawdown'] != 0 else resultado_train['retorno_liquido']
                    
                    if score > melhor_score:
                        melhor_score = score
                        melhor_periodo = periodo
            
            print(f"      Melhor período (treino): {melhor_periodo}")
            
            # Testar no período de teste
            resultado_test = self.backtest_simples(df_test, melhor_periodo)
            
            if resultado_test:
                print(f"      Retorno teste: {resultado_test['retorno_liquido']:+.2f}%")
                
                resultados_windows.append({
                    'janela': i + 1,
                    'periodo_otimo': melhor_periodo,
                    'resultado_train': self.backtest_simples(df_train, melhor_periodo),
                    'resultado_test': resultado_test
                })
        
        # Consolidar resultados
        if not resultados_windows:
            return None
        
        # Métricas agregadas
        retornos_test = [r['resultado_test']['retorno_liquido'] for r in resultados_windows]
        retorno_medio = np.mean(retornos_test)
        retorno_std = np.std(retornos_test)
        
        # Consistência (quantas janelas foram positivas)
        janelas_positivas = sum(1 for r in retornos_test if r > 0)
        consistencia = janelas_positivas / len(retornos_test) * 100
        
        # Período mais frequente
        periodos_escolhidos = [r['periodo_otimo'] for r in resultados_windows]
        periodo_mais_frequente = max(set(periodos_escolhidos), key=periodos_escolhidos.count)
        
        return {
            'yahoo_symbol': yahoo_symbol,
            'num_windows': len(resultados_windows),
            'resultados_windows': resultados_windows,
            'retorno_medio_test': retorno_medio,
            'retorno_std_test': retorno_std,
            'consistencia': consistencia,
            'periodo_mais_frequente': periodo_mais_frequente,
            'periodos_escolhidos': periodos_escolhidos
        }
    
    def comparar_estrategias(self, yahoo_symbol: str, days: int = 365) -> Dict:
        """
        Compara diferentes estratégias de trading
        """
        print(f"\n📊 Comparando Estratégias: {yahoo_symbol}")
        
        # Buscar dados
        ticker = yf.Ticker(yahoo_symbol)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days+100)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        df.columns = df.columns.str.lower()
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df = df.dropna()
        df = df.tail(days)
        
        estrategias = {}
        
        # 1. Buy & Hold
        retorno_bh = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        estrategias['buy_hold'] = {
            'retorno': retorno_bh,
            'trades': 0,
            'custo': 0
        }
        
        # 2. CHiLo período curto (7)
        resultado_7 = self.backtest_simples(df, 7)
        estrategias['chilo_7'] = resultado_7
        
        # 3. CHiLo período médio (25)
        resultado_25 = self.backtest_simples(df, 25)
        estrategias['chilo_25'] = resultado_25
        
        # 4. CHiLo período longo (50)
        resultado_50 = self.backtest_simples(df, 50)
        estrategias['chilo_50'] = resultado_50
        
        # Ranking
        ranking = sorted(estrategias.items(), 
                        key=lambda x: x[1].get('retorno_liquido', x[1]['retorno']), 
                        reverse=True)
        
        return {
            'yahoo_symbol': yahoo_symbol,
            'periodo': days,
            'estrategias': estrategias,
            'ranking': ranking
        }
    
    def gerar_relatorio_walkforward(self, resultado: Dict) -> str:
        """Gera relatório de walk-forward"""
        if not resultado:
            return "❌ Sem dados disponíveis"
        
        msg = f"\n{'='*60}\n"
        msg += f"🔄 WALK-FORWARD OPTIMIZATION: {resultado['yahoo_symbol']}\n"
        msg += f"{'='*60}\n\n"
        
        msg += f"**CONFIGURAÇÃO:**\n"
        msg += f"   Janelas testadas: {resultado['num_windows']}\n"
        msg += f"   Período mais frequente: {resultado['periodo_mais_frequente']}\n"
        msg += f"   Períodos escolhidos: {resultado['periodos_escolhidos']}\n\n"
        
        msg += f"**RESULTADOS AGREGADOS:**\n"
        msg += f"   Retorno médio (teste): {resultado['retorno_medio_test']:+.2f}%\n"
        msg += f"   Desvio padrão: {resultado['retorno_std_test']:.2f}%\n"
        msg += f"   Consistência: {resultado['consistencia']:.1f}% janelas positivas\n\n"
        
        msg += f"**DETALHES POR JANELA:**\n"
        for r in resultado['resultados_windows']:
            msg += f"\n   Janela {r['janela']}:\n"
            msg += f"      Período: {r['periodo_otimo']}\n"
            msg += f"      Retorno treino: {r['resultado_train']['retorno_liquido']:+.2f}%\n"
            msg += f"      Retorno teste: {r['resultado_test']['retorno_liquido']:+.2f}%\n"
            msg += f"      Trades teste: {r['resultado_test']['num_trades']}\n"
        
        msg += f"\n{'='*60}\n"
        
        return msg
    
    def gerar_relatorio_estrategias(self, resultado: Dict) -> str:
        """Gera relatório de comparação de estratégias"""
        if not resultado:
            return "❌ Sem dados disponíveis"
        
        msg = f"\n{'='*60}\n"
        msg += f"📊 COMPARAÇÃO DE ESTRATÉGIAS: {resultado['yahoo_symbol']}\n"
        msg += f"Período: {resultado['periodo']} dias\n"
        msg += f"{'='*60}\n\n"
        
        msg += f"**RANKING:**\n"
        for i, (nome, metricas) in enumerate(resultado['ranking'], 1):
            retorno = metricas.get('retorno_liquido', metricas.get('retorno', 0))
            msg += f"\n   {i}. {nome.upper()}: {retorno:+.2f}%\n"
            
            if 'num_trades' in metricas:
                msg += f"      Trades: {metricas['num_trades']}\n"
                msg += f"      Custo: {metricas['custo_total']:.2f}%\n"
                msg += f"      Max Drawdown: {metricas['max_drawdown']:.2f}%\n"
                msg += f"      Sharpe: {metricas['sharpe']:.2f}\n"
                msg += f"      Win Rate: {metricas['win_rate']:.1f}%\n"
        
        msg += f"\n{'='*60}\n"
        
        return msg

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BACKTESTING AVANÇADO - Magnus Wealth v8.4.0")
    print("="*60)
    
    backtest = BacktestingAvancado()
    
    # Walk-forward optimization
    periodos_teste = [3, 7, 10, 15, 20, 25, 30, 40, 50]
    resultado_wf = backtest.walk_forward_optimization(
        'BTC-USD', 
        periodos_teste,
        training_days=180,
        testing_days=90,
        num_windows=3
    )
    
    if resultado_wf:
        print(backtest.gerar_relatorio_walkforward(resultado_wf))
    
    # Comparar estratégias
    resultado_comp = backtest.comparar_estrategias('BTC-USD', days=365)
    
    if resultado_comp:
        print(backtest.gerar_relatorio_estrategias(resultado_comp))
