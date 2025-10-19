#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Criptomoedas + Trader Automático
Magnus Wealth - Versão 8.4.0

Integração completa:
- Análise com Gann HiLo Activator
- Execução automática na Binance
- Alavancagem 12x
- Proteção de fundos
"""

import sys
import os

# Importar analisador e trader
from analisador_cripto_hilo import TOP_8, analisar_cripto, formatar_mensagem, enviar_telegram
from trader_binance import BinanceTrader

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def executar_analise_e_trading():
    """
    Executa análise completa e trading automático
    """
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - ANÁLISE + TRADING AUTOMÁTICO')
    print('  Gann HiLo Activator + Binance Futures 12x')
    print('  Versão 8.4.0')
    print('═══════════════════════════════════════════════════\n')
    
    # Inicializar trader
    try:
        trader = BinanceTrader()
        logger.info("✓ Trader Binance inicializado")
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar trader: {e}")
        logger.error("Continuando apenas com análise...")
        trader = None
    
    # Analisar criptos
    resultados = []
    
    for cripto in TOP_8:
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Analisando {cripto['name']}...")
            logger.info(f"{'='*60}")
            
            resultado = analisar_cripto(cripto)
            resultados.append(resultado)
            
            logger.info(f"✓ {cripto['name']}: {resultado['sinal']} - Tendência {resultado['trend']}")
            
            # Se trader está ativo e houve mudança, executar operação
            if trader and resultado['mudanca']:
                logger.info(f"⚠️ MUDANÇA DE TENDÊNCIA DETECTADA!")
                logger.info(f"Processando sinal de trading...")
                
                trader.processar_sinal(
                    cripto=cripto,
                    sinal=resultado['sinal'],
                    mudanca=resultado['mudanca'],
                    tier=cripto['tier']
                )
            
        except Exception as e:
            logger.error(f"✗ Erro ao analisar {cripto['name']}: {e}")
    
    # Formatar e enviar mensagem de análise
    if resultados:
        logger.info('\n' + '═'*60)
        logger.info('Formatando mensagem de análise...')
        
        mensagem = formatar_mensagem(resultados)
        
        # Adicionar informações de trading se ativo
        if trader:
            mensagem += "\n\n🤖 *TRADING AUTOMÁTICO ATIVO*\n"
            mensagem += f"Alavancagem: {trader.ALAVANCAGEM}x\n"
            mensagem += f"Posições abertas: {len(trader.posicoes)}\n"
        
        logger.info('Enviando mensagem ao Telegram...')
        try:
            enviar_telegram(mensagem)
            logger.info('✓ Mensagem enviada com sucesso!')
        except Exception as e:
            logger.error(f'✗ Erro ao enviar mensagem: {e}')
    
    # Resumo final
    print('\n' + '═'*60)
    print('RESUMO DA EXECUÇÃO')
    print('═'*60)
    print(f'Total de criptos analisadas: {len(resultados)}/{len(TOP_8)}')
    
    if trader:
        print(f'Trading automático: ATIVO')
        print(f'Posições abertas: {len(trader.posicoes)}')
        
        # Listar posições
        if trader.posicoes:
            print('\nPosições ativas:')
            for symbol, pos in trader.posicoes.items():
                print(f"  - {symbol}: {pos['lado']} @ ${pos['preco_entrada']:.2f}")
    else:
        print(f'Trading automático: INATIVO (apenas análise)')
    
    print('═'*60)

if __name__ == '__main__':
    try:
        executar_analise_e_trading()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()

