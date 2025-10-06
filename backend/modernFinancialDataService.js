/**
 * 🚀 QUANTUM TRADES - MODERN FINANCIAL DATA SERVICE
 * Serviço que usa o backend Flask para dados financeiros
 */

class ModernFinancialDataService {
  constructor() {
    this.backendApi = window.backendApi;
    
    // Cache local para melhor performance
    this.localCache = new Map();
    this.cacheTimeout = 60000; // 1 minuto
    
    // Métricas
    this.metrics = {
      requests: 0,
      errors: 0,
      cacheHits: 0,
      cacheMisses: 0
    };
    
    console.log('[ModernFinancialDataService] Initialized with backend API');
  }

  /**
   * Obter dados do cache local
   */
  _getFromCache(key) {
    const cached = this.localCache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      this.metrics.cacheHits++;
      return cached.data;
    }
    this.metrics.cacheMisses++;
    return null;
  }

  /**
   * Salvar dados no cache local
   */
  _setCache(key, data) {
    this.localCache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Obter preço de uma ação
   */
  async getStockPrice(symbol, options = {}) {
    this.metrics.requests++;
    
    const cacheKey = `stock_price_${symbol}`;
    
    // Verificar cache local primeiro
    if (!options.forceRefresh) {
      const cached = this._getFromCache(cacheKey);
      if (cached) {
        return cached;
      }
    }

    try {
      const response = await this.backendApi.getQuote(symbol);
      
      if (response.success && response.data) {
        const stockData = {
          symbol: response.data.symbol,
          price: response.data.price,
          change: response.data.change,
          changePercent: response.data.change_percent,
          volume: response.data.volume,
          currency: response.data.currency || 'BRL',
          timestamp: response.data.timestamp,
          source: response.data.source
        };
        
        this._setCache(cacheKey, stockData);
        return stockData;
      } else {
        throw new Error('Dados não encontrados');
      }
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[ModernFinancialDataService] Error fetching ${symbol}:`, error);
      
      // Retornar dados mockados como fallback
      return this._getMockData(symbol);
    }
  }

  /**
   * Obter dados históricos
   */
  async getHistoricalData(symbol, period = '1y') {
    this.metrics.requests++;
    
    const cacheKey = `historical_${symbol}_${period}`;
    
    // Verificar cache local
    const cached = this._getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const response = await this.backendApi.getHistoricalData(symbol, period);
      
      if (response.success && response.data) {
        const historicalData = {
          symbol: response.data.symbol,
          period: response.data.period,
          data: response.data.data,
          timestamp: response.data.timestamp,
          source: response.data.source
        };
        
        this._setCache(cacheKey, historicalData);
        return historicalData;
      } else {
        throw new Error('Dados históricos não encontrados');
      }
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[ModernFinancialDataService] Error fetching historical data for ${symbol}:`, error);
      
      // Retornar dados mockados como fallback
      return this._getMockHistoricalData(symbol, period);
    }
  }

  /**
   * Buscar símbolos
   */
  async searchStocks(query) {
    this.metrics.requests++;
    
    if (!query || query.length < 2) {
      return [];
    }

    try {
      const response = await this.backendApi.searchSymbols(query);
      
      if (response.success && response.data) {
        return response.data.map(item => ({
          symbol: item.symbol,
          name: item.name,
          exchange: item.exchange,
          type: item.type,
          currency: item.currency
        }));
      } else {
        return [];
      }
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[ModernFinancialDataService] Error searching stocks:`, error);
      return this._getMockSearchResults(query);
    }
  }

  /**
   * Obter resumo do mercado
   */
  async getMarketSummary() {
    this.metrics.requests++;
    
    const cacheKey = 'market_summary';
    
    // Verificar cache local
    const cached = this._getFromCache(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      const response = await this.backendApi.getMarketSummary();
      
      if (response.success && response.data) {
        const summary = {};
        
        for (const [symbol, data] of Object.entries(response.data)) {
          summary[symbol] = {
            symbol: data.symbol,
            price: data.price,
            change: data.change,
            changePercent: data.change_percent,
            volume: data.volume
          };
        }
        
        this._setCache(cacheKey, summary);
        return summary;
      } else {
        throw new Error('Resumo do mercado não disponível');
      }
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[ModernFinancialDataService] Error fetching market summary:`, error);
      return this._getMockMarketSummary();
    }
  }

  /**
   * Obter múltiplas cotações
   */
  async getMultipleStocks(symbols) {
    this.metrics.requests++;
    
    if (!symbols || symbols.length === 0) {
      return {};
    }

    try {
      const response = await this.backendApi.getMultipleQuotes(symbols);
      
      if (response.success && response.data) {
        const result = {};
        
        for (const [symbol, data] of Object.entries(response.data)) {
          result[symbol] = {
            symbol: data.symbol,
            price: data.price,
            change: data.change,
            changePercent: data.change_percent,
            volume: data.volume,
            timestamp: data.timestamp
          };
        }
        
        return result;
      } else {
        throw new Error('Múltiplas cotações não disponíveis');
      }
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[ModernFinancialDataService] Error fetching multiple quotes:`, error);
      
      // Retornar dados mockados para cada símbolo
      const result = {};
      symbols.forEach(symbol => {
        result[symbol] = this._getMockData(symbol);
      });
      return result;
    }
  }

  /**
   * Obter métricas do serviço
   */
  getMetrics() {
    return {
      ...this.metrics,
      cacheSize: this.localCache.size,
      hitRatio: this.metrics.requests > 0 ? 
        (this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses)) : 0
    };
  }

  /**
   * Limpar cache local
   */
  clearCache() {
    this.localCache.clear();
    console.log('[ModernFinancialDataService] Cache cleared');
  }

  // === MÉTODOS DE FALLBACK (DADOS MOCKADOS) ===

  _getMockData(symbol) {
    const basePrice = 100 + (symbol.charCodeAt(0) % 50);
    const change = (Math.random() - 0.5) * 10;
    
    return {
      symbol,
      price: basePrice + change,
      change: change,
      changePercent: (change / basePrice) * 100,
      volume: Math.floor(Math.random() * 1000000),
      currency: 'BRL',
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  _getMockHistoricalData(symbol, period) {
    const data = [];
    const days = period === '1d' ? 1 : period === '1m' ? 30 : 365;
    const basePrice = 100 + (symbol.charCodeAt(0) % 50);
    
    for (let i = days; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      const variation = (Math.random() - 0.5) * 10;
      const price = basePrice + variation;
      
      data.push({
        date: date.toISOString().split('T')[0],
        open: price,
        high: price + Math.random() * 5,
        low: price - Math.random() * 5,
        close: price,
        volume: Math.floor(Math.random() * 1000000)
      });
    }
    
    return {
      symbol,
      period,
      data,
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  _getMockSearchResults(query) {
    const mockSymbols = [
      { symbol: 'PETR4.SA', name: 'Petrobras PN', exchange: 'BVMF' },
      { symbol: 'VALE3.SA', name: 'Vale ON', exchange: 'BVMF' },
      { symbol: 'ITUB4.SA', name: 'Itaú Unibanco PN', exchange: 'BVMF' },
      { symbol: 'BBDC4.SA', name: 'Bradesco PN', exchange: 'BVMF' },
      { symbol: 'AAPL', name: 'Apple Inc.', exchange: 'NASDAQ' },
      { symbol: 'MSFT', name: 'Microsoft Corporation', exchange: 'NASDAQ' }
    ];
    
    return mockSymbols.filter(item => 
      item.symbol.toLowerCase().includes(query.toLowerCase()) ||
      item.name.toLowerCase().includes(query.toLowerCase())
    );
  }

  _getMockMarketSummary() {
    return {
      '^BVSP': this._getMockData('^BVSP'),
      '^GSPC': this._getMockData('^GSPC'),
      '^DJI': this._getMockData('^DJI'),
      'BRL=X': this._getMockData('BRL=X')
    };
  }
}

// Instância global
window.modernFinancialService = new ModernFinancialDataService();

