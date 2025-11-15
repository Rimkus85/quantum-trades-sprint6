#!/usr/bin/env python3
"""
Analisador de Criptomoedas - CHiLo (Custom HiLo)
Magnus Wealth - Versão 9.0.0 (Notificações Individuais)
Indicador: CHiLo por Paulo H. Parize e Tio Huli

MUDANÇAS v9.0.0:
- Notificações enviadas individualmente para cada usuário cadastrado
- Não envia mais para o grupo (apenas análises normais)
- Erros enviados apenas ao admin
"""

import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import json

# Carregar variáveis de ambiente
load_dotenv()

# Importar sistema de notificações e banco de dados
try:
    from database_usuarios import DatabaseUsuarios
    from notificador_usuario import NotificadorUsuario
    DB_DISPONIVEL = True
except:
    DB_DISPONIVEL = False
    print("⚠️ Sistema de usuários não disponível - usando modo legado")

# Carregar criptomoedas do portfolio_config.json (DINÂMICO)
try:
    from portfolio_manager import PortfolioManager
    portfolio = PortfolioManager()
    TOP_8 = portfolio.exportar_para_lista()
    print(f"✅ Carregadas {len(TOP_8)} criptomoedas ativas do portfolio_config.json")
except Exception as e:
    print(f"⚠️ Erro ao carregar portfolio_config.json: {e}")
    print("⚠️ Usando lista padrão de criptomoedas")
    # Fallback para lista padrão
    TOP_8 = [
        # TIER 1 - Blue Chips (50% da alocação)
        {'name': 'Bitcoin', 'symbol': 'BTCUSDT', 'yahoo': 'BTC-USD', 'period': 3, 'emoji': '🥇', 'tier': 1, 'alocacao': 0.25},
        {'name': 'Ethereum', 'symbol': 'ETHUSDT', 'yahoo': 'ETH-USD', 'period': 45, 'emoji': '🥈', 'tier': 1, 'alocacao': 0.25},
        
        # TIER 2 - Large Caps (25% da alocação)
        {'name': 'Binance Coin', 'symbol': 'BNBUSDT', 'yahoo': 'BNB-USD', 'period': 70, 'emoji': '🟡', 'tier': 2, 'alocacao': 0.125},
        {'name': 'Solana', 'symbol': 'SOLUSDT', 'yahoo': 'SOL-USD', 'period': 7, 'emoji': '🟣', 'tier': 2, 'alocacao': 0.125},
        
        # TIER 3 - Mid Caps (25% da alocação)
        {'name': 'Chainlink', 'symbol': 'LINKUSDT', 'yahoo': 'LINK-USD', 'period': 40, 'emoji': '🔗', 'tier': 3, 'alocacao': 0.0625},
        {'name': 'Uniswap', 'symbol': 'UNIUSDT', 'yahoo': 'UNI7083-USD', 'period': 65, 'emoji': '🦄', 'tier': 3, 'alocacao': 0.0625},
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
        return False, None, None
    
    estado_anterior = df['hilo_state'].iloc[-2]
    estado_atual = df['hilo_state'].iloc[-1]
    
    if estado_anterior == 0 or estado_atual == 0:
        return False, None, None
    
    if estado_anterior != estado_atual:
        return True, estado_anterior, estado_atual
    
    return False, None, None

def analisar_cripto(cripto):
    """
    Analisa uma criptomoeda usando CHiLo
    """
    print(f"\n{cripto['emoji']} Analisando {cripto['name']}...")
    
    # Buscar dados
    df = buscar_dados_yahoo(cripto['yahoo'])
    if df is None:
        return None
    
    # Calcular CHiLo
    df = calcular_gann_hilo_activator(df, cripto['period'])
    
    # Pegar último estado
    estado_atual = df['hilo_state'].iloc[-1]
    preco_atual = df['close'].iloc[-1]
    
    # Detectar mudança de tendência
    mudou, estado_anterior, estado_novo = detectar_mudanca_tendencia(df)
    
    # Determinar tendência
    if estado_atual == 1:
        tendencia = "Verde 🟢"
        cor_emoji = "🟢"
    elif estado_atual == -1:
        tendencia = "Vermelho 🔴"
        cor_emoji = "🔴"
    else:
        tendencia = "Neutro ⚪"
        cor_emoji = "⚪"
    
    resultado = {
        'name': cripto['name'],
        'emoji': cripto['emoji'],
        'period': cripto['period'],
        'estado': estado_atual,
        'tendencia': tendencia,
        'cor_emoji': cor_emoji,
        'preco': preco_atual,
        'mudou': mudou,
        'estado_anterior': estado_anterior,
        'estado_novo': estado_novo,
        'tier': cripto['tier']
    }
    
    print(f"   ✓ CHiLo {cripto['period']}: {tendencia}")
    if mudou:
        print(f"   🔔 MUDANÇA DE TENDÊNCIA DETECTADA!")
    
    return resultado

def gerar_mensagem_analise(resultados):
    """
    Gera mensagem formatada com os resultados da análise
    """
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S EDT')
    
    msg = f"📊 *ANÁLISE DIÁRIA - MAGNUS WEALTH*\n"
    msg += f"⏰ {timestamp}\n\n"
    
    # Agrupar por tier
    tier1 = [r for r in resultados if r and r['tier'] == 1]
    tier2 = [r for r in resultados if r and r['tier'] == 2]
    tier3 = [r for r in resultados if r and r['tier'] == 3]
    
    # TIER 1
    if tier1:
        msg += "🥇 *TIER 1 - Blue Chips*\n"
        for r in tier1:
            msg += f"{r['emoji']} *{r['name']}* (CHiLo {r['period']})\n"
            msg += f"   Tendência: {r['tendencia']}\n"
            msg += f"   Preço: ${r['preco']:,.2f}\n"
            if r['mudou']:
                msg += f"   🔔 *MUDANÇA DE TENDÊNCIA!*\n"
            msg += "\n"
    
    # TIER 2
    if tier2:
        msg += "🥈 *TIER 2 - Large Caps*\n"
        for r in tier2:
            msg += f"{r['emoji']} *{r['name']}* (CHiLo {r['period']})\n"
            msg += f"   Tendência: {r['tendencia']}\n"
            msg += f"   Preço: ${r['preco']:,.2f}\n"
            if r['mudou']:
                msg += f"   🔔 *MUDANÇA DE TENDÊNCIA!*\n"
            msg += "\n"
    
    # TIER 3
    if tier3:
        msg += "🥉 *TIER 3 - Mid Caps*\n"
        for r in tier3:
            msg += f"{r['emoji']} *{r['name']}* (CHiLo {r['period']})\n"
            msg += f"   Tendência: {r['tendencia']}\n"
            msg += f"   Preço: ${r['preco']:,.2f}\n"
            if r['mudou']:
                msg += f"   🔔 *MUDANÇA DE TENDÊNCIA!*\n"
            msg += "\n"
    
    # Mudanças de tendência
    mudancas = [r for r in resultados if r and r['mudou']]
    if mudancas:
        msg += "🚨 *MUDANÇAS DE TENDÊNCIA*\n\n"
        for r in mudancas:
            anterior = "🟢 Verde" if r['estado_anterior'] == 1 else "🔴 Vermelho"
            novo = "🟢 Verde" if r['estado_novo'] == 1 else "🔴 Vermelho"
            msg += f"{r['emoji']} *{r['name']}*: {anterior} → {novo}\n"
        msg += "\n"
    else:
        msg += "✅ *Sem mudanças de tendência hoje*\n\n"
    
    msg += "─────────────────────\n"
    msg += "📈 Magnus Wealth - Sistema CHiLo\n"
    msg += "🤖 Análise Automatizada v9.0.0"
    
    return msg

def enviar_para_usuarios_individuais(msg):
    """
    Envia mensagem individualmente para cada usuário cadastrado
    """
    if not DB_DISPONIVEL:
        print("⚠️ Sistema de usuários não disponível")
        return False
    
    try:
        db = DatabaseUsuarios()
        usuarios_ativos = db.listar_usuarios(apenas_ativos=True)
        
        if not usuarios_ativos:
            print("⚠️ Nenhum usuário ativo cadastrado")
            return False
        
        print(f"\n📤 Enviando para {len(usuarios_ativos)} usuários...")
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN não configurado")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        enviados = 0
        erros = 0
        
        for usuario in usuarios_ativos:
            user_id = usuario['telegram_user_id']
            nome = usuario['nome']
            
            payload = {
                'chat_id': user_id,
                'text': msg,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                if result.get('ok'):
                    print(f"   ✓ Enviado para {nome} ({user_id})")
                    enviados += 1
                else:
                    print(f"   ❌ Erro ao enviar para {nome}: {result}")
                    erros += 1
                    
            except Exception as e:
                print(f"   ❌ Erro ao enviar para {nome}: {e}")
                erros += 1
        
        print(f"\n📊 Resumo do envio:")
        print(f"   ✓ Enviados: {enviados}")
        print(f"   ❌ Erros: {erros}")
        
        return enviados > 0
        
    except Exception as e:
        print(f"❌ Erro ao enviar para usuários: {e}")
        
        # Notificar admin do erro
        try:
            notificador = NotificadorUsuario()
            notificador.notificar_erro_usuario(
                erro=str(e),
                contexto="Envio de análise diária para usuários",
                traceback=""
            )
        except:
            pass
        
        return False

def enviar_telegram_bot_legado(msg):
    """
    Envia mensagem usando modo legado (para o grupo)
    APENAS PARA COMPATIBILIDADE - NÃO USAR EM PRODUÇÃO
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
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✓ Mensagem enviada via modo legado (grupo)")
            return True
        else:
            print(f"❌ Erro na resposta: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

def main():
    """
    Função principal
    """
    print("=" * 80)
    print("ANALISADOR DE CRIPTOMOEDAS - MAGNUS WEALTH v9.0.0")
    print("Sistema CHiLo (Custom HiLo) - Notificações Individuais")
    print("=" * 80)
    
    # Verificar sistema de usuários
    if DB_DISPONIVEL:
        db = DatabaseUsuarios()
        stats = db.estatisticas()
        print(f"\n👥 Usuários ativos: {stats['usuarios_ativos']}")
    else:
        print("\n⚠️ Sistema de usuários não disponível - usando modo legado")
    
    print(f"\n📊 Analisando {len(TOP_8)} criptomoedas...")
    
    # Analisar cada cripto
    resultados = []
    for cripto in TOP_8:
        resultado = analisar_cripto(cripto)
        if resultado:
            resultados.append(resultado)
    
    if not resultados:
        print("\n❌ Nenhuma análise bem-sucedida")
        return
    
    print(f"\n✓ {len(resultados)} criptomoedas analisadas com sucesso")
    
    # Gerar mensagem
    mensagem = gerar_mensagem_analise(resultados)
    
    # Enviar para usuários individuais
    print("\n" + "=" * 80)
    print("ENVIANDO NOTIFICAÇÕES")
    print("=" * 80)
    
    if DB_DISPONIVEL:
        sucesso = enviar_para_usuarios_individuais(mensagem)
    else:
        print("⚠️ Usando modo legado (grupo)")
        sucesso = enviar_telegram_bot_legado(mensagem)
    
    if sucesso:
        print("\n✅ Análise concluída e notificações enviadas!")
    else:
        print("\n⚠️ Análise concluída mas houve problemas no envio")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
