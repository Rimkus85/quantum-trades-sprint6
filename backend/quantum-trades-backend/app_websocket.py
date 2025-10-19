#!/usr/bin/env python3
"""
Magnus Wealth - WebSocket Server
Servidor WebSocket para cotações em tempo real
"""

import os
import asyncio
import requests
from datetime import datetime
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================================================
# ESTADO GLOBAL
# ============================================================================

# Lista de clientes conectados e seus tickers inscritos
connected_clients = {}
subscribed_tickers = set()

# Cache de preços
price_cache = {}

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def fetch_price(ticker):
    """Busca preço atual de um ticker"""
    try:
        url = f"https://brapi.dev/api/quote/{ticker}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('results') and len(data['results']) > 0:
            result = data['results'][0]
            return {
                'ticker': ticker,
                'price': result.get('regularMarketPrice', 0),
                'change': result.get('regularMarketChange', 0),
                'changePercent': result.get('regularMarketChangePercent', 0),
                'volume': result.get('regularMarketVolume', 0),
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Erro ao buscar preço de {ticker}: {e}")
    
    return None

def fetch_multiple_prices(tickers):
    """Busca preços de múltiplos tickers"""
    if not tickers:
        return {}
    
    try:
        # A brapi.dev suporta múltiplos tickers separados por vírgula
        tickers_str = ','.join(tickers)
        url = f"https://brapi.dev/api/quote/{tickers_str}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        prices = {}
        if data.get('results'):
            for result in data['results']:
                ticker = result.get('symbol')
                prices[ticker] = {
                    'ticker': ticker,
                    'price': result.get('regularMarketPrice', 0),
                    'change': result.get('regularMarketChange', 0),
                    'changePercent': result.get('regularMarketChangePercent', 0),
                    'volume': result.get('regularMarketVolume', 0),
                    'timestamp': datetime.now().isoformat()
                }
        
        return prices
    except Exception as e:
        print(f"Erro ao buscar preços: {e}")
        return {}

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    print(f"Cliente conectado: {request.sid}")
    connected_clients[request.sid] = set()
    emit('connected', {'status': 'ok', 'message': 'Conectado ao Magnus Wealth'})

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    print(f"Cliente desconectado: {request.sid}")
    
    # Remover tickers inscritos deste cliente
    if request.sid in connected_clients:
        client_tickers = connected_clients[request.sid]
        
        # Verificar se algum ticker não tem mais clientes inscritos
        for ticker in client_tickers:
            # Contar quantos clientes ainda estão inscritos neste ticker
            still_subscribed = any(
                ticker in tickers 
                for sid, tickers in connected_clients.items() 
                if sid != request.sid
            )
            
            if not still_subscribed:
                subscribed_tickers.discard(ticker)
        
        del connected_clients[request.sid]

@socketio.on('subscribe')
def handle_subscribe(data):
    """Cliente se inscreve para receber atualizações de um ticker"""
    ticker = data.get('ticker', '').upper()
    
    if not ticker:
        emit('error', {'message': 'Ticker não fornecido'})
        return
    
    print(f"Cliente {request.sid} inscrito em {ticker}")
    
    # Adicionar ticker à lista do cliente
    if request.sid not in connected_clients:
        connected_clients[request.sid] = set()
    
    connected_clients[request.sid].add(ticker)
    subscribed_tickers.add(ticker)
    
    # Enviar preço atual imediatamente
    price = fetch_price(ticker)
    if price:
        emit('price_update', price)
    else:
        emit('error', {'message': f'Não foi possível obter preço de {ticker}'})

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Cliente cancela inscrição de um ticker"""
    ticker = data.get('ticker', '').upper()
    
    if request.sid in connected_clients:
        connected_clients[request.sid].discard(ticker)
        
        # Verificar se nenhum cliente está mais inscrito neste ticker
        still_subscribed = any(
            ticker in tickers 
            for tickers in connected_clients.values()
        )
        
        if not still_subscribed:
            subscribed_tickers.discard(ticker)
        
        print(f"Cliente {request.sid} desinscrito de {ticker}")

@socketio.on('subscribe_multiple')
def handle_subscribe_multiple(data):
    """Cliente se inscreve em múltiplos tickers"""
    tickers = data.get('tickers', [])
    
    if not tickers:
        emit('error', {'message': 'Nenhum ticker fornecido'})
        return
    
    # Normalizar tickers
    tickers = [t.upper() for t in tickers]
    
    print(f"Cliente {request.sid} inscrito em {len(tickers)} tickers")
    
    # Adicionar tickers à lista do cliente
    if request.sid not in connected_clients:
        connected_clients[request.sid] = set()
    
    for ticker in tickers:
        connected_clients[request.sid].add(ticker)
        subscribed_tickers.add(ticker)
    
    # Enviar preços atuais
    prices = fetch_multiple_prices(tickers)
    for ticker, price in prices.items():
        emit('price_update', price)

# ============================================================================
# BACKGROUND TASK - ATUALIZAÇÃO DE PREÇOS
# ============================================================================

def background_price_updates():
    """Task em background para enviar atualizações de preços"""
    print("Iniciando background task de atualização de preços...")
    
    while True:
        try:
            if subscribed_tickers:
                # Buscar preços de todos os tickers inscritos
                prices = fetch_multiple_prices(list(subscribed_tickers))
                
                # Enviar atualizações para cada cliente
                for sid, client_tickers in connected_clients.items():
                    for ticker in client_tickers:
                        if ticker in prices:
                            socketio.emit(
                                'price_update', 
                                prices[ticker],
                                room=sid
                            )
                
                # Atualizar cache
                price_cache.update(prices)
                
                print(f"Atualizados {len(prices)} tickers para {len(connected_clients)} clientes")
            
            # Aguardar 15 segundos
            socketio.sleep(15)
            
        except Exception as e:
            print(f"Erro no background task: {e}")
            socketio.sleep(5)

# ============================================================================
# ROTAS HTTP (PARA TESTES)
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return {
        'status': 'ok',
        'service': 'Magnus Wealth WebSocket',
        'connected_clients': len(connected_clients),
        'subscribed_tickers': len(subscribed_tickers),
        'tickers': list(subscribed_tickers)
    }

@app.route('/api/price/<ticker>', methods=['GET'])
def get_price(ticker):
    """Retorna preço atual de um ticker"""
    ticker = ticker.upper()
    
    # Verificar cache
    if ticker in price_cache:
        return {'success': True, 'data': price_cache[ticker]}
    
    # Buscar preço
    price = fetch_price(ticker)
    if price:
        price_cache[ticker] = price
        return {'success': True, 'data': price}
    
    return {'success': False, 'message': 'Ticker não encontrado'}, 404

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("MAGNUS WEALTH - WEBSOCKET SERVER")
    print("=" * 60)
    print("Servidor WebSocket para cotações em tempo real")
    print("Porta: 5001")
    print("=" * 60)
    print("\nEndpoints disponíveis:")
    print("  GET  /api/health")
    print("  GET  /api/price/<ticker>")
    print("\nWebSocket Events:")
    print("  connect - Cliente conectado")
    print("  disconnect - Cliente desconectado")
    print("  subscribe - Inscrever em ticker")
    print("  unsubscribe - Desinscrever de ticker")
    print("  subscribe_multiple - Inscrever em múltiplos tickers")
    print("  price_update - Atualização de preço (emitido pelo servidor)")
    print("\nIniciando servidor...")
    print("=" * 60)
    
    # Iniciar background task
    socketio.start_background_task(background_price_updates)
    
    # Iniciar servidor
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)

