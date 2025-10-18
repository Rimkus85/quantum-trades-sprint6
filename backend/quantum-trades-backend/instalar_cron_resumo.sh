#!/bin/bash
#
# Instalar Cron do Resumo Semanal - Magnus Wealth
# Configura envio automático todo sábado às 10:00
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_FILE="$SCRIPT_DIR/cron_resumo_semanal.txt"

echo "============================================================"
echo "Magnus Wealth - Instalação do Cron Resumo Semanal"
echo "============================================================"
echo ""

# Verificar se crontab está disponível
if ! command -v crontab &> /dev/null; then
    echo "⚠️ Crontab não está disponível neste ambiente"
    echo ""
    echo "📋 INSTRUÇÕES PARA INSTALAÇÃO MANUAL:"
    echo ""
    echo "1. Em um servidor com cron instalado, execute:"
    echo "   crontab -e"
    echo ""
    echo "2. Adicione a seguinte linha:"
    echo "   0 10 * * 6 cd $SCRIPT_DIR && python3 resumo_semanal.py >> logs/resumo_semanal.log 2>&1"
    echo ""
    echo "3. Salve e feche o editor"
    echo ""
    echo "Isso configurará o resumo para ser enviado todo sábado às 10:00"
    echo ""
    echo "============================================================"
    exit 1
fi

# Verificar se arquivo de cron existe
if [ ! -f "$CRON_FILE" ]; then
    echo "❌ Erro: Arquivo de cron não encontrado: $CRON_FILE"
    exit 1
fi

echo "📅 Configuração: Todo sábado às 10:00"
echo "📁 Logs: $SCRIPT_DIR/logs/resumo_semanal.log"
echo ""

# Verificar se já existe agendamento
if crontab -l 2>/dev/null | grep -q "resumo_semanal.py"; then
    echo "⚠️ Já existe um agendamento de resumo semanal."
    read -p "Deseja substituir? [s/N]: " replace
    if [[ ! $replace =~ ^[Ss]$ ]]; then
        echo "❌ Cancelado"
        exit 0
    fi
    # Remover linha antiga
    crontab -l 2>/dev/null | grep -v "resumo_semanal.py" | crontab -
    echo "✅ Agendamento anterior removido"
fi

# Instalar novo cron
echo ""
echo "📥 Instalando agendamento..."
(crontab -l 2>/dev/null; cat "$CRON_FILE" | grep -v "^#" | grep -v "^$") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron instalado com sucesso!"
    echo ""
    echo "📋 Agendamento ativo:"
    crontab -l | grep resumo_semanal
    echo ""
    echo "🎯 Próximo envio: Sábado às 10:00"
    echo ""
    echo "Para ver todos os agendamentos:"
    echo "   crontab -l"
    echo ""
    echo "Para editar agendamentos:"
    echo "   crontab -e"
    echo ""
    echo "Para ver logs:"
    echo "   tail -f $SCRIPT_DIR/logs/resumo_semanal.log"
else
    echo "❌ Erro ao instalar cron"
    exit 1
fi

echo "============================================================"
echo "✅ Instalação concluída!"
echo "============================================================"

