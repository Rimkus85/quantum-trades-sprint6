#!/usr/bin/env python3
"""
Otimizador Quinzenal Magnus Wealth v9.0.0

Integrado com sistema dinâmico de portfólio:
1. Otimiza períodos CHiLo das criptos atuais
2. Avalia novas candidatas
3. Atualiza portfolio_config.json
4. Coleta dados de novas criptos
5. Treina modelos ML
6. Remove modelos de criptos excluídas
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from portfolio_manager import PortfolioManager
from typing import Dict, List

# Importar funções do otimizador original
sys.path.insert(0, os.path.dirname(__file__))
from otimizador_quinzenal import (
    otimizar_periodo,
    avaliar_candidata,
    formatar_relatorio,
    enviar_telegram_bot,
    CANDIDATAS
)

class OtimizadorQuinzenalV9:
    """
    Otimizador integrado com sistema dinâmico de portfólio
    """
    
    def __init__(self):
        self.portfolio = PortfolioManager()
        self.mudancas_realizadas = {
            'periodos_atualizados': [],
            'criptos_adicionadas': [],
            'criptos_removidas': []
        }
    
    def executar_otimizacao_completa(self):
        """
        Executa otimização completa do portfólio
        """
        print("=" * 80)
        print("OTIMIZAÇÃO QUINZENAL - MAGNUS WEALTH v9.0.0")
        print("=" * 80)
        print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Etapa 1: Otimizar períodos CHiLo
        print("\n📊 ETAPA 1: Otimização de Períodos CHiLo")
        print("=" * 80)
        otimizacoes = self._otimizar_periodos()
        
        # Etapa 2: Avaliar candidatas
        print("\n🔍 ETAPA 2: Avaliação de Novas Candidatas")
        print("=" * 80)
        candidatas_aprovadas = self._avaliar_candidatas()
        
        # Etapa 3: Decidir mudanças no portfólio
        print("\n⚖️  ETAPA 3: Decisão de Mudanças no Portfólio")
        print("=" * 80)
        self._decidir_mudancas(otimizacoes, candidatas_aprovadas)
        
        # Etapa 4: Aplicar mudanças
        print("\n🔄 ETAPA 4: Aplicando Mudanças")
        print("=" * 80)
        self._aplicar_mudancas()
        
        # Etapa 5: Atualizar ML
        print("\n🤖 ETAPA 5: Atualização de Modelos ML")
        print("=" * 80)
        self._atualizar_ml()
        
        # Etapa 6: Gerar relatório
        print("\n📄 ETAPA 6: Gerando Relatório")
        print("=" * 80)
        relatorio = self._gerar_relatorio(otimizacoes, candidatas_aprovadas)
        
        # Etapa 7: Enviar para Telegram
        print("\n📱 ETAPA 7: Enviando para Telegram")
        print("=" * 80)
        enviar_telegram_bot(relatorio)
        
        print("\n" + "=" * 80)
        print("✅ OTIMIZAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        
        return relatorio
    
    def _otimizar_periodos(self) -> List[Dict]:
        """
        Otimiza períodos CHiLo das criptos atuais
        """
        otimizacoes = []
        criptos_ativas = self.portfolio.obter_criptos_ativas()
        
        for cripto in criptos_ativas:
            # Converter para formato esperado pelo otimizador original
            cripto_formato = {
                'name': cripto['name'],
                'yahoo': cripto['yahoo'],
                'period': cripto['period_chilo'],
                'emoji': cripto.get('emoji', '💎')
            }
            
            resultado = otimizar_periodo(cripto_formato)
            if resultado:
                otimizacoes.append(resultado)
                
                # Se recomenda atualização, registrar
                if resultado.get('recomendar_atualizacao', False):
                    self.mudancas_realizadas['periodos_atualizados'].append({
                        'cripto': resultado['cripto'],
                        'periodo_antigo': resultado['periodo_atual'],
                        'periodo_novo': resultado['periodo_otimo'],
                        'melhoria_pct': resultado['melhoria_pct']
                    })
        
        print(f"\n✓ {len(otimizacoes)}/{len(criptos_ativas)} criptos otimizadas")
        print(f"✓ {len(self.mudancas_realizadas['periodos_atualizados'])} períodos com melhoria >5%")
        
        return otimizacoes
    
    def _avaliar_candidatas(self) -> List[Dict]:
        """
        Avalia criptomoedas candidatas
        """
        candidatas_aprovadas = []
        
        # Filtrar candidatas que já estão no portfólio
        criptos_atuais = [c['name'] for c in self.portfolio.obter_criptos_ativas()]
        candidatas_filtradas = [c for c in CANDIDATAS if c['name'] not in criptos_atuais]
        
        print(f"Avaliando {len(candidatas_filtradas)} candidatas...")
        
        for candidata in candidatas_filtradas:
            resultado = avaliar_candidata(candidata)
            if resultado:
                candidatas_aprovadas.append(resultado)
        
        # Ordenar por score
        candidatas_aprovadas.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n✓ {len(candidatas_aprovadas)} candidatas aprovadas")
        if candidatas_aprovadas:
            melhor = candidatas_aprovadas[0]
            print(f"✓ Melhor: {melhor['name']} (score: {melhor['score']:.1f})")
        
        return candidatas_aprovadas
    
    def _decidir_mudancas(self, otimizacoes: List[Dict], candidatas: List[Dict]):
        """
        Decide quais mudanças aplicar no portfólio
        """
        config = self.portfolio.config['configuracoes']
        criptos_ativas = self.portfolio.obter_criptos_ativas()
        
        # Decidir adições
        if candidatas and len(criptos_ativas) < config['max_criptomoedas']:
            melhor_candidata = candidatas[0]
            
            # Verificar se score é suficiente
            if melhor_candidata['score'] >= config['score_minimo_entrada']:
                self.mudancas_realizadas['criptos_adicionadas'].append(melhor_candidata)
                print(f"✓ Adicionar: {melhor_candidata['name']} (score: {melhor_candidata['score']:.1f})")
        
        # Decidir remoções (criptos com performance muito baixa)
        for cripto in criptos_ativas:
            # Encontrar otimização correspondente
            opt = next((o for o in otimizacoes if o['cripto'] == cripto['name']), None)
            
            if opt and opt['score_otimo'] < config['score_minimo_permanencia']:
                # Apenas remover se houver candidata melhor para substituir
                if candidatas and len(criptos_ativas) > config['min_criptomoedas']:
                    self.mudancas_realizadas['criptos_removidas'].append({
                        'name': cripto['name'],
                        'score': opt['score_otimo'],
                        'motivo': f"Score muito baixo ({opt['score_otimo']:.1f})"
                    })
                    print(f"✓ Remover: {cripto['name']} (score: {opt['score_otimo']:.1f})")
    
    def _aplicar_mudancas(self):
        """
        Aplica mudanças no portfolio_config.json
        """
        # Atualizar períodos
        for mudanca in self.mudancas_realizadas['periodos_atualizados']:
            self.portfolio.atualizar_periodo(
                mudanca['cripto'],
                mudanca['periodo_novo'],
                f"Otimização quinzenal: melhoria de {mudanca['melhoria_pct']:.1f}%"
            )
        
        # Remover criptos
        for mudanca in self.mudancas_realizadas['criptos_removidas']:
            self.portfolio.remover_cripto(
                mudanca['name'],
                mudanca['motivo']
            )
        
        # Adicionar criptos
        for candidata in self.mudancas_realizadas['criptos_adicionadas']:
            nova_cripto = {
                'name': candidata['name'],
                'yahoo': candidata['yahoo'],
                'period_chilo': candidata['periodo_otimo'],
                'emoji': candidata['emoji'],
                'tier': 3,  # Novas criptos começam no tier 3
                'alocacao': 0.05  # 5% inicial
            }
            self.portfolio.adicionar_cripto(
                nova_cripto,
                f"Otimização quinzenal: score {candidata['score']:.1f}"
            )
        
        print(f"\n✓ Mudanças aplicadas ao portfolio_config.json")
    
    def _atualizar_ml(self):
        """
        Atualiza modelos ML conforme mudanças no portfólio
        """
        # Se houve adições, coletar dados e treinar
        if self.mudancas_realizadas['criptos_adicionadas']:
            print("\n📊 Coletando dados de novas criptomoedas...")
            try:
                subprocess.run(['python3', 'coletor_dados_ml_8anos.py'], check=True)
                print("✓ Dados coletados")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao coletar dados: {e}")
            
            print("\n🤖 Treinando modelos ML...")
            try:
                subprocess.run(['python3', 'treinar_modelo_inversao.py'], check=True)
                print("✓ Modelos treinados")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao treinar modelos: {e}")
        
        # Se houve remoções, remover modelos
        if self.mudancas_realizadas['criptos_removidas']:
            print("\n🗑️  Removendo modelos de criptos excluídas...")
            for mudanca in self.mudancas_realizadas['criptos_removidas']:
                nome_arquivo = f"ml_models/{mudanca['name'].lower().replace(' ', '_')}_inversao.pkl"
                if os.path.exists(nome_arquivo):
                    os.remove(nome_arquivo)
                    print(f"✓ Removido: {nome_arquivo}")
        
        # Se houve atualizações de período, retreinar
        if self.mudancas_realizadas['periodos_atualizados']:
            print("\n🔄 Retreinando modelos com novos períodos...")
            try:
                subprocess.run(['python3', 'treinar_modelo_inversao.py'], check=True)
                print("✓ Modelos retreinados")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao retreinar modelos: {e}")
    
    def _gerar_relatorio(self, otimizacoes: List[Dict], candidatas: List[Dict]) -> str:
        """
        Gera relatório completo da otimização
        """
        # Usar função original para gerar relatório base
        relatorio = formatar_relatorio(otimizacoes, candidatas)
        
        # Adicionar seção de mudanças aplicadas
        if any(self.mudancas_realizadas.values()):
            relatorio += "\n\n═══════════════════════════════════\n"
            relatorio += "🔄 **MUDANÇAS APLICADAS**\n\n"
            
            if self.mudancas_realizadas['periodos_atualizados']:
                relatorio += f"**Períodos Atualizados:** {len(self.mudancas_realizadas['periodos_atualizados'])}\n"
                for m in self.mudancas_realizadas['periodos_atualizados']:
                    relatorio += f"   • {m['cripto']}: {m['periodo_antigo']} → {m['periodo_novo']} (+{m['melhoria_pct']:.1f}%)\n"
                relatorio += "\n"
            
            if self.mudancas_realizadas['criptos_adicionadas']:
                relatorio += f"**Criptos Adicionadas:** {len(self.mudancas_realizadas['criptos_adicionadas'])}\n"
                for c in self.mudancas_realizadas['criptos_adicionadas']:
                    relatorio += f"   • {c['emoji']} {c['name']} (score: {c['score']:.1f})\n"
                relatorio += "\n"
            
            if self.mudancas_realizadas['criptos_removidas']:
                relatorio += f"**Criptos Removidas:** {len(self.mudancas_realizadas['criptos_removidas'])}\n"
                for c in self.mudancas_realizadas['criptos_removidas']:
                    relatorio += f"   • {c['name']} ({c['motivo']})\n"
                relatorio += "\n"
            
            relatorio += "✅ **Modelos ML atualizados automaticamente**\n"
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"relatorio_otimizacao_v9_{timestamp}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(f"✓ Relatório salvo em: {filename}")
        
        return relatorio


def main():
    """
    Função principal
    """
    otimizador = OtimizadorQuinzenalV9()
    otimizador.executar_otimizacao_completa()


if __name__ == '__main__':
    main()
