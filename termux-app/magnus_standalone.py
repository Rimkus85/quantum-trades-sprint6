#!/usr/bin/env python3
"""
Magnus Wealth - Standalone Trading Bot
Roda 100% no Termux, sem depender de servidor externo
"""

import os
import requests
import pandas as pd
import yfinance as yf
from binance.client import Client
from datetime import datetime, timedelta
import schedule
import time

# ═══════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════

# Binance API (cole suas chaves aqui)
BINANCE_API_KEY = "SUA_API_KEY_AQUI"
BINANCE_API_SECRET = "SUA_API_SECRET_AQUI"

# Telegram (opcional)
TELEGRAM_BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

# Capital inicial
CAPITAL_INICIAL = 2000  # USD

# TOP 8 Criptos otimizadas
CRIPTOS = [
    {"nome": "Bitcoin", "symbol": "BTCUSDT", "ticker_yahoo": "BTC-USD", "periodo": 40, "tier": 1, "alocacao": 0.25},
    {"nome": "Ethereum", "symbol": "ETHUSDT", "ticker_yahoo": "ETH-USD", "periodo": 50, "tier": 1, "alocacao": 0.25},
    {"nome": "Binance Coin", "symbol": "BNBUSDT", "ticker_yahoo": "BNB-USD", "periodo": 70, "tier": 2, "alocacao": 0.125},
    {"nome": "Solana", "symbol": "SOLUSDT", "ticker_yahoo": "SOL-USD", "periodo": 45, "tier": 2, "alocacao": 0.125},
    {"nome": "Chainlink", "symbol": "LINKUSDT", "ticker_yahoo": "LINK-USD", "periodo": 40, "tier": 3, "alocacao": 0.0625},
    {"nome": "Uniswap", "symbol": "UNIUSDT", "ticker_yahoo": "UNI-USD", "periodo": 65, "tier": 3, "alocacao": 0.0625},
    {"nome": "Algorand", "symbol": "ALGOUSDT", "ticker_yahoo": "ALGO-USD", "periodo": 40, "tier": 3, "alocacao": 0.0625},
    {"nome": "VeChain", "symbol": "VETUSDT", "ticker_yahoo": "VET-USD", "periodo": 25, "tier": 3, "alocacao": 0.0625},
]

ALAVANCAGEM = 12

# ═══════════════════════════════════════
# FUNÇÕES
# ═══════════════════════════════════════

def enviar_telegram(mensagem):
    """Envia mensagem para o Telegram"""
    if TELEGRAM_BOT_TOKEN == "SEU_BOT_TOKEN_AQUI":
        return
    try:
        url = f"https://api.telegram.com/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"})
    except:
        pass

def buscar_dados(ticker, dias=365):
    """Busca dados históricos do Yahoo Finance"""
    try:
        df = yf.download(ticker, period=f"{dias}d", interval="1d", progress=False)
        if df.empty:
            return None
        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
        return df[["open", "high", "low", "close"]]
    except:
        return None

def calcular_gann_hilo(df, periodo):
    """Calcula Gann HiLo Activator"""
    df = df.copy()
    df["sma_high"] = df["high"].rolling(window=periodo).mean()
    df["sma_low"] = df["low"].rolling(window=periodo).mean()
    
    df["hilo_state"] = 0
    df["ghla"] = 0.0
    
    for i in range(periodo, len(df)):
        close = df.iloc[i]["close"]
        sma_high = df.iloc[i]["sma_high"]
        sma_low = df.iloc[i]["sma_low"]
        prev_state = df.iloc[i-1]["hilo_state"]
        prev_ghla = df.iloc[i-1]["ghla"]
        
        if close > sma_high:
            state = 1
            ghla = sma_low
        elif close < sma_low:
            state = -1
            ghla = sma_high
        else:
            state = prev_state
            ghla = prev_ghla
        
        df.iloc[i, df.columns.get_loc("hilo_state")] = state
        df.iloc[i, df.columns.get_loc("ghla")] = ghla
    
    return df

def analisar_cripto(cripto):
    """Analisa uma criptomoeda"""
    print(f"\n📊 Analisando {cripto['nome']}...")
    
    df = buscar_dados(cripto["ticker_yahoo"])
    if df is None or len(df) < cripto["periodo"] + 10:
        print(f"  ✗ Sem dados suficientes")
        return None
    
    df = calcular_gann_hilo(df, cripto["periodo"])
    
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2]
    
    preco_atual = ultimo["close"]
    ghla = ultimo["ghla"]
    tendencia_atual = "VERDE" if ultimo["hilo_state"] == 1 else "VERMELHO" if ultimo["hilo_state"] == -1 else "NEUTRO"
    tendencia_anterior = "VERDE" if penultimo["hilo_state"] == 1 else "VERMELHO" if penultimo["hilo_state"] == -1 else "NEUTRO"
    
    mudou = tendencia_atual != tendencia_anterior and tendencia_anterior != "NEUTRO"
    
    if mudou:
        if tendencia_atual == "VERDE":
            sinal = "COMPRAR"
        elif tendencia_atual == "VERMELHO":
            sinal = "VENDER"
        else:
            sinal = "MANTER"
    else:
        sinal = "MANTER"
    
    print(f"  Preço: ${preco_atual:,.2f}")
    print(f"  GHLA: ${ghla:,.2f}")
    print(f"  Tendência: {tendencia_atual}")
    print(f"  Sinal: {sinal}")
    
    return {
        "cripto": cripto,
        "preco": preco_atual,
        "ghla": ghla,
        "tendencia": tendencia_atual,
        "sinal": sinal,
        "mudou": mudou
    }

def executar_ordem(binance_client, analise):
    """Executa ordem na Binance"""
    cripto = analise["cripto"]
    symbol = cripto["symbol"]
    sinal = analise["sinal"]
    
    if sinal == "MANTER":
        return None
    
    try:
        # Configurar alavancagem
        binance_client.futures_change_leverage(symbol=symbol, leverage=ALAVANCAGEM)
        
        # Configurar margem isolada
        try:
            binance_client.futures_change_margin_type(symbol=symbol, marginType="ISOLATED")
        except:
            pass
        
        # Fechar posição anterior (se houver)
        positions = binance_client.futures_position_information(symbol=symbol)
        pos = next((p for p in positions if float(p["positionAmt"]) != 0), None)
        
        if pos:
            amt = abs(float(pos["positionAmt"]))
            side = "SELL" if float(pos["positionAmt"]) > 0 else "BUY"
            binance_client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=amt)
            print(f"  ✓ Posição anterior fechada")
        
        # Calcular quantidade
        capital_alocado = CAPITAL_INICIAL * cripto["alocacao"]
        capital_com_alavancagem = capital_alocado * ALAVANCAGEM
        quantidade = capital_com_alavancagem / analise["preco"]
        
        # Arredondar quantidade conforme regras da Binance
        quantidade = round(quantidade, 3)
        
        # Abrir nova posição
        if sinal == "COMPRAR":
            order = binance_client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantidade)
            print(f"  ✓ LONG aberto: {quantidade} @ ${analise['preco']:.2f}")
        elif sinal == "VENDER":
            order = binance_client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantidade)
            print(f"  ✓ SHORT aberto: {quantidade} @ ${analise['preco']:.2f}")
        
        return order
        
    except Exception as e:
        print(f"  ✗ Erro ao executar ordem: {e}")
        return None

def executar_analise_completa():
    """Executa análise completa de todas as criptos"""
    print("\n" + "="*50)
    print(f"  MAGNUS WEALTH - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50)
    
    # Conectar Binance
    binance_client = None
    if BINANCE_API_KEY != "SUA_API_KEY_AQUI":
        try:
            binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            binance_client.ping()
            print("✓ Binance conectada")
        except Exception as e:
            print(f"✗ Erro ao conectar Binance: {e}")
    
    # Analisar todas as criptos
    resultados = []
    sinais_gerados = []
    
    for cripto in CRIPTOS:
        analise = analisar_cripto(cripto)
        if analise:
            resultados.append(analise)
            
            if analise["sinal"] != "MANTER" and binance_client:
                ordem = executar_ordem(binance_client, analise)
                if ordem:
                    sinais_gerados.append(analise)
    
    # Enviar resumo ao Telegram
    if sinais_gerados:
        msg = f"🚀 *SINAIS GERADOS* ({len(sinais_gerados)})\n\n"
        for s in sinais_gerados:
            emoji = "🟢" if s["sinal"] == "COMPRAR" else "🔴"
            msg += f"{emoji} *{s['cripto']['nome']}*\n"
            msg += f"Sinal: {s['sinal']}\n"
            msg += f"Preço: ${s['preco']:,.2f}\n\n"
        enviar_telegram(msg)
    else:
        print("\n✓ Nenhum sinal gerado")
    
    print("\n" + "="*50)
    print("  ANÁLISE CONCLUÍDA")
    print("="*50 + "\n")

# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

if __name__ == "__main__":
    print("═══════════════════════════════════════")
    print("  MAGNUS WEALTH - TRADING BOT")
    print("═══════════════════════════════════════\n")
    
    # Agendar execução diária às 21h
    schedule.every().day.at("21:00").do(executar_analise_completa)
    
    print("✓ Bot iniciado")
    print("✓ Agendamento: Todos os dias às 21:00")
    print("\nPressione Ctrl+C para parar\n")
    
    # Executar uma vez agora para testar
    print("Executando análise inicial...")
    executar_analise_completa()
    
    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(60)

