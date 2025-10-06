/**
 * 💰 QUANTUM FINANCE - FINANCIAL DATA SERVICE
 * Serviço principal que integra todas as APIs e sistema de cache
 */

class FinancialDataService {
  constructor() {
    // Inicializar APIs
    this.apis = {
      primary: new YahooFinanceAPI(),
      secondary: new BrapiAPI(),
      tertiary: null // Placeholder para HG Brasil ou outra API
    };
    
    // Inicializar sistema de cache
    this.cache = new CacheService();
    this.cacheManager = new IntelligentCacheManager(this.cache);
    this.fallbackManager = new APIFallbackService(this.apis);
    
    // Configurações
    this.config = {
      enableCache: true,
      enableFallback: true,
      defaultTimeout: 5000,
      maxRetries: 3
    };
    
    // Métricas
    this.metrics = {
      requests: 0,
      errors: 0,
      cacheHits: 0,
      cacheMisses: 0,
      apiCalls: 0,
      fallbacks: 0
    };
    
    console.log('[FinancialDataService] Initialized with cache and fallback support');
  }

  /**
   * Obter preço atual de uma ação
   */
  async getStockPrice(symbol, options = {}) {
    this.metrics.requests++;
    
    const cacheKey = `stock_price_${symbol}`;
    const forceRefresh = options.forceRefresh || false;
    
    try {
      // Tentar cache primeiro (se não for refresh forçado)
      if (this.config.enableCache && !forceRefresh) {
        const cached = await this.cacheManager.get(
          cacheKey, 
          'STOCK_PRICES',
          () => this.fetchStockPrice(symbol)
        );
        
        if (cached) {
          this.metrics.cacheHits++;
          return this.transformStockData(cached);
        }
        
        this.metrics.cacheMisses++;
      }

      // Buscar dados das APIs
      const data = await this.fetchStockPrice(symbol);
      
      // Armazenar no cache
      if (this.config.enableCache) {
        await this.cacheManager.set(cacheKey, data, 'STOCK_PRICES');
      }
      
      return this.transformStockData(data);
      
    } catch (error) {
      this.metrics.errors++;
      
      // Tentar retornar dados em cache como fallback
      if (this.config.enableCache) {
        const staleData = await this.cache.get(cacheKey);
        if (staleData) {
          console.warn(`[FinancialDataService] Returning stale data for ${symbol}`);
          return this.transformStockData(staleData);
        }
      }
      
      throw new Error(`Failed to fetch stock price for ${symbol}: ${error.message}`);
    }
  }

  /**
   * Obter múltiplas ações de uma vez
   */
  async getMultipleStockPrices(symbols, options = {}) {
    const promises = symbols.map(symbol => 
      this.getStockPrice(symbol, options).catch(error => ({
        symbol,
        error: error.message,
        price: null
      }))
    );
    
    const results = await Promise.all(promises);
    
    return {
      success: results.filter(r => !r.error),
      errors: results.filter(r => r.error),
      timestamp: new Date()
    };
  }

  /**
   * Obter histórico de preços
   */
  async getStockHistory(symbol, period = '1M', interval = '1d', options = {}) {
    this.metrics.requests++;
    
    const cacheKey = `stock_history_${symbol}_${period}_${interval}`;
    const forceRefresh = options.forceRefresh || false;
    
    try {
      // Tentar cache primeiro
      if (this.config.enableCache && !forceRefresh) {
        const cached = await this.cacheManager.get(
          cacheKey,
          'HISTORICAL_DATA',
          () => this.fetchStockHistory(symbol, period, interval)
        );
        
        if (cached) {
          this.metrics.cacheHits++;
          return this.transformHistoricalData(cached);
        }
        
        this.metrics.cacheMisses++;
      }

      // Buscar dados das APIs
      const data = await this.fetchStockHistory(symbol, period, interval);
      
      // Armazenar no cache
      if (this.config.enableCache) {
        await this.cacheManager.set(cacheKey, data, 'HISTORICAL_DATA');
      }
      
      return this.transformHistoricalData(data);
      
    } catch (error) {
      this.metrics.errors++;
      throw new Error(`Failed to fetch stock history for ${symbol}: ${error.message}`);
    }
  }

  /**
   * Buscar ações por nome ou símbolo
   */
  async searchStocks(query, limit = 10, options = {}) {
    if (query.length < 2) return [];
    
    this.metrics.requests++;
    
    const cacheKey = `search_${query.toLowerCase()}_${limit}`;
    const forceRefresh = options.forceRefresh || false;
    
    try {
      // Tentar cache primeiro
      if (this.config.enableCache && !forceRefresh) {
        const cached = await this.cacheManager.get(
          cacheKey,
          'SEARCH_RESULTS',
          () => this.fetchSearchResults(query, limit)
        );
        
        if (cached) {
          this.metrics.cacheHits++;
          return cached;
        }
        
        this.metrics.cacheMisses++;
      }

      // Buscar dados das APIs
      const results = await this.fetchSearchResults(query, limit);
      
      // Armazenar no cache
      if (this.config.enableCache) {
        await this.cacheManager.set(cacheKey, results, 'SEARCH_RESULTS');
      }
      
      return results;
      
    } catch (error) {
      this.metrics.errors++;
      console.error(`[FinancialDataService] Search error for "${query}":`, error);
      return [];
    }
  }

  /**
   * Obter visão geral do mercado
   */
  async getMarketOverview(options = {}) {
    this.metrics.requests++;
    
    const cacheKey = 'market_overview';
    const forceRefresh = options.forceRefresh || false;
    
    try {
      // Tentar cache primeiro
      if (this.config.enableCache && !forceRefresh) {
        const cached = await this.cacheManager.get(
          cacheKey,
          'MARKET_OVERVIEW',
          () => this.fetchMarketOverview()
        );
        
        if (cached) {
          this.metrics.cacheHits++;
          return cached;
        }
        
        this.metrics.cacheMisses++;
      }

      // Buscar dados das APIs
      const overview = await this.fetchMarketOverview();
      
      // Armazenar no cache
      if (this.config.enableCache) {
        await this.cacheManager.set(cacheKey, overview, 'MARKET_OVERVIEW');
      }
      
      return overview;
      
    } catch (error) {
      this.metrics.errors++;
      throw new Error(`Failed to fetch market overview: ${error.message}`);
    }
  }

  /**
   * Buscar preço de uma ação nas APIs
   */
  async fetchStockPrice(symbol) {
    this.metrics.apiCalls++;
    
    if (this.config.enableFallback) {
      return await this.fallbackManager.fetchWithFallback('getStockPrice', symbol);
    } else {
      return await this.apis.primary.getStockPrice(symbol);
    }
  }

  /**
   * Buscar histórico nas APIs
   */
  async fetchStockHistory(symbol, period, interval) {
    this.metrics.apiCalls++;
    
    if (this.config.enableFallback) {
      return await this.fallbackManager.fetchWithFallback('getStockHistory', symbol, period, interval);
    } else {
      return await this.apis.primary.getStockHistory(symbol, period, interval);
    }
  }

  /**
   * Buscar resultados de pesquisa nas APIs
   */
  async fetchSearchResults(query, limit) {
    this.metrics.apiCalls++;
    
    if (this.config.enableFallback) {
      return await this.fallbackManager.fetchWithFallback('searchStocks', query, limit);
    } else {
      return await this.apis.primary.searchStocks(query, limit);
    }
  }

  /**
   * Buscar visão geral do mercado
   */
  async fetchMarketOverview() {
    this.metrics.apiCalls++;
    
    const indices = ['IBOV', 'IFIX', 'SMLL'];
    const promises = indices.map(index => this.fetchStockPrice(index));
    
    try {
      const data = await Promise.all(promises);
      
      return {
        ibovespa: data[0],
        ifix: data[1],
        smallCap: data[2],
        timestamp: new Date(),
        source: 'aggregated'
      };
      
    } catch (error) {
      // Fallback: tentar buscar pelo menos o Ibovespa
      try {
        const ibovespa = await this.fetchStockPrice('IBOV');
        return {
          ibovespa,
          ifix: null,
          smallCap: null,
          timestamp: new Date(),
          source: 'partial',
          warning: 'Partial data due to API errors'
        };
      } catch (fallbackError) {
        throw error;
      }
    }
  }

  /**
   * Transformar dados de ação para formato padrão
   */
  transformStockData(rawData) {
    if (!rawData) return null;
    
    return {
      symbol: rawData.symbol,
      price: parseFloat(rawData.price || 0),
      change: parseFloat(rawData.change || 0),
      changePercent: parseFloat(rawData.changePercent || 0),
      volume: parseInt(rawData.volume || 0),
      marketCap: rawData.marketCap,
      timestamp: new Date(rawData.timestamp || Date.now()),
      currency: rawData.currency || 'BRL',
      exchange: rawData.exchange || 'B3',
      source: rawData.source || 'unknown'
    };
  }

  /**
   * Transformar dados históricos para formato padrão
   */
  transformHistoricalData(rawData) {
    if (!Array.isArray(rawData)) return [];
    
    return rawData.map(item => ({
      date: new Date(item.date),
      open: parseFloat(item.open || 0),
      high: parseFloat(item.high || 0),
      low: parseFloat(item.low || 0),
      close: parseFloat(item.close || 0),
      adjClose: parseFloat(item.adjClose || item.close || 0),
      volume: parseInt(item.volume || 0),
      symbol: item.symbol
    })).filter(item => item.close > 0);
  }

  /**
   * Invalidar cache por símbolo
   */
  async invalidateSymbol(symbol) {
    await this.cache.invalidate(`_${symbol}`);
    console.log(`[FinancialDataService] Invalidated cache for symbol: ${symbol}`);
  }

  /**
   * Invalidar cache por tipo
   */
  async invalidateByType(type) {
    await this.cacheManager.invalidateByEvent(type);
  }

  /**
   * Obter métricas do serviço
   */
  getMetrics() {
    const cacheMetrics = this.cache.getMetrics();
    const fallbackMetrics = this.fallbackManager ? this.fallbackManager.getMetrics() : {};
    
    return {
      service: this.metrics,
      cache: cacheMetrics,
      fallback: fallbackMetrics,
      timestamp: new Date()
    };
  }

  /**
   * Obter status de saúde do serviço
   */
  async getHealthStatus() {
    const metrics = this.getMetrics();
    const cacheSize = metrics.cache.cacheSize;
    const hitRatio = metrics.cache.hitRatio;
    const errorRate = this.metrics.requests > 0 ? 
      (this.metrics.errors / this.metrics.requests) * 100 : 0;
    
    const status = {
      healthy: errorRate < 10 && hitRatio > 30,
      metrics: {
        errorRate: parseFloat(errorRate.toFixed(2)),
        hitRatio,
        cacheSize,
        totalRequests: this.metrics.requests
      },
      apis: await this.checkAPIHealth(),
      timestamp: new Date()
    };
    
    return status;
  }

  /**
   * Verificar saúde das APIs
   */
  async checkAPIHealth() {
    const health = {};
    
    for (const [name, api] of Object.entries(this.apis)) {
      if (!api) {
        health[name] = { status: 'disabled' };
        continue;
      }
      
      try {
        // Teste simples com símbolo conhecido
        await api.getStockPrice('PETR4');
        health[name] = { status: 'healthy', lastCheck: new Date() };
      } catch (error) {
        health[name] = { 
          status: 'unhealthy', 
          error: error.message,
          lastCheck: new Date()
        };
      }
    }
    
    return health;
  }

  /**
   * Configurar serviço
   */
  configure(options = {}) {
    this.config = {
      ...this.config,
      ...options
    };
    
    // Inicializar serviço mock para fallback
    this.mockService = new MockDataService();
    this.mockService.setDelay(200); // Delay menor para melhor UX
    
    console.log('[FinancialDataService] Configured:', this.config);
  }

  /**
   * Obter preço de uma ação com fallback para mock
   */
  async getStockPriceWithFallback(symbol, options = {}) {
    try {
      // Tentar APIs reais primeiro
      const result = await this.getStockPrice(symbol, options);
      console.log(`[FinancialDataService] Successfully fetched real data for ${symbol}`);
      return result;
    } catch (error) {
      console.warn(`[FinancialDataService] Real APIs failed for ${symbol}, using mock data:`, error.message);
      this.metrics.fallbacks++;
      
      try {
        // Garantir que o mock service está inicializado
        if (!this.mockService) {
          this.mockService = new MockDataService();
          this.mockService.setDelay(100); // Delay menor para melhor UX
        }
        
        const mockResult = await this.mockService.getStockPrice(symbol);
        console.log(`[FinancialDataService] Successfully returned mock data for ${symbol}`);
        return mockResult;
      } catch (mockError) {
        console.error(`[FinancialDataService] Mock service also failed for ${symbol}:`, mockError);
        // Retornar dados básicos como último recurso
        return {
          symbol,
          name: `Ação ${symbol}`,
          price: 25.00 + Math.random() * 50,
          previousClose: 25.00,
          change: (Math.random() - 0.5) * 5,
          changePercent: (Math.random() - 0.5) * 10,
          volume: Math.floor(Math.random() * 1000000),
          high: 30.00,
          low: 20.00,
          timestamp: new Date(),
          isFallback: true
        };
      }
    }
  }

  /**
   * Obter múltiplos preços com fallback para mock
   */
  async getMultipleStockPricesWithFallback(symbols, options = {}) {
    console.log(`[FinancialDataService] Fetching multiple stocks with fallback:`, symbols);
    
    const results = {
      success: [],
      errors: []
    };

    // Processar cada símbolo individualmente para garantir fallback
    for (const symbol of symbols) {
      try {
        const stockData = await this.getStockPriceWithFallback(symbol, options);
        results.success.push(stockData);
      } catch (error) {
        console.error(`[FinancialDataService] Failed to get data for ${symbol}:`, error);
        results.errors.push({ symbol, error: error.message });
        
        // Adicionar dados básicos mesmo em caso de erro total
        results.success.push({
          symbol,
          name: `Ação ${symbol}`,
          price: 25.00 + Math.random() * 50,
          previousClose: 25.00,
          change: (Math.random() - 0.5) * 5,
          changePercent: (Math.random() - 0.5) * 10,
          volume: Math.floor(Math.random() * 1000000),
          high: 30.00,
          low: 20.00,
          timestamp: new Date(),
          isFallback: true,
          isEmergencyFallback: true
        });
      }
    }

    console.log(`[FinancialDataService] Multiple stocks result:`, {
      requested: symbols.length,
      successful: results.success.length,
      errors: results.errors.length
    });

    return results;
  }

  /**
   * Obter histórico com fallback para mock
   */
  async getStockHistoryWithFallback(symbol, period, interval, options = {}) {
    try {
      return await this.getStockHistory(symbol, period, interval, options);
    } catch (error) {
      console.warn(`[FinancialDataService] Using mock data for ${symbol} history:`, error.message);
      return await this.mockService.getStockHistory(symbol, period, interval);
    }
  }

  /**
   * Obter visão geral do mercado com fallback para mock
   */
  async getMarketOverviewWithFallback(options = {}) {
    try {
      // Tentar APIs reais primeiro
      const result = await this.getMarketOverview(options);
      console.log('[FinancialDataService] Successfully fetched real market data');
      return result;
    } catch (error) {
      console.warn('[FinancialDataService] Real APIs failed for market overview, using mock data:', error.message);
      this.metrics.fallbacks++;
      
      try {
        // Garantir que o mock service está inicializado
        if (!this.mockService) {
          this.mockService = new MockDataService();
          this.mockService.setDelay(100);
        }
        
        const mockResult = await this.mockService.getMarketOverview();
        console.log('[FinancialDataService] Successfully returned mock market data');
        return mockResult;
      } catch (mockError) {
        console.error('[FinancialDataService] Mock service also failed for market overview:', mockError);
        
        // Retornar dados básicos do mercado brasileiro como último recurso
        return {
          indices: [
            {
              symbol: 'IBOV',
              name: 'Ibovespa',
              price: 121000 + Math.random() * 10000,
              change: (Math.random() - 0.5) * 2000,
              changePercent: (Math.random() - 0.5) * 2,
              volume: Math.floor(Math.random() * 100000000),
              timestamp: new Date(),
              isFallback: true
            },
            {
              symbol: 'IFIX',
              name: 'IFIX',
              price: 2800 + Math.random() * 200,
              change: (Math.random() - 0.5) * 50,
              changePercent: (Math.random() - 0.5) * 2,
              volume: Math.floor(Math.random() * 10000000),
              timestamp: new Date(),
              isFallback: true
            },
            {
              symbol: 'SMLL',
              name: 'Small Cap',
              price: 3200 + Math.random() * 300,
              change: (Math.random() - 0.5) * 100,
              changePercent: (Math.random() - 0.5) * 3,
              volume: Math.floor(Math.random() * 50000000),
              timestamp: new Date(),
              isFallback: true
            }
          ],
          summary: {
            trend: Math.random() > 0.5 ? 'Alta' : 'Baixa',
            lastUpdate: new Date(),
            nextUpdate: new Date(Date.now() + 60000),
            marketStatus: 'Fechado',
            isFallback: true
          }
        };
      }
    }
  }

  /**
   * Buscar ações com fallback para mock
   */
  async searchStocksWithFallback(query, limit = 10) {
    try {
      return await this.searchStocks(query, limit);
    } catch (error) {
      console.warn('[FinancialDataService] Using mock data for search:', error.message);
      return await this.mockService.searchStocks(query, limit);
    }
  }

  /** Destruir serviço e limpar recursos
   */
  destroy() {
    if (this.cache) {
      this.cache.destroy();
    }
    
    console.log('[FinancialDataService] Service destroyed');
  }
}

/**
 * 🔄 API FALLBACK SERVICE
 * Gerencia fallback entre múltiplas APIs
 */
class APIFallbackService {
  constructor(apis) {
    this.apis = Object.entries(apis)
      .filter(([name, api]) => api !== null)
      .map(([name, api], index) => ({
        name,
        instance: api,
        priority: index + 1,
        failures: 0,
        lastFailure: null
      }));
    
    this.circuitBreaker = new Map();
    this.metrics = {
      totalCalls: 0,
      fallbacks: 0,
      failures: 0
    };
  }

  /**
   * Executar método com fallback
   */
  async fetchWithFallback(method, ...args) {
    this.metrics.totalCalls++;
    const errors = [];
    
    for (const api of this.apis) {
      if (this.isCircuitOpen(api.name)) {
        console.warn(`[Fallback] Skipping ${api.name} - Circuit breaker open`);
        continue;
      }

      try {
        const result = await api.instance[method](...args);
        this.recordSuccess(api.name);
        
        if (api.priority > 1) {
          this.metrics.fallbacks++;
          console.log(`[Fallback] Success with ${api.name} (priority ${api.priority})`);
        }
        
        return result;
        
      } catch (error) {
        errors.push({ api: api.name, error });
        this.recordFailure(api.name);
        console.warn(`[Fallback] Failed with ${api.name}: ${error.message}`);
      }
    }

    this.metrics.failures++;
    throw new Error(`All APIs failed: ${errors.map(e => `${e.api}: ${e.error.message}`).join(', ')}`);
  }

  /**
   * Verificar se circuit breaker está aberto
   */
  isCircuitOpen(apiName) {
    const circuit = this.circuitBreaker.get(apiName);
    if (!circuit) return false;
    
    const now = Date.now();
    const timeSinceLastFailure = now - circuit.lastFailure;
    const recoveryTimeout = 60000; // 1 minuto
    
    if (circuit.failures >= 5 && timeSinceLastFailure < recoveryTimeout) {
      return true;
    }
    
    return false;
  }

  /**
   * Registrar sucesso
   */
  recordSuccess(apiName) {
    this.circuitBreaker.set(apiName, {
      failures: 0,
      lastFailure: null
    });
  }

  /**
   * Registrar falha
   */
  recordFailure(apiName) {
    const circuit = this.circuitBreaker.get(apiName) || { failures: 0 };
    circuit.failures++;
    circuit.lastFailure = Date.now();
    this.circuitBreaker.set(apiName, circuit);
  }

  /**
   * Obter métricas do fallback
   */
  getMetrics() {
    return {
      ...this.metrics,
      circuitBreakers: Object.fromEntries(this.circuitBreaker),
      apis: this.apis.map(api => ({
        name: api.name,
        priority: api.priority,
        failures: api.failures
      }))
    };
  }
}

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FinancialDataService, APIFallbackService };
} else {
  window.FinancialDataService = FinancialDataService;
  window.APIFallbackService = APIFallbackService;
}

