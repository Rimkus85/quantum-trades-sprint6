# 🚀 Magnus Wealth - Guia Rápido de Inicialização

## Início Rápido (3 Passos)

### 1️⃣ Configurar Credenciais

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env
```

Preencha com suas credenciais do Telegram:
- `TELEGRAM_API_ID`: Obtenha em https://my.telegram.org
- `TELEGRAM_API_HASH`: Obtenha em https://my.telegram.org
- `TELEGRAM_PHONE`: Seu número de telefone (+5511999999999)
- `TELEGRAM_GROUP_USERNAME`: Nome do grupo do Telegram

### 2️⃣ Iniciar Servidor

**Modo Desenvolvimento (com debug):**
```bash
./start_server.sh development
```

**Modo Produção (otimizado):**
```bash
./start_server.sh production
```

**Em Background (daemon):**
```bash
./start_background.sh
```

### 3️⃣ Verificar Status

```bash
# Ver status do servidor
./status_server.sh

# Testar API
curl http://localhost:5000/api/health
```

## 📊 Gerenciamento do Servidor

### Comandos Básicos

```bash
# Iniciar em background
./start_background.sh

# Ver status
./status_server.sh

# Parar servidor
./stop_server.sh

# Ver logs em tempo real
tail -f logs/magnus.log
```

### Instalar como Serviço (Opcional)

Para executar como serviço do sistema (recomendado para produção):

```bash
# Instalar serviço
sudo ./install_systemd.sh

# Iniciar serviço
sudo systemctl start magnus-wealth

# Ver status
sudo systemctl status magnus-wealth

# Ver logs
sudo journalctl -u magnus-wealth -f
```

## 🔧 Configuração de Automações

### Instalar Cron Jobs

```bash
# Instalar agendamentos automáticos
./install_cron.sh

# Verificar instalação
crontab -l
```

**Agendamentos Configurados:**
- **21:00** - Análise diária de carteiras
- **10:10, 14:00, 16:45** - Análise de opções (dias úteis)
- **Último dia do mês 21:00** - Relatório mensal

## 🌐 Endpoints da API

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Telegram
```bash
# Configuração do Telegram
curl http://localhost:5000/api/telegram/config

# Ler mensagens
curl http://localhost:5000/api/telegram/messages?limit=10

# Ler carteiras
curl http://localhost:5000/api/telegram/carteiras?days=7
```

### Magnus Learning
```bash
# Recomendações
curl http://localhost:5000/api/magnus/recommendations

# Análise de ativo
curl http://localhost:5000/api/magnus/analyze/PETR4

# Estatísticas
curl http://localhost:5000/api/magnus/statistics
```

## 📁 Estrutura de Arquivos

```
backend/quantum-trades-backend/
├── app.py                      # API principal
├── wsgi.py                     # Entry point para produção
├── requirements.txt            # Dependências Python
├── .env                        # Configurações (não commitar!)
├── magnus_session.session      # Sessão do Telegram (não commitar!)
│
├── services/                   # Serviços
│   └── telegram_service.py
│
├── modules/                    # Módulos
│   ├── magnus_learning.py
│   ├── magnus_advanced_learning.py
│   ├── carteira_parser.py
│   └── market_data_api.py
│
├── logs/                       # Logs do servidor
│   ├── magnus.log
│   ├── access.log
│   └── error.log
│
└── Scripts de gerenciamento:
    ├── start_server.sh         # Iniciar servidor
    ├── start_background.sh     # Iniciar em background
    ├── stop_server.sh          # Parar servidor
    ├── status_server.sh        # Ver status
    ├── install_systemd.sh      # Instalar como serviço
    └── install_cron.sh         # Instalar automações
```

## 🔍 Troubleshooting

### Servidor não inicia

```bash
# Verificar se a porta está em uso
sudo lsof -i :5000

# Ver logs de erro
cat logs/error.log
```

### Telegram não conecta

```bash
# Renovar sessão
python renovar_sessao.py

# Verificar credenciais
cat .env | grep TELEGRAM
```

### Cron jobs não executam

```bash
# Verificar se estão instalados
crontab -l

# Ver logs do sistema
grep CRON /var/log/syslog

# Testar execução manual
python analise_diaria.py
```

## 📦 Backup

### Criar Backup

```bash
# Backup completo
tar -czf magnus-backup-$(date +%Y%m%d).tar.gz \
  magnus_session.session \
  .env \
  *.json \
  logs/
```

### Restaurar Backup

```bash
# Extrair backup
tar -xzf magnus-backup-YYYYMMDD.tar.gz
```

## 🔄 Atualização

```bash
# 1. Fazer backup
tar -czf magnus-backup-$(date +%Y%m%d).tar.gz *.session .env *.json

# 2. Parar servidor
./stop_server.sh

# 3. Atualizar código
git pull origin master

# 4. Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. Reiniciar servidor
./start_background.sh
```

## 🆘 Suporte

- **Documentação Completa**: `DEPLOYMENT.md`
- **GitHub Issues**: https://github.com/Rimkus85/quantum-trades-sprint6/issues
- **Logs do Sistema**: `logs/magnus.log`

---

**Magnus Wealth API** v9.2.0  
Sistema de Análise de Investimentos com IA

