#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trader Binance via Proxy (App no Celular)
Magnus Wealth - Versão 2.0.0

Envia comandos para o app no celular que executa na Binance
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/quantum-trades-sprint6/logs/trader.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configurações
ALAVANCAGEM = 12
CAPITAL_TOTAL = 2000
STOP_LOSS_PERCENT = 5

# URL do app (será configurada)
APP_URL = os.getenv('APP_URL', 'http://192.168.1.100:5000')

# Alocação por tier
ALOCACAO_TIER = {
    1: 0.25,
    2: 0.125,
    3: 0.0625
}

class BinanceProxyTrader:
    """
    Trader que envia comandos para o app no celular
    """
    
    def __init__(self, app_url=None):
        """Inicializa trader proxy"""
        self.app_url = app_url or APP_URL
        logger.info(f"Trader Proxy inicializado: {self.app_url}")
        
        # Arquivo de estado
        self.estado_file = '/home/ubuntu/quantum-trades-sprint6/data/posicoes.json'
        self.carregar_estado()
        
        # Verificar conexão com app
        self.verificar_app()
    
    def carregar_estado(self):
        """Carrega estado das posições"""
        try:
            if os.path.exists(self.estado_file):
                with open(self.estado_file, 'r') as f:
                    self.posicoes = json.load(f)
            else:
                self.posicoes = {}
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            self.posicoes = {}
    
    def salvar_estado(self):
        """Salva estado das posições"""
        try:
            os.makedirs(os.path.dirname(self.estado_file), exist_ok=True)
            with open(self.estado_file, 'w') as f:
                json.dump(self.posicoes, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def verificar_app(self):
        """Verifica se app está online"""
        try:
            response = requests.get(f"{self.app_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ App online: {data}")
                return True
            else:
                logger.error(f"✗ App retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ App offline: {e}")
            return False
    
    def abrir_posicao(self, symbol, lado, capital_alocado, tier):
        """
        Envia comando para abrir posição no app
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"ABRINDO POSIÇÃO {lado} - {symbol}")
            logger.info(f"{'='*60}")
            
            # Obter preço atual
            preco = self.obter_preco_atual(symbol)
            if not preco:
                return False
            
            # Calcular quantidade
            poder_compra = capital_alocado * ALAVANCAGEM
            quantidade = poder_compra / preco
            quantidade = round(quantidade, 3)
            
            logger.info(f"Capital: ${capital_alocado:.2f}")
            logger.info(f"Alavancagem: {ALAVANCAGEM}x")
            logger.info(f"Quantidade: {quantidade}")
            
            # Enviar comando ao app
            action = 'open_long' if lado == 'LONG' else 'open_short'
            
            response = requests.post(
                f"{self.app_url}/execute",
                json={
                    'action': action,
                    'symbol': symbol,
                    'quantity': quantidade,
                    'leverage': ALAVANCAGEM
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Ordem executada: {result['order_id']}")
                
                # Salvar no estado
                self.posicoes[symbol] = {
                    'lado': lado,
                    'preco_entrada': preco,
                    'quantidade': quantidade,
                    'capital_alocado': capital_alocado,
                    'alavancagem': ALAVANCAGEM,
                    'ordem_id': result['order_id'],
                    'tier': tier,
                    'data_abertura': datetime.now().isoformat()
                }
                
                self.salvar_estado()
                
                # Notificar Telegram
                self.notificar_telegram(
                    f"🟢 POSIÇÃO ABERTA\n\n"
                    f"Cripto: {symbol}\n"
                    f"Lado: {lado}\n"
                    f"Preço: ${preco:.2f}\n"
                    f"Quantidade: {quantidade}\n"
                    f"Capital: ${capital_alocado:.2f}\n"
                    f"Alavancagem: {ALAVANCAGEM}x\n"
                    f"Ordem ID: {result['order_id']}"
                )
                
                return True
            else:
                logger.error(f"✗ Erro do app: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Erro ao abrir posição: {e}")
            return False
    
    def fechar_posicao(self, symbol):
        """
        Envia comando para fechar posição no app
        """
        try:
            if symbol not in self.posicoes:
                logger.warning(f"Posição {symbol} não encontrada")
                return False
            
            posicao = self.posicoes[symbol]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"FECHANDO POSIÇÃO - {symbol}")
            logger.info(f"{'='*60}")
            
            # Obter preço atual
            preco_saida = self.obter_preco_atual(symbol)
            if not preco_saida:
                return False
            
            # Calcular P&L
            if posicao['lado'] == 'LONG':
                pnl_percent = ((preco_saida - posicao['preco_entrada']) / posicao['preco_entrada']) * 100 * ALAVANCAGEM
            else:
                pnl_percent = ((posicao['preco_entrada'] - preco_saida) / posicao['preco_entrada']) * 100 * ALAVANCAGEM
            
            pnl_usd = posicao['capital_alocado'] * (pnl_percent / 100)
            
            logger.info(f"P&L: {pnl_percent:+.2f}% (${pnl_usd:+.2f})")
            
            # Enviar comando ao app
            response = requests.post(
                f"{self.app_url}/execute",
                json={
                    'action': 'close_position',
                    'symbol': symbol
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Posição fechada")
                
                # Remover do estado
                del self.posicoes[symbol]
                self.salvar_estado()
                
                # Notificar Telegram
                emoji = '✅' if pnl_percent > 0 else '❌'
                self.notificar_telegram(
                    f"{emoji} POSIÇÃO FECHADA\n\n"
                    f"Cripto: {symbol}\n"
                    f"Lado: {posicao['lado']}\n"
                    f"Entrada: ${posicao['preco_entrada']:.2f}\n"
                    f"Saída: ${preco_saida:.2f}\n"
                    f"P&L: {pnl_percent:+.2f}%\n"
                    f"Lucro/Prejuízo: ${pnl_usd:+.2f}"
                )
                
                return True
            else:
                logger.error(f"✗ Erro do app: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Erro ao fechar posição: {e}")
            return False
    
    def obter_preco_atual(self, symbol):
        """Obtém preço atual via Yahoo Finance"""
        try:
            import yfinance as yf
            # Converter BTCUSDT para BTC-USD
            yahoo_symbol = symbol.replace('USDT', '-USD')
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period='1d')
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            return None
        except Exception as e:
            logger.error(f"Erro ao obter preço: {e}")
            return None
    
    def processar_sinal(self, cripto, sinal, mudanca, tier):
        """Processa sinal e envia comando ao app"""
        symbol = cripto['symbol'].replace('USDT', '') + 'USDT'
        
        alocacao_percent = ALOCACAO_TIER[tier]
        capital_alocado = CAPITAL_TOTAL * alocacao_percent
        
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSANDO SINAL: {cripto['name']}")
        logger.info(f"Sinal: {sinal} | Mudança: {mudanca}")
        logger.info(f"{'='*60}")
        
        if not mudanca:
            logger.info("Sem mudança. Mantendo posição.")
            return
        
        # Fechar posição se houver
        if symbol in self.posicoes:
            self.fechar_posicao(symbol)
        
        # Abrir nova posição
        if sinal == 'COMPRA':
            self.abrir_posicao(symbol, 'LONG', capital_alocado, tier)
        elif sinal == 'VENDA':
            self.abrir_posicao(symbol, 'SHORT', capital_alocado, tier)
    
    def notificar_telegram(self, mensagem):
        """Envia notificação ao Telegram"""
        try:
            api_id = int(os.getenv('TELEGRAM_API_ID'))
            api_hash = os.getenv('TELEGRAM_API_HASH')
            group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
            
            with TelegramClient('magnus_session', api_id, api_hash) as client:
                client.send_message(group_id, mensagem)
            
            logger.info("✓ Notificação enviada")
        except Exception as e:
            logger.error(f"✗ Erro ao notificar: {e}")

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - TRADER PROXY')
    print('  Versão 2.0.0 - Via App no Celular')
    print('═══════════════════════════════════════════════════\n')
    
    trader = BinanceProxyTrader()
    print(f'\n✓ Trader Proxy inicializado!')
    print(f'✓ App URL: {trader.app_url}')

