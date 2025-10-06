/**
 * Serviço de Portfólio - Quantum Finance
 * Gerencia dados e operações do portfólio do usuário
 */

class PortfolioService {
    constructor() {
        this.portfolio = {
            assets: [],
            transactions: [],
            totalValue: 0,
            totalInvested: 0,
            totalReturn: 0,
            returnPercentage: 0
        };
        
        this.storageKey = 'quantum_finance_portfolio';
        this.loadPortfolio();
    }

    /**
     * Carrega portfólio do localStorage
     */
    loadPortfolio() {
        try {
            const savedPortfolio = localStorage.getItem(this.storageKey);
            if (savedPortfolio) {
                this.portfolio = { ...this.portfolio, ...JSON.parse(savedPortfolio) };
            } else {
                // Criar portfólio demo se não existir
                this.createDemoPortfolio();
            }
        } catch (error) {
            console.error('Erro ao carregar portfólio:', error);
            this.createDemoPortfolio();
        }
    }

    /**
     * Salva portfólio no localStorage
     */
    savePortfolio() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.portfolio));
        } catch (error) {
            console.error('Erro ao salvar portfólio:', error);
        }
    }

    /**
     * Cria portfólio de demonstração
     */
    createDemoPortfolio() {
        const demoAssets = [
            {
                id: 1,
                symbol: 'PETR4',
                name: 'Petrobras PN',
                type: 'stock',
                sector: 'Energia',
                quantity: 100,
                averagePrice: 28.50,
                currentPrice: 32.15,
                totalValue: 3215.00,
                totalInvested: 2850.00,
                return: 365.00,
                returnPercentage: 12.81,
                dividendYield: 8.5
            },
            {
                id: 2,
                symbol: 'VALE3',
                name: 'Vale ON',
                type: 'stock',
                sector: 'Mineração',
                quantity: 50,
                averagePrice: 65.20,
                currentPrice: 71.80,
                totalValue: 3590.00,
                totalInvested: 3260.00,
                return: 330.00,
                returnPercentage: 10.12,
                dividendYield: 12.3
            },
            {
                id: 3,
                symbol: 'ITUB4',
                name: 'Itaú Unibanco PN',
                type: 'stock',
                sector: 'Financeiro',
                quantity: 200,
                averagePrice: 24.80,
                currentPrice: 26.45,
                totalValue: 5290.00,
                totalInvested: 4960.00,
                return: 330.00,
                returnPercentage: 6.65,
                dividendYield: 6.8
            },
            {
                id: 4,
                symbol: 'HGLG11',
                name: 'CSHG Logística FII',
                type: 'fii',
                sector: 'Logística',
                quantity: 30,
                averagePrice: 145.60,
                currentPrice: 152.30,
                totalValue: 4569.00,
                totalInvested: 4368.00,
                return: 201.00,
                returnPercentage: 4.60,
                dividendYield: 9.2
            }
        ];

        const demoTransactions = [
            {
                id: 1,
                symbol: 'PETR4',
                type: 'buy',
                quantity: 100,
                price: 28.50,
                total: 2850.00,
                date: '2024-01-15',
                fees: 15.00
            },
            {
                id: 2,
                symbol: 'VALE3',
                type: 'buy',
                quantity: 50,
                price: 65.20,
                total: 3260.00,
                date: '2024-02-10',
                fees: 18.50
            },
            {
                id: 3,
                symbol: 'ITUB4',
                type: 'buy',
                quantity: 200,
                price: 24.80,
                total: 4960.00,
                date: '2024-03-05',
                fees: 22.30
            },
            {
                id: 4,
                symbol: 'HGLG11',
                type: 'buy',
                quantity: 30,
                price: 145.60,
                total: 4368.00,
                date: '2024-04-20',
                fees: 25.80
            }
        ];

        this.portfolio.assets = demoAssets;
        this.portfolio.transactions = demoTransactions;
        this.calculatePortfolioMetrics();
        this.savePortfolio();
    }

    /**
     * Calcula métricas do portfólio
     */
    calculatePortfolioMetrics() {
        this.portfolio.totalValue = this.portfolio.assets.reduce((sum, asset) => sum + asset.totalValue, 0);
        this.portfolio.totalInvested = this.portfolio.assets.reduce((sum, asset) => sum + asset.totalInvested, 0);
        this.portfolio.totalReturn = this.portfolio.totalValue - this.portfolio.totalInvested;
        this.portfolio.returnPercentage = this.portfolio.totalInvested > 0 
            ? (this.portfolio.totalReturn / this.portfolio.totalInvested) * 100 
            : 0;
    }

    /**
     * Adiciona novo ativo ao portfólio
     */
    async addAsset(assetData) {
        try {
            // Simular busca de dados do ativo
            await this.delay(1000);
            
            const existingAsset = this.portfolio.assets.find(asset => asset.symbol === assetData.symbol);
            
            if (existingAsset) {
                // Atualizar ativo existente (preço médio)
                const totalQuantity = existingAsset.quantity + assetData.quantity;
                const totalInvested = existingAsset.totalInvested + (assetData.quantity * assetData.price);
                const newAveragePrice = totalInvested / totalQuantity;
                
                existingAsset.quantity = totalQuantity;
                existingAsset.averagePrice = newAveragePrice;
                existingAsset.totalInvested = totalInvested;
                existingAsset.totalValue = totalQuantity * existingAsset.currentPrice;
                existingAsset.return = existingAsset.totalValue - existingAsset.totalInvested;
                existingAsset.returnPercentage = (existingAsset.return / existingAsset.totalInvested) * 100;
            } else {
                // Adicionar novo ativo
                const newAsset = {
                    id: Date.now(),
                    symbol: assetData.symbol.toUpperCase(),
                    name: assetData.name || assetData.symbol,
                    type: this.getAssetType(assetData.symbol),
                    sector: assetData.sector || 'Outros',
                    quantity: assetData.quantity,
                    averagePrice: assetData.price,
                    currentPrice: assetData.price, // Simular preço atual igual ao de compra
                    totalValue: assetData.quantity * assetData.price,
                    totalInvested: assetData.quantity * assetData.price,
                    return: 0,
                    returnPercentage: 0,
                    dividendYield: Math.random() * 10 + 2 // Simular dividend yield
                };
                
                this.portfolio.assets.push(newAsset);
            }
            
            // Adicionar transação
            const transaction = {
                id: Date.now(),
                symbol: assetData.symbol.toUpperCase(),
                type: 'buy',
                quantity: assetData.quantity,
                price: assetData.price,
                total: assetData.quantity * assetData.price,
                date: assetData.date,
                fees: (assetData.quantity * assetData.price) * 0.005 // 0.5% de taxa
            };
            
            this.portfolio.transactions.unshift(transaction);
            
            this.calculatePortfolioMetrics();
            this.savePortfolio();
            
            return { success: true, message: 'Ativo adicionado com sucesso!' };
            
        } catch (error) {
            return { success: false, message: 'Erro ao adicionar ativo: ' + error.message };
        }
    }

    /**
     * Remove ativo do portfólio
     */
    removeAsset(assetId) {
        const assetIndex = this.portfolio.assets.findIndex(asset => asset.id === assetId);
        if (assetIndex !== -1) {
            this.portfolio.assets.splice(assetIndex, 1);
            this.calculatePortfolioMetrics();
            this.savePortfolio();
            return { success: true, message: 'Ativo removido com sucesso!' };
        }
        return { success: false, message: 'Ativo não encontrado!' };
    }

    /**
     * Atualiza preços dos ativos (simulado)
     */
    async updatePrices() {
        try {
            await this.delay(2000);
            
            this.portfolio.assets.forEach(asset => {
                // Simular variação de preço (-5% a +5%)
                const variation = (Math.random() - 0.5) * 0.1;
                asset.currentPrice = asset.averagePrice * (1 + variation);
                asset.totalValue = asset.quantity * asset.currentPrice;
                asset.return = asset.totalValue - asset.totalInvested;
                asset.returnPercentage = (asset.return / asset.totalInvested) * 100;
            });
            
            this.calculatePortfolioMetrics();
            this.savePortfolio();
            
            return { success: true, message: 'Preços atualizados com sucesso!' };
            
        } catch (error) {
            return { success: false, message: 'Erro ao atualizar preços: ' + error.message };
        }
    }

    /**
     * Obtém dados do portfólio
     */
    getPortfolio() {
        return this.portfolio;
    }

    /**
     * Obtém diversificação por setor
     */
    getSectorDiversification() {
        const sectors = {};
        
        this.portfolio.assets.forEach(asset => {
            if (!sectors[asset.sector]) {
                sectors[asset.sector] = 0;
            }
            sectors[asset.sector] += asset.totalValue;
        });
        
        return Object.entries(sectors).map(([sector, value]) => ({
            sector,
            value,
            percentage: (value / this.portfolio.totalValue) * 100
        }));
    }

    /**
     * Obtém alocação por ativo
     */
    getAssetAllocation() {
        return this.portfolio.assets.map(asset => ({
            symbol: asset.symbol,
            name: asset.name,
            value: asset.totalValue,
            percentage: (asset.totalValue / this.portfolio.totalValue) * 100
        }));
    }

    /**
     * Determina tipo do ativo baseado no símbolo
     */
    getAssetType(symbol) {
        if (symbol.includes('11')) return 'fii';
        if (symbol.includes('BTC') || symbol.includes('ETH')) return 'crypto';
        return 'stock';
    }

    /**
     * Exporta portfólio para CSV
     */
    exportToCSV() {
        const headers = ['Símbolo', 'Nome', 'Quantidade', 'Preço Médio', 'Preço Atual', 'Valor Total', 'Rentabilidade %'];
        const rows = this.portfolio.assets.map(asset => [
            asset.symbol,
            asset.name,
            asset.quantity,
            asset.averagePrice.toFixed(2),
            asset.currentPrice.toFixed(2),
            asset.totalValue.toFixed(2),
            asset.returnPercentage.toFixed(2)
        ]);
        
        const csvContent = [headers, ...rows]
            .map(row => row.join(','))
            .join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `portfolio_quantum_finance_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    /**
     * Simula delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Filtra ativos por tipo
     */
    filterAssets(type) {
        if (type === 'all') return this.portfolio.assets;
        return this.portfolio.assets.filter(asset => asset.type === type);
    }

    /**
     * Busca ativos por símbolo ou nome
     */
    searchAssets(query) {
        if (!query) return this.portfolio.assets;
        
        const searchTerm = query.toLowerCase();
        return this.portfolio.assets.filter(asset => 
            asset.symbol.toLowerCase().includes(searchTerm) ||
            asset.name.toLowerCase().includes(searchTerm)
        );
    }
}

// Instância global do serviço de portfólio
window.portfolioService = new PortfolioService();

