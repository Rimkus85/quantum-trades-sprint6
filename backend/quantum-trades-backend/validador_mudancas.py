"""
Sistema de Validação de Mudanças - Magnus Wealth v8.3.0
Valida e aprova/rejeita mudanças de períodos CHiLo automaticamente
"""

from typing import Dict, List, Tuple
from datetime import datetime
import json
import os

# Critérios de validação automática
CRITERIOS = {
    # Melhoria mínima para aprovação automática
    'melhoria_minima': 5.0,  # 5% de melhoria no score
    
    # Retorno líquido mínimo
    'retorno_liquido_minimo': -10.0,  # -10% (não pode ser pior que isso)
    
    # Custo anual máximo
    'custo_anual_maximo': 5.0,  # 5% ao ano
    
    # Número máximo de trades por ano
    'trades_ano_maximo': 100,  # ~2 trades por semana
    
    # Sharpe mínimo
    'sharpe_minimo': -1.0,  # Não pode ser muito negativo
    
    # Taxa de acerto mínima
    'taxa_acerto_minima': 30.0,  # 30% (melhor que aleatório)
    
    # Diferença máxima de período
    'diferenca_periodo_maxima': 50,  # Não mudar mais que 50 períodos de uma vez
}

class ValidadorMudancas:
    """Valida mudanças de períodos CHiLo"""
    
    def __init__(self):
        self.historico_file = '/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/historico_mudancas.json'
        self.historico = self._carregar_historico()
    
    def _carregar_historico(self) -> List[Dict]:
        """Carrega histórico de mudanças"""
        if os.path.exists(self.historico_file):
            with open(self.historico_file, 'r') as f:
                return json.load(f)
        return []
    
    def _salvar_historico(self):
        """Salva histórico de mudanças"""
        with open(self.historico_file, 'w') as f:
            json.dump(self.historico, f, indent=2)
    
    def validar_mudanca(self, otimizacao: Dict) -> Tuple[str, str, List[str]]:
        """
        Valida uma mudança proposta
        
        Retorna:
        - status: 'APROVADO_AUTO', 'APROVADO_MANUAL', 'REJEITADO', 'REQUER_ANALISE'
        - motivo: Explicação da decisão
        - alertas: Lista de alertas/avisos
        """
        cripto = otimizacao['cripto']
        periodo_atual = otimizacao['periodo_atual']
        periodo_novo = otimizacao['periodo_otimo']
        melhoria = otimizacao['melhoria_pct']
        metricas = otimizacao['metricas_otimo']
        
        alertas = []
        motivos_rejeicao = []
        motivos_analise = []
        
        # 1. Verificar melhoria mínima
        if melhoria < CRITERIOS['melhoria_minima']:
            motivos_rejeicao.append(f"Melhoria insuficiente ({melhoria:.1f}% < {CRITERIOS['melhoria_minima']}%)")
        
        # 2. Verificar retorno líquido
        if metricas['retorno_liquido'] < CRITERIOS['retorno_liquido_minimo']:
            motivos_rejeicao.append(f"Retorno líquido muito negativo ({metricas['retorno_liquido']:.1f}%)")
        
        # 3. Verificar custo anual
        if metricas['custo_anual'] > CRITERIOS['custo_anual_maximo']:
            alertas.append(f"⚠️ Custo anual elevado: {metricas['custo_anual']:.2f}% (máx: {CRITERIOS['custo_anual_maximo']}%)")
            motivos_analise.append("Custo anual acima do limite")
        
        # 4. Verificar número de trades
        trades_ano = metricas['num_trades'] * (365 / 90)  # Estimar anual baseado em 90 dias
        if trades_ano > CRITERIOS['trades_ano_maximo']:
            alertas.append(f"⚠️ Muitos trades: {trades_ano:.0f}/ano (máx: {CRITERIOS['trades_ano_maximo']})")
            motivos_analise.append("Número de trades excessivo")
        
        # 5. Verificar Sharpe
        if metricas['sharpe'] < CRITERIOS['sharpe_minimo']:
            alertas.append(f"⚠️ Sharpe muito negativo: {metricas['sharpe']:.2f}")
            motivos_analise.append("Sharpe ratio muito baixo")
        
        # 6. Verificar taxa de acerto
        if metricas['taxa_acerto'] < CRITERIOS['taxa_acerto_minima']:
            alertas.append(f"⚠️ Taxa de acerto baixa: {metricas['taxa_acerto']:.1f}%")
            motivos_analise.append("Taxa de acerto abaixo do mínimo")
        
        # 7. Verificar mudança drástica de período
        diferenca_periodo = abs(periodo_novo - periodo_atual)
        if diferenca_periodo > CRITERIOS['diferenca_periodo_maxima']:
            alertas.append(f"⚠️ Mudança drástica: {periodo_atual} → {periodo_novo} ({diferenca_periodo} períodos)")
            motivos_analise.append("Mudança de período muito grande")
        
        # 8. Verificar se retorno líquido é positivo
        if metricas['retorno_liquido'] > 0:
            alertas.append(f"✅ Retorno líquido positivo: {metricas['retorno_liquido']:.1f}%")
        
        # Decisão final
        if motivos_rejeicao:
            status = 'REJEITADO'
            motivo = ' | '.join(motivos_rejeicao)
        elif motivos_analise:
            status = 'REQUER_ANALISE'
            motivo = ' | '.join(motivos_analise)
        elif melhoria >= CRITERIOS['melhoria_minima'] * 2:  # Melhoria > 10%
            status = 'APROVADO_AUTO'
            motivo = f"Melhoria significativa ({melhoria:.1f}%) e métricas adequadas"
        else:
            status = 'APROVADO_MANUAL'
            motivo = f"Melhoria moderada ({melhoria:.1f}%), requer confirmação"
        
        return status, motivo, alertas
    
    def processar_otimizacoes(self, otimizacoes: List[Dict]) -> Dict:
        """
        Processa lista de otimizações e retorna recomendações
        
        Retorna:
        - aprovadas_auto: Lista de mudanças aprovadas automaticamente
        - requer_analise: Lista de mudanças que requerem análise manual
        - rejeitadas: Lista de mudanças rejeitadas
        """
        aprovadas_auto = []
        requer_analise = []
        rejeitadas = []
        
        for opt in otimizacoes:
            if not opt or not opt.get('recomendar_atualizacao'):
                continue
            
            status, motivo, alertas = self.validar_mudanca(opt)
            
            resultado = {
                'cripto': opt['cripto'],
                'emoji': opt['emoji'],
                'periodo_atual': opt['periodo_atual'],
                'periodo_novo': opt['periodo_otimo'],
                'melhoria': opt['melhoria_pct'],
                'metricas': opt['metricas_otimo'],
                'status': status,
                'motivo': motivo,
                'alertas': alertas
            }
            
            if status == 'APROVADO_AUTO':
                aprovadas_auto.append(resultado)
            elif status == 'REQUER_ANALISE':
                requer_analise.append(resultado)
            else:  # REJEITADO
                rejeitadas.append(resultado)
        
        return {
            'aprovadas_auto': aprovadas_auto,
            'requer_analise': requer_analise,
            'rejeitadas': rejeitadas
        }
    
    def registrar_mudanca(self, cripto: str, periodo_anterior: int, periodo_novo: int, 
                         motivo: str, aprovado: bool):
        """Registra mudança no histórico"""
        registro = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cripto': cripto,
            'periodo_anterior': periodo_anterior,
            'periodo_novo': periodo_novo,
            'motivo': motivo,
            'aprovado': aprovado
        }
        
        self.historico.append(registro)
        self._salvar_historico()
    
    def gerar_relatorio(self, resultados: Dict) -> str:
        """Gera relatório de validação"""
        msg = "\n" + "="*60 + "\n"
        msg += "🔍 RELATÓRIO DE VALIDAÇÃO DE MUDANÇAS\n"
        msg += "="*60 + "\n\n"
        
        # Aprovadas automaticamente
        if resultados['aprovadas_auto']:
            msg += "✅ **APROVADAS AUTOMATICAMENTE** (Aplicar sem confirmação)\n\n"
            for r in resultados['aprovadas_auto']:
                msg += f"{r['emoji']} **{r['cripto']}**: {r['periodo_atual']} → {r['periodo_novo']}\n"
                msg += f"   Melhoria: {r['melhoria']:+.1f}%\n"
                msg += f"   Motivo: {r['motivo']}\n"
                for alerta in r['alertas']:
                    msg += f"   {alerta}\n"
                msg += "\n"
        
        # Requer análise
        if resultados['requer_analise']:
            msg += "⚠️ **REQUER ANÁLISE MANUAL** (Revisar antes de aplicar)\n\n"
            for r in resultados['requer_analise']:
                msg += f"{r['emoji']} **{r['cripto']}**: {r['periodo_atual']} → {r['periodo_novo']}\n"
                msg += f"   Melhoria: {r['melhoria']:+.1f}%\n"
                msg += f"   Motivo: {r['motivo']}\n"
                msg += f"   Métricas:\n"
                msg += f"      - Retorno líquido: {r['metricas']['retorno_liquido']:+.1f}%\n"
                msg += f"      - Sharpe: {r['metricas']['sharpe']:.2f}\n"
                msg += f"      - Taxa acerto: {r['metricas']['taxa_acerto']:.1f}%\n"
                msg += f"      - Trades: {r['metricas']['num_trades']} ({r['metricas']['custo_anual']:.2f}% anual)\n"
                for alerta in r['alertas']:
                    msg += f"   {alerta}\n"
                msg += "\n"
        
        # Rejeitadas
        if resultados['rejeitadas']:
            msg += "❌ **REJEITADAS** (Não aplicar)\n\n"
            for r in resultados['rejeitadas']:
                msg += f"{r['emoji']} **{r['cripto']}**: {r['periodo_atual']} → {r['periodo_novo']}\n"
                msg += f"   Melhoria: {r['melhoria']:+.1f}%\n"
                msg += f"   Motivo da rejeição: {r['motivo']}\n"
                for alerta in r['alertas']:
                    msg += f"   {alerta}\n"
                msg += "\n"
        
        # Resumo
        msg += "="*60 + "\n"
        msg += "📊 **RESUMO**\n\n"
        msg += f"   ✅ Aprovadas automaticamente: {len(resultados['aprovadas_auto'])}\n"
        msg += f"   ⚠️ Requerem análise: {len(resultados['requer_analise'])}\n"
        msg += f"   ❌ Rejeitadas: {len(resultados['rejeitadas'])}\n"
        msg += "="*60 + "\n"
        
        return msg

if __name__ == "__main__":
    # Teste do validador
    validador = ValidadorMudancas()
    
    # Exemplo de otimização
    opt_teste = {
        'cripto': 'Bitcoin',
        'emoji': '🥇',
        'periodo_atual': 40,
        'periodo_otimo': 3,
        'melhoria_pct': 124.0,
        'recomendar_atualizacao': True,
        'metricas_otimo': {
            'taxa_acerto': 75.0,
            'sharpe': 0.5,
            'retorno': 12.0,
            'retorno_liquido': 11.5,
            'num_trades': 15,
            'custo_total': 0.75,
            'custo_anual': 3.0
        }
    }
    
    status, motivo, alertas = validador.validar_mudanca(opt_teste)
    print(f"Status: {status}")
    print(f"Motivo: {motivo}")
    print(f"Alertas: {alertas}")
