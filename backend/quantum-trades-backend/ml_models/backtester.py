#!/usr/bin/env python3
"""
Magnus Wealth - Backtester
Sistema de backtesting para validação de estratégias
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class Backtester:
    """
    Sistema de backtesting para estratégias de trading
    """
    
    def __init__(self, initial_capital: float = 10000.0, results_dir='data/backtests'):
        """
        Inicializa o backtester
        
        Args:
            initial_capital: Capital inicial
            results_dir: Diretório para salvar resultados
        """
        self.initial_capital = initial_capital
        self.results_dir = results_dir
        
        # Criar diretório de resultados
        os.makedirs(results_dir, exist_ok=True)
    
    def calculate_returns(self, prices: List[float]) -> List[float]:
        """
        Calcula retornos diários
        
        Args:
            prices: Lista de preços
            
        Returns:
            Lista de retornos
        """
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        return returns
    
    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.0
    ) -> float:
        """
        Calcula Sharpe Ratio
        
        Args:
            returns: Lista de retornos
            risk_free_rate: Taxa livre de risco
            
        Returns:
            Sharpe Ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        
        # Retorno médio
        mean_return = np.mean(returns_array)
        
        # Volatilidade
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        # Sharpe Ratio (anualizado)
        sharpe = (mean_return - risk_free_rate) / std_return * np.sqrt(252)
        
        return float(sharpe)
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Tuple[float, int, int]:
        """
        Calcula Maximum Drawdown
        
        Args:
            equity_curve: Curva de capital
            
        Returns:
            Tupla (max_drawdown, start_idx, end_idx)
        """
        if not equity_curve:
            return 0.0, 0, 0
        
        equity_array = np.array(equity_curve)
        
        # Calcular peak (máximo acumulado)
        peak = np.maximum.accumulate(equity_array)
        
        # Calcular drawdown
        drawdown = (equity_array - peak) / peak
        
        # Encontrar máximo drawdown
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        
        # Encontrar início do drawdown
        start_idx = np.argmax(peak[:max_dd_idx+1])
        
        return float(max_dd * 100), int(start_idx), int(max_dd_idx)
    
    def backtest_buy_and_hold(
        self,
        ticker: str,
        prices: List[float],
        dates: Optional[List[str]] = None
    ) -> Dict:
        """
        Backtesting de estratégia Buy and Hold
        
        Args:
            ticker: Ticker do ativo
            prices: Lista de preços
            dates: Lista de datas (opcional)
            
        Returns:
            Resultados do backtest
        """
        if not prices or len(prices) < 2:
            raise ValueError("Necessário pelo menos 2 preços")
        
        # Calcular número de ações que podem ser compradas
        shares = self.initial_capital / prices[0]
        
        # Calcular valor do portfólio ao longo do tempo
        equity_curve = [price * shares for price in prices]
        
        # Calcular retornos
        returns = self.calculate_returns(equity_curve)
        
        # Calcular métricas
        final_capital = equity_curve[-1]
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        max_dd, dd_start, dd_end = self.calculate_max_drawdown(equity_curve)
        
        # Preparar resultado
        result = {
            'strategy': 'buy_and_hold',
            'ticker': ticker,
            'period': {
                'start': dates[0] if dates else 'N/A',
                'end': dates[-1] if dates else 'N/A',
                'days': len(prices)
            },
            'capital': {
                'initial': round(self.initial_capital, 2),
                'final': round(final_capital, 2),
                'peak': round(max(equity_curve), 2)
            },
            'metrics': {
                'total_return': round(total_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_dd, 2),
                'volatility': round(np.std(returns) * np.sqrt(252) * 100, 2) if returns else 0
            },
            'equity_curve': [round(e, 2) for e in equity_curve],
            'executed_at': datetime.now().isoformat()
        }
        
        return result
    
    def backtest_portfolio(
        self,
        allocations: Dict[str, float],
        prices_history: Dict[str, List[float]],
        dates: Optional[List[str]] = None
    ) -> Dict:
        """
        Backtesting de portfólio com múltiplos ativos
        
        Args:
            allocations: Dicionário {ticker: peso}
            prices_history: Dicionário {ticker: [preços]}
            dates: Lista de datas (opcional)
            
        Returns:
            Resultados do backtest
        """
        # Validar alocações
        total_weight = sum(allocations.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Soma dos pesos deve ser 1.0, obtido: {total_weight}")
        
        # Encontrar tamanho mínimo
        min_length = min(len(prices) for prices in prices_history.values())
        
        # Calcular capital alocado para cada ativo
        portfolio_values = []
        
        for i in range(min_length):
            total_value = 0
            
            for ticker, weight in allocations.items():
                if ticker not in prices_history:
                    continue
                
                # Capital alocado para este ativo
                allocated_capital = self.initial_capital * weight
                
                # Preço no dia i
                price = prices_history[ticker][i]
                
                # Número de ações
                shares = allocated_capital / prices_history[ticker][0]
                
                # Valor atual
                value = shares * price
                
                total_value += value
            
            portfolio_values.append(total_value)
        
        # Calcular retornos
        returns = self.calculate_returns(portfolio_values)
        
        # Calcular métricas
        final_capital = portfolio_values[-1]
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        max_dd, dd_start, dd_end = self.calculate_max_drawdown(portfolio_values)
        
        # Preparar resultado
        result = {
            'strategy': 'portfolio',
            'allocations': allocations,
            'period': {
                'start': dates[0] if dates else 'N/A',
                'end': dates[min_length-1] if dates else 'N/A',
                'days': min_length
            },
            'capital': {
                'initial': round(self.initial_capital, 2),
                'final': round(final_capital, 2),
                'peak': round(max(portfolio_values), 2)
            },
            'metrics': {
                'total_return': round(total_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_dd, 2),
                'volatility': round(np.std(returns) * np.sqrt(252) * 100, 2) if returns else 0
            },
            'equity_curve': [round(v, 2) for v in portfolio_values],
            'executed_at': datetime.now().isoformat()
        }
        
        return result
    
    def compare_with_benchmark(
        self,
        strategy_result: Dict,
        benchmark_prices: List[float],
        benchmark_name: str = 'Benchmark'
    ) -> Dict:
        """
        Compara estratégia com benchmark
        
        Args:
            strategy_result: Resultado da estratégia
            benchmark_prices: Preços do benchmark
            benchmark_name: Nome do benchmark
            
        Returns:
            Comparação
        """
        # Backtest do benchmark
        benchmark_shares = self.initial_capital / benchmark_prices[0]
        benchmark_curve = [price * benchmark_shares for price in benchmark_prices]
        
        benchmark_returns = self.calculate_returns(benchmark_curve)
        benchmark_final = benchmark_curve[-1]
        benchmark_return = ((benchmark_final - self.initial_capital) / self.initial_capital) * 100
        
        # Comparação
        comparison = {
            'strategy': {
                'name': strategy_result['strategy'],
                'return': strategy_result['metrics']['total_return'],
                'sharpe': strategy_result['metrics']['sharpe_ratio'],
                'max_dd': strategy_result['metrics']['max_drawdown']
            },
            'benchmark': {
                'name': benchmark_name,
                'return': round(benchmark_return, 2),
                'sharpe': round(self.calculate_sharpe_ratio(benchmark_returns), 2),
                'max_dd': round(self.calculate_max_drawdown(benchmark_curve)[0], 2)
            },
            'outperformance': {
                'return': round(strategy_result['metrics']['total_return'] - benchmark_return, 2),
                'sharpe': round(strategy_result['metrics']['sharpe_ratio'] - self.calculate_sharpe_ratio(benchmark_returns), 2)
            }
        }
        
        return comparison
    
    def save_result(self, result: Dict, filename: Optional[str] = None) -> str:
        """
        Salva resultado do backtest
        
        Args:
            result: Resultado do backtest
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo salvo
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            strategy = result.get('strategy', 'unknown')
            filename = f'{strategy}_{timestamp}.json'
        
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        return filepath


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do backtester"""
    
    backtester = Backtester(initial_capital=10000)
    
    print("=" * 60)
    print("TESTE DO SISTEMA DE BACKTESTING")
    print("=" * 60)
    
    # Gerar dados sintéticos
    np.random.seed(42)
    
    # Ativo 1: Tendência de alta
    prices1 = [30 + i * 0.1 + np.random.normal(0, 0.5) for i in range(252)]
    
    # Ativo 2: Lateral
    prices2 = [50 + np.random.normal(0, 1) for i in range(252)]
    
    # Teste 1: Buy and Hold
    print("\n1. Backtesting Buy and Hold (Ativo 1):")
    result = backtester.backtest_buy_and_hold('TEST1', prices1)
    
    print(f"   Capital inicial: R$ {result['capital']['initial']:.2f}")
    print(f"   Capital final: R$ {result['capital']['final']:.2f}")
    print(f"   Retorno total: {result['metrics']['total_return']:.2f}%")
    print(f"   Sharpe Ratio: {result['metrics']['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {result['metrics']['max_drawdown']:.2f}%")
    print(f"   Volatilidade: {result['metrics']['volatility']:.2f}%")
    
    # Teste 2: Portfólio
    print("\n2. Backtesting de Portfólio:")
    allocations = {
        'TEST1': 0.6,
        'TEST2': 0.4
    }
    prices_history = {
        'TEST1': prices1,
        'TEST2': prices2
    }
    
    result_portfolio = backtester.backtest_portfolio(allocations, prices_history)
    
    print(f"   Alocação: TEST1 60%, TEST2 40%")
    print(f"   Capital inicial: R$ {result_portfolio['capital']['initial']:.2f}")
    print(f"   Capital final: R$ {result_portfolio['capital']['final']:.2f}")
    print(f"   Retorno total: {result_portfolio['metrics']['total_return']:.2f}%")
    print(f"   Sharpe Ratio: {result_portfolio['metrics']['sharpe_ratio']:.2f}")
    
    # Teste 3: Comparação com benchmark
    print("\n3. Comparação com Benchmark:")
    comparison = backtester.compare_with_benchmark(result, prices2, 'Benchmark')
    
    print(f"   Estratégia: {comparison['strategy']['return']:.2f}%")
    print(f"   Benchmark: {comparison['benchmark']['return']:.2f}%")
    print(f"   Outperformance: {comparison['outperformance']['return']:.2f}%")
    
    # Teste 4: Salvar resultado
    print("\n4. Salvando resultado:")
    filepath = backtester.save_result(result)
    print(f"   ✅ Salvo em: {filepath}")
    print(f"   Tamanho: {os.path.getsize(filepath) / 1024:.1f} KB")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

