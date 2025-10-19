#!/usr/bin/env python3
"""
Analisador de Criptomoedas com HiLo Activator
Gera recomendações automáticas para o grupo Magnus Wealth
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

# Top 15 criptomoedas com períodos otimizados
CRIPTO_CONFIG = {
    'BTCUSDT': {'nome': 'Bitcoin', 'periodo_hilo': 70, 'tier': 1},
    'ETHUSDT': {'nome': 'Ethereum', 'periodo_hilo': 60, 'tier': 1},
    'BNBUSDT': {'nome': 'Binance Coin', 'periodo_hilo': 50, 'tier': 2},
    'SOLUSDT': {'nome': 'Solana', 'periodo_hilo': 40, 'tier': 2},
    'XRPUSDT': {'nome': 'XRP', 'periodo_hilo': 65, 'tier': 2},
    'ADAUSDT': {'nome': 'Cardano', 'periodo_hilo': 55, 'tier': 2},
    'AVAXUSDT': {'nome': 'Avalanche', 'periodo_hilo': 45, 'tier': 3},
    'DOTUSDT': {'nome': 'Polkadot', 'periodo_hilo': 50, 'tier': 3},
    'MATICUSDT': {'nome': 'Polygon', 'periodo_hilo': 45, 'tier': 3},
    'LINKUSDT': {'nome': 'Chainlink', 'periodo_hilo': 55, 'tier': 3},
    'LTCUSDT': {'nome': 'Litecoin', 'periodo_hilo': 65, 'tier': 3},
    'UNIUSDT': {'nome': 'Uniswap', 'periodo_hilo': 50, 'tier': 3},
    'ATOMUSDT': {'nome': 'Cosmos', 'periodo_hilo': 55, 'tier': 3},
    'ALGOUSDT': {'nome': 'Algorand', 'periodo_hilo': 50, 'tier': 3},
    'VETUSDT': {'nome': 'VeChain', 'periodo_hilo': 60, 'tier': 3},
}

class AnalisadorCriptoHilo:
    def __init__(self):
        self.base_url = "https://fapi.binance.com/fapi/v1"
        
    def buscar_dados_binance(self, symbol, interval='1d', limit=200):
        """Busca dados históricos da Binance Futures"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Converter para DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Converter tipos
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df
            
        except Exception as e:
            print(f"Erro ao buscar dados de {symbol}: {e}")
            return None
    
    def calcular_hilo(self, df, period):
        """Calcula HiLo Activator"""
        if df is None or len(df) < period:
            return None
        
        df = df.copy()
        
        # HiLo Activator = Média móvel dos highs e lows
        df['hilo_high'] = df['high'].rolling(window=period).mean()
        df['hilo_low'] = df['low'].rolling(window=period).mean()
        
        # Determinar tendência
        df['hilo'] = np.nan
        df['tendencia'] = 'neutro'
        
        for i in range(period, len(df)):
            if df['close'].iloc[i] > df['hilo_high'].iloc[i-1]:
                df.loc[df.index[i], 'hilo'] = df['hilo_low'].iloc[i]
                df.loc[df.index[i], 'tendencia'] = 'alta'
            elif df['close'].iloc[i] < df['hilo_low'].iloc[i-1]:
                df.loc[df.index[i], 'hilo'] = df['hilo_high'].iloc[i]
                df.loc[df.index[i], 'tendencia'] = 'baixa'
            else:
                # Mantém tendência anterior
                df.loc[df.index[i], 'hilo'] = df['hilo'].iloc[i-1]
                df.loc[df.index[i], 'tendencia'] = df['tendencia'].iloc[i-1]
        
        return df
    
    def analisar_moeda(self, symbol, config):
        """Analisa uma moeda e retorna sinal"""
        df = self.buscar_dados_binance(symbol)
        if df is None:
            return None
        
        periodo = config['periodo_hilo']
        df = self.calcular_hilo(df, periodo)
        
        if df is None:
            return None
        
        # Pegar últimos 2 dias
        atual = df.iloc[-1]
        anterior = df.iloc[-2]
        
        # Detectar mudança de tendência
        sinal = None
        if anterior['tendencia'] == 'baixa' and atual['tendencia'] == 'alta':
            sinal = 'COMPRA'
        elif anterior['tendencia'] == 'alta' and atual['tendencia'] == 'baixa':
            sinal = 'VENDA'
        
        # Calcular métricas
        preco_atual = atual['close']
        hilo_atual = atual['hilo']
        distancia_stop = abs(preco_atual - hilo_atual) / preco_atual * 100
        
        # Volume
        volume_medio = df['volume'].tail(20).mean()
        volume_atual = atual['volume']
        volume_ratio = volume_atual / volume_medio
        
        return {
            'symbol': symbol,
            'nome': config['nome'],
            'tier': config['tier'],
            'periodo_hilo': periodo,
            'preco_atual': preco_atual,
            'hilo': hilo_atual,
            'tendencia_anterior': anterior['tendencia'],
            'tendencia_atual': atual['tendencia'],
            'sinal': sinal,
            'distancia_stop': distancia_stop,
            'volume_ratio': volume_ratio,
            'timestamp': atual['timestamp']
        }
    
    def gerar_recomendacoes(self):
        """Gera recomendações para todas as moedas"""
        recomendacoes = []
        
        for symbol, config in CRIPTO_CONFIG.items():
            print(f"Analisando {config['nome']}...")
            resultado = self.analisar_moeda(symbol, config)
            
            if resultado and resultado['sinal']:
                recomendacoes.append(resultado)
        
        return recomendacoes
    
    def formatar_mensagem(self, rec):
        """Formata mensagem de recomendação"""
        emoji_tier = {1: '🥇', 2: '🥈', 3: '🥉'}
        emoji_sinal = {'COMPRA': '🟢', 'VENDA': '🔴'}
        
        msg = f"""
{emoji_sinal[rec['sinal']]} **{rec['nome']} ({rec['symbol'].replace('USDT', '')})** {emoji_tier[rec['tier']]}

📊 **Sinal:** {rec['sinal']}
💰 **Preço Atual:** ${rec['preco_atual']:.2f}

"""
        
        if rec['sinal'] == 'COMPRA':
            # Calcular teto (2% acima do preço atual)
            teto = rec['preco_atual'] * 1.02
            
            msg += f"""🎯 **Entrada Sugerida:** ${rec['preco_atual']:.2f}
🔝 **Teto de Entrada:** ${teto:.2f}
🛑 **Stop Loss:** ${rec['hilo']:.2f} ({rec['distancia_stop']:.2f}%)
✅ **Stop Gain:** Quando HiLo virar vermelho

📈 **Gestão:**
• Risco: 3% do capital
• Distância do stop: {rec['distancia_stop']:.2f}%
• Volume: {rec['volume_ratio']:.1f}x a média

⚙️ **Configuração:**
• Timeframe: Diário
• HiLo Período: {rec['periodo_hilo']}
• Tier: {rec['tier']} ({"Baixo" if rec['tier']==1 else "Médio" if rec['tier']==2 else "Alto"} Risco)
"""
        else:  # VENDA
            msg += f"""🎯 **Ação:** Vender posição
🛑 **Saída:** ${rec['preco_atual']:.2f}
📉 **Motivo:** HiLo virou vermelho (tendência de baixa)

⚠️ **Se ainda não vendeu:**
• Saia imediatamente no próximo candle
• Stop está em ${rec['hilo']:.2f}
"""
        
        msg += f"""
🕐 **Análise:** {rec['timestamp'].strftime('%d/%m/%Y %H:%M')}

_Estratégia: Siga a Tendência (HiLo Activator)_
"""
        
        return msg.strip()
    
    def enviar_telegram(self, mensagem):
        """Envia mensagem para o grupo Magnus Wealth"""
        try:
            api_id = int(os.getenv('TELEGRAM_API_ID'))
            api_hash = os.getenv('TELEGRAM_API_HASH')
            phone = os.getenv('TELEGRAM_PHONE')
            group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
            
            with TelegramClient('magnus_session', api_id, api_hash) as client:
                client.send_message(group_id, mensagem)
                print("✅ Mensagem enviada com sucesso!")
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
    
    def executar_analise_diaria(self):
        """Executa análise diária e envia recomendações"""
        print(f"\n{'='*60}")
        print(f"🪙 ANÁLISE DIÁRIA DE CRIPTOMOEDAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"{'='*60}\n")
        
        recomendacoes = self.gerar_recomendacoes()
        
        if not recomendacoes:
            msg = f"""
🪙 **Análise Diária de Criptomoedas**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

✅ Análise concluída!
📊 **Nenhum sinal novo** detectado hoje.

Todas as moedas mantêm suas tendências atuais.
Continue monitorando as posições abertas.

_Próxima análise: Amanhã às 21:00_
"""
            self.enviar_telegram(msg)
            print("ℹ️  Nenhum sinal detectado hoje.")
            return
        
        # Mensagem de cabeçalho
        header = f"""
🪙 **ANÁLISE DIÁRIA DE CRIPTOMOEDAS**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

🎯 **{len(recomendacoes)} Sinal(is) Detectado(s)**

{'='*40}
"""
        self.enviar_telegram(header)
        
        # Enviar cada recomendação
        for rec in recomendacoes:
            msg = self.formatar_mensagem(rec)
            self.enviar_telegram(msg)
            print(f"✅ Recomendação enviada: {rec['nome']} - {rec['sinal']}")
        
        # Mensagem de rodapé
        footer = f"""
{'='*40}

📊 **Resumo:**
• Sinais de COMPRA: {sum(1 for r in recomendacoes if r['sinal'] == 'COMPRA')}
• Sinais de VENDA: {sum(1 for r in recomendacoes if r['sinal'] == 'VENDA')}

⚠️ **Lembre-se:**
• Risco máximo: 3% por operação
• Máximo 5 posições simultâneas
• Use sempre o HiLo como stop

_Próxima análise: Amanhã às 21:00_
"""
        self.enviar_telegram(footer)
        
        print(f"\n✅ Análise concluída! {len(recomendacoes)} recomendações enviadas.")

if __name__ == "__main__":
    analisador = AnalisadorCriptoHilo()
    analisador.executar_analise_diaria()

