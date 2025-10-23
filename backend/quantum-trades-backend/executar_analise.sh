#!/bin/bash
#
# Script Wrapper para Execução do Analisador de Criptomoedas
# Magnus Wealth v8.3.0
#
# Este script garante que:
# 1. O diretório de trabalho está correto
# 2. As variáveis de ambiente são carregadas
# 3. O arquivo de sessão do Telegram é encontrado
# 4. Logs são gerados corretamente
#

# Definir diretório do script
SCRIPT_DIR="/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend"
cd "$SCRIPT_DIR" || exit 1

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "ERRO: Arquivo .env não encontrado em $SCRIPT_DIR"
    exit 1
fi

# Verificar se o arquivo de sessão existe
if [ ! -f "magnus_session.session" ]; then
    echo "ERRO: Arquivo de sessão magnus_session.session não encontrado"
    echo "Execute: python3 setup_telegram.py para criar a sessão"
    exit 1
fi

# Criar diretório de logs se não existir
LOG_DIR="/home/ubuntu/logs"
mkdir -p "$LOG_DIR"

# Definir arquivo de log com data
LOG_FILE="$LOG_DIR/cripto_analise_$(date +%Y%m%d).log"

# Registrar início da execução
echo "========================================" >> "$LOG_FILE"
echo "Início: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "Diretório: $SCRIPT_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Executar o analisador
python3 "$SCRIPT_DIR/analisador_cripto_hilo.py" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Registrar fim da execução
echo "========================================" >> "$LOG_FILE"
echo "Fim: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "Código de saída: $EXIT_CODE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Retornar código de saída
exit $EXIT_CODE

