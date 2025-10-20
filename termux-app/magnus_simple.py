from flask import Flask, request, jsonify
from binance.client import Client
import json, os
from datetime import datetime

app = Flask(__name__)
binance_client = None
CONFIG_FILE = 'config.json'

def carregar_config():
    global binance_client
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                client = Client(config['api_key'], config['api_secret'])
                client.ping()
                binance_client = client
                print('Binance conectada')
                return True
        except: pass
    return False

@app.route('/')
def index():
    status = 'ONLINE' if binance_client else 'OFFLINE'
    return f'<h1>Magnus Wealth</h1><p>Status: {status}</p><a href="/config">Configurar</a>'

@app.route('/health')
def health():
    return jsonify({'status': 'online', 'binance_connected': binance_client is not None})

@app.route('/config', methods=['GET', 'POST'])
def config():
    global binance_client
    if request.method == 'POST':
        try:
            data = request.json
            client = Client(data['api_key'], data['api_secret'])
            client.ping()
            binance_client = client
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return '''
    <h2>Configurar</h2>
    <input id="k" placeholder="API Key" style="width:100%;padding:10px;margin:5px 0">
    <input id="s" type="password" placeholder="Secret" style="width:100%;padding:10px;margin:5px 0">
    <button onclick="conectar()" style="width:100%;padding:15px;background:#667eea;color:white;border:none;font-size:16px">Conectar</button>
    <div id="r"></div>
    <script>
    async function conectar(){
        const r = await fetch('/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({api_key: document.getElementById('k').value, api_secret: document.getElementById('s').value})
        });
        const d = await r.json();
        document.getElementById('r').innerHTML = r.ok ? 'Conectado!' : 'Erro: ' + d.error;
    }
    </script>
    '''

@app.route('/execute', methods=['POST'])
def execute():
    global binance_client
    if not binance_client:
        return jsonify({'error': 'Nao conectado'}), 400
    try:
        data = request.json
        symbol = data['symbol']
        quantity = data['quantity']
        leverage = data.get('leverage', 12)
        
        binance_client.futures_change_leverage(symbol=symbol, leverage=leverage)
        try:
            binance_client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
        except: pass
        
        if data['action'] == 'open_long':
            order = binance_client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity)
        elif data['action'] == 'open_short':
            order = binance_client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=quantity)
        elif data['action'] == 'close_position':
            positions = binance_client.futures_position_information(symbol=symbol)
            pos = next((p for p in positions if float(p['positionAmt']) != 0), None)
            if not pos:
                return jsonify({'status': 'no_position'})
            amt = float(pos['positionAmt'])
            order = binance_client.futures_create_order(symbol=symbol, side='SELL' if amt > 0 else 'BUY', type='MARKET', quantity=abs(amt))
        
        print(f"Ordem executada: {data['action']} {symbol}")
        return jsonify({'status': 'success', 'order_id': order.get('orderId')})
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/positions')
def positions():
    if not binance_client:
        return jsonify({'error': 'Nao conectado'}), 400
    try:
        pos = binance_client.futures_position_information()
        return jsonify({'positions': [{'symbol': p['symbol'], 'amount': p['positionAmt'], 'pnl': p['unRealizedProfit']} for p in pos if float(p['positionAmt']) != 0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('MAGNUS WEALTH - PROXY BINANCE')
    carregar_config()
    print('Servidor: http://0.0.0.0:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)

