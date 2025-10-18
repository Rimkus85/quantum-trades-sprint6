#!/usr/bin/env python3
"""
Magnus Wealth - Sistema de Carteiras Customizadas
Cria carteiras personalizadas baseadas em análise fundamentalista profunda
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class MagnusCarteiraCustomizada:
    """
    Sistema de criação de carteiras customizadas
    Objetivo: Rentabilidade > Inflação > Renda Fixa > IBOV
    """
    
    # Benchmarks para comparação
    BENCHMARKS = {
        'inflacao_anual': 4.5,  # Meta IPCA
        'renda_fixa_anual': 10.75,  # CDI aproximado
        'ibov_anual': 15.0  # Estimativa conservadora
    }
    
    def __init__(self):
        self.base_conhecimento = self.carregar_conhecimento()
        self.carteiras_suno = self.carregar_carteiras_suno()
        self.relatorios = self.carregar_relatorios()
        
    def carregar_conhecimento(self) -> Dict:
        """Carrega base de conhecimento do Magnus"""
        try:
            path = Path("youtube_knowledge/magnus_knowledge_base.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def carregar_carteiras_suno(self) -> Dict:
        """Carrega carteiras recomendadas da Suno"""
        try:
            path = Path("suno_data/magnus_suno_knowledge.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def carregar_relatorios(self) -> Dict:
        """Carrega relatórios e análises fundamentalistas"""
        try:
            path = Path("suno_relatorios_conhecimento.json")
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def analisar_ativo(self, ticker: str) -> Dict:
        """Análise fundamentalista completa de um ativo"""
        analise = {
            'ticker': ticker,
            'score_magnus': 0,
            'recomendacao_suno': None,
            'analise_fundamentalista': {},
            'riscos': [],
            'potencial_retorno': 0,
            'dividend_yield': 0,
            'qualidade_fundamentos': 0,
            'fontes': []
        }
        
        # Buscar em carteiras Suno
        if self.carteiras_suno:
            for carteira in self.carteiras_suno.get('carteiras', []):
                for ativo in carteira.get('ativos', []):
                    if ativo.get('ticker') == ticker:
                        analise['recomendacao_suno'] = ativo.get('recomendacao')
                        analise['potencial_retorno'] = float(ativo.get('rentabilidade', '0').replace('%', ''))
                        analise['dividend_yield'] = float(ativo.get('dy_esperado', '0').replace('%', ''))
                        analise['fontes'].append(f"Carteira {carteira['nome']}")
        
        # Buscar em relatórios
        if self.relatorios:
            analises_fund = self.relatorios.get('analises_fundamentalistas', {})
            if ticker in analises_fund:
                analise['analise_fundamentalista'] = analises_fund[ticker]
                analise['fontes'].append("Relatórios Suno")
        
        # Calcular score Magnus (0-100)
        analise['score_magnus'] = self.calcular_score_magnus(analise)
        
        return analise
    
    def calcular_score_magnus(self, analise: Dict) -> float:
        """
        Calcula score Magnus (0-100) baseado em múltiplos fatores
        Quanto maior, melhor o ativo
        """
        score = 0
        
        # Recomendação Suno (30 pontos)
        if analise['recomendacao_suno'] == 'Comprar':
            score += 30
        elif analise['recomendacao_suno'] == 'Aguardar':
            score += 15
        
        # Potencial de retorno (25 pontos)
        if analise['potencial_retorno'] > 50:
            score += 25
        elif analise['potencial_retorno'] > 20:
            score += 15
        elif analise['potencial_retorno'] > 0:
            score += 5
        
        # Dividend Yield (20 pontos)
        if analise['dividend_yield'] > 8:
            score += 20
        elif analise['dividend_yield'] > 5:
            score += 15
        elif analise['dividend_yield'] > 3:
            score += 10
        
        # Múltiplas fontes (15 pontos)
        score += min(len(analise['fontes']) * 5, 15)
        
        # Análise fundamentalista disponível (10 pontos)
        if analise['analise_fundamentalista']:
            score += 10
        
        return min(score, 100)
    
    def criar_carteira_customizada(
        self,
        perfil: str = 'moderado',
        objetivo_retorno: float = 20.0,
        max_ativos: int = 15,
        incluir_renda_fixa: bool = True
    ) -> Dict:
        """
        Cria carteira customizada baseada em análise profunda
        
        Args:
            perfil: conservador, moderado, agressivo
            objetivo_retorno: retorno anual esperado (%)
            max_ativos: número máximo de ativos
            incluir_renda_fixa: incluir alocação em renda fixa
        """
        
        print(f"\n🎯 Criando carteira customizada Magnus")
        print(f"Perfil: {perfil.upper()}")
        print(f"Objetivo: {objetivo_retorno}% ao ano")
        print("=" * 60)
        
        # Coletar todos os ativos disponíveis
        ativos_disponiveis = self.coletar_ativos_disponiveis()
        
        print(f"\n📊 Ativos disponíveis para análise: {len(ativos_disponiveis)}")
        
        # Analisar cada ativo
        ativos_analisados = []
        for ticker in ativos_disponiveis:
            analise = self.analisar_ativo(ticker)
            ativos_analisados.append(analise)
        
        # Ordenar por score Magnus
        ativos_analisados.sort(key=lambda x: x['score_magnus'], reverse=True)
        
        # Filtrar por perfil
        ativos_filtrados = self.filtrar_por_perfil(ativos_analisados, perfil)
        
        # Selecionar top ativos
        ativos_selecionados = ativos_filtrados[:max_ativos]
        
        # Calcular alocações
        alocacoes = self.calcular_alocacoes(
            ativos_selecionados,
            perfil,
            incluir_renda_fixa
        )
        
        # Montar carteira final
        carteira = {
            'nome': f'Magnus Customizada - {perfil.capitalize()}',
            'data_criacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'perfil': perfil,
            'objetivo_retorno_anual': objetivo_retorno,
            'total_ativos': len(alocacoes),
            'alocacoes': alocacoes,
            'retorno_esperado': self.calcular_retorno_esperado(alocacoes),
            'dividend_yield_medio': self.calcular_dy_medio(alocacoes),
            'score_medio': sum(a['score_magnus'] for a in ativos_selecionados) / len(ativos_selecionados),
            'benchmarks': self.BENCHMARKS,
            'vantagem_vs_benchmarks': {}
        }
        
        # Calcular vantagens
        carteira['vantagem_vs_benchmarks'] = {
            'vs_inflacao': carteira['retorno_esperado'] - self.BENCHMARKS['inflacao_anual'],
            'vs_renda_fixa': carteira['retorno_esperado'] - self.BENCHMARKS['renda_fixa_anual'],
            'vs_ibov': carteira['retorno_esperado'] - self.BENCHMARKS['ibov_anual']
        }
        
        return carteira
    
    def coletar_ativos_disponiveis(self) -> List[str]:
        """Coleta todos os ativos disponíveis nas fontes"""
        ativos = set()
        
        # Carteiras Suno
        if self.carteiras_suno:
            for carteira in self.carteiras_suno.get('carteiras', []):
                for ativo in carteira.get('ativos', []):
                    ticker = ativo.get('ticker')
                    if ticker:
                        ativos.add(ticker)
        
        # Relatórios
        if self.relatorios:
            analises = self.relatorios.get('analises_fundamentalistas', {})
            ativos.update(analises.keys())
        
        return list(ativos)
    
    def filtrar_por_perfil(self, ativos: List[Dict], perfil: str) -> List[Dict]:
        """Filtra ativos baseado no perfil de risco"""
        if perfil == 'conservador':
            # Apenas ativos com score > 60 e DY > 5%
            return [a for a in ativos if a['score_magnus'] > 60 and a['dividend_yield'] > 5]
        
        elif perfil == 'moderado':
            # Ativos com score > 50
            return [a for a in ativos if a['score_magnus'] > 50]
        
        elif perfil == 'agressivo':
            # Ativos com alto potencial de retorno
            return [a for a in ativos if a['score_magnus'] > 40 or a['potencial_retorno'] > 30]
        
        return ativos
    
    def calcular_alocacoes(
        self,
        ativos: List[Dict],
        perfil: str,
        incluir_renda_fixa: bool
    ) -> List[Dict]:
        """Calcula alocação percentual de cada ativo"""
        alocacoes = []
        
        # Definir % renda fixa por perfil
        pct_renda_fixa = 0
        if incluir_renda_fixa:
            if perfil == 'conservador':
                pct_renda_fixa = 30
            elif perfil == 'moderado':
                pct_renda_fixa = 15
            elif perfil == 'agressivo':
                pct_renda_fixa = 5
        
        # % disponível para renda variável
        pct_disponivel = 100 - pct_renda_fixa
        
        # Calcular peso de cada ativo baseado no score
        total_score = sum(a['score_magnus'] for a in ativos)
        
        for ativo in ativos:
            peso = (ativo['score_magnus'] / total_score) * pct_disponivel
            
            alocacoes.append({
                'ticker': ativo['ticker'],
                'alocacao_pct': round(peso, 2),
                'score_magnus': ativo['score_magnus'],
                'recomendacao': ativo['recomendacao_suno'],
                'potencial_retorno': ativo['potencial_retorno'],
                'dividend_yield': ativo['dividend_yield'],
                'fontes': ativo['fontes']
            })
        
        # Adicionar renda fixa se necessário
        if pct_renda_fixa > 0:
            alocacoes.append({
                'ticker': 'RENDA_FIXA',
                'alocacao_pct': pct_renda_fixa,
                'score_magnus': 70,
                'recomendacao': 'Comprar',
                'potencial_retorno': self.BENCHMARKS['renda_fixa_anual'],
                'dividend_yield': 0,
                'fontes': ['CDI/Tesouro Direto']
            })
        
        return alocacoes
    
    def calcular_retorno_esperado(self, alocacoes: List[Dict]) -> float:
        """Calcula retorno esperado da carteira"""
        retorno = 0
        for alocacao in alocacoes:
            peso = alocacao['alocacao_pct'] / 100
            retorno += peso * alocacao['potencial_retorno']
        return round(retorno, 2)
    
    def calcular_dy_medio(self, alocacoes: List[Dict]) -> float:
        """Calcula dividend yield médio da carteira"""
        dy = 0
        for alocacao in alocacoes:
            if alocacao['ticker'] != 'RENDA_FIXA':
                peso = alocacao['alocacao_pct'] / 100
                dy += peso * alocacao['dividend_yield']
        return round(dy, 2)
    
    def salvar_carteira(self, carteira: Dict, arquivo: str):
        """Salva carteira em arquivo JSON"""
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(carteira, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Carteira salva: {arquivo}")


def main():
    """Função principal"""
    print("🚀 Magnus Wealth - Carteiras Customizadas")
    print("=" * 60)
    
    magnus = MagnusCarteiraCustomizada()
    
    # Criar carteiras para diferentes perfis
    perfis = ['conservador', 'moderado', 'agressivo']
    
    for perfil in perfis:
        carteira = magnus.criar_carteira_customizada(
            perfil=perfil,
            objetivo_retorno=20.0 if perfil == 'moderado' else (15.0 if perfil == 'conservador' else 30.0),
            max_ativos=12,
            incluir_renda_fixa=True
        )
        
        # Exibir resumo
        print(f"\n📊 CARTEIRA {perfil.upper()}")
        print(f"Retorno esperado: {carteira['retorno_esperado']}% a.a.")
        print(f"DY médio: {carteira['dividend_yield_medio']}%")
        print(f"Score médio: {carteira['score_medio']:.1f}/100")
        print(f"\nVantagens vs Benchmarks:")
        print(f"  vs Inflação: +{carteira['vantagem_vs_benchmarks']['vs_inflacao']:.2f}%")
        print(f"  vs Renda Fixa: +{carteira['vantagem_vs_benchmarks']['vs_renda_fixa']:.2f}%")
        print(f"  vs IBOV: +{carteira['vantagem_vs_benchmarks']['vs_ibov']:.2f}%")
        
        # Salvar
        arquivo = f"carteira_magnus_{perfil}.json"
        magnus.salvar_carteira(carteira, arquivo)
    
    print("\n" + "=" * 60)
    print("✅ Carteiras customizadas criadas com sucesso!")


if __name__ == "__main__":
    main()

