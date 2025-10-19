#!/usr/bin/env python3
"""
Analisador de Criptomoedas - Estratégia HiLo Activator
Magnus Wealth - Versão 7.9.0
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import json

load_dotenv()

# Top 15 Criptomoedas (atualizado mensalmente)
TOP_15_CRIPTOS = [
    {'symbol': 'BTCUSDT', 'name': 'Bitcoin', 'emoji': '🥇', 'hilo_period': 70, 'tier': 1},
    {'symbol': 'ETHUSDT', 'name': 'Ethereum', 'emoji': '🥈', 'hilo_period': 60, 'tier': 1},
    {'symbol': 'BNBUSDT', 'name': 'Binance Coin', 'emoji': '🟡', 'hilo_period': 50, 'tier': 2},
    {'symbol': 'SOLUSDT', 'name': 'Solana', 'emoji': '🟣', 'hilo_period': 40, 'tier': 2},
    {'symbol': 'XRPUSDT', 'name': 'XRP', 'emoji': '💧', 'hilo_period': 65, 'tier': 2},
    {'symbol': 'ADAUSDT', 'name': 'Cardano', 'emoji': '🔵', 'hilo_period': 55, 'tier': 2},
    {'symbol': 'AVAXUSDT', 'name': 'Avalanche', 'emoji': '🔺', 'hilo_period': 45, 'tier': 3},
    {'symbol': 'DOTUSDT', 'name': 'Polkadot', 'emoji': '⚪', 'hilo_period': 50, 'tier': 3},
    {'symbol': 'MATICUSDT', 'name': 'Polygon', 'emoji': '🟣', 'hilo_period': 45, 'tier': 3},
    {'symbol': 'LINKUSDT', 'name': 'Chainlink', 'emoji': '🔗', 'hilo_period': 55, 'tier': 3},
    {'symbol': 'LTCUSDT', 'name': 'Litecoin', 'emoji': '⚡', 'hilo_period': 65, 'tier': 3},
    {'symbol': 'UNIUSDT', 'name': 'Uniswap', 'emoji': '🦄', 'hilo_period': 50, 'tier': 3},
    {'symbol': 'ATOMUSDT', 'name': 'Cosmos', 'emoji': '⚛️', 'hilo_period': 55, 'tier': 3},
    {'symbol': 'ALGOUSDT', 'name': 'Algorand', 'emoji': '🔷', 'hilo_period': 50, 'tier': 3},
    {'symbol': 'VETUSDT', 'name': 'VeChain', 'emoji': '🌿', 'hilo_period': 60, 'tier': 3},
]

print("Analisador criado com sucesso!")
