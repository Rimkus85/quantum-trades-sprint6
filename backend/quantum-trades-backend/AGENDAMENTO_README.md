# ⏰ SISTEMA DE AGENDAMENTO - MAGNUS WEALTH

**Versão:** 7.0.0  
**Data:** 18/10/2025

---

## 📋 VISÃO GERAL

O Sistema de Agendamento do Magnus Wealth automatiza todas as análises e relatórios, tornando o sistema **completamente autônomo**.

---

## 🎯 FUNCIONALIDADES

### 1. **Análise Diária** 📊
- **Horário:** 21:00 (todos os dias)
- **Script:** `analise_diaria.py`
- **Função:** Análise completa do dia após fechamento do mercado
- **Output:** Mensagem no grupo Magnus Wealth

### 2. **Análise de Opções** 📈
- **Horários:** 10:10, 14:00, 16:45 (dias úteis)
- **Script:** `analise_opcoes.py`
- **Função:** Monitoramento de montagens/desmontagens de opções
- **Output:** Alertas no grupo Magnus Wealth

### 3. **Resumo Semanal** 📋
- **Horário:** Sábado às 10:00
- **Script:** `resumo_semanal.py`
- **Função:** Resumo consolidado da semana
- **Output:** Relatório completo no grupo

### 4. **Bot de Comandos** 🤖
- **Execução:** Contínua (24/7)
- **Script:** `bot_comandos.py`
- **Função:** Responde comandos dos usuários
- **Comandos:** `/ajuda`, `/status`, `/carteiras`, `/analise`, `/opcoes`

---

## 🚀 INSTALAÇÃO

### Opção 1: Instalação Automática (Recomendado)

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
chmod +x setup_agendamento.sh
./setup_agendamento.sh
```

O script irá:
- ✅ Verificar dependências
- ✅ Criar diretórios necessários
- ✅ Tornar scripts executáveis
- ✅ Instalar crontab
- ✅ Configurar logs

### Opção 2: Instalação Manual

#### 2.1. Criar diretórios
```bash
mkdir -p logs backups youtube_knowledge
```

#### 2.2. Tornar scripts executáveis
```bash
chmod +x analise_diaria.py
chmod +x analise_opcoes.py
chmod +x resumo_semanal.py
chmod +x bot_comandos.py
```

#### 2.3. Instalar crontab
```bash
crontab crontab_magnus.txt
```

#### 2.4. Verificar instalação
```bash
crontab -l
```

---

## 🔧 CONFIGURAÇÃO

### Variáveis de Ambiente

Criar arquivo `.env` com suas credenciais:

```bash
cp .env.example .env
nano .env
```

Preencher:
```
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999
```

### Sessão do Telegram

Garantir que o arquivo `magnus_session.session` está presente:

```bash
ls -la magnus_session.session
```

Se não existir, executar:
```bash
python3 connect_telegram.py
```

---

## 📅 AGENDAMENTOS CONFIGURADOS

| Tarefa | Horário | Frequência | Script |
|--------|---------|------------|--------|
| Análise Diária | 21:00 | Todos os dias | `analise_diaria.py` |
| Análise Opções (Abertura) | 10:10 | Dias úteis | `analise_opcoes.py` |
| Análise Opções (Meio-dia) | 14:00 | Dias úteis | `analise_opcoes.py` |
| Análise Opções (Fechamento) | 16:45 | Dias úteis | `analise_opcoes.py` |
| Resumo Semanal | Sábado 10:00 | Semanal | `resumo_semanal.py` |
| Limpeza de Logs | Domingo 02:00 | Semanal | Automático |
| Backup de Dados | Domingo 03:00 | Semanal | Automático |

---

## 🤖 BOT DE COMANDOS

### Iniciar Bot (Background)

```bash
nohup python3 bot_comandos.py > logs/bot_comandos.log 2>&1 &
```

### Verificar se está rodando

```bash
ps aux | grep bot_comandos
```

### Parar Bot

```bash
pkill -f bot_comandos.py
```

### Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `/ajuda` | Lista todos os comandos |
| `/status` | Status do sistema |
| `/carteiras` | Carteiras recomendadas |
| `/analise` | Última análise de mercado |
| `/opcoes` | Análise de opções |
| `/perfil` | Perfil de investidor |
| `/alertas` | Sistema de alertas |

---

## 📊 MONITORAMENTO

### Verificar Logs

#### Logs em tempo real
```bash
tail -f logs/*.log
```

#### Log específico
```bash
tail -f logs/analise_diaria.log
tail -f logs/analise_opcoes.log
tail -f logs/resumo_semanal.log
tail -f logs/bot_comandos.log
```

#### Últimas 50 linhas
```bash
tail -n 50 logs/analise_diaria.log
```

### Verificar Crontab

```bash
crontab -l
```

### Verificar Execuções do Cron

```bash
grep CRON /var/log/syslog | tail -20
```

---

## 🧪 TESTES

### Testar Análise Diária

```bash
python3 analise_diaria.py
```

### Testar Análise de Opções

```bash
python3 analise_opcoes.py
```

### Testar Resumo Semanal

```bash
python3 resumo_semanal.py
```

### Testar Bot de Comandos

```bash
python3 bot_comandos.py
```

Depois, no grupo Magnus Wealth, enviar: `/status`

---

## 🔄 MANUTENÇÃO

### Atualizar Horários

Editar o arquivo `crontab_magnus.txt` e reinstalar:

```bash
nano crontab_magnus.txt
crontab crontab_magnus.txt
```

### Adicionar Novo Agendamento

1. Editar `crontab_magnus.txt`
2. Adicionar linha no formato:
   ```
   # Comentário
   minuto hora dia mês dia_semana comando
   ```
3. Reinstalar crontab:
   ```bash
   crontab crontab_magnus.txt
   ```

### Remover Agendamentos

```bash
crontab -r
```

### Backup do Crontab

```bash
crontab -l > crontab_backup_$(date +%Y%m%d).txt
```

---

## 🆘 TROUBLESHOOTING

### Problema: Cron não executa

**Verificar:**
1. Cron está instalado?
   ```bash
   systemctl status cron
   ```

2. Crontab está instalado?
   ```bash
   crontab -l
   ```

3. Logs do cron:
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

**Solução:**
```bash
sudo systemctl start cron
sudo systemctl enable cron
```

### Problema: Script não executa

**Verificar:**
1. Script é executável?
   ```bash
   ls -la analise_diaria.py
   ```

2. Python está instalado?
   ```bash
   which python3
   ```

3. Dependências instaladas?
   ```bash
   pip3 list | grep telethon
   ```

**Solução:**
```bash
chmod +x analise_diaria.py
pip3 install -r requirements.txt
```

### Problema: Bot não conecta ao Telegram

**Verificar:**
1. Arquivo .env existe?
   ```bash
   ls -la .env
   ```

2. Sessão existe?
   ```bash
   ls -la magnus_session.session
   ```

3. Credenciais corretas?
   ```bash
   cat .env
   ```

**Solução:**
```bash
cp .env.example .env
nano .env
python3 connect_telegram.py
```

### Problema: Logs não são criados

**Verificar:**
1. Diretório logs existe?
   ```bash
   ls -la logs/
   ```

2. Permissões corretas?
   ```bash
   ls -ld logs/
   ```

**Solução:**
```bash
mkdir -p logs
chmod 755 logs
```

---

## 📚 ESTRUTURA DE ARQUIVOS

```
backend/quantum-trades-backend/
├── analise_diaria.py          # Script de análise diária
├── analise_opcoes.py          # Script de análise de opções
├── resumo_semanal.py          # Script de resumo semanal
├── bot_comandos.py            # Bot de comandos interativo
├── crontab_magnus.txt         # Configuração do crontab
├── setup_agendamento.sh       # Script de instalação
├── .env                       # Variáveis de ambiente (não commitar!)
├── .env.example               # Template de variáveis
├── magnus_session.session     # Sessão do Telegram (não commitar!)
├── logs/                      # Diretório de logs
│   ├── analise_diaria.log
│   ├── analise_opcoes.log
│   ├── resumo_semanal.log
│   └── bot_comandos.log
├── backups/                   # Backups automáticos
└── youtube_knowledge/         # Base de conhecimento
```

---

## ✅ CHECKLIST DE INSTALAÇÃO

- [ ] Dependências instaladas (`pip3 install -r requirements.txt`)
- [ ] Diretórios criados (`logs/`, `backups/`, `youtube_knowledge/`)
- [ ] Scripts executáveis (`chmod +x *.py`)
- [ ] Arquivo `.env` configurado
- [ ] Sessão do Telegram presente (`magnus_session.session`)
- [ ] Crontab instalado (`crontab crontab_magnus.txt`)
- [ ] Bot de comandos iniciado (`nohup python3 bot_comandos.py &`)
- [ ] Logs verificados (`tail -f logs/*.log`)
- [ ] Teste de comando no grupo (`/status`)

---

## 🚀 PRÓXIMOS PASSOS

Após instalação:

1. ✅ Monitorar logs por 24-48h
2. ✅ Verificar se análises estão sendo enviadas
3. ✅ Testar todos os comandos do bot
4. ✅ Configurar deploy permanente (Railway/DigitalOcean)
5. ✅ Documentar configurações

---

**Magnus Wealth v7.0.0** - Sistema de Agendamento Completo ⏰

