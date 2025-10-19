#!/usr/bin/env python3
"""
Script para extrair TODOS os vídeos da plataforma Tio Huli
e processar automaticamente
"""

import json
import time
from pathlib import Path

# Mapeamento completo da plataforma
CURSOS_TIOHULI = {
    "prioridade_alta": [
        {
            "nome": "Sala de Opções",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=saladeopcoes",
            "tipo": "opcoes",
            "descricao": "Sinais e estratégias de opções (calls e puts)"
        },
        {
            "nome": "Sala de Sinais Cripto",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=saladesinaiscripto",
            "tipo": "cripto",
            "descricao": "Sinais e análises de criptomoedas"
        },
        {
            "nome": "Máquina de Ganhos Explosivos",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=maquinadeganhos",
            "tipo": "estrategias",
            "descricao": "Estratégias avançadas de trading"
        }
    ],
    
    "prioridade_media": [
        {
            "nome": "Mentoria Start Milionário",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=startmilionario",
            "tipo": "mentoria",
            "descricao": "Mentoria completa para iniciantes"
        },
        {
            "nome": "Fábrica de Ganhos Explosivos",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=fabricadeganhos",
            "tipo": "estrategias",
            "descricao": "Estratégias de alto retorno"
        },
        {
            "nome": "Sala 1KF",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=sala1kf",
            "tipo": "renda_fixa",
            "descricao": "Estratégias de renda fixa"
        },
        {
            "nome": "500 Dólares por Semana",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=500dolares",
            "tipo": "internacional",
            "descricao": "Renda em dólar"
        }
    ],
    
    "prioridade_baixa": [
        {
            "nome": "Master Business",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=masterbusiness",
            "tipo": "negocios",
            "descricao": "Empreendedorismo e negócios"
        },
        {
            "nome": "Reset 21",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=reset21",
            "tipo": "mindset",
            "descricao": "Reprogramação mental"
        },
        {
            "nome": "InvestClub",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=investclub",
            "tipo": "comunidade",
            "descricao": "Clube de investidores"
        },
        {
            "nome": "Radar de Renda",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=radarderenda",
            "tipo": "renda_fixa",
            "descricao": "Análise de renda fixa"
        },
        {
            "nome": "Indicador GX",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=indicadorgx",
            "tipo": "ferramenta",
            "descricao": "Indicador técnico"
        },
        {
            "nome": "Guia Anticrise",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=guiaanticrise",
            "tipo": "protecao",
            "descricao": "Proteção de patrimônio"
        },
        {
            "nome": "Carteira Recomendada Start",
            "url": "https://membros.tiohuli.com.br/m/courses?tenant=carteirarecomendada",
            "tipo": "carteira",
            "descricao": "Carteira para iniciantes"
        }
    ]
}

def salvar_mapeamento():
    """Salva mapeamento completo em JSON"""
    output_file = Path(__file__).parent / "tiohuli_cursos_mapeamento.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(CURSOS_TIOHULI, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Mapeamento salvo: {output_file}")
    
    # Estatísticas
    total = (len(CURSOS_TIOHULI["prioridade_alta"]) + 
             len(CURSOS_TIOHULI["prioridade_media"]) + 
             len(CURSOS_TIOHULI["prioridade_baixa"]))
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"  • Prioridade Alta: {len(CURSOS_TIOHULI['prioridade_alta'])} cursos")
    print(f"  • Prioridade Média: {len(CURSOS_TIOHULI['prioridade_media'])} cursos")
    print(f"  • Prioridade Baixa: {len(CURSOS_TIOHULI['prioridade_baixa'])} cursos")
    print(f"  • TOTAL: {total} cursos")
    
    return output_file

def gerar_plano_extracao():
    """Gera plano de extração de vídeos"""
    print("\n" + "="*80)
    print("PLANO DE EXTRAÇÃO DE VÍDEOS - PLATAFORMA TIO HULI")
    print("="*80)
    
    print("\n🎯 FASE 1: PRIORIDADE ALTA (Opções, Cripto, Estratégias)")
    for curso in CURSOS_TIOHULI["prioridade_alta"]:
        print(f"  ✓ {curso['nome']}")
        print(f"    URL: {curso['url']}")
        print(f"    Tipo: {curso['tipo']}")
        print()
    
    print("\n📊 FASE 2: PRIORIDADE MÉDIA (Mentorias e Cursos)")
    for curso in CURSOS_TIOHULI["prioridade_media"]:
        print(f"  ○ {curso['nome']}")
        print(f"    URL: {curso['url']}")
        print()
    
    print("\n📚 FASE 3: PRIORIDADE BAIXA (Complementares)")
    for curso in CURSOS_TIOHULI["prioridade_baixa"]:
        print(f"  ○ {curso['nome']}")
    
    print("\n" + "="*80)
    print("PRÓXIMOS PASSOS:")
    print("="*80)
    print("1. Usar browser automation para acessar cada curso")
    print("2. Listar todas as aulas de cada curso")
    print("3. Extrair URLs dos vídeos")
    print("4. Processar com processar_videos_longos.py")
    print("5. Integrar conhecimento no Magnus Brain")
    print("="*80)

def main():
    """Função principal"""
    print("🎬 EXTRATOR DE VÍDEOS - TIO HULI")
    print()
    
    # Salvar mapeamento
    arquivo = salvar_mapeamento()
    
    # Gerar plano
    gerar_plano_extracao()
    
    print(f"\n✅ Mapeamento completo salvo em: {arquivo}")
    print("\nPróximo passo: Usar browser automation para extrair links dos vídeos")

if __name__ == "__main__":
    main()

