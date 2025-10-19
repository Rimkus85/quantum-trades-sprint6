#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Criptomoedas - Custom HiLo Indicator (Parize)
Magnus Wealth - Versão 8.0.0
"""

import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

# Top 15 Criptomoedas
TOP_15 = [
    {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'emoji': '🥇', 'period': 70, 'tier': 1},
    {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'emoji': '🥈', 'period': 60, 'tier': 1},
    {'symbol': 'BNBUSDT', 'name': 'Binance Coin', 'emoji': '🟡', 'period': 50, 'tier': 2},
    {'symbol': 'SOLUSDT', 'name': 'Solana', 'emoji': '🟣', 'period': 40, 'tier': 2},
    {'symbol': 'XRPUSDT', 'name': 'XRP', 'emoji': '💧', 'period': 65, 'tier': 2},
    {'symbol': 'ADAUSDT', 'name': 'Cardano', 'emoji': '🔵', 'period': 55, 'tier': 2},
    {'symbol': 'AVAXUSDT', 'name': 'Avalanche', 'emoji': '🔺', 'period': 45, 'tier': 3},
    {'symbol': 'DOTUSDT', 'name': 'Polkadot', 'emoji': '⚪', 'period': 50, 'tier': 3},
    {'symbol': 'MATICUSDT', 'name': 'Polygon', 'emoji': '🟣', 'period': 45, 'tier': 3},
    {'symbol': 'LINKUSDT', 'name': 'Chainlink', 'emoji': '🔗', 'period': 55, 'tier': 3},
    {'symbol': 'LTCUSDT', 'name': 'Litecoin', 'emoji': '⚡', 'period': 65, 'tier': 3},
    {'symbol': 'UNIUSDT', 'name': 'Uniswap', 'emoji': '🦄', 'period': 50, 'tier': 3},
    {'symbol': 'ATOMUSDT', 'name': 'Cosmos', 'emoji': '⚛️', 'period': 55, 'tier': 3},
    {'symbol': 'ALGOUSDT', 'name': 'Algorand', 'emoji': '🔷', 'period': 50, 'tier': 3},
    {'symbol': 'VETUSDT', 'name': 'VeChain', 'emoji': '🌿', 'period': 60, 'tier': 3},
]

def buscar_dados(symbol, limit=500):
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': '1d', 'limit': limit}
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    df = pd.DataFrame(data, columns=['time','o','h','l','c','v','ct','qv','t','tb','tq','i'])
    df['c'] = df['c'].astype(float)
    df['h'] = df['h'].astype(float)
    df['l'] = df['l'].astype(float)
    return df

def calcular_hilo(df, period):
    df['hilo_high'] = df['h'].rolling(period).mean()
    df['hilo_low'] = df['l'].rolling(period).mean()
    df['trend'] = 'verde'
    for i in range(1, len(df)):
        if df['c'].iloc[i] > df['hilo_high'].iloc[i-1]:
            df.loc[df.index[i], 'trend'] = 'verde'
        elif df['c'].iloc[i] < df['hilo_low'].iloc[i-1]:
            df.loc[df.index[i], 'trend'] = 'vermelho'
        else:
            df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
    return df

def calcular_performance(df, days=None):
    if days:
        df = df.tail(days)
    capital = 100.0
    pos = None
    entrada = 0
    for i in range(1, len(df)):
        t_atual = df['trend'].iloc[i]
        t_ant = df['trend'].iloc[i-1]
        preco = df['c'].iloc[i]
        if t_ant != t_atual:
            if pos == 'comprado':
                capital *= (1 + (preco - entrada) / entrada)
            elif pos == 'vendido':
                capital *= (1 + (entrada - preco) / entrada)
            pos = 'comprado' if t_atual == 'verde' else 'vendido'
            entrada = preco
    preco_final = df['c'].iloc[-1]
    if pos == 'comprado':
        capital *= (1 + (preco_final - entrada) / entrada)
    elif pos == 'vendido':
        capital *= (1 + (entrada - preco_final) / entrada)
    return {'capital': capital, 'retorno': ((capital - 100) / 100) * 100}

def analisar(cripto):
    df = buscar_dados(cripto['symbol'])
    df = calcular_hilo(df, cripto['period'])
    trend = df['trend'].iloc[-1]
    trend_ant = df['trend'].iloc[-2]
    preco = df['c'].iloc[-1]
    mudanca = (trend != trend_ant)
    sinal = 'COMPRA' if (mudanca and trend == 'verde') else 'VENDA' if (mudanca and trend == 'vermelho') else 'MANTER'
    p_total = calcular_performance(df)
    p_6m = calcular_performance(df, 180)
    p_90d = calcular_performance(df, 90)
    p_30d = calcular_performance(df, 30)
    return {
        'name': cripto['name'],
        'symbol': cripto['symbol'],
        'emoji': cripto['emoji'],
        'preco': preco,
        'period': cripto['period'],
        'tier': cripto['tier'],
        'sinal': sinal,
        'mudanca': mudanca,
        'p_total': p_total,
        'p_6m': p_6m,
        'p_90d': p_90d,
        'p_30d': p_30d
    }

def enviar_telegram(msg):
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
    with TelegramClient('magnus_session', api_id, api_hash) as client:
        client.send_message(group_id, msg)

if __name__ == '__main__':
    print('Analisador Custom HiLo (Parize) - v8.0.0')
    for c in TOP_15:
        print(f"Analisando {c['name']}...")
