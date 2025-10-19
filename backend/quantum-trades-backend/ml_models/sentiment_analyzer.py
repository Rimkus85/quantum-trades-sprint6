#!/usr/bin/env python3
"""
Magnus Wealth - Sentiment Analyzer
Analisador de sentimento para notícias e mensagens do Telegram
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class SentimentAnalyzer:
    """
    Analisador de sentimento baseado em dicionário léxico
    """
    
    def __init__(self):
        """Inicializa o analisador com dicionários de palavras"""
        
        # Palavras positivas (mercado financeiro brasileiro)
        self.positive_words = {
            # Ações e movimentos
            'alta', 'subida', 'valorização', 'valoriza', 'sobe', 'crescimento',
            'crescer', 'aumenta', 'aumento', 'recuperação', 'recupera',
            
            # Resultados
            'lucro', 'lucros', 'lucrar', 'lucrativo', 'ganho', 'ganhos',
            'receita', 'receitas', 'faturamento', 'resultado', 'positivo',
            
            # Sentimentos
            'otimista', 'otimismo', 'confiança', 'confiante', 'forte',
            'fortalece', 'bom', 'boa', 'excelente', 'ótimo', 'ótima',
            
            # Recomendações
            'compra', 'comprar', 'recomenda', 'recomendação', 'oportunidade',
            'atrativo', 'atrativa', 'interessante', 'promissor', 'promissora',
            
            # Mercado
            'bull', 'bullish', 'rally', 'momentum', 'tendência', 'positiva',
            'favorável', 'benefício', 'beneficia', 'vantagem', 'vantajoso',
            
            # Empresas
            'inovação', 'inovador', 'expansão', 'expande', 'investimento',
            'investe', 'dividendo', 'dividendos', 'proventos', 'distribuição'
        }
        
        # Palavras negativas (mercado financeiro brasileiro)
        self.negative_words = {
            # Ações e movimentos
            'queda', 'baixa', 'desvalorização', 'desvaloriza', 'cai',
            'despenca', 'derrete', 'recua', 'recuo', 'retração',
            
            # Resultados
            'prejuízo', 'prejuízos', 'perda', 'perdas', 'negativo',
            'déficit', 'deficit', 'redução', 'reduz', 'diminui',
            
            # Sentimentos
            'pessimista', 'pessimismo', 'medo', 'pânico', 'incerteza',
            'insegurança', 'fraco', 'fraca', 'ruim', 'péssimo', 'péssima',
            
            # Recomendações
            'venda', 'vender', 'evitar', 'cautela', 'cuidado', 'risco',
            'arriscado', 'perigoso', 'desfavorável', 'problemático',
            
            # Mercado
            'bear', 'bearish', 'crash', 'correção', 'tendência', 'negativa',
            'desfavorável', 'adverso', 'adversa', 'desvantagem',
            
            # Empresas
            'crise', 'falência', 'dívida', 'dívidas', 'endividamento',
            'calote', 'inadimplência', 'problema', 'problemas', 'dificuldade'
        }
        
        # Intensificadores (multiplicam o score)
        self.intensifiers = {
            'muito': 1.5,
            'muita': 1.5,
            'extremamente': 2.0,
            'bastante': 1.3,
            'super': 1.5,
            'mega': 1.8,
            'ultra': 1.8,
            'forte': 1.3,
            'fortemente': 1.5
        }
        
        # Negadores (invertem o sentimento)
        self.negators = {
            'não', 'nao', 'nunca', 'jamais', 'nem', 'sem'
        }
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Pré-processa o texto para análise
        
        Args:
            text: Texto a ser processado
            
        Returns:
            Lista de palavras processadas
        """
        # Converter para minúsculas
        text = text.lower()
        
        # Remover pontuação (exceto hífen)
        text = re.sub(r'[^\w\s-]', ' ', text)
        
        # Remover números
        text = re.sub(r'\d+', '', text)
        
        # Dividir em palavras
        words = text.split()
        
        return words
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analisa o sentimento de um texto
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dicionário com resultado da análise
        """
        words = self.preprocess_text(text)
        
        if not words:
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0.0,
                'positive_words': [],
                'negative_words': []
            }
        
        score = 0
        positive_found = []
        negative_found = []
        
        # Analisar cada palavra
        for i, word in enumerate(words):
            # Verificar intensificador
            multiplier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                multiplier = self.intensifiers[words[i-1]]
            
            # Verificar negador
            is_negated = False
            if i > 0 and words[i-1] in self.negators:
                is_negated = True
            
            # Calcular score
            if word in self.positive_words:
                word_score = 1 * multiplier
                if is_negated:
                    word_score = -word_score
                score += word_score
                positive_found.append(word)
            
            elif word in self.negative_words:
                word_score = -1 * multiplier
                if is_negated:
                    word_score = -word_score
                score += word_score
                negative_found.append(word)
        
        # Determinar sentimento
        if score > 0:
            sentiment = 'positive'
        elif score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calcular confiança (normalizada)
        total_sentiment_words = len(positive_found) + len(negative_found)
        confidence = min(total_sentiment_words / max(len(words), 1), 1.0)
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': round(confidence, 2),
            'positive_words': positive_found,
            'negative_words': negative_found,
            'total_words': len(words)
        }
    
    def analyze_ticker_sentiment(self, ticker: str, messages: List[Dict]) -> Dict:
        """
        Analisa sentimento agregado para um ticker específico
        
        Args:
            ticker: Ticker do ativo (ex: PETR4)
            messages: Lista de mensagens a serem analisadas
            
        Returns:
            Dicionário com sentimento agregado
        """
        ticker = ticker.upper()
        sentiments = []
        
        # Filtrar mensagens que mencionam o ticker
        for msg in messages:
            text = msg.get('text', '') or msg.get('message', '')
            
            if ticker in text.upper():
                result = self.analyze_text(text)
                result['timestamp'] = msg.get('date') or msg.get('timestamp')
                sentiments.append(result)
        
        if not sentiments:
            return {
                'ticker': ticker,
                'sentiment': 'neutral',
                'average_score': 0,
                'total_messages': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'confidence': 0.0
            }
        
        # Calcular estatísticas
        total_messages = len(sentiments)
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        average_score = sum(s['score'] for s in sentiments) / total_messages
        average_confidence = sum(s['confidence'] for s in sentiments) / total_messages
        
        # Determinar sentimento geral
        if average_score > 0.5:
            overall_sentiment = 'positive'
        elif average_score < -0.5:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'ticker': ticker,
            'sentiment': overall_sentiment,
            'average_score': round(average_score, 2),
            'total_messages': total_messages,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'confidence': round(average_confidence, 2),
            'distribution': {
                'positive': round(positive_count / total_messages * 100, 1),
                'negative': round(negative_count / total_messages * 100, 1),
                'neutral': round(neutral_count / total_messages * 100, 1)
            },
            'recent_sentiments': sentiments[-5:]  # Últimos 5
        }
    
    def analyze_multiple_tickers(self, tickers: List[str], messages: List[Dict]) -> List[Dict]:
        """
        Analisa sentimento de múltiplos tickers
        
        Args:
            tickers: Lista de tickers
            messages: Lista de mensagens
            
        Returns:
            Lista de resultados de análise
        """
        results = []
        
        for ticker in tickers:
            result = self.analyze_ticker_sentiment(ticker, messages)
            results.append(result)
        
        # Ordenar por score (mais positivo primeiro)
        results.sort(key=lambda x: x['average_score'], reverse=True)
        
        return results
    
    def get_market_sentiment(self, messages: List[Dict]) -> Dict:
        """
        Analisa sentimento geral do mercado
        
        Args:
            messages: Lista de mensagens
            
        Returns:
            Dicionário com sentimento geral do mercado
        """
        if not messages:
            return {
                'sentiment': 'neutral',
                'score': 0,
                'confidence': 0.0,
                'total_messages': 0
            }
        
        sentiments = []
        
        for msg in messages:
            text = msg.get('text', '') or msg.get('message', '')
            result = self.analyze_text(text)
            sentiments.append(result)
        
        # Calcular médias
        total_messages = len(sentiments)
        average_score = sum(s['score'] for s in sentiments) / total_messages
        average_confidence = sum(s['confidence'] for s in sentiments) / total_messages
        
        # Determinar sentimento geral
        if average_score > 0.5:
            overall_sentiment = 'positive'
            emoji = '😊'
        elif average_score < -0.5:
            overall_sentiment = 'negative'
            emoji = '😢'
        else:
            overall_sentiment = 'neutral'
            emoji = '😐'
        
        return {
            'sentiment': overall_sentiment,
            'emoji': emoji,
            'score': round(average_score, 2),
            'confidence': round(average_confidence, 2),
            'total_messages': total_messages,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do analisador de sentimento"""
    
    analyzer = SentimentAnalyzer()
    
    print("=" * 60)
    print("TESTE DO ANALISADOR DE SENTIMENTO")
    print("=" * 60)
    
    # Teste 1: Texto positivo
    print("\n1. Texto Positivo:")
    text1 = "PETR4 teve lucro recorde no trimestre, ações sobem forte"
    result1 = analyzer.analyze_text(text1)
    print(f"   Texto: {text1}")
    print(f"   Resultado: {result1}")
    
    # Teste 2: Texto negativo
    print("\n2. Texto Negativo:")
    text2 = "VALE3 despenca com queda de preços e prejuízo no trimestre"
    result2 = analyzer.analyze_text(text2)
    print(f"   Texto: {text2}")
    print(f"   Resultado: {result2}")
    
    # Teste 3: Texto neutro
    print("\n3. Texto Neutro:")
    text3 = "ITUB4 divulga resultado do trimestre"
    result3 = analyzer.analyze_text(text3)
    print(f"   Texto: {text3}")
    print(f"   Resultado: {result3}")
    
    # Teste 4: Análise de ticker
    print("\n4. Análise de Ticker:")
    messages = [
        {'text': 'PETR4 teve lucro recorde', 'date': '2025-10-18'},
        {'text': 'PETR4 valoriza forte hoje', 'date': '2025-10-18'},
        {'text': 'Recomendo compra de PETR4', 'date': '2025-10-18'},
    ]
    result4 = analyzer.analyze_ticker_sentiment('PETR4', messages)
    print(f"   Ticker: PETR4")
    print(f"   Resultado: {result4}")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

