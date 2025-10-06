#!/usr/bin/env python3
"""
Script para processar dados históricos da B3 e gerar JSON otimizado
Formato COTAHIST da B3 - Posições fixas
"""
import zipfile
import json
import os
from datetime import datetime
from collections import defaultdict

# Diretórios
input_dir = "/home/ubuntu/b3_historical_data"
output_dir = "/home/ubuntu/quantum-trades-sprint6/frontend/data"
os.makedirs(output_dir, exist_ok=True)

print("🚀 Processando dados históricos da B3\n")

# Estrutura para armazenar dados
stocks_data = defaultdict(lambda: {
    'symbol': '',
    'name': '',
    'prices': []
})

# Anos para processar
years = range(2005, 2026)
total_records = 0
processed_years = 0

for year in years:
    zip_file = os.path.join(input_dir, f"COTAHIST_A{year}.ZIP")
    
    if not os.path.exists(zip_file):
        print(f"⏭️  {year}: arquivo não encontrado")
        continue
    
    print(f"📂 Processando {year}... ", end="", flush=True)
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            txt_file = f"COTAHIST_A{year}.TXT"
            with z.open(txt_file) as f:
                lines = f.readlines()
                year_records = 0
                
                for line in lines:
                    line = line.decode('latin-1').strip()
                    
                    # Ignorar header e trailer
                    if line.startswith('00') or line.startswith('99'):
                        continue
                    
                    # Tipo de registro (posição 0-1)
                    tipo_reg = line[0:2]
                    if tipo_reg != '01':
                        continue
                    
                    # Extrair campos (posições fixas conforme layout B3)
                    data_pregao = line[2:10]  # AAAAMMDD
                    cod_bdi = line[10:12]
                    cod_negociacao = line[12:24].strip()  # Ticker
                    tipo_mercado = line[24:27]
                    nome_empresa = line[27:39].strip()
                    especificacao = line[39:49].strip()
                    prazo_dias = line[49:52]
                    moeda = line[52:56].strip()
                    
                    # Preços (valores inteiros, dividir por 100)
                    preco_abertura = int(line[56:69]) / 100.0
                    preco_maximo = int(line[69:82]) / 100.0
                    preco_minimo = int(line[82:95]) / 100.0
                    preco_medio = int(line[95:108]) / 100.0
                    preco_ultimo = int(line[108:121]) / 100.0
                    preco_melhor_compra = int(line[121:134]) / 100.0
                    preco_melhor_venda = int(line[134:147]) / 100.0
                    
                    # Volume
                    num_negocios = int(line[147:152])
                    qtd_titulos = int(line[152:170])
                    vol_total = int(line[170:188]) / 100.0
                    
                    # Filtrar apenas ações (tipo 010 = ações)
                    if cod_bdi != '02':
                        continue
                    
                    # Filtrar apenas ações principais (ON, PN, UNT)
                    if not (cod_negociacao.endswith('3') or cod_negociacao.endswith('4') or cod_negociacao.endswith('11')):
                        continue
                    
                    # Ignorar se não teve negociação
                    if preco_ultimo == 0 or vol_total == 0:
                        continue
                    
                    # Formatar data
                    date_str = f"{data_pregao[0:4]}-{data_pregao[4:6]}-{data_pregao[6:8]}"
                    
                    # Armazenar dados
                    if not stocks_data[cod_negociacao]['symbol']:
                        stocks_data[cod_negociacao]['symbol'] = cod_negociacao
                        stocks_data[cod_negociacao]['name'] = nome_empresa
                    
                    stocks_data[cod_negociacao]['prices'].append({
                        'date': date_str,
                        'open': preco_abertura,
                        'high': preco_maximo,
                        'low': preco_minimo,
                        'close': preco_ultimo,
                        'volume': qtd_titulos,
                        'trades': num_negocios
                    })
                    
                    year_records += 1
                    total_records += 1
                
                print(f"✅ {year_records:,} registros")
                processed_years += 1
                
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

print(f"\n📊 Processamento concluído:")
print(f"✅ Anos processados: {processed_years}")
print(f"✅ Total de registros: {total_records:,}")
print(f"✅ Ações únicas: {len(stocks_data)}")

# Filtrar apenas ações com dados significativos (pelo menos 100 registros)
filtered_stocks = {k: v for k, v in stocks_data.items() if len(v['prices']) >= 100}
print(f"✅ Ações com dados completos: {len(filtered_stocks)}")

# Ordenar preços por data
print(f"\n📈 Ordenando dados...")
for symbol in filtered_stocks:
    filtered_stocks[symbol]['prices'].sort(key=lambda x: x['date'])

# Salvar em JSON
output_file = os.path.join(output_dir, 'b3_historical_data.json')
print(f"\n💾 Salvando em {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(filtered_stocks, f, ensure_ascii=False, separators=(',', ':'))

file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
print(f"✅ Arquivo salvo: {file_size_mb:.2f} MB")

# Criar arquivo de metadados
metadata = {
    'generated_at': datetime.now().isoformat(),
    'period': '2005-2025',
    'total_stocks': len(filtered_stocks),
    'total_records': total_records,
    'file_size_mb': round(file_size_mb, 2)
}

metadata_file = os.path.join(output_dir, 'b3_metadata.json')
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Metadados salvos: {metadata_file}")
print(f"\n✨ Processamento completo!")
