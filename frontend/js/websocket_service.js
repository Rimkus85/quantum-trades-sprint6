/**
 * Magnus Wealth - WebSocket Service
 * Serviço para conexão WebSocket e cotações em tempo real
 */

// ============================================================================
// CONFIGURAÇÃO
// ============================================================================

const WEBSOCKET_URL = 'http://localhost:5001';

// ============================================================================
// ESTADO GLOBAL
// ============================================================================

let socket = null;
let isConnected = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 segundos

// Callbacks registrados
const priceUpdateCallbacks = new Map();
const connectionCallbacks = [];

// ============================================================================
// CONEXÃO
// ============================================================================

/**
 * Conecta ao servidor WebSocket
 */
function connectWebSocket() {
    if (typeof io === 'undefined') {
        console.error('Socket.IO não está carregado. Adicione o script: https://cdn.socket.io/4.5.4/socket.io.min.js');
        return;
    }

    console.log('Conectando ao WebSocket...');

    socket = io(WEBSOCKET_URL, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: RECONNECT_DELAY,
        reconnectionAttempts: MAX_RECONNECT_ATTEMPTS
    });

    // Event: Conectado
    socket.on('connect', () => {
        console.log('WebSocket conectado!');
        isConnected = true;
        reconnectAttempts = 0;
        
        // Notificar callbacks
        connectionCallbacks.forEach(callback => callback(true));
        
        // Reinscrever em tickers se houver
        if (priceUpdateCallbacks.size > 0) {
            const tickers = Array.from(priceUpdateCallbacks.keys());
            subscribeMultipleTickers(tickers);
        }
    });

    // Event: Desconectado
    socket.on('disconnect', (reason) => {
        console.log('WebSocket desconectado:', reason);
        isConnected = false;
        
        // Notificar callbacks
        connectionCallbacks.forEach(callback => callback(false));
    });

    // Event: Erro de conexão
    socket.on('connect_error', (error) => {
        console.error('Erro de conexão WebSocket:', error);
        reconnectAttempts++;
        
        if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            console.error('Máximo de tentativas de reconexão atingido');
        }
    });

    // Event: Mensagem de conexão confirmada
    socket.on('connected', (data) => {
        console.log('Conexão confirmada:', data.message);
    });

    // Event: Atualização de preço
    socket.on('price_update', (data) => {
        console.log('Atualização de preço:', data);
        
        // Chamar callback registrado para este ticker
        const callback = priceUpdateCallbacks.get(data.ticker);
        if (callback) {
            callback(data);
        }
        
        // Chamar callback global (se existir)
        const globalCallback = priceUpdateCallbacks.get('*');
        if (globalCallback) {
            globalCallback(data);
        }
    });

    // Event: Erro
    socket.on('error', (data) => {
        console.error('Erro do servidor:', data.message);
    });
}

/**
 * Desconecta do WebSocket
 */
function disconnectWebSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
        isConnected = false;
        console.log('WebSocket desconectado manualmente');
    }
}

// ============================================================================
// INSCRIÇÕES
// ============================================================================

/**
 * Inscreve em um ticker para receber atualizações
 */
function subscribeTicker(ticker, callback) {
    if (!socket || !isConnected) {
        console.error('WebSocket não está conectado');
        return false;
    }

    ticker = ticker.toUpperCase();
    
    // Registrar callback
    priceUpdateCallbacks.set(ticker, callback);
    
    // Enviar inscrição
    socket.emit('subscribe', { ticker });
    
    console.log(`Inscrito em ${ticker}`);
    return true;
}

/**
 * Desinscreve de um ticker
 */
function unsubscribeTicker(ticker) {
    if (!socket || !isConnected) {
        console.error('WebSocket não está conectado');
        return false;
    }

    ticker = ticker.toUpperCase();
    
    // Remover callback
    priceUpdateCallbacks.delete(ticker);
    
    // Enviar desinscri��ão
    socket.emit('unsubscribe', { ticker });
    
    console.log(`Desinscrito de ${ticker}`);
    return true;
}

/**
 * Inscreve em múltiplos tickers
 */
function subscribeMultipleTickers(tickers, callback) {
    if (!socket || !isConnected) {
        console.error('WebSocket não está conectado');
        return false;
    }

    // Normalizar tickers
    tickers = tickers.map(t => t.toUpperCase());
    
    // Registrar callbacks
    if (callback) {
        tickers.forEach(ticker => {
            priceUpdateCallbacks.set(ticker, callback);
        });
    }
    
    // Enviar inscrição
    socket.emit('subscribe_multiple', { tickers });
    
    console.log(`Inscrito em ${tickers.length} tickers:`, tickers);
    return true;
}

/**
 * Registra callback global para todas as atualizações
 */
function onPriceUpdate(callback) {
    priceUpdateCallbacks.set('*', callback);
}

/**
 * Registra callback para mudanças de conexão
 */
function onConnectionChange(callback) {
    connectionCallbacks.push(callback);
}

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * Verifica se está conectado
 */
function isWebSocketConnected() {
    return isConnected;
}

/**
 * Retorna lista de tickers inscritos
 */
function getSubscribedTickers() {
    return Array.from(priceUpdateCallbacks.keys()).filter(t => t !== '*');
}

// ============================================================================
// AUTO-INICIALIZAÇÃO
// ============================================================================

// Conectar automaticamente ao carregar o script
if (typeof io !== 'undefined') {
    connectWebSocket();
} else {
    console.warn('Socket.IO não está disponível. Carregue o script antes de usar o WebSocket.');
}

// ============================================================================
// EXPORTAR FUNÇÕES
// ============================================================================

window.WebSocketService = {
    connect: connectWebSocket,
    disconnect: disconnectWebSocket,
    subscribe: subscribeTicker,
    unsubscribe: unsubscribeTicker,
    subscribeMultiple: subscribeMultipleTickers,
    onPriceUpdate: onPriceUpdate,
    onConnectionChange: onConnectionChange,
    isConnected: isWebSocketConnected,
    getSubscribedTickers: getSubscribedTickers
};

