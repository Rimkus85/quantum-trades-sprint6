#!/usr/bin/env python3
"""
Magnus Wealth - Portfolio Optimizer
Otimizador de portfólio usando Teoria Moderna de Portfólio (Markowitz)
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class PortfolioOptimizer:
    """
    Otimizador de portfólio usando Modern Portfolio Theory (MPT)
    """
    
    def __init__(self):
        """Inicializa o otimizador"""
        self.returns = {}
        self.volatilities = {}
        self.covariance_matrix = None
        self.tickers = []
    
    def calculate_returns(self, prices_history: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calcula retornos esperados de cada ativo
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            
        Returns:
            Dicionário {ticker: retorno_esperado}
        """
        returns = {}
        
        for ticker, prices in prices_history.items():
            if len(prices) < 2:
                returns[ticker] = 0.0
                continue
            
            prices_array = np.array(prices)
            
            # Calcular retornos diários
            daily_returns = np.diff(prices_array) / prices_array[:-1]
            
            # Retorno médio (anualizado)
            mean_return = np.mean(daily_returns) * 252  # 252 dias úteis
            
            returns[ticker] = float(mean_return)
        
        self.returns = returns
        return returns
    
    def calculate_volatility(self, prices_history: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Calcula volatilidade (risco) de cada ativo
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            
        Returns:
            Dicionário {ticker: volatilidade}
        """
        volatilities = {}
        
        for ticker, prices in prices_history.items():
            if len(prices) < 2:
                volatilities[ticker] = 0.0
                continue
            
            prices_array = np.array(prices)
            
            # Calcular retornos diários
            daily_returns = np.diff(prices_array) / prices_array[:-1]
            
            # Volatilidade (desvio padrão anualizado)
            volatility = np.std(daily_returns) * np.sqrt(252)
            
            volatilities[ticker] = float(volatility)
        
        self.volatilities = volatilities
        return volatilities
    
    def calculate_covariance_matrix(self, prices_history: Dict[str, List[float]]) -> np.ndarray:
        """
        Calcula matriz de covariância entre ativos
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            
        Returns:
            Matriz de covariância
        """
        self.tickers = list(prices_history.keys())
        n_assets = len(self.tickers)
        
        # Calcular retornos diários de todos os ativos
        returns_matrix = []
        
        for ticker in self.tickers:
            prices = np.array(prices_history[ticker])
            daily_returns = np.diff(prices) / prices[:-1]
            returns_matrix.append(daily_returns)
        
        # Garantir que todos tenham o mesmo tamanho
        min_length = min(len(r) for r in returns_matrix)
        returns_matrix = [r[-min_length:] for r in returns_matrix]
        
        # Converter para array numpy
        returns_matrix = np.array(returns_matrix)
        
        # Calcular matriz de covariância
        cov_matrix = np.cov(returns_matrix) * 252  # Anualizar
        
        self.covariance_matrix = cov_matrix
        return cov_matrix
    
    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calcula métricas do portfólio
        
        Args:
            weights: Pesos dos ativos
            
        Returns:
            Tupla (retorno, volatilidade, sharpe_ratio)
        """
        # Retorno do portfólio
        portfolio_return = sum(
            weights[i] * self.returns[self.tickers[i]]
            for i in range(len(self.tickers))
        )
        
        # Volatilidade do portfólio
        portfolio_variance = sum(
            sum(
                weights[i] * weights[j] * self.covariance_matrix[i][j]
                for j in range(len(self.tickers))
            )
            for i in range(len(self.tickers))
        )
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Sharpe Ratio (assumindo taxa livre de risco = 0)
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def optimize_sharpe_ratio(
        self,
        prices_history: Dict[str, List[float]],
        risk_tolerance: str = 'moderate',
        min_weight: float = 0.0,
        max_weight: float = 1.0
    ) -> Dict:
        """
        Otimiza portfólio para maximizar Sharpe Ratio
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            risk_tolerance: Tolerância ao risco ('conservative', 'moderate', 'aggressive')
            min_weight: Peso mínimo por ativo
            max_weight: Peso máximo por ativo
            
        Returns:
            Dicionário com portfólio otimizado
        """
        # Calcular métricas
        self.calculate_returns(prices_history)
        self.calculate_volatility(prices_history)
        self.calculate_covariance_matrix(prices_history)
        
        n_assets = len(self.tickers)
        
        # Ajustar limites baseado na tolerância ao risco
        if risk_tolerance == 'conservative':
            # Portfólio mais diversificado
            max_weight = min(max_weight, 0.30)  # Máximo 30% em um ativo
        elif risk_tolerance == 'aggressive':
            # Permite concentração maior
            max_weight = min(max_weight, 0.60)  # Máximo 60% em um ativo
        else:  # moderate
            max_weight = min(max_weight, 0.40)  # Máximo 40% em um ativo
        
        # Função objetivo: maximizar Sharpe Ratio (minimizar negativo)
        def negative_sharpe(weights):
            _, _, sharpe = self.calculate_portfolio_metrics(weights)
            return -sharpe
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: sum(w) - 1}  # Soma dos pesos = 100%
        ]
        
        # Limites
        bounds = [(min_weight, max_weight) for _ in range(n_assets)]
        
        # Chute inicial (pesos iguais)
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Otimizar
        result = minimize(
            negative_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if not result.success:
            # Se falhar, usar pesos iguais
            optimal_weights = initial_weights
        else:
            optimal_weights = result.x
        
        # Calcular métricas do portfólio otimizado
        portfolio_return, portfolio_volatility, sharpe_ratio = \
            self.calculate_portfolio_metrics(optimal_weights)
        
        # Preparar resultado
        allocations = []
        for i, ticker in enumerate(self.tickers):
            weight = optimal_weights[i]
            if weight > 0.01:  # Só incluir se > 1%
                allocations.append({
                    'ticker': ticker,
                    'weight': round(float(weight * 100), 2),  # Percentual
                    'expected_return': round(self.returns[ticker] * 100, 2),  # Percentual
                    'volatility': round(self.volatilities[ticker] * 100, 2)  # Percentual
                })
        
        # Ordenar por peso (maior primeiro)
        allocations.sort(key=lambda x: x['weight'], reverse=True)
        
        return {
            'tickers': self.tickers,
            'allocations': allocations,
            'portfolio_metrics': {
                'expected_return': round(portfolio_return * 100, 2),  # Percentual anual
                'volatility': round(portfolio_volatility * 100, 2),  # Percentual anual
                'sharpe_ratio': round(sharpe_ratio, 2)
            },
            'risk_tolerance': risk_tolerance,
            'optimization_status': 'success' if result.success else 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_min_volatility(
        self,
        prices_history: Dict[str, List[float]],
        target_return: Optional[float] = None
    ) -> Dict:
        """
        Otimiza portfólio para minimizar volatilidade
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            target_return: Retorno alvo (opcional)
            
        Returns:
            Dicionário com portfólio otimizado
        """
        # Calcular métricas
        self.calculate_returns(prices_history)
        self.calculate_volatility(prices_history)
        self.calculate_covariance_matrix(prices_history)
        
        n_assets = len(self.tickers)
        
        # Função objetivo: minimizar volatilidade
        def portfolio_volatility(weights):
            _, volatility, _ = self.calculate_portfolio_metrics(weights)
            return volatility
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: sum(w) - 1}  # Soma = 100%
        ]
        
        # Se houver retorno alvo, adicionar restrição
        if target_return is not None:
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: sum(w[i] * self.returns[self.tickers[i]] for i in range(n_assets)) - target_return
            })
        
        # Limites
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Chute inicial
        initial_weights = np.array([1/n_assets] * n_assets)
        
        # Otimizar
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        if not result.success:
            optimal_weights = initial_weights
        else:
            optimal_weights = result.x
        
        # Calcular métricas
        portfolio_return, portfolio_volatility, sharpe_ratio = \
            self.calculate_portfolio_metrics(optimal_weights)
        
        # Preparar resultado
        allocations = []
        for i, ticker in enumerate(self.tickers):
            weight = optimal_weights[i]
            if weight > 0.01:
                allocations.append({
                    'ticker': ticker,
                    'weight': round(float(weight * 100), 2),
                    'expected_return': round(self.returns[ticker] * 100, 2),
                    'volatility': round(self.volatilities[ticker] * 100, 2)
                })
        
        allocations.sort(key=lambda x: x['weight'], reverse=True)
        
        return {
            'tickers': self.tickers,
            'allocations': allocations,
            'portfolio_metrics': {
                'expected_return': round(portfolio_return * 100, 2),
                'volatility': round(portfolio_volatility * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 2)
            },
            'optimization_type': 'minimum_volatility',
            'target_return': target_return,
            'optimization_status': 'success' if result.success else 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_efficient_frontier(
        self,
        prices_history: Dict[str, List[float]],
        n_points: int = 20
    ) -> List[Dict]:
        """
        Gera fronteira eficiente
        
        Args:
            prices_history: Dicionário {ticker: [preços]}
            n_points: Número de pontos na fronteira
            
        Returns:
            Lista de portfólios na fronteira eficiente
        """
        # Calcular métricas
        self.calculate_returns(prices_history)
        self.calculate_volatility(prices_history)
        self.calculate_covariance_matrix(prices_history)
        
        # Determinar range de retornos
        min_return = min(self.returns.values())
        max_return = max(self.returns.values())
        
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier = []
        
        for target_return in target_returns:
            try:
                result = self.optimize_min_volatility(prices_history, target_return)
                frontier.append({
                    'return': result['portfolio_metrics']['expected_return'],
                    'volatility': result['portfolio_metrics']['volatility'],
                    'sharpe_ratio': result['portfolio_metrics']['sharpe_ratio']
                })
            except:
                continue
        
        return frontier


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do otimizador de portfólio"""
    
    optimizer = PortfolioOptimizer()
    
    print("=" * 60)
    print("TESTE DO OTIMIZADOR DE PORTFÓLIO")
    print("=" * 60)
    
    # Gerar dados sintéticos para 3 ativos
    np.random.seed(42)
    
    # Ativo 1: Alto retorno, alta volatilidade
    prices1 = [30 + i * 0.1 + np.random.normal(0, 1) for i in range(60)]
    
    # Ativo 2: Médio retorno, média volatilidade
    prices2 = [50 + i * 0.05 + np.random.normal(0, 0.5) for i in range(60)]
    
    # Ativo 3: Baixo retorno, baixa volatilidade
    prices3 = [25 + i * 0.02 + np.random.normal(0, 0.2) for i in range(60)]
    
    prices_history = {
        'PETR4': prices1,
        'VALE3': prices2,
        'ITUB4': prices3
    }
    
    print("\n1. Dados Sintéticos:")
    for ticker, prices in prices_history.items():
        variation = ((prices[-1] - prices[0]) / prices[0]) * 100
        print(f"   {ticker}: R$ {prices[0]:.2f} → R$ {prices[-1]:.2f} ({variation:+.2f}%)")
    
    # Calcular métricas individuais
    print("\n2. Métricas Individuais:")
    returns = optimizer.calculate_returns(prices_history)
    volatilities = optimizer.calculate_volatility(prices_history)
    
    for ticker in prices_history.keys():
        print(f"   {ticker}:")
        print(f"     Retorno esperado: {returns[ticker]*100:.2f}% ao ano")
        print(f"     Volatilidade: {volatilities[ticker]*100:.2f}% ao ano")
    
    # Otimizar portfólio (Sharpe Ratio)
    print("\n3. Portfólio Otimizado (Máximo Sharpe Ratio):")
    result = optimizer.optimize_sharpe_ratio(prices_history, risk_tolerance='moderate')
    
    print(f"   Status: {result['optimization_status']}")
    print(f"   Alocação:")
    for allocation in result['allocations']:
        print(f"     {allocation['ticker']}: {allocation['weight']:.2f}%")
    
    print(f"\n   Métricas do Portfólio:")
    metrics = result['portfolio_metrics']
    print(f"     Retorno esperado: {metrics['expected_return']:.2f}% ao ano")
    print(f"     Volatilidade: {metrics['volatility']:.2f}% ao ano")
    print(f"     Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    # Otimizar para mínima volatilidade
    print("\n4. Portfólio de Mínima Volatilidade:")
    result_min_vol = optimizer.optimize_min_volatility(prices_history)
    
    print(f"   Alocação:")
    for allocation in result_min_vol['allocations']:
        print(f"     {allocation['ticker']}: {allocation['weight']:.2f}%")
    
    print(f"\n   Métricas do Portfólio:")
    metrics = result_min_vol['portfolio_metrics']
    print(f"     Retorno esperado: {metrics['expected_return']:.2f}% ao ano")
    print(f"     Volatilidade: {metrics['volatility']:.2f}% ao ano")
    print(f"     Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

