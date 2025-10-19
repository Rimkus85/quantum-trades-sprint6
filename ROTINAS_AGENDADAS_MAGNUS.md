# Rotinas Agendadas do Magnus Wealth

**Versão:** 7.3.0  
**Data:** 18/10/2025  
**Autor:** Manus AI

---

## 📅 Visão Geral

O Magnus Wealth possui um sistema completo de automação com **7 rotinas agendadas** que operam 24/7 via **cron jobs**, garantindo análises contínuas e envio automático de relatórios para o grupo do Telegram.

---

## 🤖 Rotinas Implementadas

### 1. **Análise Diária** 📊
**Arquivo:** `analise_diaria.py` (6.6 KB)  
**Horário:** 21:00 (todos os dias)  
**Cron:** `0 21 * * *`

**Descrição:**  
Executa análise completa do dia após o fechamento do mercado (17:00). Processa todas as mensagens do Telegram, identifica carteiras recomendadas e envia relatório consolidado para o grupo Magnus Wealth.

**Funcionalidades:**
- Leitura de mensagens do Telegram
- Identificação de tickers e recomendações
- Análise de sentimento
- Geração de relatório diário
- Envio automático para o grupo

**Log:** `logs/analise_diaria.log`

---

### 2. **Análise de Opções** 📈
**Arquivo:** `analise_opcoes.py` (7.6 KB)  
**Horários:** 10:10, 14:00, 16:45 (dias úteis)  
**Cron:**
- `10 10 * * 1-5` (Abertura)
- `0 14 * * 1-5` (Meio-dia)
- `45 16 * * 1-5` (Pré-fechamento)

**Descrição:**  
Monitora e analisa opções em 3 momentos estratégicos do pregão:
- **10:10** - Análise pós-abertura (mercado abre às 10:00)
- **14:00** - Análise meio-dia
- **16:45** - Análise pré-fechamento (mercado fecha às 17:00)

**Funcionalidades:**
- Identificação de opções mencionadas
- Análise de volatilidade
- Detecção de oportunidades
- Alertas em tempo real

**Log:** `logs/analise_opcoes.log`

---

### 3. **Resumo Semanal** 📅
**Arquivo:** `resumo_semanal.py` (8.6 KB)  
**Horário:** Sábado 10:00  
**Cron:** `0 10 * * 6`

**Descrição:**  
Gera relatório consolidado da semana com estatísticas, performance das recomendações e insights do Magnus Brain.

**Funcionalidades:**
- Consolidação de todas as análises da semana
- Estatísticas de performance
- Top ativos recomendados
- Aprendizados do Magnus
- Envio para o grupo

**Log:** `logs/resumo_semanal.log`

---

### 4. **Bot de Comandos** 🤖
**Arquivo:** `bot_comandos.py` (11 KB)  
**Execução:** Contínua (daemon)  
**Modo:** Serviço systemd

**Descrição:**  
Bot interativo que responde a comandos dos usuários no grupo do Telegram 24/7.

**Comandos disponíveis:**
- `/ajuda` - Lista de comandos
- `/status` - Status do sistema
- `/carteiras` - Carteiras recomendadas
- `/analise` - Última análise
- `/opcoes` - Análise de opções
- `/perfil` - Perfil de investidor
- `/alertas` - Sistema de alertas

**Modo de execução:** Processo em background via systemd

---

### 5. **Limpeza de Logs** 🧹
**Horário:** Domingo 02:00  
**Cron:** `0 2 * * 0`

**Descrição:**  
Remove logs com mais de 30 dias para economizar espaço em disco.

**Comando:**
```bash
find $LOGS_DIR -name "*.log" -type f -mtime +30 -delete
```

---

### 6. **Backup de Dados** 💾
**Horário:** Domingo 03:00  
**Cron:** `0 3 * * 0`

**Descrição:**  
Faz backup semanal da base de conhecimento do Magnus, logs e arquivos JSON importantes.

**Comando:**
```bash
tar -czf backups/backup_$(date +%Y%m%d).tar.gz youtube_knowledge/ logs/ *.json
```

**Localização:** `backups/backup_YYYYMMDD.tar.gz`

---

### 7. **Monitoramento de Saúde** ❤️
**Horário:** A cada 6 horas (00:00, 06:00, 12:00, 18:00)  
**Cron:** `0 */6 * * *` (comentado por padrão)

**Descrição:**  
Verifica se todos os serviços estão funcionando corretamente e envia alertas em caso de problemas.

**Status:** Desabilitado por padrão (linha comentada no crontab)

---

## 📂 Estrutura de Arquivos

```
backend/quantum-trades-backend/
├── analise_diaria.py          # Rotina diária
├── analise_opcoes.py          # Rotina de opções
├── resumo_semanal.py          # Rotina semanal
├── bot_comandos.py            # Bot interativo
├── crontab_magnus.txt         # Configuração do cron
├── setup_agendamento.sh       # Script de instalação
├── logs/                      # Logs das rotinas
│   ├── analise_diaria.log
│   ├── analise_opcoes.log
│   ├── resumo_semanal.log
│   └── health_check.log
└── backups/                   # Backups semanais
    └── backup_YYYYMMDD.tar.gz
```

---

## 🚀 Como Instalar

### Opção 1: Script Automático
```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
chmod +x setup_agendamento.sh
./setup_agendamento.sh
```

### Opção 2: Manual
```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
crontab crontab_magnus.txt
```

---

## 🔍 Verificar Status

### Ver cron jobs instalados
```bash
crontab -l
```

### Ver logs em tempo real
```bash
# Análise diária
tail -f logs/analise_diaria.log

# Análise de opções
tail -f logs/analise_opcoes.log

# Resumo semanal
tail -f logs/resumo_semanal.log
```

### Verificar se o bot está rodando
```bash
ps aux | grep bot_comandos.py
```

---

## 📊 Cronograma Semanal

| Dia       | Horário | Rotina                    |
|-----------|---------|---------------------------|
| Seg-Sex   | 10:10   | Análise de Opções         |
| Seg-Sex   | 14:00   | Análise de Opções         |
| Seg-Sex   | 16:45   | Análise de Opções         |
| Todos     | 21:00   | Análise Diária            |
| Sábado    | 10:00   | Resumo Semanal            |
| Domingo   | 02:00   | Limpeza de Logs           |
| Domingo   | 03:00   | Backup de Dados           |
| 24/7      | -       | Bot de Comandos (daemon)  |

---

## ⚙️ Configuração

Todas as configurações estão no arquivo `crontab_magnus.txt`:

```bash
# Diretórios
MAGNUS_DIR=/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
PYTHON=/usr/bin/python3
LOGS_DIR=/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/logs
```

---

## 🛠️ Manutenção

### Desabilitar uma rotina
Edite `crontab_magnus.txt` e comente a linha com `#`:
```bash
# 0 21 * * * cd $MAGNUS_DIR && $PYTHON analise_diaria.py >> $LOGS_DIR/analise_diaria.log 2>&1
```

### Alterar horários
Edite os valores do cron:
```bash
# Mudar de 21:00 para 20:00
0 20 * * * cd $MAGNUS_DIR && $PYTHON analise_diaria.py >> $LOGS_DIR/analise_diaria.log 2>&1
```

### Recarregar configurações
```bash
crontab crontab_magnus.txt
```

---

## 📝 Notas Importantes

1. **Fuso Horário:** Todos os horários são baseados no fuso horário do servidor
2. **Dependências:** Certifique-se de que o Python 3 e todas as bibliotecas estão instaladas
3. **Telegram:** As credenciais do Telegram devem estar configuradas no `.env`
4. **Logs:** Os logs crescem com o tempo, a limpeza automática mantém apenas 30 dias
5. **Backups:** Backups semanais são criados automaticamente aos domingos

---

## ✅ Status Atual

- ✅ 7 rotinas implementadas
- ✅ Cron jobs configurados
- ✅ Logs funcionando
- ✅ Bot interativo operacional
- ✅ Sistema de backup ativo
- ✅ Totalmente autônomo (24/7)

