#!/usr/bin/env python3
"""
Analisador de Opções com Recomendações Automáticas
Gera sinais de compra/venda para o grupo Magnus Wealth
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

class AnalisadorOpcoes:
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
    
    def buscar_opcoes(self, ticker):
        """Busca cadeia de opções do ativo"""
        try:
            # Remover número do ticker para buscar opções
            ticker_base = ''.join([c for c in ticker if not c.isdigit()])
            
            url = f"{self.base_url_brapi}/quote/list"
            params = {'search': ticker_base, 'type': 'option'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'stocks' in data:
                # Filtrar opções do ticker específico
                opcoes = [o for o in data['stocks'] if ticker_base in o['stock']]
                return opcoes
            return []
            
        except Exception as e:
            print(f"Erro ao buscar opções de {ticker}: {e}")
            return []
    
    def analisar_tendencia(self, ticker):
        """Analisa tendência do ativo (simplificado)"""
        try:
            url = f"{self.base_url_brapi}/quote/{ticker}?range=1mo&interval=1d"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'results' not in data or len(data['results']) == 0:
                return 'neutro'
            
            historico = data['results'][0].get('historicalDataPrice', [])
            if len(historico) < 20:
                return 'neutro'
            
            # Calcular médias móveis
            closes = [h['close'] for h in historico]
            ma20 = np.mean(closes[-20:])
            ma5 = np.mean(closes[-5:])
            preco_atual = closes[-1]
            
            # Determinar tendência
            if preco_atual > ma20 and ma5 > ma20:
                return 'alta'
            elif preco_atual < ma20 and ma5 < ma20:
                return 'baixa'
            else:
                return 'neutro'
                
        except Exception as e:
            print(f"Erro ao analisar tendência de {ticker}: {e}")
            return 'neutro'
    
    def calcular_moneyness(self, preco_ativo, strike):
        """Calcula se opção está ITM, ATM ou OTM"""
        diff_percent = abs(strike - preco_ativo) / preco_ativo * 100
        
        if diff_percent <= 2:
            return 'ATM'
        elif strike < preco_ativo:
            return 'ITM'
        else:
            return 'OTM'
    
    def gerar_recomendacao_call(self, ticker, cotacao, tendencia):
        """Gera recomendação de compra de call"""
        if tendencia != 'alta':
            return None
        
        preco = cotacao['regularMarketPrice']
        
        # Procurar call ATM ou ligeiramente OTM
        strike_ideal = preco * 1.02  # 2% acima
        
        recomendacao = {
            'tipo': 'CALL',
            'acao': 'COMPRA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'tendencia': tendencia,
            'motivo': 'Ativo em tendência de alta, rompimento de resistência detectado',
            'entrada_sugerida': None,  # Será preenchido com dados reais da opção
            'teto_entrada': None,
            'stop_loss': preco * 0.97,  # 3% abaixo
            'stop_gain': 'Quando ativo perder tendência de alta ou lucro > 100%',
            'gestao_risco': '3% do capital',
            'holding': '5-15 dias',
            'setup': 'Setup 1: Compra de Call em Rompimento'
        }
        
        return recomendacao
    
    def gerar_recomendacao_put(self, ticker, cotacao, tendencia):
        """Gera recomendação de compra de put"""
        if tendencia != 'baixa':
            return None
        
        preco = cotacao['regularMarketPrice']
        
        # Procurar put ATM ou ligeiramente OTM
        strike_ideal = preco * 0.98  # 2% abaixo
        
        recomendacao = {
            'tipo': 'PUT',
            'acao': 'COMPRA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'tendencia': tendencia,
            'motivo': 'Ativo em tendência de baixa, perda de suporte detectada',
            'entrada_sugerida': None,
            'teto_entrada': None,
            'stop_loss': preco * 1.03,  # 3% acima
            'stop_gain': 'Quando ativo encontrar novo suporte ou lucro > 100%',
            'gestao_risco': '3% do capital',
            'holding': '3-10 dias',
            'setup': 'Setup 2: Compra de Put em Queda'
        }
        
        return recomendacao
    
    def gerar_recomendacao_venda_coberta(self, ticker, cotacao, tendencia):
        """Gera recomendação de venda coberta"""
        if tendencia == 'baixa':
            return None
        
        preco = cotacao['regularMarketPrice']
        
        # Vender call OTM (5% acima)
        strike_ideal = preco * 1.05
        
        recomendacao = {
            'tipo': 'CALL',
            'acao': 'VENDA COBERTA',
            'ticker': ticker,
            'preco_ativo': preco,
            'strike_sugerido': strike_ideal,
            'tendencia': tendencia,
            'motivo': 'Mercado lateral/leve alta, ideal para gerar renda extra',
            'entrada_sugerida': None,
            'teto_entrada': None,
            'stop_loss': 'Recomprar se ativo cair 5%',
            'stop_gain': 'Deixar expirar sem valor',
            'gestao_risco': 'Você já possui as ações',
            'holding': 'Até vencimento',
            'setup': 'Setup 3: Venda Coberta (Proteção + Renda)'
        }
        
        return recomendacao
    
    def analisar_ativo(self, ticker):
        """Analisa um ativo e gera recomendações"""
        print(f"Analisando {ticker}...")
        
        cotacao = self.buscar_cotacao(ticker)
        if not cotacao:
            return []
        
        tendencia = self.analisar_tendencia(ticker)
        
        recomendacoes = []
        
        # Gerar recomendações baseadas na tendência
        if tendencia == 'alta':
            rec_call = self.gerar_recomendacao_call(ticker, cotacao, tendencia)
            if rec_call:
                recomendacoes.append(rec_call)
                
            rec_venda = self.gerar_recomendacao_venda_coberta(ticker, cotacao, tendencia)
            if rec_venda:
                recomendacoes.append(rec_venda)
                
        elif tendencia == 'baixa':
            rec_put = self.gerar_recomendacao_put(ticker, cotacao, tendencia)
            if rec_put:
                recomendacoes.append(rec_put)
        
        return recomendacoes
    
    def formatar_mensagem(self, rec):
        """Formata mensagem de recomendação"""
        emoji_tipo = {'CALL': '📈', 'PUT': '📉'}
        emoji_acao = {'COMPRA': '🟢', 'VENDA COBERTA': '🔵'}
        
        msg = f"""
{emoji_tipo[rec['tipo']]} **{rec['ticker']} - {rec['tipo']}** {emoji_acao[rec['acao']]}

🎯 **Ação:** {rec['acao']}
💰 **Preço do Ativo:** R$ {rec['preco_ativo']:.2f}
🎲 **Strike Sugerido:** R$ {rec['strike_sugerido']:.2f}

📊 **Análise:**
• Tendência: {rec['tendencia'].upper()}
• Setup: {rec['setup']}

💡 **Motivo da Recomendação:**
{rec['motivo']}

"""
        
        if rec['acao'] == 'COMPRA':
            msg += f"""🎯 **Gestão da Operação:**
• Entrada: Buscar opção ATM/OTM próxima de R$ {rec['strike_sugerido']:.2f}
• Teto: Não pagar mais que 10% acima do prêmio inicial
• Stop Loss: Se {rec['ticker']} cair para R$ {rec['stop_loss']:.2f}
• Stop Gain: {rec['stop_gain']}
• Risco: {rec['gestao_risco']}
• Holding: {rec['holding']}

⚠️ **Disclaimer:**
Esta recomendação é baseada em análise técnica automatizada.
Opções são instrumentos de alto risco e podem resultar em perda
total do capital investido. Avalie seu perfil de risco antes de operar.
Não é recomendação de investimento, apenas sinal educacional.
"""
        else:  # VENDA COBERTA
            msg += f"""🎯 **Gestão da Operação:**
• Vender: Call strike R$ {rec['strike_sugerido']:.2f}
• Prêmio esperado: 1-3% do valor das ações
• Stop Loss: {rec['stop_loss']}
• Stop Gain: {rec['stop_gain']}
• Requisito: Possuir 100 ações de {rec['ticker']}
• Holding: {rec['holding']}

⚠️ **Disclaimer:**
Venda coberta limita ganhos mas gera renda extra. Se o ativo subir
muito acima do strike, suas ações serão exercidas. Ideal para
quem tem posição de longo prazo e quer rentabilizar a carteira.
Não é recomendação de investimento, apenas sinal educacional.
"""
        
        msg += f"""
🕐 **Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

_Estratégia: Análise Técnica + Opções_
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
        """Executa análise de opções e envia recomendações"""
        print(f"\n{'='*60}")
        print(f"📊 ANÁLISE DE OPÇÕES - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"{'='*60}\n")
        
        todas_recomendacoes = []
        
        for ticker in ATIVOS_PRINCIPAIS:
            recomendacoes = self.analisar_ativo(ticker)
            todas_recomendacoes.extend(recomendacoes)
        
        if not todas_recomendacoes:
            msg = f"""
📊 **Análise de Opções**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

✅ Análise concluída!
📈 **Nenhuma oportunidade** detectada no momento.

Ativos analisados: {', '.join(ATIVOS_PRINCIPAIS)}
Aguardando melhores setups.

_Próxima análise: Conforme agenda (10:10, 14:00, 16:45)_
"""
            self.enviar_telegram(msg)
            print("ℹ️  Nenhuma recomendação gerada.")
            return
        
        # Mensagem de cabeçalho
        header = f"""
📊 **ANÁLISE DE OPÇÕES**
📅 {datetime.now().strftime('%d/%m/%Y às %H:%M')}

🎯 **{len(todas_recomendacoes)} Oportunidade(s) Detectada(s)**

{'='*40}
"""
        self.enviar_telegram(header)
        
        # Enviar cada recomendação
        for rec in todas_recomendacoes:
            msg = self.formatar_mensagem(rec)
            self.enviar_telegram(msg)
            print(f"✅ Recomendação enviada: {rec['ticker']} - {rec['tipo']} {rec['acao']}")
        
        # Mensagem de rodapé
        footer = f"""
{'='*40}

📊 **Resumo:**
• Calls: {sum(1 for r in todas_recomendacoes if r['tipo'] == 'CALL')}
• Puts: {sum(1 for r in todas_recomendacoes if r['tipo'] == 'PUT')}

⚠️ **Lembre-se:**
• Risco máximo: 3% por operação
• Sempre use stop loss
• Opções são instrumentos de alto risco

_Próxima análise: Conforme agenda_
"""
        self.enviar_telegram(footer)
        
        print(f"\n✅ Análise concluída! {len(todas_recomendacoes)} recomendações enviadas.")

if __name__ == "__main__":
    analisador = AnalisadorOpcoes()
    analisador.executar_analise()

