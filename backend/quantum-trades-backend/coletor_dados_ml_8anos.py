#!/usr/bin/env python3
"""
Coletor de Dados Multi-Timeframe para ML - 8 ANOS
Magnus Wealth v9.0.0

Coleta dados históricos de 8 anos em múltiplos timeframes para treinamento do modelo ML
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import time

# Timeframes a serem analisados
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
    CRIPTOS = [{'name': c['name'], 'yahoo': c['yahoo']} for c in portfolio.obter_criptos_ativas()]
    print(f"✅ Carregadas {len(CRIPTOS)} criptomoedas ativas do portfolio_config.json")
except Exception as e:
    print(f"⚠️ Erro ao carregar portfolio_config.json: {e}")
    print("⚠️ Usando lista padrão de criptomoedas")
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

# Períodos CHiLo para testar
PERIODOS_TESTE = list(range(3, 71))  # 3 a 70

# Diretório para salvar dados
DATA_DIR = 'ml_data_8anos'
os.makedirs(DATA_DIR, exist_ok=True)


def buscar_dados_timeframe(yahoo_symbol: str, interval: str) -> pd.DataFrame:
    """
    Busca dados históricos de um timeframe específico - MÁXIMO DISPONÍVEL (8+ anos)
    
    Args:
        yahoo_symbol: Símbolo no Yahoo Finance
        interval: Intervalo (15m, 30m, 1h, etc)
    
    Returns:
        DataFrame com dados históricos
    """
    try:
        print(f"   📊 Buscando {yahoo_symbol} ({interval})...")
        
        ticker = yf.Ticker(yahoo_symbol)
        
        # Yahoo Finance tem limites por intervalo
        if interval in ['15m', '30m']:
            # Máximo 60 dias para intervalos curtos
            period = '60d'
        elif interval in ['1h']:
            # Máximo 730 dias para 1h
            period = '730d'
        else:
            # Máximo disponível para intervalos maiores (geralmente 8-10 anos)
            period = 'max'
        
        df = ticker.history(interval=interval, period=period)
        
        if df.empty:
            print(f"   ⚠️ Sem dados para {yahoo_symbol} ({interval})")
            return None
        
        # Renomear colunas
        df.columns = [c.lower() for c in df.columns]
        
        # Calcular período de dados em anos
        dias = (df.index[-1] - df.index[0]).days
        anos = dias / 365.25
        
        print(f"   ✓ {len(df)} candles obtidos ({anos:.1f} anos de dados)")
        return df
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return None


def calcular_chilo(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Calcula CHiLo (Custom HiLo) - Modo Activator
    
    Args:
        df: DataFrame com dados OHLCV
        period: Período do CHiLo
    
    Returns:
        DataFrame com colunas hilo e hilo_state adicionadas
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


def contar_candles_virados(df: pd.DataFrame) -> List[int]:
    """
    Conta quantos candles consecutivos estão virados na mesma direção
    
    Args:
        df: DataFrame com coluna hilo_state
    
    Returns:
        Lista com contagem de candles virados para cada posição
    """
    if 'hilo_state' not in df.columns:
        return []
    
    contagem = []
    
    for i in range(len(df)):
        estado_atual = df['hilo_state'].iloc[i]
        
        if estado_atual == 0:
            contagem.append(0)
            continue
        
        # Contar quantos candles anteriores têm o mesmo estado
        count = 1
        for j in range(i-1, -1, -1):
            if df['hilo_state'].iloc[j] == estado_atual:
                count += 1
            else:
                break
        
        contagem.append(count)
    
    return contagem


def otimizar_periodo_timeframe(yahoo_symbol: str, interval: str) -> Tuple[int, float]:
    """
    Encontra o período CHiLo mais vencedor para um timeframe
    
    Args:
        yahoo_symbol: Símbolo no Yahoo Finance
        interval: Intervalo (15m, 30m, 1h, etc)
    
    Returns:
        (melhor_periodo, taxa_acerto)
    """
    print(f"\n🔍 Otimizando período para {yahoo_symbol} ({interval})...")
    
    # Buscar dados
    df = buscar_dados_timeframe(yahoo_symbol, interval)
    if df is None or len(df) < 100:
        return None, None
    
    melhor_periodo = None
    melhor_taxa = 0
    
    for periodo in PERIODOS_TESTE:
        if len(df) < periodo * 2:
            continue
        
        # Calcular CHiLo
        df_test = df.copy()
        df_test = calcular_chilo(df_test, periodo)
        
        # Calcular taxa de acerto
        estados = df_test['hilo_state'].dropna()
        
        if len(estados) < 10:
            continue
        
        # Contar acertos (quando estado prevê corretamente o próximo movimento)
        acertos = 0
        total = 0
        
        for i in range(len(estados) - 1):
            if estados.iloc[i] == 0:
                continue
            
            preco_atual = df_test['close'].iloc[i]
            preco_proximo = df_test['close'].iloc[i+1]
            
            # Se estado é 1 (verde), espera-se que preço suba
            # Se estado é -1 (vermelho), espera-se que preço caia
            if estados.iloc[i] == 1 and preco_proximo > preco_atual:
                acertos += 1
            elif estados.iloc[i] == -1 and preco_proximo < preco_atual:
                acertos += 1
            
            total += 1
        
        if total > 0:
            taxa = acertos / total
            
            if taxa > melhor_taxa:
                melhor_taxa = taxa
                melhor_periodo = periodo
    
    if melhor_periodo:
        print(f"   ✓ Melhor período: {melhor_periodo} (taxa: {melhor_taxa:.2%})")
    else:
        print(f"   ⚠️ Nenhum período encontrado")
    
    return melhor_periodo, melhor_taxa


def coletar_dados_cripto(cripto: Dict) -> Dict:
    """
    Coleta dados de todos os timeframes para uma criptomoeda
    
    Args:
        cripto: Dicionário com informações da cripto
    
    Returns:
        Dicionário com dados coletados
    """
    print(f"\n{'='*80}")
    print(f"📊 COLETANDO DADOS: {cripto['name']}")
    print(f"{'='*80}")
    
    resultado = {
        'cripto': cripto['name'],
        'yahoo': cripto['yahoo'],
        'timestamp': datetime.now().isoformat(),
        'timeframes': {}
    }
    
    # Para cada timeframe
    for tf_name, tf_interval in TIMEFRAMES.items():
        print(f"\n⏱️ Timeframe: {tf_name}")
        
        # Otimizar período
        melhor_periodo, taxa_acerto = otimizar_periodo_timeframe(
            cripto['yahoo'], 
            tf_interval
        )
        
        if melhor_periodo is None:
            continue
        
        # Buscar dados com período otimizado
        df = buscar_dados_timeframe(cripto['yahoo'], tf_interval)
        if df is None:
            continue
        
        # Calcular CHiLo com período otimizado
        df = calcular_chilo(df, melhor_periodo)
        
        # Contar candles virados
        candles_virados = contar_candles_virados(df)
        df['candles_virados'] = candles_virados
        
        # Calcular período de dados
        dias = (df.index[-1] - df.index[0]).days
        anos = dias / 365.25
        
        # Salvar dados do timeframe
        resultado['timeframes'][tf_name] = {
            'periodo_otimizado': melhor_periodo,
            'taxa_acerto': taxa_acerto,
            'total_candles': len(df),
            'data_inicio': df.index[0].isoformat(),
            'data_fim': df.index[-1].isoformat(),
            'dias_dados': dias,
            'anos_dados': round(anos, 2)
        }
        
        # Salvar DataFrame
        filename = f"{DATA_DIR}/{cripto['name']}_{tf_name}.csv"
        df.to_csv(filename)
        print(f"   💾 Salvo: {filename}")
        
        # Aguardar para não sobrecarregar API
        time.sleep(2)
    
    return resultado


def gerar_dataset_ml():
    """
    Gera dataset para treinamento do modelo ML
    Combina dados de todos os timeframes para prever inversão do diário
    
    Dataset com 8 anos de dados históricos para treinamento robusto
    """
    print(f"\n{'='*80}")
    print("🤖 GERANDO DATASET PARA ML (8 ANOS DE DADOS)")
    print(f"{'='*80}")
    
    dataset = []
    
    for cripto in CRIPTOS:
        print(f"\n📊 Processando {cripto['name']}...")
        
        # Carregar dados do diário
        try:
            df_diario = pd.read_csv(f"{DATA_DIR}/{cripto['name']}_1d.csv", index_col=0, parse_dates=True)
        except:
            print(f"   ⚠️ Dados diários não encontrados")
            continue
        
        # Para cada dia
        for i in range(1, len(df_diario)):
            data_atual = df_diario.index[i]
            
            # Verificar se houve inversão no diário
            estado_anterior = df_diario['hilo_state'].iloc[i-1]
            estado_atual = df_diario['hilo_state'].iloc[i]
            
            if estado_anterior == 0 or estado_atual == 0:
                continue
            
            virou = (estado_anterior != estado_atual)
            
            # Coletar features de todos os timeframes
            features = {
                'cripto': cripto['name'],
                'data': data_atual.isoformat(),
                'virou_diario': virou
            }
            
            # Para cada timeframe menor que diário
            for tf_name in ['15m', '30m', '1h', '6h', '8h', '12h']:
                try:
                    df_tf = pd.read_csv(
                        f"{DATA_DIR}/{cripto['name']}_{tf_name}.csv", 
                        index_col=0, 
                        parse_dates=True
                    )
                    
                    # Pegar dados até a data atual
                    df_tf_ate_data = df_tf[df_tf.index <= data_atual]
                    
                    if len(df_tf_ate_data) == 0:
                        continue
                    
                    # Última linha
                    ultima = df_tf_ate_data.iloc[-1]
                    
                    features[f'{tf_name}_estado'] = int(ultima['hilo_state'])
                    features[f'{tf_name}_candles_virados'] = int(ultima['candles_virados'])
                    
                except:
                    features[f'{tf_name}_estado'] = 0
                    features[f'{tf_name}_candles_virados'] = 0
            
            dataset.append(features)
    
    # Salvar dataset
    df_dataset = pd.DataFrame(dataset)
    filename = f"{DATA_DIR}/dataset_ml_inversao_8anos.csv"
    df_dataset.to_csv(filename, index=False)
    
    print(f"\n✓ Dataset salvo: {filename}")
    print(f"✓ Total de amostras: {len(df_dataset)}")
    print(f"✓ Inversões detectadas: {df_dataset['virou_diario'].sum()}")
    print(f"✓ Período de dados: 8 anos (máximo histórico disponível)")
    
    # Estatísticas do dataset
    if len(df_dataset) > 0:
        taxa_inversao = (df_dataset['virou_diario'].sum() / len(df_dataset)) * 100
        print(f"✓ Taxa de inversão: {taxa_inversao:.2f}%")
        
        # Estatísticas por cripto
        print(f"\n📊 Estatísticas por Cripto:")
        for cripto in CRIPTOS:
            df_cripto = df_dataset[df_dataset['cripto'] == cripto['name']]
            if len(df_cripto) > 0:
                inversoes = df_cripto['virou_diario'].sum()
                taxa = (inversoes / len(df_cripto)) * 100
                print(f"   {cripto['name']}: {len(df_cripto)} amostras, {inversoes} inversões ({taxa:.1f}%)")
    
    return df_dataset


def main():
    """
    Função principal
    """
    print("=" * 80)
    print("COLETOR DE DADOS MULTI-TIMEFRAME PARA ML - 8 ANOS")
    print("Magnus Wealth v9.0.0")
    print("=" * 80)
    print("\n⚠️ ATENÇÃO: Este processo pode levar 1-2 HORAS")
    print("   Coletando máximo de dados históricos disponíveis (8+ anos)")
    print("=" * 80)
    
    resultados = []
    
    # Coletar dados de cada cripto
    for cripto in CRIPTOS:
        resultado = coletar_dados_cripto(cripto)
        resultados.append(resultado)
        
        # Aguardar entre criptos
        time.sleep(5)
    
    # Salvar resumo
    resumo_file = f"{DATA_DIR}/resumo_coleta_8anos.json"
    with open(resumo_file, 'w') as f:
        json.dump(resultados, f, indent=2)
    
    print(f"\n✓ Resumo salvo: {resumo_file}")
    
    # Gerar dataset para ML
    dataset = gerar_dataset_ml()
    
    print("\n" + "=" * 80)
    print("✅ COLETA CONCLUÍDA!")
    print("=" * 80)
    print(f"\n📁 Arquivos salvos em: {DATA_DIR}/")
    print(f"📊 Total de criptos: {len(CRIPTOS)}")
    print(f"⏱️ Total de timeframes: {len(TIMEFRAMES)}")
    print(f"🤖 Dataset ML: {len(dataset)} amostras")
    print(f"📅 Período: 8 anos de dados históricos")


if __name__ == '__main__':
    main()
