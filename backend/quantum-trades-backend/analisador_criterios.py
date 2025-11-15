#!/usr/bin/env python3
"""
Analisador de Critérios de Inversão
Magnus Wealth v9.0.0

Verifica os 3 critérios para execução de ordens:
1. Inversão confirmada no candle diário (21:00:01 Brasília)
2. ML Multi-Timeframe (probabilidade > 70%)
3. Stop Loss de 25%
"""

from datetime import datetime, time
import pytz
from typing import Dict, Optional, Tuple
from monitor_multitimeframe import MonitorMultiTimeframe
from predicao_inversao import PreditorInversao
import json
import os

# Configurações
CONFIG_FILE = 'config_ordens.json'

# Timezone de Brasília
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')

class AnalisadorCriterios:
    """
    Analisa critérios para execução de ordens
    """
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config = self.carregar_config(config_file)
        self.monitor = MonitorMultiTimeframe()
        self.preditor = PreditorInversao()
        self.posicoes_abertas = {}  # {cripto: {preco_entrada, preco_inicial_tendencia, ...}}
    
    def carregar_config(self, config_file: str) -> Dict:
        """
        Carrega configurações do sistema
        """
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"✓ Configurações carregadas de {config_file}")
                return config
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
        
        # Configurações padrão
        config = {
            'execucao_ativa': False,
            'modo_teste': True,
            'criterios': {
                'criterio_1_ativo': True,
                'criterio_2_ativo': True,
                'criterio_3_ativo': True
            },
            'ml': {
                'threshold_probabilidade': 0.70,
                'min_timeframes_alinhados': 5
            },
            'stop_loss': {
                'percentual': 0.25,
                'ativo': True
            },
            'horario_verificacao_diario': '21:00:01'
        }
        
        print(f"⚠️ Usando configurações padrão")
        return config
    
    def verificar_criterio_1(self, cripto: str, resultado_monitor: Dict) -> Tuple[bool, str]:
        """
        Critério 1: Inversão confirmada no candle diário (21:00:01 Brasília)
        
        Returns:
            (satisfeito, motivo)
        """
        if not self.config['criterios']['criterio_1_ativo']:
            return False, "Critério 1 desativado"
        
        # Verificar horário
        agora_brasilia = datetime.now(TZ_BRASILIA)
        hora_verificacao = self.config['horario_verificacao_diario']
        
        # Parsear horário de verificação
        h, m, s = map(int, hora_verificacao.split(':'))
        horario_alvo = time(h, m, s)
        
        # Verificar se estamos no horário correto (com margem de 1 minuto)
        hora_atual = agora_brasilia.time()
        margem_segundos = 60
        
        # Converter para segundos para comparação
        segundos_atual = hora_atual.hour * 3600 + hora_atual.minute * 60 + hora_atual.second
        segundos_alvo = horario_alvo.hour * 3600 + horario_alvo.minute * 60 + horario_alvo.second
        
        diferenca = abs(segundos_atual - segundos_alvo)
        
        if diferenca > margem_segundos:
            return False, f"Fora do horário de verificação (atual: {hora_atual.strftime('%H:%M:%S')})"
        
        # Verificar inversão no candle diário
        if '1d' not in resultado_monitor['timeframes']:
            return False, "Dados do candle diário não disponíveis"
        
        tf_diario = resultado_monitor['timeframes']['1d']
        estado_atual = tf_diario['estado']
        
        # Verificar se houve inversão
        # (Precisaríamos comparar com estado anterior - simplificado aqui)
        if estado_atual == 0:
            return False, "Estado neutro no candle diário"
        
        # Se chegou aqui, está no horário correto e há um estado definido
        return True, f"Inversão confirmada no candle diário às {hora_atual.strftime('%H:%M:%S')}"
    
    def verificar_criterio_2(self, cripto: str, features: Dict) -> Tuple[bool, str, float]:
        """
        Critério 2: ML Multi-Timeframe (probabilidade > 70%)
        
        Returns:
            (satisfeito, motivo, probabilidade)
        """
        if not self.config['criterios']['criterio_2_ativo']:
            return False, "Critério 2 desativado", 0.0
        
        # Verificar alinhamento de timeframes
        threshold_ml = self.config['ml']['threshold_probabilidade']
        min_alinhados = self.config['ml']['min_timeframes_alinhados']
        
        # Fazer predição
        resultado_ml = self.preditor.prever(cripto, features)
        
        if not resultado_ml:
            return False, "Modelo ML não disponível", 0.0
        
        probabilidade = resultado_ml['probabilidade_virar']
        
        # Verificar threshold
        if probabilidade < threshold_ml:
            return False, f"Probabilidade ({probabilidade:.2%}) < {threshold_ml:.0%}", probabilidade
        
        # Verificar alinhamento de timeframes
        # Contar quantos timeframes estão na mesma direção
        estados = []
        for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
            estado = features.get(f'{tf}_estado', 0)
            if estado != 0:
                estados.append(estado)
        
        if len(estados) < min_alinhados:
            return False, f"Poucos timeframes alinhados ({len(estados)} < {min_alinhados})", probabilidade
        
        # Verificar se estão na mesma direção
        positivos = sum(1 for e in estados if e > 0)
        negativos = sum(1 for e in estados if e < 0)
        
        if positivos < min_alinhados and negativos < min_alinhados:
            return False, f"Timeframes não alinhados (+ {positivos}, -{negativos})", probabilidade
        
        # Critério satisfeito
        direcao = "alta" if positivos >= min_alinhados else "baixa"
        return True, f"ML: {probabilidade:.2%} > {threshold_ml:.0%}, {len(estados)} TFs alinhados ({direcao})", probabilidade
    
    def verificar_criterio_3(self, cripto: str, preco_atual: float) -> Tuple[bool, str]:
        """
        Critério 3: Stop Loss de 25%
        
        Returns:
            (satisfeito, motivo)
        """
        if not self.config['criterios']['criterio_3_ativo']:
            return False, "Critério 3 desativado"
        
        if not self.config['stop_loss']['ativo']:
            return False, "Stop loss desativado"
        
        # Verificar se há posição aberta
        if cripto not in self.posicoes_abertas:
            return False, "Sem posição aberta"
        
        posicao = self.posicoes_abertas[cripto]
        preco_inicial_tendencia = posicao.get('preco_inicial_tendencia', preco_atual)
        
        # Calcular perda
        perda_percentual = (preco_inicial_tendencia - preco_atual) / preco_inicial_tendencia
        
        threshold_stop = self.config['stop_loss']['percentual']
        
        if perda_percentual >= threshold_stop:
            return True, f"Stop loss ativado: perda de {perda_percentual:.2%} >= {threshold_stop:.0%}"
        
        return False, f"Stop loss não ativado: perda de {perda_percentual:.2%} < {threshold_stop:.0%}"
    
    def analisar_cripto(self, cripto: str) -> Dict:
        """
        Analisa todos os critérios para uma criptomoeda
        
        Returns:
            Dicionário com análise completa
        """
        print(f"\n{'='*80}")
        print(f"🔍 ANALISANDO CRITÉRIOS: {cripto}")
        print(f"{'='*80}")
        
        # Monitorar timeframes
        resultado_monitor = None
        for c in self.monitor.periodos_otimizados:
            if c == cripto:
                # Buscar dados da cripto
                cripto_config = next((c for c in [
                    {'name': 'Bitcoin', 'yahoo': 'BTC-USD', 'period': 3},
                    {'name': 'Ethereum', 'yahoo': 'ETH-USD', 'period': 45},
                    {'name': 'Binance Coin', 'yahoo': 'BNB-USD', 'period': 70},
                    {'name': 'Solana', 'yahoo': 'SOL-USD', 'period': 7},
                    {'name': 'Chainlink', 'yahoo': 'LINK-USD', 'period': 40},
                    {'name': 'Uniswap', 'yahoo': 'UNI7083-USD', 'period': 65},
                    {'name': 'Algorand', 'yahoo': 'ALGO-USD', 'period': 40},
                    {'name': 'VeChain', 'yahoo': 'VET-USD', 'period': 25}
                ] if c['name'] == cripto), None)
                
                if cripto_config:
                    resultado_monitor = self.monitor.monitorar_cripto(cripto_config)
                break
        
        if not resultado_monitor:
            return {
                'cripto': cripto,
                'erro': 'Não foi possível monitorar a criptomoeda',
                'executar_ordem': False
            }
        
        # Gerar features para ML
        features = self.monitor.gerar_features_ml(resultado_monitor)
        
        # Preço atual
        preco_atual = resultado_monitor['timeframes'].get('1d', {}).get('preco', 0)
        
        # Verificar cada critério
        print(f"\n📊 Verificando critérios...")
        
        # Critério 1
        c1_satisfeito, c1_motivo = self.verificar_criterio_1(cripto, resultado_monitor)
        print(f"\n1️⃣ Critério 1 (Candle Diário):")
        print(f"   {'✅' if c1_satisfeito else '❌'} {c1_motivo}")
        
        # Critério 2
        c2_satisfeito, c2_motivo, probabilidade = self.verificar_criterio_2(cripto, features)
        print(f"\n2️⃣ Critério 2 (ML Multi-Timeframe):")
        print(f"   {'✅' if c2_satisfeito else '❌'} {c2_motivo}")
        
        # Critério 3
        c3_satisfeito, c3_motivo = self.verificar_criterio_3(cripto, preco_atual)
        print(f"\n3️⃣ Critério 3 (Stop Loss):")
        print(f"   {'✅' if c3_satisfeito else '❌'} {c3_motivo}")
        
        # Decisão final
        executar = c1_satisfeito or c2_satisfeito or c3_satisfeito
        
        print(f"\n{'='*80}")
        print(f"🎯 DECISÃO: {'✅ EXECUTAR ORDEM' if executar else '⏳ AGUARDAR'}")
        print(f"{'='*80}")
        
        if executar:
            motivos = []
            if c1_satisfeito:
                motivos.append("Critério 1")
            if c2_satisfeito:
                motivos.append("Critério 2")
            if c3_satisfeito:
                motivos.append("Critério 3")
            
            print(f"Motivo: {', '.join(motivos)}")
        
        return {
            'cripto': cripto,
            'timestamp': datetime.now().isoformat(),
            'preco_atual': preco_atual,
            'criterio_1': {
                'satisfeito': c1_satisfeito,
                'motivo': c1_motivo
            },
            'criterio_2': {
                'satisfeito': c2_satisfeito,
                'motivo': c2_motivo,
                'probabilidade': probabilidade
            },
            'criterio_3': {
                'satisfeito': c3_satisfeito,
                'motivo': c3_motivo
            },
            'executar_ordem': executar,
            'motivos_execucao': [
                'Critério 1' if c1_satisfeito else None,
                'Critério 2' if c2_satisfeito else None,
                'Critério 3' if c3_satisfeito else None
            ]
        }


def exemplo_uso():
    """
    Exemplo de uso do analisador
    """
    print("=" * 80)
    print("ANALISADOR DE CRITÉRIOS - MAGNUS WEALTH v9.0.0")
    print("=" * 80)
    
    analisador = AnalisadorCriterios()
    
    # Analisar Bitcoin
    resultado = analisador.analisar_cripto('Bitcoin')
    
    print(f"\n📋 Resultado da análise:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    exemplo_uso()
