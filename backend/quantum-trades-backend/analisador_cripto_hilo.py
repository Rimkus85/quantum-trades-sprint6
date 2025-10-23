#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Criptomoedas - CHiLo (Custom HiLo)
Magnus Wealth - Versão 8.3.0
Indicador: CHiLo por Paulo H. Parize e Tio Huli

ATUALIZAÇÃO: Top 8 Criptos com Períodos Otimizados (Dados Reais Yahoo Finance)
Data: 19/10/2025
Execução: Diária às 21h
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import yfinance as yf

load_dotenv()

# Top 8 Criptomoedas com Períodos Otimizados (Simulação 2025 - Dados Reais)
# Removidas: XRP (-25.67%), Litecoin (-18.03%), Cosmos (-10.10%)
TOP_8 = [
    {'symbol': 'BTCUSDT', 'yahoo': 'BTC-USD', 'name': 'Bitcoin', 'emoji': '🥇', 'period': 40, 'tier': 1, 'alocacao': 0.25},
    {'symbol': 'ETHUSDT', 'yahoo': 'ETH-USD', 'name': 'Ethereum', 'emoji': '🥈', 'period': 50, 'tier': 1, 'alocacao': 0.25},
    {'symbol': 'BNBUSDT', 'yahoo': 'BNB-USD', 'name': 'Binance Coin', 'emoji': '🟡', 'period': 70, 'tier': 2, 'alocacao': 0.125},
    {'symbol': 'SOLUSDT', 'yahoo': 'SOL-USD', 'name': 'Solana', 'emoji': '🟣', 'period': 45, 'tier': 2, 'alocacao': 0.125},
    {'symbol': 'LINKUSDT', 'yahoo': 'LINK-USD', 'name': 'Chainlink', 'emoji': '🔗', 'period': 40, 'tier': 3, 'alocacao': 0.0625},
    {'symbol': 'UNIUSDT', 'yahoo': 'UNI-USD', 'name': 'Uniswap', 'emoji': '🦄', 'period': 65, 'tier': 3, 'alocacao': 0.0625},
    {'symbol': 'ALGOUSDT', 'yahoo': 'ALGO-USD', 'name': 'Algorand', 'emoji': '🔷', 'period': 40, 'tier': 3, 'alocacao': 0.0625},
    {'symbol': 'VETUSDT', 'yahoo': 'VET-USD', 'name': 'VeChain', 'emoji': '🌿', 'period': 25, 'tier': 3, 'alocacao': 0.0625},
]

def buscar_dados(symbol, yahoo_symbol):
    """
    Busca dados históricos do Yahoo Finance (dados reais diários)
    """
    try:
        print(f"   📊 Buscando dados de {yahoo_symbol}...")
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period='1y', interval='1d')
        
        if df.empty:
            raise ValueError(f"Nenhum dado retornado para {yahoo_symbol}")
        
        # Renomear colunas
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        df = df.rename(columns={'date': 'time'})
        
        return df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar {yahoo_symbol}: {e}")
        return None

def calcular_gann_hilo_activator(df, period, ma_type='SMA'):
    """
    Calcula o CHiLo (Custom HiLo) - Modo HiLo Activator
    Indicador criado por Paulo H. Parize e Tio Huli
    
    Fórmula matemática (Modo Activator):
    
    1. Calcular MA(H,n) e MA(L,n) [SMA ou EMA]
    
    2. Estado HiLo:
        BULLISH (1)  se Close > MA(H,n)      # Tendência de alta
        BEARISH (-1) se Close < MA(L,n)      # Tendência de baixa
        NEUTRO (0)   caso contrário           # Zona neutra
    
    3. Linha CHiLo (Modo Activator):
        Se BULLISH:  CHiLo = MA(L,n)   # Plota média dos lows (suporte)
        Se BEARISH:  CHiLo = MA(H,n)   # Plota média dos highs (resistência)
        Se NEUTRO:   CHiLo = valor anterior  # Mantém linha anterior
    
    Referência: TradingView - CHiLo by Parize
    https://www.tradingview.com/script/YUqiooBi-CHiLo-Custom-HiLo-SMA-EMA-Activator-Shading-Auto-Decimals/
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
    df = buscar_dados(cripto['symbol'], cripto['yahoo'])
    
    if df is None or len(df) == 0:
        raise ValueError(f"Dados insuficientes para {cripto['name']}")
    
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
    # Verificar se há mudanças de tendência
    mudancas = [r for r in resultados if r['mudanca']]
    
    msg = "🚀 *ANÁLISE DIÁRIA DE CRIPTOMOEDAS - CHiLo (CUSTOM HILO)*\n\n"
    msg += f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    
    # ALERTA GIGANTE se houver mudanças
    if mudancas:
        msg += "\n"
        msg += "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨\n"
        msg += "*⚠️ ALERTA DE MUDANÇA! ⚠️*\n"
        msg += "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨\n"
        msg += f"*{len(mudancas)} CRIPTO(S) MUDOU DE TENDÊNCIA!*\n"
        for m in mudancas:
            direcao = "🟢 COMPRA" if m['trend'] == 'verde' else "🔴 VENDA"
            msg += f"• *{m['name']}* → {direcao}\n"
        msg += "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨\n\n"
    
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
                msg += f"📈 Alocação: {r['alocacao']*100:.2f}%\n"
                msg += f"{emoji_sinal} Sinal: *{r['sinal']}*\n"
                
                if r['mudanca']:
                    msg += "\n"
                    msg += "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
                    if r['trend'] == 'verde':
                        msg += "*💚 VIROU VERDE! SINAL DE COMPRA! 💚*\n"
                        msg += "*📈 ZERA VENDA + ENTRA COMPRADO! 📈*\n"
                    else:
                        msg += "*❤️ VIROU VERMELHO! SINAL DE VENDA! ❤️*\n"
                        msg += "*📉 ZERA COMPRA + ENTRA VENDIDO! 📉*\n"
                    msg += "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n"
                
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
    msg += "📊 Indicador: CHiLo (Custom HiLo) - Modo Activator\n"
    msg += "👥 Criadores: Paulo H. Parize e Tio Huli\n"
    msg += "🔧 Magnus Wealth v8.3.0 - Top 8 Otimizado (Dados Reais)\n"
    
    return msg

def enviar_telegram(msg):
    """
    Envia mensagem para o grupo do Telegram
    """
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
    
    # Usar caminho absoluto para o arquivo de sessão
    script_dir = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(script_dir, 'magnus_session')
    
    with TelegramClient(session_path, api_id, api_hash) as client:
        client.send_message(group_id, msg, parse_mode='markdown')

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - ANALISADOR DE CRIPTOMOEDAS')
    print('  CHiLo (Custom HiLo) - Modo Activator - v8.3.0')
    print('  Indicador: Paulo H. Parize e Tio Huli')
    print('  TOP 8 CRIPTOS - PERÍODOS OTIMIZADOS (DADOS REAIS)')
    print('═══════════════════════════════════════════════════\n')
    
    resultados = []
    
    for cripto in TOP_8:
        try:
            resultado = analisar_cripto(cripto)
            resultados.append(resultado)
            print(f"✓ {cripto['name']}: {resultado['sinal']} - Tendência {resultado['trend']}")
        except Exception as e:
            print(f"✗ Erro ao analisar {cripto['name']}: {e}")
    
    print('\n' + '═'*50)
    print('Análise concluída!')
    print(f'Total de criptos analisadas: {len(resultados)}/{len(TOP_8)}')
    
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

