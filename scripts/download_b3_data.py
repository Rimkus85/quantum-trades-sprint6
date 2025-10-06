#!/usr/bin/env python3
"""
Script para baixar dados históricos da B3
"""
import requests
import os
from datetime import datetime

# Diretório para salvar os arquivos
output_dir = "/home/ubuntu/b3_historical_data"
os.makedirs(output_dir, exist_ok=True)

# Anos para baixar (últimos 20 anos)
current_year = datetime.now().year
years = range(2005, current_year + 1)

print(f"🚀 Iniciando download de dados históricos da B3")
print(f"📅 Período: 2005 a {current_year} ({len(list(years))} anos)")
print(f"📁 Salvando em: {output_dir}\n")

# URL base da B3 para download
base_url = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP"

downloaded = 0
failed = []

for year in years:
    url = base_url.format(year=year)
    filename = f"COTAHIST_A{year}.ZIP"
    filepath = os.path.join(output_dir, filename)
    
    print(f"📥 Baixando {year}... ", end="", flush=True)
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            size_mb = len(response.content) / (1024 * 1024)
            print(f"✅ OK ({size_mb:.2f} MB)")
            downloaded += 1
        else:
            print(f"❌ Erro {response.status_code}")
            failed.append(year)
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        failed.append(year)

print(f"\n📊 Resumo:")
print(f"✅ Sucesso: {downloaded}")
print(f"❌ Falhas: {len(failed)}")
if failed:
    print(f"Anos com falha: {failed}")

print(f"\n✨ Download concluído!")
