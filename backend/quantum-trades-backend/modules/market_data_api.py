#!/usr/bin/env python3
"""
Integração com APIs de dados de mercado.
Fornece cotações, indicadores e dados fundamentalistas em tempo real.
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class MarketDataAPI:
    """Cliente para APIs de dados de mercado."""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutos
    
    def get_quote(self, ticker: str) -> Dict:
        """
        Obtém cotação atual de um ticker.
        
        Args:
            ticker: Código do ticker (ex: PETR4)
            
        Returns:
            Dados de cotação
        """
        # Verificar cache
        cache_key = f"quote_{ticker}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        # Aqui seria integrado com API real (ex: Alpha Vantage, Yahoo Finance, B3)
        # Por enquanto, retorna dados simulados
        data = self._get_simulated_quote(ticker)
        
        # Armazenar em cache
        self._cache_data(cache_key, data)
        
        return data
    
    def get_historical_data(self, ticker: str, days: int = 30) -> List[Dict]:
        """
        Obtém dados históricos de um ticker.
        
        Args:
            ticker: Código do ticker
            days: Número de dias de histórico
            
        Returns:
            Lista de dados históricos
        """
        cache_key = f"historical_{ticker}_{days}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        data = self._get_simulated_historical(ticker, days)
        self._cache_data(cache_key, data)
        
        return data
    
    def get_market_indicators(self) -> Dict:
        """
        Obtém indicadores de mercado (Ibovespa, dólar, etc).
        
        Returns:
            Indicadores de mercado
        """
        cache_key = "market_indicators"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        data = {
            "ibovespa": {
                "value": 125000,
                "change": 1.5,
                "change_30d": 5.2,
                "volatility": 15.3
            },
            "dolar": {
                "value": 5.15,
                "change": -0.3,
                "change_30d": -2.1
            },
            "selic": {
                "value": 11.75,
                "last_update": "2025-10-15"
            },
            "inflation_ipca": {
                "value": 4.5,
                "period": "12 meses"
            }
        }
        
        self._cache_data(cache_key, data)
        return data
    
    def get_sector_data(self, sector: str) -> Dict:
        """
        Obtém dados de um setor específico.
        
        Args:
            sector: Nome do setor
            
        Returns:
            Dados do setor
        """
        cache_key = f"sector_{sector}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        # Dados simulados por setor
        sector_data = {
            "financeiro": {
                "trend": "alta",
                "performance_30d": 8.5,
                "outlook": "positivo",
                "risks": ["Aumento de inadimplência", "Regulação"],
                "opportunities": ["Expansão de crédito", "Digitalização"]
            },
            "petroleo": {
                "trend": "alta",
                "performance_30d": 12.3,
                "outlook": "positivo",
                "risks": ["Volatilidade do petróleo", "Transição energética"],
                "opportunities": ["Preço do barril elevado", "Pré-sal"]
            },
            "tecnologia": {
                "trend": "alta",
                "performance_30d": 15.7,
                "outlook": "muito_positivo",
                "risks": ["Concorrência global", "Regulação"],
                "opportunities": ["Transformação digital", "IA", "Cloud"]
            },
            "agronegocio": {
                "trend": "lateral",
                "performance_30d": 2.1,
                "outlook": "neutro",
                "risks": ["Clima", "Preços de commodities"],
                "opportunities": ["Demanda global", "Automação"]
            },
            "varejo": {
                "trend": "baixa",
                "performance_30d": -3.5,
                "outlook": "negativo",
                "risks": ["Juros altos", "Endividamento"],
                "opportunities": ["E-commerce", "Recuperação econômica"]
            },
            "fiis": {
                "trend": "baixa",
                "performance_30d": -8.2,
                "outlook": "negativo",
                "risks": ["Juros altos", "Vacância"],
                "opportunities": ["Yields atrativos", "Diversificação"]
            }
        }
        
        data = sector_data.get(sector.lower(), {
            "trend": "neutro",
            "performance_30d": 0,
            "outlook": "neutro",
            "risks": [],
            "opportunities": []
        })
        
        self._cache_data(cache_key, data)
        return data
    
    def get_company_fundamentals(self, ticker: str) -> Dict:
        """
        Obtém dados fundamentalistas de uma empresa.
        
        Args:
            ticker: Código do ticker
            
        Returns:
            Dados fundamentalistas
        """
        cache_key = f"fundamentals_{ticker}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        # Dados simulados
        data = {
            "ticker": ticker,
            "company_name": f"Empresa {ticker}",
            "sector": self._get_sector_for_ticker(ticker),
            "market_cap": 50000000000,
            "pe_ratio": 12.5,
            "dividend_yield": 4.2,
            "roe": 18.5,
            "debt_equity": 0.45,
            "revenue_growth": 8.3,
            "profit_margin": 15.2,
            "last_earnings": {
                "date": "2025-08-15",
                "eps": 2.35,
                "revenue": 5000000000,
                "profit": 760000000
            }
        }
        
        self._cache_data(cache_key, data)
        return data
    
    def _get_simulated_quote(self, ticker: str) -> Dict:
        """Gera cotação simulada."""
        import random
        
        base_prices = {
            "PETR4": 38.50,
            "VALE3": 65.20,
            "ITUB4": 28.75,
            "BBDC4": 14.30,
            "WEGE3": 42.10,
            "MGLU3": 3.85,
            "ABEV3": 12.45,
            "B3SA3": 11.90
        }
        
        base_price = base_prices.get(ticker, 25.00)
        variation = random.uniform(-0.03, 0.03)
        current_price = base_price * (1 + variation)
        
        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "change": round(variation * 100, 2),
            "volume": random.randint(10000000, 50000000),
            "high": round(current_price * 1.02, 2),
            "low": round(current_price * 0.98, 2),
            "open": round(base_price, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_simulated_historical(self, ticker: str, days: int) -> List[Dict]:
        """Gera histórico simulado."""
        import random
        
        data = []
        base_price = self.get_quote(ticker)['price']
        
        for i in range(days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            variation = random.uniform(-0.02, 0.02)
            price = base_price * (1 + variation * i / days)
            
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(price * 0.99, 2),
                "high": round(price * 1.02, 2),
                "low": round(price * 0.98, 2),
                "close": round(price, 2),
                "volume": random.randint(5000000, 30000000)
            })
        
        return data
    
    def _get_sector_for_ticker(self, ticker: str) -> str:
        """Retorna setor de um ticker."""
        sectors = {
            "PETR4": "petroleo",
            "VALE3": "mineracao",
            "ITUB4": "financeiro",
            "BBDC4": "financeiro",
            "WEGE3": "industrial",
            "MGLU3": "varejo",
            "ABEV3": "consumo",
            "B3SA3": "financeiro"
        }
        
        return sectors.get(ticker, "outros")
    
    def _is_cached(self, key: str) -> bool:
        """Verifica se dado está em cache válido."""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        age = (datetime.now() - cached_time).total_seconds()
        
        return age < self.cache_duration
    
    def _cache_data(self, key: str, data: any):
        """Armazena dado em cache."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }


# Instância global
market_api = MarketDataAPI()

