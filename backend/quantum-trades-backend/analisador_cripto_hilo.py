#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Criptomoedas - Gann HiLo Activator (Implementação Correta)
Magnus Wealth - Versão 8.2.0

ATUALIZAÇÃO: Top 11 Criptos com Períodos Otimizados
Data: 19/10/2025
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

# Top 11 Criptomoedas com Períodos Otimizados (Simulação 2025)
TOP_11 = [
    {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'emoji': '🥇', 'period': 45, 'tier': 1, 'alocacao': 0.25},
    {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'emoji': '🥈', 'period': 25, 'tier': 1, 'alocacao': 0.25},
    {'symbol': 'BNBUSDT', 'name': 'Binance Coin', 'emoji': '🟡', 'period': 30, 'tier': 2, 'alocacao': 0.10},
    {'symbol': 'SOLUSDT', 'name': 'Solana', 'emoji': '🟣', 'period': 25, 'tier': 2, 'alocacao': 0.10},
    {'symbol': 'XRPUSDT', 'name': 'XRP', 'emoji': '💧', 'period': 55, 'tier': 2, 'alocacao': 0.10},
    {'symbol': 'LINKUSDT', 'name': 'Chainlink', 'emoji': '🔗', 'period': 30, 'tier': 3, 'alocacao': 0.05},
    {'symbol': 'LTCUSDT', 'name': 'Litecoin', 'emoji': '⚡', 'period': 25, 'tier': 3, 'alocacao': 0.05},
    {'symbol': 'UNIUSDT', 'name': 'Uniswap', 'emoji': '🦄', 'period': 20, 'tier': 3, 'alocacao': 0.05},
    {'symbol': 'ATOMUSDT', 'name': 'Cosmos', 'emoji': '⚛️', 'period': 35, 'tier': 3, 'alocacao': 0.05},
    {'symbol': 'ALGOUSDT', 'name': 'Algorand', 'emoji': '🔷', 'period': 25, 'tier': 3, 'alocacao': 0.05},
    {'symbol': 'VETUSDT', 'name': 'VeChain', 'emoji': '🌿', 'period': 35, 'tier': 3, 'alocacao': 0.05},
]

def buscar_dados(symbol, limit=500):
    """
    Busca dados históricos da Binance
    Fallback: Usa CoinGecko se Binance estiver bloqueada
    """
    # Tentar Binance primeiro
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {'symbol': symbol, 'interval': '1d', 'limit': limit}
        r = requests.get(url, params=params, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data, columns=['time','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore'])
                df['close'] = df['close'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                return df
    except Exception as e:
        print(f"Erro ao buscar dados da Binance: {e}")
    
    # Fallback: CoinGecko
    print(f"Usando CoinGecko como fallback para {symbol}...")
    
    # Mapear símbolos Binance para IDs CoinGecko
    coingecko_ids = {
        'BTCUSDT': 'bitcoin',
        'ETHUSDT': 'ethereum',
        'BNBUSDT': 'binancecoin',
        'SOLUSDT': 'solana',
        'XRPUSDT': 'ripple',
        'LINKUSDT': 'chainlink',
        'LTCUSDT': 'litecoin',
        'UNIUSDT': 'uniswap',
        'ATOMUSDT': 'cosmos',
        'ALGOUSDT': 'algorand',
        'VETUSDT': 'vechain'
    }
    
    coin_id = coingecko_ids.get(symbol)
    if not coin_id:
        raise ValueError(f"Símbolo {symbol} não mapeado para CoinGecko")
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    # CoinGecko aceita: 1, 7, 14, 30, 90, 180, 365, max
    if limit <= 7:
        days = 7
    elif limit <= 30:
        days = 30
    elif limit <= 90:
        days = 90
    elif limit <= 180:
        days = 180
    else:
        days = 365
    
    params = {'vs_currency': 'usd', 'days': days}
    
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    
    data = r.json()
    
    # CoinGecko retorna: [timestamp, open, high, low, close]
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['volume'] = 0  # CoinGecko OHLC não inclui volume
    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
    
    return df

def calcular_gann_hilo_activator(df, period, ma_type='SMA'):
    """
    Calcula o Gann HiLo Activator - IMPLEMENTAÇÃO CORRETA
    
    Fórmula matemática:
    
    1. Calcular SMAt-1(H,n) e SMAt-1(L,n)
    
    2. HiLot(n) = {
        1   se Ct > SMAt-1(H,n)      # BULLISH
        0   se SMAt-1(L,n) ≤ Ct ≤ SMAt-1(H,n)  # NEUTRO
       -1   se Ct < SMAt-1(L,n)      # BEARISH
    }
    
    3. GHLAt(n) = {
        SMAt-1(L,n)    se HiLot(n) = 1   # Plota SMA dos lows
        GHLAt-1(n)     se HiLot(n) = 0   # Mantém valor anterior
        SMAt-1(H,n)    se HiLot(n) = -1  # Plota SMA dos highs
    }
    
    Referência: Sierra Chart, ThinkOrSwim, TradingView
    """
    # Calcular médias móveis dos highs e lows
    if ma_type == 'SMA':
        hima = df['high'].rolling(window=period).mean()
        loma = df['low'].rolling(window=period).mean()
    elif ma_type == 'EMA':
        hima = df['high'].ewm(span=period, adjust=False).mean()
        loma = df['low'].ewm(span=period, adjust=False).mean()
    else:
        raise ValueError(f"Tipo de MA não suportado: {ma_type}")
    
    # Inicializar arrays
    hilo_state = pd.Series(0, index=df.index, dtype=int)
    ghla = pd.Series(np.nan, index=df.index, dtype=float)
    
    # Calcular HiLot(n) e GHLAt(n) conforme fórmula matemática
    for i in range(period, len(df)):
        close = df['close'].iloc[i]
        hima_prev = hima.iloc[i-1]  # SMAt-1(H,n)
        loma_prev = loma.iloc[i-1]  # SMAt-1(L,n)
        
        # Determinar estado HiLot(n)
        if close > hima_prev:
            hilo_state.iloc[i] = 1  # BULLISH
        elif close < loma_prev:
            hilo_state.iloc[i] = -1  # BEARISH
        else:
            hilo_state.iloc[i] = 0  # NEUTRO
        
        # Calcular GHLAt(n)
        if hilo_state.iloc[i] == 1:
            ghla.iloc[i] = loma_prev  # Plota SMA dos lows
        elif hilo_state.iloc[i] == -1:
            ghla.iloc[i] = hima_prev  # Plota SMA dos highs
        else:
            ghla.iloc[i] = ghla.iloc[i-1]  # Mantém valor anterior
    
    # Determinar cor/tendência baseado no estado
    df['hilo_state'] = hilo_state
    df['ghla'] = ghla
    df['trend'] = df['hilo_state'].map({1: 'verde', -1: 'vermelho', 0: None})
    
    # Preencher valores None com a tendência anterior
    df['trend'] = df['trend'].ffill()
    
    return df

def calcular_performance(df, days=None):
    """
    Calcula performance da estratégia HiLo com R$ 100 sem alavancagem
    
    Lógica:
    - Verde = COMPRA
    - Virar vermelho = ZERA + VENDE
    - Vermelho = VENDA
    - Virar verde = ZERA + COMPRA
    """
    if days:
        df = df.tail(days).copy()
    
    capital = 100.0
    posicao = None  # 'comprado' ou 'vendido'
    preco_entrada = 0
    
    for i in range(1, len(df)):
        trend_atual = df['trend'].iloc[i]
        trend_anterior = df['trend'].iloc[i-1]
        preco = df['close'].iloc[i]
        
        # Detectar mudança de tendência
        if trend_anterior != trend_atual:
            # Zerar posição anterior
            if posicao == 'comprado':
                # Realizar lucro/prejuízo da posição comprada
                capital *= (1 + (preco - preco_entrada) / preco_entrada)
            elif posicao == 'vendido':
                # Realizar lucro/prejuízo da posição vendida
                capital *= (1 + (preco_entrada - preco) / preco_entrada)
            
            # Entrar na nova posição
            if trend_atual == 'verde':
                posicao = 'comprado'
                preco_entrada = preco
            elif trend_atual == 'vermelho':
                posicao = 'vendido'
                preco_entrada = preco
    
    # Fechar posição final
    preco_final = df['close'].iloc[-1]
    if posicao == 'comprado':
        capital *= (1 + (preco_final - preco_entrada) / preco_entrada)
    elif posicao == 'vendido':
        capital *= (1 + (preco_entrada - preco_final) / preco_entrada)
    
    retorno_percentual = ((capital - 100) / 100) * 100
    
    return {
        'capital': capital,
        'retorno': retorno_percentual
    }

def analisar_cripto(cripto):
    """
    Analisa uma criptomoeda usando o Gann HiLo Activator
    """
    print(f"Analisando {cripto['name']} ({cripto['symbol']}) com período {cripto['period']}...")
    
    # Buscar dados
    df = buscar_dados(cripto['symbol'])
    
    # Calcular Gann HiLo Activator
    df = calcular_gann_hilo_activator(df, cripto['period'], ma_type='SMA')
    
    # Analisar situação atual
    if len(df) < 2:
        raise ValueError(f"Dados insuficientes para análise de {cripto['name']}")
    
    trend_atual = df['trend'].iloc[-1]
    trend_anterior = df['trend'].iloc[-2]
    preco_atual = df['close'].iloc[-1]
    ghla_atual = df['ghla'].iloc[-1]
    
    # Detectar mudança de tendência
    mudanca = (trend_atual != trend_anterior)
    
    # Determinar sinal
    if mudanca:
        if trend_atual == 'verde':
            sinal = 'COMPRA'
        elif trend_atual == 'vermelho':
            sinal = 'VENDA'
        else:
            sinal = 'MANTER'
    else:
        sinal = 'MANTER'
    
    # Calcular performances
    p_total = calcular_performance(df)
    p_6m = calcular_performance(df, 180)
    p_90d = calcular_performance(df, 90)
    p_30d = calcular_performance(df, 30)
    
    return {
        'name': cripto['name'],
        'symbol': cripto['symbol'],
        'emoji': cripto['emoji'],
        'preco': preco_atual,
        'ghla': ghla_atual,
        'period': cripto['period'],
        'tier': cripto['tier'],
        'alocacao': cripto['alocacao'],
        'trend': trend_atual,
        'sinal': sinal,
        'mudanca': mudanca,
        'p_total': p_total,
        'p_6m': p_6m,
        'p_90d': p_90d,
        'p_30d': p_30d
    }

def formatar_mensagem(resultados):
    """
    Formata mensagem para envio ao Telegram
    """
    msg = "🚀 *ANÁLISE DIÁRIA DE CRIPTOMOEDAS - GANN HILO ACTIVATOR*\n\n"
    msg += f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Agrupar por tier
    tier1 = [r for r in resultados if r['tier'] == 1]
    tier2 = [r for r in resultados if r['tier'] == 2]
    tier3 = [r for r in resultados if r['tier'] == 3]
    
    for tier_name, tier_list in [('🥇 TIER 1 - Blue Chips', tier1), 
                                   ('🥈 TIER 2 - Large Caps', tier2), 
                                   ('🥉 TIER 3 - Mid Caps', tier3)]:
        if tier_list:
            msg += f"*{tier_name}*\n\n"
            
            for r in tier_list:
                emoji_trend = '🟢' if r['trend'] == 'verde' else '🔴'
                emoji_sinal = '🚨' if r['mudanca'] else '➡️'
                
                msg += f"{r['emoji']} *{r['name']}* {emoji_trend}\n"
                msg += f"💰 Preço: ${r['preco']:,.2f}\n"
                msg += f"📊 Período HiLo: {r['period']}\n"
                msg += f"📈 Alocação: {r['alocacao']*100:.0f}%\n"
                msg += f"{emoji_sinal} Sinal: *{r['sinal']}*\n"
                
                if r['mudanca']:
                    msg += f"⚠️ *MUDANÇA DE TENDÊNCIA DETECTADA!*\n"
                
                msg += f"\n📈 *Performance com R$ 100:*\n"
                msg += f"• Desde início: R$ {r['p_total']['capital']:.2f} ({r['p_total']['retorno']:+.1f}%)\n"
                msg += f"• 6 meses: R$ {r['p_6m']['capital']:.2f} ({r['p_6m']['retorno']:+.1f}%)\n"
                msg += f"• 90 dias: R$ {r['p_90d']['capital']:.2f} ({r['p_90d']['retorno']:+.1f}%)\n"
                msg += f"• 30 dias: R$ {r['p_30d']['capital']:.2f} ({r['p_30d']['retorno']:+.1f}%)\n"
                msg += "\n"
            
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += "📚 *Lógica da Estratégia:*\n"
    msg += "🟢 Verde = COMPRA\n"
    msg += "🔴 Virar vermelho = ZERA + VENDE\n"
    msg += "🔴 Vermelho = VENDA\n"
    msg += "🟢 Virar verde = ZERA + COMPRA\n\n"
    
    msg += "⚠️ *Disclaimer:* Análise educacional. Não é recomendação de investimento.\n"
    msg += "📊 Indicador: Gann HiLo Activator (Robert Krausz)\n"
    msg += "🔧 Magnus Wealth v8.2.0 - Top 11 Otimizado\n"
    
    return msg

def enviar_telegram(msg):
    """
    Envia mensagem para o grupo do Telegram
    """
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
    
    with TelegramClient('magnus_session', api_id, api_hash) as client:
        client.send_message(group_id, msg, parse_mode='markdown')

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - ANALISADOR DE CRIPTOMOEDAS')
    print('  Gann HiLo Activator - v8.2.0')
    print('  TOP 11 CRIPTOS - PERÍODOS OTIMIZADOS')
    print('═══════════════════════════════════════════════════\n')
    
    resultados = []
    
    for cripto in TOP_11:
        try:
            resultado = analisar_cripto(cripto)
            resultados.append(resultado)
            print(f"✓ {cripto['name']}: {resultado['sinal']} - Tendência {resultado['trend']}")
        except Exception as e:
            print(f"✗ Erro ao analisar {cripto['name']}: {e}")
    
    print('\n' + '═'*50)
    print('Análise concluída!')
    print(f'Total de criptos analisadas: {len(resultados)}/{len(TOP_11)}')
    
    # Formatar e enviar mensagem
    if resultados:
        print('\nFormatando mensagem...')
        mensagem = formatar_mensagem(resultados)
        
        print('\nEnviando para Telegram...')
        try:
            enviar_telegram(mensagem)
            print('✓ Mensagem enviada com sucesso!')
        except Exception as e:
            print(f'✗ Erro ao enviar mensagem: {e}')
            print('\nMensagem que seria enviada:')
            print(mensagem)

