# 🤖 TRADING AUTOMÁTICO - GUIA COMPLETO

## Magnus Wealth - Sistema de Trading Automático Binance

**Versão:** 8.4.0  
**Data:** 19/10/2025  
**Status:** Pronto para configuração

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Configuração](#configuração)
4. [Gestão de Risco](#gestão-de-risco)
5. [Como Funciona](#como-funciona)
6. [Ativação](#ativação)
7. [Monitoramento](#monitoramento)
8. [FAQ](#faq)

---

## 🎯 VISÃO GERAL

O sistema de trading automático executa operações na Binance Futures baseado nos sinais do **Gann HiLo Activator**.

### Características Principais

- ✅ **Alavancagem:** 12x (configurável)
- ✅ **Mercado:** Binance Futures USDT
- ✅ **Proteção:** Stop Loss automático em cada operação
- ✅ **Gestão:** Capital alocado por tier
- ✅ **Notificações:** Telegram em tempo real
- ✅ **Logs:** Registro completo de todas as operações

---

## 🚀 FUNCIONALIDADES

### 1. Execução Automática de Ordens

Quando o **Gann HiLo Activator** detecta mudança de tendência:

**🟢 VERDE → VERMELHO:**
1. Fecha posição LONG (se aberta)
2. Abre posição SHORT
3. Coloca Stop Loss automático

**🔴 VERMELHO → VERDE:**
1. Fecha posição SHORT (se aberta)
2. Abre posição LONG
3. Coloca Stop Loss automático

### 2. Gestão de Capital

**Alocação por Tier:**

| Tier | Criptos | Alocação | Capital ($2,000) |
|------|---------|----------|------------------|
| 1 | BTC, ETH | 25% cada | $500 cada |
| 2 | BNB, SOL | 12.5% cada | $250 cada |
| 3 | LINK, UNI, ALGO, VET | 6.25% cada | $125 cada |

**Com Alavancagem 12x:**
- Capital $500 → Poder de compra $6,000
- Capital $250 → Poder de compra $3,000
- Capital $125 → Poder de compra $1,500

### 3. Proteção de Fundos

**Stop Loss Automático:**
- Percentual: 5% do capital (não alavancado)
- Com alavancagem 12x: ~0.42% de movimento de preço
- Exemplo: Capital $500, Stop Loss = $25 (5%)

**Cálculo do Stop Loss:**
```
LONG: Stop = Preço Entrada × (1 - 5% / 12)
SHORT: Stop = Preço Entrada × (1 + 5% / 12)
```

### 4. Notificações Telegram

**Ao abrir posição:**
```
🟢 POSIÇÃO ABERTA

Cripto: BTCUSDT
Lado: LONG
Preço: $109,317.00
Quantidade: 0.055
Capital: $500.00
Alavancagem: 12x
Stop Loss: $108,935.00
Ordem ID: 12345678
```

**Ao fechar posição:**
```
✅ POSIÇÃO FECHADA

Cripto: BTCUSDT
Lado: LONG
Entrada: $109,317.00
Saída: $110,500.00
P&L: +12.98%
Lucro/Prejuízo: $+64.90
Ordem ID: 12345679
```

---

## ⚙️ CONFIGURAÇÃO

### Passo 1: Criar API Keys na Binance

1. Acesse: https://www.binance.com/en/my/settings/api-management
2. Clique em "Create API"
3. Nome: "Magnus Wealth Trading"
4. **IMPORTANTE:** Habilite as seguintes permissões:
   - ✅ Enable Futures
   - ✅ Enable Reading
   - ❌ Enable Spot & Margin Trading (não necessário)
   - ❌ Enable Withdrawals (NUNCA habilitar)

5. Copie:
   - API Key
   - Secret Key

### Passo 2: Configurar Variáveis de Ambiente

Edite o arquivo `.env`:

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
nano .env
```

Adicione:

```env
# Binance API
BINANCE_API_KEY=sua_api_key_aqui
BINANCE_API_SECRET=sua_secret_key_aqui

# Trading
ALAVANCAGEM=12
CAPITAL_TOTAL=2000
STOP_LOSS_PERCENT=5
TRADING_ATIVO=false  # Manter false até testar
```

### Passo 3: Instalar Dependências

```bash
pip3 install python-binance
```

### Passo 4: Testar Conexão

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
python3 trader_binance.py
```

**Saída esperada:**
```
✓ Conectado à Binance API
✓ Saldo: $2,000.00
✓ Alavancagem: 12x
✓ Capital total: $2,000.00
```

---

## 🛡️ GESTÃO DE RISCO

### Proteções Implementadas

1. **Stop Loss Automático**
   - Colocado em TODAS as operações
   - Limita prejuízo a 5% do capital alocado

2. **Alocação Controlada**
   - Capital dividido por tier
   - Máximo 25% em uma cripto (BTC/ETH)

3. **Sem Reentrada Automática**
   - Se stop loss é atingido, não reentra automaticamente
   - Aguarda próximo sinal do HiLo

4. **Logs Completos**
   - Todas as operações registradas
   - Arquivo: `/logs/trader.log`

5. **Estado Persistente**
   - Posições salvas em arquivo JSON
   - Recuperação após restart

### Riscos a Considerar

⚠️ **Alavancagem 12x:**
- Amplifica ganhos E perdas
- Movimento de 0.42% já aciona stop loss
- Mercado volátil pode gerar múltiplos stops

⚠️ **Slippage:**
- Ordens MARKET podem ter slippage
- Em momentos de alta volatilidade, preço pode variar

⚠️ **Gaps:**
- Mercado cripto opera 24/7
- Gaps podem pular o stop loss

⚠️ **API Failures:**
- Conexão pode falhar
- Sistema tem retry, mas não é 100% garantido

---

## 🔧 COMO FUNCIONA

### Fluxo Completo

```
1. ANÁLISE (21h diariamente)
   ↓
2. Buscar dados Yahoo Finance
   ↓
3. Calcular Gann HiLo Activator
   ↓
4. Detectar mudança de tendência?
   ├─ NÃO → Manter posição atual
   └─ SIM → Continuar
       ↓
5. Há posição aberta?
   ├─ SIM → Fechar posição
   └─ NÃO → Continuar
       ↓
6. Sinal = COMPRA?
   ├─ SIM → Abrir LONG
   └─ NÃO → Sinal = VENDA?
       ├─ SIM → Abrir SHORT
       └─ NÃO → Não fazer nada
           ↓
7. Colocar Stop Loss
   ↓
8. Salvar estado
   ↓
9. Notificar Telegram
   ↓
10. FIM
```

### Exemplo Prático

**Cenário:** Bitcoin muda de VERMELHO para VERDE

```
Hora: 21:00
Cripto: Bitcoin (BTCUSDT)
Preço: $109,317
Sinal: COMPRA (mudança detectada)
Capital alocado: $500 (Tier 1, 25%)

AÇÕES:
1. Configurar alavancagem 12x
2. Calcular quantidade: $500 × 12 / $109,317 = 0.055 BTC
3. Executar ordem MARKET BUY 0.055 BTC
4. Calcular stop loss: $109,317 × (1 - 0.0042) = $108,858
5. Colocar STOP MARKET SELL em $108,858
6. Salvar posição no estado
7. Notificar Telegram

POSIÇÃO ABERTA:
- Lado: LONG
- Quantidade: 0.055 BTC
- Entrada: $109,317
- Stop Loss: $108,858
- Risco: $25 (5% de $500)
- Potencial: Ilimitado (até próxima virada)
```

---

## ✅ ATIVAÇÃO

### Modo 1: Apenas Análise (Padrão)

```bash
# Executar apenas análise (sem trading)
python3 analisador_cripto_hilo.py
```

### Modo 2: Análise + Trading Automático

**1. Ativar no .env:**
```env
TRADING_ATIVO=true
```

**2. Executar:**
```bash
python3 analisador_com_trader.py
```

### Modo 3: Agendamento Automático

**Atualizar agendamento para usar versão com trading:**

```bash
# Editar o cron job para usar analisador_com_trader.py
# O agendamento já está configurado para 21h
```

---

## 📊 MONITORAMENTO

### 1. Logs

**Arquivo:** `/home/ubuntu/quantum-trades-sprint6/logs/trader.log`

```bash
tail -f /home/ubuntu/quantum-trades-sprint6/logs/trader.log
```

### 2. Estado das Posições

**Arquivo:** `/home/ubuntu/quantum-trades-sprint6/data/posicoes.json`

```bash
cat /home/ubuntu/quantum-trades-sprint6/data/posicoes.json | python3 -m json.tool
```

### 3. Telegram

Todas as operações são notificadas em tempo real no grupo.

### 4. Binance App

Acompanhe posições abertas diretamente no app da Binance:
- Futures → Positions

---

## ❓ FAQ

### 1. É seguro usar alavancagem 12x?

**R:** Alavancagem amplifica ganhos E perdas. Com stop loss de 5%, você pode perder no máximo 5% do capital alocado por operação. Porém, em mercados voláteis, múltiplos stops podem ser acionados.

**Recomendação:** Comece com capital pequeno para testar.

---

### 2. Posso mudar a alavancagem?

**R:** Sim! Edite no `.env`:

```env
ALAVANCAGEM=6  # Mais conservador
ALAVANCAGEM=20 # Mais agressivo (NÃO RECOMENDADO)
```

---

### 3. O que acontece se a API da Binance cair?

**R:** O sistema tem retry automático, mas se falhar:
- A análise continua
- Mensagem é enviada ao Telegram
- Operação não é executada
- Você pode executar manualmente

---

### 4. Posso operar apenas algumas criptos?

**R:** Sim! Edite `TOP_8` no `analisador_cripto_hilo.py` e remova as que não quer operar.

---

### 5. Como desativar o trading automático?

**R:** Edite `.env`:

```env
TRADING_ATIVO=false
```

Ou use apenas:
```bash
python3 analisador_cripto_hilo.py  # Sem trading
```

---

### 6. Quanto capital preciso?

**R:** Mínimo recomendado: $1,000

- Com $2,000: Alocação ideal conforme tier
- Com $1,000: Reduza alocação pela metade
- Com $500: Opere apenas 2-3 criptos

---

### 7. O stop loss é garantido?

**R:** Não 100%. Em casos de:
- Gaps extremos
- Liquidez baixa
- Problemas na Binance

O stop pode ser executado a preço pior. Isso é raro, mas possível.

---

### 8. Posso testar sem arriscar dinheiro real?

**R:** Sim! Use a **Binance Testnet**:

1. Acesse: https://testnet.binancefuture.com
2. Crie API keys de teste
3. Use no `.env`
4. Teste à vontade com dinheiro virtual

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Configurar API Keys da Binance
2. ✅ Testar conexão
3. ✅ Executar em modo análise (sem trading)
4. ✅ Validar sinais por 1 semana
5. ⏳ Ativar trading com capital pequeno
6. ⏳ Monitorar por 1 mês
7. ⏳ Escalar capital gradualmente

---

## ⚠️ DISCLAIMER

**Este sistema é para fins educacionais.**

- Não é garantia de lucro
- Trading com alavancagem é arriscado
- Você pode perder todo o capital
- Use apenas dinheiro que pode perder
- Não é aconselhamento financeiro

**Opere por sua conta e risco.**

---

## 📞 SUPORTE

**Problemas técnicos:**
- Verifique logs: `/logs/trader.log`
- Verifique estado: `/data/posicoes.json`
- Teste conexão: `python3 trader_binance.py`

**Dúvidas sobre sinais:**
- Consulte: `RELATORIO_FINAL_DADOS_REAIS_2025.md`
- Valide no TradingView

---

**Versão:** 8.4.0  
**Última atualização:** 19/10/2025  
**Autor:** Magnus Wealth Team

