#!/bin/bash
# Backup da sessão do Telegram e arquivo .env
# Execute este script para fazer backup dos arquivos sensíveis

BACKUP_DIR="/home/ubuntu/backups/telegram_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Criando backup em: $BACKUP_DIR"

# Copiar arquivos
cp magnus_session.session "$BACKUP_DIR/" 2>/dev/null && echo "✓ magnus_session.session"
cp .env "$BACKUP_DIR/" 2>/dev/null && echo "✓ .env"

echo ""
echo "Backup concluído!"
echo "Localização: $BACKUP_DIR"
