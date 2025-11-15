#!/usr/bin/env python3
"""
Portfolio Manager - Magnus Wealth v9.0.0

Gerencia configuração dinâmica de criptomoedas do portfólio
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class PortfolioManager:
    """
    Gerenciador centralizado do portfólio de criptomoedas
    """
    
    def __init__(self, config_path: str = "portfolio_config.json"):
        self.config_path = config_path
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> Dict:
        """Carrega configuração do arquivo JSON"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _salvar_config(self):
        """Salva configuração no arquivo JSON"""
        self.config['ultima_atualizacao'] = datetime.now().isoformat()
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def obter_criptos_ativas(self) -> List[Dict]:
        """Retorna lista de criptomoedas ativas"""
        return [c for c in self.config['criptomoedas'] if c.get('ativa', True)]
    
    def obter_cripto(self, name: str) -> Optional[Dict]:
        """Retorna dados de uma criptomoeda específica"""
        for cripto in self.config['criptomoedas']:
            if cripto['name'].lower() == name.lower():
                return cripto
        return None
    
    def adicionar_cripto(self, cripto: Dict, motivo: str = "") -> bool:
        """
        Adiciona nova criptomoeda ao portfólio
        
        Args:
            cripto: Dicionário com dados da cripto
            motivo: Motivo da adição
        
        Returns:
            True se adicionada com sucesso
        """
        # Verificar se já existe
        if self.obter_cripto(cripto['name']):
            print(f"⚠️ {cripto['name']} já existe no portfólio")
            return False
        
        # Verificar limite máximo
        max_criptos = self.config['configuracoes']['max_criptomoedas']
        if len(self.obter_criptos_ativas()) >= max_criptos:
            print(f"⚠️ Portfólio já atingiu o máximo de {max_criptos} criptomoedas")
            return False
        
        # Adicionar campos obrigatórios
        cripto['ativa'] = True
        cripto['data_adicao'] = datetime.now().isoformat()
        cripto['motivo_adicao'] = motivo
        
        # Adicionar ao portfólio
        self.config['criptomoedas'].append(cripto)
        
        # Registrar no histórico
        self._registrar_mudanca('adicao', f"Adicionada {cripto['name']}", 
                               criptos_adicionadas=[cripto['name']])
        
        self._salvar_config()
        print(f"✅ {cripto['name']} adicionada ao portfólio")
        return True
    
    def remover_cripto(self, name: str, motivo: str = "") -> bool:
        """
        Remove criptomoeda do portfólio (marca como inativa)
        
        Args:
            name: Nome da criptomoeda
            motivo: Motivo da remoção
        
        Returns:
            True se removida com sucesso
        """
        cripto = self.obter_cripto(name)
        if not cripto:
            print(f"⚠️ {name} não encontrada no portfólio")
            return False
        
        if not cripto.get('ativa', True):
            print(f"⚠️ {name} já está inativa")
            return False
        
        # Verificar limite mínimo
        min_criptos = self.config['configuracoes']['min_criptomoedas']
        if len(self.obter_criptos_ativas()) <= min_criptos:
            print(f"⚠️ Portfólio já está no mínimo de {min_criptos} criptomoedas")
            return False
        
        # Marcar como inativa
        cripto['ativa'] = False
        cripto['data_remocao'] = datetime.now().isoformat()
        cripto['motivo_remocao'] = motivo
        
        # Registrar no histórico
        self._registrar_mudanca('remocao', f"Removida {name}: {motivo}",
                               criptos_removidas=[name])
        
        self._salvar_config()
        print(f"✅ {name} removida do portfólio")
        return True
    
    def atualizar_periodo(self, name: str, novo_periodo: int, motivo: str = "") -> bool:
        """
        Atualiza período CHiLo de uma criptomoeda
        
        Args:
            name: Nome da criptomoeda
            novo_periodo: Novo período CHiLo
            motivo: Motivo da atualização
        
        Returns:
            True se atualizado com sucesso
        """
        cripto = self.obter_cripto(name)
        if not cripto:
            print(f"⚠️ {name} não encontrada no portfólio")
            return False
        
        periodo_antigo = cripto['period_chilo']
        if periodo_antigo == novo_periodo:
            print(f"⚠️ {name} já usa período {novo_periodo}")
            return False
        
        cripto['period_chilo'] = novo_periodo
        
        # Registrar no histórico
        self._registrar_mudanca('atualizacao_periodo',
                               f"{name}: período {periodo_antigo} → {novo_periodo}",
                               periodos_atualizados=[{
                                   'cripto': name,
                                   'periodo_antigo': periodo_antigo,
                                   'periodo_novo': novo_periodo,
                                   'motivo': motivo
                               }])
        
        self._salvar_config()
        print(f"✅ {name}: período atualizado para {novo_periodo}")
        return True
    
    def _registrar_mudanca(self, tipo: str, descricao: str, 
                          criptos_adicionadas: List[str] = None,
                          criptos_removidas: List[str] = None,
                          periodos_atualizados: List[Dict] = None):
        """Registra mudança no histórico"""
        mudanca = {
            'data': datetime.now().isoformat(),
            'tipo': tipo,
            'descricao': descricao,
            'criptos_adicionadas': criptos_adicionadas or [],
            'criptos_removidas': criptos_removidas or [],
            'periodos_atualizados': periodos_atualizados or []
        }
        
        self.config['historico_mudancas'].append(mudanca)
    
    def obter_historico(self, limit: int = 10) -> List[Dict]:
        """Retorna histórico de mudanças"""
        return self.config['historico_mudancas'][-limit:]
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do portfólio"""
        criptos_ativas = self.obter_criptos_ativas()
        
        return {
            'total_criptos': len(self.config['criptomoedas']),
            'criptos_ativas': len(criptos_ativas),
            'criptos_inativas': len(self.config['criptomoedas']) - len(criptos_ativas),
            'distribuicao_tier': self._contar_por_tier(criptos_ativas),
            'alocacao_total': sum(c.get('alocacao', 0) for c in criptos_ativas),
            'ultima_atualizacao': self.config['ultima_atualizacao'],
            'proxima_otimizacao': self.config.get('proxima_otimizacao', 'N/A')
        }
    
    def _contar_por_tier(self, criptos: List[Dict]) -> Dict:
        """Conta criptos por tier"""
        tiers = {}
        for cripto in criptos:
            tier = cripto.get('tier', 0)
            tiers[tier] = tiers.get(tier, 0) + 1
        return tiers
    
    def exportar_para_lista(self) -> List[Dict]:
        """
        Exporta criptos ativas no formato usado pelos scripts antigos
        Para compatibilidade com código legado
        """
        criptos_ativas = self.obter_criptos_ativas()
        return [{
            'name': c['name'],
            'symbol': c.get('symbol', ''),
            'yahoo': c['yahoo'],
            'period': c['period_chilo'],
            'emoji': c.get('emoji', '💎'),
            'tier': c.get('tier', 3),
            'alocacao': c.get('alocacao', 0.0)
        } for c in criptos_ativas]


def main():
    """Função principal para testes"""
    import sys
    
    manager = PortfolioManager()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'listar':
            print("=" * 80)
            print("CRIPTOMOEDAS ATIVAS")
            print("=" * 80)
            for cripto in manager.obter_criptos_ativas():
                print(f"{cripto['emoji']} {cripto['name']}")
                print(f"   Período CHiLo: {cripto['period_chilo']}")
                print(f"   Tier: {cripto['tier']} | Alocação: {cripto['alocacao']*100:.1f}%")
                print()
        
        elif comando == 'stats':
            print("=" * 80)
            print("ESTATÍSTICAS DO PORTFÓLIO")
            print("=" * 80)
            stats = manager.obter_estatisticas()
            for key, value in stats.items():
                print(f"{key}: {value}")
        
        elif comando == 'historico':
            print("=" * 80)
            print("HISTÓRICO DE MUDANÇAS")
            print("=" * 80)
            for mudanca in manager.obter_historico():
                print(f"{mudanca['data']}: {mudanca['descricao']}")
        
        else:
            print("Comandos: listar, stats, historico")
    else:
        # Mostrar resumo
        print("=" * 80)
        print("PORTFOLIO MANAGER - MAGNUS WEALTH v9.0.0")
        print("=" * 80)
        stats = manager.obter_estatisticas()
        print(f"\nCriptos ativas: {stats['criptos_ativas']}")
        print(f"Última atualização: {stats['ultima_atualizacao']}")
        print("\nUse: python3 portfolio_manager.py [listar|stats|historico]")


if __name__ == '__main__':
    main()
