"""
Processador Inteligente de Mensagens de Opções.
Aprende com operações vencedoras e perdedoras.
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class OperationType(Enum):
    """Tipos de operação."""
    COMPRA_CALL = "Compra de Call"
    COMPRA_PUT = "Compra de Put"
    VENDA_CALL = "Venda de Call"
    VENDA_PUT = "Venda de Put"
    TRAVA_ALTA = "Trava de Alta"
    TRAVA_BAIXA = "Trava de Baixa"
    BUTTERFLY = "Butterfly"
    OUTRO = "Outro"


class OperationStatus(Enum):
    """Status da operação."""
    MONTADA = "Montada"  # Apenas alerta de montagem
    ROLADA = "Rolada"  # Foi rolada
    DESMONTADA_LUCRO = "Desmontada com Lucro"  # Vencedora
    DESMONTADA_PREJUIZO = "Desmontada com Prejuízo"
    EXPIRADA_PO = "Expirada (Virou Pó)"  # Perdedora


@dataclass
class OptionsAlert:
    """Alerta de opções."""
    date: str
    alert_type: str  # "Montagem", "Desmontagem", "Rolagem"
    ticker: str
    structure: str
    strike: Optional[str] = None
    expiration: Optional[str] = None
    price: Optional[float] = None
    profit_pct: Optional[float] = None
    context: str = ""  # Texto ao redor do alerta
    message_id: int = 0


@dataclass
class OptionsOperation:
    """Operação completa de opções."""
    ticker: str
    structure: str
    montagem: OptionsAlert
    rolagens: List[OptionsAlert]
    desmontagem: Optional[OptionsAlert]
    status: OperationStatus
    profit_pct: Optional[float] = None
    days_duration: Optional[int] = None
    motivation: str = ""  # Por que montou
    learning: str = ""  # O que aprendeu


class OpcoesProcessor:
    """Processa mensagens de opções e aprende com elas."""
    
    def __init__(self):
        """Inicializa o processador."""
        self.alerts: List[OptionsAlert] = []
        self.operations: List[OptionsOperation] = []
        self.knowledge_base = {
            'winners': [],  # Operações vencedoras
            'losers': [],   # Operações perdedoras
            'patterns': {}  # Padrões identificados
        }
    
    def process_messages(self, messages: List[Dict]) -> Dict:
        """
        Processa mensagens e extrai alertas.
        
        Args:
            messages: Lista de mensagens
            
        Returns:
            Estatísticas do processamento
        """
        print("=" * 80)
        print("PROCESSADOR DE OPÇÕES - APRENDIZADO INTELIGENTE")
        print("=" * 80)
        
        # Extrair alertas
        print(f"\n📊 Processando {len(messages)} mensagens...")
        for msg in messages:
            alert = self._extract_alert(msg)
            if alert:
                self.alerts.append(alert)
        
        print(f"✅ {len(self.alerts)} alertas extraídos")
        
        # Agrupar em operações
        print(f"\n🔄 Agrupando alertas em operações...")
        self._group_into_operations()
        print(f"✅ {len(self.operations)} operações identificadas")
        
        # Classificar operações
        print(f"\n🎯 Classificando operações...")
        self._classify_operations()
        
        # Gerar base de conhecimento
        print(f"\n🧠 Gerando base de conhecimento...")
        self._generate_knowledge_base()
        
        # Estatísticas
        stats = self._calculate_stats()
        
        print("\n" + "=" * 80)
        print("✅ PROCESSAMENTO CONCLUÍDO")
        print("=" * 80)
        
        return stats
    
    def _extract_alert(self, message: Dict) -> Optional[OptionsAlert]:
        """
        Extrai alerta de uma mensagem.
        
        Args:
            message: Mensagem
            
        Returns:
            OptionsAlert ou None
        """
        text = message.get('text', '')
        date = message.get('date', '')
        
        # Detectar tipo de alerta
        alert_type = None
        if '**Alerta de Montagem**' in text or 'Alerta de Montagem' in text:
            alert_type = 'Montagem'
        elif '**Alerta de Desmontagem**' in text or 'Alerta de Desmontagem' in text:
            alert_type = 'Desmontagem'
        elif 'rolagem' in text.lower() or 'rolar' in text.lower():
            alert_type = 'Rolagem'
        
        if not alert_type:
            return None
        
        # Extrair informações
        ticker = self._extract_ticker(text)
        structure = self._extract_structure(text)
        strike = self._extract_strike(text)
        expiration = self._extract_expiration(text)
        price = self._extract_price(text)
        profit_pct = self._extract_profit(text)
        
        if not ticker:
            return None
        
        return OptionsAlert(
            date=date,
            alert_type=alert_type,
            ticker=ticker,
            structure=structure,
            strike=strike,
            expiration=expiration,
            price=price,
            profit_pct=profit_pct,
            context=text[:500]  # Primeiros 500 caracteres
        )
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """Extrai ticker da mensagem."""
        # Padrão: "Ativo objeto: TICKER"
        match = re.search(r'Ativo objeto:\s*([A-Z0-9]+)', text)
        if match:
            return match.group(1)
        
        # Padrão: "TICKER 251121 C"
        match = re.search(r'\b([A-Z]{3,5}\d?)\s+\d{6}\s+[CP]', text)
        if match:
            return match.group(1)
        
        # Padrão: ticker entre **
        match = re.search(r'\*\*([A-Z]{3,5}\d?)\s+\d{6}', text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_structure(self, text: str) -> str:
        """Extrai estrutura da operação."""
        text_lower = text.lower()
        
        if 'compra de call' in text_lower:
            return OperationType.COMPRA_CALL.value
        elif 'compra de put' in text_lower:
            return OperationType.COMPRA_PUT.value
        elif 'venda de call' in text_lower:
            return OperationType.VENDA_CALL.value
        elif 'venda de put' in text_lower:
            return OperationType.VENDA_PUT.value
        elif 'trava de alta' in text_lower:
            return OperationType.TRAVA_ALTA.value
        elif 'trava de baixa' in text_lower:
            return OperationType.TRAVA_BAIXA.value
        elif 'butterfly' in text_lower:
            return OperationType.BUTTERFLY.value
        
        return OperationType.OUTRO.value
    
    def _extract_strike(self, text: str) -> Optional[str]:
        """Extrai strike da opção."""
        # Padrão: C 00015000 ou P 00058560
        match = re.search(r'[CP]\s+(\d{8})', text)
        if match:
            strike_raw = match.group(1)
            # Converter para float e formatar
            strike_value = int(strike_raw) / 100
            return f"{strike_value:.2f}"
        
        # Padrão: strike 238
        match = re.search(r'strike\s+(\d+(?:\.\d+)?)', text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_expiration(self, text: str) -> Optional[str]:
        """Extrai vencimento."""
        # Padrão: 21/11/2025
        match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if match:
            return match.group(1)
        
        # Padrão: 251121 (AAMMDD)
        match = re.search(r'(\d{6})\s+[CP]', text)
        if match:
            date_str = match.group(1)
            year = '20' + date_str[:2]
            month = date_str[2:4]
            day = date_str[4:6]
            return f"{day}/{month}/{year}"
        
        return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extrai preço."""
        # Padrão: saindo a 10.85 ou saindo entre 3.85 e 3.80
        match = re.search(r'saindo\s+(?:a|entre)\s+(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))
        
        # Padrão: preço de mercado R$ 1,50
        match = re.search(r'R\$\s*(\d+(?:[,\.]\d+)?)', text)
        if match:
            price_str = match.group(1).replace(',', '.')
            return float(price_str)
        
        return None
    
    def _extract_profit(self, text: str) -> Optional[float]:
        """Extrai percentual de lucro."""
        # Padrão: ~150% de lucro ou 85% de alta
        match = re.search(r'~?(\d+)%\s+de\s+(?:lucro|alta)', text)
        if match:
            return float(match.group(1))
        
        return None
    
    def _group_into_operations(self):
        """Agrupa alertas em operações completas."""
        # Agrupar por ticker
        by_ticker = {}
        for alert in self.alerts:
            if alert.ticker not in by_ticker:
                by_ticker[alert.ticker] = []
            by_ticker[alert.ticker].append(alert)
        
        # Criar operações
        for ticker, alerts in by_ticker.items():
            # Ordenar por data
            alerts.sort(key=lambda x: x.date)
            
            # Agrupar em ciclos (Montagem → Rolagens → Desmontagem)
            i = 0
            while i < len(alerts):
                alert = alerts[i]
                
                if alert.alert_type == 'Montagem':
                    # Início de uma operação
                    montagem = alert
                    rolagens = []
                    desmontagem = None
                    
                    # Buscar rolagens e desmontagem
                    j = i + 1
                    while j < len(alerts):
                        next_alert = alerts[j]
                        
                        if next_alert.alert_type == 'Rolagem':
                            rolagens.append(next_alert)
                        elif next_alert.alert_type == 'Desmontagem':
                            desmontagem = next_alert
                            i = j
                            break
                        elif next_alert.alert_type == 'Montagem':
                            # Nova montagem, termina ciclo anterior
                            break
                        
                        j += 1
                    
                    # Criar operação
                    operation = OptionsOperation(
                        ticker=ticker,
                        structure=montagem.structure,
                        montagem=montagem,
                        rolagens=rolagens,
                        desmontagem=desmontagem,
                        status=OperationStatus.MONTADA
                    )
                    
                    self.operations.append(operation)
                
                i += 1
    
    def _classify_operations(self):
        """Classifica operações como vencedoras ou perdedoras."""
        for op in self.operations:
            # Calcular duração
            if op.desmontagem:
                date_montagem = datetime.fromisoformat(op.montagem.date.replace(' ', 'T'))
                date_desmontagem = datetime.fromisoformat(op.desmontagem.date.replace(' ', 'T'))
                op.days_duration = (date_desmontagem - date_montagem).days
            
            # Classificar
            if op.desmontagem:
                # Tem desmontagem
                if op.desmontagem.profit_pct and op.desmontagem.profit_pct > 0:
                    op.status = OperationStatus.DESMONTADA_LUCRO
                    op.profit_pct = op.desmontagem.profit_pct
                else:
                    op.status = OperationStatus.DESMONTADA_PREJUIZO
            elif op.rolagens:
                # Tem rolagens mas sem desmontagem (ainda ativa ou virou pó)
                op.status = OperationStatus.ROLADA
            else:
                # Apenas montagem, sem desmontagem
                # Verificar se expirou
                if op.montagem.expiration:
                    try:
                        exp_date = datetime.strptime(op.montagem.expiration, '%d/%m/%Y')
                        if exp_date < datetime.now():
                            op.status = OperationStatus.EXPIRADA_PO
                    except:
                        pass
    
    def _generate_knowledge_base(self):
        """Gera base de conhecimento com operações vencedoras e perdedoras."""
        for op in self.operations:
            if op.status == OperationStatus.DESMONTADA_LUCRO:
                # VENCEDORA - Aprender e replicar
                learning = {
                    'ticker': op.ticker,
                    'structure': op.structure,
                    'profit_pct': op.profit_pct,
                    'days_duration': op.days_duration,
                    'motivation': self._extract_motivation(op.montagem.context),
                    'context': op.montagem.context[:200],
                    'date': op.montagem.date,
                    'had_rolagens': len(op.rolagens) > 0
                }
                self.knowledge_base['winners'].append(learning)
            
            elif op.status == OperationStatus.EXPIRADA_PO:
                # PERDEDORA - Aprender o que evitar
                learning = {
                    'ticker': op.ticker,
                    'structure': op.structure,
                    'what_went_wrong': 'Opção expirou sem valor (virou pó)',
                    'context': op.montagem.context[:200],
                    'date': op.montagem.date,
                    'lesson': 'Evitar estruturas similares neste contexto'
                }
                self.knowledge_base['losers'].append(learning)
    
    def _extract_motivation(self, context: str) -> str:
        """Extrai motivação da montagem do contexto."""
        # Procurar por indicadores de motivação
        motivations = []
        
        context_lower = context.lower()
        
        if 'correção' in context_lower or 'correcao' in context_lower:
            motivations.append('Correção de mercado')
        if 'tendência' in context_lower or 'tendencia' in context_lower:
            motivations.append('Mudança de tendência')
        if 'alta' in context_lower and 'esperada' in context_lower:
            motivations.append('Expectativa de alta')
        if 'baixa' in context_lower and 'esperada' in context_lower:
            motivations.append('Expectativa de baixa')
        if 'suporte' in context_lower:
            motivations.append('Teste de suporte')
        if 'resistência' in context_lower or 'resistencia' in context_lower:
            motivations.append('Teste de resistência')
        
        return ', '.join(motivations) if motivations else 'Análise técnica'
    
    def _calculate_stats(self) -> Dict:
        """Calcula estatísticas."""
        total_ops = len(self.operations)
        winners = len(self.knowledge_base['winners'])
        losers = len(self.knowledge_base['losers'])
        
        win_rate = (winners / total_ops * 100) if total_ops > 0 else 0
        
        avg_profit = 0
        if winners > 0:
            profits = [w['profit_pct'] for w in self.knowledge_base['winners'] if w.get('profit_pct')]
            avg_profit = sum(profits) / len(profits) if profits else 0
        
        avg_duration = 0
        if winners > 0:
            durations = [w['days_duration'] for w in self.knowledge_base['winners'] if w.get('days_duration')]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_alerts': len(self.alerts),
            'total_operations': total_ops,
            'winners': winners,
            'losers': losers,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_duration': avg_duration
        }
    
    def save_knowledge_base(self, filename: str = 'opcoes_knowledge_base.json'):
        """Salva base de conhecimento."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Base de conhecimento salva em: {filename}")
    
    def print_summary(self):
        """Imprime resumo do aprendizado."""
        print("\n" + "=" * 80)
        print("📊 RESUMO DO APRENDIZADO")
        print("=" * 80)
        
        stats = self._calculate_stats()
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total de alertas: {stats['total_alerts']}")
        print(f"   Total de operações: {stats['total_operations']}")
        print(f"   Operações vencedoras: {stats['winners']}")
        print(f"   Operações perdedoras: {stats['losers']}")
        print(f"   Taxa de acerto: {stats['win_rate']:.1f}%")
        print(f"   Lucro médio: {stats['avg_profit']:.1f}%")
        print(f"   Duração média: {stats['avg_duration']:.0f} dias")
        
        # Top vencedoras
        if self.knowledge_base['winners']:
            print(f"\n🏆 TOP 5 OPERAÇÕES VENCEDORAS:")
            winners_sorted = sorted(
                self.knowledge_base['winners'],
                key=lambda x: x.get('profit_pct', 0),
                reverse=True
            )[:5]
            
            for i, w in enumerate(winners_sorted, 1):
                print(f"\n   {i}. {w['ticker']} - {w['structure']}")
                print(f"      Lucro: {w.get('profit_pct', 0):.0f}%")
                print(f"      Duração: {w.get('days_duration', 0)} dias")
                print(f"      Motivação: {w.get('motivation', 'N/A')}")
        
        # Perdedoras
        if self.knowledge_base['losers']:
            print(f"\n❌ OPERAÇÕES PERDEDORAS (Viraram Pó):")
            for i, l in enumerate(self.knowledge_base['losers'], 1):
                print(f"\n   {i}. {l['ticker']} - {l['structure']}")
                print(f"      Erro: {l['what_went_wrong']}")
                print(f"      Lição: {l['lesson']}")


def main():
    """Função principal para teste."""
    # Carregar mensagens
    with open('opcoes_messages.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    # Processar
    processor = OpcoesProcessor()
    stats = processor.process_messages(messages)
    
    # Salvar
    processor.save_knowledge_base()
    
    # Resumo
    processor.print_summary()


if __name__ == '__main__':
    main()

