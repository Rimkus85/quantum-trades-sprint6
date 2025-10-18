#!/bin/bash
#
# Setup Resumo Semanal - Magnus Wealth
# Configura envio automático de resumo semanal no Telegram
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/resumo_semanal.py"

echo "============================================================"
echo "Magnus Wealth - Setup de Resumo Semanal"
echo "============================================================"
echo ""

# Verificar se o script existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Erro: Script não encontrado: $PYTHON_SCRIPT"
    exit 1
fi

echo "Escolha quando deseja receber o resumo semanal:"
echo ""
echo "1) Toda segunda-feira às 09:00"
echo "2) Todo domingo às 20:00"
echo "3) Toda sexta-feira às 18:00"
echo "4) Personalizado"
echo "5) Executar agora (teste)"
echo "6) Cancelar"
echo ""
read -p "Opção [1-6]: " option

case $option in
    1)
        CRON_SCHEDULE="0 9 * * 1"
        DESCRIPTION="segunda-feira às 09:00"
        ;;
    2)
        CRON_SCHEDULE="0 20 * * 0"
        DESCRIPTION="domingo às 20:00"
        ;;
    3)
        CRON_SCHEDULE="0 18 * * 5"
        DESCRIPTION="sexta-feira às 18:00"
        ;;
    4)
        echo ""
        echo "Dia da semana (0=Domingo, 1=Segunda, ..., 6=Sábado):"
        read -p "Dia [0-6]: " dia
        echo "Hora (0-23):"
        read -p "Hora: " hora
        CRON_SCHEDULE="0 $hora * * $dia"
        DESCRIPTION="personalizado"
        ;;
    5)
        echo ""
        echo "🚀 Executando resumo semanal agora..."
        echo ""
        python3 "$PYTHON_SCRIPT"
        exit 0
        ;;
    6)
        echo ""
        echo "❌ Cancelado"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

# Adicionar ao crontab
CRON_COMMAND="$CRON_SCHEDULE cd $SCRIPT_DIR && python3 $PYTHON_SCRIPT >> $SCRIPT_DIR/logs/resumo_semanal.log 2>&1"

# Verificar se já existe
if crontab -l 2>/dev/null | grep -q "resumo_semanal.py"; then
    echo ""
    echo "⚠️ Já existe um agendamento de resumo semanal."
    read -p "Deseja substituir? [s/N]: " replace
    if [[ ! $replace =~ ^[Ss]$ ]]; then
        echo "❌ Cancelado"
        exit 0
    fi
    # Remover linha antiga
    crontab -l 2>/dev/null | grep -v "resumo_semanal.py" | crontab -
fi

# Adicionar nova linha
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

echo ""
echo "✅ Resumo semanal configurado com sucesso!"
echo "   Frequência: $DESCRIPTION"
echo "   Logs: $SCRIPT_DIR/logs/resumo_semanal.log"
echo ""
echo "Para ver o agendamento:"
echo "   crontab -l"
echo ""
echo "Para executar manualmente:"
echo "   python3 $PYTHON_SCRIPT"
echo ""
echo "Para ver os logs:"
echo "   tail -f $SCRIPT_DIR/logs/resumo_semanal.log"
echo ""
echo "============================================================"
echo "✅ Setup concluído!"
echo "============================================================"

