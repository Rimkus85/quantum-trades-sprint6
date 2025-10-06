/**
 * Hybrid Data Service - Quantum Trades
 * Combina dados históricos (banco local) + dados atuais (brapi.dev)
 */

class HybridDataService {
    constructor() {
        this.localAPI = 'https://5000-iu9xdjz7njtmlqv6r3thq-474a425c.manusvm.computer/api';
        this.brapiAPI = 'https://brapi.dev/api';
        this.brapiToken = localStorage.getItem('brapi_token') || '';
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos para dados atuais
    }

    /**
     * Configurar token da brapi
     */
    setToken(token) {
        this.brapiToken = token;
        localStorage.setItem('brapi_token', token);
    }

    /**
     * Obter cotação atual (brapi.dev)
     */
    async getCurrentQuote(symbol) {
        const cacheKey = `current_${symbol}`;
        
        // Verificar cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            const url = this.brapiToken 
                ? `${this.brapiAPI}/quote/${symbol}?token=${this.brapiToken}`
                : `${this.brapiAPI}/quote/${symbol}`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                const quote = data.results[0];
                
                const result = {
                    symbol: quote.symbol,
                    name: quote.longName || quote.shortName,
                    price: quote.regularMarketPrice,
                    change: quote.regularMarketChangePercent,
                    open: quote.regularMarketOpen,
                    high: quote.regularMarketDayHigh,
                    low: quote.regularMarketDayLow,
                    volume: quote.regularMarketVolume,
                    date: new Date().toISOString().split('T')[0],
                    source: 'brapi_current'
                };
                
                // Armazenar em cache
                this.cache.set(cacheKey, {
                    data: result,
                    timestamp: Date.now()
                });
                
                return result;
            }
            
            return null;
        } catch (error) {
            console.error('Erro ao buscar cotação atual:', error);
            return null;
        }
    }

    /**
     * Obter dados históricos (banco local)
     */
    async getHistoricalData(symbol, options = {}) {
        try {
            let endpoint = `${this.localAPI}/stock/${symbol}`;
            const params = new URLSearchParams();
            
            if (options.startDate) params.append('start_date', options.startDate);
            if (options.endDate) params.append('end_date', options.endDate);
            if (options.limit) params.append('limit', options.limit);
            
            const queryString = params.toString();
            if (queryString) {
                endpoint += `?${queryString}`;
            }
            
            const response = await fetch(endpoint);
            const data = await response.json();
            
            if (data.success) {
                return {
                    symbol: data.symbol,
                    name: data.name,
                    prices: data.prices,
                    source: 'local_historical'
                };
            }
            
            return null;
        } catch (error) {
            console.error('Erro ao buscar dados históricos:', error);
            return null;
        }
    }

    /**
     * Obter cotação completa (híbrido: atual + histórico)
     */
    async getCompleteQuote(symbol) {
        try {
            // Buscar cotação atual (brapi)
            const current = await this.getCurrentQuote(symbol);
            
            // Buscar últimos 30 dias do histórico (banco local)
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            
            const historical = await this.getHistoricalData(symbol, {
                startDate: thirtyDaysAgo.toISOString().split('T')[0],
                limit: 30
            });
            
            // Combinar dados
            return {
                current: current,
                historical: historical,
                symbol: symbol,
                hasCurrentData: !!current,
                hasHistoricalData: !!historical
            };
        } catch (error) {
            console.error('Erro ao buscar cotação completa:', error);
            return null;
        }
    }

    /**
     * Obter cotação (prioriza atual, fallback para histórico)
     */
    async getQuote(symbol) {
        // Tentar buscar cotação atual
        const current = await this.getCurrentQuote(symbol);
        if (current) {
            return current;
        }
        
        // Fallback: buscar última cotação do histórico
        try {
            const response = await fetch(`${this.localAPI}/stock/${symbol}/latest`);
            const data = await response.json();
            
            if (data.success) {
                return {
                    symbol: data.symbol,
                    name: data.name,
                    price: data.close,
                    change: ((data.close - data.open) / data.open * 100).toFixed(2),
                    open: data.open,
                    high: data.high,
                    low: data.low,
                    volume: data.volume,
                    date: data.date,
                    source: 'local_latest'
                };
            }
        } catch (error) {
            console.error('Erro ao buscar última cotação:', error);
        }
        
        return null;
    }

    /**
     * Obter dados para análise técnica
     * Combina histórico (banco) + atual (brapi)
     */
    async getAnalysisData(symbol, period = '1y') {
        try {
            // Buscar histórico do período
            const response = await fetch(`${this.localAPI}/stock/${symbol}/period?period=${period}`);
            const data = await response.json();
            
            if (!data.success) {
                return null;
            }
            
            const prices = data.prices;
            
            // Buscar cotação atual e adicionar se for mais recente
            const current = await this.getCurrentQuote(symbol);
            if (current && prices.length > 0) {
                const lastDate = prices[prices.length - 1].date;
                const currentDate = current.date;
                
                if (currentDate > lastDate) {
                    prices.push({
                        date: current.date,
                        open: current.open,
                        high: current.high,
                        low: current.low,
                        close: current.price,
                        volume: current.volume,
                        trades: 0
                    });
                }
            }
            
            return {
                symbol: data.symbol,
                name: data.name,
                period: period,
                prices: prices,
                totalRecords: prices.length,
                source: 'hybrid'
            };
        } catch (error) {
            console.error('Erro ao buscar dados para análise:', error);
            return null;
        }
    }

    /**
     * Verificar status das APIs
     */
    async checkStatus() {
        const status = {
            local: false,
            brapi: false,
            timestamp: new Date().toISOString()
        };
        
        // Verificar API local
        try {
            const response = await fetch(`${this.localAPI}/health`);
            const data = await response.json();
            status.local = data.status === 'ok';
        } catch (error) {
            status.local = false;
        }
        
        // Verificar brapi
        try {
            const response = await fetch(`${this.brapiAPI}/quote/PETR4`);
            status.brapi = response.ok;
        } catch (error) {
            status.brapi = false;
        }
        
        return status;
    }

    /**
     * Obter estatísticas do banco local
     */
    async getLocalStats() {
        try {
            const response = await fetch(`${this.localAPI}/stats`);
            const data = await response.json();
            
            if (data.success) {
                return data.stats;
            }
            
            return null;
        } catch (error) {
            console.error('Erro ao buscar estatísticas:', error);
            return null;
        }
    }

    /**
     * Limpar cache
     */
    clearCache() {
        this.cache.clear();
    }
}

// Criar instância global
const quantumHybridData = new HybridDataService();
