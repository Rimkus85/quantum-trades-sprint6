#!/usr/bin/env python3
"""
Quantum Trades - API Flask para produção
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Permitir requisições do frontend

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), 'b3_data.db')

def get_db():
    """Conectar ao banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rota raiz - servir dashboard
@app.route('/')
def index():
    return app.send_static_file('dashboard_final.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Verificar se API está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'API de dados históricos B3 funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stocks', methods=['GET'])
def list_stocks():
    """Listar todas as ações disponíveis"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.symbol, s.name, COUNT(p.id) as total_records,
                   MIN(p.date) as first_date, MAX(p.date) as last_date
            FROM stocks s
            LEFT JOIN prices p ON s.id = p.stock_id
            GROUP BY s.id
            ORDER BY s.symbol
        ''')
        
        stocks = []
        for row in cursor.fetchall():
            stocks.append({
                'symbol': row['symbol'],
                'name': row['name'],
                'total_records': row['total_records'],
                'first_date': row['first_date'],
                'last_date': row['last_date']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total': len(stocks),
            'stocks': stocks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Obter dados históricos de uma ação específica"""
    try:
        # Parâmetros opcionais
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Buscar ID da ação
        cursor.execute('SELECT id, name FROM stocks WHERE symbol = ?', (symbol.upper(),))
        stock = cursor.fetchone()
        
        if not stock:
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Ação {symbol} não encontrada'
            }), 404
        
        stock_id = stock['id']
        stock_name = stock['name']
        
        # Construir query com filtros
        query = '''
            SELECT date, open, high, low, close, volume, trades
            FROM prices
            WHERE stock_id = ?
        '''
        params = [stock_id]
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY date DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        
        prices = []
        for row in cursor.fetchall():
            prices.append({
                'date': row['date'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'trades': row['trades']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'name': stock_name,
            'total_records': len(prices),
            'prices': prices
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/<symbol>/latest', methods=['GET'])
def get_latest_price(symbol):
    """Obter última cotação de uma ação"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.name, p.date, p.open, p.high, p.low, p.close, p.volume, p.trades
            FROM stocks s
            JOIN prices p ON s.id = p.stock_id
            WHERE s.symbol = ?
            ORDER BY p.date DESC
            LIMIT 1
        ''', (symbol.upper(),))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': f'Ação {symbol} não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'name': row['name'],
            'date': row['date'],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume'],
            'trades': row['trades']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/<symbol>/period', methods=['GET'])
def get_period_data(symbol):
    """Obter dados de um período específico (1m, 3m, 6m, 1y, 5y, max)"""
    try:
        period = request.args.get('period', '1y')
        
        # Calcular data inicial baseado no período
        end_date = datetime.now()
        
        if period == '1m':
            start_date = end_date - timedelta(days=30)
        elif period == '3m':
            start_date = end_date - timedelta(days=90)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        elif period == '5y':
            start_date = end_date - timedelta(days=365*5)
        elif period == 'max':
            start_date = datetime(2005, 1, 1)
        else:
            return jsonify({
                'success': False,
                'error': 'Período inválido. Use: 1m, 3m, 6m, 1y, 5y, max'
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.name, p.date, p.open, p.high, p.low, p.close, p.volume, p.trades
            FROM stocks s
            JOIN prices p ON s.id = p.stock_id
            WHERE s.symbol = ? AND p.date >= ?
            ORDER BY p.date ASC
        ''', (symbol.upper(), start_date.strftime('%Y-%m-%d')))
        
        prices = []
        stock_name = ''
        for row in cursor.fetchall():
            if not stock_name:
                stock_name = row['name']
            prices.append({
                'date': row['date'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume'],
                'trades': row['trades']
            })
        
        conn.close()
        
        if not prices:
            return jsonify({
                'success': False,
                'error': f'Ação {symbol} não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'name': stock_name,
            'period': period,
            'total_records': len(prices),
            'prices': prices
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas do banco de dados"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM stocks')
        total_stocks = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM prices')
        total_prices = cursor.fetchone()['total']
        
        cursor.execute('SELECT MIN(date) as first_date, MAX(date) as last_date FROM prices')
        dates = cursor.fetchone()
        
        conn.close()
        
        # Tamanho do banco
        db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_stocks': total_stocks,
                'total_prices': total_prices,
                'first_date': dates['first_date'],
                'last_date': dates['last_date'],
                'db_size_mb': round(db_size_mb, 2)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Quantum Trades - API em Produção")
    print(f"📂 Banco de dados: {DB_PATH}")
    print(f"🌐 Servidor: http://0.0.0.0:5000")
    print("\n✨ Sistema pronto!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
