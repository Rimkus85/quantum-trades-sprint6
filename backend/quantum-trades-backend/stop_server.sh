#!/bin/bash
# Script para parar o Magnus Wealth API
# Uso: ./stop_server.sh

echo "=========================================="
echo "Magnus Wealth API - Parar Servidor"
echo "=========================================="
echo ""

# Verificar se o arquivo PID existe
if [ ! -f "magnus.pid" ]; then
    echo "⚠️  Arquivo magnus.pid não encontrado"
    echo "   O servidor pode não estar rodando"
    
    # Tentar encontrar processo pelo nome
    PIDS=$(pgrep -f "gunicorn.*wsgi:app")
    if [ -n "$PIDS" ]; then
        echo "   Encontrados processos gunicorn rodando:"
        ps -p $PIDS -o pid,cmd
        echo ""
        read -p "   Deseja parar estes processos? (s/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            kill $PIDS
            echo "✅ Processos parados"
        fi
    fi
    exit 0
fi

# Ler PID do arquivo
PID=$(cat magnus.pid)

# Verificar se o processo está rodando
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Processo $PID não está rodando"
    rm magnus.pid
    exit 0
fi

# Parar o processo
echo "🛑 Parando servidor (PID: $PID)..."
kill $PID

# Aguardar até 10 segundos para o processo parar
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ Servidor parado com sucesso"
        rm magnus.pid
        exit 0
    fi
    sleep 1
done

# Se ainda estiver rodando, forçar parada
echo "⚠️  Processo não parou, forçando..."
kill -9 $PID 2>/dev/null
rm magnus.pid
echo "✅ Servidor parado (forçado)"

