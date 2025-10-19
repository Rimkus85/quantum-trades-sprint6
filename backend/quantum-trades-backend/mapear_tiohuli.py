#!/usr/bin/env python3
"""
Script para mapear toda a plataforma Tio Huli e extrair conhecimento
"""

# Mapeamento completo da plataforma baseado na navegação

PLATAFORMA_TIOHULI = {
    "mentorias": [
        {
            "nome": "Master Business",
            "tipo": "Mentoria",
            "foco": "Negócios e Empreendedorismo"
        },
        {
            "nome": "Mentoria Start Milionário",
            "tipo": "Mentoria",
            "foco": "Investimentos para Iniciantes"
        }
    ],
    
    "salas_recomendacao": [
        {
            "nome": "Sala de Opções",
            "tipo": "Sala de Sinais",
            "foco": "Opções (Calls e Puts)",
            "conteudo": [
                "Comece por aqui - Sala de Opções",
                "Como executar os sinais enviados",
                "Encontros Ao Vivo com Tio Huli",
                "Encontros Ao Vivo com Fernando Kling",
                "Marco Zero das Opções (31 aulas)",
                "Sinais da Bolsa"
            ],
            "prioridade": "ALTA"
        },
        {
            "nome": "Sala de Sinais Cripto",
            "tipo": "Sala de Sinais",
            "foco": "Criptomoedas",
            "prioridade": "ALTA"
        },
        {
            "nome": "Sala 1KF",
            "tipo": "Sala de Sinais",
            "foco": "Estratégias de Renda Fixa"
        },
        {
            "nome": "Carteira Recomendada Start",
            "tipo": "Carteira",
            "foco": "Ações para Iniciantes"
        }
    ],
    
    "treinamentos": [
        {
            "nome": "Máquina de Ganhos Explosivos",
            "tipo": "Curso",
            "foco": "Estratégias Avançadas"
        },
        {
            "nome": "Reset 21 - Protocolo Oficial de Reprogramação",
            "tipo": "Curso",
            "foco": "Mindset e Reprogramação Mental"
        },
        {
            "nome": "InvestClub",
            "tipo": "Clube",
            "foco": "Comunidade de Investidores"
        },
        {
            "nome": "Radar de Renda",
            "tipo": "Curso",
            "foco": "Renda Fixa"
        },
        {
            "nome": "500 Dólares por Semana",
            "tipo": "Curso",
            "foco": "Renda em Dólar"
        },
        {
            "nome": "Fábrica de Ganhos Explosivos",
            "tipo": "Curso",
            "foco": "Estratégias de Alto Retorno"
        },
        {
            "nome": "Indicador GX",
            "tipo": "Ferramenta",
            "foco": "Indicador Técnico"
        },
        {
            "nome": "Guia Anticrise",
            "tipo": "Guia",
            "foco": "Proteção de Patrimônio"
        }
    ]
}

# Áreas prioritárias para extração de conhecimento
PRIORIDADES = {
    "alta": [
        "Sala de Opções",
        "Marco Zero das Opções",
        "Sala de Sinais Cripto",
        "Máquina de Ganhos Explosivos"
    ],
    "media": [
        "Mentoria Start Milionário",
        "Carteira Recomendada Start",
        "Fábrica de Ganhos Explosivos"
    ],
    "baixa": [
        "Reset 21",
        "InvestClub",
        "Guia Anticrise"
    ]
}

def listar_conteudos():
    """Lista todos os conteúdos disponíveis"""
    print("=" * 80)
    print("MAPEAMENTO COMPLETO - PLATAFORMA TIO HULI")
    print("=" * 80)
    
    print("\n📚 MENTORIAS:")
    for item in PLATAFORMA_TIOHULI["mentorias"]:
        print(f"  • {item['nome']} - {item['foco']}")
    
    print("\n📊 SALAS DE RECOMENDAÇÃO:")
    for item in PLATAFORMA_TIOHULI["salas_recomendacao"]:
        prioridade = item.get('prioridade', 'MÉDIA')
        print(f"  • {item['nome']} - {item['foco']} [{prioridade}]")
        if 'conteudo' in item:
            for sub in item['conteudo']:
                print(f"    - {sub}")
    
    print("\n🎓 TREINAMENTOS E CURSOS:")
    for item in PLATAFORMA_TIOHULI["treinamentos"]:
        print(f"  • {item['nome']} - {item['foco']}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {len(PLATAFORMA_TIOHULI['mentorias'])} mentorias + "
          f"{len(PLATAFORMA_TIOHULI['salas_recomendacao'])} salas + "
          f"{len(PLATAFORMA_TIOHULI['treinamentos'])} treinamentos")
    print("=" * 80)

if __name__ == "__main__":
    listar_conteudos()

