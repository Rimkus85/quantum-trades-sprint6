#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Magnus Wealth - Proxy Binance para Termux
Versão 1.0.0

Roda no celular via Termux e executa ordens na Binance
usando seu IP residencial (sem bloqueio)
"""

from flask import Flask, request, jsonify
from binance.client import Client
import json
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('magnus_proxy.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Cliente Binance global
binance_client = None
api_key_global = None
api_secret_global = None

# Configurações
ALAVANCAGEM = 12
CONFIG_FILE = 'config.json'

def carregar_config():
    """Carrega configuração salva"""
    global binance_client, api_key_global, api_secret_global
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key')
                api_secret = config.get('api_secret')
                
                if api_key and api_secret:
                    client = Client(api_key, api_secret)
                    client.ping()
                    
                    binance_client = client
                    api_key_global = api_key
                    api_secret_global = api_secret
                    
                    logger.info("✓ Configuração carregada e Binance conectada")
                    return True
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
    
    return False

def salvar_config(api_key, api_secret):
    """Salva configuração"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'api_key': api_key,
                'api_secret': api_secret
            }, f)
        logger.info("✓ Configuração salva")
    except Exception as e:
        logger.error(f"Erro ao salvar config: {e}")

@app.route('/')
def index():
    """Página inicial"""
    status = "🟢 ONLINE" if binance_client else "🔴 OFFLINE"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Magnus Wealth - Proxy</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                max-width: 500px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 20px;
            }}
            h1 {{ margin-bottom: 10px; }}
            .status {{ font-size: 24px; margin: 20px 0; }}
            .info {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Magnus Wealth</h1>
            <p>Proxy Binance - Termux</p>
            <div class="status">{status}</div>
            <div class="info">
                <strong>Binance:</strong> {'Conectada ✓' if binance_client else 'Aguardando configuração'}
            </div>
            <div class="info">
                <strong>Servidor:</strong> Ativo
            </div>
            <div class="info">
                <strong>Porta:</strong> 5000
            </div>
            <p style="margin-top: 30px; font-size: 12px;">
                Acesse /health para status<br>
                Acesse /config para configurar
            </p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'online',
        'binance_connected': binance_client is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configurar API Keys"""
    global binance_client, api_key_global, api_secret_global
    
    if request.method == 'POST':
        try:
            data = request.json
            api_key = data.get('api_key')
            api_secret = data.get('api_secret')
            
            if not api_key or not api_secret:
                return jsonify({'error': 'API Key e Secret são obrigatórios'}), 400
            
            # Tentar conectar
            client = Client(api_key, api_secret)
            client.ping()
            
            # Salvar
            binance_client = client
            api_key_global = api_key
            api_secret_global = api_secret
            salvar_config(api_key, api_secret)
            
            logger.info("✓ Binance conectada com sucesso")
            
            return jsonify({
                'status': 'success',
                'message': 'Conectado à Binance com sucesso'
            })
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            return jsonify({'error': str(e)}), 500
    
    # GET - retorna formulário
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Configurar - Magnus Wealth</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
            }
            .container {
                max-width: 500px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 20px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 14px;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                display: none;
            }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🔑 Configurar API Binance</h2>
            <input type="text" id="apiKey" placeholder="API Key">
            <input type="password" id="apiSecret" placeholder="API Secret">
            <button onclick="conectar()">Conectar</button>
            <div id="result" class="result"></div>
        </div>
        <script>
            async function conectar() {
                const apiKey = document.getElementById('apiKey').value;
                const apiSecret = document.getElementById('apiSecret').value;
                const result = document.getElementById('result');
                
                try {
                    const response = await fetch('/config', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({api_key: apiKey, api_secret: apiSecret})
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        result.className = 'result success';
                        result.textContent = '✓ ' + data.message;
                    } else {
                        result.className = 'result error';
                        result.textContent = '✗ ' + data.error;
                    }
                    
                    result.style.display = 'block';
                } catch (error) {
                    result.className = 'result error';
                    result.textContent = '✗ Erro: ' + error.message;
                    result.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/execute', methods=['POST'])
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
        
        logger.info(f"📥 Comando recebido: {action} {symbol} {quantity}")
        
        # Configurar alavancagem
        binance_client.futures_change_leverage(
            symbol=symbol,
            leverage=leverage
        )
        logger.info(f"✓ Alavancagem {leverage}x configurada")
        
        # Configurar margem isolada
        try:
            binance_client.futures_change_margin_type(
                symbol=symbol,
                marginType='ISOLATED'
            )
            logger.info(f"✓ Margem isolada configurada")
        except:
            logger.info(f"✓ Margem já está isolada")
        
        # Executar ordem
        if action == 'open_long':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"✅ LONG aberto: {order['orderId']}")
            
        elif action == 'open_short':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"✅ SHORT aberto: {order['orderId']}")
            
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
                logger.info(f"✅ Posição fechada: {order['orderId']}")
            else:
                logger.info(f"⚠️ Nenhuma posição aberta em {symbol}")
                return jsonify({'status': 'no_position'})
        
        return jsonify({
            'status': 'success',
            'order_id': order.get('orderId'),
            'symbol': symbol,
            'action': action
        })
        
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/positions')
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
    print('  MAGNUS WEALTH - PROXY BINANCE TERMUX')
    print('  Versão 1.0.0')
    print('═══════════════════════════════════════════════════\n')
    
    # Tentar carregar configuração salva
    if carregar_config():
        print('✓ Binance conectada automaticamente\n')
    else:
        print('⚠️ Configure suas API Keys em /config\n')
    
    print('✓ Servidor iniciado em http://0.0.0.0:5000')
    print('✓ Acesse pelo navegador para configurar\n')
    print('📱 Mantenha o Termux aberto em segundo plano')
    print('🔋 Recomendado: deixar celular carregando\n')
    
    # Rodar servidor
    app.run(host='0.0.0.0', port=5000, debug=False)

