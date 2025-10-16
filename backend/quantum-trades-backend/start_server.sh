#!/bin/bash
# Script de inicialização do Magnus Wealth API
# Uso: ./start_server.sh [production|development]

MODE=${1:-development}

echo "=========================================="
echo "Magnus Wealth API - Inicialização"
echo "=========================================="
echo "Modo: $MODE"
echo ""

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: Execute este script no diretório backend/quantum-trades-backend"
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado"
    echo "Copiando .env.example para .env..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado. Por favor, configure suas credenciais."
        exit 1
    else
        echo "❌ Erro: .env.example não encontrado"
        exit 1
    fi
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3.11 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependências instaladas"

# Configurar variáveis de ambiente baseado no modo
if [ "$MODE" == "production" ]; then
    export FLASK_ENV=production
    export FLASK_DEBUG=False
    export PORT=5000
    
    echo ""
    echo "🚀 Iniciando servidor em modo PRODUÇÃO..."
    echo "   Host: 0.0.0.0"
    echo "   Port: $PORT"
    echo "   Workers: 2"
    echo ""
    
    # Iniciar com gunicorn
    gunicorn --bind 0.0.0.0:$PORT \
             --workers 2 \
             --timeout 120 \
             --access-logfile - \
             --error-logfile - \
             wsgi:app
else
    export FLASK_ENV=development
    export FLASK_DEBUG=True
    export PORT=5000
    
    echo ""
    echo "🔧 Iniciando servidor em modo DESENVOLVIMENTO..."
    echo "   Host: 0.0.0.0"
    echo "   Port: $PORT"
    echo "   Debug: ON"
    echo ""
    
    # Iniciar com Flask development server
    python app.py
fi

