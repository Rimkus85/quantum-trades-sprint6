# 🤖 Sistema de Recomendações Automáticas - Magnus Wealth

> **Status:** ✅ Implementado e Operacional  
> **Versão:** 7.6.0  
> **Data:** 19/10/2025

---

## 📋 Visão Geral

O Magnus Wealth agora possui um **sistema completo de recomendações automáticas** que analisa mercados e envia sinais de compra/venda para o grupo do Telegram em horários estratégicos.

---

## 🪙 Análise de Criptomoedas

### Configuração

| Parâmetro | Valor |
|-----------|-------|
| **Frequência** | Diária |
| **Horário** | 21:00 (Horário de Brasília) |
| **Estratégia** | Siga a Tendência (HiLo Activator) |
| **Timeframe** | Gráfico Diário |
| **Fonte de Dados** | Binance Futures API |
| **Moedas Analisadas** | Top 15 por market cap |

### Moedas Operadas

| # | Moeda | Ticker | Período HiLo | Tier |
|---|-------|--------|--------------|------|
| 1 | Bitcoin | BTCUSDT | 70 | 1 (Baixo Risco) |
| 2 | Ethereum | ETHUSDT | 60 | 1 (Baixo Risco) |
| 3 | Binance Coin | BNBUSDT | 50 | 2 (Médio Risco) |
| 4 | Solana | SOLUSDT | 40 | 2 (Médio Risco) |
| 5 | XRP | XRPUSDT | 65 | 2 (Médio Risco) |
| 6 | Cardano | ADAUSDT | 55 | 2 (Médio Risco) |
| 7 | Avalanche | AVAXUSDT | 45 | 3 (Alto Risco) |
| 8 | Polkadot | DOTUSDT | 50 | 3 (Alto Risco) |
| 9 | Polygon | MATICUSDT | 45 | 3 (Alto Risco) |
| 10 | Chainlink | LINKUSDT | 55 | 3 (Alto Risco) |
| 11 | Litecoin | LTCUSDT | 65 | 3 (Alto Risco) |
| 12 | Uniswap | UNIUSDT | 50 | 3 (Alto Risco) |
| 13 | Cosmos | ATOMUSDT | 55 | 3 (Alto Risco) |
| 14 | Algorand | ALGOUSDT | 50 | 3 (Alto Risco) |
| 15 | VeChain | VETUSDT | 60 | 3 (Alto Risco) |

### Formato da Recomendação

```
🟢 Bitcoin (BTC) 🥇

📊 Sinal: COMPRA
💰 Preço Atual: $60,000.00

🎯 Entrada Sugerida: $60,000.00
🔝 Teto de Entrada: $61,200.00
🛑 Stop Loss: $58,000.00 (3.33%)
✅ Stop Gain: Quando HiLo virar vermelho

📈 Gestão:
• Risco: 3% do capital
• Distância do stop: 3.33%
• Volume: 1.5x a média

⚙️ Configuração:
• Timeframe: Diário
• HiLo Período: 70
• Tier: 1 (Baixo Risco)

🕐 Análise: 19/10/2025 21:00

Estratégia: Siga a Tendência (HiLo Activator)
```

### Gestão de Risco

- **Risco por operação:** 3% do capital
- **Máximo de posições:** 5 simultâneas
- **Stop loss:** Dinâmico (próprio HiLo)
- **Take profit:** Quando HiLo inverter tendência

---

## 📊 Análise de Opções

### Configuração

| Parâmetro | Valor |
|-----------|-------|
| **Frequência** | 3x por dia (dias úteis) |
| **Horários** | 10:10, 14:00, 16:45 |
| **Estratégia** | Análise Técnica + Setups de Opções |
| **Fonte de Dados** | brapi.dev API |
| **Ativos Analisados** | 8 principais (PETR4, VALE3, etc) |

### Ativos Operados

1. PETR4 (Petrobras)
2. VALE3 (Vale)
3. ITUB4 (Itaú)
4. BBDC4 (Bradesco)
5. ABEV3 (Ambev)
6. BBAS3 (Banco do Brasil)
7. WEGE3 (WEG)
8. B3SA3 (B3)

### Tipos de Recomendações

#### 1. Compra de Call (Tendência de Alta)

```
📈 PETR4 - CALL 🟢

🎯 Ação: COMPRA
💰 Preço do Ativo: R$ 40.00
🎲 Strike Sugerido: R$ 40.80

📊 Análise:
• Tendência: ALTA
• Setup: Setup 1: Compra de Call em Rompimento

💡 Motivo da Recomendação:
Ativo em tendência de alta, rompimento de resistência detectado

🎯 Gestão da Operação:
• Entrada: Buscar opção ATM/OTM próxima de R$ 40.80
• Teto: Não pagar mais que 10% acima do prêmio inicial
• Stop Loss: Se PETR4 cair para R$ 38.80
• Stop Gain: Quando ativo perder tendência de alta ou lucro > 100%
• Risco: 3% do capital
• Holding: 5-15 dias

⚠️ Disclaimer:
Esta recomendação é baseada em análise técnica automatizada.
Opções são instrumentos de alto risco e podem resultar em perda
total do capital investido. Avalie seu perfil de risco antes de operar.
Não é recomendação de investimento, apenas sinal educacional.

🕐 Análise: 19/10/2025 10:10

Estratégia: Análise Técnica + Opções
```

#### 2. Compra de Put (Tendência de Baixa)

```
📉 VALE3 - PUT 🟢

🎯 Ação: COMPRA
💰 Preço do Ativo: R$ 70.00
🎲 Strike Sugerido: R$ 68.60

📊 Análise:
• Tendência: BAIXA
• Setup: Setup 2: Compra de Put em Queda

💡 Motivo da Recomendação:
Ativo em tendência de baixa, perda de suporte detectada

🎯 Gestão da Operação:
• Entrada: Buscar opção ATM/OTM próxima de R$ 68.60
• Teto: Não pagar mais que 10% acima do prêmio inicial
• Stop Loss: Se VALE3 subir para R$ 72.10
• Stop Gain: Quando ativo encontrar novo suporte ou lucro > 100%
• Risco: 3% do capital
• Holding: 3-10 dias

⚠️ Disclaimer:
[Mesmo disclaimer acima]
```

#### 3. Venda Coberta (Mercado Lateral)

```
📈 ITUB4 - CALL 🔵

🎯 Ação: VENDA COBERTA
💰 Preço do Ativo: R$ 28.00
🎲 Strike Sugerido: R$ 29.40

📊 Análise:
• Tendência: NEUTRO
• Setup: Setup 3: Venda Coberta (Proteção + Renda)

💡 Motivo da Recomendação:
Mercado lateral/leve alta, ideal para gerar renda extra

🎯 Gestão da Operação:
• Vender: Call strike R$ 29.40
• Prêmio esperado: 1-3% do valor das ações
• Stop Loss: Recomprar se ativo cair 5%
• Stop Gain: Deixar expirar sem valor
• Requisito: Possuir 100 ações de ITUB4
• Holding: Até vencimento

⚠️ Disclaimer:
Venda coberta limita ganhos mas gera renda extra. Se o ativo subir
muito acima do strike, suas ações serão exercidas. Ideal para
quem tem posição de longo prazo e quer rentabilizar a carteira.
Não é recomendação de investimento, apenas sinal educacional.
```

### Gestão de Risco

- **Risco por operação:** 3% do capital
- **Stop loss:** Sempre definido
- **Take profit:** Baseado em setup específico
- **Disclaimer:** Incluído em todas as recomendações

---

## 🗓️ Agenda Completa

### Segunda a Sexta (Dias Úteis)

| Horário | Análise | Descrição |
|---------|---------|-----------|
| 10:10 | Opções | Análise pós-abertura |
| 14:00 | Opções | Análise meio-dia |
| 16:45 | Opções | Análise pré-fechamento |
| 21:00 | Ações | Análise diária completa |
| 21:05 | Cripto | Análise HiLo (Top 15) |

### Sábado

| Horário | Análise | Descrição |
|---------|---------|-----------|
| 10:00 | Resumo Semanal | Consolidação da semana |

### Domingo

| Horário | Tarefa | Descrição |
|---------|--------|-----------|
| 02:00 | Limpeza | Remove logs antigos |
| 03:00 | Backup | Backup de dados |

---

## 🛠️ Arquivos do Sistema

### Scripts de Análise

| Arquivo | Função |
|---------|--------|
| `analisador_cripto_hilo.py` | Análise de criptomoedas com HiLo |
| `analisador_opcoes_recomendacoes.py` | Análise de opções com recomendações |
| `analise_diaria.py` | Análise diária de ações |
| `resumo_semanal.py` | Resumo semanal consolidado |
| `bot_comandos.py` | Bot de comandos 24/7 |

### Configuração

| Arquivo | Função |
|---------|--------|
| `crontab_magnus.txt` | Agendamento de tarefas |
| `.env` | Credenciais do Telegram |

### Documentação

| Arquivo | Função |
|---------|--------|
| `CONHECIMENTO_CRIPTO_HILO_MAGNUS.md` | Guia completo de cripto |
| `CONHECIMENTO_OPCOES_PRATICO_MAGNUS.md` | Guia completo de opções |
| `SISTEMA_RECOMENDACOES_AUTOMATICAS.md` | Este arquivo |

---

## 🚀 Como Instalar

### 1. Configurar Variáveis de Ambiente

Editar `/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/.env`:

```bash
TELEGRAM_API_ID=20866496
TELEGRAM_API_HASH=b3634619ea4d9c7d039a372801165bbf
TELEGRAM_PHONE=+5511974169060
TELEGRAM_PASSWORD=gatinha01*
TELEGRAM_GROUP_ID=-4844836232
```

### 2. Instalar Dependências

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
pip3 install requests pandas numpy python-dotenv telethon
```

### 3. Instalar Crontab

```bash
crontab crontab_magnus.txt
```

### 4. Verificar Instalação

```bash
crontab -l
```

### 5. Testar Manualmente

```bash
# Testar análise de cripto
python3 analisador_cripto_hilo.py

# Testar análise de opções
python3 analisador_opcoes_recomendacoes.py
```

---

## 📊 Métricas e Monitoramento

### Logs

Todos os logs são salvos em:
```
/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/logs/
```

| Log | Conteúdo |
|-----|----------|
| `analise_cripto.log` | Análises de criptomoedas |
| `analise_opcoes.log` | Análises de opções |
| `analise_diaria.log` | Análises diárias de ações |
| `resumo_semanal.log` | Resumos semanais |
| `bot_comandos.log` | Bot de comandos |

### Verificar Logs

```bash
# Ver últimas 50 linhas do log de cripto
tail -50 /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/logs/analise_cripto.log

# Ver últimas 50 linhas do log de opções
tail -50 /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/logs/analise_opcoes.log
```

---

## ⚙️ Personalização

### Alterar Horários

Editar `crontab_magnus.txt` e reinstalar:

```bash
crontab crontab_magnus.txt
```

### Adicionar/Remover Moedas

Editar `analisador_cripto_hilo.py`:

```python
CRIPTO_CONFIG = {
    'BTCUSDT': {'nome': 'Bitcoin', 'periodo_hilo': 70, 'tier': 1},
    # Adicionar nova moeda aqui
}
```

### Adicionar/Remover Ativos (Opções)

Editar `analisador_opcoes_recomendacoes.py`:

```python
ATIVOS_PRINCIPAIS = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'BBAS3', 'WEGE3', 'B3SA3']
```

---

## 🔒 Segurança

### Credenciais

- ✅ Armazenadas em `.env` (não commitado no Git)
- ✅ Sessão do Telegram criptografada
- ✅ Acesso restrito ao grupo Magnus Wealth

### Backup

- ✅ Backup automático semanal (Domingo 03:00)
- ✅ Logs rotacionados (30 dias)
- ✅ Dados salvos em `backups/`

---

## 📈 Próximas Melhorias

### Curto Prazo
- [ ] Integração com mais exchanges (Coinbase, Kraken)
- [ ] Análise de mais ativos (ETFs, FIIs)
- [ ] Dashboard web com histórico de recomendações

### Médio Prazo
- [ ] Machine Learning para otimizar períodos HiLo
- [ ] Backtesting automático mensal
- [ ] Alertas personalizados por perfil de risco

### Longo Prazo
- [ ] Execução automática de ordens (com aprovação)
- [ ] Portfolio tracking integrado
- [ ] Relatórios de performance individualizados

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs em `/logs/`
2. Testar scripts manualmente
3. Revisar documentação completa

---

**Última atualização:** 19/10/2025  
**Versão:** 7.6.0  
**Autor:** Magnus Wealth AI

