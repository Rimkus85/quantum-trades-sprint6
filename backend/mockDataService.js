/**
 * 🎭 QUANTUM FINANCE - MOCK DATA SERVICE
 * Serviço de dados simulados para desenvolvimento e testes
 */

class MockDataService {
  constructor() {
    this.isEnabled = true;
    this.delay = 500; // Simular latência de rede
  }

  /**
   * Simular delay de rede
   */
  async simulateDelay() {
    if (this.delay > 0) {
      await new Promise(resolve => setTimeout(resolve, this.delay));
    }
  }

  /**
   * Gerar preço aleatório baseado em um valor base
   */
  generateRandomPrice(basePrice, volatility = 0.05) {
    const change = (Math.random() - 0.5) * 2 * volatility;
    return basePrice * (1 + change);
  }

  /**
   * Gerar dados de ações brasileiras
   */
  async getStockPrice(symbol) {
    await this.simulateDelay();

    const stockData = {
      'PETR4': { basePrice: 32.50, name: 'Petróleo Brasileiro S.A. - Petrobras' },
      'VALE3': { basePrice: 65.80, name: 'Vale S.A.' },
      'ITUB4': { basePrice: 28.90, name: 'Itaú Unibanco Holding S.A.' },
      'BBDC4': { basePrice: 22.15, name: 'Banco Bradesco S.A.' },
      'ABEV3': { basePrice: 12.45, name: 'Ambev S.A.' },
      'MGLU3': { basePrice: 8.75, name: 'Magazine Luiza S.A.' },
      'WEGE3': { basePrice: 45.20, name: 'WEG S.A.' },
      'SUZB3': { basePrice: 52.30, name: 'Suzano S.A.' },
      'RENT3': { basePrice: 35.60, name: 'Localiza Rent a Car S.A.' },
      'LREN3': { basePrice: 18.90, name: 'Lojas Renner S.A.' }
    };

    const stock = stockData[symbol] || { basePrice: 25.00, name: 'Ação Desconhecida' };
    const currentPrice = this.generateRandomPrice(stock.basePrice);
    const previousPrice = this.generateRandomPrice(stock.basePrice, 0.02);
    const change = currentPrice - previousPrice;
    const changePercent = (change / previousPrice) * 100;

    return {
      symbol,
      name: stock.name,
      price: currentPrice,
      previousClose: previousPrice,
      change,
      changePercent,
      volume: Math.floor(Math.random() * 10000000) + 1000000,
      high: this.generateRandomPrice(currentPrice, 0.03),
      low: this.generateRandomPrice(currentPrice, -0.03),
      timestamp: new Date()
    };
  }

  /**
   * Gerar múltiplos preços de ações
   */
  async getMultipleStockPrices(symbols) {
    await this.simulateDelay();

    const results = {
      success: [],
      errors: []
    };

    for (const symbol of symbols) {
      try {
        const stockData = await this.getStockPrice(symbol);
        results.success.push(stockData);
      } catch (error) {
        results.errors.push({ symbol, error: error.message });
      }
    }

    return results;
  }

  /**
   * Gerar dados históricos de uma ação
   */
  async getStockHistory(symbol, period = '1M', interval = '1d') {
    await this.simulateDelay();

    const basePrice = 30 + Math.random() * 50; // Preço base entre 30-80
    const dataPoints = this.getDataPointsForPeriod(period);
    const data = [];

    let currentPrice = basePrice;
    const startDate = this.getStartDateForPeriod(period);

    for (let i = 0; i < dataPoints; i++) {
      const date = new Date(startDate.getTime() + (i * this.getIntervalMs(interval)));
      
      // Simular movimento de preço com tendência e volatilidade
      const trend = (Math.random() - 0.48) * 0.02; // Leve tendência de alta
      const volatility = (Math.random() - 0.5) * 0.08; // Volatilidade
      const priceChange = currentPrice * (trend + volatility);
      
      currentPrice = Math.max(currentPrice + priceChange, 1); // Preço mínimo de R$ 1
      
      const high = currentPrice * (1 + Math.random() * 0.03);
      const low = currentPrice * (1 - Math.random() * 0.03);
      const volume = Math.floor(Math.random() * 5000000) + 500000;

      data.push({
        date,
        open: currentPrice,
        high,
        low,
        close: currentPrice,
        volume,
        timestamp: date
      });
    }

    return data;
  }

  /**
   * Gerar visão geral do mercado
   */
  async getMarketOverview() {
    await this.simulateDelay();

    return {
      ibovespa: {
        price: 118500 + Math.random() * 5000,
        change: (Math.random() - 0.5) * 2000,
        changePercent: (Math.random() - 0.5) * 4,
        volume: Math.floor(Math.random() * 50000000000) + 10000000000,
        timestamp: new Date()
      },
      ifix: {
        price: 2850 + Math.random() * 200,
        change: (Math.random() - 0.5) * 50,
        changePercent: (Math.random() - 0.5) * 2,
        volume: Math.floor(Math.random() * 1000000000) + 100000000,
        timestamp: new Date()
      },
      smallCap: {
        price: 3200 + Math.random() * 300,
        change: (Math.random() - 0.5) * 100,
        changePercent: (Math.random() - 0.5) * 3,
        volume: Math.floor(Math.random() * 2000000000) + 200000000,
        timestamp: new Date()
      },
      timestamp: new Date()
    };
  }

  /**
   * Buscar ações
   */
  async searchStocks(query, limit = 10) {
    await this.simulateDelay();

    const allStocks = [
      { symbol: 'PETR4', name: 'Petróleo Brasileiro S.A. - Petrobras', exchange: 'B3', type: 'Equity' },
      { symbol: 'PETR3', name: 'Petróleo Brasileiro S.A. - Petrobras', exchange: 'B3', type: 'Equity' },
      { symbol: 'VALE3', name: 'Vale S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'ITUB4', name: 'Itaú Unibanco Holding S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'ITUB3', name: 'Itaú Unibanco Holding S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'BBDC4', name: 'Banco Bradesco S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'BBDC3', name: 'Banco Bradesco S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'ABEV3', name: 'Ambev S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'MGLU3', name: 'Magazine Luiza S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'WEGE3', name: 'WEG S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'SUZB3', name: 'Suzano S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'RENT3', name: 'Localiza Rent a Car S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'LREN3', name: 'Lojas Renner S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'JBSS3', name: 'JBS S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'HAPV3', name: 'Hapvida Participações e Investimentos S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'RADL3', name: 'Raia Drogasil S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'RAIL3', name: 'Rumo S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'UGPA3', name: 'Ultrapar Participações S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'CSAN3', name: 'Cosan S.A.', exchange: 'B3', type: 'Equity' },
      { symbol: 'KLBN11', name: 'Klabin S.A.', exchange: 'B3', type: 'Equity' }
    ];

    const queryUpper = query.toUpperCase();
    const filtered = allStocks.filter(stock => 
      stock.symbol.includes(queryUpper) || 
      stock.name.toUpperCase().includes(queryUpper)
    );

    return filtered.slice(0, limit);
  }

  /**
   * Gerar status de saúde
   */
  async getHealthStatus() {
    await this.simulateDelay();

    return {
      healthy: true,
      timestamp: new Date(),
      metrics: {
        errorRate: Math.random() * 5, // 0-5% de erro
        totalRequests: Math.floor(Math.random() * 10000) + 1000
      },
      apis: {
        mock: {
          status: 'healthy',
          responseTime: Math.floor(Math.random() * 200) + 100
        }
      }
    };
  }

  /**
   * Utilitários para cálculo de períodos
   */
  getDataPointsForPeriod(period) {
    const points = {
      '1D': 78,    // 5 min intervals for 6.5 hours
      '5D': 390,   // 5 min intervals for 5 days
      '1M': 22,    // Daily for ~1 month
      '3M': 66,    // Daily for ~3 months
      '6M': 132,   // Daily for ~6 months
      '1Y': 252,   // Daily for ~1 year
      '2Y': 104,   // Weekly for 2 years
      '5Y': 60     // Monthly for 5 years
    };
    
    return points[period] || 30;
  }

  getStartDateForPeriod(period) {
    const now = new Date();
    const periods = {
      '1D': 1,
      '5D': 5,
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365,
      '2Y': 730,
      '5Y': 1825
    };
    
    const days = periods[period] || 30;
    return new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
  }

  getIntervalMs(interval) {
    const intervals = {
      '1m': 60 * 1000,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
      '1h': 60 * 60 * 1000,
      '1d': 24 * 60 * 60 * 1000,
      '1wk': 7 * 24 * 60 * 60 * 1000,
      '1mo': 30 * 24 * 60 * 60 * 1000
    };
    
    return intervals[interval] || intervals['1d'];
  }

  /**
   * Configurar delay de simulação
   */
  setDelay(ms) {
    this.delay = ms;
  }

  /**
   * Habilitar/desabilitar serviço mock
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
  }
}

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MockDataService;
} else {
  window.MockDataService = MockDataService;
}

