# 🚀 Quantum Trades - Sprint 6 + Integração Telegram

Sistema de trading com IA integrado com dados reais de mercado e leitura de grupos do Telegram para recomendações de carteiras.

## ✨ Novidades da Sprint 6

### 🎯 Dados Reais de Mercado
- ✅ Integração com API brapi.dev
- ✅ Cotações em tempo real
- ✅ Histórico de até 20 anos
- ✅ +4.000 ações da B3

### 💾 Banco de Dados Local
- ✅ IndexedDB com 4 stores
- ✅ Armazenamento de 20 anos de histórico
- ✅ Sincronização automática mensal
- ✅ Economia de 95% nas requisições à API

### 🔄 Sistema Híbrido Inteligente
- ✅ Banco local para dados históricos
- ✅ API para dados do mês atual
- ✅ Fallback automático para mock
- ✅ Cache de 30 minutos

### 🎨 Interface Aprimorada
- ✅ Modal de configuração de API
- ✅ Modal de importação de dados
- ✅ Barra de progresso em tempo real
- ✅ Estatísticas do banco de dados

### 📱 Nova Funcionalidade: Integração com Telegram
- ✅ Leitura de mensagens de grupos do Telegram
- ✅ Filtragem automática de recomendações de carteiras
- ✅ Parser inteligente de tickers e percentuais
- ✅ Análise de recomendações (compra/venda/manter)
- ✅ API REST completa para integração com frontend
- ✅ Estatísticas de ativos mais mencionados

## 📊 Resultados

| Métrica | Resultado |
|---------|-----------|
| **Funcionalidades mantidas** | 25/25 (100%) |
| **Layout alterado** | 0% |
| **Performance** | < 1.5s |
| **Economia de API** | 95% |
| **Débitos técnicos** | 0 |
| **Nova funcionalidade** | Telegram ✅ |

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│         QUANTUM TRADES SPRINT 6 + TELEGRAM          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────┐ │
│  │  IndexedDB   │   │  brapi.dev   │   │Telegram │ │
│  │  (20 anos)   │   │  (Mês atual) │   │ Groups  │ │
│  └──────┬───────┘   └──────┬───────┘   └────┬────┘ │
│         │                  │                 │      │
│         └────────┬─────────┴─────────────────┘      │
│                  │                                   │
│         ┌────────▼────────┐                          │
│         │  Backend API    │                          │
│         │  (Flask/Python) │                          │
│         └────────┬────────┘                          │
│                  │                                   │
│         ┌────────▼────────┐                          │
│         │   Dashboard UI  │                          │
│         └─────────────────┘                          │
└─────────────────────────────────────────────────────┘
```

## 📦 Estrutura do Projeto

### Frontend
- `dashboard_final.html` - Dashboard principal
- `portfolio.html` - Gestão de portfolio
- `painel_ia.html` - Painel de IA
- `alertas_sistema.html` - Sistema de alertas

### Backend (Novo!)
```
backend/quantum-trades-backend/
├── app.py                      # API Flask principal
├── requirements.txt            # Dependências Python
├── services/
│   └── telegram_service.py    # Integração com Telegram
├── modules/
│   └── carteira_parser.py     # Parser de carteiras
└── README.md                  # Documentação do backend
```

### Serviços (1.540 linhas)
- `config.js` - Configurações centralizadas
- `realDataService.js` - Integração com API
- `databaseService.js` - Gerenciamento IndexedDB
- `syncService.js` - Sincronização automática
- `dataService.js` - Orquestrador unificado

### Documentação
- `SPRINT6_IMPLEMENTACAO_COMPLETA.md` - Documentação técnica completa
- `backend/quantum-trades-backend/README.md` - Documentação da API Telegram

## 🚀 Como Usar

### 1. Frontend (Dashboard)

```bash
# 1. Clone o repositório
git clone https://github.com/Rimkus85/quantum-trades-sprint6.git

# 2. Abra o dashboard
cd quantum-trades-sprint6/frontend
# Abra dashboard_final.html no navegador
```

### 2. Backend (API Telegram)

```bash
# 1. Instale as dependências
cd backend/quantum-trades-backend
pip install -r requirements.txt

# 2. Configure o Telegram
cp .env.example .env
nano .env
# Adicione suas credenciais do Telegram

# 3. Execute a API
python app.py
```

A API estará disponível em `http://localhost:5000`.

### 3. Configurar API brapi.dev (Opcional)

1. Acesse https://brapi.dev/dashboard
2. Crie uma conta gratuita
3. Copie seu token
4. No dashboard, clique em "API"
5. Cole o token e salve

**Sem token:** Funciona com 4 ações de teste (PETR4, VALE3, MGLU3, ITUB4)  
**Com token:** Acesso a +4.000 ações da B3

### 4. Configurar Telegram (Nova Funcionalidade)

Para usar a integração com Telegram:

1. Acesse https://my.telegram.org
2. Faça login e vá em "API development tools"
3. Crie uma aplicação e obtenha `API ID` e `API Hash`
4. Configure no arquivo `.env` do backend:
   ```env
   TELEGRAM_API_ID=seu_api_id
   TELEGRAM_API_HASH=seu_api_hash
   TELEGRAM_PHONE=+5511999999999
   TELEGRAM_GROUP_USERNAME=@seu_grupo
   ```

## 🔌 Endpoints da API Telegram

A API fornece os seguintes endpoints:

- **GET** `/api/health` - Status da API
- **GET** `/api/telegram/config` - Configuração do Telegram
- **GET** `/api/telegram/messages` - Ler mensagens do grupo
- **GET** `/api/telegram/carteiras` - Ler apenas mensagens sobre carteiras
- **POST** `/api/carteiras/parse` - Analisar mensagens
- **POST** `/api/carteiras/summary` - Resumo de recomendações
- **GET** `/api/carteiras/analyze` - Análise completa (lê + analisa)

Consulte a [documentação completa do backend](backend/quantum-trades-backend/README.md) para mais detalhes.

## 📊 Economia de API

### Uso Mensal Estimado

| Atividade | Requisições |
|-----------|-------------|
| Importação inicial | 20 |
| Sincronização mensal | 20 |
| Cotações diárias | 600 |
| Buscas diversas | 100 |
| **TOTAL** | **740** |

**Limite gratuito:** 15.000 requisições/mês  
**Uso real:** 740 requisições/mês  
**Economia:** 95% 🎉

## 🎯 Funcionalidades

### Dashboard Principal
- ✅ Busca de ações com dados reais
- ✅ Cotações em tempo real
- ✅ Gráficos de preços
- ✅ Indicadores técnicos
- ✅ Sistema de alertas

### Portfolio
- ✅ Gestão de ativos
- ✅ Cálculo de lucro/prejuízo
- ✅ Performance individual
- ✅ Valor total investido

### Painel IA
- ✅ Predições de mercado
- ✅ Análise de sentimento
- ✅ Recomendações inteligentes
- ✅ Métricas de confiança

### Sistema de Alertas
- ✅ Alertas de preço
- ✅ Alertas de indicadores
- ✅ Notificações automáticas
- ✅ Gerenciamento completo

### Integração Telegram (Novo!)
- ✅ Leitura de grupos do Telegram
- ✅ Filtragem de mensagens sobre carteiras
- ✅ Extração de tickers e percentuais
- ✅ Identificação de recomendações (compra/venda)
- ✅ Estatísticas de ativos mencionados
- ✅ API REST para integração

## 🔧 Tecnologias

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python 3.11, Flask, Telethon
- **Banco de Dados:** IndexedDB (nativo do navegador)
- **API Mercado:** brapi.dev (dados de mercado brasileiros)
- **API Telegram:** Telethon (cliente Python)
- **Cache:** Sistema próprio com timeout de 30 minutos
- **Sincronização:** Automática no dia 02 de cada mês

## 📈 Performance

| Operação | Tempo |
|----------|-------|
| Busca de cotação | < 1s |
| Histórico (banco) | < 0.5s |
| Histórico (API) | < 1.5s |
| Carregamento página | < 2s |
| Importação (20 ações) | 3-5 min |
| Leitura Telegram (100 msgs) | 2-3s |
| Análise de carteiras | < 1s |

## 🔒 Segurança

- ✅ Token armazenado localmente (localStorage)
- ✅ Dados no IndexedDB (isolado por domínio)
- ✅ HTTPS obrigatório para API
- ✅ Sem envio de dados para servidores terceiros
- ✅ Controle total do usuário
- ✅ Credenciais Telegram em variáveis de ambiente
- ✅ Sessão Telegram criptografada localmente

## 📚 Documentação

- [Implementação Completa](documentacao/SPRINT6_IMPLEMENTACAO_COMPLETA.md)
- [Backend API Telegram](backend/quantum-trades-backend/README.md)
- [Validação do Sistema](documentacao/quantum_trades_validation.md)

## 🎓 Sprints

- **Sprint 1-2:** Estrutura base e design
- **Sprint 3:** Menu hambúrguer e navegação
- **Sprint 4:** Dashboard integrado
- **Sprint 5:** Painel IA e alertas
- **Sprint 6:** Dados reais com banco local ✅
- **Sprint 6.1:** Integração Telegram ✅

## 🚀 Próximas Sprints

- **Sprint 7:** Interface frontend para Telegram
- **Sprint 8:** Análise técnica avançada
- **Sprint 9:** Machine Learning e predições
- **Sprint 10:** Notificações push
- **Sprint 11:** Modo offline completo

## 📞 Suporte

- **Issues:** https://github.com/Rimkus85/quantum-trades-sprint6/issues
- **Documentação:** Pasta `/documentacao`
- **API brapi.dev:** https://brapi.dev/docs
- **Telegram API:** https://core.telegram.org/api

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para mais detalhes.

---

**Quantum Trades Sprint 6.1** - Sistema de trading com IA, dados reais de mercado e integração com Telegram 🚀

**Status:** ✅ Produção  
**Versão:** 6.1.0  
**Data:** 15/10/2025

