#!/usr/bin/env python3
"""
Magnus Advanced Learning - Sistema de Aprendizado Avançado.
Aprende com performance real, erros, contexto de mercado e ajusta estratégias autonomamente.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import statistics


class MarketCondition(Enum):
    """Condições de mercado."""
    BULL = "alta"  # Mercado em alta
    BEAR = "baixa"  # Mercado em baixa
    SIDEWAYS = "lateral"  # Mercado lateral
    VOLATILE = "volátil"  # Mercado volátil
    CRISIS = "crise"  # Crise/crash


class StrategyMode(Enum):
    """Modos de estratégia."""
    AGGRESSIVE = "agressivo"
    MODERATE = "moderado"
    CONSERVATIVE = "conservador"
    DEFENSIVE = "defensivo"


@dataclass
class Position:
    """Representa uma posição na carteira."""
    ticker: str
    entry_date: str
    entry_price: float
    quantity: int
    target_price: float
    stop_loss: float
    expected_return: float  # Percentual esperado
    timeframe_days: int  # Prazo em dias
    validity_date: str  # Data de validade
    reason: str  # Razão da entrada
    sector: str  # Setor da empresa
    current_price: Optional[float] = None
    current_return: Optional[float] = None
    status: str = "active"  # active, expired, stopped, target_reached
    
    def is_expired(self) -> bool:
        """Verifica se a posição expirou."""
        validity = datetime.fromisoformat(self.validity_date)
        return datetime.now() > validity
    
    def days_remaining(self) -> int:
        """Dias restantes até expiração."""
        validity = datetime.fromisoformat(self.validity_date)
        delta = validity - datetime.now()
        return max(0, delta.days)
    
    def update_current_price(self, price: float):
        """Atualiza preço atual e retorno."""
        self.current_price = price
        self.current_return = ((price - self.entry_price) / self.entry_price) * 100
        
        # Atualizar status
        if self.current_return >= self.expected_return:
            self.status = "target_reached"
        elif price <= self.stop_loss:
            self.status = "stopped"
        elif self.is_expired():
            self.status = "expired"


@dataclass
class PerformanceRecord:
    """Registro de performance de uma recomendação."""
    ticker: str
    recommendation_date: str
    recommendation_type: str  # compra, venda, manter
    entry_price: float
    target_price: float
    timeframe_days: int
    actual_price: Optional[float] = None
    actual_return: Optional[float] = None
    expected_return: Optional[float] = None
    hit: Optional[bool] = None  # True se atingiu meta, False se não
    closed_date: Optional[str] = None
    reason_for_close: Optional[str] = None


class PerformanceTracker:
    """Rastreador de performance de recomendações."""
    
    def __init__(self):
        self.positions: List[Position] = []
        self.performance_history: List[PerformanceRecord] = []
        self.sector_performance: Dict[str, List[float]] = defaultdict(list)
    
    def add_position(self, position: Position):
        """Adiciona nova posição."""
        self.positions.append(position)
    
    def update_prices(self, prices: Dict[str, float]):
        """Atualiza preços de todas as posições."""
        for position in self.positions:
            if position.ticker in prices and position.status == "active":
                position.update_current_price(prices[position.ticker])
    
    def get_active_positions(self) -> List[Position]:
        """Retorna posições ativas."""
        return [p for p in self.positions if p.status == "active"]
    
    def get_expired_positions(self) -> List[Position]:
        """Retorna posições expiradas que precisam revisão."""
        return [p for p in self.positions if p.is_expired() and p.status == "active"]
    
    def close_position(self, ticker: str, final_price: float, reason: str):
        """Fecha uma posição e registra performance."""
        for position in self.positions:
            if position.ticker == ticker and position.status == "active":
                position.update_current_price(final_price)
                position.status = "closed"
                
                # Criar registro de performance
                record = PerformanceRecord(
                    ticker=ticker,
                    recommendation_date=position.entry_date,
                    recommendation_type="compra",
                    entry_price=position.entry_price,
                    target_price=position.target_price,
                    timeframe_days=position.timeframe_days,
                    actual_price=final_price,
                    actual_return=position.current_return,
                    expected_return=position.expected_return,
                    hit=position.current_return >= position.expected_return,
                    closed_date=datetime.now().isoformat(),
                    reason_for_close=reason
                )
                
                self.performance_history.append(record)
                self.sector_performance[position.sector].append(position.current_return or 0)
                
                break
    
    def get_hit_rate(self, days: Optional[int] = None) -> float:
        """Calcula taxa de acerto."""
        records = self.performance_history
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            records = [r for r in records if datetime.fromisoformat(r.recommendation_date) > cutoff]
        
        if not records:
            return 0.0
        
        hits = sum(1 for r in records if r.hit)
        return (hits / len(records)) * 100
    
    def get_average_return(self, days: Optional[int] = None) -> float:
        """Calcula retorno médio."""
        records = self.performance_history
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            records = [r for r in records if datetime.fromisoformat(r.recommendation_date) > cutoff]
        
        returns = [r.actual_return for r in records if r.actual_return is not None]
        
        if not returns:
            return 0.0
        
        return statistics.mean(returns)
    
    def get_sector_performance(self, sector: str) -> Dict:
        """Retorna performance de um setor."""
        returns = self.sector_performance.get(sector, [])
        
        if not returns:
            return {
                "sector": sector,
                "trades": 0,
                "average_return": 0.0,
                "best_return": 0.0,
                "worst_return": 0.0
            }
        
        return {
            "sector": sector,
            "trades": len(returns),
            "average_return": statistics.mean(returns),
            "best_return": max(returns),
            "worst_return": min(returns)
        }


class MarketContextAnalyzer:
    """Analisador de contexto de mercado."""
    
    def __init__(self):
        self.market_condition = MarketCondition.SIDEWAYS
        self.sector_trends: Dict[str, str] = {}
        self.macro_indicators: Dict[str, float] = {}
    
    def analyze_market_condition(self, market_data: Dict) -> MarketCondition:
        """Analisa condição atual do mercado."""
        # Aqui seria integrado com APIs de mercado
        # Por enquanto, análise básica
        
        ibov_change = market_data.get('ibovespa_change_30d', 0)
        volatility = market_data.get('volatility', 0)
        
        if volatility > 30:
            return MarketCondition.VOLATILE
        elif ibov_change > 10:
            return MarketCondition.BULL
        elif ibov_change < -10:
            return MarketCondition.BEAR
        elif ibov_change < -20:
            return MarketCondition.CRISIS
        else:
            return MarketCondition.SIDEWAYS
    
    def analyze_sector(self, sector: str, sector_data: Dict) -> Dict:
        """Analisa um setor específico."""
        return {
            "sector": sector,
            "trend": sector_data.get('trend', 'neutral'),
            "performance_30d": sector_data.get('performance_30d', 0),
            "outlook": sector_data.get('outlook', 'neutral'),
            "risks": sector_data.get('risks', []),
            "opportunities": sector_data.get('opportunities', [])
        }
    
    def get_sector_correlation(self, sector1: str, sector2: str) -> float:
        """Calcula correlação entre setores."""
        # Exemplo: tecnologia pode impactar agronegócio
        correlations = {
            ('tecnologia', 'agronegocio'): 0.3,  # Automação
            ('tecnologia', 'financeiro'): 0.7,  # Fintechs
            ('commodities', 'agronegocio'): 0.8,  # Alta correlação
            ('energia', 'industrial'): 0.6,
        }
        
        key = (sector1.lower(), sector2.lower())
        return correlations.get(key, correlations.get((sector2.lower(), sector1.lower()), 0.0))


class StrategyAdjuster:
    """Ajustador autônomo de estratégias."""
    
    def __init__(self, performance_tracker: PerformanceTracker, 
                 market_analyzer: MarketContextAnalyzer):
        self.performance_tracker = performance_tracker
        self.market_analyzer = market_analyzer
        self.current_mode = StrategyMode.MODERATE
    
    def determine_strategy_mode(self) -> StrategyMode:
        """Determina modo de estratégia baseado em contexto."""
        # Análise de performance recente
        hit_rate_30d = self.performance_tracker.get_hit_rate(days=30)
        avg_return_30d = self.performance_tracker.get_average_return(days=30)
        
        # Condição de mercado
        market_condition = self.market_analyzer.market_condition
        
        # Lógica de decisão
        if market_condition == MarketCondition.CRISIS:
            return StrategyMode.DEFENSIVE
        
        elif market_condition == MarketCondition.BEAR:
            if hit_rate_30d < 50:
                return StrategyMode.DEFENSIVE
            else:
                return StrategyMode.CONSERVATIVE
        
        elif market_condition == MarketCondition.BULL:
            if hit_rate_30d > 70 and avg_return_30d > 5:
                return StrategyMode.AGGRESSIVE
            else:
                return StrategyMode.MODERATE
        
        elif market_condition == MarketCondition.VOLATILE:
            if hit_rate_30d > 60:
                return StrategyMode.MODERATE
            else:
                return StrategyMode.CONSERVATIVE
        
        else:  # SIDEWAYS
            return StrategyMode.MODERATE
    
    def adjust_position_sizing(self, base_size: float) -> float:
        """Ajusta tamanho de posição baseado em estratégia."""
        mode = self.current_mode
        
        multipliers = {
            StrategyMode.AGGRESSIVE: 1.5,
            StrategyMode.MODERATE: 1.0,
            StrategyMode.CONSERVATIVE: 0.7,
            StrategyMode.DEFENSIVE: 0.5
        }
        
        return base_size * multipliers[mode]
    
    def adjust_targets(self, base_target: float, base_stop: float) -> Tuple[float, float]:
        """Ajusta alvos e stops baseado em estratégia."""
        mode = self.current_mode
        
        if mode == StrategyMode.AGGRESSIVE:
            # Alvos mais ambiciosos, stops mais largos
            target = base_target * 1.3
            stop = base_stop * 0.8
        elif mode == StrategyMode.MODERATE:
            target = base_target
            stop = base_stop
        elif mode == StrategyMode.CONSERVATIVE:
            # Alvos mais conservadores, stops mais apertados
            target = base_target * 0.8
            stop = base_stop * 1.2
        else:  # DEFENSIVE
            # Alvos muito conservadores, stops muito apertados
            target = base_target * 0.6
            stop = base_stop * 1.5
        
        return target, stop


class MagnusAdvancedLearning:
    """Sistema avançado de aprendizado do Magnus."""
    
    def __init__(self):
        self.performance_tracker = PerformanceTracker()
        self.market_analyzer = MarketContextAnalyzer()
        self.strategy_adjuster = StrategyAdjuster(
            self.performance_tracker,
            self.market_analyzer
        )
        self.error_log: List[Dict] = []
        self.learning_insights: List[Dict] = []
    
    def review_expired_positions(self) -> List[Dict]:
        """Revisa posições expiradas e decide ações."""
        expired = self.performance_tracker.get_expired_positions()
        actions = []
        
        for position in expired:
            # Analisar se ainda faz sentido manter
            analysis = self._analyze_position_validity(position)
            
            action = {
                "ticker": position.ticker,
                "entry_date": position.entry_date,
                "days_held": (datetime.now() - datetime.fromisoformat(position.entry_date)).days,
                "current_return": position.current_return,
                "expected_return": position.expected_return,
                "analysis": analysis,
                "recommendation": analysis['recommendation']
            }
            
            actions.append(action)
        
        return actions
    
    def _analyze_position_validity(self, position: Position) -> Dict:
        """Analisa se posição ainda é válida."""
        # Verificar performance atual
        if position.current_return and position.current_return >= position.expected_return:
            return {
                "status": "target_reached",
                "recommendation": "REALIZAR_LUCRO",
                "reason": f"Meta de {position.expected_return}% atingida"
            }
        
        # Verificar se atingiu stop
        if position.current_price and position.current_price <= position.stop_loss:
            return {
                "status": "stop_hit",
                "recommendation": "VENDER",
                "reason": "Stop loss atingido"
            }
        
        # Verificar contexto de mercado
        sector_perf = self.performance_tracker.get_sector_performance(position.sector)
        
        if sector_perf['average_return'] < -5:
            return {
                "status": "sector_underperforming",
                "recommendation": "REAVALIAR",
                "reason": f"Setor {position.sector} com performance negativa"
            }
        
        # Verificar se ainda há potencial
        remaining_potential = position.expected_return - (position.current_return or 0)
        
        if remaining_potential > 5:
            return {
                "status": "still_valid",
                "recommendation": "MANTER",
                "reason": f"Ainda há potencial de {remaining_potential:.1f}%"
            }
        else:
            return {
                "status": "low_potential",
                "recommendation": "SUBSTITUIR",
                "reason": "Baixo potencial restante, buscar melhores oportunidades"
            }
    
    def learn_from_error(self, error: Dict):
        """Aprende com um erro de análise."""
        self.error_log.append({
            **error,
            "timestamp": datetime.now().isoformat()
        })
        
        # Gerar insight
        insight = self._generate_insight_from_error(error)
        if insight:
            self.learning_insights.append(insight)
    
    def _generate_insight_from_error(self, error: Dict) -> Optional[Dict]:
        """Gera insight a partir de erro."""
        error_type = error.get('type')
        
        if error_type == 'wrong_direction':
            # Erro de direção (compra quando deveria vender)
            return {
                "type": "direction_correction",
                "ticker": error.get('ticker'),
                "lesson": f"Evitar {error.get('action')} em {error.get('ticker')} sob condições similares",
                "conditions": error.get('market_conditions'),
                "timestamp": datetime.now().isoformat()
            }
        
        elif error_type == 'timing_error':
            # Erro de timing
            return {
                "type": "timing_adjustment",
                "ticker": error.get('ticker'),
                "lesson": "Ajustar timeframe de análise",
                "adjustment": "Aumentar prazo de análise em 20%",
                "timestamp": datetime.now().isoformat()
            }
        
        elif error_type == 'sector_misjudgment':
            # Erro de análise setorial
            return {
                "type": "sector_learning",
                "sector": error.get('sector'),
                "lesson": f"Setor {error.get('sector')} mais sensível a {error.get('factor')}",
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def get_autonomous_recommendation(self, ticker: str, sector: str, 
                                     current_price: float, 
                                     market_data: Dict) -> Dict:
        """Gera recomendação autônoma baseada em todo o aprendizado."""
        
        # Atualizar condição de mercado
        self.market_analyzer.market_condition = \
            self.market_analyzer.analyze_market_condition(market_data)
        
        # Determinar modo de estratégia
        self.strategy_adjuster.current_mode = \
            self.strategy_adjuster.determine_strategy_mode()
        
        # Verificar performance histórica do ticker
        ticker_history = [r for r in self.performance_tracker.performance_history 
                         if r.ticker == ticker]
        
        # Verificar performance do setor
        sector_perf = self.performance_tracker.get_sector_performance(sector)
        
        # Verificar erros anteriores
        ticker_errors = [e for e in self.error_log if e.get('ticker') == ticker]
        
        # Calcular score baseado em múltiplos fatores
        score = self._calculate_comprehensive_score(
            ticker, sector, ticker_history, sector_perf, ticker_errors
        )
        
        # Gerar recomendação
        if score > 75:
            action = "COMPRA_FORTE"
            target_multiplier = 1.2
        elif score > 60:
            action = "COMPRA"
            target_multiplier = 1.1
        elif score > 40:
            action = "MANTER"
            target_multiplier = 1.0
        elif score > 25:
            action = "VENDA"
            target_multiplier = 0.9
        else:
            action = "VENDA_FORTE"
            target_multiplier = 0.8
        
        # Calcular alvos ajustados
        base_target = current_price * 1.1  # 10% de alvo base
        base_stop = current_price * 0.95   # 5% de stop base
        
        adjusted_target, adjusted_stop = self.strategy_adjuster.adjust_targets(
            base_target, base_stop
        )
        
        return {
            "ticker": ticker,
            "action": action,
            "score": score,
            "current_price": current_price,
            "target_price": adjusted_target,
            "stop_loss": adjusted_stop,
            "expected_return": ((adjusted_target - current_price) / current_price) * 100,
            "strategy_mode": self.strategy_adjuster.current_mode.value,
            "market_condition": self.market_analyzer.market_condition.value,
            "sector_performance": sector_perf,
            "confidence": self._calculate_confidence(score, ticker_history),
            "reasoning": self._generate_reasoning(score, sector_perf, ticker_errors)
        }
    
    def _calculate_comprehensive_score(self, ticker: str, sector: str,
                                       ticker_history: List,
                                       sector_perf: Dict,
                                       ticker_errors: List) -> float:
        """Calcula score abrangente."""
        score = 50  # Base neutra
        
        # Ajustar por performance histórica do ticker
        if ticker_history:
            hit_rate = sum(1 for r in ticker_history if r.hit) / len(ticker_history)
            score += (hit_rate - 0.5) * 40  # -20 a +20
        
        # Ajustar por performance do setor
        if sector_perf['trades'] > 0:
            sector_score = min(20, max(-20, sector_perf['average_return']))
            score += sector_score
        
        # Penalizar por erros recentes
        recent_errors = [e for e in ticker_errors 
                        if (datetime.now() - datetime.fromisoformat(e['timestamp'])).days < 30]
        score -= len(recent_errors) * 10
        
        # Ajustar por condição de mercado
        market_adjustments = {
            MarketCondition.BULL: 10,
            MarketCondition.SIDEWAYS: 0,
            MarketCondition.BEAR: -10,
            MarketCondition.VOLATILE: -5,
            MarketCondition.CRISIS: -20
        }
        score += market_adjustments[self.market_analyzer.market_condition]
        
        # Normalizar entre 0 e 100
        return max(0, min(100, score))
    
    def _calculate_confidence(self, score: float, history: List) -> float:
        """Calcula confiança na recomendação."""
        base_confidence = score / 100
        
        # Ajustar por quantidade de dados históricos
        if len(history) > 10:
            base_confidence *= 1.2
        elif len(history) < 3:
            base_confidence *= 0.7
        
        return min(1.0, base_confidence)
    
    def _generate_reasoning(self, score: float, sector_perf: Dict, 
                           errors: List) -> str:
        """Gera explicação da recomendação."""
        reasons = []
        
        if score > 70:
            reasons.append("Score alto baseado em análise abrangente")
        elif score < 30:
            reasons.append("Score baixo indica riscos elevados")
        
        if sector_perf['trades'] > 0:
            if sector_perf['average_return'] > 5:
                reasons.append(f"Setor com performance positiva ({sector_perf['average_return']:.1f}%)")
            elif sector_perf['average_return'] < -5:
                reasons.append(f"Setor com performance negativa ({sector_perf['average_return']:.1f}%)")
        
        if len(errors) > 0:
            reasons.append(f"{len(errors)} erro(s) recente(s) identificado(s)")
        
        market_condition = self.market_analyzer.market_condition
        reasons.append(f"Mercado em condição de {market_condition.value}")
        
        return "; ".join(reasons)
    
    def save_state(self, filename: str = 'magnus_advanced_state.json'):
        """Salva estado completo do sistema."""
        state = {
            "positions": [asdict(p) for p in self.performance_tracker.positions],
            "performance_history": [asdict(r) for r in self.performance_tracker.performance_history],
            "error_log": self.error_log,
            "learning_insights": self.learning_insights,
            "market_condition": self.market_analyzer.market_condition.value,
            "strategy_mode": self.strategy_adjuster.current_mode.value,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def load_state(self, filename: str = 'magnus_advanced_state.json') -> bool:
        """Carrega estado do sistema."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Carregar posições
            self.performance_tracker.positions = [
                Position(**p) for p in state.get('positions', [])
            ]
            
            # Carregar histórico
            self.performance_tracker.performance_history = [
                PerformanceRecord(**r) for r in state.get('performance_history', [])
            ]
            
            # Carregar logs e insights
            self.error_log = state.get('error_log', [])
            self.learning_insights = state.get('learning_insights', [])
            
            # Carregar condições
            self.market_analyzer.market_condition = MarketCondition(
                state.get('market_condition', 'lateral')
            )
            self.strategy_adjuster.current_mode = StrategyMode(
                state.get('strategy_mode', 'moderado')
            )
            
            return True
        except FileNotFoundError:
            return False

