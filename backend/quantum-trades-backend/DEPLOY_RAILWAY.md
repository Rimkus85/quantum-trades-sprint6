# 🚀 GUIA DE DEPLOY - RAILWAY

**Magnus Wealth v7.0.0**  
**Data:** 18/10/2025

---

## 📋 VISÃO GERAL

Este guia explica como fazer o deploy do Magnus Wealth no **Railway**, uma plataforma de cloud que oferece:

- ✅ **Plano gratuito** com $5 de crédito mensal
- ✅ **Deploy automático** via GitHub
- ✅ **Uptime 24/7** garantido
- ✅ **Logs centralizados**
- ✅ **Fácil configuração**

---

## 🎯 PRÉ-REQUISITOS

1. **Conta no Railway**
   - Acesse: https://railway.app
   - Faça login com GitHub

2. **Repositório no GitHub**
   - Repositório: https://github.com/Rimkus85/quantum-trades-sprint6
   - Branch: main

3. **Credenciais do Telegram**
   - API ID
   - API Hash
   - Telefone
   - Sessão (magnus_session.session)

---

## 📦 PASSO 1: PREPARAR O PROJETO

### 1.1. Criar arquivo Procfile

O Railway usa o Procfile para saber como executar o projeto.

**Criar arquivo:** `backend/quantum-trades-backend/Procfile`

```
# Magnus Wealth - Procfile para Railway

# Bot de comandos (processo principal)
bot: python3 bot_comandos.py

# API Flask (opcional, se quiser expor API)
# web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### 1.2. Criar arquivo railway.json

Configurações específicas do Railway.

**Criar arquivo:** `backend/quantum-trades-backend/railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python3 bot_comandos.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 1.3. Atualizar requirements.txt

Garantir que todas as dependências estão listadas.

**Arquivo:** `backend/quantum-trades-backend/requirements.txt`

```
telethon
python-dotenv
flask
gunicorn
```

### 1.4. Criar arquivo .env.example

Template para variáveis de ambiente.

**Criar arquivo:** `backend/quantum-trades-backend/.env.example`

```bash
# Telegram API Credentials
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+5511999999999

# Flask Configuration (opcional)
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

---

## 🚀 PASSO 2: DEPLOY NO RAILWAY

### 2.1. Criar Novo Projeto

1. Acesse: https://railway.app/dashboard
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha: `Rimkus85/quantum-trades-sprint6`
5. Selecione o diretório: `backend/quantum-trades-backend`

### 2.2. Configurar Variáveis de Ambiente

No painel do Railway:

1. Vá em **"Variables"**
2. Adicione as variáveis:

```
TELEGRAM_API_ID = seu_api_id
TELEGRAM_API_HASH = seu_api_hash
TELEGRAM_PHONE = +5511999999999
```

### 2.3. Upload da Sessão do Telegram

A sessão do Telegram (`magnus_session.session`) precisa estar no servidor.

**Opção 1: Via GitHub (Recomendado)**
```bash
# No seu computador local
cd quantum-trades-sprint6/backend/quantum-trades-backend
git add magnus_session.session
git commit -m "Add Telegram session"
git push origin main
```

**Opção 2: Via Railway CLI**
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link ao projeto
railway link

# Upload de arquivo
railway run bash
# Depois fazer upload manual via interface
```

### 2.4. Configurar Cron Jobs

O Railway não suporta cron nativamente. Use **Railway Cron** ou **GitHub Actions**.

**Opção A: Railway Cron (Pago)**
- Disponível apenas em planos pagos

**Opção B: GitHub Actions (Grátis)**

Criar arquivo: `.github/workflows/magnus-cron.yml`

```yaml
name: Magnus Wealth - Cron Jobs

on:
  schedule:
    # Análise diária - 21:00 UTC-3 = 00:00 UTC
    - cron: '0 0 * * *'
    
    # Análise opções - 10:10, 14:00, 16:45 UTC-3
    - cron: '10 13 * * 1-5'  # 10:10
    - cron: '0 17 * * 1-5'   # 14:00
    - cron: '45 19 * * 1-5'  # 16:45
    
    # Resumo semanal - Sábado 10:00 UTC-3 = 13:00 UTC
    - cron: '0 13 * * 6'

jobs:
  run-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Railway Deployment
        run: |
          curl -X POST ${{ secrets.RAILWAY_WEBHOOK_URL }}
```

**Opção C: Serviço Externo (EasyCron)**
- https://www.easycron.com (grátis até 100 jobs)
- Configurar para chamar webhook do Railway

---

## 🔧 PASSO 3: CONFIGURAR SERVIÇOS

### 3.1. Bot de Comandos (24/7)

O bot de comandos deve rodar continuamente.

**No Railway:**
1. Processo: `bot`
2. Comando: `python3 bot_comandos.py`
3. Restart Policy: `ON_FAILURE`

### 3.2. Análises Agendadas

Como o Railway não tem cron nativo, use uma das opções:

**Opção 1: Webhook + Serviço Externo**

Criar endpoint na API para receber webhooks:

```python
# Em app.py
@app.route('/cron/analise-diaria', methods=['POST'])
def cron_analise_diaria():
    # Verificar token de segurança
    token = request.headers.get('X-Cron-Token')
    if token != os.getenv('CRON_TOKEN'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Executar análise em background
    asyncio.create_task(executar_analise_diaria())
    
    return jsonify({'status': 'ok'})
```

Depois configurar no EasyCron:
- URL: `https://seu-app.railway.app/cron/analise-diaria`
- Header: `X-Cron-Token: seu_token_secreto`
- Schedule: `0 21 * * *` (21:00)

**Opção 2: Servidor VPS Separado**

Manter o Railway apenas para o bot de comandos, e usar um VPS (DigitalOcean, AWS) para os cron jobs.

---

## 📊 PASSO 4: MONITORAMENTO

### 4.1. Logs do Railway

Acessar logs em tempo real:
1. Dashboard do Railway
2. Aba **"Deployments"**
3. Clicar no deployment ativo
4. Ver **"Logs"**

### 4.2. Health Check

Criar endpoint de health check:

```python
# Em app.py
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '7.0.0',
        'services': {
            'bot': 'running',
            'telegram': 'connected'
        }
    })
```

Configurar monitoramento externo:
- UptimeRobot: https://uptimerobot.com (grátis)
- Configurar para verificar `/health` a cada 5 minutos

---

## 💰 CUSTOS ESTIMADOS

### Railway - Plano Gratuito
- **Crédito mensal:** $5
- **Uso estimado:** ~$3-4/mês
- **Conclusão:** ✅ **Grátis** (dentro do crédito)

### Railway - Plano Hobby ($5/mês)
- **Crédito mensal:** $5 + uso
- **Recursos:** Mais CPU e RAM
- **Conclusão:** Recomendado se exceder o plano grátis

### Alternativas

| Plataforma | Custo/mês | Uptime | Cron |
|------------|-----------|--------|------|
| Railway | $0-5 | 99.9% | ❌ (via webhook) |
| Heroku | $7 | 99.9% | ❌ (via addon) |
| DigitalOcean | $5 | 99.9% | ✅ Nativo |
| AWS EC2 | $5-10 | 99.9% | ✅ Nativo |
| Render | $0-7 | 99.9% | ❌ (via webhook) |

**Recomendação:** Railway para bot + DigitalOcean ($5) para cron jobs

---

## 🔐 SEGURANÇA

### 5.1. Variáveis de Ambiente

✅ **NUNCA** commitar `.env` no GitHub  
✅ Usar variáveis de ambiente do Railway  
✅ Adicionar `.env` no `.gitignore`

### 5.2. Sessão do Telegram

⚠️ **CUIDADO:** A sessão do Telegram é sensível!

**Opções:**
1. **Commit no repositório privado** (se o repo for privado)
2. **Upload manual via Railway CLI**
3. **Gerar nova sessão no Railway** (requer autenticação)

### 5.3. Tokens de Webhook

Se usar webhooks para cron:
- Gerar token aleatório forte
- Armazenar em variável de ambiente
- Validar em cada requisição

---

## 🧪 PASSO 5: TESTAR DEPLOY

### 5.1. Verificar Bot

1. Acessar logs do Railway
2. Verificar mensagem: `✅ Conectado ao Telegram!`
3. No grupo Magnus Wealth, enviar: `/status`
4. Bot deve responder

### 5.2. Testar Análise Manual

Via Railway CLI:
```bash
railway run python3 analise_diaria.py
```

Ou criar endpoint de teste:
```python
@app.route('/test/analise-diaria', methods=['POST'])
def test_analise_diaria():
    # Executar análise
    asyncio.create_task(executar_analise_diaria())
    return jsonify({'status': 'triggered'})
```

---

## 📝 CHECKLIST DE DEPLOY

- [ ] Criar conta no Railway
- [ ] Conectar repositório GitHub
- [ ] Adicionar variáveis de ambiente
- [ ] Upload da sessão do Telegram
- [ ] Configurar Procfile
- [ ] Deploy do projeto
- [ ] Verificar logs
- [ ] Testar bot de comandos (`/status`)
- [ ] Configurar cron jobs (webhook ou externo)
- [ ] Configurar monitoramento (UptimeRobot)
- [ ] Testar análise manual
- [ ] Documentar URLs e credenciais

---

## 🆘 TROUBLESHOOTING

### Problema: Bot não conecta ao Telegram

**Solução:**
1. Verificar variáveis de ambiente
2. Verificar se sessão foi enviada
3. Gerar nova sessão se necessário

### Problema: Cron jobs não executam

**Solução:**
1. Verificar configuração do webhook
2. Testar endpoint manualmente
3. Verificar logs do serviço de cron

### Problema: Aplicação crashando

**Solução:**
1. Verificar logs do Railway
2. Aumentar recursos (upgrade de plano)
3. Verificar dependências no requirements.txt

---

## 📚 RECURSOS ÚTEIS

- **Railway Docs:** https://docs.railway.app
- **Railway CLI:** https://docs.railway.app/develop/cli
- **Telethon Docs:** https://docs.telethon.dev
- **UptimeRobot:** https://uptimerobot.com
- **EasyCron:** https://www.easycron.com

---

## ✅ PRÓXIMOS PASSOS

Após deploy bem-sucedido:

1. ✅ Monitorar logs por 24-48h
2. ✅ Verificar se análises estão sendo enviadas
3. ✅ Configurar alertas de downtime
4. ✅ Documentar URLs e credenciais
5. ✅ Fazer backup da configuração

---

**Magnus Wealth v7.0.0** - Deploy no Railway 🚀

