# Magnus Wealth - Sistema de Análise de Criptomoedas

## 🎯 Sistema Configurado e Funcionando

O sistema de análise automática de criptomoedas está **100% funcional** e pronto para uso!

---

## ✅ Status da Configuração

- ✅ **Credenciais do Telegram configuradas**
- ✅ **Sessão persistente criada** (`magnus_session.session`)
- ✅ **ID do grupo obtido e configurado** (-4844836232)
- ✅ **Teste de envio realizado com sucesso**
- ✅ **Análise completa executada e enviada**

---

## 🚀 Como Executar

### Execução Manual

Para executar a análise manualmente a qualquer momento:

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
python3 analisador_cripto_hilo.py
```

O sistema irá:
1. Buscar dados reais do Yahoo Finance para as TOP 8 criptos
2. Calcular o indicador Gann HiLo Activator
3. Detectar sinais e mudanças de tendência
4. Calcular performance em múltiplos períodos
5. Enviar mensagem formatada automaticamente ao Telegram

**Não é necessário autenticação!** A sessão já está salva e será reutilizada automaticamente.

---

## ⏰ Agendamento Automático (Cron)

Para executar automaticamente todos os dias às 21h:

### 1. Abrir o crontab:
```bash
crontab -e
```

### 2. Adicionar a linha:
```bash
0 21 * * * cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend && python3 analisador_cripto_hilo.py >> /home/ubuntu/logs/cripto_analise.log 2>&1
```

### 3. Criar diretório de logs:
```bash
mkdir -p /home/ubuntu/logs
```

---

## 📊 TOP 8 Criptomoedas Analisadas

| Cripto | Símbolo | Período HiLo | Tier | Alocação |
|--------|---------|--------------|------|----------|
| Bitcoin | BTC-USD | 40 | 1 | 25.00% |
| Ethereum | ETH-USD | 50 | 1 | 25.00% |
| Binance Coin | BNB-USD | 70 | 2 | 12.50% |
| Solana | SOL-USD | 45 | 2 | 12.50% |
| Chainlink | LINK-USD | 40 | 3 | 6.25% |
| Uniswap | UNI-USD | 65 | 3 | 6.25% |
| Algorand | ALGO-USD | 40 | 3 | 6.25% |
| VeChain | VET-USD | 25 | 3 | 6.25% |

---

## 🔧 Arquivos Importantes

### Arquivo de Sessão
- **`magnus_session.session`** - Sessão autenticada do Telegram (NÃO DELETAR!)
- Este arquivo contém a autenticação persistente
- Sem ele, será necessário autenticar novamente

### Arquivo de Configuração
- **`.env`** - Variáveis de ambiente com credenciais
- Contém: API_ID, API_HASH, PHONE, PASSWORD, GROUP_ID
- **NUNCA commitar este arquivo no GitHub!**

### Scripts Principais
- **`analisador_cripto_hilo.py`** - Script principal de análise
- **`setup_telegram.py`** - Script de configuração inicial (já executado)

---

## 🔄 Manutenção

### Verificar Logs
```bash
tail -f /home/ubuntu/logs/cripto_analise.log
```

### Testar Envio Manual
```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
python3 analisador_cripto_hilo.py
```

### Reautenticar (se necessário)
Se por algum motivo a sessão expirar ou o arquivo `magnus_session.session` for deletado:

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
rm magnus_session.session  # Deletar sessão antiga
python3 setup_telegram.py   # Executar setup novamente
```

---

## 📈 Lógica da Estratégia Gann HiLo Activator

O indicador Gann HiLo Activator foi desenvolvido por Robert Krausz e utiliza médias móveis dos preços máximos e mínimos para identificar tendências.

### Regras de Trading:
- 🟢 **Verde** = Sinal de COMPRA
- 🔴 **Virar vermelho** = ZERA posição + VENDE
- 🔴 **Vermelho** = Sinal de VENDA
- 🟢 **Virar verde** = ZERA posição + COMPRA

### Fórmula Matemática:

1. Calcular SMA(High, n) e SMA(Low, n)

2. Determinar estado HiLo:
   - **BULLISH** (1): se Close > SMA(High)
   - **BEARISH** (-1): se Close < SMA(Low)
   - **NEUTRO** (0): caso contrário

3. Calcular linha GHLA:
   - Se BULLISH: GHLA = SMA(Low)
   - Se BEARISH: GHLA = SMA(High)
   - Se NEUTRO: GHLA = valor anterior

---

## 📊 Métricas de Performance

O sistema calcula a performance simulada com R$ 100 iniciais (sem alavancagem) em 4 períodos:

- **Desde o início**: Performance total desde o primeiro dado disponível
- **6 meses**: Performance nos últimos 180 dias
- **90 dias**: Performance nos últimos 3 meses
- **30 dias**: Performance no último mês

A estratégia utiliza **capital composto**, ou seja, os lucros/prejuízos são reinvestidos automaticamente.

---

## 🔐 Segurança

### Arquivos Sensíveis (NÃO COMMITAR):
- `.env` - Credenciais
- `magnus_session.session` - Sessão autenticada
- `*.session-journal` - Arquivos temporários da sessão

### Já Configurado no .gitignore:
```
.env
*.session
*.session-journal
```

---

## 🆘 Troubleshooting

### Erro: "No module named 'telethon'"
```bash
pip3 install telethon
```

### Erro: "No module named 'yfinance'"
```bash
pip3 install yfinance
```

### Erro: "No module named 'dotenv'"
```bash
pip3 install python-dotenv
```

### Erro: "Please enter your phone"
A sessão expirou. Execute:
```bash
python3 setup_telegram.py
```

### Erro: "Invalid code"
O código de autenticação expirou (válido por 5 minutos). Execute novamente:
```bash
python3 setup_telegram.py
```

---

## 📞 Grupo do Telegram

**Nome:** Magnus Wealth🎯💵🪙  
**ID:** -4844836232

As mensagens são enviadas automaticamente para este grupo sempre que o script é executado.

---

## 🎓 Referências

- **Indicador:** Gann HiLo Activator (Robert Krausz)
- **Fonte de Dados:** Yahoo Finance (yfinance)
- **API Telegram:** Telethon
- **Versão:** Magnus Wealth v8.3.0

---

## ✨ Próximas Melhorias Sugeridas

1. **Notificações de Mudança de Tendência**: Enviar alerta especial quando detectar mudança
2. **Gráficos**: Gerar gráficos das tendências e anexar nas mensagens
3. **Histórico**: Salvar histórico de análises em banco de dados
4. **Backtesting**: Sistema de backtesting para otimizar períodos
5. **Multi-timeframe**: Análise em múltiplos timeframes (diário, 4h, 1h)
6. **Alertas de Preço**: Notificar quando atingir níveis importantes
7. **Dashboard Web**: Interface web para visualizar análises históricas

---

**Sistema desenvolvido e configurado em 19/10/2025**  
**Status: ✅ OPERACIONAL**

