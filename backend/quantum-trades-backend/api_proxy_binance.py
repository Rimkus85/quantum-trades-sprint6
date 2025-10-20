#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Proxy Binance - Backend
Magnus Wealth

Endpoints para a página web do proxy Binance
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from binance.client import Client
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Cliente Binance global
binance_client = None
api_key_global = None
api_secret_global = None

# Configurações
ALAVANCAGEM = 12

@app.route('/')
def index():
    """Serve a página do proxy"""
    return send_from_directory('/home/ubuntu/quantum-trades-sprint6/frontend', 'proxy-binance.html')

@app.route('/api/proxy/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'online',
        'binance_connected': binance_client is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/proxy/connect', methods=['POST'])
def connect():
    """Conecta à Binance com as credenciais fornecidas"""
    global binance_client, api_key_global, api_secret_global
    
    try:
        data = request.json
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        
        if not api_key or not api_secret:
            return jsonify({'error': 'API Key e Secret são obrigatórios'}), 400
        
        # Tentar conectar
        client = Client(api_key, api_secret)
        client.ping()
        
        # Salvar cliente
        binance_client = client
        api_key_global = api_key
        api_secret_global = api_secret
        
        return jsonify({
            'status': 'success',
            'message': 'Conectado à Binance com sucesso'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/execute', methods=['POST'])
def execute_order():
    """
    Executa ordem na Binance
    
    Body:
    {
        "action": "open_long" | "open_short" | "close_position",
        "symbol": "BTCUSDT",
        "quantity": 0.001,
        "leverage": 12
    }
    """
    global binance_client
    
    if not binance_client:
        return jsonify({'error': 'Binance não conectada'}), 400
    
    try:
        data = request.json
        action = data.get('action')
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        leverage = data.get('leverage', ALAVANCAGEM)
        
        print(f"📥 Comando recebido: {action} {symbol} {quantity}")
        
        # Configurar alavancagem
        binance_client.futures_change_leverage(
            symbol=symbol,
            leverage=leverage
        )
        
        # Configurar margem isolada
        try:
            binance_client.futures_change_margin_type(
                symbol=symbol,
                marginType='ISOLATED'
            )
        except:
            pass  # Já está isolado
        
        # Executar ordem
        if action == 'open_long':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            print(f"✅ LONG aberto: {order['orderId']}")
            
        elif action == 'open_short':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            print(f"✅ SHORT aberto: {order['orderId']}")
            
        elif action == 'close_position':
            # Obter posição atual
            positions = binance_client.futures_position_information(symbol=symbol)
            pos = next((p for p in positions if float(p['positionAmt']) != 0), None)
            
            if pos:
                amt = float(pos['positionAmt'])
                side = 'SELL' if amt > 0 else 'BUY'
                
                order = binance_client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=abs(amt)
                )
                print(f"✅ Posição fechada: {order['orderId']}")
            else:
                print(f"⚠️ Nenhuma posição aberta em {symbol}")
                return jsonify({'status': 'no_position'})
        
        return jsonify({
            'status': 'success',
            'order_id': order.get('orderId'),
            'symbol': symbol,
            'action': action
        })
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/positions', methods=['GET'])
def get_positions():
    """Retorna posições abertas"""
    global binance_client
    
    if not binance_client:
        return jsonify({'error': 'Binance não conectada'}), 400
    
    try:
        positions = binance_client.futures_position_information()
        open_positions = [
            {
                'symbol': p['symbol'],
                'amount': p['positionAmt'],
                'entry_price': p['entryPrice'],
                'unrealized_pnl': p['unRealizedProfit']
            }
            for p in positions if float(p['positionAmt']) != 0
        ]
        
        return jsonify({'positions': open_positions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - API PROXY BINANCE')
    print('  Versão 1.0.0')
    print('═══════════════════════════════════════════════════\n')
    print('✓ Servidor iniciado em http://0.0.0.0:5000')
    print('✓ Acesse pelo celular: http://[SEU_IP]:5000\n')
    
    app.run(host='0.0.0.0', port=5000, debug=False)

