#!/usr/bin/env python3
"""
Script para importar dados JSON da B3 para banco SQLite
"""
import json
import sqlite3
import os
from datetime import datetime

# Caminhos
json_file = "/home/ubuntu/quantum-trades-sprint6/frontend/data/b3_historical_data.json"
db_file = "/home/ubuntu/quantum-trades-sprint6/backend/b3_data.db"

print("🚀 Importando dados para SQLite\n")

# Criar conexão com banco
print("📂 Criando banco de dados...")
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Criar tabelas
print("📋 Criando tabelas...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    date DATE NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume INTEGER NOT NULL,
    trades INTEGER NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    UNIQUE(stock_id, date)
)
''')

# Criar índices para performance
print("🔍 Criando índices...")
cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON stocks(symbol)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_date ON prices(stock_id, date)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON prices(date)')

conn.commit()

# Carregar JSON
print(f"📥 Carregando {json_file}...")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ {len(data)} ações carregadas\n")

# Importar dados
total_stocks = len(data)
total_prices = 0
current = 0

print("💾 Importando dados...")
for symbol, stock_data in data.items():
    current += 1
    
    # Inserir ação
    try:
        cursor.execute(
            'INSERT OR IGNORE INTO stocks (symbol, name) VALUES (?, ?)',
            (symbol, stock_data['name'])
        )
        
        # Obter ID da ação
        cursor.execute('SELECT id FROM stocks WHERE symbol = ?', (symbol,))
        stock_id = cursor.fetchone()[0]
        
        # Inserir preços em lote
        prices_data = [
            (
                stock_id,
                price['date'],
                price['open'],
                price['high'],
                price['low'],
                price['close'],
                price['volume'],
                price['trades']
            )
            for price in stock_data['prices']
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO prices (stock_id, date, open, high, low, close, volume, trades) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            prices_data
        )
        
        total_prices += len(prices_data)
        
        # Commit a cada 50 ações
        if current % 50 == 0:
            conn.commit()
            progress = (current / total_stocks) * 100
            print(f"  {current}/{total_stocks} ({progress:.1f}%) - {total_prices:,} registros")
    
    except Exception as e:
        print(f"❌ Erro ao importar {symbol}: {str(e)}")

# Commit final
conn.commit()

print(f"\n✅ Importação concluída!")
print(f"📊 Estatísticas:")
print(f"  • Ações: {total_stocks:,}")
print(f"  • Registros de preços: {total_prices:,}")

# Verificar tamanho do banco
db_size_mb = os.path.getsize(db_file) / (1024 * 1024)
print(f"  • Tamanho do banco: {db_size_mb:.2f} MB")

# Fechar conexão
conn.close()

print(f"\n✨ Banco de dados pronto: {db_file}")
