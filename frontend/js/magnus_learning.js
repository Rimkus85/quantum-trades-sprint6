/**
 * Magnus Learning Integration
 * Sistema de aprendizado do agente Magnus integrado ao frontend
 */

const MagnusLearning = {
    apiUrl: 'http://localhost:5000/api',
    
    /**
     * Aprende com recomendações do Telegram
     */
    async learnFromTelegram(limit = 100) {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/learn-from-telegram?limit=${limit}`);
            const data = await response.json();
            
            if (data.success) {
                console.log('✓ Magnus aprendeu com', data.total_messages, 'mensagens');
                return data;
            } else {
                throw new Error(data.error || 'Erro ao processar aprendizado');
            }
        } catch (error) {
            console.error('Erro ao aprender do Telegram:', error);
            throw error;
        }
    },
    
    /**
     * Obtém recomendações do Magnus
     */
    async getRecommendations(limit = 10) {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/recommendations?limit=${limit}`);
            const data = await response.json();
            
            if (data.success) {
                return data.recommendations;
            } else {
                throw new Error(data.error || 'Erro ao obter recomendações');
            }
        } catch (error) {
            console.error('Erro ao obter recomendações:', error);
            throw error;
        }
    },
    
    /**
     * Obtém recomendação para um ticker específico
     */
    async getTickerRecommendation(ticker) {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/recommendation/${ticker}`);
            const data = await response.json();
            
            if (data.success) {
                return data.recommendation;
            } else {
                throw new Error(data.error || 'Erro ao obter recomendação');
            }
        } catch (error) {
            console.error('Erro ao obter recomendação do ticker:', error);
            throw error;
        }
    },
    
    /**
     * Obtém sugestão de portfolio do Magnus
     */
    async getPortfolioSuggestion(numAssets = 5) {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/portfolio?num_assets=${numAssets}`);
            const data = await response.json();
            
            if (data.success) {
                return data.portfolio;
            } else {
                throw new Error(data.error || 'Erro ao gerar portfolio');
            }
        } catch (error) {
            console.error('Erro ao obter portfolio:', error);
            throw error;
        }
    },
    
    /**
     * Analisa um ticker com Magnus
     */
    async analyzeTicker(ticker) {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/analyze/${ticker}`);
            const data = await response.json();
            
            if (data.success) {
                return data.analysis;
            } else {
                throw new Error(data.error || 'Erro ao analisar ticker');
            }
        } catch (error) {
            console.error('Erro ao analisar ticker:', error);
            throw error;
        }
    },
    
    /**
     * Obtém estatísticas do aprendizado
     */
    async getStatistics() {
        try {
            const response = await fetch(`${this.apiUrl}/magnus/statistics`);
            const data = await response.json();
            
            if (data.success) {
                return data.statistics;
            } else {
                throw new Error(data.error || 'Erro ao obter estatísticas');
            }
        } catch (error) {
            console.error('Erro ao obter estatísticas:', error);
            throw error;
        }
    },
    
    /**
     * Renderiza recomendações na interface
     */
    renderRecommendations(recommendations, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'recommendation-card';
            card.style.cssText = `
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                border-left: 4px solid ${rec.color};
                transition: all 0.3s ease;
            `;
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h3 style="color: #ffd700; font-size: 1.2rem; margin: 0;">${rec.ticker}</h3>
                    <span style="
                        background: ${rec.color};
                        color: white;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.85rem;
                        font-weight: 600;
                    ">${rec.recommendation}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-top: 1rem;">
                    <div>
                        <div style="color: #888; font-size: 0.85rem;">Peso</div>
                        <div style="color: white; font-size: 1.1rem; font-weight: 600;">${(rec.weight * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                        <div style="color: #888; font-size: 0.85rem;">Confiança</div>
                        <div style="color: white; font-size: 1.1rem; font-weight: 600;">${(rec.confidence * 100).toFixed(1)}%</div>
                    </div>
                </div>
            `;
            
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
                card.style.boxShadow = '0 8px 25px rgba(255, 215, 0, 0.2)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = 'none';
            });
            
            container.appendChild(card);
        });
    },
    
    /**
     * Renderiza portfolio sugerido
     */
    renderPortfolio(portfolio, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (portfolio.status !== 'success') {
            container.innerHTML = `
                <div style="
                    background: rgba(255, 193, 7, 0.1);
                    border: 1px solid rgba(255, 193, 7, 0.3);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    color: #ffc107;
                ">
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>${portfolio.message}</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
            ">
                <h3 style="color: #ffd700; margin-bottom: 1rem;">
                    <i class="fas fa-chart-pie"></i> Portfolio Sugerido pelo Magnus
                </h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="text-align: center;">
                        <div style="color: #888; font-size: 0.85rem;">Ativos</div>
                        <div style="color: #ffd700; font-size: 1.5rem; font-weight: 600;">${portfolio.num_assets}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #888; font-size: 0.85rem;">Alocação Total</div>
                        <div style="color: #4caf50; font-size: 1.5rem; font-weight: 600;">${portfolio.total_percentage}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #888; font-size: 0.85rem;">Confiança Média</div>
                        <div style="color: #2196f3; font-size: 1.5rem; font-weight: 600;">${(portfolio.average_confidence * 100).toFixed(1)}%</div>
                    </div>
                </div>
                <div id="portfolio-allocations"></div>
            </div>
        `;
        
        const allocationsContainer = document.getElementById('portfolio-allocations');
        
        portfolio.allocations.forEach(allocation => {
            const item = document.createElement('div');
            item.style.cssText = `
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                border-left: 3px solid #ffd700;
            `;
            
            item.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="color: white; font-weight: 600; font-size: 1.1rem;">${allocation.ticker}</span>
                    <span style="color: #4caf50; font-weight: 600; font-size: 1.2rem;">${allocation.percentage}%</span>
                </div>
                <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; height: 8px; overflow: hidden;">
                    <div style="
                        background: linear-gradient(90deg, #ffd700, #4caf50);
                        height: 100%;
                        width: ${allocation.percentage}%;
                        transition: width 0.5s ease;
                    "></div>
                </div>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.85rem; color: #888;">
                    <span>Peso: ${(allocation.weight * 100).toFixed(1)}%</span>
                    <span>Confiança: ${(allocation.confidence * 100).toFixed(1)}%</span>
                </div>
            `;
            
            allocationsContainer.appendChild(item);
        });
    },
    
    /**
     * Renderiza estatísticas do aprendizado
     */
    renderStatistics(stats, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 1.5rem;
            ">
                <h3 style="color: #ffd700; margin-bottom: 1rem;">
                    <i class="fas fa-brain"></i> Estatísticas de Aprendizado
                </h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                        <div style="color: #888; font-size: 0.85rem;">Recomendações Processadas</div>
                        <div style="color: #ffd700; font-size: 1.8rem; font-weight: 600;">${stats.total_recommendations_processed}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                        <div style="color: #888; font-size: 0.85rem;">Tickers Únicos</div>
                        <div style="color: #4caf50; font-size: 1.8rem; font-weight: 600;">${stats.unique_tickers}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                        <div style="color: #888; font-size: 0.85rem;">Ajustes de Estratégia</div>
                        <div style="color: #2196f3; font-size: 1.8rem; font-weight: 600;">${stats.strategy_adjustments}</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
                        <div style="color: #888; font-size: 0.85rem;">Taxa de Aprendizado</div>
                        <div style="color: #ff9800; font-size: 1.8rem; font-weight: 600;">${(stats.learning_rate * 100).toFixed(0)}%</div>
                    </div>
                </div>
                ${stats.last_update ? `
                    <div style="margin-top: 1rem; text-align: center; color: #888; font-size: 0.85rem;">
                        Última atualização: ${new Date(stats.last_update).toLocaleString('pt-BR')}
                    </div>
                ` : ''}
            </div>
        `;
    },
    
    /**
     * Inicializa sincronização automática
     */
    startAutoSync(intervalMinutes = 60) {
        console.log(`Sincronização automática iniciada (${intervalMinutes} minutos)`);
        
        // Sincronizar imediatamente
        this.learnFromTelegram().catch(console.error);
        
        // Configurar intervalo
        setInterval(() => {
            this.learnFromTelegram().catch(console.error);
        }, intervalMinutes * 60 * 1000);
    }
};

// Exportar para uso global
window.MagnusLearning = MagnusLearning;

