/**
 * Magnus Wealth - ML Service
 * Serviço para integração com modelos de Machine Learning
 */

const API_BASE_URL = 'http://localhost:5000/api';

// ============================================================================
// ANÁLISE DE SENTIMENTO
// ============================================================================

/**
 * Carrega sentimento geral do mercado
 */
async function loadMarketSentiment() {
    const container = document.getElementById('market-sentiment');
    
    try {
        const response = await fetch(`${API_BASE_URL}/ml/sentiment/market?limit=100`);
        const data = await response.json();
        
        if (data.success) {
            const sentiment = data.analysis;
            
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 5rem; margin-bottom: 1rem;">
                        ${sentiment.emoji}
                    </div>
                    <h3 style="font-size: 2rem; color: var(--accent); margin-bottom: 0.5rem;">
                        ${getSentimentLabel(sentiment.sentiment)}
                    </h3>
                    <p style="font-size: 1.2rem; color: var(--text-secondary);">
                        Score: ${sentiment.score} | Confiança: ${(sentiment.confidence * 100).toFixed(0)}%
                    </p>
                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 1rem;">
                        Baseado em ${sentiment.total_messages} mensagens
                    </p>
                </div>
            `;
        } else {
            throw new Error(data.message || 'Erro ao carregar sentimento');
        }
    } catch (error) {
        console.error('Erro ao carregar sentimento do mercado:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--danger);">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <p>Erro ao carregar sentimento do mercado</p>
            </div>
        `;
    }
}

/**
 * Carrega sentimentos por ticker
 */
async function loadTickerSentiments() {
    const container = document.getElementById('ticker-sentiments');
    const tickers = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3'];
    
    try {
        container.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Carregando...</p></div>';
        
        const sentiments = [];
        
        for (const ticker of tickers) {
            try {
                const response = await fetch(`${API_BASE_URL}/ml/sentiment/ticker/${ticker}?limit=50`);
                const data = await response.json();
                
                if (data.success) {
                    sentiments.push(data.analysis);
                }
            } catch (error) {
                console.error(`Erro ao carregar sentimento de ${ticker}:`, error);
            }
        }
        
        if (sentiments.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <p>Nenhum dado de sentimento disponível</p>
                </div>
            `;
            return;
        }
        
        // Renderizar cards
        container.innerHTML = sentiments.map(s => `
            <div class="sentiment-card">
                <div class="sentiment-emoji">${getSentimentEmoji(s.sentiment)}</div>
                <div class="sentiment-ticker">${s.ticker}</div>
                <div class="sentiment-label">${getSentimentLabel(s.sentiment)}</div>
                <div class="sentiment-score">
                    Score: ${s.average_score} | ${s.total_messages} mensagens
                </div>
                <div style="margin-top: 1rem; font-size: 0.85rem; color: var(--text-secondary);">
                    <div>Positivo: ${s.distribution.positive}%</div>
                    <div>Negativo: ${s.distribution.negative}%</div>
                    <div>Neutro: ${s.distribution.neutral}%</div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Erro ao carregar sentimentos:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--danger);">
                <p>Erro ao carregar sentimentos</p>
            </div>
        `;
    }
}

// ============================================================================
// PREVISÃO DE PREÇOS
// ============================================================================

/**
 * Treina modelo de previsão
 */
async function trainPriceModel(ticker, prices) {
    try {
        const response = await fetch(`${API_BASE_URL}/ml/predict/train`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ticker: ticker,
                prices: prices
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erro ao treinar modelo:', error);
        throw error;
    }
}

/**
 * Prevê preços futuros
 */
async function predictPrices(ticker, prices, days = 7) {
    try {
        const response = await fetch(`${API_BASE_URL}/ml/predict/price/${ticker}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prices: prices,
                days: days
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erro ao prever preços:', error);
        throw error;
    }
}

// ============================================================================
// OTIMIZAÇÃO DE PORTFÓLIO
// ============================================================================

/**
 * Otimiza portfólio
 */
async function optimizePortfolio(pricesHistory, riskTolerance = 'moderate') {
    try {
        const response = await fetch(`${API_BASE_URL}/ml/portfolio/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prices_history: pricesHistory,
                risk_tolerance: riskTolerance,
                optimization_type: 'sharpe'
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erro ao otimizar portfólio:', error);
        throw error;
    }
}

/**
 * Renderiza portfólio otimizado
 */
function renderOptimizedPortfolio(portfolio) {
    const container = document.getElementById('optimized-portfolio');
    
    const allocations = portfolio.allocations;
    const metrics = portfolio.portfolio_metrics;
    
    // Preparar dados para gráfico de pizza
    const labels = allocations.map(a => a.ticker);
    const data = allocations.map(a => a.weight);
    
    container.innerHTML = `
        <div class="portfolio-allocation">
            <div class="allocation-chart">
                <canvas id="portfolio-chart"></canvas>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Retorno Esperado</div>
                    <div class="metric-value">${metrics.expected_return}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Volatilidade</div>
                    <div class="metric-value">${metrics.volatility}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Sharpe Ratio</div>
                    <div class="metric-value">${metrics.sharpe_ratio}</div>
                </div>
            </div>
            
            <div class="allocation-list">
                ${allocations.map(a => `
                    <div class="allocation-item">
                        <div>
                            <span class="allocation-ticker">${a.ticker}</span>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                Retorno: ${a.expected_return}% | Risco: ${a.volatility}%
                            </div>
                        </div>
                        <div class="allocation-weight">${a.weight}%</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // Criar gráfico de pizza
    const ctx = document.getElementById('portfolio-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FFD700',
                    '#FFA500',
                    '#FF6347',
                    '#4CAF50',
                    '#2196F3',
                    '#9C27B0'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Retorna emoji do sentimento
 */
function getSentimentEmoji(sentiment) {
    const emojis = {
        'positive': '😊',
        'negative': '😢',
        'neutral': '😐'
    };
    return emojis[sentiment] || '😐';
}

/**
 * Retorna label do sentimento
 */
function getSentimentLabel(sentiment) {
    const labels = {
        'positive': 'Positivo',
        'negative': 'Negativo',
        'neutral': 'Neutro'
    };
    return labels[sentiment] || 'Neutro';
}

// ============================================================================
// EXPORTAR FUNÇÕES
// ============================================================================

window.loadMarketSentiment = loadMarketSentiment;
window.loadTickerSentiments = loadTickerSentiments;
window.trainPriceModel = trainPriceModel;
window.predictPrices = predictPrices;
window.optimizePortfolio = optimizePortfolio;
window.renderOptimizedPortfolio = renderOptimizedPortfolio;

