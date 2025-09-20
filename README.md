# 🚀 Quantum Trades - Sprint 6

## Plataforma de Trading Profissional com Dados Reais B3

### ✨ **Funcionalidades Implementadas na Sprint 6**

- **📊 Dados Reais B3**: Integração com APIs reais para cotações em tempo real
- **🔌 WebSockets Escaláveis**: Sistema de streaming para atualizações instantâneas
- **📈 TradingView Charts**: Gráficos profissionais com indicadores técnicos
- **🎛️ Dashboard Profissional**: Interface moderna e responsiva
- **🍔 Menu Hambúrguer**: Navegação completa entre módulos
- **⭐ Watchlist**: Lista personalizada com dados reais da B3
- **🎨 Identidade Visual**: Design consistente com cores oficiais

### 🌐 **Demo Online**

**URL de Produção**: [https://58hpi8cpx01e.manus.space/dashboard_sprint6.html](https://58hpi8cpx01e.manus.space/dashboard_sprint6.html)

### 🛠️ **Tecnologias Utilizadas**

#### Backend
- **Python Flask** - Framework web
- **Yahoo Finance API** - Dados reais da B3
- **WebSockets** - Comunicação em tempo real
- **Redis** - Cache inteligente

#### Frontend
- **HTML5 + CSS3** - Interface moderna
- **JavaScript ES6+** - Funcionalidades interativas
- **TradingView Lightweight Charts** - Gráficos profissionais
- **Font Awesome** - Ícones

### 📁 **Estrutura do Projeto**

```
quantum-trades-sprint6/
├── backend/
│   └── quantum-trades-backend/
│       ├── src/
│       │   ├── main_sprint6.py          # Servidor principal
│       │   ├── routes/
│       │   │   └── sprint6/             # Rotas da Sprint 6
│       │   │       ├── real_market_routes.py
│       │   │       ├── websocket_routes.py
│       │   │       └── tradingview_routes.py
│       │   ├── services/
│       │   │   └── sprint6/             # Serviços da Sprint 6
│       │   │       ├── real_b3_data_service.py
│       │   │       ├── websocket_service.py
│       │   │       └── tradingview_service.py
│       │   └── static/
│       │       ├── dashboard_sprint6.html # Dashboard principal
│       │       └── assets/              # Logos e imagens
│       └── requirements.txt             # Dependências Python
└── frontend/
    └── dashboard_final.html             # Dashboard original
```

### 🚀 **Como Executar**

#### 1. Backend (Flask)
```bash
cd backend/quantum-trades-backend
pip install -r requirements.txt
cd src
python main_sprint6.py
```

#### 2. Acessar Dashboard
```
http://localhost:5000/dashboard_sprint6.html
```

### 📊 **APIs Disponíveis**

#### Dados de Mercado
- `GET /api/market/sprint6/real/quote/{symbol}` - Cotação em tempo real
- `GET /api/market/sprint6/real/historical/{symbol}` - Dados históricos
- `GET /api/market/sprint6/real/status` - Status do mercado

#### WebSocket
- `GET /api/websocket/ws/status` - Status da conexão
- `WS /ws` - Stream de dados em tempo real

#### TradingView
- `GET /api/tradingview/config` - Configuração dos gráficos
- `GET /api/tradingview/symbols` - Lista de símbolos disponíveis

### 🎨 **Identidade Visual**

#### Cores Oficiais
- **Primária**: `#1a1a2e` (Azul escuro)
- **Secundária**: `#16213e` (Azul médio)
- **Destaque**: `#ffd700` (Dourado)

#### Tipografia
- **Fonte**: Inter (Google Fonts)
- **Pesos**: 300, 400, 500, 600, 700

### 📈 **Dados Suportados**

#### Ações B3
- **PETR4** - Petrobras
- **VALE3** - Vale
- **ITUB4** - Itaú Unibanco
- **BBDC4** - Bradesco
- **ABEV3** - Ambev

### 🔧 **Configuração**

#### Variáveis de Ambiente
```bash
FLASK_ENV=production
FLASK_DEBUG=False
REDIS_URL=redis://localhost:6379
API_RATE_LIMIT=100
```

### 📱 **Responsividade**

- **Desktop**: Layout completo com sidebar
- **Tablet**: Menu hambúrguer adaptativo
- **Mobile**: Interface otimizada para touch

### 🛡️ **Segurança**

- **Rate Limiting**: Proteção contra spam
- **CORS**: Configurado para produção
- **Validação**: Sanitização de inputs
- **Cache**: Otimização de performance

### 📝 **Changelog Sprint 6**

#### ✅ Implementado
- [x] Integração com dados reais B3
- [x] Sistema WebSocket escalável
- [x] Gráficos TradingView funcionais
- [x] Menu hambúrguer completo
- [x] Watchlist com dados reais
- [x] Dashboard profissional
- [x] Identidade visual preservada
- [x] Deploy em produção

### 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

### 📞 **Suporte**

Para suporte técnico ou dúvidas sobre implementação, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para o mercado financeiro brasileiro**
