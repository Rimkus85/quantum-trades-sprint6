/**
 * Magnus Wealth - Telegram Service
 * Serviço para integração com API do Telegram
 */

const API_BASE_URL = 'http://localhost:5000/api';

// ============================================================================
// ESTADO GLOBAL
// ============================================================================

let allMessages = [];
let currentFilter = 'all';

// ============================================================================
// FUNÇÕES DE API
// ============================================================================

/**
 * Carrega mensagens do Telegram
 */
async function loadMessages() {
    const refreshBtn = document.getElementById('refresh-btn');
    const messagesList = document.getElementById('messages-list');

    try {
        // Mostrar loading
        refreshBtn.classList.add('loading');
        messagesList.innerHTML = `
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Carregando mensagens...</p>
            </div>
        `;

        // Fazer requisição
        const response = await fetch(`${API_BASE_URL}/telegram/messages?limit=100`);
        const data = await response.json();

        if (data.success) {
            allMessages = data.messages || [];
            renderMessages(allMessages);
        } else {
            throw new Error(data.message || 'Erro ao carregar mensagens');
        }
    } catch (error) {
        console.error('Erro ao carregar mensagens:', error);
        messagesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Erro ao carregar mensagens</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">${error.message}</p>
            </div>
        `;
    } finally {
        refreshBtn.classList.remove('loading');
    }
}

/**
 * Carrega estatísticas do Magnus
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/magnus/statistics`);
        const data = await response.json();

        if (data.success) {
            const stats = data.statistics;

            // Atualizar estatísticas
            document.getElementById('stat-messages').textContent = 
                stats.total_recommendations || '0';
            document.getElementById('stat-tickers').textContent = 
                stats.unique_tickers || '0';
            document.getElementById('stat-buy').textContent = 
                stats.buy_recommendations || '0';
            
            // Última atualização
            const lastUpdate = stats.last_update || 'Nunca';
            if (lastUpdate !== 'Nunca') {
                const date = new Date(lastUpdate);
                const now = new Date();
                const diff = Math.floor((now - date) / 1000 / 60); // minutos
                
                if (diff < 1) {
                    document.getElementById('stat-updated').textContent = 'Agora';
                } else if (diff < 60) {
                    document.getElementById('stat-updated').textContent = `há ${diff} min`;
                } else {
                    const hours = Math.floor(diff / 60);
                    document.getElementById('stat-updated').textContent = `há ${hours}h`;
                }
            } else {
                document.getElementById('stat-updated').textContent = lastUpdate;
            }
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ============================================================================
// FUNÇÕES DE RENDERIZAÇÃO
// ============================================================================

/**
 * Renderiza lista de mensagens
 */
function renderMessages(messages) {
    const messagesList = document.getElementById('messages-list');

    if (!messages || messages.length === 0) {
        messagesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Nenhuma mensagem encontrada</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">
                    Aguarde o processamento de mensagens do Telegram
                </p>
            </div>
        `;
        return;
    }

    // Renderizar mensagens
    messagesList.innerHTML = messages.map(msg => renderMessage(msg)).join('');
}

/**
 * Renderiza uma mensagem individual
 */
function renderMessage(message) {
    const action = detectAction(message.text || message.message || '');
    const ticker = detectTicker(message.text || message.message || '');
    const source = message.source || message.group || 'Telegram';
    const time = formatTime(message.date || message.timestamp);

    return `
        <div class="message-card ${action}">
            <div class="message-header">
                <span class="ticker-badge ${action}">${ticker || 'N/A'}</span>
                <span class="action-badge ${action}">${getActionLabel(action)}</span>
            </div>
            <div class="message-body">
                ${truncateText(message.text || message.message || 'Sem conteúdo', 200)}
            </div>
            <div class="message-footer">
                <span class="message-source">
                    <i class="fab fa-telegram"></i>
                    ${source}
                </span>
                <span class="message-time">${time}</span>
            </div>
        </div>
    `;
}

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Detecta ação (compra/venda/manutenção) no texto
 */
function detectAction(text) {
    const textLower = text.toLowerCase();

    if (textLower.includes('compra') || textLower.includes('buy') || 
        textLower.includes('entrada') || textLower.includes('adiciona')) {
        return 'buy';
    }

    if (textLower.includes('venda') || textLower.includes('sell') || 
        textLower.includes('saída') || textLower.includes('remove')) {
        return 'sell';
    }

    if (textLower.includes('manutenção') || textLower.includes('hold') || 
        textLower.includes('mantém') || textLower.includes('manter')) {
        return 'hold';
    }

    return 'hold'; // Padrão
}

/**
 * Detecta ticker no texto
 */
function detectTicker(text) {
    // Regex para tickers brasileiros (4 letras + número)
    const tickerRegex = /\b([A-Z]{4}\d{1,2})\b/g;
    const matches = text.match(tickerRegex);

    if (matches && matches.length > 0) {
        return matches[0]; // Retorna primeiro ticker encontrado
    }

    return null;
}

/**
 * Retorna label da ação
 */
function getActionLabel(action) {
    const labels = {
        'buy': 'COMPRA',
        'sell': 'VENDA',
        'hold': 'MANUTENÇÃO'
    };
    return labels[action] || 'NEUTRO';
}

/**
 * Formata timestamp
 */
function formatTime(timestamp) {
    if (!timestamp) return 'Data desconhecida';

    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60); // minutos

    if (diff < 1) {
        return 'Agora';
    } else if (diff < 60) {
        return `há ${diff} min`;
    } else if (diff < 1440) {
        const hours = Math.floor(diff / 60);
        return `há ${hours}h`;
    } else {
        const days = Math.floor(diff / 1440);
        return `há ${days}d`;
    }
}

/**
 * Trunca texto
 */
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Filtra mensagens
 */
function filterMessages(filter) {
    currentFilter = filter;

    if (filter === 'all') {
        renderMessages(allMessages);
        return;
    }

    const filtered = allMessages.filter(msg => {
        const text = (msg.text || msg.message || '').toLowerCase();

        if (filter === 'carteiras') {
            return text.includes('carteira') || text.includes('portfolio') || 
                   text.includes('recomenda');
        }

        if (filter === 'opcoes') {
            return text.includes('opção') || text.includes('opcao') || 
                   text.includes('call') || text.includes('put');
        }

        return true;
    });

    renderMessages(filtered);
}

// ============================================================================
// EXPORTAR FUNÇÕES
// ============================================================================

// Tornar funções disponíveis globalmente
window.loadMessages = loadMessages;
window.loadStatistics = loadStatistics;
window.filterMessages = filterMessages;

