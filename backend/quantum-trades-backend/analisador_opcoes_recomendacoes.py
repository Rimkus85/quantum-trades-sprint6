#!/usr/bin/env python3
"""
Analisador Completo de Opções - Magnus Wealth
Gera recomendações com TODAS as estratégias e passo a passo de execução
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

# Ativos principais para análise
ATIVOS_PRINCIPAIS = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'BBAS3', 'WEGE3', 'B3SA3']

class AnalisadorOpcoesCompleto:
    def __init__(self):
        self.base_url_brapi = "https://brapi.dev/api"
        
    def buscar_cotacao(self, ticker):
        """Busca cotação atual do ativo"""
        try:
            url = f"{self.base_url_brapi}/quote/{ticker}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
            return None
            
        except Exception as e:
            print(f"Erro ao buscar cotação de {ticker}: {e}")
            return None
    
    def analisar_tendencia(self, ticker):
        """Analisa tendência do ativo"""
        try:
            url = f"{self.base_url_brapi}/quote/{ticker}?range=1mo&interval=1d"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' not in data or len(data['results']) == 0:
                return 'neutro', 0
            
            historico = data['results'][0].get('historicalDataPrice', [])
            if len(historico) < 20:
                return 'neutro', 0
            
            # Calcular médias móveis e força da tendência
            closes = [h['close'] for h in historico]
            ma20 = np.mean(closes[-20:])
            ma5 = np.mean(closes[-5:])
            preco_atual = closes[-1]
            
            # Calcular inclinação (força da tendência)
            forca = abs(ma5 - ma20) / ma20 * 100
            
            # Determinar tendência
            if preco_atual > ma20 and ma5 > ma20:
                return 'alta', forca
            elif preco_atual < ma20 and ma5 < ma20:
                return 'baixa', forca
            else:
                return 'neutro', forca
                
        except Exception as e:
            print(f"Erro ao analisar tendência de {ticker}: {e}")
            return 'neutro', 0
    
    def calcular_volatilidade(self, ticker):
        """Calcula volatilidade do ativo"""
        try:
            url = f"{self.base_url_brapi}/quote/{ticker}?range=1mo&interval=1d"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'results' not in data or len(data['results']) == 0:
                return 0
            
            historico = data['results'][0].get('historicalDataPrice', [])
            if len(historico) < 20:
                return 0
            
            closes = [h['close'] for h in historico]
            returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
            volatilidade = np.std(returns) * np.sqrt(252) * 100  # Anualizada
            
            return volatilidade
            
        except:
            return 0
    
    # ========== ESTRATÉGIAS DE OPÇÕES ==========
    
    def gerar_compra_call(self, ticker, cotacao, tendencia, forca):
        """Setup 1: Compra de Call em Rompimento"""
        if tendencia != 'alta' or forca < 2:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_ideal = preco * 1.02  # ATM ou ligeiramente OTM
        
        return {
            'tipo': 'COMPRA CALL',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Tendência de alta forte ({forca:.1f}%), rompimento detectado',
            'setup': 'Setup 1: Compra de Call em Rompimento',
            'objetivo': 'Lucrar com alta do ativo',
            'risco': 'Limitado ao prêmio pago',
            'retorno': 'Ilimitado',
            'holding': '5-15 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_compra_call(ticker, strike_ideal)
        }
    
    def gerar_compra_put(self, ticker, cotacao, tendencia, forca):
        """Setup 2: Compra de Put em Queda"""
        if tendencia != 'baixa' or forca < 2:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_ideal = preco * 0.98  # ATM ou ligeiramente OTM
        
        return {
            'tipo': 'COMPRA PUT',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Tendência de baixa forte ({forca:.1f}%), perda de suporte',
            'setup': 'Setup 2: Compra de Put em Queda',
            'objetivo': 'Lucrar com queda do ativo',
            'risco': 'Limitado ao prêmio pago',
            'retorno': 'Alto (até o ativo chegar a zero)',
            'holding': '3-10 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_compra_put(ticker, strike_ideal)
        }
    
    def gerar_trava_alta(self, ticker, cotacao, tendencia, forca):
        """Setup 4: Trava de Alta (Bull Call Spread)"""
        if tendencia != 'alta':
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_compra = preco  # ATM
        strike_venda = preco * 1.05  # 5% acima
        
        return {
            'tipo': 'TRAVA DE ALTA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_compra': strike_compra,
            'strike_venda': strike_venda,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Alta moderada esperada, reduzir custo da operação',
            'setup': 'Setup 4: Trava de Alta (Bull Call Spread)',
            'objetivo': 'Lucrar com alta limitada, custo reduzido',
            'risco': 'Limitado ao custo da trava',
            'retorno': 'Limitado (diferença entre strikes - custo)',
            'holding': 'Até vencimento',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_trava_alta(ticker, strike_compra, strike_venda)
        }
    
    def gerar_trava_baixa(self, ticker, cotacao, tendencia, forca):
        """Trava de Baixa (Bear Put Spread)"""
        if tendencia != 'baixa':
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_compra = preco  # ATM
        strike_venda = preco * 0.95  # 5% abaixo
        
        return {
            'tipo': 'TRAVA DE BAIXA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_compra': strike_compra,
            'strike_venda': strike_venda,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Baixa moderada esperada, reduzir custo',
            'setup': 'Trava de Baixa (Bear Put Spread)',
            'objetivo': 'Lucrar com queda limitada, custo reduzido',
            'risco': 'Limitado ao custo da trava',
            'retorno': 'Limitado (diferença entre strikes - custo)',
            'holding': 'Até vencimento',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_trava_baixa(ticker, strike_compra, strike_venda)
        }
    
    def gerar_borboleta(self, ticker, cotacao, tendencia, volatilidade):
        """Borboleta (Butterfly Spread)"""
        if volatilidade > 30:  # Alta volatilidade, borboleta não é ideal
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_baixo = preco * 0.97
        strike_medio = preco
        strike_alto = preco * 1.03
        
        return {
            'tipo': 'BORBOLETA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_baixo': strike_baixo,
            'strike_medio': strike_medio,
            'strike_alto': strike_alto,
            'tendencia': tendencia,
            'volatilidade': volatilidade,
            'motivo': 'Mercado lateral, baixa volatilidade esperada',
            'setup': 'Borboleta (Butterfly Spread)',
            'objetivo': 'Lucrar com mercado lateral (preço próximo ao strike médio)',
            'risco': 'Limitado ao custo da borboleta',
            'retorno': 'Moderado (máximo no strike médio)',
            'holding': 'Até vencimento',
            'gestao_risco': '2% do capital',
            'passo_a_passo': self._passo_borboleta(ticker, strike_baixo, strike_medio, strike_alto)
        }
    
    def gerar_straddle(self, ticker, cotacao, volatilidade):
        """Straddle (Compra Call + Put mesmo strike)"""
        if volatilidade < 20:  # Baixa volatilidade, straddle não compensa
            return None
        
        preco = cotacao['regularMarketPrice']
        strike = preco  # ATM
        
        return {
            'tipo': 'STRADDLE',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike': strike,
            'volatilidade': volatilidade,
            'motivo': f'Alta volatilidade ({volatilidade:.1f}%), movimento forte esperado',
            'setup': 'Straddle (Long Straddle)',
            'objetivo': 'Lucrar com movimento forte (alta ou baixa)',
            'risco': 'Alto (custo de 2 opções)',
            'retorno': 'Ilimitado (em qualquer direção)',
            'holding': '5-15 dias',
            'gestao_risco': '4% do capital (2 opções)',
            'passo_a_passo': self._passo_straddle(ticker, strike)
        }
    
    def gerar_strangle(self, ticker, cotacao, volatilidade):
        """Strangle (Compra Call OTM + Put OTM)"""
        if volatilidade < 25:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_call = preco * 1.03  # 3% acima
        strike_put = preco * 0.97  # 3% abaixo
        
        return {
            'tipo': 'STRANGLE',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_call': strike_call,
            'strike_put': strike_put,
            'volatilidade': volatilidade,
            'motivo': f'Alta volatilidade ({volatilidade:.1f}%), custo menor que straddle',
            'setup': 'Strangle (Long Strangle)',
            'objetivo': 'Lucrar com movimento forte, custo reduzido',
            'risco': 'Moderado (custo de 2 opções OTM)',
            'retorno': 'Ilimitado (em qualquer direção)',
            'holding': '5-15 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_strangle(ticker, strike_call, strike_put)
        }
    
    # ========== PASSO A PASSO ==========
    
    def _passo_compra_call(self, ticker, strike):
        return f"""
**📋 PASSO A PASSO - COMPRA DE CALL**

**1️⃣ Abrir Plataforma**
• Acesse ProfitChart ou sua corretora
• Vá em "Opções" ou "Derivativos"

**2️⃣ Buscar Opção**
• Digite: {ticker}
• Selecione "CALLS"
• Procure strike próximo de R$ {strike:.2f}
• Escolha vencimento: 15-30 dias

**3️⃣ Analisar Prêmio**
• Veja o preço da opção (ASK)
• Calcule: Prêmio / Preço Ativo
• Ideal: 3-7% do preço do ativo
• Se > 10%, muito caro (evite)

**4️⃣ Calcular Quantidade**
• Capital disponível: R$ X
• Risco: 3% = R$ Y
• Quantidade: R$ Y / Prêmio
• Exemplo: R$ 300 / R$ 1,50 = 200 opções

**5️⃣ Executar Ordem**
• Tipo: COMPRA
• Código: {ticker}CXXX (verificar código real)
• Quantidade: Calculada acima
• Preço: Limite (não pague mais que 5% acima do ASK)
• Validade: Dia

**6️⃣ Confirmar e Monitorar**
• Verifique ordem executada
• Anote: Preço de entrada, stop loss
• Monitore diariamente
• Stop: 50% de perda OU ativo cair 3%
• Alvo: 100-200% de lucro OU ativo perder tendência
"""
    
    def _passo_compra_put(self, ticker, strike):
        return f"""
**📋 PASSO A PASSO - COMPRA DE PUT**

**1️⃣ Abrir Plataforma**
• Acesse ProfitChart ou sua corretora
• Vá em "Opções" ou "Derivativos"

**2️⃣ Buscar Opção**
• Digite: {ticker}
• Selecione "PUTS"
• Procure strike próximo de R$ {strike:.2f}
• Escolha vencimento: 15-30 dias

**3️⃣ Analisar Prêmio**
• Veja o preço da opção (ASK)
• Calcule: Prêmio / Preço Ativo
• Ideal: 3-7% do preço do ativo

**4️⃣ Calcular Quantidade**
• Capital disponível: R$ X
• Risco: 3% = R$ Y
• Quantidade: R$ Y / Prêmio

**5️⃣ Executar Ordem**
• Tipo: COMPRA
• Código: {ticker}WXXX (verificar código real)
• Quantidade: Calculada acima
• Preço: Limite
• Validade: Dia

**6️⃣ Confirmar e Monitorar**
• Stop: 50% de perda OU ativo subir 3%
• Alvo: 100-150% de lucro OU ativo encontrar suporte
"""
    
    def _passo_trava_alta(self, ticker, strike_compra, strike_venda):
        return f"""
**📋 PASSO A PASSO - TRAVA DE ALTA**

**1️⃣ Entender a Trava**
• Você vai COMPRAR 1 call (strike baixo)
• E VENDER 1 call (strike alto)
• Reduz custo mas limita ganho

**2️⃣ Primeira Perna - COMPRAR CALL**
• Strike: R$ {strike_compra:.2f} (ATM)
• Quantidade: Ex: 100 opções
• Você PAGA o prêmio (ex: R$ 1,80)

**3️⃣ Segunda Perna - VENDER CALL**
• Strike: R$ {strike_venda:.2f} (OTM, 5% acima)
• Quantidade: MESMA (100 opções)
• Você RECEBE o prêmio (ex: R$ 0,60)

**4️⃣ Calcular Custo e Ganho**
• Custo líquido: R$ 1,80 - R$ 0,60 = R$ 1,20
• Ganho máximo: (R$ {strike_venda:.2f} - R$ {strike_compra:.2f}) - R$ 1,20
• Exemplo: (R$ 42 - R$ 40) - R$ 1,20 = R$ 0,80
• Retorno: R$ 0,80 / R$ 1,20 = 67%

**5️⃣ Executar Ordem**
• Opção 1: Montar perna por perna (acima)
• Opção 2: Usar "Spread" na plataforma
• Selecione "Bull Call Spread"
• Informe os 2 strikes
• Sistema monta automaticamente

**6️⃣ Gestão**
• Risco: Custo da trava (R$ 1,20)
• Ganho máximo: No vencimento, se ativo >= strike alto
• Holding: Até vencimento
• Não precisa de stop (risco já limitado)
"""
    
    def _passo_trava_baixa(self, ticker, strike_compra, strike_venda):
        return f"""
**📋 PASSO A PASSO - TRAVA DE BAIXA**

**1️⃣ Entender a Trava**
• Você vai COMPRAR 1 put (strike alto)
• E VENDER 1 put (strike baixo)
• Reduz custo mas limita ganho

**2️⃣ Primeira Perna - COMPRAR PUT**
• Strike: R$ {strike_compra:.2f} (ATM)
• Quantidade: Ex: 100 opções
• Você PAGA o prêmio (ex: R$ 1,80)

**3️⃣ Segunda Perna - VENDER PUT**
• Strike: R$ {strike_venda:.2f} (OTM, 5% abaixo)
• Quantidade: MESMA (100 opções)
• Você RECEBE o prêmio (ex: R$ 0,60)

**4️⃣ Calcular Custo e Ganho**
• Custo líquido: R$ 1,80 - R$ 0,60 = R$ 1,20
• Ganho máximo: (R$ {strike_compra:.2f} - R$ {strike_venda:.2f}) - R$ 1,20

**5️⃣ Executar Ordem**
• Use "Bear Put Spread" na plataforma
• Ou monte perna por perna

**6️⃣ Gestão**
• Ganho máximo: Se ativo <= strike baixo
• Holding: Até vencimento
"""
    
    def _passo_borboleta(self, ticker, strike_baixo, strike_medio, strike_alto):
        return f"""
**📋 PASSO A PASSO - BORBOLETA**

**1️⃣ Entender a Borboleta**
• Você vai COMPRAR 1 call (strike baixo)
• VENDER 2 calls (strike médio)
• COMPRAR 1 call (strike alto)
• Lucra se ativo ficar próximo ao strike médio

**2️⃣ Primeira Perna**
• COMPRAR call strike R$ {strike_baixo:.2f}
• Quantidade: 100
• Paga: Ex: R$ 2,50

**3️⃣ Segunda Perna**
• VENDER call strike R$ {strike_medio:.2f}
• Quantidade: 200 (DOBRO!)
• Recebe: Ex: R$ 1,50 x 2 = R$ 3,00

**4️⃣ Terceira Perna**
• COMPRAR call strike R$ {strike_alto:.2f}
• Quantidade: 100
• Paga: Ex: R$ 0,80

**5️⃣ Calcular Custo**
• Custo: R$ 2,50 + R$ 0,80 - R$ 3,00 = R$ 0,30
• Ganho máximo: Se ativo = R$ {strike_medio:.2f}

**6️⃣ Executar Ordem**
• Use "Butterfly Spread" na plataforma
• Ou monte perna por perna (cuidado com a ordem!)

**7️⃣ Gestão**
• Ideal para mercado lateral
• Ganho máximo: No strike médio
• Perda máxima: Custo da borboleta
"""
    
    def _passo_straddle(self, ticker, strike):
        return f"""
**📋 PASSO A PASSO - STRADDLE**

**1️⃣ Entender o Straddle**
• Você vai COMPRAR 1 call (ATM)
• E COMPRAR 1 put (ATM, mesmo strike)
• Lucra se ativo se mover MUITO (qualquer direção)

**2️⃣ Primeira Perna - COMPRAR CALL**
• Strike: R$ {strike:.2f} (ATM)
• Quantidade: 100
• Paga: Ex: R$ 1,80

**3️⃣ Segunda Perna - COMPRAR PUT**
• Strike: R$ {strike:.2f} (MESMO strike)
• Quantidade: 100 (MESMA quantidade)
• Paga: Ex: R$ 1,50

**4️⃣ Calcular Custo e Breakeven**
• Custo total: R$ 1,80 + R$ 1,50 = R$ 3,30
• Breakeven superior: R$ {strike:.2f} + R$ 3,30
• Breakeven inferior: R$ {strike:.2f} - R$ 3,30
• Precisa de movimento > 8% para lucrar

**5️⃣ Executar Ordem**
• Compre as 2 opções separadamente
• Ou use "Straddle" na plataforma

**6️⃣ Gestão**
• Ideal para: Eventos (balanços, decisões importantes)
• Risco: Alto (custo de 2 opções)
• Alvo: Movimento forte em qualquer direção
"""
    
    def _passo_strangle(self, ticker, strike_call, strike_put):
        return f"""
**📋 PASSO A PASSO - STRANGLE**

**1️⃣ Entender o Strangle**
• Similar ao straddle mas strikes diferentes
• COMPRAR call OTM (acima do preço)
• COMPRAR put OTM (abaixo do preço)
• Custo menor, mas precisa de movimento maior

**2️⃣ Primeira Perna - COMPRAR CALL**
• Strike: R$ {strike_call:.2f} (3% acima)
• Quantidade: 100
• Paga: Ex: R$ 0,80

**3️⃣ Segunda Perna - COMPRAR PUT**
• Strike: R$ {strike_put:.2f} (3% abaixo)
• Quantidade: 100
• Paga: Ex: R$ 0,70

**4️⃣ Calcular Custo**
• Custo total: R$ 0,80 + R$ 0,70 = R$ 1,50
• Mais barato que straddle!
• Mas precisa de movimento > 10%

**5️⃣ Executar Ordem**
• Compre as 2 opções separadamente
• Ou use "Strangle" na plataforma

**6️⃣ Gestão**
• Ideal para: Alta volatilidade esperada
• Custo menor que straddle
• Precisa de movimento maior para lucrar
"""
    
    # ========== ANÁLISE E ENVIO ==========
    
    def analisar_ativo(self, ticker):
        """Analisa um ativo e gera TODAS as recomendações possíveis"""
        print(f"Analisando {ticker}...")
        
        cotacao = self.buscar_cotacao(ticker)
        if not cotacao:
            return []
        
        tendencia, forca = self.analisar_tendencia(ticker)
        volatilidade = self.calcular_volatilidade(ticker)
        
        recomendacoes = []
        
        # Gerar todas as estratégias aplicáveis
        estrategias = [
            self.gerar_compra_call(ticker, cotacao, tendencia, forca),
            self.gerar_compra_put(ticker, cotacao, tendencia, forca),
            self.gerar_trava_alta(ticker, cotacao, tendencia, forca),
            self.gerar_trava_baixa(ticker, cotacao, tendencia, forca),
            self.gerar_borboleta(ticker, cotacao, tendencia, volatilidade),
            self.gerar_straddle(ticker, cotacao, volatilidade),
            self.gerar_strangle(ticker, cotacao, volatilidade),
        ]
        
        # Filtrar apenas estratégias válidas
        recomendacoes = [e for e in estrategias if e is not None]
        
        return recomendacoes
    
    def formatar_mensagem(self, rec):
        """Formata mensagem de recomendação"""
        emoji_tipo = {
            'COMPRA CALL': '📈🟢',
            'COMPRA PUT': '📉🟢',
            'TRAVA DE ALTA': '📊🔵',
            'TRAVA DE BAIXA': '📊🔴',
            'BORBOLETA': '🦋',
            'STRADDLE': '⚡',
            'STRANGLE': '⚡🔶'
        }
        
        msg = f"""
{emoji_tipo.get(rec['tipo'], '📊')} **{rec['ticker']} - {rec['tipo']}**

💰 **Preço do Ativo:** R$ {rec['preco_ativo']:.2f}
"""
        
        # Adicionar strikes específicos por estratégia
        if 'strike_sugerido' in rec:
            msg += f"🎲 **Strike Sugerido:** R$ {rec['strike_sugerido']:.2f}\n"
        elif 'strike_compra' in rec and 'strike_venda' in rec:
            msg += f"""🎲 **Strikes:**
• Compra: R$ {rec['strike_compra']:.2f}
• Venda: R$ {rec['strike_venda']:.2f}
"""
        elif 'strike_baixo' in rec:
            msg += f"""🎲 **Strikes:**
• Baixo: R$ {rec['strike_baixo']:.2f}
• Médio: R$ {rec['strike_medio']:.2f}
• Alto: R$ {rec['strike_alto']:.2f}
"""
        elif 'strike_call' in rec and 'strike_put' in rec:
            msg += f"""🎲 **Strikes:**
• Call: R$ {rec['strike_call']:.2f}
• Put: R$ {rec['strike_put']:.2f}
"""
        elif 'strike' in rec:
            msg += f"🎲 **Strike:** R$ {rec['strike']:.2f}\n"
        
        msg += f"""
📊 **Análise:**
• Setup: {rec['setup']}
• Motivo: {rec['motivo']}

🎯 **Objetivo:** {rec['objetivo']}
💵 **Risco:** {rec['risco']}
💰 **Retorno:** {rec['retorno']}
⏱️ **Holding:** {rec['holding']}
🛡️ **Gestão:** {rec['gestao_risco']}

{rec['passo_a_passo']}

⚠️ **DISCLAIMER:**
Esta recomendação é baseada em análise técnica automatizada.
Opções são instrumentos de ALTO RISCO e podem resultar em
PERDA TOTAL do capital investido. Avalie seu perfil de risco
antes de operar. Não é recomendação de investimento, apenas
sinal educacional para fins de estudo.

🕐 **Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
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
    
    def executar_analise(self):
        """Executa análise completa de opções"""
        print(f"\n{'='*60}")
        print(f"📊 ANÁLISE COMPLETA DE OPÇÕES - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"{'='*60}\n")
        
        todas_recomendacoes = []
        
        for ticker in ATIVOS_PRINCIPAIS:
            recomendacoes = self.analisar_ativo(ticker)
            todas_recomendacoes.extend(recomendacoes)
        
        if not todas_recomendacoes:
            msg = f"""
📊 **Análise Completa de Opções**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

✅ Análise concluída!
📈 **Nenhuma oportunidade** detectada no momento.

Ativos analisados: {', '.join(ATIVOS_PRINCIPAIS)}
Estratégias avaliadas: 7 tipos
Aguardando melhores setups.

_Próxima análise: Conforme agenda (10:10, 14:00, 16:45)_
"""
            self.enviar_telegram(msg)
            print("ℹ️  Nenhuma recomendação gerada.")
            return
        
        # Mensagem de cabeçalho
        header = f"""
📊 **ANÁLISE COMPLETA DE OPÇÕES**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

🎯 **{len(todas_recomendacoes)} Oportunidade(s) Detectada(s)**

Estratégias: Calls, Puts, Travas, Borboletas, Straddles, Strangles

{'='*40}
"""
        self.enviar_telegram(header)
        
        # Enviar cada recomendação
        for rec in todas_recomendacoes:
            msg = self.formatar_mensagem(rec)
            self.enviar_telegram(msg)
            print(f"✅ Recomendação enviada: {rec['ticker']} - {rec['tipo']}")
        
        # Mensagem de rodapé
        tipos_count = {}
        for r in todas_recomendacoes:
            tipo = r['tipo']
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        resumo_tipos = '\n'.join([f"• {tipo}: {count}" for tipo, count in tipos_count.items()])
        
        footer = f"""
{'='*40}

📊 **Resumo por Estratégia:**
{resumo_tipos}

⚠️ **Lembre-se:**
• Risco máximo: 3% por operação
• Sempre use stop loss
• Opções são instrumentos de ALTO RISCO
• Siga o passo a passo com atenção
• Em caso de dúvida, NÃO opere

_Próxima análise: Conforme agenda_
"""
        self.enviar_telegram(footer)
        
        print(f"\n✅ Análise concluída! {len(todas_recomendacoes)} recomendações enviadas.")

if __name__ == "__main__":
    analisador = AnalisadorOpcoesCompleto()
    analisador.executar_analise()

