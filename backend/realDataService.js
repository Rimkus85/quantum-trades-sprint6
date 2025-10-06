/**
 * 🚀 QUANTUM TRADES - REAL DATA SERVICE
 * Serviço de integração com brapi.dev para dados reais de mercado
 * Sprint 6 - Integração com Dados Reais
 */

class RealDataService {
  constructor(apiToken = null) {
    this.baseUrl = 'https://brapi.dev/api';
    this.apiToken = apiToken;
    this.cache = new Map();
    this.cacheTimeout = 30 * 60 * 1000; // 30 minutos
    this.requestCount = 0;
  }

  /**
   * Fazer requisição à API com cache
   */
  async fetchWithCache(url) {
    const cacheKey = url;
    const cached = this.cache.get(cacheKey);
    
    // Verificar cache
    if (cached && (Date.now() - cached.timestamp < this.cacheTimeout)) {
      console.log('📦 Usando dados do cache:', cacheKey);
      return cached.data;
    }

    // Fazer requisição
    const headers = {};
    if (this.apiToken) {
      headers['Authorization'] = `Bearer ${this.apiToken}`;
    }

    try {
      this.requestCount++;
      console.log(`🌐 Requisição #${this.requestCount} à API:`, url);
      
      const response = await fetch(url, { headers });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Salvar no cache
      this.cache.set(cacheKey, {
        data: data,
        timestamp: Date.now()
      });

      return data;
    } catch (error) {
      console.error('❌ Erro na API:', error);
      
      // Retornar cache expirado se disponível
      if (cached) {
        console.warn('⚠️ Usando cache expirado devido a erro na API');
        return cached.data;
      }
      
      throw error;
    }
  }

  /**
   * Obter cotação de uma ação
   */
  async getStockPrice(symbol) {
    try {
      const url = `${this.baseUrl}/quote/${symbol}`;
      const response = await this.fetchWithCache(url);

      if (!response.results || response.results.length === 0) {
        throw new Error(`Ação ${symbol} não encontrada`);
      }

      const stock = response.results[0];

      // Converter para formato compatível com o sistema atual
      return this.convertBrapiToQuantum(stock);
    } catch (error) {
      console.error(`Erro ao buscar ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Obter múltiplas cotações
   */
  async getMultipleStockPrices(symbols) {
    const results = {
      success: [],
      errors: []
    };

    try {
      // brapi aceita múltiplos símbolos separados por vírgula
      const symbolsStr = symbols.join(',');
      const url = `${this.baseUrl}/quote/${symbolsStr}`;
      const response = await this.fetchWithCache(url);

      if (response.results) {
        for (const stock of response.results) {
          try {
            results.success.push(this.convertBrapiToQuantum(stock));
          } catch (error) {
            results.errors.push({ symbol: stock.symbol, error: error.message });
          }
        }
      }
    } catch (error) {
      console.error('Erro ao buscar múltiplas ações:', error);
      for (const symbol of symbols) {
        results.errors.push({ symbol, error: error.message });
      }
    }

    return results;
  }

  /**
   * Obter histórico de uma ação
   */
  async getStockHistory(symbol, period = '1mo', interval = '1d') {
    try {
      // Mapear períodos para formato brapi
      const rangeMap = {
        '1D': '1d',
        '5D': '5d',
        '1M': '1mo',
        '3M': '3mo',
        '6M': '6mo',
        '1Y': '1y',
        '2Y': '2y',
        '5Y': '5y',
        '10Y': '10y',
        '20Y': 'max',
        'MAX': 'max'
      };

      const range = rangeMap[period.toUpperCase()] || period;
      const url = `${this.baseUrl}/quote/${symbol}?range=${range}&interval=${interval}`;
      const response = await this.fetchWithCache(url);

      if (!response.results || response.results.length === 0) {
        throw new Error(`Histórico de ${symbol} não encontrado`);
      }

      const stock = response.results[0];
      const historicalData = stock.historicalDataPrice || [];

      // Converter para formato compatível
      return historicalData.map(item => ({
        date: new Date(item.date * 1000).toISOString().split('T')[0],
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume,
        adjustedClose: item.close, // brapi não retorna adjusted, usar close
        timestamp: new Date(item.date * 1000)
      }));
    } catch (error) {
      console.error(`Erro ao buscar histórico de ${symbol}:`, error);
      throw error;
    }
  }

  /**
   * Obter visão geral do mercado
   */
  async getMarketOverview() {
    try {
      // Buscar principais índices
      const indices = await this.getMultipleStockPrices(['^BVSP', 'IFIX.SA', 'SMLL.SA']);
      
      const ibovespa = indices.success.find(s => s.symbol === '^BVSP') || {};
      const ifix = indices.success.find(s => s.symbol === 'IFIX.SA') || {};
      const smallCap = indices.success.find(s => s.symbol === 'SMLL.SA') || {};

      return {
        ibovespa: {
          price: ibovespa.price || 0,
          change: ibovespa.change || 0,
          changePercent: ibovespa.changePercent || 0,
          volume: ibovespa.volume || 0,
          timestamp: new Date()
        },
        ifix: {
          price: ifix.price || 0,
          change: ifix.change || 0,
          changePercent: ifix.changePercent || 0,
          volume: ifix.volume || 0,
          timestamp: new Date()
        },
        smallCap: {
          price: smallCap.price || 0,
          change: smallCap.change || 0,
          changePercent: smallCap.changePercent || 0,
          volume: smallCap.volume || 0,
          timestamp: new Date()
        },
        timestamp: new Date()
      };
    } catch (error) {
      console.error('Erro ao buscar visão geral do mercado:', error);
      throw error;
    }
  }

  /**
   * Buscar ações
   */
  async searchStocks(query, limit = 10) {
    try {
      // brapi tem endpoint de lista
      const url = `${this.baseUrl}/quote/list`;
      const response = await this.fetchWithCache(url);

      if (!response.stocks) {
        return [];
      }

      const queryUpper = query.toUpperCase();
      const filtered = response.stocks.filter(stock => 
        stock.stock.includes(queryUpper) || 
        stock.name.toUpperCase().includes(queryUpper)
      );

      return filtered.slice(0, limit).map(stock => ({
        symbol: stock.stock,
        name: stock.name,
        exchange: 'B3',
        type: stock.type || 'stock'
      }));
    } catch (error) {
      console.error('Erro ao buscar ações:', error);
      return [];
    }
  }

  /**
   * Converter formato brapi para formato Quantum
   */
  convertBrapiToQuantum(brapiStock) {
    return {
      symbol: brapiStock.symbol,
      name: brapiStock.shortName || brapiStock.longName,
      price: brapiStock.regularMarketPrice,
      previousClose: brapiStock.regularMarketPreviousClose || brapiStock.regularMarketPrice,
      change: brapiStock.regularMarketChange || 0,
      changePercent: brapiStock.regularMarketChangePercent || 0,
      volume: brapiStock.regularMarketVolume,
      high: brapiStock.regularMarketDayHigh,
      low: brapiStock.regularMarketDayLow,
      dayHigh: brapiStock.regularMarketDayHigh,
      dayLow: brapiStock.regularMarketDayLow,
      lastUpdate: brapiStock.regularMarketTime,
      timestamp: new Date()
    };
  }

  /**
   * Configurar token de API
   */
  setApiToken(token) {
    this.apiToken = token;
    console.log('✅ Token atualizado no RealDataService');
  }

  /**
   * Limpar cache
   */
  clearCache() {
    this.cache.clear();
    console.log('🗑️ Cache limpo');
  }

  /**
   * Obter estatísticas de uso
   */
  getStats() {
    return {
      requestCount: this.requestCount,
      cacheSize: this.cache.size,
      hasToken: !!this.apiToken
    };
  }
}

// Exportar para uso
if (typeof module !== 'undefined' && module.exports) {
  module.exports = RealDataService;
} else {
  window.RealDataService = RealDataService;
}
