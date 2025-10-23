# 🤖 Configuração do GitHub Actions - Execução Automática

## ✅ Solução Implementada

O sistema agora usa **GitHub Actions** para executar automaticamente a análise de criptomoedas **todos os dias às 21:50 horário de Brasília**, sem necessidade de servidor externo ou intervenção humana.

---

## 🎯 Como Funciona

1. **GitHub Actions** é um serviço gratuito do GitHub que executa código na nuvem
2. O workflow está configurado para rodar diariamente no horário definido
3. As credenciais ficam armazenadas de forma segura nos **Secrets** do GitHub
4. A sessão do Telegram é restaurada automaticamente a cada execução
5. A mensagem é enviada ao Telegram sem intervenção humana

---

## 🔐 Configurar Secrets no GitHub

### Passo 1: Acessar Configurações do Repositório

1. Acesse: https://github.com/Rimkus85/quantum-trades-sprint6
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret**

### Passo 2: Adicionar os Secrets

Adicione cada um dos seguintes secrets (um por vez):

#### Secret 1: TELEGRAM_API_ID
- **Name:** `TELEGRAM_API_ID`
- **Value:** `20866496`

#### Secret 2: TELEGRAM_API_HASH
- **Name:** `TELEGRAM_API_HASH`
- **Value:** `b3634619ea4d9c7d039a372801165bbf`

#### Secret 3: TELEGRAM_PHONE
- **Name:** `TELEGRAM_PHONE`
- **Value:** `+5511974169060`

#### Secret 4: TELEGRAM_PASSWORD
- **Name:** `TELEGRAM_PASSWORD`
- **Value:** `gatinha01*`

#### Secret 5: TELEGRAM_GROUP_ID
- **Name:** `TELEGRAM_GROUP_ID`
- **Value:** `-4844836232`

#### Secret 6: TELEGRAM_SESSION_BASE64
- **Name:** `TELEGRAM_SESSION_BASE64`
- **Value:** (copie o conteúdo do arquivo abaixo)

**Para obter o valor do TELEGRAM_SESSION_BASE64:**

Execute este comando no terminal:
```bash
cat /tmp/session_base64.txt
```

Copie **TODO** o texto que aparecer (são ~136.000 caracteres) e cole no campo Value.

---

## ✅ Verificar Configuração

Após adicionar todos os secrets, você deve ter **6 secrets** configurados:

- ✅ TELEGRAM_API_ID
- ✅ TELEGRAM_API_HASH
- ✅ TELEGRAM_PHONE
- ✅ TELEGRAM_PASSWORD
- ✅ TELEGRAM_GROUP_ID
- ✅ TELEGRAM_SESSION_BASE64

---

## 🚀 Testar Execução Manual

Antes de esperar o horário agendado, você pode testar manualmente:

1. Acesse: https://github.com/Rimkus85/quantum-trades-sprint6/actions
2. Clique em **Análise Diária de Criptomoedas** (no menu lateral)
3. Clique em **Run workflow** (botão à direita)
4. Clique em **Run workflow** (botão verde)
5. Aguarde ~1-2 minutos
6. Verifique o Telegram para a mensagem

---

## ⏰ Horário de Execução

**Configurado para:** Diariamente às 21:50 horário de Brasília (GMT-3)

**Cron expression:** `50 0 * * *` (00:50 UTC = 21:50 Brasília)

### Alterar Horário (se necessário)

Para alterar o horário, edite o arquivo `.github/workflows/analise-cripto-diaria.yml`:

```yaml
schedule:
  - cron: '50 0 * * *'  # Minuto Hora * * *
```

**Exemplos:**
- `0 21 * * *` = 18:00 Brasília (21:00 UTC)
- `30 22 * * *` = 19:30 Brasília (22:30 UTC)
- `0 0 * * *` = 21:00 Brasília (00:00 UTC)

**Lembre-se:** GitHub Actions usa UTC, então subtraia 3 horas do horário de Brasília.

---

## 📊 Monitorar Execuções

### Ver Histórico de Execuções
1. Acesse: https://github.com/Rimkus85/quantum-trades-sprint6/actions
2. Veja todas as execuções passadas
3. Clique em qualquer execução para ver detalhes e logs

### Ver Logs Detalhados
1. Clique em uma execução
2. Clique em **analisar-criptos**
3. Expanda cada step para ver os logs

### Verificar Sucesso
- ✅ **Verde** = Executou com sucesso
- ❌ **Vermelho** = Erro na execução

---

## 🔄 Próximas Execuções

O GitHub Actions executará automaticamente:
- **Primeira execução:** Amanhã às 21:50 (23/10/2025)
- **Frequência:** Todos os dias no mesmo horário
- **Sem intervenção:** Totalmente automático

---

## ⚠️ Importante

### Segurança dos Secrets
- ✅ Os secrets **nunca** aparecem nos logs
- ✅ Apenas o repositório tem acesso
- ✅ Não são expostos em commits ou pull requests

### Limites do GitHub Actions
- ✅ **Gratuito** para repositórios públicos (ilimitado)
- ✅ **2.000 minutos/mês** para repositórios privados
- ✅ Cada execução leva ~1-2 minutos

### Manutenção
- ✅ **Nenhuma manutenção necessária**
- ✅ Executa automaticamente todos os dias
- ✅ Se falhar, você recebe notificação por email

---

## 🆘 Troubleshooting

### Problema: Workflow não executa
**Solução:** Verifique se todos os 6 secrets estão configurados corretamente

### Problema: Erro "Unauthorized"
**Solução:** Verifique se TELEGRAM_API_ID e TELEGRAM_API_HASH estão corretos

### Problema: Erro "Session expired"
**Solução:** 
1. Execute `setup_telegram.py` localmente para criar nova sessão
2. Converta para base64: `base64 -w 0 magnus_session.session`
3. Atualize o secret TELEGRAM_SESSION_BASE64

### Problema: Mensagem não chega no Telegram
**Solução:** Verifique se TELEGRAM_GROUP_ID está correto (-4844836232)

---

## 📝 Resumo dos Próximos Passos

1. ✅ **Commit do workflow já foi feito** (arquivo `.github/workflows/analise-cripto-diaria.yml`)
2. ⏳ **Você precisa:** Configurar os 6 secrets no GitHub (5 minutos)
3. ✅ **Testar:** Executar workflow manualmente para validar
4. ✅ **Pronto:** Sistema funcionará automaticamente todos os dias

---

## 🎉 Vantagens desta Solução

✅ **Totalmente automático** - Zero intervenção humana  
✅ **Gratuito** - GitHub Actions é grátis para repositórios públicos  
✅ **Confiável** - Infraestrutura do GitHub (99.9% uptime)  
✅ **Sem servidor** - Não precisa de VPS, Railway, etc  
✅ **Fácil monitoramento** - Logs e histórico no GitHub  
✅ **Notificações** - Email automático se algo falhar  
✅ **Sessão persistente** - Restaurada automaticamente  
✅ **Alertas visuais** - Emojis chamativos para mudanças  

---

**Configuração criada em:** 22/10/2025 20:48 UTC  
**Status:** ⏳ **Aguardando configuração dos secrets**  
**Próxima execução:** Após configurar secrets, teste manualmente

