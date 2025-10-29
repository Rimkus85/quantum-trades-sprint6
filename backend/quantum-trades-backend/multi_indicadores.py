"""
Sistema Multi-Indicadores - Magnus Wealth v8.4.0
Combina CHiLo com RSI, MACD e Bollinger Bands
Sistema de votação para sinais mais robustos
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class MultiIndicadores:
    """
    Sistema que combina múltiplos indicadores técnicos
    """
    
    def __init__(self):
        # Pesos dos indicadores (soma = 1.0)
        self.pesos = {
            'chilo': 0.40,      # 40% - Indicador principal
            'rsi': 0.20,        # 20%
            'macd': 0.20,       # 20%
            'bollinger': 0.20   # 20%
        }
    
    def calcular_chilo(self, df: pd.DataFrame, period: int) -> pd.DataFrame:
        """Calcula CHiLo (Custom HiLo)"""
        df['hilo_high'] = df['high'].rolling(window=period).mean()
        df['hilo_low'] = df['low'].rolling(window=period).mean()
        
        df['chilo_trend'] = 0
        for i in range(period, len(df)):
            if df['close'].iloc[i] > df['hilo_high'].iloc[i]:
                df.loc[df.index[i], 'chilo_trend'] = 1  # Bullish
            elif df['close'].iloc[i] < df['hilo_low'].iloc[i]:
                df.loc[df.index[i], 'chilo_trend'] = -1  # Bearish
            else:
                df.loc[df.index[i], 'chilo_trend'] = df['chilo_trend'].iloc[i-1]
        
        return df
    
    def calcular_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula RSI (Relative Strength Index)
        Sinal: RSI > 70 = Sobrecomprado (vender)
               RSI < 30 = Sobrevendido (comprar)
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Sinal: 1 (comprar), 0 (neutro), -1 (vender)
        df['rsi_signal'] = 0
        df.loc[df['rsi'] < 30, 'rsi_signal'] = 1   # Sobrevendido = Comprar
        df.loc[df['rsi'] > 70, 'rsi_signal'] = -1  # Sobrecomprado = Vender
        
        return df
    
    def calcular_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calcula MACD (Moving Average Convergence Divergence)
        Sinal: MACD > Signal = Bullish (comprar)
               MACD < Signal = Bearish (vender)
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Sinal: 1 (comprar), 0 (neutro), -1 (vender)
        df['macd_trend'] = 0
        df.loc[df['macd'] > df['macd_signal'], 'macd_trend'] = 1   # Bullish
        df.loc[df['macd'] < df['macd_signal'], 'macd_trend'] = -1  # Bearish
        
        return df
    
    def calcular_bollinger(self, df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
        """
        Calcula Bollinger Bands
        Sinal: Preço < Banda Inferior = Comprar
               Preço > Banda Superior = Vender
        """
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        df['bb_std'] = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (std * df['bb_std'])
        
        # Sinal: 1 (comprar), 0 (neutro), -1 (vender)
        df['bb_signal'] = 0
        df.loc[df['close'] < df['bb_lower'], 'bb_signal'] = 1   # Abaixo da banda = Comprar
        df.loc[df['close'] > df['bb_upper'], 'bb_signal'] = -1  # Acima da banda = Vender
        
        return df
    
    def calcular_todos_indicadores(self, df: pd.DataFrame, chilo_period: int) -> pd.DataFrame:
        """Calcula todos os indicadores"""
        df = self.calcular_chilo(df, chilo_period)
        df = self.calcular_rsi(df)
        df = self.calcular_macd(df)
        df = self.calcular_bollinger(df)
        return df
    
    def votacao_ponderada(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sistema de votação ponderada
        Combina sinais de todos os indicadores
        """
        # Calcular voto ponderado
        df['voto_total'] = (
            df['chilo_trend'] * self.pesos['chilo'] +
            df['rsi_signal'] * self.pesos['rsi'] +
            df['macd_trend'] * self.pesos['macd'] +
            df['bb_signal'] * self.pesos['bollinger']
        )
        
        # Sinal final: 1 (comprar), 0 (neutro), -1 (vender)
        df['sinal_final'] = 0
        df.loc[df['voto_total'] > 0.3, 'sinal_final'] = 1   # Maioria bullish
        df.loc[df['voto_total'] < -0.3, 'sinal_final'] = -1  # Maioria bearish
        
        # Força do sinal (0-100%)
        df['forca_sinal'] = abs(df['voto_total']) * 100
        
        return df
    
    def analisar_cripto(self, yahoo_symbol: str, chilo_period: int, days: int = 90) -> Dict:
        """
        Analisa criptomoeda com multi-indicadores
        """
        try:
            # Buscar dados
            ticker = yf.Ticker(yahoo_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days+60)  # +60 para warmup
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                return None
            
            df.columns = df.columns.str.lower()
            df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            df = df.dropna()
            
            # Calcular todos os indicadores
            df = self.calcular_todos_indicadores(df, chilo_period)
            
            # Sistema de votação
            df = self.votacao_ponderada(df)
            
            # Limitar aos últimos N dias
            df = df.tail(days)
            
            # Calcular performance
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['returns'] * df['sinal_final'].shift(1)
            
            retorno_total = (1 + df['strategy_returns']).prod() - 1
            retorno_pct = retorno_total * 100
            
            # Contar trades
            df['signal_change'] = df['sinal_final'].diff()
            num_trades = (df['signal_change'] != 0).sum()
            
            # Calcular custos
            TAXA_TAKER = 0.0005
            custo_total = num_trades * TAXA_TAKER
            retorno_liquido = (retorno_total - custo_total) * 100
            
            # Análise de acurácia
            trades = df[df['signal_change'] != 0].copy()
            if len(trades) > 0:
                trades['price_entry'] = trades['close']
                trades['price_exit'] = trades['close'].shift(-1)
                trades['trade_return'] = (trades['price_exit'] - trades['price_entry']) / trades['price_entry']
                trades['correct'] = ((trades['signal_change'] > 0) & (trades['trade_return'] > 0)) | \
                                   ((trades['signal_change'] < 0) & (trades['trade_return'] < 0))
                acuracia = trades['correct'].sum() / len(trades) * 100
            else:
                acuracia = 0
            
            # Sharpe Ratio
            volatilidade = df['strategy_returns'].std() * np.sqrt(252)
            sharpe = (retorno_liquido / 100 * (365/days)) / volatilidade if volatilidade > 0 else 0
            
            # Análise de concordância entre indicadores
            concordancia = {
                'chilo_rsi': ((df['chilo_trend'] == df['rsi_signal']) & (df['chilo_trend'] != 0)).sum() / len(df) * 100,
                'chilo_macd': ((df['chilo_trend'] == df['macd_trend']) & (df['chilo_trend'] != 0)).sum() / len(df) * 100,
                'chilo_bb': ((df['chilo_trend'] == df['bb_signal']) & (df['chilo_trend'] != 0)).sum() / len(df) * 100,
                'todos': ((df['chilo_trend'] == df['rsi_signal']) & 
                         (df['chilo_trend'] == df['macd_trend']) & 
                         (df['chilo_trend'] == df['bb_signal']) & 
                         (df['chilo_trend'] != 0)).sum() / len(df) * 100
            }
            
            # Sinal atual
            sinal_atual = df['sinal_final'].iloc[-1]
            forca_atual = df['forca_sinal'].iloc[-1]
            
            return {
                'retorno_bruto': retorno_pct,
                'retorno_liquido': retorno_liquido,
                'num_trades': num_trades,
                'custo_total': custo_total * 100,
                'acuracia': acuracia,
                'sharpe': sharpe,
                'sinal_atual': sinal_atual,
                'forca_sinal': forca_atual,
                'concordancia': concordancia,
                'indicadores_atuais': {
                    'chilo': df['chilo_trend'].iloc[-1],
                    'rsi': df['rsi_signal'].iloc[-1],
                    'macd': df['macd_trend'].iloc[-1],
                    'bollinger': df['bb_signal'].iloc[-1]
                }
            }
        except Exception as e:
            print(f"❌ Erro ao analisar: {str(e)[:100]}")
            return None
    
    def comparar_chilo_vs_multi(self, yahoo_symbol: str, chilo_period: int, days: int = 90) -> Dict:
        """
        Compara performance CHiLo sozinho vs Multi-indicadores
        """
        # Analisar com multi-indicadores
        resultado_multi = self.analisar_cripto(yahoo_symbol, chilo_period, days)
        
        # Analisar com CHiLo apenas
        try:
            ticker = yf.Ticker(yahoo_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days+chilo_period+10)
            df = ticker.history(start=start_date, end=end_date)
            
            df.columns = df.columns.str.lower()
            df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            df = df.dropna()
            
            df = self.calcular_chilo(df, chilo_period)
            df = df.tail(days)
            
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['returns'] * df['chilo_trend'].shift(1)
            
            retorno_total = (1 + df['strategy_returns']).prod() - 1
            
            df['signal_change'] = df['chilo_trend'].diff()
            num_trades = (df['signal_change'] != 0).sum()
            
            TAXA_TAKER = 0.0005
            custo_total = num_trades * TAXA_TAKER
            retorno_liquido_chilo = (retorno_total - custo_total) * 100
            
            resultado_chilo = {
                'retorno_liquido': retorno_liquido_chilo,
                'num_trades': num_trades
            }
        except:
            resultado_chilo = None
        
        if resultado_multi and resultado_chilo:
            diferenca = resultado_multi['retorno_liquido'] - resultado_chilo['retorno_liquido']
            return {
                'multi': resultado_multi,
                'chilo': resultado_chilo,
                'diferenca': diferenca,
                'multi_melhor': diferenca > 0
            }
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SISTEMA MULTI-INDICADORES - Magnus Wealth v8.4.0")
    print("="*60)
    
    multi = MultiIndicadores()
    
    # Testar com Bitcoin
    print("\n🥇 BITCOIN - CHiLo 3 vs Multi-Indicadores")
    print("="*60)
    
    comparacao = multi.comparar_chilo_vs_multi('BTC-USD', 3, days=90)
    
    if comparacao:
        print(f"\n📊 RESULTADOS (90 dias):")
        print(f"\n   CHiLo Apenas:")
        print(f"      Retorno líquido: {comparacao['chilo']['retorno_liquido']:+.2f}%")
        print(f"      Trades: {comparacao['chilo']['num_trades']}")
        
        print(f"\n   Multi-Indicadores:")
        print(f"      Retorno líquido: {comparacao['multi']['retorno_liquido']:+.2f}%")
        print(f"      Trades: {comparacao['multi']['num_trades']}")
        print(f"      Acurácia: {comparacao['multi']['acuracia']:.1f}%")
        print(f"      Sharpe: {comparacao['multi']['sharpe']:.2f}")
        
        print(f"\n   Diferença: {comparacao['diferenca']:+.2f}%")
        
        if comparacao['multi_melhor']:
            print(f"   ✅ Multi-indicadores é MELHOR")
        else:
            print(f"   ⚠️  CHiLo sozinho é melhor")
        
        print(f"\n   Concordância entre indicadores:")
        for ind, valor in comparacao['multi']['concordancia'].items():
            print(f"      {ind}: {valor:.1f}%")
        
        print(f"\n   Sinal atual: {comparacao['multi']['sinal_atual']}")
        print(f"   Força do sinal: {comparacao['multi']['forca_sinal']:.1f}%")
        
        print(f"\n   Indicadores atuais:")
        for ind, sinal in comparacao['multi']['indicadores_atuais'].items():
            emoji = "🟢" if sinal == 1 else "🔴" if sinal == -1 else "⚪"
            print(f"      {emoji} {ind}: {sinal}")
