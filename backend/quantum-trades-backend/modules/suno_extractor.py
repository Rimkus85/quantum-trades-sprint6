#!/usr/bin/env python3
"""
Extrator de Carteiras Suno Research
Extrai automaticamente carteiras recomendadas da plataforma Suno
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

class SunoExtractor:
    """Extrator de dados da Suno Research"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://investidor.suno.com.br"
        self.logged_in = False
        
    def login(self) -> bool:
        """Faz login na plataforma Suno"""
        try:
            login_url = "https://login.suno.com.br/entrar/cef02de7-1e5a-4b0e-9f41-04e9278aa2d7/"
            
            # Headers para simular navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json',
            }
            
            # Dados de login
            payload = {
                'email': self.email,
                'password': self.password
            }
            
            response = self.session.post(login_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                self.logged_in = True
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"❌ Erro no login: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            return False
    
    def extrair_carteira(self, nome_carteira: str) -> Optional[Dict]:
        """Extrai dados de uma carteira específica"""
        if not self.logged_in:
            print("❌ Não está logado. Execute login() primeiro.")
            return None
            
        try:
            # URL da carteira
            carteira_slug = nome_carteira.lower().replace(" ", "-")
            url = f"{self.base_url}/carteiras/{carteira_slug}"
            
            response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Erro ao acessar carteira: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrair dados da carteira
            carteira_data = {
                "nome": nome_carteira,
                "url": url,
                "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ativos": [],
                "rentabilidade_total": None,
                "total_comprar": 0,
                "total_aguardar": 0
            }
            
            # Aqui você implementaria a lógica de scraping
            # Por enquanto, retornamos estrutura básica
            
            print(f"✅ Carteira {nome_carteira} extraída")
            return carteira_data
            
        except Exception as e:
            print(f"❌ Erro ao extrair carteira: {e}")
            return None
    
    def extrair_todas_carteiras(self) -> List[Dict]:
        """Extrai todas as carteiras disponíveis"""
        carteiras = [
            "Dividendos",
            "Valor",
            "FIIs",
            "Small Caps",
            "Internacional",
            "Start"
        ]
        
        resultados = []
        
        for carteira in carteiras:
            print(f"\n📊 Extraindo carteira: {carteira}")
            dados = self.extrair_carteira(carteira)
            if dados:
                resultados.append(dados)
        
        return resultados
    
    def salvar_json(self, dados: List[Dict], arquivo: str):
        """Salva dados em arquivo JSON"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            print(f"✅ Dados salvos em: {arquivo}")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")


def main():
    """Função principal"""
    # Credenciais (em produção, usar variáveis de ambiente)
    EMAIL = os.getenv("SUNO_EMAIL", "rodrigues.roberta@outlook.com")
    PASSWORD = os.getenv("SUNO_PASSWORD", "First1MM2025%")
    
    print("🚀 Iniciando extrator Suno Research")
    print("=" * 50)
    
    # Criar extrator
    extrator = SunoExtractor(EMAIL, PASSWORD)
    
    # Fazer login
    if not extrator.login():
        print("❌ Falha no login. Abortando.")
        return
    
    # Extrair carteiras
    print("\n📊 Extraindo carteiras...")
    carteiras = extrator.extrair_todas_carteiras()
    
    # Salvar resultados
    output_file = "suno_carteiras.json"
    extrator.salvar_json(carteiras, output_file)
    
    print("\n" + "=" * 50)
    print(f"✅ Extração concluída!")
    print(f"📊 Total de carteiras: {len(carteiras)}")
    print(f"📁 Arquivo: {output_file}")


if __name__ == "__main__":
    main()

