# 🚀 GUIA COMPLETO - MAGNUS WEALTH BOT NO TERMUX

## 📱 PASSO A PASSO SUPER DETALHADO

---

## ✅ PASSO 1: INSTALAR DEPENDÊNCIAS

**Abra o Termux e cole CADA linha (uma de cada vez):**

```bash
pip install yfinance
```
*Aguarde terminar (aparece "Successfully installed")*

```bash
pip install pandas
```
*Aguarde terminar*

```bash
pip install python-binance
```
*Aguarde terminar*

```bash
pip install schedule
```
*Aguarde terminar*

**Pronto! Dependências instaladas ✓**

---

## ✅ PASSO 2: CRIAR O ARQUIVO DO BOT

**Cole isso no Termux:**

```bash
cat > magnus_bot.py << 'FIM_DO_CODIGO'
#!/usr/bin/env python3
import os
import requests
import pandas as pd
import yfinance as yf
from binance.client import Client
from datetime import datetime, timedelta
import schedule
import time

# COLE SUAS CHAVES AQUI
BINANCE_API_KEY = "lCkKoBwC2hVgjkrvKcCeMP3p4UyiNPXA97sKbBvu3XsQbrZVltp58j2JlCuclJIr"
BINANCE_API_SECRET = "7SVFFQfMAXFb3s7z3NiJ9UynjrNXQoqS25z8ZwUD863iTNudXtIdA6tAkAi7WkEP"

TELEGRAM_BOT_TOKEN = "SEU_BOT_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

CAPITAL_INICIAL = 2000

CRIPTOS = [
    {"nome": "Bitcoin", "symbol": "BTCUSDT", "ticker_yahoo": "BTC-USD", "periodo": 40, "tier": 1, "alocacao": 0.25},
    {"nome": "Ethereum", "symbol": "ETHUSDT", "ticker_yahoo": "ETH-USD", "periodo": 50, "tier": 1, "alocacao": 0.25},
    {"nome": "Binance Coin", "symbol": "BNBUSDT", "ticker_yahoo": "BNB-USD", "periodo": 70, "tier": 2, "alocacao": 0.125},
    {"nome": "Solana", "symbol": "SOLUSDT", "ticker_yahoo": "SOL-USD", "periodo": 45, "tier": 2, "alocacao": 0.125},
    {"nome": "Chainlink", "symbol": "LINKUSDT", "ticker_yahoo": "LINK-USD", "periodo": 40, "tier": 3, "alocacao": 0.0625},
    {"nome": "Uniswap", "symbol": "UNIUSDT", "ticker_yahoo": "UNI-USD", "periodo": 65, "tier": 3, "alocacao": 0.0625},
    {"nome": "Algorand", "symbol": "ALGOUSDT", "ticker_yahoo": "ALGO-USD", "periodo": 40, "tier": 3, "alocacao": 0.0625},
    {"nome": "VeChain", "symbol": "VETUSDT", "ticker_yahoo": "VET-USD", "periodo": 25, "tier": 3, "alocacao": 0.0625},
]

ALAVANCAGEM = 12

def enviar_telegram(mensagem):
    if TELEGRAM_BOT_TOKEN == "SEU_BOT_TOKEN_AQUI":
        return
    try:
        url = f"https://api.telegram.com/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"})
    except:
        pass

def buscar_dados(ticker, dias=365):
    try:
        df = yf.download(ticker, period=f"{dias}d", interval="1d", progress=False)
        if df.empty:
            return None
        df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
        return df[["open", "high", "low", "close"]]
    except:
        return None

def calcular_gann_hilo(df, periodo):
    df = df.copy()
    df["sma_high"] = df["high"].rolling(window=periodo).mean()
    df["sma_low"] = df["low"].rolling(window=periodo).mean()
    df["hilo_state"] = 0
    df["ghla"] = 0.0
    
    for i in range(periodo, len(df)):
        close = df.iloc[i]["close"]
        sma_high = df.iloc[i]["sma_high"]
        sma_low = df.iloc[i]["sma_low"]
        prev_state = df.iloc[i-1]["hilo_state"]
        prev_ghla = df.iloc[i-1]["ghla"]
        
        if close > sma_high:
            state = 1
            ghla = sma_low
        elif close < sma_low:
            state = -1
            ghla = sma_high
        else:
            state = prev_state
            ghla = prev_ghla
        
        df.iloc[i, df.columns.get_loc("hilo_state")] = state
        df.iloc[i, df.columns.get_loc("ghla")] = ghla
    
    return df

def analisar_cripto(cripto):
    print(f"\n📊 Analisando {cripto['nome']}...")
    
    df = buscar_dados(cripto["ticker_yahoo"])
    if df is None or len(df) < cripto["periodo"] + 10:
        print(f"  ✗ Sem dados suficientes")
        return None
    
    df = calcular_gann_hilo(df, cripto["periodo"])
    
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2]
    
    preco_atual = ultimo["close"]
    ghla = ultimo["ghla"]
    tendencia_atual = "VERDE" if ultimo["hilo_state"] == 1 else "VERMELHO" if ultimo["hilo_state"] == -1 else "NEUTRO"
    tendencia_anterior = "VERDE" if penultimo["hilo_state"] == 1 else "VERMELHO" if penultimo["hilo_state"] == -1 else "NEUTRO"
    
    mudou = tendencia_atual != tendencia_anterior and tendencia_anterior != "NEUTRO"
    
    if mudou:
        if tendencia_atual == "VERDE":
            sinal = "COMPRAR"
        elif tendencia_atual == "VERMELHO":
            sinal = "VENDER"
        else:
            sinal = "MANTER"
    else:
        sinal = "MANTER"
    
    print(f"  Preço: ${preco_atual:,.2f}")
    print(f"  GHLA: ${ghla:,.2f}")
    print(f"  Tendência: {tendencia_atual}")
    print(f"  Sinal: {sinal}")
    
    return {
        "cripto": cripto,
        "preco": preco_atual,
        "ghla": ghla,
        "tendencia": tendencia_atual,
        "sinal": sinal,
        "mudou": mudou
    }

def executar_ordem(binance_client, analise):
    cripto = analise["cripto"]
    symbol = cripto["symbol"]
    sinal = analise["sinal"]
    
    if sinal == "MANTER":
        return None
    
    try:
        binance_client.futures_change_leverage(symbol=symbol, leverage=ALAVANCAGEM)
        
        try:
            binance_client.futures_change_margin_type(symbol=symbol, marginType="ISOLATED")
        except:
            pass
        
        positions = binance_client.futures_position_information(symbol=symbol)
        pos = next((p for p in positions if float(p["positionAmt"]) != 0), None)
        
        if pos:
            amt = abs(float(pos["positionAmt"]))
            side = "SELL" if float(pos["positionAmt"]) > 0 else "BUY"
            binance_client.futures_create_order(symbol=symbol, side=side, type="MARKET", quantity=amt)
            print(f"  ✓ Posição anterior fechada")
        
        capital_alocado = CAPITAL_INICIAL * cripto["alocacao"]
        capital_com_alavancagem = capital_alocado * ALAVANCAGEM
        quantidade = capital_com_alavancagem / analise["preco"]
        quantidade = round(quantidade, 3)
        
        if sinal == "COMPRAR":
            order = binance_client.futures_create_order(symbol=symbol, side="BUY", type="MARKET", quantity=quantidade)
            print(f"  ✓ LONG aberto: {quantidade} @ ${analise['preco']:.2f}")
        elif sinal == "VENDER":
            order = binance_client.futures_create_order(symbol=symbol, side="SELL", type="MARKET", quantity=quantidade)
            print(f"  ✓ SHORT aberto: {quantidade} @ ${analise['preco']:.2f}")
        
        return order
        
    except Exception as e:
        print(f"  ✗ Erro ao executar ordem: {e}")
        return None

def executar_analise_completa():
    print("\n" + "="*50)
    print(f"  MAGNUS WEALTH - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*50)
    
    binance_client = None
    if BINANCE_API_KEY != "SUA_API_KEY_AQUI":
        try:
            binance_client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            binance_client.ping()
            print("✓ Binance conectada")
        except Exception as e:
            print(f"✗ Erro ao conectar Binance: {e}")
    
    resultados = []
    sinais_gerados = []
    
    for cripto in CRIPTOS:
        analise = analisar_cripto(cripto)
        if analise:
            resultados.append(analise)
            
            if analise["sinal"] != "MANTER" and binance_client:
                ordem = executar_ordem(binance_client, analise)
                if ordem:
                    sinais_gerados.append(analise)
    
    if sinais_gerados:
        msg = f"🚀 *SINAIS GERADOS* ({len(sinais_gerados)})\n\n"
        for s in sinais_gerados:
            emoji = "🟢" if s["sinal"] == "COMPRAR" else "🔴"
            msg += f"{emoji} *{s['cripto']['nome']}*\n"
            msg += f"Sinal: {s['sinal']}\n"
            msg += f"Preço: ${s['preco']:,.2f}\n\n"
        enviar_telegram(msg)
    else:
        print("\n✓ Nenhum sinal gerado")
    
    print("\n" + "="*50)
    print("  ANÁLISE CONCLUÍDA")
    print("="*50 + "\n")

if __name__ == "__main__":
    print("═══════════════════════════════════════")
    print("  MAGNUS WEALTH - TRADING BOT")
    print("═══════════════════════════════════════\n")
    
    schedule.every().day.at("21:00").do(executar_analise_completa)
    
    print("✓ Bot iniciado")
    print("✓ Agendamento: Todos os dias às 21:00")
    print("\nPressione Ctrl+C para parar\n")
    
    print("Executando análise inicial...")
    executar_analise_completa()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
FIM_DO_CODIGO
```

**Pronto! Arquivo criado ✓**

---

## ✅ PASSO 3: TESTAR O BOT

**Cole isso no Termux:**

```bash
python magnus_bot.py
```

**O que vai acontecer:**
1. Vai aparecer "MAGNUS WEALTH - TRADING BOT"
2. Vai mostrar "Bot iniciado"
3. Vai executar análise inicial
4. Vai analisar as 8 criptos
5. Se tiver sinal, vai executar ordem na Binance
6. Vai ficar aguardando até às 21h

**Para parar:** Pressione `Ctrl+C`

---

## ✅ PASSO 4: RODAR EM SEGUNDO PLANO (OPCIONAL)

Se quiser que rode mesmo com tela bloqueada:

```bash
nohup python magnus_bot.py > bot.log 2>&1 &
```

**Ver se está rodando:**
```bash
ps aux | grep magnus_bot
```

**Ver logs:**
```bash
tail -f bot.log
```

**Parar:**
```bash
pkill -f magnus_bot.py
```

---

## 📊 O QUE O BOT FAZ

### Às 21h todos os dias:

1. **Busca dados** do Yahoo Finance
2. **Calcula Gann HiLo** para cada cripto
3. **Detecta sinais** (COMPRAR/VENDER/MANTER)
4. **Se tiver sinal:**
   - Fecha posição antiga
   - Abre nova posição (LONG ou SHORT)
   - Usa alavancagem 12x
   - Margem isolada
5. **Envia notificação** ao Telegram (se configurado)

---

## ⚙️ CONFIGURAÇÕES (OPCIONAL)

**Mudar capital inicial:**
Linha 12: `CAPITAL_INICIAL = 2000` → Mude para o valor que quiser

**Mudar alavancagem:**
Linha 29: `ALAVANCAGEM = 12` → Mude para 5, 10, 15, etc

**Adicionar Telegram:**
Linhas 14-15: Cole token e chat ID do seu bot

---

## 🎯 RESUMO RÁPIDO

```bash
# 1. Instalar
pip install yfinance pandas python-binance schedule

# 2. Criar arquivo (cole o código acima)
cat > magnus_bot.py << 'FIM_DO_CODIGO'
...
FIM_DO_CODIGO

# 3. Rodar
python magnus_bot.py
```

**PRONTO! Bot funcionando!** 🚀

---

## ❓ DÚVIDAS COMUNS

**P: Precisa ficar com Termux aberto?**
R: Não, pode bloquear a tela. Use `nohup` (passo 4)

**P: Vai gastar muita bateria?**
R: Não, o bot fica dormindo e acorda às 21h

**P: E se o celular reiniciar?**
R: Precisa rodar o comando novamente

**P: Como sei se está funcionando?**
R: Veja o arquivo `bot.log` com `tail -f bot.log`

---

**Alguma dúvida? Me pergunte!** 😊

