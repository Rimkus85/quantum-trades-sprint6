"""
Otimizador Quinzenal Magnus Wealth
Versão 1.0

Otimiza períodos CHiLo e avalia novas criptomoedas para o portfólio
Executa a cada 15 dias às 22:00 BR
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import json
from typing import Dict, List, Tuple

# Carregar variáveis de ambiente
load_dotenv()

# Configuração das TOP 8 criptomoedas atuais
PORTFOLIO_ATUAL = [
    {'name': 'Bitcoin', 'symbol': 'BTCUSDT', 'yahoo': 'BTC-USD', 'period': 40, 'emoji': '🥇', 'tier': 1, 'alocacao': 0.25},
    {'name': 'Ethereum', 'symbol': 'ETHUSDT', 'yahoo': 'ETH-USD', 'period': 50, 'emoji': '🥈', 'tier': 1, 'alocacao': 0.25},
    {'name': 'Binance Coin', 'symbol': 'BNBUSDT', 'yahoo': 'BNB-USD', 'period': 70, 'emoji': '🟡', 'tier': 2, 'alocacao': 0.125},
    {'name': 'Solana', 'symbol': 'SOLUSDT', 'yahoo': 'SOL-USD', 'period': 45, 'emoji': '🟣', 'tier': 2, 'alocacao': 0.125},
    {'name': 'Chainlink', 'symbol': 'LINKUSDT', 'yahoo': 'LINK-USD', 'period': 40, 'emoji': '🔗', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'Uniswap', 'symbol': 'UNIUSDT', 'yahoo': 'UNI7083-USD', 'period': 65, 'emoji': '🦄', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'Algorand', 'symbol': 'ALGOUSDT', 'yahoo': 'ALGO-USD', 'period': 40, 'emoji': '🔷', 'tier': 3, 'alocacao': 0.0625},
    {'name': 'VeChain', 'symbol': 'VETUSDT', 'yahoo': 'VET-USD', 'period': 25, 'emoji': '🌿', 'tier': 3, 'alocacao': 0.0625}
]

# Candidatas para análise (Top 50 - excluindo as já no portfólio)
CANDIDATAS = [
    {'name': 'Cardano', 'yahoo': 'ADA-USD', 'emoji': '🔵'},
    {'name': 'Avalanche', 'yahoo': 'AVAX-USD', 'emoji': '🔺'},
    {'name': 'Polygon', 'yahoo': 'MATIC-USD', 'emoji': '🟣'},
    {'name': 'Polkadot', 'yahoo': 'DOT-USD', 'emoji': '🔴'},
    {'name': 'Litecoin', 'yahoo': 'LTC-USD', 'emoji': '⚪'},
    {'name': 'Cosmos', 'yahoo': 'ATOM-USD', 'emoji': '⚛️'},
    {'name': 'Stellar', 'yahoo': 'XLM-USD', 'emoji': '⭐'},
    {'name': 'Filecoin', 'yahoo': 'FIL-USD', 'emoji': '📁'},
    {'name': 'Hedera', 'yahoo': 'HBAR-USD', 'emoji': '♓'},
    {'name': 'Cronos', 'yahoo': 'CRO-USD', 'emoji': '💎'},
    {'name': 'Near Protocol', 'yahoo': 'NEAR-USD', 'emoji': '🌐'},
    {'name': 'Aptos', 'yahoo': 'APT-USD', 'emoji': '🅰️'},
    {'name': 'Arbitrum', 'yahoo': 'ARB-USD', 'emoji': '🔷'},
    {'name': 'Optimism', 'yahoo': 'OP-USD', 'emoji': '🔴'},
    {'name': 'Immutable', 'yahoo': 'IMX-USD', 'emoji': '🎮'},
]

# Períodos para testar (3-60)
PERIODOS_TESTE = [3, 5, 7, 10, 12, 15, 18, 20, 22, 25, 28, 30, 33, 35, 38, 40, 45, 50, 55, 60]

# Pesos das métricas (sem drawdown)
PESOS = {
    'taxa_acerto': 0.40,
    'sharpe': 0.30,
    'retorno': 0.30
}

def buscar_dados_yahoo(yahoo_symbol: str, period: str = '1y') -> pd.DataFrame:
    """
    Busca dados históricos do Yahoo Finance
    """
    try:
        ticker = yf.Ticker(yahoo_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return None
        
        df.columns = [c.lower() for c in df.columns]
        return df
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar {yahoo_symbol}: {e}")
        return None

def calcular_chilo(df: pd.DataFrame, period: int) -> pd.DataFrame:
    """
    Calcula o CHiLo (Custom HiLo) - Modo Activator
    """
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

def calcular_metricas(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de performance do indicador
    
    Retorna:
    - taxa_acerto: % de sinais corretos
    - sharpe: Sharpe Ratio
    - retorno: Retorno total %
    """
    if len(df) < 10:
        return None
    
    # Remover NaN
    df = df.dropna(subset=['hilo_state']).copy()  # .copy() evita SettingWithCopyWarning
    
    if len(df) < 10:
        return None
    
    # Calcular retornos diários
    df.loc[:, 'retorno_diario'] = df['close'].pct_change()
    
    # Simular estratégia: comprado quando verde (1), vendido quando vermelho (-1)
    df.loc[:, 'sinal'] = df['hilo_state'].shift(1)  # Usar sinal do dia anterior
    df.loc[:, 'estrategia_retorno'] = df['sinal'] * df['retorno_diario']
    
    # Remover NaN
    df = df.dropna(subset=['estrategia_retorno'])
    
    if len(df) < 10:
        return None
    
    # Taxa de acerto
    acertos = (df['estrategia_retorno'] > 0).sum()
    total_trades = len(df[df['estrategia_retorno'] != 0])
    taxa_acerto = (acertos / total_trades * 100) if total_trades > 0 else 0
    
    # Sharpe Ratio (anualizado)
    retorno_medio = df['estrategia_retorno'].mean()
    std_retorno = df['estrategia_retorno'].std()
    sharpe = (retorno_medio / std_retorno * np.sqrt(252)) if std_retorno > 0 else 0
    
    # Retorno total
    retorno_total = (1 + df['estrategia_retorno']).prod() - 1
    retorno_pct = retorno_total * 100
    
    # Buy & Hold para comparação
    retorno_bh = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
    
    return {
        'taxa_acerto': taxa_acerto,
        'sharpe': sharpe,
        'retorno': retorno_pct,
        'retorno_bh': retorno_bh,
        'superacao_bh': retorno_pct - retorno_bh
    }

def calcular_score(metricas: Dict) -> float:
    """
    Calcula score ponderado (0-100)
    """
    if not metricas:
        return 0
    
    # Normalizar métricas
    score_acerto = min(metricas['taxa_acerto'] / 70 * 100, 100)  # 70% = 100 pontos
    score_sharpe = min(metricas['sharpe'] / 1.5 * 100, 100)  # Sharpe 1.5 = 100 pontos
    score_retorno = min(max(metricas['superacao_bh'] / 20 * 100, 0), 100)  # +20% vs BH = 100 pontos
    
    # Score ponderado
    score = (
        score_acerto * PESOS['taxa_acerto'] +
        score_sharpe * PESOS['sharpe'] +
        score_retorno * PESOS['retorno']
    )
    
    return round(score, 1)

def otimizar_periodo(cripto: Dict) -> Dict:
    """
    Encontra o melhor período para uma criptomoeda
    """
    print(f"\n🔍 Otimizando {cripto['name']}...")
    
    # Buscar dados
    df = buscar_dados_yahoo(cripto['yahoo'])
    if df is None:
        print(f"   ❌ Sem dados para {cripto['name']}")
        return None
    
    melhor_periodo = cripto['period']
    melhor_score = 0
    melhor_metricas = None
    
    resultados = []
    
    # Testar cada período
    for periodo in PERIODOS_TESTE:
        df_teste = df.copy()
        df_teste = calcular_chilo(df_teste, periodo)
        metricas = calcular_metricas(df_teste)
        
        if metricas:
            score = calcular_score(metricas)
            resultados.append({
                'periodo': periodo,
                'score': score,
                'metricas': metricas
            })
            
            if score > melhor_score:
                melhor_score = score
                melhor_periodo = periodo
                melhor_metricas = metricas
    
    # Ordenar por score
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    # Calcular melhoria
    periodo_atual = cripto['period']
    score_atual = next((r['score'] for r in resultados if r['periodo'] == periodo_atual), 0)
    melhoria_pct = ((melhor_score - score_atual) / score_atual * 100) if score_atual > 0 else 0
    
    print(f"   ✓ Período atual: {periodo_atual} (score: {score_atual:.1f})")
    print(f"   ✓ Melhor período: {melhor_periodo} (score: {melhor_score:.1f})")
    print(f"   ✓ Melhoria: {melhoria_pct:+.1f}%")
    
    return {
        'cripto': cripto['name'],
        'emoji': cripto['emoji'],
        'periodo_atual': periodo_atual,
        'periodo_otimo': melhor_periodo,
        'score_atual': score_atual,
        'score_otimo': melhor_score,
        'melhoria_pct': melhoria_pct,
        'metricas_atual': next((r['metricas'] for r in resultados if r['periodo'] == periodo_atual), None),
        'metricas_otimo': melhor_metricas,
        'recomendar_atualizacao': melhoria_pct > 5.0  # >5% de melhoria
    }

def avaliar_candidata(candidata: Dict) -> Dict:
    """
    Avalia uma criptomoeda candidata
    """
    print(f"\n🔍 Avaliando {candidata['name']}...")
    
    # Buscar dados
    df = buscar_dados_yahoo(candidata['yahoo'])
    if df is None:
        print(f"   ❌ Sem dados para {candidata['name']}")
        return None
    
    # Verificar requisitos mínimos
    if len(df) < 252:  # Menos de 1 ano
        print(f"   ❌ Histórico insuficiente (<1 ano)")
        return None
    
    # Encontrar melhor período
    melhor_periodo = None
    melhor_score = 0
    melhor_metricas = None
    
    for periodo in PERIODOS_TESTE:
        df_teste = df.copy()
        df_teste = calcular_chilo(df_teste, periodo)
        metricas = calcular_metricas(df_teste)
        
        if metricas:
            score = calcular_score(metricas)
            
            if score > melhor_score:
                melhor_score = score
                melhor_periodo = periodo
                melhor_metricas = metricas
    
    if melhor_metricas is None:
        print(f"   ❌ Não foi possível calcular métricas")
        return None
    
    # Verificar requisitos mínimos de performance
    if melhor_metricas['taxa_acerto'] < 55:
        print(f"   ❌ Taxa de acerto muito baixa ({melhor_metricas['taxa_acerto']:.1f}%)")
        return None
    
    if melhor_metricas['sharpe'] < 0.5:
        print(f"   ❌ Sharpe muito baixo ({melhor_metricas['sharpe']:.2f})")
        return None
    
    print(f"   ✓ Score: {melhor_score:.1f}")
    print(f"   ✓ Período ótimo: {melhor_periodo}")
    print(f"   ✓ Taxa de acerto: {melhor_metricas['taxa_acerto']:.1f}%")
    print(f"   ✓ Sharpe: {melhor_metricas['sharpe']:.2f}")
    
    return {
        'name': candidata['name'],
        'emoji': candidata['emoji'],
        'yahoo': candidata['yahoo'],
        'periodo_otimo': melhor_periodo,
        'score': melhor_score,
        'metricas': melhor_metricas
    }

def formatar_relatorio(otimizacoes: List[Dict], candidatas: List[Dict]) -> str:
    """
    Formata relatório em Markdown para Telegram
    """
    hoje = datetime.now().strftime('%d/%m/%Y')
    proxima = (datetime.now() + timedelta(days=15)).strftime('%d/%m/%Y')
    
    msg = f"""🔄 **RELATÓRIO QUINZENAL DE OTIMIZAÇÃO**
Magnus Wealth - {hoje}

═══════════════════════════════════

📊 **OTIMIZAÇÃO DE PERÍODOS**

"""
    
    # Otimizações recomendadas
    atualizacoes = [o for o in otimizacoes if o and o['recomendar_atualizacao']]
    
    if atualizacoes:
        msg += "✅ **ATUALIZAÇÕES RECOMENDADAS:**\n\n"
        for opt in atualizacoes:
            msg += f"{opt['emoji']} **{opt['cripto']}**\n"
            msg += f"   Período: {opt['periodo_atual']} → {opt['periodo_otimo']}\n"
            msg += f"   Melhoria: {opt['melhoria_pct']:+.1f}%\n"
            msg += f"   Score: {opt['score_atual']:.1f} → {opt['score_otimo']:.1f}\n"
            if opt['metricas_otimo']:
                msg += f"   Taxa acerto: {opt['metricas_otimo']['taxa_acerto']:.1f}%\n"
                msg += f"   Sharpe: {opt['metricas_otimo']['sharpe']:.2f}\n"
            msg += "\n"
    else:
        msg += "⏸️ **SEM ATUALIZAÇÕES NECESSÁRIAS**\n"
        msg += "Todos os períodos estão otimizados!\n\n"
    
    # Sem alterações
    sem_alteracao = [o for o in otimizacoes if o and not o['recomendar_atualizacao']]
    if sem_alteracao:
        msg += "⏸️ **SEM ALTERAÇÕES:**\n"
        for opt in sem_alteracao:
            msg += f"   • {opt['cripto']} ({opt['periodo_atual']}) ✅\n"
        msg += "\n"
    
    msg += "═══════════════════════════════════\n\n"
    msg += "🔍 **ANÁLISE DE NOVAS CANDIDATAS**\n\n"
    
    # Top 5 candidatas
    if candidatas:
        candidatas_validas = [c for c in candidatas if c is not None]
        candidatas_validas.sort(key=lambda x: x['score'], reverse=True)
        top5 = candidatas_validas[:5]
        
        msg += f"**TOP {len(top5)} MELHORES SCORES:**\n\n"
        for i, cand in enumerate(top5, 1):
            msg += f"{i}. {cand['emoji']} **{cand['name']}** - Score: {cand['score']:.1f}/100\n"
            msg += f"   • Taxa acerto: {cand['metricas']['taxa_acerto']:.1f}%\n"
            msg += f"   • Sharpe: {cand['metricas']['sharpe']:.2f}\n"
            msg += f"   • Retorno 90d: {cand['metricas']['retorno']:+.1f}%\n"
            msg += f"   • Período ótimo: {cand['periodo_otimo']}\n\n"
        
        # Recomendação
        msg += "═══════════════════════════════════\n\n"
        msg += "💡 **RECOMENDAÇÕES FINAIS**\n\n"
        
        # Verificar se há candidata muito superior
        melhor_candidata = top5[0] if top5 else None
        pior_portfolio = min(otimizacoes, key=lambda x: x['score_atual'] if x else 0)
        
        if melhor_candidata and pior_portfolio and melhor_candidata['score'] > pior_portfolio['score_atual'] * 1.2:
            # Recomendar substituição
            msg += "🔄 **SUBSTITUIÇÃO PROPOSTA:**\n\n"
            msg += f"**REMOVER:** {pior_portfolio['emoji']} {pior_portfolio['cripto']} (Score: {pior_portfolio['score_atual']:.1f}/100)\n"
            msg += f"   • Taxa de acerto: {pior_portfolio['metricas_atual']['taxa_acerto']:.1f}%\n"
            msg += f"   • Sharpe: {pior_portfolio['metricas_atual']['sharpe']:.2f}\n\n"
            msg += f"**ADICIONAR:** {melhor_candidata['emoji']} {melhor_candidata['name']} (Score: {melhor_candidata['score']:.1f}/100)\n"
            msg += f"   • Taxa de acerto: {melhor_candidata['metricas']['taxa_acerto']:.1f}% ({melhor_candidata['metricas']['taxa_acerto']-pior_portfolio['metricas_atual']['taxa_acerto']:+.1f}pp)\n"
            msg += f"   • Sharpe: {melhor_candidata['metricas']['sharpe']:.2f} ({melhor_candidata['metricas']['sharpe']-pior_portfolio['metricas_atual']['sharpe']:+.2f})\n"
            msg += f"   • Período ótimo: {melhor_candidata['periodo_otimo']}\n\n"
            msg += "**IMPACTO ESPERADO:**\n"
            msg += f"   • Melhoria de score: {melhor_candidata['score']-pior_portfolio['score_atual']:+.1f} pontos\n"
        elif melhor_candidata and melhor_candidata['score'] > 70:
            # Recomendar expansão
            msg += "➕ **EXPANSÃO DO PORTFÓLIO PROPOSTA:**\n\n"
            msg += f"**ADICIONAR:** {melhor_candidata['emoji']} {melhor_candidata['name']} (Score: {melhor_candidata['score']:.1f}/100)\n"
            msg += f"   • Taxa de acerto: {melhor_candidata['metricas']['taxa_acerto']:.1f}%\n"
            msg += f"   • Sharpe: {melhor_candidata['metricas']['sharpe']:.2f}\n"
            msg += f"   • Retorno 90d: {melhor_candidata['metricas']['retorno']:+.1f}%\n"
            msg += f"   • Período ótimo: {melhor_candidata['periodo_otimo']}\n\n"
            msg += f"**Portfólio:** {len(PORTFOLIO_ATUAL)} → {len(PORTFOLIO_ATUAL)+1} criptos\n\n"
            msg += "**IMPACTO ESPERADO:**\n"
            msg += "   • Diversificação melhorada\n"
            msg += "   • Performance média elevada\n"
        else:
            msg += "✅ **MANTER PORTFÓLIO ATUAL**\n\n"
            msg += "Nenhuma candidata apresenta vantagem significativa.\n"
            msg += "Portfólio atual está bem otimizado!\n"
    else:
        msg += "❌ Nenhuma candidata válida encontrada.\n"
    
    msg += "\n═══════════════════════════════════\n\n"
    msg += "⚙️ **AÇÕES NECESSÁRIAS:**\n\n"
    
    if atualizacoes:
        msg += "Para aplicar as otimizações:\n"
        msg += "1. Confirme as alterações\n"
        msg += "2. Atualizarei automaticamente o código\n"
        msg += "3. Próxima análise diária já usará novos parâmetros\n\n"
        msg += "Responda:\n"
        msg += "✅ APROVAR TUDO\n"
        msg += "🔧 APROVAR APENAS PERÍODOS\n"
        msg += "❌ MANTER COMO ESTÁ\n"
    else:
        msg += "Nenhuma ação necessária no momento.\n"
    
    msg += f"\n═══════════════════════════════════\n\n"
    msg += f"📅 Próxima otimização: {proxima}\n"
    
    return msg

def enviar_telegram_bot(mensagem: str):
    """
    Envia mensagem via Telegram Bot
    """
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Credenciais do Telegram não configuradas")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': mensagem,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✓ Relatório enviado com sucesso via Bot!")
            return True
        else:
            print(f"❌ Erro na resposta: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - OTIMIZADOR QUINZENAL')
    print('  Versão 1.0')
    print('═══════════════════════════════════════════════════\n')
    
    # Etapa 1: Otimizar períodos do portfólio atual
    print("📊 ETAPA 1: Otimização de Períodos\n")
    otimizacoes = []
    for cripto in PORTFOLIO_ATUAL:
        resultado = otimizar_periodo(cripto)
        if resultado:
            otimizacoes.append(resultado)
    
    print(f"\n✓ {len(otimizacoes)}/{len(PORTFOLIO_ATUAL)} criptos otimizadas")
    
    # Etapa 2: Avaliar candidatas
    print("\n\n🔍 ETAPA 2: Avaliação de Candidatas\n")
    candidatas_avaliadas = []
    for candidata in CANDIDATAS:
        resultado = avaliar_candidata(candidata)
        if resultado:
            candidatas_avaliadas.append(resultado)
    
    print(f"\n✓ {len(candidatas_avaliadas)}/{len(CANDIDATAS)} candidatas válidas")
    
    # Etapa 3: Gerar relatório
    print("\n\n📝 ETAPA 3: Geração de Relatório\n")
    relatorio = formatar_relatorio(otimizacoes, candidatas_avaliadas)
    
    # Salvar relatório em arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/home/ubuntu/relatorio_otimizacao_{timestamp}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    print(f"✓ Relatório salvo em: {filename}")
    
    # Etapa 4: Enviar para Telegram
    print("\n\n📤 ETAPA 4: Envio para Telegram\n")
    enviar_telegram_bot(relatorio)
    
    print("\n═══════════════════════════════════════════════════")
    print("✓ Otimização quinzenal concluída!")
    print("═══════════════════════════════════════════════════")

