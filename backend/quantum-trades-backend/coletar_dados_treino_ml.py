"""
Coletor de Dados para Treinamento de ML
Magnus Wealth - Versão 1.0

Coleta dados históricos de 5 anos e testa todos os períodos
para criar dataset de treinamento do modelo de ML
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List
import time

# Configuração das criptomoedas
CRIPTOS = [
    {'name': 'Bitcoin', 'yahoo': 'BTC-USD'},
    {'name': 'Ethereum', 'yahoo': 'ETH-USD'},
    {'name': 'Binance Coin', 'yahoo': 'BNB-USD'},
    {'name': 'Solana', 'yahoo': 'SOL-USD'},
    {'name': 'Chainlink', 'yahoo': 'LINK-USD'},
    {'name': 'Uniswap', 'yahoo': 'UNI7083-USD'},
    {'name': 'Algorand', 'yahoo': 'ALGO-USD'},
    {'name': 'VeChain', 'yahoo': 'VET-USD'}
]

# Períodos para testar
PERIODOS = [3, 5, 7, 10, 12, 15, 18, 20, 22, 25, 28, 30, 33, 35, 38, 40, 45, 50, 55, 60]

# Janela de análise (dias)
JANELA_ANALISE = 90  # Analisar últimos 90 dias para cada ponto

def buscar_dados_historicos(yahoo_symbol: str, years: int = 5) -> pd.DataFrame:
    """
    Busca dados históricos do Yahoo Finance
    """
    try:
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period=f'{years}y')
        
        if df.empty:
            print(f"   ❌ Sem dados para {yahoo_symbol}")
            return None
        
        df.columns = [c.lower() for c in df.columns]
        print(f"   ✓ {len(df)} dias de dados obtidos")
        return df
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None

def calcular_chilo(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Calcula o CHiLo (Custom HiLo) - Modo Activator
    """
    df = df.copy()
    
    # Calcular médias móveis dos highs e lows
    hima = df['high'].rolling(window=period).mean()
    loma = df['low'].rolling(window=period).mean()
    
    # Inicializar série do HiLo
    hilo = pd.Series(index=df.index, dtype=float)
    hilo_state = pd.Series(index=df.index, dtype=int)
    
    # Calcular estado e linha HiLo
    for i in range(period, len(df)):
        close = df['close'].iloc[i]
        hi = hima.iloc[i-1]
        lo = loma.iloc[i-1]
        
        if close > hi:
            state = 1  # BULLISH
            hilo.iloc[i] = lo
        elif close < lo:
            state = -1  # BEARISH
            hilo.iloc[i] = hi
        else:
            state = 0  # NEUTRO
            hilo.iloc[i] = hilo.iloc[i-1] if i > period else lo
        
        hilo_state.iloc[i] = state
    
    df['hilo'] = hilo
    df['hilo_state'] = hilo_state
    
    return df

def calcular_score_periodo(df: pd.DataFrame, period: int) -> float:
    """
    Calcula score de um período específico
    """
    df_teste = calcular_chilo(df.copy(), period)
    df_teste = df_teste.dropna(subset=['hilo_state']).copy()
    
    if len(df_teste) < 10:
        return 0
    
    # Calcular retornos
    df_teste.loc[:, 'retorno_diario'] = df_teste['close'].pct_change()
    df_teste.loc[:, 'sinal'] = df_teste['hilo_state'].shift(1)
    df_teste.loc[:, 'estrategia_retorno'] = df_teste['sinal'] * df_teste['retorno_diario']
    df_teste = df_teste.dropna(subset=['estrategia_retorno'])
    
    if len(df_teste) < 10:
        return 0
    
    # Taxa de acerto
    acertos = (df_teste['estrategia_retorno'] > 0).sum()
    total = len(df_teste[df_teste['estrategia_retorno'] != 0])
    taxa_acerto = (acertos / total * 100) if total > 0 else 0
    
    # Sharpe
    retorno_medio = df_teste['estrategia_retorno'].mean()
    std_retorno = df_teste['estrategia_retorno'].std()
    sharpe = (retorno_medio / std_retorno * np.sqrt(252)) if std_retorno > 0 else 0
    
    # Retorno total
    retorno_total = (1 + df_teste['estrategia_retorno']).prod() - 1
    retorno_pct = retorno_total * 100
    retorno_bh = (df_teste['close'].iloc[-1] / df_teste['close'].iloc[0] - 1) * 100
    superacao = retorno_pct - retorno_bh
    
    # Score ponderado
    score_acerto = min(taxa_acerto / 70 * 100, 100)
    score_sharpe = min(sharpe / 1.5 * 100, 100)
    score_retorno = min(max(superacao / 20 * 100, 0), 100)
    
    score = (score_acerto * 0.40 + score_sharpe * 0.30 + score_retorno * 0.30)
    
    return round(score, 2)

def extrair_features(df: pd.DataFrame) -> Dict:
    """
    Extrai features do mercado para ML
    """
    # Garantir que temos dados suficientes
    if len(df) < 60:
        return None
    
    # Calcular ATR (Average True Range)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr_14 = true_range.rolling(14).mean().iloc[-1]
    
    # Volatilidade
    returns = df['close'].pct_change()
    std_20 = returns.rolling(20).std().iloc[-1]
    std_60 = returns.rolling(60).std().iloc[-1]
    volatility_ratio = std_20 / std_60 if std_60 > 0 else 1.0
    
    # Tendência (slope da MA50)
    ma_50 = df['close'].rolling(50).mean()
    if len(ma_50.dropna()) >= 2:
        ma_slope = (ma_50.iloc[-1] - ma_50.iloc[-10]) / 10 if len(ma_50) >= 10 else 0
    else:
        ma_slope = 0
    
    trend_strength = abs(ma_slope) / std_20 if std_20 > 0 else 0
    
    # Volume
    volume_ma_20 = df['volume'].rolling(20).mean()
    volume_ratio = df['volume'].iloc[-1] / volume_ma_20.iloc[-1] if volume_ma_20.iloc[-1] > 0 else 1.0
    
    # ROC (Rate of Change)
    roc_10 = ((df['close'].iloc[-1] / df['close'].iloc[-11]) - 1) * 100 if len(df) >= 11 else 0
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_14 = (100 - (100 / (1 + rs))).iloc[-1] if len(rs.dropna()) > 0 else 50
    
    # Autocorrelação
    if len(returns.dropna()) >= 10:
        autocorr_5 = returns.autocorr(lag=5)
        autocorr_10 = returns.autocorr(lag=10)
    else:
        autocorr_5 = 0
        autocorr_10 = 0
    
    features = {
        'atr_14': float(atr_14) if not np.isnan(atr_14) else 0,
        'std_20': float(std_20) if not np.isnan(std_20) else 0,
        'volatility_ratio': float(volatility_ratio) if not np.isnan(volatility_ratio) else 1.0,
        'ma_slope': float(ma_slope) if not np.isnan(ma_slope) else 0,
        'trend_strength': float(trend_strength) if not np.isnan(trend_strength) else 0,
        'volume_ratio': float(volume_ratio) if not np.isnan(volume_ratio) else 1.0,
        'roc_10': float(roc_10) if not np.isnan(roc_10) else 0,
        'rsi_14': float(rsi_14) if not np.isnan(rsi_14) else 50,
        'autocorr_5': float(autocorr_5) if not np.isnan(autocorr_5) else 0,
        'autocorr_10': float(autocorr_10) if not np.isnan(autocorr_10) else 0,
    }
    
    return features

def coletar_dados_cripto(cripto: Dict) -> List[Dict]:
    """
    Coleta dados de uma criptomoeda
    """
    print(f"\n{'='*60}")
    print(f"🔍 Coletando dados: {cripto['name']}")
    print(f"{'='*60}")
    
    # Buscar dados históricos
    df_completo = buscar_dados_historicos(cripto['yahoo'], years=5)
    if df_completo is None or len(df_completo) < 365:
        print(f"   ❌ Dados insuficientes (<1 ano)")
        return []
    
    print(f"   ✓ Período: {df_completo.index[0].date()} a {df_completo.index[-1].date()}")
    
    # Lista para armazenar amostras
    amostras = []
    
    # Iterar por janelas deslizantes (a cada 7 dias para reduzir volume)
    total_janelas = (len(df_completo) - JANELA_ANALISE) // 7
    print(f"   ✓ Analisando {total_janelas} janelas...")
    
    for i in range(0, len(df_completo) - JANELA_ANALISE, 7):  # A cada 7 dias
        # Pegar janela de análise
        df_janela = df_completo.iloc[i:i+JANELA_ANALISE].copy()
        
        if len(df_janela) < JANELA_ANALISE:
            continue
        
        # Extrair features
        features = extrair_features(df_janela)
        if features is None:
            continue
        
        # Testar todos os períodos
        scores = {}
        for periodo in PERIODOS:
            score = calcular_score_periodo(df_janela, periodo)
            scores[periodo] = score
        
        # Encontrar período ótimo
        periodo_otimo = max(scores, key=scores.get)
        score_otimo = scores[periodo_otimo]
        
        # Criar amostra
        amostra = {
            'cripto': cripto['name'],
            'data': df_janela.index[-1].strftime('%Y-%m-%d'),
            'periodo_otimo': periodo_otimo,
            'score_otimo': score_otimo,
            **features
        }
        
        amostras.append(amostra)
        
        # Progress
        if len(amostras) % 50 == 0:
            print(f"   ✓ {len(amostras)} amostras coletadas...")
    
    print(f"   ✅ Total: {len(amostras)} amostras")
    return amostras

def main():
    print('═══════════════════════════════════════════════════')
    print('  COLETOR DE DADOS PARA TREINAMENTO ML')
    print('  Magnus Wealth - Versão 1.0')
    print('═══════════════════════════════════════════════════\n')
    
    inicio = time.time()
    
    # Coletar dados de todas as criptos
    dataset_completo = []
    
    for cripto in CRIPTOS:
        amostras = coletar_dados_cripto(cripto)
        dataset_completo.extend(amostras)
        
        # Salvar parcialmente (backup)
        df_temp = pd.DataFrame(dataset_completo)
        df_temp.to_csv('/home/ubuntu/dataset_treino_temp.csv', index=False)
    
    # Criar DataFrame final
    df_final = pd.DataFrame(dataset_completo)
    
    # Estatísticas
    print(f"\n{'='*60}")
    print("📊 ESTATÍSTICAS DO DATASET")
    print(f"{'='*60}")
    print(f"Total de amostras: {len(df_final)}")
    print(f"Criptos: {df_final['cripto'].nunique()}")
    print(f"Período: {df_final['data'].min()} a {df_final['data'].max()}")
    print(f"\nDistribuição de períodos ótimos:")
    print(df_final['periodo_otimo'].value_counts().sort_index())
    print(f"\nScore médio: {df_final['score_otimo'].mean():.2f}")
    print(f"Score mínimo: {df_final['score_otimo'].min():.2f}")
    print(f"Score máximo: {df_final['score_otimo'].max():.2f}")
    
    # Salvar dataset final
    output_file = '/home/ubuntu/dataset_treino_ml.csv'
    df_final.to_csv(output_file, index=False)
    
    tempo_total = (time.time() - inicio) / 60
    print(f"\n✅ Dataset salvo em: {output_file}")
    print(f"📦 Tamanho: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    print(f"⏱️  Tempo total: {tempo_total:.1f} minutos")
    
    print("\n═══════════════════════════════════════════════════")
    print("✓ Coleta de dados concluída!")
    print("═══════════════════════════════════════════════════")

if __name__ == '__main__':
    main()

