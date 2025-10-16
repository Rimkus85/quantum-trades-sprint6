#!/bin/bash
# Script para instalar Magnus Wealth como serviço systemd
# Requer privilégios sudo
# Uso: sudo ./install_systemd.sh

echo "=========================================="
echo "Magnus Wealth API - Instalação Systemd"
echo "=========================================="
echo ""

# Verificar se está rodando como root/sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Este script precisa ser executado com sudo"
    echo "   Uso: sudo ./install_systemd.sh"
    exit 1
fi

# Verificar se está no diretório correto
if [ ! -f "magnus-wealth.service" ]; then
    echo "❌ Erro: arquivo magnus-wealth.service não encontrado"
    exit 1
fi

# Criar diretório de logs
echo "📁 Criando diretório de logs..."
mkdir -p /var/log/magnus
chown ubuntu:ubuntu /var/log/magnus
echo "✅ Diretório de logs criado: /var/log/magnus"

# Copiar arquivo de serviço
echo ""
echo "📋 Instalando arquivo de serviço..."
cp magnus-wealth.service /etc/systemd/system/
echo "✅ Arquivo copiado para /etc/systemd/system/"

# Recarregar systemd
echo ""
echo "🔄 Recarregando systemd..."
systemctl daemon-reload
echo "✅ Systemd recarregado"

# Habilitar serviço para iniciar no boot
echo ""
echo "⚙️  Habilitando serviço para iniciar automaticamente..."
systemctl enable magnus-wealth.service
echo "✅ Serviço habilitado"

echo ""
echo "=========================================="
echo "✅ Instalação concluída com sucesso!"
echo "=========================================="
echo ""
echo "📊 Comandos disponíveis:"
echo "   Iniciar serviço:    sudo systemctl start magnus-wealth"
echo "   Parar serviço:      sudo systemctl stop magnus-wealth"
echo "   Reiniciar serviço:  sudo systemctl restart magnus-wealth"
echo "   Status do serviço:  sudo systemctl status magnus-wealth"
echo "   Ver logs:           sudo journalctl -u magnus-wealth -f"
echo "   Desabilitar auto-start: sudo systemctl disable magnus-wealth"
echo ""
echo "🚀 Para iniciar o serviço agora, execute:"
echo "   sudo systemctl start magnus-wealth"
echo ""

