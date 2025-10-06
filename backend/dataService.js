/**
 * 🎯 QUANTUM TRADES - DATA SERVICE UNIFICADO
 * Gerencia banco local + API + mock com fallback automático
 * Sprint 6 - Orquestrador de Dados
 */

class DataService {
  constructor() {
    this.db = null;
    this.realService = null;
    this.mockService = null;
    this.useRealData = QuantumConfig.features.useRealData;
    this.useFallback = QuantumConfig.features.useFallback;
    this.initialized = false;
  }

  /**
   * Inicializar serviços
   */
  async init() {
    if (this.initialized) return;

    try {
      this.db = window.quantumDB || new DatabaseService();
      await this.db.init();

      this.realService = new RealDataService(QuantumConfig.brapi.token);
      this.mockService = new MockDataService();

      this.initialized = true;
      console.log('✅ DataService inicializado');
    } catch (error) {
      console.error('❌ Erro ao inicializar DataService:', error);
      throw error;
    }
  }

  /**
   * Obter cotação atual de uma ação
   */
  async getStockPrice(symbol) {
    await this.init();

    if (!this.useRealData) {
      console.log('📊 Usando dados MOCK (configuração)');
      const data = await this.mockService.getStockPrice(symbol);
      data._source = 'mock';
      return data;
    }

    try {
      console.log('🌐 Buscando cotação atual na API...');
      const data = await this.realService.getStockPrice(symbol);
      data._source = 'real';
      return data;

    } catch (error) {
      console.warn('⚠️ Erro ao buscar cotação real:', error.message);

      if (this.useFallback) {
        console.log('🔄 Usando FALLBACK para dados mock');
        const data = await this.mockService.getStockPrice(symbol);
        data._source = 'mock';
        return data;
      }

      throw error;
    }
  }

  /**
   * Obter múltiplas cotações
   */
  async getMultipleStockPrices(symbols) {
    await this.init();

    if (!this.useRealData) {
      const data = await this.mockService.getMultipleStockPrices(symbols);
      data._source = 'mock';
      return data;
    }

    try {
      const data = await this.realService.getMultipleStockPrices(symbols);
      data._source = 'real';
      return data;
    } catch (error) {
      if (this.useFallback) {
        const data = await this.mockService.getMultipleStockPrices(symbols);
        data._source = 'mock';
        return data;
      }
      throw error;
    }
  }

  /**
   * Obter histórico de uma ação (OTIMIZADO com banco local)
   */
  async getStockHistory(symbol, period = '1mo', interval = '1d') {
    await this.init();

    if (!this.useRealData) {
      return await this.mockService.getStockHistory(symbol, period, interval);
    }

    try {
      // Determinar range de datas
      const { startDate, endDate } = this.calculateDateRange(period);
      const currentMonthStart = this.getCurrentMonthStart();

      // Verificar se período solicitado inclui mês atual
      const needsCurrentMonth = new Date(endDate) >= new Date(currentMonthStart);

      let historicalData = [];
      let currentMonthData = [];

      // 1. Buscar dados históricos no banco local (até mês anterior)
      if (new Date(startDate) < new Date(currentMonthStart)) {
        console.log('📊 Buscando dados históricos no banco local...');

        const dbEndDate = needsCurrentMonth ? 
          this.getLastClosedMonth() : 
          endDate;

        historicalData = await this.db.getHistoricalPrices(
          symbol,
          startDate,
          dbEndDate
        );

        console.log(`✅ ${historicalData.length} registros encontrados no banco`);
      }

      // 2. Buscar dados do mês atual na API (se necessário)
      if (needsCurrentMonth) {
        console.log('🌐 Buscando dados do mês atual na API...');

        currentMonthData = await this.realService.getStockHistory(
          symbol,
          '1mo',
          interval
        );

        // Filtrar apenas mês atual
        currentMonthData = currentMonthData.filter(item => {
          return item.date >= currentMonthStart;
        });

        console.log(`✅ ${currentMonthData.length} registros do mês atual`);
      }

      // 3. Combinar dados
      const combinedData = [...historicalData, ...currentMonthData];

      // 4. Filtrar pelo range solicitado
      const filteredData = combinedData.filter(item => {
        const itemDate = item.date;
        return itemDate >= startDate && itemDate <= endDate;
      });

      // 5. Ordenar por data
      filteredData.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateA - dateB;
      });

      console.log(`📈 Total: ${filteredData.length} registros retornados`);

      return filteredData;

    } catch (error) {
      console.error('❌ Erro ao buscar histórico:', error);

      if (this.useFallback) {
        console.log('🔄 Usando fallback para dados mock');
        return await this.mockService.getStockHistory(symbol, period, interval);
      }

      throw error;
    }
  }

  /**
   * Obter visão geral do mercado
   */
  async getMarketOverview() {
    await this.init();

    if (!this.useRealData) {
      return await this.mockService.getMarketOverview();
    }

    try {
      return await this.realService.getMarketOverview();
    } catch (error) {
      if (this.useFallback) {
        return await this.mockService.getMarketOverview();
      }
      throw error;
    }
  }

  /**
   * Buscar ações
   */
  async searchStocks(query, limit = 10) {
    await this.init();

    if (!this.useRealData) {
      return await this.mockService.searchStocks(query, limit);
    }

    try {
      return await this.realService.searchStocks(query, limit);
    } catch (error) {
      if (this.useFallback) {
        return await this.mockService.searchStocks(query, limit);
      }
      throw error;
    }
  }

  /**
   * Atualizar token em tempo real
   */
  updateToken(token) {
    if (this.realService) {
      this.realService.setApiToken(token);
    }
    QuantumConfig.setApiToken(token);
  }

  /**
   * Alternar fonte de dados
   */
  toggleDataSource() {
    this.useRealData = !this.useRealData;
    QuantumConfig.features.useRealData = this.useRealData;
    localStorage.setItem('quantum_use_real_data', this.useRealData);
    console.log(`🔄 Fonte alterada para: ${this.useRealData ? 'REAL' : 'MOCK'}`);
    return this.useRealData;
  }

  /**
   * Calcular range de datas baseado no período
   */
  calculateDateRange(period) {
    const endDate = new Date();
    const startDate = new Date();

    const periodMap = {
      '1D': 1,
      '5D': 5,
      '1M': 30,
      '3M': 90,
      '6M': 180,
      '1Y': 365,
      '2Y': 730,
      '5Y': 1825,
      '10Y': 3650,
      '20Y': 7300,
      'MAX': 7300
    };

    const days = periodMap[period.toUpperCase()] || periodMap['1M'];
    startDate.setDate(startDate.getDate() - days);

    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0]
    };
  }

  /**
   * Obter primeiro dia do mês atual
   */
  getCurrentMonthStart() {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1)
      .toISOString().split('T')[0];
  }

  /**
   * Obter último mês fechado
   */
  getLastClosedMonth() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const lastDay = new Date(lastMonth.getFullYear(), lastMonth.getMonth() + 1, 0);
    return lastDay.toISOString().split('T')[0];
  }

  /**
   * Obter estatísticas de uso
   */
  async getStats() {
    await this.init();

    const dbStats = await this.db.getStats();
    const apiStats = this.realService.getStats();

    return {
      database: dbStats,
      api: apiStats,
      config: {
        useRealData: this.useRealData,
        useFallback: this.useFallback,
        hasToken: !!QuantumConfig.brapi.token
      }
    };
  }

  /**
   * Limpar todos os caches
   */
  clearAllCaches() {
    if (this.realService) {
      this.realService.clearCache();
    }
    console.log('🗑️ Todos os caches limpos');
  }
}

// Instância global
const quantumDataService = new DataService();

// Exportar
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataService;
} else {
  window.DataService = DataService;
  window.quantumDataService = quantumDataService;
}
