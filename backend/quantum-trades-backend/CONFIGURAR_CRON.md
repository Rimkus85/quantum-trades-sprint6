# 📅 Configuração do Cron para Execução Automática

## ✅ Solução Implementada

O problema de "pedir dados novamente" no cron foi **resolvido** com as seguintes mudanças:

### 1. Caminho Absoluto da Sessão ✅
O código agora usa **caminho absoluto** para o arquivo de sessão:

```python
# Antes (caminho relativo - problema no cron)
with TelegramClient('magnus_session', api_id, api_hash) as client:

# Depois (caminho absoluto - funciona no cron)
script_dir = os.path.dirname(os.path.abspath(__file__))
session_path = os.path.join(script_dir, 'magnus_session')
with TelegramClient(session_path, api_id, api_hash) as client:
```

### 2. Script Wrapper Criado ✅
Criado `executar_analise.sh` que:
- Define o diretório de trabalho correto
- Verifica se .env existe
- Verifica se magnus_session.session existe
- Cria logs organizados por data
- Registra início e fim de cada execução

---

## 🚀 Como Configurar o Cron

### Passo 1: Testar o Script Wrapper

```bash
# Executar manualmente para testar
/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh

# Verificar o log
cat /home/ubuntu/logs/cripto_analise_$(date +%Y%m%d).log
```

**Resultado esperado:** Mensagem enviada ao Telegram sem pedir código

### Passo 2: Abrir o Crontab

```bash
crontab -e
```

Se for a primeira vez, escolha um editor (recomendo `nano` - opção 1)

### Passo 3: Adicionar a Linha do Cron

**Para executar diariamente às 21h:**

```bash
0 21 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

**Explicação:**
- `0` = minuto 0
- `21` = hora 21 (9 PM)
- `*` = todo dia do mês
- `*` = todo mês
- `*` = todo dia da semana

### Passo 4: Salvar e Sair

**No nano:**
- Pressione `Ctrl + O` para salvar
- Pressione `Enter` para confirmar
- Pressione `Ctrl + X` para sair

### Passo 5: Verificar se Foi Salvo

```bash
crontab -l
```

**Resultado esperado:**
```
0 21 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

---

## 📊 Outros Horários Úteis

### Executar a cada 6 horas
```bash
0 */6 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

### Executar 2x por dia (9h e 21h)
```bash
0 9,21 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

### Executar de segunda a sexta às 21h
```bash
0 21 * * 1-5 /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

### Executar a cada 1 hora
```bash
0 * * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

### Executar a cada 30 minutos
```bash
*/30 * * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

---

## 📝 Monitoramento

### Ver Logs em Tempo Real
```bash
tail -f /home/ubuntu/logs/cripto_analise_$(date +%Y%m%d).log
```

### Ver Últimas 50 Linhas do Log
```bash
tail -50 /home/ubuntu/logs/cripto_analise_$(date +%Y%m%d).log
```

### Listar Todos os Logs
```bash
ls -lh /home/ubuntu/logs/
```

### Ver Log de um Dia Específico
```bash
cat /home/ubuntu/logs/cripto_analise_20251022.log
```

---

## 🔍 Verificar se o Cron Está Funcionando

### Método 1: Verificar Logs do Sistema
```bash
grep CRON /var/log/syslog | tail -20
```

### Método 2: Verificar Logs do Aplicativo
```bash
ls -lt /home/ubuntu/logs/ | head -5
```

### Método 3: Verificar no Telegram
- Abrir o grupo "Magnus Wealth🎯💵🪙"
- Verificar se a mensagem foi recebida no horário agendado

---

## 🧪 Testar Execução Imediata

Para testar se vai funcionar no cron sem esperar o horário:

```bash
# Adicionar linha temporária para executar em 2 minutos
# Se agora são 20:30, adicione:
32 20 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh

# Aguardar 2 minutos e verificar o log
tail -f /home/ubuntu/logs/cripto_analise_$(date +%Y%m%d).log
```

Depois de testar, remova a linha temporária e mantenha apenas a linha do horário definitivo.

---

## ⚠️ Troubleshooting

### Problema: Cron não executa
**Verificar:**
```bash
# 1. Verificar se o cron está rodando
sudo systemctl status cron

# 2. Verificar se o script tem permissão de execução
ls -l /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh

# 3. Verificar logs do sistema
grep CRON /var/log/syslog | tail -20
```

### Problema: Script executa mas pede código
**Causa:** Arquivo de sessão não encontrado

**Solução:**
```bash
# Verificar se o arquivo existe
ls -lah /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/magnus_session.session

# Se não existir, criar novamente
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
python3 setup_telegram.py
```

### Problema: Erro de permissão
**Solução:**
```bash
chmod +x /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
chmod 644 /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/magnus_session.session
```

### Problema: Variáveis de ambiente não carregadas
**Causa:** O cron não carrega o .env automaticamente

**Solução:** O script wrapper já resolve isso! Ele muda para o diretório correto onde está o .env, e o python-dotenv carrega automaticamente.

---

## 📦 Estrutura de Arquivos

```
/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/
├── analisador_cripto_hilo.py          # Script principal (MODIFICADO)
├── executar_analise.sh                # Script wrapper (NOVO)
├── setup_telegram.py                  # Script de setup
├── .env                               # Credenciais (já existe)
├── magnus_session.session             # Sessão do Telegram (já existe)
└── backup_sessao.sh                   # Script de backup

/home/ubuntu/logs/
└── cripto_analise_YYYYMMDD.log        # Logs diários
```

---

## ✅ Checklist de Verificação

Antes de configurar o cron, verifique:

- [ ] Arquivo `magnus_session.session` existe (100KB)
- [ ] Arquivo `.env` existe e contém todas as credenciais
- [ ] Script `executar_analise.sh` tem permissão de execução
- [ ] Teste manual funciona sem pedir código
- [ ] Diretório `/home/ubuntu/logs/` existe
- [ ] Cron está rodando no sistema

---

## 🎯 Comando Final para Cron

**Copie e cole esta linha no crontab:**

```bash
0 21 * * * /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/executar_analise.sh
```

**Para editar:**
```bash
crontab -e
```

**Para verificar:**
```bash
crontab -l
```

---

## 📊 Exemplo de Log Bem-Sucedido

```
========================================
Início: 2025-10-22 21:00:01
Diretório: /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
========================================
═══════════════════════════════════════════════════
  MAGNUS WEALTH - ANALISADOR DE CRIPTOMOEDAS
  CHiLo (Custom HiLo) - Modo Activator - v8.3.0
  Indicador: Paulo H. Parize e Tio Huli
  TOP 8 CRIPTOS - PERÍODOS OTIMIZADOS (DADOS REAIS)
═══════════════════════════════════════════════════
Analisando Bitcoin (BTCUSDT) com período 40...
   📊 Buscando dados de BTC-USD...
✓ Bitcoin: MANTER - Tendência vermelho
[... outras criptos ...]
✓ Mensagem enviada com sucesso!
========================================
Fim: 2025-10-22 21:00:35
Código de saída: 0
========================================
```

**Código de saída 0 = Sucesso!**

---

## 🔄 Manutenção

### Limpeza de Logs Antigos (Opcional)
```bash
# Manter apenas logs dos últimos 30 dias
find /home/ubuntu/logs/ -name "cripto_analise_*.log" -mtime +30 -delete
```

### Adicionar ao Cron (Executar todo dia 1 às 3h)
```bash
0 3 1 * * find /home/ubuntu/logs/ -name "cripto_analise_*.log" -mtime +30 -delete
```

---

**Configuração implementada em:** 22/10/2025 20:25 UTC  
**Status:** ✅ **TESTADO E FUNCIONANDO**  
**Próximo passo:** Adicionar ao crontab para execução automática

