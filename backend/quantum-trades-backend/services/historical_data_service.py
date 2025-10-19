#!/usr/bin/env python3
"""
Magnus Wealth - Historical Data Service
Serviço para coleta e cache de dados históricos de ações
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class HistoricalDataService:
    """
    Serviço para buscar e armazenar dados históricos de ações
    """
    
    def __init__(self, cache_dir='data/historical'):
        """
        Inicializa o serviço
        
        Args:
            cache_dir: Diretório para cache de dados
        """
        self.cache_dir = cache_dir
        self.base_url = 'https://brapi.dev/api'
        
        # Criar diretório de cache
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_path(self, ticker: str, period: str) -> str:
        """Retorna caminho do arquivo de cache"""
        return os.path.join(self.cache_dir, f'{ticker}_{period}.json')
    
    def is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """
        Verifica se o cache ainda é válido
        
        Args:
            cache_path: Caminho do arquivo de cache
            max_age_hours: Idade máxima em horas
            
        Returns:
            True se o cache é válido
        """
        if not os.path.exists(cache_path):
            return False
        
        # Verificar idade do arquivo
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        
        return age.total_seconds() < (max_age_hours * 3600)
    
    def load_from_cache(self, ticker: str, period: str) -> Optional[Dict]:
        """
        Carrega dados do cache
        
        Args:
            ticker: Ticker do ativo
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dados históricos ou None
        """
        cache_path = self.get_cache_path(ticker, period)
        
        if not self.is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            return None
    
    def save_to_cache(self, ticker: str, period: str, data: Dict):
        """
        Salva dados no cache
        
        Args:
            ticker: Ticker do ativo
            period: Período
            data: Dados a serem salvos
        """
        cache_path = self.get_cache_path(ticker, period)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def fetch_from_api(self, ticker: str, period: str = '1y') -> Optional[Dict]:
        """
        Busca dados da API brapi.dev
        
        Args:
            ticker: Ticker do ativo (ex: PETR4)
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Dados históricos ou None
        """
        try:
            url = f'{self.base_url}/quote/{ticker}?range={period}&interval=1d'
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar se há resultados
            if 'results' not in data or not data['results']:
                return None
            
            result = data['results'][0]
            
            # Verificar se há dados históricos
            if 'historicalDataPrice' not in result:
                return None
            
            # Formatar dados
            formatted_data = {
                'ticker': ticker,
                'period': period,
                'fetched_at': datetime.now().isoformat(),
                'data': []
            }
            
            for item in result['historicalDataPrice']:
                formatted_data['data'].append({
                    'date': datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d'),
                    'open': item.get('open'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'close': item.get('close'),
                    'volume': item.get('volume')
                })
            
            # Ordenar por data (mais antigo primeiro)
            formatted_data['data'].sort(key=lambda x: x['date'])
            
            return formatted_data
        
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados da API: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return None
    
    def get_historical_data(
        self,
        ticker: str,
        period: str = '1y',
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Busca dados históricos (cache ou API)
        
        Args:
            ticker: Ticker do ativo
            period: Período
            use_cache: Se deve usar cache
            
        Returns:
            Dados históricos ou None
        """
        ticker = ticker.upper()
        
        # Tentar carregar do cache
        if use_cache:
            cached_data = self.load_from_cache(ticker, period)
            if cached_data:
                return cached_data
        
        # Buscar da API
        data = self.fetch_from_api(ticker, period)
        
        # Salvar no cache
        if data:
            self.save_to_cache(ticker, period, data)
        
        return data
    
    def get_prices_only(
        self,
        ticker: str,
        period: str = '1y',
        use_cache: bool = True
    ) -> Optional[List[float]]:
        """
        Retorna apenas os preços de fechamento
        
        Args:
            ticker: Ticker do ativo
            period: Período
            use_cache: Se deve usar cache
            
        Returns:
            Lista de preços ou None
        """
        data = self.get_historical_data(ticker, period, use_cache)
        
        if not data or 'data' not in data:
            return None
        
        prices = [item['close'] for item in data['data'] if item['close'] is not None]
        
        return prices if prices else None
    
    def get_multiple_tickers(
        self,
        tickers: List[str],
        period: str = '1y',
        use_cache: bool = True
    ) -> Dict[str, Dict]:
        """
        Busca dados de múltiplos tickers
        
        Args:
            tickers: Lista de tickers
            period: Período
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário {ticker: dados}
        """
        results = {}
        
        for ticker in tickers:
            data = self.get_historical_data(ticker, period, use_cache)
            if data:
                results[ticker.upper()] = data
        
        return results
    
    def clear_cache(self, ticker: Optional[str] = None):
        """
        Limpa o cache
        
        Args:
            ticker: Ticker específico ou None para limpar tudo
        """
        if ticker:
            # Limpar cache de um ticker específico
            for filename in os.listdir(self.cache_dir):
                if filename.startswith(ticker.upper()):
                    os.remove(os.path.join(self.cache_dir, filename))
        else:
            # Limpar todo o cache
            for filename in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, filename))


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do serviço de dados históricos"""
    
    service = HistoricalDataService()
    
    print("=" * 60)
    print("TESTE DO SERVIÇO DE DADOS HISTÓRICOS")
    print("=" * 60)
    
    # Teste 1: Buscar dados de um ticker
    print("\n1. Buscando dados de PETR4 (1 ano):")
    data = service.get_historical_data('PETR4', period='1y', use_cache=False)
    
    if data:
        print(f"   ✅ Dados obtidos com sucesso")
        print(f"   Ticker: {data['ticker']}")
        print(f"   Período: {data['period']}")
        print(f"   Total de dias: {len(data['data'])}")
        print(f"   Primeiro dia: {data['data'][0]['date']}")
        print(f"   Último dia: {data['data'][-1]['date']}")
        print(f"   Preço inicial: R$ {data['data'][0]['close']:.2f}")
        print(f"   Preço final: R$ {data['data'][-1]['close']:.2f}")
    else:
        print("   ❌ Erro ao buscar dados")
    
    # Teste 2: Buscar apenas preços
    print("\n2. Buscando apenas preços de VALE3:")
    prices = service.get_prices_only('VALE3', period='6mo')
    
    if prices:
        print(f"   ✅ Preços obtidos")
        print(f"   Total: {len(prices)} dias")
        print(f"   Mínimo: R$ {min(prices):.2f}")
        print(f"   Máximo: R$ {max(prices):.2f}")
        print(f"   Médio: R$ {sum(prices)/len(prices):.2f}")
    else:
        print("   ❌ Erro ao buscar preços")
    
    # Teste 3: Buscar múltiplos tickers
    print("\n3. Buscando múltiplos tickers:")
    tickers = ['ITUB4', 'BBDC4']
    results = service.get_multiple_tickers(tickers, period='3mo')
    
    print(f"   Total de tickers: {len(results)}")
    for ticker, data in results.items():
        print(f"   {ticker}: {len(data['data'])} dias")
    
    # Teste 4: Verificar cache
    print("\n4. Testando cache:")
    cache_path = service.get_cache_path('PETR4', '1y')
    if os.path.exists(cache_path):
        print(f"   ✅ Cache criado: {cache_path}")
        print(f"   Tamanho: {os.path.getsize(cache_path) / 1024:.1f} KB")
    else:
        print("   ❌ Cache não criado")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

