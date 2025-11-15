#!/usr/bin/env python3
"""
Sistema Principal de Ordens Magnus Wealth v9.0.0

Orquestra todo o sistema:
- Monitor multi-timeframe
- Análise de critérios
- Execução de ordens
- Gerenciamento de stop loss
"""

from datetime import datetime
import time
from typing import Dict, List
from monitor_multitimeframe import MonitorMultiTimeframe
from analisador_criterios import AnalisadorCriterios
from executador_ordens import ExecutadorOrdens
from notificador_usuario import NotificadorUsuario
import json

class SistemaOrdensMagnus:
    """
    Sistema principal que orquestra todas as operações
    """
    
    def __init__(self):
        print("=" * 80)
        print("SISTEMA DE ORDENS MAGNUS WEALTH v9.0.0")
        print("=" * 80)
        
        self.monitor = MonitorMultiTimeframe()
        self.analisador = AnalisadorCriterios()
        self.executador = ExecutadorOrdens()
        self.notificador = NotificadorUsuario()
        
        print("\n✅ Todos os módulos inicializados")
    
    def verificar_e_executar_ordens(self):
        """
        Verifica critérios e executa ordens se necessário
        """
        print(f"\n{'='*80}")
        print(f"🔍 VERIFICAÇÃO DE ORDENS")
        print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Monitorar todas as criptos
        print("\n📊 Monitorando timeframes...")
        resultados_monitor = self.monitor.monitorar_todas()
        
        # Para cada cripto, verificar critérios
        for cripto, resultado_monitor in resultados_monitor.items():
            print(f"\n{'='*80}")
            print(f"🪙 {cripto}")
            print(f"{'='*80}")
            
            # Gerar features para ML
            features = self.monitor.gerar_features_ml(resultado_monitor)
            
            # Preço atual
            preco_atual = resultado_monitor['timeframes'].get('1d', {}).get('preco', 0)
            
            if preco_atual == 0:
                print(f"⚠️ Preço não disponível, pulando...")
                continue
            
            # Verificar se já há posição aberta
            posicoes = self.executador.obter_posicoes_abertas()
            tem_posicao = cripto in posicoes
            
            if tem_posicao:
                print(f"📍 Posição aberta: ${posicoes[cripto]['preco_entrada']:,.2f}")
                
                # Verificar stop loss
                if self.executador.verificar_stop_loss(cripto, preco_atual):
                    print(f"🚨 STOP LOSS ATINGIDO - Executando venda...")
                    
                    resultado = self.executador.executar_venda(
                        cripto=cripto,
                        preco=preco_atual,
                        motivo='CRITÉRIO 3: Stop Loss de 25%'
                    )
                    
                    if resultado['sucesso']:
                        print(f"✅ Venda executada com sucesso")
                    else:
                        print(f"❌ Erro na venda: {resultado.get('erro')}")
                    
                    continue
                
                # Verificar critérios para venda (inversão)
                # Aqui poderia verificar se houve inversão para vender
                print(f"✅ Stop loss OK, mantendo posição")
            
            else:
                print(f"📍 Sem posição aberta")
                
                # Analisar critérios para compra
                analise = self.analisador.analisar_cripto(cripto)
                
                if analise.get('executar_ordem', False):
                    print(f"\n✅ CRITÉRIOS SATISFEITOS - Executando compra...")
                    
                    # Determinar motivo
                    motivos = []
                    if analise['criterio_1']['satisfeito']:
                        motivos.append('CRITÉRIO 1: Inversão candle diário')
                    if analise['criterio_2']['satisfeito']:
                        motivos.append(f"CRITÉRIO 2: ML {analise['criterio_2']['probabilidade']:.0%}")
                    if analise['criterio_3']['satisfeito']:
                        motivos.append('CRITÉRIO 3: Stop Loss')
                    
                    motivo = ' | '.join(motivos)
                    
                    resultado = self.executador.executar_compra(
                        cripto=cripto,
                        preco=preco_atual,
                        motivo=motivo
                    )
                    
                    if resultado['sucesso']:
                        print(f"✅ Compra executada com sucesso")
                    else:
                        print(f"❌ Erro na compra: {resultado.get('erro')}")
                else:
                    print(f"⏳ Critérios não satisfeitos, aguardando...")
        
        # Resumo final
        print(f"\n{'='*80}")
        print(f"📊 RESUMO DA VERIFICAÇÃO")
        print(f"{'='*80}")
        
        posicoes = self.executador.obter_posicoes_abertas()
        print(f"\n📍 Posições abertas: {len(posicoes)}")
        for cripto, pos in posicoes.items():
            pl_atual = ((preco_atual - pos['preco_entrada']) / pos['preco_entrada']) * 100
            print(f"   {cripto}: ${pos['preco_entrada']:,.2f} ({pl_atual:+.2f}%)")
        
        perf = self.executador.calcular_performance()
        print(f"\n📈 Performance:")
        print(f"   Total de operações: {perf['total_operacoes']}")
        print(f"   Taxa de acerto: {perf['taxa_acerto']:.2f}%")
        print(f"   P&L médio: {perf['percentual_medio']:+.2f}%")
        print(f"   Lucro total: ${perf['lucro_total']:+,.2f}")
    
    def executar_verificacao_unica(self):
        """
        Executa uma verificação única (para testes)
        """
        try:
            self.verificar_e_executar_ordens()
            print(f"\n✅ Verificação concluída com sucesso")
        except Exception as e:
            print(f"\n❌ Erro na verificação: {e}")
            self.notificador.notificar_erro_usuario(
                erro=str(e),
                contexto="Verificação de ordens",
                traceback=""
            )
    
    def executar_loop_continuo(self, intervalo_minutos: int = 15):
        """
        Executa loop contínuo de verificação
        
        Args:
            intervalo_minutos: Intervalo entre verificações
        """
        print(f"\n🔄 Iniciando loop contínuo (intervalo: {intervalo_minutos} min)")
        print(f"⏸️  Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                self.verificar_e_executar_ordens()
                
                print(f"\n⏸️  Aguardando {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Loop interrompido pelo usuário")
        except Exception as e:
            print(f"\n\n❌ Erro no loop: {e}")
            self.notificador.notificar_erro_usuario(
                erro=str(e),
                contexto="Loop contínuo de ordens",
                traceback=""
            )


def criar_config_padrao():
    """
    Cria arquivo de configuração padrão
    """
    config = {
        'execucao_ativa': False,
        'modo_teste': True,
        'capital_inicial': 1000.0,
        'percentual_por_operacao': 0.10,
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
        'horario_verificacao_diario': '21:00:01',
        'intervalo_verificacao_minutos': 15
    }
    
    with open('config_ordens.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Arquivo config_ordens.json criado")
    print("\n⚠️  IMPORTANTE:")
    print("   - Modo TESTE ativado por padrão")
    print("   - Para ativar execução real, edite config_ordens.json:")
    print("     'execucao_ativa': true")
    print("     'modo_teste': false")


def main():
    """
    Função principal
    """
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == 'config':
            # Criar configuração padrão
            criar_config_padrao()
            return
        
        elif comando == 'verificar':
            # Verificação única
            sistema = SistemaOrdensMagnus()
            sistema.executar_verificacao_unica()
            return
        
        elif comando == 'loop':
            # Loop contínuo
            intervalo = int(sys.argv[2]) if len(sys.argv) > 2 else 15
            sistema = SistemaOrdensMagnus()
            sistema.executar_loop_continuo(intervalo)
            return
        
        elif comando == 'help':
            print("=" * 80)
            print("SISTEMA DE ORDENS MAGNUS WEALTH v9.0.0")
            print("=" * 80)
            print("\nComandos disponíveis:")
            print("  python3 sistema_ordens_magnus.py config")
            print("    → Cria arquivo de configuração padrão")
            print("\n  python3 sistema_ordens_magnus.py verificar")
            print("    → Executa uma verificação única")
            print("\n  python3 sistema_ordens_magnus.py loop [intervalo_minutos]")
            print("    → Executa loop contínuo (padrão: 15 min)")
            print("\n  python3 sistema_ordens_magnus.py help")
            print("    → Mostra esta ajuda")
            print("\n" + "=" * 80)
            return
    
    # Padrão: verificação única
    sistema = SistemaOrdensMagnus()
    sistema.executar_verificacao_unica()


if __name__ == '__main__':
    main()
