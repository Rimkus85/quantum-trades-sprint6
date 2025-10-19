# 🏗️ ARQUITETURA - FASE 2: VISUALIZAÇÃO E INTERFACE

**Projeto:** Magnus Wealth  
**Versão Alvo:** 7.2.0  
**Data:** 18/10/2025  
**Foco:** Visualização de Dados e Experiência do Usuário

---

## 📋 VISÃO GERAL

A Fase 2 tem como objetivo melhorar significativamente a **experiência visual e interativa** do Magnus Wealth, integrando os dados do Telegram com o dashboard web existente e adicionando gráficos interativos para análise técnica avançada.

---

## 🎯 OBJETIVOS DA FASE 2

1. **Integração Frontend-Telegram:** Criar painéis web para visualizar dados capturados do Telegram
2. **Gráficos Interativos:** Implementar gráficos candlestick com indicadores técnicos
3. **Tempo Real:** Adicionar WebSockets para atualização automática de cotações
4. **Experiência do Usuário:** Melhorar navegação e responsividade

---

## 🏗️ ARQUITETURA PROPOSTA

### Estrutura Atual (v7.1.0)

```
quantum-trades-sprint6/
├── backend/
│   └── quantum-trades-backend/
│       ├── app.py (API Flask)
│       ├── bot_comandos.py (Bot Telegram)
│       ├── analise_diaria.py
│       ├── analise_opcoes.py
│       └── resumo_semanal.py
│
└── frontend/
    ├── dashboard_final.html (76 KB)
    ├── dashboard_sprint6.html (34 KB)
    ├── portfolio.html (16 KB)
    ├── painel_ia.html (25 KB)
    ├── alertas_sistema.html (15 KB)
    └── js/
        └── magnus_learning.js (14 KB)
```

### Estrutura Proposta (v7.2.0)

```
quantum-trades-sprint6/
├── backend/
│   └── quantum-trades-backend/
│       ├── app.py (API Flask - EXPANDIDA)
│       │   └── Novos endpoints:
│       │       ├── /api/telegram/messages
│       │       ├── /api/telegram/carteiras
│       │       ├── /api/telegram/opcoes
│       │       ├── /api/market/quotes (WebSocket)
│       │       └── /api/market/history
│       │
│       ├── bot_comandos.py
│       ├── analise_diaria.py
│       ├── analise_opcoes.py
│       └── resumo_semanal.py
│
└── frontend/
    ├── dashboard_final.html (ATUALIZADO)
    │   └── + Painel Telegram integrado
    │
    ├── painel_telegram.html (NOVO)
    │   └── Visualização de mensagens e carteiras
    │
    ├── graficos_avancados.html (NOVO)
    │   └── Gráficos candlestick + indicadores
    │
    ├── js/
    │   ├── magnus_learning.js
    │   ├── telegram_service.js (NOVO)
    │   ├── charts_service.js (NOVO)
    │   └── websocket_service.js (NOVO)
    │
    └── css/
        └── telegram_panel.css (NOVO)
```

---

## 🔌 COMPONENTES DA FASE 2

### 1. **Painel de Telegram** 📱

**Objetivo:** Visualizar dados capturados do Telegram de forma organizada e interativa.

**Funcionalidades:**
- Listar mensagens recentes dos grupos monitorados
- Filtrar por tipo (carteiras, opções, geral)
- Destacar tickers mencionados
- Mostrar estatísticas de ativos mais mencionados
- Exibir recomendações de compra/venda

**Tecnologias:**
- HTML5 + CSS3 (design responsivo)
- JavaScript Vanilla (sem frameworks pesados)
- API REST (backend Flask)

**Endpoints Necessários:**
```
GET /api/telegram/messages?limit=50&type=carteiras
GET /api/telegram/carteiras/summary
GET /api/telegram/opcoes/recent
GET /api/telegram/stats/tickers
```

**Wireframe:**
```
┌─────────────────────────────────────────────────┐
│  PAINEL TELEGRAM                          [🔄]  │
├─────────────────────────────────────────────────┤
│  Filtros: [Todos] [Carteiras] [Opções]          │
├─────────────────────────────────────────────────┤
│  📊 Estatísticas                                │
│  • Mensagens processadas: 500+                  │
│  • Tickers únicos: 21                           │
│  • Última atualização: há 5 min                 │
├─────────────────────────────────────────────────┤
│  📋 Mensagens Recentes                          │
│  ┌───────────────────────────────────────────┐ │
│  │ 🟢 PETR4 - Recomendação de COMPRA         │ │
│  │ Fonte: Carteira Recomendada               │ │
│  │ Data: 18/10/2025 14:30                    │ │
│  └───────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────┐ │
│  │ 🔴 VALE3 - Desmontagem de opção           │ │
│  │ Fonte: Sala de Opções                     │ │
│  │ Data: 18/10/2025 10:15                    │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 2. **Gráficos Interativos** 📈

**Objetivo:** Fornecer análise técnica visual avançada com gráficos candlestick e indicadores.

**Funcionalidades:**
- Gráficos candlestick (velas japonesas)
- Indicadores técnicos (MA, RSI, MACD, Bollinger)
- Múltiplos timeframes (1min, 5min, 1h, 1d)
- Zoom e pan nos gráficos
- Desenho de linhas de suporte/resistência

**Tecnologias:**
- **Opção 1:** TradingView Lightweight Charts (recomendado)
  - Leve e rápido
  - Gratuito
  - Fácil integração
  
- **Opção 2:** Chart.js + chartjs-chart-financial
  - Mais customizável
  - Open source completo
  - Requer mais configuração

**Decisão:** Usar **TradingView Lightweight Charts** por ser mais adequado para gráficos financeiros.

**Endpoints Necessários:**
```
GET /api/market/history?ticker=PETR4&timeframe=1d&limit=100
GET /api/market/indicators?ticker=PETR4&indicator=MA&period=20
```

**Wireframe:**
```
┌─────────────────────────────────────────────────┐
│  GRÁFICOS AVANÇADOS                             │
├─────────────────────────────────────────────────┤
│  Ativo: [PETR4 ▼]  Timeframe: [1D ▼]           │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐ │
│  │                                           │ │
│  │         📊 GRÁFICO CANDLESTICK            │ │
│  │                                           │ │
│  │  40 ┤                    ╭──╮             │ │
│  │     │         ╭──╮      │  │             │ │
│  │  35 ┤    ╭──╮│  │  ╭──╮│  │             │ │
│  │     │   │  ││  │ │  ││  │             │ │
│  │  30 ┴───┴──┴┴──┴─┴──┴┴──┴─────────────  │ │
│  │     Jan  Fev  Mar  Abr  Mai             │ │
│  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│  Indicadores: [☑ MA20] [☑ RSI] [☐ MACD]        │
└─────────────────────────────────────────────────┘
```

### 3. **WebSockets (Tempo Real)** 🔄

**Objetivo:** Atualizar cotações automaticamente sem refresh da página.

**Funcionalidades:**
- Conexão WebSocket com backend
- Atualização de preços em tempo real
- Reconexão automática em caso de queda
- Indicadores visuais de alta/baixa

**Tecnologias:**
- Flask-SocketIO (backend)
- Socket.IO Client (frontend)

**Fluxo:**
```
Backend (Flask-SocketIO)
    ↓
    ├─ Conecta com API brapi.dev
    ├─ Recebe cotações a cada 15s
    ├─ Emite evento "price_update"
    ↓
Frontend (Socket.IO Client)
    ├─ Escuta evento "price_update"
    ├─ Atualiza DOM com novo preço
    └─ Mostra animação de alta/baixa
```

**Código de Exemplo:**
```javascript
// Frontend
const socket = io('http://localhost:5000');

socket.on('price_update', (data) => {
    updatePrice(data.ticker, data.price, data.change);
});

function updatePrice(ticker, price, change) {
    const element = document.getElementById(`price-${ticker}`);
    element.textContent = `R$ ${price.toFixed(2)}`;
    element.className = change > 0 ? 'price-up' : 'price-down';
}
```

---

## 📊 INTEGRAÇÃO COM BACKEND

### Expansão da API Flask

O arquivo `app.py` será expandido com novos endpoints:

```python
# backend/quantum-trades-backend/app.py

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ============================================================================
# ENDPOINTS TELEGRAM
# ============================================================================

@app.route('/api/telegram/messages', methods=['GET'])
def get_telegram_messages():
    """Retorna mensagens do Telegram"""
    limit = request.args.get('limit', 50, type=int)
    tipo = request.args.get('type', 'all')
    
    # Carregar mensagens do arquivo JSON
    messages = load_telegram_messages(tipo, limit)
    
    return jsonify({
        'success': True,
        'count': len(messages),
        'messages': messages
    })

@app.route('/api/telegram/carteiras/summary', methods=['GET'])
def get_carteiras_summary():
    """Retorna resumo das carteiras do Telegram"""
    summary = load_carteiras_summary()
    return jsonify(summary)

@app.route('/api/telegram/opcoes/recent', methods=['GET'])
def get_opcoes_recent():
    """Retorna opções recentes"""
    opcoes = load_opcoes_recent()
    return jsonify(opcoes)

# ============================================================================
# ENDPOINTS MERCADO
# ============================================================================

@app.route('/api/market/history', methods=['GET'])
def get_market_history():
    """Retorna histórico de preços"""
    ticker = request.args.get('ticker', 'PETR4')
    timeframe = request.args.get('timeframe', '1d')
    limit = request.args.get('limit', 100, type=int)
    
    # Buscar dados da API brapi.dev ou IndexedDB
    history = fetch_market_history(ticker, timeframe, limit)
    
    return jsonify(history)

# ============================================================================
# WEBSOCKETS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')
    emit('connected', {'status': 'ok'})

@socketio.on('subscribe')
def handle_subscribe(data):
    """Cliente se inscreve para receber atualizações de um ticker"""
    ticker = data.get('ticker')
    print(f'Cliente inscrito em {ticker}')
    # Adicionar à lista de inscritos

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

# Background task para enviar atualizações
def send_price_updates():
    while True:
        # Buscar preços atualizados
        prices = fetch_current_prices()
        
        # Emitir para todos os clientes
        socketio.emit('price_update', prices)
        
        # Aguardar 15 segundos
        socketio.sleep(15)

if __name__ == '__main__':
    socketio.start_background_task(send_price_updates)
    socketio.run(app, debug=True, port=5000)
```

---

## 🎨 DESIGN E UX

### Paleta de Cores (Mantida)

```css
:root {
    --primary: #1a1a2e;
    --secondary: #16213e;
    --accent: #ffd700;
    --success: #4CAF50;
    --danger: #f44336;
    --warning: #ff9800;
    --text: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
}
```

### Componentes Reutilizáveis

**Card de Mensagem:**
```html
<div class="telegram-message">
    <div class="message-header">
        <span class="ticker">PETR4</span>
        <span class="action buy">COMPRA</span>
    </div>
    <div class="message-body">
        Recomendação de compra baseada em fundamentos...
    </div>
    <div class="message-footer">
        <span class="source">Carteira Recomendada</span>
        <span class="time">há 5 min</span>
    </div>
</div>
```

**Indicador de Preço:**
```html
<div class="price-indicator">
    <span class="ticker">PETR4</span>
    <span class="price" id="price-PETR4">R$ 38.50</span>
    <span class="change positive">+2.5%</span>
</div>
```

---

## 📱 RESPONSIVIDADE

Todos os novos componentes serão **mobile-first**, garantindo boa experiência em:
- Desktop (1920x1080+)
- Tablet (768x1024)
- Mobile (375x667)

**Breakpoints:**
```css
/* Mobile first */
.container { width: 100%; }

/* Tablet */
@media (min-width: 768px) {
    .container { width: 750px; }
}

/* Desktop */
@media (min-width: 1200px) {
    .container { width: 1140px; }
}
```

---

## 🧪 TESTES

### Testes de Integração
- Verificar se endpoints retornam dados corretos
- Validar formato JSON das respostas
- Testar WebSocket (conexão, reconexão, mensagens)

### Testes de UI
- Verificar responsividade em diferentes tamanhos
- Testar interações (cliques, filtros, zoom)
- Validar animações e transições

### Testes de Performance
- Tempo de carregamento < 2s
- Gráficos renderizam em < 500ms
- WebSocket sem lag perceptível

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 2.1: Painel Telegram
- [ ] Criar endpoint `/api/telegram/messages`
- [ ] Criar endpoint `/api/telegram/carteiras/summary`
- [ ] Criar endpoint `/api/telegram/opcoes/recent`
- [ ] Criar `painel_telegram.html`
- [ ] Criar `telegram_service.js`
- [ ] Criar `telegram_panel.css`
- [ ] Integrar com dashboard principal
- [ ] Testar responsividade

### Fase 2.2: Gráficos Interativos
- [ ] Instalar TradingView Lightweight Charts
- [ ] Criar endpoint `/api/market/history`
- [ ] Criar endpoint `/api/market/indicators`
- [ ] Criar `graficos_avancados.html`
- [ ] Criar `charts_service.js`
- [ ] Implementar indicadores (MA, RSI, MACD)
- [ ] Adicionar controles de timeframe
- [ ] Testar performance

### Fase 2.3: WebSockets
- [ ] Instalar Flask-SocketIO
- [ ] Implementar WebSocket server
- [ ] Criar `websocket_service.js`
- [ ] Implementar reconexão automática
- [ ] Adicionar indicadores visuais
- [ ] Testar com múltiplos clientes
- [ ] Otimizar frequência de updates

---

## 🚀 CRONOGRAMA ESTIMADO

| Fase | Descrição | Tempo Estimado |
|---|---|---|
| **2.1** | Painel Telegram | 5-8 horas |
| **2.2** | Gráficos Interativos | 8-13 horas |
| **2.3** | WebSockets | 5-8 horas |
| **Testes** | Validação completa | 2-3 horas |
| **Documentação** | Atualização de docs | 1-2 horas |
| **TOTAL** | | **21-34 horas** |

---

## 🎯 RESULTADO ESPERADO

Ao final da Fase 2, o Magnus Wealth terá:

✅ Interface web moderna e interativa  
✅ Visualização completa dos dados do Telegram  
✅ Gráficos avançados para análise técnica  
✅ Cotações atualizadas em tempo real  
✅ Experiência do usuário significativamente melhorada

---

**Magnus Wealth v7.2.0** - Arquitetura da Fase 2 🏗️

