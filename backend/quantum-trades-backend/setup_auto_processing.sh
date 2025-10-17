#!/bin/bash
#
# Setup Auto Processing - Magnus Wealth
# Configura processamento automático de novos vídeos
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_process_new_videos.py"
LOG_DIR="$SCRIPT_DIR/logs"

# Criar diretório de logs
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "Magnus Wealth - Setup de Processamento Automático"
echo "============================================================"
echo ""

# Verificar se o script existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Erro: Script não encontrado: $PYTHON_SCRIPT"
    exit 1
fi

echo "Escolha o método de agendamento:"
echo ""
echo "1) Cron (executar periodicamente)"
echo "2) Systemd Timer (executar periodicamente como serviço)"
echo "3) Executar agora (teste manual)"
echo "4) Cancelar"
echo ""
read -p "Opção [1-4]: " option

case $option in
    1)
        echo ""
        echo "📅 Configurando Cron..."
        echo ""
        echo "Com que frequência deseja processar novos vídeos?"
        echo ""
        echo "1) A cada hora"
        echo "2) A cada 6 horas"
        echo "3) Uma vez por dia (às 02:00)"
        echo "4) Uma vez por semana (domingo às 02:00)"
        echo ""
        read -p "Opção [1-4]: " freq_option
        
        case $freq_option in
            1)
                CRON_SCHEDULE="0 * * * *"
                DESCRIPTION="a cada hora"
                ;;
            2)
                CRON_SCHEDULE="0 */6 * * *"
                DESCRIPTION="a cada 6 horas"
                ;;
            3)
                CRON_SCHEDULE="0 2 * * *"
                DESCRIPTION="diariamente às 02:00"
                ;;
            4)
                CRON_SCHEDULE="0 2 * * 0"
                DESCRIPTION="semanalmente (domingo às 02:00)"
                ;;
            *)
                echo "❌ Opção inválida"
                exit 1
                ;;
        esac
        
        # Adicionar ao crontab
        CRON_COMMAND="$CRON_SCHEDULE cd $SCRIPT_DIR && python3 $PYTHON_SCRIPT >> $LOG_DIR/auto_process.log 2>&1"
        
        # Verificar se já existe
        if crontab -l 2>/dev/null | grep -q "auto_process_new_videos.py"; then
            echo ""
            echo "⚠️ Já existe um agendamento configurado."
            read -p "Deseja substituir? [s/N]: " replace
            if [[ ! $replace =~ ^[Ss]$ ]]; then
                echo "❌ Cancelado"
                exit 0
            fi
            # Remover linha antiga
            crontab -l 2>/dev/null | grep -v "auto_process_new_videos.py" | crontab -
        fi
        
        # Adicionar nova linha
        (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
        
        echo ""
        echo "✅ Cron configurado com sucesso!"
        echo "   Frequência: $DESCRIPTION"
        echo "   Logs: $LOG_DIR/auto_process.log"
        echo ""
        echo "Para ver o agendamento:"
        echo "   crontab -l"
        echo ""
        echo "Para ver os logs:"
        echo "   tail -f $LOG_DIR/auto_process.log"
        ;;
        
    2)
        echo ""
        echo "⚙️ Configurando Systemd Timer..."
        echo ""
        
        # Criar service
        SERVICE_FILE="/etc/systemd/system/magnus-auto-process.service"
        TIMER_FILE="/etc/systemd/system/magnus-auto-process.timer"
        
        echo "Com que frequência deseja processar novos vídeos?"
        echo ""
        echo "1) A cada hora"
        echo "2) A cada 6 horas"
        echo "3) Uma vez por dia"
        echo "4) Uma vez por semana"
        echo ""
        read -p "Opção [1-4]: " freq_option
        
        case $freq_option in
            1)
                TIMER_SCHEDULE="hourly"
                DESCRIPTION="a cada hora"
                ;;
            2)
                TIMER_SCHEDULE="*-*-* 00/6:00:00"
                DESCRIPTION="a cada 6 horas"
                ;;
            3)
                TIMER_SCHEDULE="daily"
                DESCRIPTION="diariamente"
                ;;
            4)
                TIMER_SCHEDULE="weekly"
                DESCRIPTION="semanalmente"
                ;;
            *)
                echo "❌ Opção inválida"
                exit 1
                ;;
        esac
        
        # Criar arquivo de serviço
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Magnus Auto Process New Videos
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $PYTHON_SCRIPT
StandardOutput=append:$LOG_DIR/auto_process.log
StandardError=append:$LOG_DIR/auto_process.log

[Install]
WantedBy=multi-user.target
EOF

        # Criar arquivo de timer
        sudo tee "$TIMER_FILE" > /dev/null <<EOF
[Unit]
Description=Magnus Auto Process Timer
Requires=magnus-auto-process.service

[Timer]
OnCalendar=$TIMER_SCHEDULE
Persistent=true

[Install]
WantedBy=timers.target
EOF

        # Recarregar systemd e habilitar
        sudo systemctl daemon-reload
        sudo systemctl enable magnus-auto-process.timer
        sudo systemctl start magnus-auto-process.timer
        
        echo ""
        echo "✅ Systemd Timer configurado com sucesso!"
        echo "   Frequência: $DESCRIPTION"
        echo "   Logs: $LOG_DIR/auto_process.log"
        echo ""
        echo "Para ver o status:"
        echo "   sudo systemctl status magnus-auto-process.timer"
        echo ""
        echo "Para executar manualmente:"
        echo "   sudo systemctl start magnus-auto-process.service"
        echo ""
        echo "Para ver os logs:"
        echo "   tail -f $LOG_DIR/auto_process.log"
        ;;
        
    3)
        echo ""
        echo "🚀 Executando processamento agora..."
        echo ""
        python3 "$PYTHON_SCRIPT"
        ;;
        
    4)
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

echo ""
echo "============================================================"
echo "✅ Setup concluído!"
echo "============================================================"

