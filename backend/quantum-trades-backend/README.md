# Magnus Wealth Backend - API de Integração com Telegram

Backend do sistema Magnus Wealth (Quantum Trades) com integração ao Telegram para leitura e análise de recomendações de carteiras de investimentos.

## Funcionalidades

O backend fornece uma API REST completa para integração com o Telegram e análise de carteiras. As principais funcionalidades incluem leitura de mensagens de grupos do Telegram, filtragem de mensagens relevantes sobre carteiras, análise e extração de informações estruturadas (tickers, percentuais, recomendações), geração de estatísticas e relatórios, e endpoints RESTful para integração com o frontend.

## Arquitetura

O sistema está organizado em três camadas principais. A camada de **Serviços** (`services/`) contém o `telegram_service.py` responsável pela integração com a API do Telegram usando Telethon. A camada de **Módulos** (`modules/`) possui o `carteira_parser.py` que faz o parsing e análise de mensagens. Por fim, a camada de **API** (`app.py`) oferece endpoints Flask para o frontend.

## Instalação

Para instalar e configurar o backend, siga os passos abaixo:

### Pré-requisitos

Certifique-se de ter Python 3.11 ou superior instalado no sistema.

### Passo 1: Instalar Dependências

```bash
cd backend/quantum-trades-backend
pip install -r requirements.txt
```

### Passo 2: Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
nano .env
```

Edite o arquivo `.env` com suas credenciais do Telegram:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+5511999999999
TELEGRAM_GROUP_USERNAME=@seu_grupo
```

Para obter as credenciais, acesse [my.telegram.org](https://my.telegram.org), faça login e crie uma aplicação em "API development tools".

### Passo 3: Executar o Servidor

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`.

## Endpoints da API

### Health Check

**GET** `/api/health`

Verifica o status da API e configuração do Telegram.

**Resposta:**
```json
{
  "status": "ok",
  "service": "Magnus Wealth API",
  "version": "1.0.0",
  "telegram_configured": true
}
```

### Configuração do Telegram

**GET** `/api/telegram/config`

Retorna o status da configuração do Telegram.

**Resposta:**
```json
{
  "configured": true,
  "has_api_id": true,
  "has_api_hash": true,
  "has_phone": true,
  "has_group": true
}
```

### Ler Mensagens do Telegram

**GET** `/api/telegram/messages?group=@grupo&limit=100`

Lê mensagens de um grupo do Telegram.

**Parâmetros:**
- `group` (opcional): Username ou ID do grupo
- `limit` (opcional): Número de mensagens (padrão: 100)

**Resposta:**
```json
{
  "success": true,
  "total": 50,
  "group": "@carteiras_recomendadas",
  "messages": [...]
}
```

### Ler Carteiras do Telegram

**GET** `/api/telegram/carteiras?group=@grupo&limit=100`

Lê e filtra apenas mensagens sobre carteiras.

**Parâmetros:**
- `group` (opcional): Username ou ID do grupo
- `limit` (opcional): Número de mensagens (padrão: 100)

**Resposta:**
```json
{
  "success": true,
  "total": 15,
  "group": "@carteiras_recomendadas",
  "carteiras": [...]
}
```

### Analisar Mensagens

**POST** `/api/carteiras/parse`

Analisa mensagens e extrai informações estruturadas.

**Body:**
```json
{
  "messages": [
    {
      "id": 123,
      "date": "2025-10-15T10:00:00",
      "text": "Carteira recomendada: PETR4 30%, VALE3 25%"
    }
  ]
}
```

**Resposta:**
```json
{
  "success": true,
  "report": {
    "data_geracao": "2025-10-15T12:00:00",
    "total_mensagens_analisadas": 1,
    "carteiras": [...],
    "estatisticas": {...}
  }
}
```

### Resumo de Recomendações

**POST** `/api/carteiras/summary`

Retorna um resumo das recomendações.

**Body:**
```json
{
  "messages": [...]
}
```

**Resposta:**
```json
{
  "success": true,
  "summary": {
    "top_tickers": [["PETR4", 5], ["VALE3", 3]],
    "compras": 10,
    "vendas": 3,
    "total": 15,
    "latest": [...]
  }
}
```

### Análise Completa

**GET** `/api/carteiras/analyze?group=@grupo&limit=100`

Endpoint completo que lê do Telegram e retorna análise estruturada.

**Parâmetros:**
- `group` (opcional): Username ou ID do grupo
- `limit` (opcional): Número de mensagens (padrão: 100)

**Resposta:**
```json
{
  "success": true,
  "report": {
    "data_geracao": "2025-10-15T12:00:00",
    "total_mensagens_analisadas": 15,
    "carteiras": [...],
    "estatisticas": {
      "total_carteiras": 15,
      "total_tickers_unicos": 8,
      "tickers_mais_mencionados": {...},
      "distribuicao_recomendacoes": {...}
    }
  }
}
```

## Estrutura de Dados

### Mensagem do Telegram

```json
{
  "id": 12345,
  "date": "2025-10-15T10:30:00",
  "sender_id": 987654321,
  "text": "Carteira recomendada: PETR4 30%, VALE3 25%",
  "is_reply": false,
  "views": 150
}
```

### Carteira Analisada

```json
{
  "data": "2025-10-15T10:30:00",
  "texto_original": "Carteira recomendada: PETR4 30%, VALE3 25%",
  "tipo_recomendacao": "indefinido",
  "tickers": ["PETR4", "VALE3"],
  "alocacoes": [
    {"ticker": "PETR4", "percentual": 30.0},
    {"ticker": "VALE3", "percentual": 25.0}
  ],
  "precos": [],
  "total_percentual": 55.0
}
```

## Integração com Frontend

Para integrar com o frontend, adicione as seguintes chamadas JavaScript:

```javascript
// Ler carteiras do Telegram
async function getCarteiras() {
  const response = await fetch('http://localhost:5000/api/telegram/carteiras?limit=100');
  const data = await response.json();
  return data.carteiras;
}

// Analisar carteiras
async function analyzeCarteiras() {
  const response = await fetch('http://localhost:5000/api/carteiras/analyze?limit=100');
  const data = await response.json();
  return data.report;
}
```

## Segurança

O sistema implementa as seguintes práticas de segurança:

- **Credenciais em variáveis de ambiente**: Nunca no código
- **CORS configurado**: Permite requisições do frontend
- **Sessão do Telegram**: Armazenada localmente em arquivo `.session`
- **Sem armazenamento de senhas**: Apenas token de sessão

**Importante**: Nunca compartilhe seu arquivo `.env` ou `.session`. Adicione-os ao `.gitignore`.

## Desenvolvimento

### Estrutura de Diretórios

```
backend/quantum-trades-backend/
├── app.py                      # API Flask principal
├── requirements.txt            # Dependências Python
├── .env.example               # Exemplo de configuração
├── services/
│   ├── __init__.py
│   └── telegram_service.py    # Serviço do Telegram
├── modules/
│   ├── __init__.py
│   └── carteira_parser.py     # Parser de carteiras
└── config/
    └── (configurações futuras)
```

### Adicionar Novos Endpoints

Para adicionar novos endpoints, edite o arquivo `app.py`:

```python
@app.route('/api/seu-endpoint', methods=['GET'])
def seu_endpoint():
    return jsonify({'mensagem': 'Seu endpoint'})
```

### Estender o Parser

Para adicionar novos padrões de análise, edite `modules/carteira_parser.py`:

```python
# Adicionar novo padrão regex
NOVO_PATTERN = r'seu_regex_aqui'

def extract_novo_dado(self, text: str):
    matches = re.findall(self.NOVO_PATTERN, text)
    return matches
```

## Troubleshooting

### Erro: "Telegram não configurado"

Verifique se o arquivo `.env` existe e contém todas as variáveis necessárias.

### Erro: "Grupo não encontrado"

Certifique-se de que você é membro do grupo e que o username está correto (incluindo @).

### Erro de autenticação

Na primeira execução, você precisará autenticar com o código enviado pelo Telegram. Execute o script diretamente:

```bash
python services/telegram_service.py
```

## Próximos Passos

Funcionalidades planejadas para futuras versões:

- Banco de dados PostgreSQL para armazenamento persistente
- Sistema de cache Redis para melhor performance
- Webhooks para notificações em tempo real
- Autenticação JWT para segurança da API
- Rate limiting para proteção contra abuso
- Logs estruturados com Winston/Loguru

## Licença

MIT License - Veja [LICENSE](../../LICENSE) para mais detalhes.

