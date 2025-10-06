#!/usr/bin/env python3
"""
Script de Sincronização Mensal - Quantum Trades
Executa todo dia 02 do mês para importar dados do mês anterior
"""
import requests
import sqlite3
import os
from datetime import datetime, timedelta
import zipfile
import tempfile

# Configurações
DB_PATH = os.path.join(os.path.dirname(__file__), 'b3_data.db')
B3_URL_BASE = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_M{month:02d}{year}.ZIP"

def get_previous_month():
    """Obter mês anterior"""
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    return last_day_prev_month.year, last_day_prev_month.month

def download_monthly_data(year, month):
    """Baixar dados mensais da B3"""
    url = B3_URL_BASE.format(year=year, month=month)
    
    print(f"📥 Baixando dados de {month:02d}/{year}...")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            size_mb = len(response.content) / (1024 * 1024)
            print(f"✅ Download concluído: {size_mb:.2f} MB")
            return response.content
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao baixar: {str(e)}")
        return None

def process_b3_file(zip_content):
    """Processar arquivo ZIP da B3"""
    print("📂 Processando arquivo...")
    
    records = []
    
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(zip_content)
            tmp_path = tmp_file.name
        
        # Extrair e processar
        with zipfile.ZipFile(tmp_path, 'r') as z:
            txt_files = [f for f in z.namelist() if f.endswith('.TXT')]
            
            if not txt_files:
                print("❌ Nenhum arquivo TXT encontrado no ZIP")
                return records
            
            txt_file = txt_files[0]
            print(f"   Processando: {txt_file}")
            
            with z.open(txt_file) as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.decode('latin-1').strip()
                    
                    # Ignorar header e trailer
                    if line.startswith('00') or line.startswith('99'):
                        continue
                    
                    # Tipo de registro
                    tipo_reg = line[0:2]
                    if tipo_reg != '01':
                        continue
                    
                    # Extrair campos
                    data_pregao = line[2:10]
                    cod_bdi = line[10:12]
                    cod_negociacao = line[12:24].strip()
                    nome_empresa = line[27:39].strip()
                    
                    # Preços
                    preco_abertura = int(line[56:69]) / 100.0
                    preco_maximo = int(line[69:82]) / 100.0
                    preco_minimo = int(line[82:95]) / 100.0
                    preco_ultimo = int(line[108:121]) / 100.0
                    
                    # Volume
                    qtd_titulos = int(line[152:170])
                    num_negocios = int(line[147:152])
                    
                    # Filtrar apenas ações
                    if cod_bdi != '02':
                        continue
                    
                    # Filtrar apenas ações principais
                    if not (cod_negociacao.endswith('3') or cod_negociacao.endswith('4') or cod_negociacao.endswith('11')):
                        continue
                    
                    # Ignorar se não teve negociação
                    if preco_ultimo == 0 or qtd_titulos == 0:
                        continue
                    
                    # Formatar data
                    date_str = f"{data_pregao[0:4]}-{data_pregao[4:6]}-{data_pregao[6:8]}"
                    
                    records.append({
                        'symbol': cod_negociacao,
                        'name': nome_empresa,
                        'date': date_str,
                        'open': preco_abertura,
                        'high': preco_maximo,
                        'low': preco_minimo,
                        'close': preco_ultimo,
                        'volume': qtd_titulos,
                        'trades': num_negocios
                    })
        
        # Remover arquivo temporário
        os.unlink(tmp_path)
        
        print(f"✅ {len(records)} registros processados")
        return records
        
    except Exception as e:
        print(f"❌ Erro ao processar: {str(e)}")
        return records

def update_database(records):
    """Atualizar banco de dados"""
    print(f"💾 Atualizando banco de dados...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        stocks_added = 0
        prices_added = 0
        prices_updated = 0
        
        for record in records:
            # Verificar se ação existe
            cursor.execute('SELECT id FROM stocks WHERE symbol = ?', (record['symbol'],))
            stock = cursor.fetchone()
            
            if stock:
                stock_id = stock[0]
            else:
                # Inserir nova ação
                cursor.execute(
                    'INSERT INTO stocks (symbol, name) VALUES (?, ?)',
                    (record['symbol'], record['name'])
                )
                stock_id = cursor.lastrowid
                stocks_added += 1
            
            # Verificar se preço já existe
            cursor.execute(
                'SELECT id FROM prices WHERE stock_id = ? AND date = ?',
                (stock_id, record['date'])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar preço existente
                cursor.execute('''
                    UPDATE prices 
                    SET open = ?, high = ?, low = ?, close = ?, volume = ?, trades = ?
                    WHERE id = ?
                ''', (
                    record['open'], record['high'], record['low'], 
                    record['close'], record['volume'], record['trades'],
                    existing[0]
                ))
                prices_updated += 1
            else:
                # Inserir novo preço
                cursor.execute('''
                    INSERT INTO prices (stock_id, date, open, high, low, close, volume, trades)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock_id, record['date'], record['open'], record['high'],
                    record['low'], record['close'], record['volume'], record['trades']
                ))
                prices_added += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Banco atualizado:")
        print(f"   • Novas ações: {stocks_added}")
        print(f"   • Novos preços: {prices_added}")
        print(f"   • Preços atualizados: {prices_updated}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🚀 Quantum Trades - Sincronização Mensal")
    print("=" * 50)
    
    # Obter mês anterior
    year, month = get_previous_month()
    print(f"📅 Sincronizando dados de {month:02d}/{year}")
    print()
    
    # Baixar dados
    zip_content = download_monthly_data(year, month)
    if not zip_content:
        print("❌ Falha no download. Abortando.")
        return False
    
    print()
    
    # Processar arquivo
    records = process_b3_file(zip_content)
    if not records:
        print("❌ Nenhum registro processado. Abortando.")
        return False
    
    print()
    
    # Atualizar banco
    success = update_database(records)
    
    print()
    print("=" * 50)
    if success:
        print("✅ Sincronização concluída com sucesso!")
    else:
        print("❌ Sincronização falhou!")
    
    return success

if __name__ == '__main__':
    main()
