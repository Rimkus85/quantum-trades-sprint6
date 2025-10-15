#!/usr/bin/env python3
"""
Parser de carteiras para o Magnus Wealth.
Extrai informações estruturadas de mensagens sobre recomendações de investimentos.
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter


class CarteiraParser:
    """Parser para extrair informações estruturadas de mensagens sobre carteiras."""
    
    # Padrões regex
    TICKER_PATTERN = r'\b([A-Z]{4}\d{1,2}[FB]?)\b'
    PERCENTAGE_PATTERN = r'(\d+(?:\.\d+)?)\s*%'
    PRICE_PATTERN = r'R\$\s*(\d+(?:,\d{2})?)'
    
    # Palavras-chave
    COMPRA_KEYWORDS = ['compra', 'comprar', 'entrada', 'adicionar', 'aumentar']
    VENDA_KEYWORDS = ['venda', 'vender', 'saída', 'reduzir', 'diminuir']
    MANTER_KEYWORDS = ['manter', 'segurar', 'hold']
    
    def __init__(self):
        self.carteiras_extraidas = []
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extrai tickers de ações do texto."""
        matches = re.findall(self.TICKER_PATTERN, text.upper())
        return list(set(matches))
    
    def extract_percentages(self, text: str) -> List[float]:
        """Extrai percentuais do texto."""
        matches = re.findall(self.PERCENTAGE_PATTERN, text)
        return [float(p) for p in matches]
    
    def extract_prices(self, text: str) -> List[float]:
        """Extrai preços em reais do texto."""
        matches = re.findall(self.PRICE_PATTERN, text)
        return [float(p.replace(',', '.')) for p in matches]
    
    def identify_recommendation_type(self, text: str) -> str:
        """Identifica o tipo de recomendação."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in self.COMPRA_KEYWORDS):
            return 'compra'
        elif any(keyword in text_lower for keyword in self.VENDA_KEYWORDS):
            return 'venda'
        elif any(keyword in text_lower for keyword in self.MANTER_KEYWORDS):
            return 'manter'
        else:
            return 'indefinido'
    
    def parse_carteira_line(self, line: str) -> Optional[Dict]:
        """Analisa uma linha que pode conter ticker e percentual."""
        tickers = self.extract_tickers(line)
        percentages = self.extract_percentages(line)
        
        if tickers and percentages:
            return {
                'ticker': tickers[0],
                'percentual': percentages[0]
            }
        return None
    
    def parse_message(self, message_text: str, message_date: str = None) -> Dict:
        """Analisa uma mensagem completa e extrai informações estruturadas."""
        result = {
            'data': message_date,
            'texto_original': message_text,
            'tipo_recomendacao': self.identify_recommendation_type(message_text),
            'tickers': self.extract_tickers(message_text),
            'alocacoes': [],
            'precos': self.extract_prices(message_text),
            'total_percentual': 0.0
        }
        
        # Tentar extrair alocações linha por linha
        lines = message_text.split('\n')
        for line in lines:
            parsed = self.parse_carteira_line(line)
            if parsed:
                result['alocacoes'].append(parsed)
        
        # Calcular total de percentual
        if result['alocacoes']:
            result['total_percentual'] = sum(a['percentual'] for a in result['alocacoes'])
        
        return result
    
    def parse_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Processa uma lista de mensagens.
        
        Args:
            messages: Lista de mensagens do Telegram
            
        Returns:
            Lista de carteiras extraídas
        """
        carteiras = []
        for msg in messages:
            parsed = self.parse_message(msg['text'], msg.get('date'))
            
            # Só adiciona se encontrou informações relevantes
            if parsed['tickers'] or parsed['alocacoes']:
                carteiras.append(parsed)
        
        self.carteiras_extraidas = carteiras
        return carteiras
    
    def generate_statistics(self) -> Dict:
        """Gera estatísticas sobre as carteiras extraídas."""
        all_tickers = []
        tipos_recomendacao = {'compra': 0, 'venda': 0, 'manter': 0, 'indefinido': 0}
        
        for carteira in self.carteiras_extraidas:
            all_tickers.extend(carteira['tickers'])
            tipos_recomendacao[carteira['tipo_recomendacao']] += 1
        
        ticker_frequency = Counter(all_tickers)
        
        return {
            'total_carteiras': len(self.carteiras_extraidas),
            'total_tickers_unicos': len(set(all_tickers)),
            'tickers_mais_mencionados': dict(ticker_frequency.most_common(10)),
            'distribuicao_recomendacoes': tipos_recomendacao
        }
    
    def generate_report(self) -> Dict:
        """Gera um relatório estruturado das carteiras extraídas."""
        return {
            'data_geracao': datetime.now().isoformat(),
            'total_mensagens_analisadas': len(self.carteiras_extraidas),
            'carteiras': self.carteiras_extraidas,
            'estatisticas': self.generate_statistics()
        }
    
    def save_report(self, filename: str = 'relatorio_carteiras.json'):
        """Salva o relatório em arquivo JSON."""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return filename
    
    def get_top_tickers(self, limit: int = 10) -> List[tuple]:
        """Retorna os tickers mais mencionados."""
        stats = self.generate_statistics()
        tickers = stats['tickers_mais_mencionados']
        return sorted(tickers.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_carteiras_by_type(self, tipo: str) -> List[Dict]:
        """Filtra carteiras por tipo de recomendação."""
        return [c for c in self.carteiras_extraidas if c['tipo_recomendacao'] == tipo]
    
    def get_latest_carteiras(self, limit: int = 5) -> List[Dict]:
        """Retorna as carteiras mais recentes."""
        return self.carteiras_extraidas[:limit]


# Funções auxiliares para integração com API
def parse_telegram_messages(messages: List[Dict]) -> Dict:
    """
    Função auxiliar para processar mensagens do Telegram.
    
    Args:
        messages: Lista de mensagens do Telegram
        
    Returns:
        Relatório estruturado
    """
    parser = CarteiraParser()
    parser.parse_messages(messages)
    return parser.generate_report()


def get_recommendations_summary(messages: List[Dict]) -> Dict:
    """
    Retorna um resumo das recomendações.
    
    Args:
        messages: Lista de mensagens do Telegram
        
    Returns:
        Resumo com estatísticas
    """
    parser = CarteiraParser()
    parser.parse_messages(messages)
    
    return {
        'top_tickers': parser.get_top_tickers(5),
        'compras': len(parser.get_carteiras_by_type('compra')),
        'vendas': len(parser.get_carteiras_by_type('venda')),
        'total': len(parser.carteiras_extraidas),
        'latest': parser.get_latest_carteiras(3)
    }

