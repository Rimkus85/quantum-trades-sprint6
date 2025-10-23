#!/usr/bin/env python3
"""
Analisador de Criptomoedas - CHiLo (Custom HiLo)
Magnus Wealth - Versão 8.3.0 (Bot Version)
Indicador: CHiLo por Paulo H. Parize e Tio Huli

Versão usando Telegram Bot (mais confiável para GitHub Actions)
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Carregar variáveis de ambiente
load_dotenv()

# Configuração das TOP 8 criptomoedas com períodos otimizados
TOP_8 = [
    # TIER 1 - Blue Chips (50% da alocação)
    {'name': 'Bitcoin', 'symbol': 'BTCUSDT', 'yahoo': 'BTC-USD', 'period': 40, 'emoji': '🥇', 'tier': 1, 'alocacao': 0.25},
    {'name': 'Ethereum', 'symbol': 'ETHUSDT', 'yahoo': 'ETH-USD', 'period': 50, 'emoji': '🥈', 'tier': 1, 'alocacao': 0.25},
    
    # TIER 2 - Large Caps (25% da alocação)
    {'name': 'Binance Coin', 'symbol': 'BNBUSDT', 'yahoo': 'BNB-USD', 'period': 70, 'emoji': '🟡', 'tier': 2, 'alocacao': 0.125},
    {'name': 'Solana', 'symbol': 'SOLUSDT', 'yahoo': 'SOL-USD', 'period': 45, 'emoji': '🟣', 'tier': 2, 'alocacao': 0.125},
    
    # TIER 3 - Mid Caps (25% da alocação)
    {'name': 'Chainlink', 'symbol': 'LINKUSDT', 'yahoo': 'LINK-USD', 'period': 40, 'emoji': '🔗', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'Uniswap', 'symbol': 'UNIUSDT', 'yahoo': 'UNI-USD', 'period': 65, 'emoji': '🦄', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'Algorand', 'symbol': 'ALGOUSDT', 'yahoo': 'ALGO-USD', 'period': 40, 'emoji': '🔷', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'VeChain', 'symbol': 'VETUSDT', 'yahoo': 'VET-USD', 'period': 25, 'emoji': '🌿', 'tier': 3, 'alocacao': 0.0625}
]

def buscar_dados_yahoo(yahoo_symbol, period='1y'):
    """
    Busca dados históricos do Yahoo Finance
    """
    try:
        print(f"   📊 Buscando dados de {yahoo_symbol}...")
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            print(f"   ❌ Sem dados para {yahoo_symbol}")
            return None
        
        # Renomear colunas para minúsculas
        df.columns = [c.lower() for c in df.columns]
        return df
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar {yahoo_symbol}: {e}")
        return None

def calcular_gann_hilo_activator(df, period, ma_type='SMA'):
    """
    Calcula o CHiLo (Custom HiLo) - Modo HiLo Activator
    Indicador criado por Paulo H. Parize e Tio Huli
    """
    # Calcular médias móveis dos highs e lows
    if ma_type == 'SMA':
        hima = df['high'].rolling(window=period).mean()
        loma = df['low'].rolling(window=period).mean()
    else:  # EMA
        hima = df['high'].ewm(span=period, adjust=False).mean()
        loma = df['low'].ewm(span=period, adjust=False).mean()
    
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

def detectar_mudanca_tendencia(df):
    """
    Detecta mudança de tendência (virada de sinal)
    """
    if len(df) < 2:
        return False
    
    estado_atual = df['hilo_state'].iloc[-1]
    estado_anterior = df['hilo_state'].iloc[-2]
    
    # Mudança de tendência = estado diferente e não-zero
    if estado_atual != estado_anterior and estado_atual != 0:
        return True
    
    return False

def calcular_performance(df, capital_inicial=100):
    """
    Calcula performance com capital composto
    """
    if len(df) < 2:
        return {'capital': capital_inicial, 'retorno': 0.0}
    
    preco_inicial = df['close'].iloc[0]
    preco_final = df['close'].iloc[-1]
    
    retorno_pct = ((preco_final - preco_inicial) / preco_inicial) * 100
    capital_final = capital_inicial * (1 + retorno_pct/100)
    
    return {
        'capital': capital_final,
        'retorno': retorno_pct
    }

def analisar_cripto(cripto):
    """
    Analisa uma criptomoeda e retorna resultados
    """
    print(f"Analisando {cripto['name']} ({cripto['symbol']}) com período {cripto['period']}...")
    
    # Buscar dados
    df = buscar_dados_yahoo(cripto['yahoo'])
    if df is None:
        return None
    
    # Calcular indicador
    df = calcular_gann_hilo_activator(df, cripto['period'])
    
    # Estado atual
    estado = df['hilo_state'].iloc[-1]
    preco_atual = df['close'].iloc[-1]
    
    # Determinar tendência e sinal
    if estado == 1:
        trend = 'verde'
        sinal = 'COMPRAR'
    elif estado == -1:
        trend = 'vermelho'
        sinal = 'VENDER'
    else:
        trend = 'neutro'
        sinal = 'MANTER'
    
    # Detectar mudança
    mudanca = detectar_mudanca_tendencia(df)
    
    # Calcular performance em diferentes períodos
    p_total = calcular_performance(df)
    p_6m = calcular_performance(df.tail(180)) if len(df) >= 180 else p_total
    p_90d = calcular_performance(df.tail(90)) if len(df) >= 90 else p_total
    p_30d = calcular_performance(df.tail(30)) if len(df) >= 30 else p_total
    
    print(f"✓ {cripto['name']}: {sinal} - Tendência {trend}")
    
    return {
        'name': cripto['name'],
        'symbol': cripto['symbol'],
        'emoji': cripto['emoji'],
        'tier': cripto['tier'],
        'alocacao': cripto['alocacao'],
        'period': cripto['period'],
        'preco': preco_atual,
        'trend': trend,
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

def enviar_telegram_bot(msg):
    """
    Envia mensagem usando Telegram Bot API (mais confiável para automação)
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Erro: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': msg,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✓ Mensagem enviada com sucesso via Bot!")
            return True
        else:
            print(f"❌ Erro na resposta: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - ANALISADOR DE CRIPTOMOEDAS')
    print('  CHiLo (Custom HiLo) - Modo Activator - v8.3.0')
    print('  Indicador: Paulo H. Parize e Tio Huli')
    print('  TOP 8 CRIPTOS - PERÍODOS OTIMIZADOS (DADOS REAIS)')
    print('  Versão: Telegram Bot')
    print('═══════════════════════════════════════════════════\n')
    
    resultados = []
    
    for cripto in TOP_8:
        resultado = analisar_cripto(cripto)
        if resultado:
            resultados.append(resultado)
    
    print('══════════════════════════════════════════════════')
    print(f'Análise concluída!')
    print(f'Total de criptos analisadas: {len(resultados)}/{len(TOP_8)}')
    
    if resultados:
        print('Formatando mensagem...')
        msg = formatar_mensagem(resultados)
        
        print('Enviando para Telegram...')
        enviar_telegram_bot(msg)

