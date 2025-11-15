#!/usr/bin/env python3
"""
Executador de Ordens e Gerenciador de Stop Loss
Magnus Wealth v9.0.0

Executa ordens de compra/venda e gerencia stop loss
"""

from datetime import datetime
from typing import Dict, Optional
import json
import os
from notificador_usuario import NotificadorUsuario

# Arquivos de dados
POSICOES_FILE = 'posicoes_abertas.json'
HISTORICO_FILE = 'historico_ordens.json'
CONFIG_FILE = 'config_ordens.json'

class ExecutadorOrdens:
    """
    Executa ordens e gerencia posições
    """
    
    def __init__(self):
        self.config = self.carregar_config()
        self.posicoes = self.carregar_posicoes()
        self.historico = self.carregar_historico()
        self.notificador = NotificadorUsuario()
    
    def carregar_config(self) -> Dict:
        """Carrega configurações"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        
        return {
            'execucao_ativa': False,
            'modo_teste': True,
            'capital_inicial': 1000.0,
            'percentual_por_operacao': 0.10,  # 10% do capital por operação
            'stop_loss': {
                'percentual': 0.25,
                'ativo': True
            }
        }
    
    def carregar_posicoes(self) -> Dict:
        """Carrega posições abertas"""
        if os.path.exists(POSICOES_FILE):
            with open(POSICOES_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def salvar_posicoes(self):
        """Salva posições abertas"""
        with open(POSICOES_FILE, 'w') as f:
            json.dump(self.posicoes, f, indent=2)
    
    def carregar_historico(self) -> list:
        """Carrega histórico de ordens"""
        if os.path.exists(HISTORICO_FILE):
            with open(HISTORICO_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def salvar_historico(self):
        """Salva histórico de ordens"""
        with open(HISTORICO_FILE, 'w') as f:
            json.dump(self.historico, f, indent=2)
    
    def calcular_quantidade(self, preco: float) -> float:
        """
        Calcula quantidade a comprar baseado no capital disponível
        """
        capital_operacao = self.config['capital_inicial'] * self.config['percentual_por_operacao']
        quantidade = capital_operacao / preco
        return quantidade
    
    def executar_compra(self, cripto: str, preco: float, motivo: str) -> Dict:
        """
        Executa ordem de COMPRA
        
        Args:
            cripto: Nome da criptomoeda
            preco: Preço de compra
            motivo: Motivo da compra (qual critério)
        
        Returns:
            Dicionário com resultado da ordem
        """
        timestamp = datetime.now().isoformat()
        
        # Verificar se já há posição aberta
        if cripto in self.posicoes:
            return {
                'sucesso': False,
                'erro': 'Já existe posição aberta para esta cripto',
                'cripto': cripto
            }
        
        # Calcular quantidade
        quantidade = self.calcular_quantidade(preco)
        valor_total = quantidade * preco
        
        # Modo teste ou produção
        if self.config['modo_teste']:
            print(f"\n🧪 MODO TESTE - Ordem NÃO executada na exchange")
        else:
            print(f"\n💰 MODO PRODUÇÃO - Executando ordem na exchange...")
            # Aqui entraria a integração com a API da exchange (Binance, etc)
            # Por enquanto, apenas simulação
        
        # Registrar posição
        self.posicoes[cripto] = {
            'tipo': 'COMPRA',
            'preco_entrada': preco,
            'quantidade': quantidade,
            'valor_total': valor_total,
            'timestamp_entrada': timestamp,
            'motivo': motivo,
            'preco_inicial_tendencia': preco,  # Para cálculo de stop loss
            'stop_loss_ativo': self.config['stop_loss']['ativo'],
            'stop_loss_percentual': self.config['stop_loss']['percentual']
        }
        
        self.salvar_posicoes()
        
        # Registrar no histórico
        ordem = {
            'id': len(self.historico) + 1,
            'cripto': cripto,
            'tipo': 'COMPRA',
            'preco': preco,
            'quantidade': quantidade,
            'valor_total': valor_total,
            'timestamp': timestamp,
            'motivo': motivo,
            'modo': 'TESTE' if self.config['modo_teste'] else 'PRODUÇÃO'
        }
        
        self.historico.append(ordem)
        self.salvar_historico()
        
        # Notificar usuário
        self.notificador.notificar_ordem_executada(
            cripto=cripto,
            tipo='COMPRA',
            quantidade=quantidade,
            preco=preco,
            motivo=motivo
        )
        
        print(f"\n✅ ORDEM DE COMPRA EXECUTADA")
        print(f"   Cripto: {cripto}")
        print(f"   Preço: ${preco:,.2f}")
        print(f"   Quantidade: {quantidade:.8f}")
        print(f"   Total: ${valor_total:,.2f}")
        print(f"   Motivo: {motivo}")
        
        return {
            'sucesso': True,
            'ordem': ordem,
            'posicao': self.posicoes[cripto]
        }
    
    def executar_venda(self, cripto: str, preco: float, motivo: str) -> Dict:
        """
        Executa ordem de VENDA
        
        Args:
            cripto: Nome da criptomoeda
            preco: Preço de venda
            motivo: Motivo da venda (qual critério)
        
        Returns:
            Dicionário com resultado da ordem
        """
        timestamp = datetime.now().isoformat()
        
        # Verificar se há posição aberta
        if cripto not in self.posicoes:
            return {
                'sucesso': False,
                'erro': 'Não há posição aberta para esta cripto',
                'cripto': cripto
            }
        
        posicao = self.posicoes[cripto]
        quantidade = posicao['quantidade']
        preco_entrada = posicao['preco_entrada']
        valor_total = quantidade * preco
        
        # Calcular P&L
        lucro_prejuizo = valor_total - posicao['valor_total']
        percentual_pl = (lucro_prejuizo / posicao['valor_total']) * 100
        
        # Modo teste ou produção
        if self.config['modo_teste']:
            print(f"\n🧪 MODO TESTE - Ordem NÃO executada na exchange")
        else:
            print(f"\n💰 MODO PRODUÇÃO - Executando ordem na exchange...")
            # Aqui entraria a integração com a API da exchange
        
        # Remover posição
        del self.posicoes[cripto]
        self.salvar_posicoes()
        
        # Registrar no histórico
        ordem = {
            'id': len(self.historico) + 1,
            'cripto': cripto,
            'tipo': 'VENDA',
            'preco': preco,
            'quantidade': quantidade,
            'valor_total': valor_total,
            'timestamp': timestamp,
            'motivo': motivo,
            'preco_entrada': preco_entrada,
            'lucro_prejuizo': lucro_prejuizo,
            'percentual_pl': percentual_pl,
            'modo': 'TESTE' if self.config['modo_teste'] else 'PRODUÇÃO'
        }
        
        self.historico.append(ordem)
        self.salvar_historico()
        
        # Notificar usuário
        self.notificador.notificar_ordem_executada(
            cripto=cripto,
            tipo='VENDA',
            quantidade=quantidade,
            preco=preco,
            motivo=f"{motivo} | P&L: {percentual_pl:+.2f}%"
        )
        
        emoji_pl = "📈" if lucro_prejuizo > 0 else "📉"
        print(f"\n✅ ORDEM DE VENDA EXECUTADA")
        print(f"   Cripto: {cripto}")
        print(f"   Preço: ${preco:,.2f}")
        print(f"   Quantidade: {quantidade:.8f}")
        print(f"   Total: ${valor_total:,.2f}")
        print(f"   Motivo: {motivo}")
        print(f"   {emoji_pl} P&L: ${lucro_prejuizo:+,.2f} ({percentual_pl:+.2f}%)")
        
        return {
            'sucesso': True,
            'ordem': ordem,
            'lucro_prejuizo': lucro_prejuizo,
            'percentual_pl': percentual_pl
        }
    
    def verificar_stop_loss(self, cripto: str, preco_atual: float) -> bool:
        """
        Verifica se stop loss foi atingido
        
        Args:
            cripto: Nome da criptomoeda
            preco_atual: Preço atual
        
        Returns:
            True se stop loss atingido
        """
        if cripto not in self.posicoes:
            return False
        
        posicao = self.posicoes[cripto]
        
        if not posicao.get('stop_loss_ativo', False):
            return False
        
        preco_inicial = posicao['preco_inicial_tendencia']
        threshold = posicao['stop_loss_percentual']
        
        # Calcular perda
        perda_percentual = (preco_inicial - preco_atual) / preco_inicial
        
        if perda_percentual >= threshold:
            print(f"\n🚨 STOP LOSS ATINGIDO: {cripto}")
            print(f"   Perda: {perda_percentual:.2%} >= {threshold:.0%}")
            return True
        
        return False
    
    def atualizar_preco_inicial_tendencia(self, cripto: str, novo_preco: float):
        """
        Atualiza preço inicial da tendência (para trailing stop)
        """
        if cripto in self.posicoes:
            self.posicoes[cripto]['preco_inicial_tendencia'] = novo_preco
            self.salvar_posicoes()
    
    def obter_posicoes_abertas(self) -> Dict:
        """Retorna posições abertas"""
        return self.posicoes
    
    def obter_historico(self, limite: int = 10) -> list:
        """Retorna histórico de ordens"""
        return self.historico[-limite:]
    
    def calcular_performance(self) -> Dict:
        """
        Calcula performance geral do sistema
        """
        if not self.historico:
            return {
                'total_operacoes': 0,
                'lucro_total': 0,
                'percentual_medio': 0,
                'taxa_acerto': 0
            }
        
        vendas = [o for o in self.historico if o['tipo'] == 'VENDA']
        
        if not vendas:
            return {
                'total_operacoes': len(self.historico),
                'lucro_total': 0,
                'percentual_medio': 0,
                'taxa_acerto': 0
            }
        
        lucro_total = sum(v.get('lucro_prejuizo', 0) for v in vendas)
        percentual_medio = sum(v.get('percentual_pl', 0) for v in vendas) / len(vendas)
        operacoes_positivas = sum(1 for v in vendas if v.get('lucro_prejuizo', 0) > 0)
        taxa_acerto = (operacoes_positivas / len(vendas)) * 100
        
        return {
            'total_operacoes': len(self.historico),
            'total_vendas': len(vendas),
            'lucro_total': lucro_total,
            'percentual_medio': percentual_medio,
            'taxa_acerto': taxa_acerto,
            'operacoes_positivas': operacoes_positivas,
            'operacoes_negativas': len(vendas) - operacoes_positivas
        }


def exemplo_uso():
    """
    Exemplo de uso do executador
    """
    print("=" * 80)
    print("EXECUTADOR DE ORDENS - MAGNUS WEALTH v9.0.0")
    print("=" * 80)
    
    executador = ExecutadorOrdens()
    
    # Exemplo: Compra
    print("\n📊 Exemplo 1: Executar COMPRA")
    resultado_compra = executador.executar_compra(
        cripto='Bitcoin',
        preco=45000.00,
        motivo='CRITÉRIO 1: Inversão confirmada no candle diário'
    )
    
    # Exemplo: Verificar stop loss
    print("\n📊 Exemplo 2: Verificar Stop Loss")
    preco_atual = 34000.00  # Queda de ~24%
    stop_atingido = executador.verificar_stop_loss('Bitcoin', preco_atual)
    
    if stop_atingido:
        # Executar venda por stop loss
        resultado_venda = executador.executar_venda(
            cripto='Bitcoin',
            preco=preco_atual,
            motivo='CRITÉRIO 3: Stop Loss de 25%'
        )
    
    # Performance
    print("\n📊 Performance Geral:")
    perf = executador.calcular_performance()
    print(json.dumps(perf, indent=2))


if __name__ == '__main__':
    exemplo_uso()
