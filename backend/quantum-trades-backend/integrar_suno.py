#!/usr/bin/env python3
"""
Integrador Suno + Magnus Learning
Integra carteiras da Suno à base de conhecimento do Magnus
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório modules ao path
sys.path.append(str(Path(__file__).parent))

from modules.suno_extractor import SunoExtractor


def integrar_suno_magnus():
    """Integra dados da Suno com base de conhecimento Magnus"""
    
    print("🚀 Magnus Wealth - Integração Suno Research")
    print("=" * 60)
    
    # Credenciais
    EMAIL = os.getenv("SUNO_EMAIL", "rodrigues.roberta@outlook.com")
    PASSWORD = os.getenv("SUNO_PASSWORD", "First1MM2025%")
    
    # Criar extrator
    print("\n📡 Conectando à Suno Research...")
    extrator = SunoExtractor(EMAIL, PASSWORD)
    
    # Login
    if not extrator.login():
        print("❌ Falha no login")
        return False
    
    # Extrair carteiras
    print("\n📊 Extraindo carteiras recomendadas...")
    carteiras = extrator.extrair_todas_carteiras()
    
    if not carteiras:
        print("❌ Nenhuma carteira extraída")
        return False
    
    # Salvar dados brutos
    output_dir = Path("suno_data")
    output_dir.mkdir(exist_ok=True)
    
    arquivo_carteiras = output_dir / "carteiras.json"
    extrator.salvar_json(carteiras, str(arquivo_carteiras))
    
    # Integrar com base de conhecimento Magnus
    print("\n🧠 Integrando com Magnus Learning...")
    
    base_conhecimento = {
        "fonte": "Suno Research",
        "tipo": "carteiras_recomendadas",
        "data_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_carteiras": len(carteiras),
        "carteiras": carteiras,
        "estatisticas": {
            "total_ativos_comprar": sum(c.get("total_comprar", 0) for c in carteiras),
            "total_ativos_aguardar": sum(c.get("total_aguardar", 0) for c in carteiras),
        }
    }
    
    # Salvar base integrada
    arquivo_base = output_dir / "magnus_suno_knowledge.json"
    with open(arquivo_base, 'w', encoding='utf-8') as f:
        json.dump(base_conhecimento, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Base de conhecimento salva: {arquivo_base}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DA INTEGRAÇÃO")
    print("=" * 60)
    print(f"✅ Carteiras extraídas: {len(carteiras)}")
    print(f"✅ Ativos para comprar: {base_conhecimento['estatisticas']['total_ativos_comprar']}")
    print(f"✅ Ativos para aguardar: {base_conhecimento['estatisticas']['total_ativos_aguardar']}")
    print(f"📁 Dados salvos em: {output_dir}")
    print("\n🎉 Integração concluída com sucesso!")
    
    return True


if __name__ == "__main__":
    sucesso = integrar_suno_magnus()
    sys.exit(0 if sucesso else 1)

