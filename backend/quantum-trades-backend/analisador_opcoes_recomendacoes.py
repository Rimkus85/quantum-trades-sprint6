#!/usr/bin/env python3
"""
Analisador Completo de Opções - Magnus Wealth
Gera recomendações com TODAS as estratégias e passo a passo de execução
Versão 7.8.0 - Ajustado conforme feedback do mentor
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import json
import calendar

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
    
    def gerar_codigo_opcao(self, ticker, tipo, strike, vencimento_dias=30):
        """Gera código aproximado da opção (formato B3)"""
        # Remover dígito do ticker
        ticker_base = ''.join([c for c in ticker if not c.isdigit()])
        
        # Calcular vencimento (próxima terceira segunda-feira)
        hoje = datetime.now()
        mes_vencimento = hoje.month
        ano_vencimento = hoje.year
        
        # Se já passou do dia 15, pegar próximo mês
        if hoje.day > 15:
            mes_vencimento += 1
            if mes_vencimento > 12:
                mes_vencimento = 1
                ano_vencimento += 1
        
        # Letra do mês (A=Jan, B=Fev, ..., L=Dez)
        letra_mes = chr(64 + mes_vencimento)  # A=65
        
        # Tipo: C=Call, W=Put (padrão B3)
        letra_tipo = 'C' if tipo == 'CALL' else 'W'
        
        # Strike arredondado
        strike_int = int(strike)
        
        # Formato: PETR4C4000 (exemplo)
        codigo = f"{ticker}{letra_mes}{strike_int}"
        
        return codigo
    
    # ========== ESTRATÉGIAS DE OPÇÕES ==========
    
    def gerar_compra_call(self, ticker, cotacao, tendencia, forca):
        """Setup 1: Compra de Call em Rompimento"""
        if tendencia != 'alta' or forca < 2:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_ideal = preco * 1.02  # ATM ou ligeiramente OTM
        codigo_opcao = self.gerar_codigo_opcao(ticker, 'CALL', strike_ideal)
        
        return {
            'tipo': 'COMPRA CALL',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'codigo_opcao': codigo_opcao,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Tendência de alta forte ({forca:.1f}%), rompimento detectado',
            'setup': 'Setup 1: Compra de Call em Rompimento',
            'objetivo': 'Lucrar com alta do ativo',
            'risco': 'Limitado ao prêmio pago (pode perder 100%)',
            'retorno': 'Ilimitado',
            'holding': '5-15 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_compra_call(ticker, strike_ideal, codigo_opcao)
        }
    
    def gerar_compra_put(self, ticker, cotacao, tendencia, forca):
        """Setup 2: Compra de Put em Queda"""
        if tendencia != 'baixa' or forca < 2:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_ideal = preco * 0.98  # ATM ou ligeiramente OTM
        codigo_opcao = self.gerar_codigo_opcao(ticker, 'PUT', strike_ideal)
        
        return {
            'tipo': 'COMPRA PUT',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'codigo_opcao': codigo_opcao,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Tendência de baixa forte ({forca:.1f}%), perda de suporte',
            'setup': 'Setup 2: Compra de Put em Queda',
            'objetivo': 'Lucrar com queda do ativo',
            'risco': 'Limitado ao prêmio pago (pode perder 100%)',
            'retorno': 'Alto (até o ativo chegar a zero)',
            'holding': '3-10 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_compra_put(ticker, strike_ideal, codigo_opcao)
        }
    
    def gerar_trava_alta(self, ticker, cotacao, tendencia, forca):
        """Setup 4: Trava de Alta (Bull Call Spread)"""
        if tendencia != 'alta':
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_compra = preco  # ATM
        strike_venda = preco * 1.05  # 5% acima
        codigo_compra = self.gerar_codigo_opcao(ticker, 'CALL', strike_compra)
        codigo_venda = self.gerar_codigo_opcao(ticker, 'CALL', strike_venda)
        
        return {
            'tipo': 'TRAVA DE ALTA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_compra': strike_compra,
            'strike_venda': strike_venda,
            'codigo_compra': codigo_compra,
            'codigo_venda': codigo_venda,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Alta moderada esperada, reduzir custo da operação',
            'setup': 'Setup 4: Trava de Alta (Bull Call Spread)',
            'objetivo': 'Lucrar com alta limitada, custo reduzido',
            'risco': 'Limitado ao custo da trava',
            'retorno': 'Limitado (diferença entre strikes - custo)',
            'holding': 'Até vencimento',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_trava_alta(ticker, strike_compra, strike_venda, codigo_compra, codigo_venda)
        }
    
    def gerar_trava_baixa(self, ticker, cotacao, tendencia, forca):
        """Trava de Baixa (Bear Put Spread)"""
        if tendencia != 'baixa':
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_compra = preco  # ATM
        strike_venda = preco * 0.95  # 5% abaixo
        codigo_compra = self.gerar_codigo_opcao(ticker, 'PUT', strike_compra)
        codigo_venda = self.gerar_codigo_opcao(ticker, 'PUT', strike_venda)
        
        return {
            'tipo': 'TRAVA DE BAIXA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_compra': strike_compra,
            'strike_venda': strike_venda,
            'codigo_compra': codigo_compra,
            'codigo_venda': codigo_venda,
            'tendencia': tendencia,
            'forca': forca,
            'motivo': f'Baixa moderada esperada, reduzir custo',
            'setup': 'Trava de Baixa (Bear Put Spread)',
            'objetivo': 'Lucrar com queda limitada, custo reduzido',
            'risco': 'Limitado ao custo da trava',
            'retorno': 'Limitado (diferença entre strikes - custo)',
            'holding': 'Até vencimento',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_trava_baixa(ticker, strike_compra, strike_venda, codigo_compra, codigo_venda)
        }
    
    def gerar_borboleta(self, ticker, cotacao, tendencia, volatilidade):
        """Borboleta (Butterfly Spread)"""
        if volatilidade > 30:  # Alta volatilidade, borboleta não é ideal
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_baixo = preco * 0.97
        strike_medio = preco
        strike_alto = preco * 1.03
        
        codigo_baixo = self.gerar_codigo_opcao(ticker, 'CALL', strike_baixo)
        codigo_medio = self.gerar_codigo_opcao(ticker, 'CALL', strike_medio)
        codigo_alto = self.gerar_codigo_opcao(ticker, 'CALL', strike_alto)
        
        return {
            'tipo': 'BORBOLETA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_baixo': strike_baixo,
            'strike_medio': strike_medio,
            'strike_alto': strike_alto,
            'codigo_baixo': codigo_baixo,
            'codigo_medio': codigo_medio,
            'codigo_alto': codigo_alto,
            'tendencia': tendencia,
            'volatilidade': volatilidade,
            'motivo': 'Mercado lateral, baixa volatilidade esperada',
            'setup': 'Borboleta (Butterfly Spread)',
            'objetivo': 'Lucrar com mercado lateral (preço próximo ao strike médio)',
            'risco': 'Limitado ao custo da borboleta',
            'retorno': 'Moderado (máximo no strike médio)',
            'holding': 'Até vencimento',
            'gestao_risco': '2% do capital',
            'passo_a_passo': self._passo_borboleta(ticker, strike_baixo, strike_medio, strike_alto, codigo_baixo, codigo_medio, codigo_alto)
        }
    
    def gerar_straddle(self, ticker, cotacao, volatilidade):
        """Straddle (Compra Call + Put mesmo strike)"""
        if volatilidade < 20:  # Baixa volatilidade, straddle não compensa
            return None
        
        preco = cotacao['regularMarketPrice']
        strike = preco  # ATM
        codigo_call = self.gerar_codigo_opcao(ticker, 'CALL', strike)
        codigo_put = self.gerar_codigo_opcao(ticker, 'PUT', strike)
        
        return {
            'tipo': 'STRADDLE',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike': strike,
            'codigo_call': codigo_call,
            'codigo_put': codigo_put,
            'volatilidade': volatilidade,
            'motivo': f'Alta volatilidade ({volatilidade:.1f}%), movimento forte esperado',
            'setup': 'Straddle (Long Straddle)',
            'objetivo': 'Lucrar com movimento forte (alta ou baixa)',
            'risco': 'Alto (custo de 2 opções, pode perder 100%)',
            'retorno': 'Ilimitado (em qualquer direção)',
            'holding': '5-15 dias',
            'gestao_risco': '4% do capital (2 opções)',
            'passo_a_passo': self._passo_straddle(ticker, strike, codigo_call, codigo_put)
        }
    
    def gerar_strangle(self, ticker, cotacao, volatilidade):
        """Strangle (Compra Call OTM + Put OTM)"""
        if volatilidade < 25:
            return None
        
        preco = cotacao['regularMarketPrice']
        strike_call = preco * 1.03  # 3% acima
        strike_put = preco * 0.97  # 3% abaixo
        codigo_call = self.gerar_codigo_opcao(ticker, 'CALL', strike_call)
        codigo_put = self.gerar_codigo_opcao(ticker, 'PUT', strike_put)
        
        return {
            'tipo': 'STRANGLE',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_call': strike_call,
            'strike_put': strike_put,
            'codigo_call': codigo_call,
            'codigo_put': codigo_put,
            'volatilidade': volatilidade,
            'motivo': f'Alta volatilidade ({volatilidade:.1f}%), custo menor que straddle',
            'setup': 'Strangle (Long Strangle)',
            'objetivo': 'Lucrar com movimento forte, custo reduzido',
            'risco': 'Moderado (custo de 2 opções OTM, pode perder 100%)',
            'retorno': 'Ilimitado (em qualquer direção)',
            'holding': '5-15 dias',
            'gestao_risco': '3% do capital',
            'passo_a_passo': self._passo_strangle(ticker, strike_call, strike_put, codigo_call, codigo_put)
        }
    
    # ========== PASSO A PASSO ==========
    
    def _passo_compra_call(self, ticker, strike, codigo):
        return f"""
📋 **PASSO A PASSO - COMPRA DE CALL**

**1️⃣ Código da Opção**
• **{codigo}** (aproximado, verificar na plataforma)
• Strike: R$ {strike:.2f}
• Tipo: CALL
• Vencimento: Próxima terceira segunda-feira

**2️⃣ Posição Mínima Sugerida**
• Prêmio esperado: 3-7% do preço do ativo
• Exemplo: Se {ticker} = R$ {strike/1.02:.2f}, prêmio ~R$ {(strike/1.02)*0.05:.2f}
• Posição mínima: 100 opções = ~R$ {(strike/1.02)*0.05*100:.2f}
• Ideal: 200-500 opções para diluir custos

**3️⃣ Preço Limite**
• Não pague mais que 5% acima do ASK
• Se ASK = R$ 1,50, limite = R$ 1,58

**4️⃣ Gestão da Operação**
• **Stop Loss:** ZERO (ou perde tudo ou ganha gigante)
• **Alvo:** 100-300% de lucro OU ativo perder tendência
• **Estratégia:** Entrar com MUITA certeza do movimento
• **Filosofia:** Perder pequeno, ganhar GIGANTESCO
"""
    
    def _passo_compra_put(self, ticker, strike, codigo):
        return f"""
📋 **PASSO A PASSO - COMPRA DE PUT**

**1️⃣ Código da Opção**
• **{codigo}** (aproximado, verificar na plataforma)
• Strike: R$ {strike:.2f}
• Tipo: PUT
• Vencimento: Próxima terceira segunda-feira

**2️⃣ Posição Mínima Sugerida**
• Prêmio esperado: 3-7% do preço do ativo
• Posição mínima: 100 opções
• Ideal: 200-500 opções

**3️⃣ Preço Limite**
• Não pague mais que 5% acima do ASK

**4️⃣ Gestão da Operação**
• **Stop Loss:** ZERO (ou perde tudo ou ganha gigante)
• **Alvo:** 100-250% de lucro OU ativo encontrar suporte
• **Estratégia:** Entrar com MUITA certeza do movimento
• **Filosofia:** Perder pequeno, ganhar GIGANTESCO
"""
    
    def _passo_trava_alta(self, ticker, strike_compra, strike_venda, codigo_compra, codigo_venda):
        return f"""
📋 **PASSO A PASSO - TRAVA DE ALTA**

**1️⃣ Códigos das Opções**
• **COMPRA:** {codigo_compra} (strike R$ {strike_compra:.2f})
• **VENDA:** {codigo_venda} (strike R$ {strike_venda:.2f})

**2️⃣ Posição Mínima Sugerida**
• Mesma quantidade nas 2 pernas
• Mínimo: 100 opções cada
• Ideal: 200-500 opções

**3️⃣ Preço Limite**
• Custo da trava = Prêmio pago - Prêmio recebido
• Exemplo: R$ 1,80 - R$ 0,60 = R$ 1,20

**4️⃣ Gestão**
• **Stop:** Não precisa (risco já limitado)
• **Alvo:** Deixar até vencimento
• **Ganho máximo:** Se ativo >= strike de venda
"""
    
    def _passo_trava_baixa(self, ticker, strike_compra, strike_venda, codigo_compra, codigo_venda):
        return f"""
📋 **PASSO A PASSO - TRAVA DE BAIXA**

**1️⃣ Códigos das Opções**
• **COMPRA:** {codigo_compra} (strike R$ {strike_compra:.2f})
• **VENDA:** {codigo_venda} (strike R$ {strike_venda:.2f})

**2️⃣ Posição Mínima Sugerida**
• Mesma quantidade nas 2 pernas
• Mínimo: 100 opções cada

**3️⃣ Preço Limite**
• Custo da trava = Prêmio pago - Prêmio recebido

**4️⃣ Gestão**
• **Stop:** Não precisa (risco já limitado)
• **Alvo:** Deixar até vencimento
• **Ganho máximo:** Se ativo <= strike de venda
"""
    
    def _passo_borboleta(self, ticker, strike_baixo, strike_medio, strike_alto, codigo_baixo, codigo_medio, codigo_alto):
        return f"""
📋 **PASSO A PASSO - BORBOLETA**

**1️⃣ Códigos das Opções**
• **COMPRA:** {codigo_baixo} (strike R$ {strike_baixo:.2f}) - 100 opções
• **VENDA:** {codigo_medio} (strike R$ {strike_medio:.2f}) - 200 opções (DOBRO!)
• **COMPRA:** {codigo_alto} (strike R$ {strike_alto:.2f}) - 100 opções

**2️⃣ Posição Mínima**
• Padrão: 1-2-1 (100-200-100)

**3️⃣ Preço Limite**
• Custo = (Prêmio baixo + Prêmio alto) - (2 x Prêmio médio)

**4️⃣ Gestão**
• **Stop:** Não precisa
• **Alvo:** Ativo próximo ao strike médio no vencimento
"""
    
    def _passo_straddle(self, ticker, strike, codigo_call, codigo_put):
        return f"""
📋 **PASSO A PASSO - STRADDLE**

**1️⃣ Códigos das Opções**
• **CALL:** {codigo_call} (strike R$ {strike:.2f})
• **PUT:** {codigo_put} (strike R$ {strike:.2f})

**2️⃣ Posição Mínima**
• Mesma quantidade nas 2 opções
• Mínimo: 100 cada

**3️⃣ Preço Limite**
• Custo total = Prêmio call + Prêmio put

**4️⃣ Gestão**
• **Stop Loss:** ZERO (ou perde tudo ou ganha gigante)
• **Alvo:** Movimento forte em qualquer direção
• **Ideal:** Antes de eventos (balanços, decisões)
"""
    
    def _passo_strangle(self, ticker, strike_call, strike_put, codigo_call, codigo_put):
        return f"""
📋 **PASSO A PASSO - STRANGLE**

**1️⃣ Códigos das Opções**
• **CALL:** {codigo_call} (strike R$ {strike_call:.2f})
• **PUT:** {codigo_put} (strike R$ {strike_put:.2f})

**2️⃣ Posição Mínima**
• Mesma quantidade nas 2 opções
• Mínimo: 100 cada

**3️⃣ Preço Limite**
• Custo total = Prêmio call + Prêmio put
• Mais barato que straddle!

**4️⃣ Gestão**
• **Stop Loss:** ZERO (ou perde tudo ou ganha gigante)
• **Alvo:** Movimento forte (precisa ser maior que straddle)
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
• Stop Loss: ZERO (perder tudo ou ganhar gigante)
• Entrar com MUITA certeza do movimento
• Filosofia: Perder pequeno, ganhar GIGANTESCO
• Opções são instrumentos de ALTO RISCO
• Em caso de dúvida, NÃO opere

_Próxima análise: Conforme agenda_
"""
        self.enviar_telegram(footer)
        
        print(f"\n✅ Análise concluída! {len(todas_recomendacoes)} recomendações enviadas.")

if __name__ == "__main__":
    analisador = AnalisadorOpcoesCompleto()
    analisador.executar_analise()

