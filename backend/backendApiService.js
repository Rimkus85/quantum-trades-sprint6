/**
 * 🚀 QUANTUM TRADES - BACKEND API SERVICE
 * Serviço para comunicação com o backend Flask
 */

class BackendApiService {
  constructor() {
    this.baseUrl = window.location.origin + '/api';
    this.token = localStorage.getItem('access_token');
    
    // Configurações
    this.config = {
      timeout: 10000,
      retries: 3
    };
    
    console.log('[BackendApiService] Initialized with base URL:', this.baseUrl);
  }

  /**
   * Configurar token de autenticação
   */
  setToken(token) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  /**
   * Remover token de autenticação
   */
  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  /**
   * Fazer requisição HTTP com retry
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` })
      },
      timeout: this.config.timeout
    };

    const finalOptions = { ...defaultOptions, ...options };

    for (let attempt = 1; attempt <= this.config.retries; attempt++) {
      try {
        console.log(`[BackendApiService] ${finalOptions.method} ${url} (attempt ${attempt})`);
        
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
        
      } catch (error) {
        console.error(`[BackendApiService] Request failed (attempt ${attempt}):`, error);
        
        if (attempt === this.config.retries) {
          throw error;
        }
        
        // Aguardar antes de tentar novamente
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }

  // === AUTENTICAÇÃO ===

  /**
   * Fazer login
   */
  async login(email, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  /**
   * Fazer logout
   */
  async logout() {
    try {
      await this.request('/auth/logout', {
        method: 'POST'
      });
    } catch (error) {
      console.error('[BackendApiService] Logout error:', error);
    } finally {
      this.clearToken();
    }
  }

  /**
   * Obter informações do usuário atual
   */
  async getCurrentUser() {
    return await this.request('/auth/me');
  }

  // === DADOS DE MERCADO ===

  /**
   * Obter cotação de um ativo
   */
  async getQuote(symbol) {
    return await this.request(`/market/quote/${symbol}`);
  }

  /**
   * Obter dados históricos
   */
  async getHistoricalData(symbol, period = '1y') {
    return await this.request(`/market/historical/${symbol}?period=${period}`);
  }

  /**
   * Buscar símbolos
   */
  async searchSymbols(query) {
    return await this.request(`/market/search?q=${encodeURIComponent(query)}`);
  }

  /**
   * Obter resumo do mercado
   */
  async getMarketSummary() {
    return await this.request('/market/summary');
  }

  /**
   * Obter múltiplas cotações
   */
  async getMultipleQuotes(symbols) {
    return await this.request('/market/multiple-quotes', {
      method: 'POST',
      body: JSON.stringify({ symbols })
    });
  }

  /**
   * Obter estatísticas do cache
   */
  async getCacheStats() {
    return await this.request('/market/cache/stats');
  }

  /**
   * Aquecer cache
   */
  async warmCache(symbols = []) {
    return await this.request('/market/cache/warm', {
      method: 'POST',
      body: JSON.stringify({ symbols })
    });
  }

  // === HEALTH CHECK ===

  /**
   * Verificar saúde da API
   */
  async healthCheck() {
    return await this.request('/health');
  }

  /**
   * Verificar saúde do serviço de mercado
   */
  async marketHealthCheck() {
    return await this.request('/market/health');
  }
}

// Instância global
window.backendApi = new BackendApiService();

