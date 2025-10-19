#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trader Automático Binance - Magnus Wealth
Versão 1.0.0

Executa operações automáticas baseadas nos sinais do Gann HiLo Activator
- Alavancagem: 12x
- Mercado: Futuros USDT
- Proteção: Stop Loss automático
- Gestão: Capital por cripto
"""

import os
import json
from datetime import datetime
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv
from telethon.sync import TelegramClient
import logging

load_dotenv()

# Configuração de logging
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
CAPITAL_TOTAL = 2000  # USD
STOP_LOSS_PERCENT = 5  # % de stop loss por operação

# Alocação por tier (mesma do analisador)
ALOCACAO_TIER = {
    1: 0.25,    # 25% cada (BTC, ETH)
    2: 0.125,   # 12.5% cada (BNB, SOL)
    3: 0.0625   # 6.25% cada (LINK, UNI, ALGO, VET)
}

class BinanceTrader:
    """
    Classe para executar operações automáticas na Binance Futures
    """
    
    def __init__(self):
        """Inicializa cliente Binance"""
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Chaves API da Binance não configuradas no .env")
        
        self.client = Client(self.api_key, self.api_secret)
        
        # Verificar conexão
        try:
            self.client.ping()
            logger.info("✓ Conectado à Binance API")
        except Exception as e:
            logger.error(f"✗ Erro ao conectar à Binance: {e}")
            raise
        
        # Arquivo de estado das posições
        self.estado_file = '/home/ubuntu/quantum-trades-sprint6/data/posicoes.json'
        self.carregar_estado()
    
    def carregar_estado(self):
        """Carrega estado das posições do arquivo"""
        try:
            if os.path.exists(self.estado_file):
                with open(self.estado_file, 'r') as f:
                    self.posicoes = json.load(f)
                logger.info(f"Estado carregado: {len(self.posicoes)} posições")
            else:
                self.posicoes = {}
                logger.info("Novo estado criado")
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            self.posicoes = {}
    
    def salvar_estado(self):
        """Salva estado das posições no arquivo"""
        try:
            os.makedirs(os.path.dirname(self.estado_file), exist_ok=True)
            with open(self.estado_file, 'w') as f:
                json.dump(self.posicoes, f, indent=2)
            logger.info("Estado salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def configurar_alavancagem(self, symbol):
        """Configura alavancagem para um símbolo"""
        try:
            self.client.futures_change_leverage(
                symbol=symbol,
                leverage=ALAVANCAGEM
            )
            logger.info(f"✓ Alavancagem {ALAVANCAGEM}x configurada para {symbol}")
            return True
        except Exception as e:
            logger.error(f"✗ Erro ao configurar alavancagem para {symbol}: {e}")
            return False
    
    def obter_preco_atual(self, symbol):
        """Obtém preço atual de um símbolo"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Erro ao obter preço de {symbol}: {e}")
            return None
    
    def calcular_quantidade(self, symbol, capital_alocado, preco):
        """
        Calcula quantidade a operar baseado no capital e alavancagem
        
        Com alavancagem 12x:
        - Capital alocado: $250 (exemplo)
        - Poder de compra: $250 * 12 = $3,000
        - Quantidade: $3,000 / preço
        """
        poder_compra = capital_alocado * ALAVANCAGEM
        quantidade = poder_compra / preco
        
        # Arredondar para precisão do símbolo
        # TODO: Obter precisão da API
        quantidade = round(quantidade, 3)
        
        return quantidade
    
    def abrir_posicao(self, symbol, lado, capital_alocado, tier):
        """
        Abre uma posição (LONG ou SHORT)
        
        Args:
            symbol: Símbolo (ex: BTCUSDT)
            lado: 'LONG' ou 'SHORT'
            capital_alocado: Capital em USD
            tier: Tier da cripto (1, 2 ou 3)
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"ABRINDO POSIÇÃO {lado} - {symbol}")
            logger.info(f"{'='*60}")
            
            # Configurar alavancagem
            if not self.configurar_alavancagem(symbol):
                return False
            
            # Obter preço atual
            preco = self.obter_preco_atual(symbol)
            if not preco:
                return False
            
            # Calcular quantidade
            quantidade = self.calcular_quantidade(symbol, capital_alocado, preco)
            
            logger.info(f"Capital alocado: ${capital_alocado:.2f}")
            logger.info(f"Alavancagem: {ALAVANCAGEM}x")
            logger.info(f"Poder de compra: ${capital_alocado * ALAVANCAGEM:.2f}")
            logger.info(f"Preço: ${preco:.2f}")
            logger.info(f"Quantidade: {quantidade}")
            
            # Determinar side da ordem
            side = SIDE_BUY if lado == 'LONG' else SIDE_SELL
            
            # Executar ordem MARKET
            ordem = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantidade
            )
            
            logger.info(f"✓ Ordem executada: {ordem['orderId']}")
            
            # Calcular stop loss
            if lado == 'LONG':
                stop_loss_preco = preco * (1 - STOP_LOSS_PERCENT / 100 / ALAVANCAGEM)
            else:
                stop_loss_preco = preco * (1 + STOP_LOSS_PERCENT / 100 / ALAVANCAGEM)
            
            # Colocar stop loss
            stop_side = SIDE_SELL if lado == 'LONG' else SIDE_BUY
            
            stop_ordem = self.client.futures_create_order(
                symbol=symbol,
                side=stop_side,
                type=FUTURE_ORDER_TYPE_STOP_MARKET,
                stopPrice=round(stop_loss_preco, 2),
                closePosition=True
            )
            
            logger.info(f"✓ Stop Loss colocado em ${stop_loss_preco:.2f}")
            
            # Salvar posição no estado
            self.posicoes[symbol] = {
                'lado': lado,
                'preco_entrada': preco,
                'quantidade': quantidade,
                'capital_alocado': capital_alocado,
                'alavancagem': ALAVANCAGEM,
                'stop_loss': stop_loss_preco,
                'ordem_id': ordem['orderId'],
                'stop_ordem_id': stop_ordem['orderId'],
                'tier': tier,
                'data_abertura': datetime.now().isoformat()
            }
            
            self.salvar_estado()
            
            # Enviar notificação ao Telegram
            self.notificar_telegram(
                f"🟢 POSIÇÃO ABERTA\n\n"
                f"Cripto: {symbol}\n"
                f"Lado: {lado}\n"
                f"Preço: ${preco:.2f}\n"
                f"Quantidade: {quantidade}\n"
                f"Capital: ${capital_alocado:.2f}\n"
                f"Alavancagem: {ALAVANCAGEM}x\n"
                f"Stop Loss: ${stop_loss_preco:.2f}\n"
                f"Ordem ID: {ordem['orderId']}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro ao abrir posição {lado} em {symbol}: {e}")
            return False
    
    def fechar_posicao(self, symbol):
        """
        Fecha uma posição existente
        """
        try:
            if symbol not in self.posicoes:
                logger.warning(f"Posição {symbol} não encontrada no estado")
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
            
            logger.info(f"Preço entrada: ${posicao['preco_entrada']:.2f}")
            logger.info(f"Preço saída: ${preco_saida:.2f}")
            logger.info(f"P&L: {pnl_percent:+.2f}% (${pnl_usd:+.2f})")
            
            # Cancelar stop loss
            try:
                self.client.futures_cancel_order(
                    symbol=symbol,
                    orderId=posicao['stop_ordem_id']
                )
                logger.info("✓ Stop Loss cancelado")
            except Exception as e:
                logger.warning(f"Aviso ao cancelar stop loss: {e}")
            
            # Fechar posição (ordem reversa)
            side = SIDE_SELL if posicao['lado'] == 'LONG' else SIDE_BUY
            
            ordem = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=posicao['quantidade']
            )
            
            logger.info(f"✓ Posição fechada: {ordem['orderId']}")
            
            # Atualizar posição no estado
            posicao['data_fechamento'] = datetime.now().isoformat()
            posicao['preco_saida'] = preco_saida
            posicao['pnl_percent'] = pnl_percent
            posicao['pnl_usd'] = pnl_usd
            posicao['ordem_fechamento_id'] = ordem['orderId']
            posicao['status'] = 'FECHADA'
            
            # Remover do estado ativo
            del self.posicoes[symbol]
            self.salvar_estado()
            
            # Enviar notificação ao Telegram
            emoji = '✅' if pnl_percent > 0 else '❌'
            self.notificar_telegram(
                f"{emoji} POSIÇÃO FECHADA\n\n"
                f"Cripto: {symbol}\n"
                f"Lado: {posicao['lado']}\n"
                f"Entrada: ${posicao['preco_entrada']:.2f}\n"
                f"Saída: ${preco_saida:.2f}\n"
                f"P&L: {pnl_percent:+.2f}%\n"
                f"Lucro/Prejuízo: ${pnl_usd:+.2f}\n"
                f"Ordem ID: {ordem['orderId']}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro ao fechar posição {symbol}: {e}")
            return False
    
    def processar_sinal(self, cripto, sinal, mudanca, tier):
        """
        Processa um sinal do analisador e executa operação se necessário
        
        Args:
            cripto: Dict com info da cripto
            sinal: 'COMPRA', 'VENDA' ou 'MANTER'
            mudanca: True se houve mudança de tendência
            tier: Tier da cripto (1, 2 ou 3)
        """
        symbol = cripto['symbol'].replace('USDT', '')  # BTC, ETH, etc
        symbol_futures = f"{symbol}USDT"  # BTCUSDT para Futures
        
        # Calcular capital alocado
        alocacao_percent = ALOCACAO_TIER[tier]
        capital_alocado = CAPITAL_TOTAL * alocacao_percent
        
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSANDO SINAL: {cripto['name']}")
        logger.info(f"Sinal: {sinal} | Mudança: {mudanca}")
        logger.info(f"{'='*60}")
        
        # Se não houve mudança, não fazer nada
        if not mudanca:
            logger.info("Sem mudança de tendência. Mantendo posição atual.")
            return
        
        # Se há posição aberta, fechar
        if symbol_futures in self.posicoes:
            logger.info("Fechando posição existente...")
            self.fechar_posicao(symbol_futures)
        
        # Abrir nova posição baseado no sinal
        if sinal == 'COMPRA':
            logger.info("Abrindo posição LONG...")
            self.abrir_posicao(symbol_futures, 'LONG', capital_alocado, tier)
        elif sinal == 'VENDA':
            logger.info("Abrindo posição SHORT...")
            self.abrir_posicao(symbol_futures, 'SHORT', capital_alocado, tier)
        else:
            logger.info("Sinal MANTER - não abrindo posição")
    
    def notificar_telegram(self, mensagem):
        """Envia notificação ao Telegram"""
        try:
            api_id = int(os.getenv('TELEGRAM_API_ID'))
            api_hash = os.getenv('TELEGRAM_API_HASH')
            group_id = int(os.getenv('TELEGRAM_GROUP_ID', '-4844836232'))
            
            with TelegramClient('magnus_session', api_id, api_hash) as client:
                client.send_message(group_id, mensagem)
            
            logger.info("✓ Notificação enviada ao Telegram")
        except Exception as e:
            logger.error(f"✗ Erro ao enviar notificação: {e}")
    
    def obter_saldo(self):
        """Obtém saldo da conta Futures"""
        try:
            account = self.client.futures_account()
            saldo = float(account['totalWalletBalance'])
            logger.info(f"Saldo total: ${saldo:.2f}")
            return saldo
        except Exception as e:
            logger.error(f"Erro ao obter saldo: {e}")
            return None
    
    def listar_posicoes_abertas(self):
        """Lista todas as posições abertas"""
        try:
            positions = self.client.futures_position_information()
            abertas = [p for p in positions if float(p['positionAmt']) != 0]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"POSIÇÕES ABERTAS: {len(abertas)}")
            logger.info(f"{'='*60}")
            
            for pos in abertas:
                logger.info(f"{pos['symbol']}: {pos['positionAmt']} @ ${pos['entryPrice']}")
            
            return abertas
        except Exception as e:
            logger.error(f"Erro ao listar posições: {e}")
            return []

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - TRADER AUTOMÁTICO BINANCE')
    print('  Versão 1.0.0 - Alavancagem 12x')
    print('═══════════════════════════════════════════════════\n')
    
    # Teste de conexão
    try:
        trader = BinanceTrader()
        
        # Obter saldo
        saldo = trader.obter_saldo()
        
        # Listar posições
        trader.listar_posicoes_abertas()
        
        print('\n✓ Trader inicializado com sucesso!')
        print(f'✓ Saldo: ${saldo:.2f}')
        print(f'✓ Alavancagem: {ALAVANCAGEM}x')
        print(f'✓ Capital total: ${CAPITAL_TOTAL:.2f}')
        
    except Exception as e:
        print(f'\n✗ Erro ao inicializar trader: {e}')

