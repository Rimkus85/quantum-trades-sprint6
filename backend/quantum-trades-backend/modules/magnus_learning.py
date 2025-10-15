#!/usr/bin/env python3
"""
Sistema de Aprendizado do Agente Magnus.
Processa recomendações do Telegram e ajusta estratégias de análise.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict, Counter
import statistics


class MagnusLearningEngine:
    """Motor de aprendizado do agente Magnus."""
    
    def __init__(self, learning_rate: float = 0.3):
        """
        Inicializa o motor de aprendizado.
        
        Args:
            learning_rate: Taxa de aprendizado (0.0 a 1.0)
                          Quanto maior, mais peso para novas informações
        """
        self.learning_rate = learning_rate
        self.knowledge_base = {
            'ticker_weights': defaultdict(float),  # Peso de cada ticker
            'recommendation_history': [],  # Histórico de recomendações
            'performance_metrics': {},  # Métricas de performance
            'strategy_adjustments': [],  # Ajustes de estratégia
            'confidence_scores': defaultdict(float)  # Confiança por ticker
        }
        self.last_update = None
    
    def process_telegram_recommendations(self, carteiras: List[Dict]) -> Dict:
        """
        Processa recomendações do Telegram e atualiza base de conhecimento.
        
        Args:
            carteiras: Lista de carteiras analisadas do Telegram
            
        Returns:
            Resumo do processamento
        """
        processed = {
            'total_processed': len(carteiras),
            'tickers_updated': set(),
            'new_insights': [],
            'strategy_changes': []
        }
        
        for carteira in carteiras:
            # Processar cada carteira
            self._process_single_recommendation(carteira, processed)
        
        # Atualizar timestamp
        self.last_update = datetime.now().isoformat()
        
        # Ajustar estratégias baseado em novas informações
        self._adjust_strategies(processed)
        
        return processed
    
    def _process_single_recommendation(self, carteira: Dict, processed: Dict):
        """Processa uma recomendação individual."""
        tipo = carteira.get('tipo_recomendacao', 'indefinido')
        tickers = carteira.get('tickers', [])
        alocacoes = carteira.get('alocacoes', [])
        data = carteira.get('data')
        
        # Registrar no histórico
        self.knowledge_base['recommendation_history'].append({
            'data': data,
            'tipo': tipo,
            'tickers': tickers,
            'alocacoes': alocacoes
        })
        
        # Atualizar pesos dos tickers
        for ticker in tickers:
            # Peso baseado no tipo de recomendação
            weight_delta = self._calculate_weight_delta(tipo)
            
            # Aplicar learning rate
            current_weight = self.knowledge_base['ticker_weights'][ticker]
            new_weight = current_weight + (weight_delta * self.learning_rate)
            
            # Normalizar entre -1 e 1
            new_weight = max(-1.0, min(1.0, new_weight))
            
            self.knowledge_base['ticker_weights'][ticker] = new_weight
            processed['tickers_updated'].add(ticker)
        
        # Processar alocações específicas
        for alocacao in alocacoes:
            ticker = alocacao['ticker']
            percentual = alocacao['percentual']
            
            # Atualizar confiança baseado em alocação
            confidence_boost = percentual / 100.0 * 0.5  # Máximo 0.5
            current_confidence = self.knowledge_base['confidence_scores'][ticker]
            new_confidence = min(1.0, current_confidence + confidence_boost * self.learning_rate)
            
            self.knowledge_base['confidence_scores'][ticker] = new_confidence
    
    def _calculate_weight_delta(self, tipo_recomendacao: str) -> float:
        """Calcula delta de peso baseado no tipo de recomendação."""
        weights = {
            'compra': 0.5,      # Peso positivo forte
            'venda': -0.5,      # Peso negativo forte
            'manter': 0.1,      # Peso positivo fraco
            'indefinido': 0.05  # Peso positivo muito fraco
        }
        return weights.get(tipo_recomendacao, 0.0)
    
    def _adjust_strategies(self, processed: Dict):
        """Ajusta estratégias baseado em novas informações."""
        # Identificar tickers com maior consenso
        top_tickers = self.get_top_recommended_tickers(limit=5)
        
        if top_tickers:
            processed['strategy_changes'].append({
                'type': 'focus_shift',
                'action': 'Aumentar foco nos tickers mais recomendados',
                'tickers': [t[0] for t in top_tickers],
                'timestamp': datetime.now().isoformat()
            })
            
            self.knowledge_base['strategy_adjustments'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'focus_shift',
                'tickers': [t[0] for t in top_tickers]
            })
    
    def get_top_recommended_tickers(self, limit: int = 10) -> List[tuple]:
        """
        Retorna os tickers mais recomendados com base nos pesos.
        
        Args:
            limit: Número máximo de tickers
            
        Returns:
            Lista de tuplas (ticker, peso)
        """
        sorted_tickers = sorted(
            self.knowledge_base['ticker_weights'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_tickers[:limit]
    
    def get_ticker_recommendation(self, ticker: str) -> Dict:
        """
        Retorna recomendação do Magnus para um ticker específico.
        
        Args:
            ticker: Código do ticker
            
        Returns:
            Recomendação estruturada
        """
        weight = self.knowledge_base['ticker_weights'].get(ticker, 0.0)
        confidence = self.knowledge_base['confidence_scores'].get(ticker, 0.0)
        
        # Determinar recomendação baseado no peso
        if weight > 0.3:
            recommendation = 'COMPRA FORTE'
            color = 'green'
        elif weight > 0.1:
            recommendation = 'COMPRA'
            color = 'lightgreen'
        elif weight > -0.1:
            recommendation = 'NEUTRO'
            color = 'gray'
        elif weight > -0.3:
            recommendation = 'VENDA'
            color = 'orange'
        else:
            recommendation = 'VENDA FORTE'
            color = 'red'
        
        return {
            'ticker': ticker,
            'recommendation': recommendation,
            'weight': round(weight, 3),
            'confidence': round(confidence, 3),
            'color': color,
            'last_update': self.last_update
        }
    
    def get_portfolio_suggestion(self, num_assets: int = 5) -> Dict:
        """
        Gera sugestão de portfolio baseado no aprendizado.
        
        Args:
            num_assets: Número de ativos no portfolio
            
        Returns:
            Sugestão de portfolio
        """
        top_tickers = self.get_top_recommended_tickers(limit=num_assets)
        
        if not top_tickers:
            return {
                'status': 'insufficient_data',
                'message': 'Dados insuficientes para gerar sugestão'
            }
        
        # Calcular alocações baseado nos pesos
        total_weight = sum(weight for _, weight in top_tickers if weight > 0)
        
        if total_weight == 0:
            return {
                'status': 'no_positive_recommendations',
                'message': 'Nenhuma recomendação positiva encontrada'
            }
        
        allocations = []
        for ticker, weight in top_tickers:
            if weight > 0:
                percentage = (weight / total_weight) * 100
                allocations.append({
                    'ticker': ticker,
                    'percentage': round(percentage, 2),
                    'weight': round(weight, 3),
                    'confidence': round(self.knowledge_base['confidence_scores'].get(ticker, 0.0), 3)
                })
        
        return {
            'status': 'success',
            'generated_at': datetime.now().isoformat(),
            'num_assets': len(allocations),
            'allocations': allocations,
            'total_percentage': round(sum(a['percentage'] for a in allocations), 2),
            'average_confidence': round(statistics.mean([a['confidence'] for a in allocations]), 3) if allocations else 0
        }
    
    def get_learning_statistics(self) -> Dict:
        """Retorna estatísticas do aprendizado."""
        return {
            'total_recommendations_processed': len(self.knowledge_base['recommendation_history']),
            'unique_tickers': len(self.knowledge_base['ticker_weights']),
            'top_tickers': self.get_top_recommended_tickers(limit=5),
            'strategy_adjustments': len(self.knowledge_base['strategy_adjustments']),
            'last_update': self.last_update,
            'learning_rate': self.learning_rate
        }
    
    def save_knowledge_base(self, filename: str = 'magnus_knowledge.json'):
        """Salva base de conhecimento em arquivo."""
        # Converter defaultdict para dict normal
        knowledge_to_save = {
            'ticker_weights': dict(self.knowledge_base['ticker_weights']),
            'recommendation_history': self.knowledge_base['recommendation_history'],
            'performance_metrics': self.knowledge_base['performance_metrics'],
            'strategy_adjustments': self.knowledge_base['strategy_adjustments'],
            'confidence_scores': dict(self.knowledge_base['confidence_scores']),
            'last_update': self.last_update,
            'learning_rate': self.learning_rate
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(knowledge_to_save, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def load_knowledge_base(self, filename: str = 'magnus_knowledge.json'):
        """Carrega base de conhecimento de arquivo."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.knowledge_base['ticker_weights'] = defaultdict(float, data.get('ticker_weights', {}))
            self.knowledge_base['recommendation_history'] = data.get('recommendation_history', [])
            self.knowledge_base['performance_metrics'] = data.get('performance_metrics', {})
            self.knowledge_base['strategy_adjustments'] = data.get('strategy_adjustments', [])
            self.knowledge_base['confidence_scores'] = defaultdict(float, data.get('confidence_scores', {}))
            self.last_update = data.get('last_update')
            self.learning_rate = data.get('learning_rate', 0.3)
            
            return True
        except FileNotFoundError:
            return False
    
    def reset_knowledge(self):
        """Reseta a base de conhecimento."""
        self.knowledge_base = {
            'ticker_weights': defaultdict(float),
            'recommendation_history': [],
            'performance_metrics': {},
            'strategy_adjustments': [],
            'confidence_scores': defaultdict(float)
        }
        self.last_update = None


class MagnusAnalyzer:
    """Analisador que combina dados do mercado com aprendizado do Magnus."""
    
    def __init__(self, learning_engine: MagnusLearningEngine):
        """
        Inicializa o analisador.
        
        Args:
            learning_engine: Instância do motor de aprendizado
        """
        self.learning_engine = learning_engine
    
    def analyze_ticker(self, ticker: str, market_data: Optional[Dict] = None) -> Dict:
        """
        Analisa um ticker combinando dados de mercado e aprendizado.
        
        Args:
            ticker: Código do ticker
            market_data: Dados de mercado (opcional)
            
        Returns:
            Análise completa
        """
        # Obter recomendação do Magnus
        magnus_rec = self.learning_engine.get_ticker_recommendation(ticker)
        
        analysis = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'magnus_recommendation': magnus_rec,
            'market_data': market_data or {},
            'combined_score': self._calculate_combined_score(magnus_rec, market_data)
        }
        
        return analysis
    
    def _calculate_combined_score(self, magnus_rec: Dict, market_data: Optional[Dict]) -> Dict:
        """Calcula score combinado entre Magnus e dados de mercado."""
        magnus_weight = magnus_rec['weight']
        magnus_confidence = magnus_rec['confidence']
        
        # Score base do Magnus (0 a 100)
        magnus_score = ((magnus_weight + 1) / 2) * 100  # Normaliza -1,1 para 0,100
        
        # Ajustar pela confiança
        final_score = magnus_score * (0.5 + magnus_confidence * 0.5)
        
        return {
            'score': round(final_score, 2),
            'magnus_weight': round(magnus_weight, 3),
            'confidence': round(magnus_confidence, 3),
            'interpretation': self._interpret_score(final_score)
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpreta o score final."""
        if score >= 75:
            return 'Muito Favorável'
        elif score >= 60:
            return 'Favorável'
        elif score >= 40:
            return 'Neutro'
        elif score >= 25:
            return 'Desfavorável'
        else:
            return 'Muito Desfavorável'

