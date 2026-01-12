# Integração com Dados Reais de Produção

## Visão Geral

Este documento detalha a arquitetura e os passos necessários para migrar o Quantum Trades de dados mockados para integração com APIs reais de mercado financeiro, seguindo as diretrizes de sistemas financeiros críticos.

---

## 1. Arquitetura de Integração

### 1.1 Camadas do Sistema

```
┌─────────────────────────────────────────┐
│          Mobile App (React Native)       │
│  - Dashboard, Portfólio, Operações      │
└──────────────────┬──────────────────────┘
                   │ tRPC
┌──────────────────▼──────────────────────┐
│       Backend API (FastAPI/Node.js)      │
│  - Autenticação, Autorização            │
│  - Validação de Ordens                  │
│  - Audit Trail                          │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
┌───────▼─────┐ ┌──▼────┐ ┌──▼─────┐
│  OMS/EMS    │ │  B3   │ │ Crypto │
│ (Cedro OMS) │ │  API  │ │  APIs  │
└─────────────┘ └───────┘ └────────┘
```

### 1.2 Princípios Fundamentais

1. **Segurança**: Nunca expor credenciais no frontend
2. **Auditabilidade**: Registrar todas as operações com timestamp
3. **Idempotência**: Ordens duplicadas devem ser detectadas
4. **Validação**: Pré-trade checks antes de enviar ordens
5. **Resiliência**: Retry com backoff exponencial

---

## 2. APIs de Mercado

### 2.1 Ações (B3)

#### Opção 1: Cedro OMS (Recomendado para Produção)
- **Website**: https://cedrotech.com
- **Protocolo**: FIX 4.4 ou REST API
- **Funcionalidades**:
  - Cotações em tempo real
  - Envio de ordens (compra/venda)
  - Book de ofertas
  - Histórico de operações
- **Custo**: Consultar comercial
- **Regulamentação**: Homologado pela CVM e B3

#### Opção 2: Alpha Vantage (Dados Históricos)
- **Website**: https://www.alphavantage.co
- **API Key**: Gratuita (500 req/dia) ou paga
- **Endpoint**: `https://www.alphavantage.co/query`
- **Exemplo**:
  ```bash
  curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=PETR4.SAO&apikey=YOUR_API_KEY"
  ```
- **Limitação**: Delay de 15min (dados gratuitos)

#### Opção 3: Yahoo Finance (Não Oficial)
- **Biblioteca**: `yfinance` (Python)
- **Exemplo**:
  ```python
  import yfinance as yf
  petr4 = yf.Ticker("PETR4.SA")
  price = petr4.history(period="1d")['Close'][0]
  ```
- **Limitação**: Não oficial, pode quebrar sem aviso

### 2.2 Opções (B3)

#### Cedro OMS
- Suporta opções de ações
- Vencimentos, strikes, tipo (call/put)
- Cálculo de gregas (delta, gamma, theta, vega)

#### Dados Históricos
- **Fonte**: B3 (http://www.b3.com.br/pt_br/market-data-e-indices/)
- **Formato**: CSV/TXT
- **Atualização**: Diária (após fechamento)

### 2.3 Criptomoedas

#### Binance API (Recomendado)
- **Website**: https://binance-docs.github.io/apidocs/spot/en/
- **Endpoint**: `https://api.binance.com/api/v3/ticker/price`
- **Exemplo**:
  ```bash
  curl "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
  ```
- **Websocket**: `wss://stream.binance.com:9443/ws/btcusdt@trade`
- **Autenticação**: API Key + Secret (para ordens)

#### Alternativas
- **Coinbase Pro**: https://docs.cloud.coinbase.com
- **Kraken**: https://docs.kraken.com/rest/
- **Mercado Bitcoin**: https://www.mercadobitcoin.com.br/api-doc/

---

## 3. Estrutura de Dados

### 3.1 Schema do Banco de Dados

```sql
-- Tabela de Ativos
CREATE TABLE assets (
  id UUID PRIMARY KEY,
  ticker VARCHAR(20) NOT NULL,
  name VARCHAR(255),
  asset_class VARCHAR(50), -- 'stock', 'option', 'crypto'
  exchange VARCHAR(50), -- 'B3', 'Binance', etc.
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Cotações
CREATE TABLE quotes (
  id UUID PRIMARY KEY,
  asset_id UUID REFERENCES assets(id),
  price DECIMAL(18, 8) NOT NULL,
  volume BIGINT,
  timestamp TIMESTAMP NOT NULL,
  source VARCHAR(50), -- 'cedro', 'binance', etc.
  INDEX idx_asset_timestamp (asset_id, timestamp DESC)
);

-- Tabela de Operações
CREATE TABLE operations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  asset_id UUID REFERENCES assets(id),
  type VARCHAR(10), -- 'buy', 'sell'
  quantity DECIMAL(18, 8) NOT NULL,
  price DECIMAL(18, 8) NOT NULL,
  total DECIMAL(18, 2) NOT NULL,
  status VARCHAR(20), -- 'pending', 'executed', 'cancelled'
  executed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  -- Audit Trail
  created_by UUID,
  ip_address INET,
  user_agent TEXT
);

-- Tabela de Portfólio
CREATE TABLE portfolio (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  asset_id UUID REFERENCES assets(id),
  quantity DECIMAL(18, 8) NOT NULL,
  avg_price DECIMAL(18, 8) NOT NULL,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, asset_id)
);
```

### 3.2 API Endpoints

```typescript
// Backend (FastAPI ou tRPC)

// 1. Cotações em Tempo Real
GET /api/quotes/:ticker
Response: {
  ticker: "PETR4",
  price: 33.85,
  change: 0.60,
  changePercent: 1.8,
  volume: 15234000,
  timestamp: "2026-01-12T10:30:00Z",
  source: "cedro"
}

// 2. Histórico de Performance
GET /api/portfolio/performance?period=1M
Response: {
  data: [
    { date: "2025-12-12", value: 120000.00 },
    { date: "2025-12-19", value: 122500.00 },
    ...
  ]
}

// 3. Criar Ordem
POST /api/orders
Request: {
  ticker: "PETR4",
  type: "buy",
  quantity: 100,
  price: 33.50, // null para ordem a mercado
  orderType: "limit" // "market", "limit", "stop"
}
Response: {
  orderId: "ord_123456",
  status: "pending",
  createdAt: "2026-01-12T10:30:00Z"
}

// 4. Listar Operações
GET /api/operations?limit=20&offset=0
Response: {
  operations: [...],
  total: 150,
  hasMore: true
}
```

---

## 4. Camada de Abstração

### 4.1 Interface Unificada

Criar uma camada de abstração para trocar entre mock e produção sem alterar o frontend:

```typescript
// lib/data-provider.ts

export interface DataProvider {
  getPortfolioSummary(): Promise<PortfolioSummary>;
  getAssetClasses(): Promise<AssetClass[]>;
  getOperations(filters?: OperationFilters): Promise<Operation[]>;
  getPerformance(period: string): Promise<PerformancePoint[]>;
  getQuote(ticker: string): Promise<Quote>;
  createOrder(order: CreateOrderRequest): Promise<Order>;
}

// Mock Provider (atual)
export class MockDataProvider implements DataProvider {
  async getPortfolioSummary() {
    return MOCK_PORTFOLIO;
  }
  // ...
}

// Production Provider (futuro)
export class ProductionDataProvider implements DataProvider {
  constructor(private apiClient: ApiClient) {}
  
  async getPortfolioSummary() {
    const response = await this.apiClient.get('/api/portfolio/summary');
    return response.data;
  }
  // ...
}

// Factory
export function createDataProvider(): DataProvider {
  if (process.env.USE_MOCK_DATA === 'true') {
    return new MockDataProvider();
  }
  return new ProductionDataProvider(apiClient);
}
```

### 4.2 Uso no App

```typescript
// app/(tabs)/index.tsx

import { createDataProvider } from '@/lib/data-provider';

export default function DashboardScreen() {
  const dataProvider = createDataProvider();
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);

  useEffect(() => {
    dataProvider.getPortfolioSummary().then(setPortfolio);
  }, []);

  // ...
}
```

---

## 5. Segurança e Compliance

### 5.1 Autenticação de APIs

```typescript
// server/integrations/cedro-client.ts

import axios from 'axios';

export class CedroClient {
  private apiKey: string;
  private apiSecret: string;

  constructor() {
    // Nunca expor no frontend!
    this.apiKey = process.env.CEDRO_API_KEY!;
    this.apiSecret = process.env.CEDRO_API_SECRET!;
  }

  async getQuote(ticker: string) {
    const signature = this.generateSignature(ticker);
    const response = await axios.get(`${CEDRO_BASE_URL}/quotes/${ticker}`, {
      headers: {
        'X-API-Key': this.apiKey,
        'X-Signature': signature,
      },
    });
    return response.data;
  }

  private generateSignature(data: string): string {
    // HMAC-SHA256
    const crypto = require('crypto');
    return crypto
      .createHmac('sha256', this.apiSecret)
      .update(data)
      .digest('hex');
  }
}
```

### 5.2 Audit Trail

```typescript
// server/middleware/audit.ts

export async function auditMiddleware(req, res, next) {
  const auditLog = {
    userId: req.user.id,
    action: `${req.method} ${req.path}`,
    ipAddress: req.ip,
    userAgent: req.headers['user-agent'],
    timestamp: new Date().toISOString(),
    requestBody: req.body,
  };

  // Salvar no banco
  await db.insert(auditLogs).values(auditLog);

  next();
}
```

### 5.3 Validação de Ordens (Pré-Trade Checks)

```typescript
// server/services/order-validator.ts

export class OrderValidator {
  async validate(order: CreateOrderRequest, user: User): Promise<ValidationResult> {
    const errors: string[] = [];

    // 1. Verificar saldo
    if (order.type === 'buy') {
      const balance = await this.getUserBalance(user.id);
      const requiredAmount = order.quantity * order.price;
      if (balance < requiredAmount) {
        errors.push('Saldo insuficiente');
      }
    }

    // 2. Verificar posição (para venda)
    if (order.type === 'sell') {
      const position = await this.getUserPosition(user.id, order.ticker);
      if (!position || position.quantity < order.quantity) {
        errors.push('Quantidade insuficiente para venda');
      }
    }

    // 3. Verificar horário de mercado
    if (!this.isMarketOpen(order.ticker)) {
      errors.push('Mercado fechado');
    }

    // 4. Verificar limites de risco
    const riskCheck = await this.checkRiskLimits(user.id, order);
    if (!riskCheck.passed) {
      errors.push(riskCheck.message);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
}
```

---

## 6. Websockets para Tempo Real

### 6.1 Backend (Servidor)

```typescript
// server/websocket.ts

import { Server } from 'socket.io';

export function setupWebSocket(httpServer) {
  const io = new Server(httpServer, {
    cors: { origin: '*' },
  });

  io.on('connection', (socket) => {
    console.log('Cliente conectado:', socket.id);

    // Cliente se inscreve em um ticker
    socket.on('subscribe', (ticker: string) => {
      socket.join(`ticker:${ticker}`);
      console.log(`${socket.id} inscrito em ${ticker}`);
    });

    // Cliente cancela inscrição
    socket.on('unsubscribe', (ticker: string) => {
      socket.leave(`ticker:${ticker}`);
    });

    socket.on('disconnect', () => {
      console.log('Cliente desconectado:', socket.id);
    });
  });

  // Broadcast de cotações (exemplo com Binance WebSocket)
  const binanceWs = new WebSocket('wss://stream.binance.com:9443/ws/btcusdt@trade');
  binanceWs.on('message', (data) => {
    const trade = JSON.parse(data);
    io.to('ticker:BTC').emit('quote', {
      ticker: 'BTC',
      price: parseFloat(trade.p),
      timestamp: new Date(trade.T).toISOString(),
    });
  });

  return io;
}
```

### 6.2 Frontend (React Native)

```typescript
// lib/websocket-client.ts

import io from 'socket.io-client';

export class WebSocketClient {
  private socket: any;

  connect() {
    this.socket = io(API_URL, {
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket conectado');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket desconectado');
    });
  }

  subscribe(ticker: string, callback: (quote: Quote) => void) {
    this.socket.emit('subscribe', ticker);
    this.socket.on('quote', (data: Quote) => {
      if (data.ticker === ticker) {
        callback(data);
      }
    });
  }

  unsubscribe(ticker: string) {
    this.socket.emit('unsubscribe', ticker);
  }

  disconnect() {
    this.socket.disconnect();
  }
}
```

---

## 7. Roadmap de Implementação

### Fase 1: Preparação (1-2 semanas)
- [ ] Criar camada de abstração DataProvider
- [ ] Definir schemas do banco de dados
- [ ] Configurar ambiente de staging
- [ ] Contratar APIs (Cedro OMS, Binance, etc.)
- [ ] Configurar secrets e variáveis de ambiente

### Fase 2: Backend (2-3 semanas)
- [ ] Implementar ProductionDataProvider
- [ ] Criar endpoints REST/tRPC
- [ ] Integrar com Cedro OMS (ações e opções)
- [ ] Integrar com Binance API (cripto)
- [ ] Implementar audit trail
- [ ] Implementar validação de ordens
- [ ] Criar testes de integração

### Fase 3: Websockets (1 semana)
- [ ] Configurar servidor WebSocket
- [ ] Integrar com Binance WebSocket
- [ ] Integrar com Cedro streaming (se disponível)
- [ ] Implementar reconexão automática
- [ ] Testar latência e performance

### Fase 4: Frontend (1 semana)
- [ ] Substituir MockDataProvider por ProductionDataProvider
- [ ] Implementar WebSocketClient
- [ ] Adicionar indicadores de "última atualização"
- [ ] Implementar pull-to-refresh
- [ ] Adicionar tratamento de erros de rede

### Fase 5: Testes e Homologação (2 semanas)
- [ ] Testes end-to-end com dados reais
- [ ] Testes de carga e stress
- [ ] Validação com CVM/B3 (se aplicável)
- [ ] Testes de segurança (penetration testing)
- [ ] Documentação final

### Fase 6: Deploy Gradual (1 semana)
- [ ] Deploy em staging
- [ ] Beta testing com usuários selecionados
- [ ] Monitoramento de métricas (latência, erros)
- [ ] Deploy em produção (canary release)
- [ ] Rollback plan

---

## 8. Custos Estimados

| Serviço | Custo Mensal | Observações |
|---------|--------------|-------------|
| Cedro OMS | R$ 500 - R$ 2.000 | Depende do volume |
| Binance API | Gratuito | Taxas de trading aplicam |
| Alpha Vantage Premium | US$ 50 | 1.200 req/min |
| Servidor (AWS/GCP) | R$ 200 - R$ 500 | 2-4 vCPUs, 8GB RAM |
| Banco de Dados | R$ 100 - R$ 300 | PostgreSQL gerenciado |
| **Total** | **R$ 850 - R$ 3.300** | |

---

## 9. Monitoramento e Alertas

### 9.1 Métricas Críticas

- **Latência de APIs**: < 200ms (p95)
- **Taxa de Erro**: < 0.1%
- **Uptime**: > 99.9%
- **Delay de Cotações**: < 1s (tempo real)

### 9.2 Ferramentas

- **Sentry**: Rastreamento de erros
- **Datadog/New Relic**: Monitoramento de performance
- **PagerDuty**: Alertas críticos
- **Grafana**: Dashboards customizados

---

## 10. Próximos Passos Imediatos

1. **Definir prioridade**: Ações, Opções ou Cripto primeiro?
2. **Contratar APIs**: Iniciar processo comercial com Cedro OMS
3. **Criar conta de teste**: Binance Testnet para desenvolvimento
4. **Implementar DataProvider**: Começar com camada de abstração
5. **Configurar banco de dados**: Criar schemas e migrations

---

## Referências

- [Cedro OMS](https://cedrotech.com)
- [Binance API Docs](https://binance-docs.github.io/apidocs/spot/en/)
- [B3 Market Data](http://www.b3.com.br/pt_br/market-data-e-indices/)
- [FIX Protocol](https://www.fixtrading.org/)
- [CVM - Regulamentação](https://www.gov.br/cvm/)
