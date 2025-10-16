#!/bin/bash
# Script para verificar status do Magnus Wealth API
# Uso: ./status_server.sh

echo "=========================================="
echo "Magnus Wealth API - Status"
echo "=========================================="
echo ""

# Verificar se o arquivo PID existe
if [ -f "magnus.pid" ]; then
    PID=$(cat magnus.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Servidor RODANDO"
        echo "   PID: $PID"
        echo ""
        echo "📊 Informações do processo:"
        ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
        echo ""
        
        # Verificar se está respondendo
        echo "🔍 Testando conectividade..."
        if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
            echo "✅ API respondendo normalmente"
            echo ""
            echo "📡 Health Check:"
            curl -s http://localhost:5000/api/health | python3 -m json.tool 2>/dev/null || echo "   Resposta recebida"
        else
            echo "⚠️  API não está respondendo"
        fi
        
        echo ""
        echo "📁 Últimas linhas do log:"
        if [ -f "logs/magnus.log" ]; then
            tail -n 5 logs/magnus.log
        else
            echo "   Arquivo de log não encontrado"
        fi
    else
        echo "❌ Servidor NÃO ESTÁ RODANDO"
        echo "   (arquivo PID existe mas processo não)"
        rm magnus.pid
    fi
else
    echo "❌ Servidor NÃO ESTÁ RODANDO"
    echo "   (arquivo PID não encontrado)"
    
    # Verificar se há processos gunicorn rodando
    PIDS=$(pgrep -f "gunicorn.*wsgi:app")
    if [ -n "$PIDS" ]; then
        echo ""
        echo "⚠️  Encontrados processos gunicorn sem arquivo PID:"
        ps -p $PIDS -o pid,cmd
    fi
fi

echo ""
echo "📊 Comandos úteis:"
echo "   Iniciar servidor:     ./start_background.sh"
echo "   Parar servidor:       ./stop_server.sh"
echo "   Ver logs:             tail -f logs/magnus.log"
echo "   Reiniciar servidor:   ./stop_server.sh && ./start_background.sh"
echo ""

