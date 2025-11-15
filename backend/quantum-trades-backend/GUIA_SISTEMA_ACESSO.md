# 🔐 GUIA DO SISTEMA DE ACESSO - MAGNUS WEALTH

## 📋 VISÃO GERAL

Sistema robusto e escalável de controle de acesso ao grupo de sinais do Magnus Wealth via Telegram Bot.

### ✨ Funcionalidades

1. **Geração de Códigos de Acesso** - Admin gera códigos únicos para novos usuários
2. **Validação Automática** - Usuário valida código via bot
3. **Banco de Dados** - Controle de usuários cadastrados
4. **Adição ao Grupo** - Usuário é automaticamente adicionado ao grupo
5. **Notificações** - Admin recebe notificações de novos cadastros

---

## 🚀 INSTALAÇÃO E CONFIGURAÇÃO

### 1. Dependências

```bash
pip3 install telethon python-dotenv requests
```

### 2. Variáveis de Ambiente (.env)

```bash
# Telegram API (Telethon)
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999

# Telegram Bot
TELEGRAM_BOT_TOKEN=seu_bot_token

# ID do grupo de sinais
TELEGRAM_CHAT_ID=-1003183162741

# ID do admin (para notificações)
TELEGRAM_USER_ID=seu_user_id
```

### 3. Iniciar Bot

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/

# Modo foreground (para testes)
python3 bot_acesso_grupo.py

# Modo background (produção)
nohup python3 bot_acesso_grupo.py > logs/bot_acesso.log 2>&1 &
```

---

## 👥 USO DO SISTEMA

### Para o ADMIN

#### 1. Gerar Código de Acesso

```bash
# Sintaxe
python3 database_usuarios.py gerar "<nome>" "<email>" [plano]

# Exemplos
python3 database_usuarios.py gerar "João Silva" "joao@email.com" premium
python3 database_usuarios.py gerar "Maria Santos" "maria@email.com" basico
python3 database_usuarios.py gerar "Pedro Costa" "pedro@email.com" vip
```

**Output:**
```
✅ Código gerado com sucesso!
📋 Código: MAGNUS-A1B2C3D4
👤 Nome: João Silva
📧 Email: joao@email.com
💎 Plano: premium

📤 Envie este código para o usuário usar no bot do Telegram
```

#### 2. Listar Usuários Cadastrados

```bash
python3 database_usuarios.py listar
```

**Output:**
```
📊 USUÁRIOS CADASTRADOS (5)
================================================================================

👤 João Silva
   Telegram ID: 123456789
   Username: @joaosilva
   Email: joao@email.com
   Plano: premium
   Status: ✅ Ativo
   Cadastro: 31/10/2025
```

#### 3. Listar Códigos Pendentes

```bash
python3 database_usuarios.py pendentes
```

**Output:**
```
📋 CÓDIGOS PENDENTES (3)
================================================================================

🔑 MAGNUS-A1B2C3D4
   Nome: Maria Santos
   Email: maria@email.com
   Plano: basico
   Gerado em: 31/10/2025
```

#### 4. Ver Estatísticas

```bash
python3 database_usuarios.py stats
```

**Output:**
```
📊 ESTATÍSTICAS DO SISTEMA
================================================================================
👥 Total de usuários: 10
✅ Usuários ativos: 9
❌ Usuários inativos: 1
🔑 Códigos gerados: 15
✅ Códigos usados: 10
⏳ Códigos pendentes: 5
```

---

### Para o USUÁRIO

#### 1. Iniciar Bot

No Telegram, procurar pelo bot e enviar:
```
/start
```

**Resposta do Bot:**
```
👋 Olá João! Bem-vindo ao Magnus Wealth!

🤖 Sou o bot de acesso ao grupo de sinais de criptomoedas.

Para acessar o grupo, você precisa de um código de acesso.

🔑 Como obter seu código:
1. Entre em contato com nossa equipe
2. Escolha seu plano (Básico, Premium ou VIP)
3. Receba seu código único

📝 Já tem um código?
Digite: /codigo SEU_CODIGO

Exemplo: /codigo MAGNUS-A1B2C3D4
```

#### 2. Validar Código

```
/codigo MAGNUS-A1B2C3D4
```

**Resposta do Bot (Sucesso):**
```
✅ CÓDIGO VALIDADO COM SUCESSO!

🎉 Bem-vindo ao Magnus Wealth, João Silva!

📊 Seu Plano: PREMIUM
📅 Data de Cadastro: 31/10/2025

Você será adicionado ao grupo de sinais em instantes...

✅ ACESSO LIBERADO!

Você foi adicionado ao grupo Magnus Wealth - Sinais!

📊 Lá você receberá:
• Análises diárias de criptomoedas
• Sinais de compra/venda
• Alertas de mudança de tendência
• Otimizações quinzenais

🚀 Bons trades!
```

**Resposta do Bot (Erro):**
```
❌ CÓDIGO INVÁLIDO

O código informado não é válido ou já foi utilizado.

Verifique se:
• Digitou o código corretamente
• O código não foi usado antes
• O código não expirou

💡 Precisa de ajuda?
Entre em contato com nosso suporte:
Email: contato@magnuswealth.com
Telegram: @MagnusSupport
```

#### 3. Ver Status da Conta

```
/status
```

**Resposta do Bot:**
```
📊 STATUS DA SUA CONTA

👤 Nome: João Silva
📧 Email: joao@email.com
💎 Plano: PREMIUM
📅 Cadastro: 31/10/2025
🔑 Código Usado: MAGNUS-A1B2C3D4
📊 Status: ✅ Ativo
💬 No Grupo: ✅ Sim

📚 Comandos:
/ajuda - Ver ajuda e comandos
```

#### 4. Ver Ajuda

```
/ajuda
```

---

## 🗄️ BANCO DE DADOS

### Estrutura do Arquivo `usuarios_magnus.json`

```json
{
  "usuarios": [
    {
      "telegram_user_id": 123456789,
      "telegram_username": "joaosilva",
      "nome": "João Silva",
      "email": "joao@email.com",
      "plano": "premium",
      "codigo_usado": "MAGNUS-A1B2C3D4",
      "data_cadastro": "2025-10-31T20:00:00",
      "ativo": true,
      "grupo_adicionado": true,
      "data_adicao_grupo": "2025-10-31T20:05:00"
    }
  ],
  "codigos_pendentes": {
    "MAGNUS-E5F6G7H8": {
      "nome": "Maria Santos",
      "email": "maria@email.com",
      "plano": "basico",
      "data_geracao": "2025-10-31T19:00:00",
      "usado": false
    },
    "MAGNUS-A1B2C3D4": {
      "nome": "João Silva",
      "email": "joao@email.com",
      "plano": "premium",
      "data_geracao": "2025-10-31T18:00:00",
      "usado": true,
      "telegram_user_id": 123456789,
      "data_uso": "2025-10-31T20:00:00"
    }
  }
}
```

### Backup do Banco de Dados

```bash
# Backup manual
cp usuarios_magnus.json usuarios_magnus_backup_$(date +%Y%m%d).json

# Backup automático (crontab)
0 3 * * * cp /path/to/usuarios_magnus.json /path/to/backups/usuarios_magnus_$(date +\%Y\%m\%d).json
```

---

## 🔔 NOTIFICAÇÕES

### Admin Recebe Notificação de Novo Cadastro

```
🎉 NOVO USUÁRIO CADASTRADO

👤 Nome: João Silva
📧 Email: joao@email.com
💎 Plano: PREMIUM
🆔 Telegram ID: 123456789
👤 Username: @joaosilva
📅 Data: 31/10/2025 20:00

✅ Usuário adicionado ao grupo com sucesso!
```

### Admin Recebe Notificação de Erro

```
⚠️ ERRO AO ADICIONAR USUÁRIO

👤 Nome: Maria Santos
🆔 Telegram ID: 987654321
👤 Username: @mariasantos

❌ Erro: User privacy settings prevent adding to group

⚠️ Ação necessária: Adicionar usuário manualmente ao grupo
```

---

## 🛠️ MANUTENÇÃO

### Verificar Bot Rodando

```bash
# Ver processo
ps aux | grep bot_acesso_grupo

# Ver logs em tempo real
tail -f logs/bot_acesso.log
```

### Reiniciar Bot

```bash
# Parar bot
pkill -f bot_acesso_grupo.py

# Iniciar bot
nohup python3 bot_acesso_grupo.py > logs/bot_acesso.log 2>&1 &
```

### Desativar Usuário

```python
from database_usuarios import DatabaseUsuarios

db = DatabaseUsuarios()
db.desativar_usuario(123456789)  # Telegram User ID
```

---

## 📊 PLANOS DISPONÍVEIS

### Básico
- Acesso ao grupo de sinais
- Análises diárias
- Alertas de mudança de tendência

### Premium
- Tudo do Básico +
- Otimizações quinzenais
- Análises multi-timeframe
- Suporte prioritário

### VIP
- Tudo do Premium +
- Sinais em tempo real
- Acesso ao sistema de execução automática
- Consultoria personalizada

---

## 🔒 SEGURANÇA

### Códigos de Acesso

- **Formato:** `MAGNUS-XXXXXXXX` (8 caracteres hexadecimais)
- **Únicos:** Cada código é único e não pode ser reutilizado
- **Rastreáveis:** Sistema registra quem usou cada código
- **Expiração:** Códigos não expiram (mas podem ser desativados manualmente)

### Privacidade

- Dados armazenados localmente
- Não compartilhados com terceiros
- Backup criptografado recomendado

### Validações

- ✅ Código existe e não foi usado
- ✅ User ID não está cadastrado
- ✅ Usuário tem permissões de privacidade adequadas

---

## 🆘 TROUBLESHOOTING

### Problema: Bot não responde

**Verificar:**
1. Bot está rodando?
   ```bash
   ps aux | grep bot_acesso_grupo
   ```

2. Credenciais corretas no .env?
   ```bash
   cat .env | grep TELEGRAM
   ```

**Solução:**
```bash
# Reiniciar bot
pkill -f bot_acesso_grupo.py
nohup python3 bot_acesso_grupo.py > logs/bot_acesso.log 2>&1 &
```

### Problema: Erro ao adicionar usuário ao grupo

**Possíveis causas:**
- Usuário tem privacidade restrita
- Bot não tem permissão de adicionar membros
- Grupo está cheio (limite do Telegram)

**Solução:**
- Adicionar usuário manualmente
- Enviar link de convite
- Pedir que usuário ajuste privacidade

### Problema: Código não valida

**Verificar:**
1. Código foi gerado?
   ```bash
   python3 database_usuarios.py pendentes
   ```

2. Código já foi usado?
   ```bash
   python3 database_usuarios.py listar
   ```

3. Usuário já está cadastrado?

---

## 📈 ESCALABILIDADE

### Capacidade

- **Usuários simultâneos:** Ilimitado (limitado pelo Telegram)
- **Códigos gerados:** Ilimitado
- **Performance:** < 1s por operação
- **Banco de dados:** JSON (pode migrar para SQL se necessário)

### Migração para SQL (Futuro)

Se necessário escalar para milhares de usuários:

```python
# Usar SQLite ou PostgreSQL
import sqlite3

# Criar tabelas
CREATE TABLE usuarios (
    telegram_user_id INTEGER PRIMARY KEY,
    nome TEXT,
    email TEXT,
    plano TEXT,
    codigo_usado TEXT,
    data_cadastro TIMESTAMP,
    ativo BOOLEAN
);

CREATE TABLE codigos (
    codigo TEXT PRIMARY KEY,
    nome TEXT,
    email TEXT,
    plano TEXT,
    data_geracao TIMESTAMP,
    usado BOOLEAN,
    telegram_user_id INTEGER
);
```

---

## 📚 REFERÊNCIAS

### Arquivos do Sistema

- `database_usuarios.py` - Gerenciamento do banco de dados
- `bot_acesso_grupo.py` - Bot de acesso ao grupo
- `usuarios_magnus.json` - Banco de dados (não commitar!)
- `notificador_usuario.py` - Sistema de notificações

### Documentação Externa

- [Telethon Docs](https://docs.telethon.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python dotenv](https://pypi.org/project/python-dotenv/)

---

## ✅ CHECKLIST DE IMPLANTAÇÃO

- [ ] Dependências instaladas
- [ ] Variáveis de ambiente configuradas (.env)
- [ ] Bot criado no @BotFather
- [ ] API ID e Hash obtidos (my.telegram.org)
- [ ] Bot adicionado ao grupo como admin
- [ ] Permissões do bot configuradas (adicionar membros)
- [ ] Bot iniciado em background
- [ ] Primeiro código gerado e testado
- [ ] Notificações de admin funcionando
- [ ] Backup do banco de dados configurado
- [ ] Logs monitorados

---

**Magnus Wealth v9.0.0** - Sistema de Acesso Robusto e Escalável 🔐

**Data:** 31/10/2025  
**Status:** ✅ Pronto para Produção
