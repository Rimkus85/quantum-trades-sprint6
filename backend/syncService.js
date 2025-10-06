/**
 * 🔄 QUANTUM TRADES - SYNC SERVICE
 * Gerenciamento de sincronização de dados históricos
 * Sprint 6 - Sincronização Automática
 */

class SyncService {
  constructor() {
    this.db = null;
    this.api = null;
    this.isSyncing = false;
    this.syncProgress = {
      current: 0,
      total: 0,
      currentSymbol: '',
      status: 'idle'
    };
  }

  /**
   * Inicializar serviço
   */
  async init() {
    if (!this.db) {
      this.db = window.quantumDB || new DatabaseService();
      await this.db.init();
    }
    if (!this.api) {
      this.api = new RealDataService(QuantumConfig.brapi.token);
    }
  }

  /**
   * Buscar lista completa de ações da B3
   */
  async getAllB3Stocks() {
    await this.init();
    
    console.log('🔍 Buscando lista completa de ações da B3...');
    
    const allStocks = [];
    let page = 1;
    let hasNextPage = true;
    
    try {
      while (hasNextPage) {
        const url = `${QuantumConfig.brapi.baseUrl}/quote/list?limit=100&page=${page}`;
        const headers = {};
        
        if (QuantumConfig.brapi.token) {
          headers['Authorization'] = `Bearer ${QuantumConfig.brapi.token}`;
        }
        
        const response = await fetch(url, { headers });
        
        if (!response.ok) {
          console.error(`❌ Erro ao buscar página ${page}: ${response.status}`);
          break;
        }
        
        const data = await response.json();
        
        if (data.stocks && data.stocks.length > 0) {
          // Adicionar apenas ações (filtrar FIIs e BDRs se necessário)
          const stocks = data.stocks
            .filter(s => s.type === 'stock') // Apenas ações
            .map(s => s.stock);
          
          allStocks.push(...stocks);
          console.log(`📊 Página ${page}: ${stocks.length} ações encontradas (total: ${allStocks.length})`);
        }
        
        hasNextPage = data.hasNextPage || false;
        page++;
        
        // Aguardar um pouco entre requisições para não sobrecarregar a API
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      console.log(`✅ Total de ações encontradas: ${allStocks.length}`);
      return allStocks;
      
    } catch (error) {
      console.error('❌ Erro ao buscar lista de ações:', error);
      return [];
    }
  }

  /**
   * Importar dados históricos completos de uma ação
   */
  async importHistoricalData(symbol, yearsBack = 20) {
    await this.init();

    if (this.isSyncing) {
      console.warn('⚠️ Sincronização já em andamento');
      return false;
    }

    this.isSyncing = true;
    console.log(`🔄 Iniciando importação de ${symbol} (${yearsBack} anos)...`);

    try {
      // Verificar se já existe dados
      const metadata = await this.db.getSyncMetadata(symbol);
      if (metadata) {
        console.log(`ℹ️ ${symbol} já possui dados. Última sync: ${metadata.lastSync}`);
        
        // Verificar se precisa atualizar
        const needsUpdate = this.needsMonthlyUpdate(metadata.lastSync);
        if (!needsUpdate) {
          console.log('✅ Dados já estão atualizados');
          this.isSyncing = false;
          return { success: true, skipped: true, message: 'Dados já atualizados' };
        }
      }

      // Buscar dados históricos da API
      console.log(`📅 Buscando histórico máximo disponível...`);

      // brapi.dev: buscar histórico completo
      const historicalData = await this.api.getStockHistory(
        symbol,
        'max', // Período máximo disponível
        '1d'   // Intervalo diário
      );

      if (!historicalData || historicalData.length === 0) {
        throw new Error(`Nenhum dado histórico encontrado para ${symbol}`);
      }

      // Filtrar apenas até o último mês fechado
      const lastClosedMonth = this.getLastClosedMonth();
      const filteredData = historicalData.filter(item => {
        return item.date <= lastClosedMonth;
      });

      console.log(`📊 ${filteredData.length} registros obtidos da API`);

      // Salvar no banco local
      const savedCount = await this.db.saveHistoricalPrices(symbol, filteredData);

      // Atualizar metadados
      await this.db.updateSyncMetadata(symbol, {
        start: filteredData[0].date,
        end: filteredData[filteredData.length - 1].date
      }, savedCount);

      console.log(`✅ Importação concluída: ${savedCount} registros salvos`);

      this.isSyncing = false;
      return { 
        success: true, 
        skipped: false, 
        recordCount: savedCount,
        dateRange: {
          start: filteredData[0].date,
          end: filteredData[filteredData.length - 1].date
        }
      };

    } catch (error) {
      console.error(`❌ Erro na importação de ${symbol}:`, error);
      this.isSyncing = false;
      throw error;
    }
  }

  /**
   * Atualizar dados do mês fechado (executar dia 02)
   */
  async updateClosedMonth(symbol) {
    await this.init();

    console.log(`🔄 Atualizando mês fechado para ${symbol}...`);

    try {
      const lastMonth = this.getLastClosedMonth();
      const firstDayLastMonth = this.getFirstDayOfMonth(lastMonth);

      // Buscar dados do mês fechado
      const monthData = await this.api.getStockHistory(
        symbol,
        '1mo', // Último mês
        '1d'
      );

      // Filtrar apenas o mês fechado
      const filteredData = monthData.filter(item => {
        return item.date >= firstDayLastMonth && item.date <= lastMonth;
      });

      if (filteredData.length === 0) {
        console.warn(`⚠️ Nenhum dado encontrado para o mês fechado`);
        return false;
      }

      // Salvar no banco
      await this.db.saveHistoricalPrices(symbol, filteredData);

      // Atualizar metadados
      const metadata = await this.db.getSyncMetadata(symbol);
      if (metadata) {
        metadata.dataRange.end = lastMonth;
        metadata.recordCount += filteredData.length;
        await this.db.updateSyncMetadata(
          symbol,
          metadata.dataRange,
          metadata.recordCount
        );
      }

      console.log(`✅ Mês fechado atualizado: ${filteredData.length} registros`);
      return true;

    } catch (error) {
      console.error(`❌ Erro ao atualizar mês fechado:`, error);
      throw error;
    }
  }

  /**
   * Sincronização automática mensal (executar dia 02)
   */
  async monthlySync(symbols = null) {
    await this.init();

    // Se não especificado, buscar todas as ações já sincronizadas
    if (!symbols) {
      symbols = await this.db.getAllSyncedSymbols();
    }

    if (symbols.length === 0) {
      console.log('ℹ️ Nenhuma ação para sincronizar');
      return { success: [], errors: [] };
    }

    console.log(`📅 Iniciando sincronização mensal (${symbols.length} ações)...`);

    const results = {
      success: [],
      errors: []
    };

    this.syncProgress.total = symbols.length;
    this.syncProgress.current = 0;
    this.syncProgress.status = 'syncing';

    for (const symbol of symbols) {
      this.syncProgress.current++;
      this.syncProgress.currentSymbol = symbol;

      try {
        await this.updateClosedMonth(symbol);
        results.success.push(symbol);
      } catch (error) {
        results.errors.push({ symbol, error: error.message });
      }

      // Aguardar entre requisições para não sobrecarregar API
      await this.sleep(QuantumConfig.sync.delayBetweenRequests);
    }

    this.syncProgress.status = 'completed';

    console.log(`✅ Sincronização mensal concluída:`);
    console.log(`   - Sucesso: ${results.success.length}`);
    console.log(`   - Erros: ${results.errors.length}`);

    return results;
  }

  /**
   * Importar lista de ações prioritárias ou todas as ações da B3
   */
  async importPriorityStocks(symbols = null) {
    await this.init();

    let stocksToImport;
    
    // Se não especificou símbolos, buscar todas as ações da B3
    if (!symbols || symbols.length === 0) {
      console.log('🔍 Buscando todas as ações da B3...');
      stocksToImport = await this.getAllB3Stocks();
      
      if (stocksToImport.length === 0) {
        console.error('❌ Nenhuma ação encontrada na B3');
        return {
          success: [],
          errors: [{ symbol: 'ALL', error: 'Nenhuma ação encontrada' }],
          skipped: []
        };
      }
    } else {
      stocksToImport = symbols;
    }

    console.log(`🚀 Iniciando importação de ${stocksToImport.length} ações...`);

    const results = {
      success: [],
      errors: [],
      skipped: []
    };

    this.syncProgress.total = stocksToImport.length;
    this.syncProgress.current = 0;
    this.syncProgress.status = 'importing';
    this.syncProgress.percentage = 0;

    for (const symbol of stocksToImport) {
      this.syncProgress.current++;
      this.syncProgress.currentSymbol = symbol;
      this.syncProgress.percentage = Math.round((this.syncProgress.current / this.syncProgress.total) * 100);

      try {
        // Verificar se já existe
        const hasData = await this.db.hasHistoricalData(symbol);
        if (hasData) {
          console.log(`⏭️ ${symbol} já importada, pulando...`);
          results.skipped.push(symbol);
          continue;
        }

        // Importar
        const result = await this.importHistoricalData(symbol, 20);
        if (result.success) {
          results.success.push(symbol);
          console.log(`✅ ${symbol} importada com sucesso (${this.syncProgress.current}/${this.syncProgress.total})`);
        }

        // Aguardar entre requisições (rate limiting)
        await this.sleep(QuantumConfig.sync.delayBetweenRequests);

      } catch (error) {
        console.error(`❌ Erro ao importar ${symbol}:`, error.message);
        results.errors.push({ symbol, error: error.message });
        
        // Se houver muitos erros seguidos, pode ser problema de API
        if (results.errors.length > 10 && results.success.length === 0) {
          console.warn('⚠️ Muitos erros detectados. Verifique sua conexão e token da API.');
        }
      }
    }

    this.syncProgress.status = 'completed';
    this.syncProgress.percentage = 100;

    console.log(`\n📊 Resumo da Importação:`);
    console.log(`   ✅ Sucesso: ${results.success.length}`);
    console.log(`   ⏭️ Puladas: ${results.skipped.length}`);
    console.log(`   ❌ Erros: ${results.errors.length}`);

    return results;
  }

  /**
   * Verificar se precisa atualização mensal
   */
  needsMonthlyUpdate(lastSyncDate) {
    const today = new Date();
    const lastSync = new Date(lastSyncDate);
    
    // Se hoje é dia 02 ou depois, e última sync foi antes do dia 02 deste mês
    if (today.getDate() >= QuantumConfig.sync.monthlyDay) {
      const thisMonthSyncDay = new Date(
        today.getFullYear(), 
        today.getMonth(), 
        QuantumConfig.sync.monthlyDay
      );
      return lastSync < thisMonthSyncDay;
    }

    return false;
  }

  /**
   * Obter último mês fechado (mês anterior)
   */
  getLastClosedMonth() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const lastDay = new Date(lastMonth.getFullYear(), lastMonth.getMonth() + 1, 0);
    return lastDay.toISOString().split('T')[0];
  }

  /**
   * Obter primeiro dia do mês
   */
  getFirstDayOfMonth(dateString) {
    const date = new Date(dateString);
    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
    return firstDay.toISOString().split('T')[0];
  }

  /**
   * Calcular data de início (X anos atrás)
   */
  calculateStartDate(yearsBack) {
    const date = new Date();
    date.setFullYear(date.getFullYear() - yearsBack);
    return date.toISOString().split('T')[0];
  }

  /**
   * Aguardar (para rate limiting)
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Obter progresso atual
   */
  getProgress() {
    return {
      ...this.syncProgress,
      percentage: this.syncProgress.total > 0 
        ? Math.round((this.syncProgress.current / this.syncProgress.total) * 100)
        : 0
    };
  }

  /**
   * Verificar e executar sincronização automática se necessário
   */
  async checkAndSync() {
    await this.init();

    if (!QuantumConfig.sync.autoSync) {
      console.log('ℹ️ Sincronização automática desabilitada');
      return;
    }

    if (!QuantumConfig.isSyncDay()) {
      console.log('ℹ️ Hoje não é dia de sincronização');
      return;
    }

    // Verificar se já sincronizou hoje
    const lastSyncKey = 'quantum_last_auto_sync';
    const lastSync = localStorage.getItem(lastSyncKey);
    const today = new Date().toISOString().split('T')[0];

    if (lastSync === today) {
      console.log('ℹ️ Sincronização automática já executada hoje');
      return;
    }

    console.log('🔄 Executando sincronização automática...');

    try {
      const results = await this.monthlySync();
      
      // Salvar data da última sincronização
      localStorage.setItem(lastSyncKey, today);
      
      // Notificar usuário
      if (window.showToast) {
        window.showToast(
          `✅ Sincronização automática concluída: ${results.success.length} ações atualizadas`,
          'success'
        );
      }

      return results;
    } catch (error) {
      console.error('❌ Erro na sincronização automática:', error);
      if (window.showToast) {
        window.showToast('❌ Erro na sincronização automática', 'error');
      }
    }
  }
}

// Instância global
const quantumSync = new SyncService();

// Verificar sincronização automática ao carregar
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    setTimeout(() => {
      quantumSync.checkAndSync().catch(console.error);
    }, 5000); // Aguardar 5 segundos após carregar a página
  });
}

// Exportar
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SyncService;
} else {
  window.SyncService = SyncService;
  window.quantumSync = quantumSync;
}
