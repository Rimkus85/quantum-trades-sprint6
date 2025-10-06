/**
 * 💾 QUANTUM TRADES - DATABASE SERVICE
 * Gerenciamento de dados históricos no IndexedDB
 * Sprint 6 - Banco de Dados Local
 */

class DatabaseService {
  constructor() {
    this.dbName = 'quantum_trades_db';
    this.dbVersion = 1;
    this.db = null;
    this.isInitialized = false;
  }

  /**
   * Inicializar banco de dados
   */
  async init() {
    if (this.isInitialized && this.db) {
      return this.db;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('❌ Erro ao abrir banco de dados:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        this.isInitialized = true;
        console.log('✅ Banco de dados inicializado');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Store 1: Preços históricos
        if (!db.objectStoreNames.contains('historicalPrices')) {
          const pricesStore = db.createObjectStore('historicalPrices', { keyPath: 'id' });
          pricesStore.createIndex('symbol', 'symbol', { unique: false });
          pricesStore.createIndex('date', 'date', { unique: false });
          pricesStore.createIndex('symbol_date', ['symbol', 'date'], { unique: true });
          console.log('📊 Store "historicalPrices" criado');
        }

        // Store 2: Dividendos
        if (!db.objectStoreNames.contains('dividends')) {
          const dividendsStore = db.createObjectStore('dividends', { keyPath: 'id' });
          dividendsStore.createIndex('symbol', 'symbol', { unique: false });
          dividendsStore.createIndex('paymentDate', 'paymentDate', { unique: false });
          console.log('💰 Store "dividends" criado');
        }

        // Store 3: Fundamentos
        if (!db.objectStoreNames.contains('fundamentals')) {
          const fundamentalsStore = db.createObjectStore('fundamentals', { keyPath: 'id' });
          fundamentalsStore.createIndex('symbol', 'symbol', { unique: false });
          fundamentalsStore.createIndex('period', 'period', { unique: false });
          console.log('📈 Store "fundamentals" criado');
        }

        // Store 4: Metadados de sincronização
        if (!db.objectStoreNames.contains('syncMetadata')) {
          db.createObjectStore('syncMetadata', { keyPath: 'symbol' });
          console.log('⚙️ Store "syncMetadata" criado');
        }

        console.log('🔧 Estrutura do banco criada');
      };
    });
  }

  /**
   * Salvar dados históricos de preços
   */
  async saveHistoricalPrices(symbol, pricesArray) {
    if (!this.db) await this.init();

    const transaction = this.db.transaction(['historicalPrices'], 'readwrite');
    const store = transaction.objectStore('historicalPrices');

    let savedCount = 0;
    const promises = [];

    for (const price of pricesArray) {
      const record = {
        id: `${symbol}_${price.date}`,
        symbol: symbol,
        date: price.date,
        open: price.open,
        high: price.high,
        low: price.low,
        close: price.close,
        volume: price.volume,
        adjustedClose: price.adjustedClose || price.close,
        timestamp: new Date(price.date).getTime()
      };

      const promise = new Promise((resolve, reject) => {
        const request = store.put(record);
        request.onsuccess = () => {
          savedCount++;
          resolve();
        };
        request.onerror = () => reject(request.error);
      });

      promises.push(promise);
    }

    await Promise.all(promises);

    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => {
        console.log(`✅ ${savedCount} registros salvos para ${symbol}`);
        resolve(savedCount);
      };
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Buscar dados históricos de uma ação
   */
  async getHistoricalPrices(symbol, startDate, endDate) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['historicalPrices'], 'readonly');
      const store = transaction.objectStore('historicalPrices');
      const index = store.index('symbol');
      const request = index.getAll(symbol);

      request.onsuccess = () => {
        let results = request.result;

        // Filtrar por data se especificado
        if (startDate || endDate) {
          const start = startDate ? new Date(startDate).getTime() : 0;
          const end = endDate ? new Date(endDate).getTime() : Date.now();

          results = results.filter(r => {
            return r.timestamp >= start && r.timestamp <= end;
          });
        }

        // Ordenar por data
        results.sort((a, b) => a.timestamp - b.timestamp);

        console.log(`📊 ${results.length} registros encontrados para ${symbol}`);
        resolve(results);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Verificar se dados históricos existem
   */
  async hasHistoricalData(symbol) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncMetadata'], 'readonly');
      const store = transaction.objectStore('syncMetadata');
      const request = store.get(symbol);

      request.onsuccess = () => {
        resolve(request.result !== undefined);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Atualizar metadados de sincronização
   */
  async updateSyncMetadata(symbol, dataRange, recordCount) {
    if (!this.db) await this.init();

    const metadata = {
      symbol: symbol,
      lastSync: new Date().toISOString().split('T')[0],
      lastUpdate: Date.now(),
      dataRange: dataRange,
      recordCount: recordCount
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncMetadata'], 'readwrite');
      const store = transaction.objectStore('syncMetadata');
      const request = store.put(metadata);

      request.onsuccess = () => {
        console.log(`✅ Metadados atualizados para ${symbol}`);
        resolve(metadata);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Obter metadados de sincronização
   */
  async getSyncMetadata(symbol) {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncMetadata'], 'readonly');
      const store = transaction.objectStore('syncMetadata');
      const request = store.get(symbol);

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Obter todas as ações sincronizadas
   */
  async getAllSyncedSymbols() {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncMetadata'], 'readonly');
      const store = transaction.objectStore('syncMetadata');
      const request = store.getAll();

      request.onsuccess = () => {
        const symbols = request.result.map(m => m.symbol);
        resolve(symbols);
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Limpar dados antigos (opcional - manutenção)
   */
  async clearOldData(olderThanYears = 25) {
    if (!this.db) await this.init();

    const cutoffDate = new Date();
    cutoffDate.setFullYear(cutoffDate.getFullYear() - olderThanYears);
    const cutoffTimestamp = cutoffDate.getTime();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['historicalPrices'], 'readwrite');
      const store = transaction.objectStore('historicalPrices');
      const request = store.openCursor();
      let deletedCount = 0;

      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          if (cursor.value.timestamp < cutoffTimestamp) {
            cursor.delete();
            deletedCount++;
          }
          cursor.continue();
        }
      };

      transaction.oncomplete = () => {
        console.log(`🗑️ ${deletedCount} registros antigos removidos`);
        resolve(deletedCount);
      };

      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Obter estatísticas do banco
   */
  async getStats() {
    if (!this.db) await this.init();

    const stats = {
      symbols: [],
      totalRecords: 0,
      dateRange: { oldest: null, newest: null },
      size: 0
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncMetadata', 'historicalPrices'], 'readonly');
      
      // Buscar metadados
      const metadataStore = transaction.objectStore('syncMetadata');
      const metadataRequest = metadataStore.getAll();

      metadataRequest.onsuccess = () => {
        stats.symbols = metadataRequest.result.map(m => ({
          symbol: m.symbol,
          records: m.recordCount,
          lastSync: m.lastSync,
          range: m.dataRange
        }));

        stats.totalRecords = stats.symbols.reduce((sum, s) => sum + s.records, 0);

        // Estimar tamanho (aproximado)
        stats.size = (stats.totalRecords * 150) / 1024; // ~150 bytes por registro, em KB

        resolve(stats);
      };

      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Deletar banco de dados (para testes/reset)
   */
  async deleteDatabase() {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.isInitialized = false;
    }

    return new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase(this.dbName);
      
      request.onsuccess = () => {
        console.log('🗑️ Banco de dados deletado');
        resolve();
      };

      request.onerror = () => {
        console.error('❌ Erro ao deletar banco:', request.error);
        reject(request.error);
      };
    });
  }
}

// Instância global
const quantumDB = new DatabaseService();

// Exportar
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DatabaseService;
} else {
  window.DatabaseService = DatabaseService;
  window.quantumDB = quantumDB;
}
