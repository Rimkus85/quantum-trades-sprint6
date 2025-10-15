#!/usr/bin/env python3
"""
API Flask para o Magnus Wealth - Quantum Trades.
Fornece endpoints para integração com Telegram e análise de carteiras.
"""

import os
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from services.telegram_service import TelegramService, TelegramCarteirasReader
from modules.carteira_parser import CarteiraParser, parse_telegram_messages, get_recommendations_summary

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurações
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_GROUP = os.getenv('TELEGRAM_GROUP_USERNAME')

# Instância global do serviço (será inicializada quando necessário)
telegram_service = None


def get_telegram_service():
    """Retorna ou cria instância do serviço do Telegram."""
    global telegram_service
    if telegram_service is None:
        if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
            return None
        telegram_service = TelegramService(TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE)
    return telegram_service


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check."""
    return jsonify({
        'status': 'ok',
        'service': 'Magnus Wealth API',
        'version': '1.0.0',
        'telegram_configured': all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE])
    })


@app.route('/api/telegram/config', methods=['GET'])
def get_telegram_config():
    """Retorna status da configuração do Telegram."""
    return jsonify({
        'configured': all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]),
        'has_api_id': bool(TELEGRAM_API_ID),
        'has_api_hash': bool(TELEGRAM_API_HASH),
        'has_phone': bool(TELEGRAM_PHONE),
        'has_group': bool(TELEGRAM_GROUP)
    })


@app.route('/api/telegram/messages', methods=['GET'])
def get_telegram_messages():
    """
    Lê mensagens do grupo do Telegram.
    
    Query params:
        - group: Username ou ID do grupo (opcional, usa padrão se não fornecido)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado',
            'message': 'Configure as variáveis de ambiente TELEGRAM_API_ID, TELEGRAM_API_HASH e TELEGRAM_PHONE'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado',
            'message': 'Forneça o parâmetro "group" ou configure TELEGRAM_GROUP_USERNAME'
        }), 400
    
    try:
        # Executar leitura assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def read():
            await service.connect()
            messages = await service.read_messages(group, limit)
            await service.disconnect()
            return messages
        
        messages = loop.run_until_complete(read())
        loop.close()
        
        return jsonify({
            'success': True,
            'total': len(messages),
            'group': group,
            'messages': messages
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao ler mensagens',
            'message': str(e)
        }), 500


@app.route('/api/telegram/carteiras', methods=['GET'])
def get_carteiras():
    """
    Lê e filtra mensagens sobre carteiras do Telegram.
    
    Query params:
        - group: Username ou ID do grupo (opcional)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado'
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def read():
            reader = TelegramCarteirasReader(service)
            await service.connect()
            carteiras = await reader.read_carteiras(group, limit)
            await service.disconnect()
            return carteiras
        
        carteiras = loop.run_until_complete(read())
        loop.close()
        
        return jsonify({
            'success': True,
            'total': len(carteiras),
            'group': group,
            'carteiras': carteiras
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao ler carteiras',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/parse', methods=['POST'])
def parse_carteiras():
    """
    Analisa mensagens e extrai informações estruturadas.
    
    Body:
        - messages: Lista de mensagens do Telegram
    """
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({
            'error': 'Mensagens não fornecidas',
            'message': 'Envie um JSON com a chave "messages" contendo a lista de mensagens'
        }), 400
    
    try:
        messages = data['messages']
        report = parse_telegram_messages(messages)
        
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao processar mensagens',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/summary', methods=['POST'])
def get_carteiras_summary():
    """
    Retorna resumo das recomendações.
    
    Body:
        - messages: Lista de mensagens do Telegram
    """
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({
            'error': 'Mensagens não fornecidas'
        }), 400
    
    try:
        messages = data['messages']
        summary = get_recommendations_summary(messages)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar resumo',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/analyze', methods=['GET'])
def analyze_carteiras_from_telegram():
    """
    Endpoint completo: lê do Telegram e retorna análise.
    
    Query params:
        - group: Username ou ID do grupo (opcional)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado'
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process():
            # Ler mensagens
            reader = TelegramCarteirasReader(service)
            await service.connect()
            carteiras = await reader.read_carteiras(group, limit)
            await service.disconnect()
            
            # Analisar
            parser = CarteiraParser()
            parser.parse_messages(carteiras)
            report = parser.generate_report()
            
            return report
        
        report = loop.run_until_complete(process())
        loop.close()
        
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar carteiras',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("MAGNUS WEALTH API - Quantum Trades")
    print("=" * 60)
    print(f"Telegram configurado: {all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE])}")
    print(f"Grupo padrão: {TELEGRAM_GROUP or 'Não configurado'}")
    print("=" * 60)
    print("\nEndpoints disponíveis:")
    print("  GET  /api/health")
    print("  GET  /api/telegram/config")
    print("  GET  /api/telegram/messages")
    print("  GET  /api/telegram/carteiras")
    print("  POST /api/carteiras/parse")
    print("  POST /api/carteiras/summary")
    print("  GET  /api/carteiras/analyze")
    print("\nIniciando servidor...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

