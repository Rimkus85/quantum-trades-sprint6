#!/bin/bash
# Script para executar Magnus Wealth API em background
# Uso: ./start_background.sh

echo "=========================================="
echo "Magnus Wealth API - Background Service"
echo "=========================================="
echo ""

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: Execute este script no diretório backend/quantum-trades-backend"
    exit 1
fi

# Verificar se já está rodando
if [ -f "magnus.pid" ]; then
    PID=$(cat magnus.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  O servidor já está rodando (PID: $PID)"
        echo "   Use ./stop_server.sh para parar o servidor primeiro"
        exit 1
    else
        echo "🧹 Removendo arquivo PID antigo..."
        rm magnus.pid
    fi
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Ativar ambiente virtual
if [ ! -d "venv" ]; then
    echo "❌ Erro: Ambiente virtual não encontrado"
    echo "   Execute ./start_server.sh primeiro para criar o ambiente"
    exit 1
fi

source venv/bin/activate

# Configurar variáveis de ambiente
export FLASK_ENV=production
export FLASK_DEBUG=False
export PORT=5000

echo "🚀 Iniciando servidor em background..."
echo "   Host: 0.0.0.0"
echo "   Port: $PORT"
echo "   Logs: logs/magnus.log"
echo ""

# Iniciar servidor em background
nohup gunicorn --bind 0.0.0.0:$PORT \
               --workers 2 \
               --timeout 120 \
               --access-logfile logs/access.log \
               --error-logfile logs/error.log \
               wsgi:app > logs/magnus.log 2>&1 &

# Salvar PID
echo $! > magnus.pid

echo "✅ Servidor iniciado com sucesso!"
echo "   PID: $(cat magnus.pid)"
echo ""
echo "📊 Comandos úteis:"
echo "   Ver logs:        tail -f logs/magnus.log"
echo "   Ver logs de erro: tail -f logs/error.log"
echo "   Parar servidor:  ./stop_server.sh"
echo "   Status:          ./status_server.sh"
echo ""

