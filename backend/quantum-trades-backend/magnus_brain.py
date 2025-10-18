#!/usr/bin/env python3
"""
Magnus Brain - Cérebro Unificado do Magnus Wealth
Integra TODAS as fontes de conhecimento em uma personalidade única
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class MagnusBrain:
    """
    Cérebro do Magnus - Integração total de conhecimento
    
    Fontes integradas:
    1. Vídeos YouTube (estratégias, setups)
    2. Carteiras Suno (6 carteiras profissionais)
    3. Relatórios Suno (análises fundamentalistas)
    4. Telegram (grupos de investimento)
    5. Análise Técnica (Fibonacci, suportes, resistências)
    6. Histórico de decisões (acertos e erros)
    """
    
    def __init__(self):
        self.conhecimento_unificado = {
            "versao": "1.0.0",
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fontes": {},
            "ativos": {},
            "estrategias": {},
            "conceitos": {},
            "padroes": {},
            "decisoes": {
                "acertos": [],
                "erros": [],
                "aprendizados": []
            },
            "personalidade": {
                "preferencias": {},
                "estilos": [],
                "regras": []
            }
        }
        
    def carregar_todas_fontes(self):
        """Carrega e integra todas as fontes de conhecimento"""
        print("🧠 Magnus Brain - Carregando conhecimento...")
        print("=" * 60)
        
        # 1. Vídeos YouTube
        print("\n📺 Carregando vídeos YouTube...")
        self.integrar_videos_youtube()
        
        # 2. Carteiras Suno
        print("\n📊 Carregando carteiras Suno...")
        self.integrar_carteiras_suno()
        
        # 3. Relatórios Suno
        print("\n📄 Carregando relatórios Suno...")
        self.integrar_relatorios_suno()
        
        # 4. Telegram
        print("\n💬 Carregando dados Telegram...")
        self.integrar_telegram()
        
        # 5. Análise Técnica
        print("\n📈 Carregando análise técnica...")
        self.integrar_analise_tecnica()
        
        # 6. Processar e consolidar
        print("\n🔄 Consolidando conhecimento...")
        self.consolidar_conhecimento()
        
        print("\n✅ Conhecimento carregado e integrado!")
        
    def integrar_videos_youtube(self):
        """Integra conhecimento dos vídeos do YouTube"""
        try:
            path = Path("youtube_knowledge/magnus_knowledge_base.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.conhecimento_unificado['fontes']['youtube'] = {
                    'total_videos': len(data.get('videos', [])),
                    'total_palavras': data.get('total_palavras', 0),
                    'relevancia_media': data.get('relevancia_media', 0),
                    'estrategias': data.get('estrategias', []),
                    'conceitos': data.get('conceitos', []),
                    'recomendacoes': data.get('recomendacoes', [])
                }
                
                # Adicionar estratégias
                for estrategia in data.get('estrategias', []):
                    nome = estrategia.get('nome', '')
                    if nome not in self.conhecimento_unificado['estrategias']:
                        self.conhecimento_unificado['estrategias'][nome] = {
                            'fontes': [],
                            'descricao': estrategia.get('descricao', ''),
                            'tipo': estrategia.get('tipo', ''),
                            'confianca': 0
                        }
                    self.conhecimento_unificado['estrategias'][nome]['fontes'].append('youtube')
                    self.conhecimento_unificado['estrategias'][nome]['confianca'] += 1
                
                # Adicionar conceitos
                for conceito in data.get('conceitos', []):
                    nome = conceito.get('conceito', '')
                    if nome:
                        if nome not in self.conhecimento_unificado['conceitos']:
                            self.conhecimento_unificado['conceitos'][nome] = {
                                'mencoes': 0,
                                'fontes': set(),
                                'contextos': []
                            }
                        self.conhecimento_unificado['conceitos'][nome]['mencoes'] += conceito.get('mencoes', 0)
                        self.conhecimento_unificado['conceitos'][nome]['fontes'].add('youtube')
                
                print(f"  ✅ {len(data.get('videos', []))} vídeos integrados")
                
        except Exception as e:
            print(f"  ⚠️ Erro ao integrar YouTube: {e}")
    
    def integrar_carteiras_suno(self):
        """Integra carteiras recomendadas da Suno"""
        try:
            path = Path("suno_data/magnus_suno_knowledge.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.conhecimento_unificado['fontes']['suno_carteiras'] = {
                    'total_carteiras': len(data.get('carteiras', [])),
                    'total_ativos': sum(len(c.get('ativos', [])) for c in data.get('carteiras', [])),
                    'carteiras': data.get('carteiras', [])
                }
                
                # Processar cada carteira
                for carteira in data.get('carteiras', []):
                    nome_carteira = carteira.get('nome', '')
                    
                    # Adicionar como estratégia
                    if nome_carteira not in self.conhecimento_unificado['estrategias']:
                        self.conhecimento_unificado['estrategias'][nome_carteira] = {
                            'fontes': [],
                            'tipo': 'portfolio',
                            'confianca': 0,
                            'rentabilidade': carteira.get('rentabilidade_total', '0')
                        }
                    self.conhecimento_unificado['estrategias'][nome_carteira]['fontes'].append('suno_carteiras')
                    self.conhecimento_unificado['estrategias'][nome_carteira]['confianca'] += 2  # Peso maior para Suno
                    
                    # Processar ativos
                    for ativo in carteira.get('ativos', []):
                        ticker = ativo.get('ticker', '')
                        if ticker:
                            if ticker not in self.conhecimento_unificado['ativos']:
                                self.conhecimento_unificado['ativos'][ticker] = {
                                    'recomendacoes': [],
                                    'analises': [],
                                    'carteiras': [],
                                    'score_agregado': 0
                                }
                            
                            self.conhecimento_unificado['ativos'][ticker]['recomendacoes'].append({
                                'fonte': 'suno_carteiras',
                                'carteira': nome_carteira,
                                'tipo': ativo.get('recomendacao', ''),
                                'preco_entrada': ativo.get('preco_entrada', 0),
                                'preco_teto': ativo.get('preco_teto', 0),
                                'rentabilidade': ativo.get('rentabilidade', '0'),
                                'dy': ativo.get('dy_esperado', '0')
                            })
                            
                            self.conhecimento_unificado['ativos'][ticker]['carteiras'].append(nome_carteira)
                
                print(f"  ✅ {len(data.get('carteiras', []))} carteiras integradas")
                
        except Exception as e:
            print(f"  ⚠️ Erro ao integrar carteiras Suno: {e}")
    
    def integrar_relatorios_suno(self):
        """Integra relatórios e análises da Suno"""
        try:
            path = Path("suno_relatorios_conhecimento.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.conhecimento_unificado['fontes']['suno_relatorios'] = {
                    'total_relatorios': len(data.get('relatorios', [])),
                    'tipos': list(set(r.get('tipo', '') for r in data.get('relatorios', []))),
                    'insights': data.get('insights', {})
                }
                
                # Processar recomendações de compra/venda
                for ativo in data.get('insights', {}).get('ativos_recomendados_compra', []):
                    ticker = ativo.get('ticker', '')
                    if ticker:
                        if ticker not in self.conhecimento_unificado['ativos']:
                            self.conhecimento_unificado['ativos'][ticker] = {
                                'recomendacoes': [],
                                'analises': [],
                                'carteiras': [],
                                'score_agregado': 0
                            }
                        
                        self.conhecimento_unificado['ativos'][ticker]['recomendacoes'].append({
                            'fonte': 'suno_relatorios',
                            'tipo': 'compra',
                            'relatorio': ativo.get('relatorio', ''),
                            'data': ativo.get('data', '')
                        })
                
                print(f"  ✅ {len(data.get('relatorios', []))} relatórios integrados")
                
        except Exception as e:
            print(f"  ⚠️ Erro ao integrar relatórios Suno: {e}")
    
    def integrar_telegram(self):
        """Integra dados dos grupos Telegram"""
        try:
            # Buscar arquivos de dados do Telegram
            telegram_files = list(Path(".").glob("*telegram*.json"))
            
            if telegram_files:
                self.conhecimento_unificado['fontes']['telegram'] = {
                    'grupos_monitorados': [],
                    'mensagens_processadas': 0,
                    'links_youtube': 0
                }
                
                print(f"  ✅ {len(telegram_files)} arquivos Telegram encontrados")
            else:
                print(f"  ⚠️ Nenhum arquivo Telegram encontrado")
                
        except Exception as e:
            print(f"  ⚠️ Erro ao integrar Telegram: {e}")
    
    def integrar_analise_tecnica(self):
        """Integra conhecimento de análise técnica"""
        # Conhecimento hard-coded de análise técnica
        self.conhecimento_unificado['fontes']['analise_tecnica'] = {
            'setups': [
                'Fibonacci Retracement',
                'Suportes e Resistências',
                'Médias Móveis',
                'IFR (Índice de Força Relativa)',
                'MACD',
                'Bandas de Bollinger'
            ],
            'padroes': [
                'Triângulo Ascendente',
                'Triângulo Descendente',
                'Ombro-Cabeça-Ombro',
                'Topo Duplo',
                'Fundo Duplo',
                'Bandeira',
                'Flâmula'
            ]
        }
        
        # Adicionar setups como estratégias
        for setup in self.conhecimento_unificado['fontes']['analise_tecnica']['setups']:
            if setup not in self.conhecimento_unificado['estrategias']:
                self.conhecimento_unificado['estrategias'][setup] = {
                    'fontes': ['analise_tecnica'],
                    'tipo': 'tecnica',
                    'confianca': 1
                }
        
        print(f"  ✅ {len(self.conhecimento_unificado['fontes']['analise_tecnica']['setups'])} setups integrados")
    
    def consolidar_conhecimento(self):
        """Consolida e processa todo o conhecimento"""
        
        # Calcular score agregado para cada ativo
        for ticker, dados in self.conhecimento_unificado['ativos'].items():
            score = 0
            
            # +10 pontos por cada recomendação de compra
            compras = [r for r in dados['recomendacoes'] if r.get('tipo') in ['Comprar', 'compra']]
            score += len(compras) * 10
            
            # +5 pontos por cada carteira que contém o ativo
            score += len(dados['carteiras']) * 5
            
            # +15 pontos se tem análise fundamentalista
            if dados['analises']:
                score += 15
            
            dados['score_agregado'] = min(score, 100)
        
        # Identificar estratégias mais confiáveis
        estrategias_ordenadas = sorted(
            self.conhecimento_unificado['estrategias'].items(),
            key=lambda x: x[1]['confianca'],
            reverse=True
        )
        
        # Criar personalidade Magnus
        self.conhecimento_unificado['personalidade'] = {
            'top_estrategias': [e[0] for e in estrategias_ordenadas[:10]],
            'preferencias': {
                'foco_dividendos': self.calcular_preferencia_dividendos(),
                'foco_crescimento': self.calcular_preferencia_crescimento(),
                'tolerancia_risco': self.calcular_tolerancia_risco()
            },
            'regras': self.gerar_regras_decisao()
        }
        
        # Estatísticas gerais
        self.conhecimento_unificado['estatisticas'] = {
            'total_fontes': len([k for k, v in self.conhecimento_unificado['fontes'].items() if v]),
            'total_ativos': len(self.conhecimento_unificado['ativos']),
            'total_estrategias': len(self.conhecimento_unificado['estrategias']),
            'total_conceitos': len(self.conhecimento_unificado['conceitos']),
            'ativos_alta_confianca': len([a for a in self.conhecimento_unificado['ativos'].values() if a['score_agregado'] > 70])
        }
    
    def calcular_preferencia_dividendos(self) -> float:
        """Calcula preferência por dividendos (0-1)"""
        # Verificar quantas estratégias focam em dividendos
        total = len(self.conhecimento_unificado['estrategias'])
        if total == 0:
            return 0.5
        
        dividendos = sum(1 for e in self.conhecimento_unificado['estrategias'].values() 
                        if 'dividend' in str(e).lower() or 'renda' in str(e).lower())
        
        return dividendos / total
    
    def calcular_preferencia_crescimento(self) -> float:
        """Calcula preferência por crescimento (0-1)"""
        total = len(self.conhecimento_unificado['estrategias'])
        if total == 0:
            return 0.5
        
        crescimento = sum(1 for e in self.conhecimento_unificado['estrategias'].values() 
                         if 'small' in str(e).lower() or 'crescimento' in str(e).lower() or 'growth' in str(e).lower())
        
        return crescimento / total
    
    def calcular_tolerancia_risco(self) -> str:
        """Calcula tolerância ao risco baseada nas estratégias"""
        # Analisar tipos de estratégias predominantes
        tipos = [e.get('tipo', '') for e in self.conhecimento_unificado['estrategias'].values()]
        
        if tipos.count('portfolio') > tipos.count('tecnica'):
            return 'moderado'
        elif 'small' in str(tipos).lower():
            return 'agressivo'
        else:
            return 'conservador'
    
    def gerar_regras_decisao(self) -> List[str]:
        """Gera regras de decisão baseadas no conhecimento"""
        regras = []
        
        # Regra 1: Múltiplas fontes
        regras.append("Priorizar ativos recomendados por múltiplas fontes")
        
        # Regra 2: Score mínimo
        regras.append("Considerar apenas ativos com score agregado > 50")
        
        # Regra 3: Diversificação
        regras.append("Manter diversificação entre setores e estratégias")
        
        # Regra 4: Benchmarking
        regras.append("Buscar rentabilidade > Inflação > Renda Fixa > IBOV")
        
        # Regra 5: Análise fundamentalista
        regras.append("Validar com análise fundamentalista quando disponível")
        
        return regras
    
    def salvar_conhecimento(self, arquivo: str = "magnus_brain.json"):
        """Salva conhecimento unificado"""
        # Converter sets para lists antes de salvar
        conhecimento_serializavel = self._preparar_para_json(self.conhecimento_unificado)
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(conhecimento_serializavel, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Conhecimento salvo: {arquivo}")
    
    def _preparar_para_json(self, obj):
        """Prepara objeto para serialização JSON"""
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: self._preparar_para_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._preparar_para_json(item) for item in obj]
        else:
            return obj
    
    def exibir_resumo(self):
        """Exibe resumo do conhecimento Magnus"""
        print("\n" + "=" * 60)
        print("🧠 MAGNUS BRAIN - RESUMO DO CONHECIMENTO")
        print("=" * 60)
        
        stats = self.conhecimento_unificado['estatisticas']
        print(f"\n📊 Estatísticas:")
        print(f"  • Fontes integradas: {stats['total_fontes']}")
        print(f"  • Ativos analisados: {stats['total_ativos']}")
        print(f"  • Estratégias identificadas: {stats['total_estrategias']}")
        print(f"  • Conceitos aprendidos: {stats['total_conceitos']}")
        print(f"  • Ativos alta confiança: {stats['ativos_alta_confianca']}")
        
        pers = self.conhecimento_unificado['personalidade']
        print(f"\n🎯 Personalidade Magnus:")
        print(f"  • Foco dividendos: {pers['preferencias']['foco_dividendos']:.1%}")
        print(f"  • Foco crescimento: {pers['preferencias']['foco_crescimento']:.1%}")
        print(f"  • Tolerância risco: {pers['preferencias']['tolerancia_risco']}")
        
        print(f"\n🏆 Top 5 Estratégias:")
        for i, estrategia in enumerate(pers['top_estrategias'][:5], 1):
            conf = self.conhecimento_unificado['estrategias'][estrategia]['confianca']
            print(f"  {i}. {estrategia} (confiança: {conf})")
        
        print(f"\n📜 Regras de Decisão:")
        for i, regra in enumerate(pers['regras'], 1):
            print(f"  {i}. {regra}")


def main():
    """Função principal"""
    print("🚀 Magnus Brain - Integração Total de Conhecimento")
    print("=" * 60)
    
    # Criar cérebro Magnus
    brain = MagnusBrain()
    
    # Carregar todas as fontes
    brain.carregar_todas_fontes()
    
    # Exibir resumo
    brain.exibir_resumo()
    
    # Salvar conhecimento unificado
    brain.salvar_conhecimento()
    
    print("\n" + "=" * 60)
    print("✅ Magnus Brain criado com sucesso!")
    print("🧠 Personalidade própria estabelecida!")


if __name__ == "__main__":
    main()

