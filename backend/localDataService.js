/**
 * Local Data Service - Integração com API Flask local
 * Usa dados históricos da B3 (2005-2025) armazenados em SQLite
 */

class LocalDataService {
    constructor() {
        this.baseURL = 'https://5000-iu9xdjz7njtmlqv6r3thq-474a425c.manusvm.computer/api';
        this.cache = new Map();
        this.cacheTimeout = 30 * 60 * 1000; // 30 minutos
    }

    /**
     * Fazer requisição à API local
     */
    async request(endpoint) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    /**
     * Verificar saúde da API
     */
    async checkHealth() {
        try {
            const data = await this.request('/health');
            return data.status === 'ok';
        } catch (error) {
            return false;
        }
    }

    /**
     * Obter estatísticas do banco
     */
    async getStats() {
        try {
            const data = await this.request('/stats');
            return data.stats;
        } catch (error) {
            console.error('Erro ao obter estatísticas:', error);
            return null;
        }
    }

    /**
     * Listar todas as ações disponíveis
     */
    async listStocks() {
        const cacheKey = 'stocks_list';
        
        // Verificar cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const data = await this.request('/stocks');
            
            // Armazenar em cache
            this.cache.set(cacheKey, {
                data: data.stocks,
                timestamp: Date.now()
            });
            
            return data.stocks;
        } catch (error) {
            console.error('Erro ao listar ações:', error);
            return [];
        }
    }

    /**
     * Obter última cotação de uma ação
     */
    async getLatestQuote(symbol) {
        try {
            const data = await this.request(`/stock/${symbol}/latest`);
            if (!data.success) {
                throw new Error(data.error);
            }
            return {
                symbol: data.symbol,
                name: data.name,
                price: data.close,
                open: data.open,
                high: data.high,
                low: data.low,
                volume: data.volume,
                date: data.date,
                change: ((data.close - data.open) / data.open * 100).toFixed(2)
            };
        } catch (error) {
            console.error(`Erro ao obter cotação de ${symbol}:`, error);
            return null;
        }
    }

    /**
     * Obter dados históricos de uma ação
     * @param {string} symbol - Código da ação
     * @param {object} options - Opções: startDate, endDate, limit
     */
    async getHistoricalData(symbol, options = {}) {
        try {
            let endpoint = `/stock/${symbol}`;
            const params = new URLSearchParams();
            
            if (options.startDate) params.append('start_date', options.startDate);
            if (options.endDate) params.append('end_date', options.endDate);
            if (options.limit) params.append('limit', options.limit);
            
            const queryString = params.toString();
            if (queryString) {
                endpoint += `?${queryString}`;
            }
            
            const data = await this.request(endpoint);
            if (!data.success) {
                throw new Error(data.error);
            }
            
            return {
                symbol: data.symbol,
                name: data.name,
                prices: data.prices
            };
        } catch (error) {
            console.error(`Erro ao obter histórico de ${symbol}:`, error);
            return null;
        }
    }

    /**
     * Obter dados de um período específico
     * @param {string} symbol - Código da ação
     * @param {string} period - Período: 1m, 3m, 6m, 1y, 5y, max
     */
    async getPeriodData(symbol, period = '1y') {
        try {
            const data = await this.request(`/stock/${symbol}/period?period=${period}`);
            if (!data.success) {
                throw new Error(data.error);
            }
            
            return {
                symbol: data.symbol,
                name: data.name,
                period: data.period,
                prices: data.prices
            };
        } catch (error) {
            console.error(`Erro ao obter período de ${symbol}:`, error);
            return null;
        }
    }

    /**
     * Calcular indicadores técnicos
     */
    calculateIndicators(prices) {
        if (!prices || prices.length === 0) return null;

        const closes = prices.map(p => p.close);
        const volumes = prices.map(p => p.volume);

        return {
            rsi: this.calculateRSI(closes),
            sma20: this.calculateSMA(closes, 20),
            sma50: this.calculateSMA(closes, 50),
            sma200: this.calculateSMA(closes, 200),
            avgVolume: volumes.reduce((a, b) => a + b, 0) / volumes.length
        };
    }

    /**
     * Calcular RSI (Relative Strength Index)
     */
    calculateRSI(prices, period = 14) {
        if (prices.length < period + 1) return null;

        const changes = [];
        for (let i = 1; i < prices.length; i++) {
            changes.push(prices[i] - prices[i - 1]);
        }

        let gains = 0;
        let losses = 0;

        for (let i = 0; i < period; i++) {
            if (changes[i] > 0) gains += changes[i];
            else losses += Math.abs(changes[i]);
        }

        let avgGain = gains / period;
        let avgLoss = losses / period;

        for (let i = period; i < changes.length; i++) {
            const change = changes[i];
            if (change > 0) {
                avgGain = (avgGain * (period - 1) + change) / period;
                avgLoss = (avgLoss * (period - 1)) / period;
            } else {
                avgGain = (avgGain * (period - 1)) / period;
                avgLoss = (avgLoss * (period - 1) + Math.abs(change)) / period;
            }
        }

        if (avgLoss === 0) return 100;
        const rs = avgGain / avgLoss;
        return 100 - (100 / (1 + rs));
    }

    /**
     * Calcular SMA (Simple Moving Average)
     */
    calculateSMA(prices, period) {
        if (prices.length < period) return null;
        const slice = prices.slice(-period);
        return slice.reduce((a, b) => a + b, 0) / period;
    }

    /**
     * Limpar cache
     */
    clearCache() {
        this.cache.clear();
    }
}

// Criar instância global
const quantumLocalData = new LocalDataService();
