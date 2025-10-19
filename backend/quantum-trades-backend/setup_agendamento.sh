#!/bin/bash

# ============================================================================
# MAGNUS WEALTH - INSTALAÇÃO DO SISTEMA DE AGENDAMENTO
# ============================================================================
# 
# Este script configura todos os agendamentos automáticos do Magnus Wealth
# 
# Uso:
#   chmod +x setup_agendamento.sh
#   ./setup_agendamento.sh
# 
# ============================================================================

set -e  # Parar em caso de erro

echo "============================================================================"
echo "🤖 MAGNUS WEALTH - INSTALAÇÃO DO SISTEMA DE AGENDAMENTO"
echo "============================================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório base
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}📂 Diretório do projeto:${NC} $SCRIPT_DIR"
echo ""

# ============================================================================
# 1. VERIFICAR DEPENDÊNCIAS
# ============================================================================

echo -e "${YELLOW}🔍 Verificando dependências...${NC}"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não encontrado!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3:${NC} $(python3 --version)"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 não encontrado!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3:${NC} instalado"

# Verificar cron
if ! command -v crontab &> /dev/null; then
    echo -e "${RED}❌ cron não encontrado!${NC}"
    echo "Instalando cron..."
    sudo apt-get update
    sudo apt-get install -y cron
fi
echo -e "${GREEN}✅ cron:${NC} instalado"

echo ""

# ============================================================================
# 2. CRIAR DIRETÓRIOS NECESSÁRIOS
# ============================================================================

echo -e "${YELLOW}📁 Criando diretórios...${NC}"
echo ""

mkdir -p logs
mkdir -p backups
mkdir -p youtube_knowledge

echo -e "${GREEN}✅ Diretórios criados:${NC}"
echo "   • logs/"
echo "   • backups/"
echo "   • youtube_knowledge/"
echo ""

# ============================================================================
# 3. TORNAR SCRIPTS EXECUTÁVEIS
# ============================================================================

echo -e "${YELLOW}🔧 Tornando scripts executáveis...${NC}"
echo ""

chmod +x analise_diaria.py
chmod +x analise_opcoes.py
chmod +x resumo_semanal.py
chmod +x bot_comandos.py

echo -e "${GREEN}✅ Scripts configurados:${NC}"
echo "   • analise_diaria.py"
echo "   • analise_opcoes.py"
echo "   • resumo_semanal.py"
echo "   • bot_comandos.py"
echo ""

# ============================================================================
# 4. INSTALAR DEPENDÊNCIAS PYTHON
# ============================================================================

echo -e "${YELLOW}📦 Verificando dependências Python...${NC}"
echo ""

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt não encontrado${NC}"
fi
echo ""

# ============================================================================
# 5. CONFIGURAR CRONTAB
# ============================================================================

echo -e "${YELLOW}⏰ Configurando agendamentos (crontab)...${NC}"
echo ""

# Backup do crontab atual
echo "📋 Fazendo backup do crontab atual..."
crontab -l > crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || echo "# Sem crontab anterior" > crontab_backup_$(date +%Y%m%d_%H%M%S).txt

# Atualizar caminhos no arquivo de crontab
sed -i "s|MAGNUS_DIR=.*|MAGNUS_DIR=$SCRIPT_DIR|g" crontab_magnus.txt
sed -i "s|LOGS_DIR=.*|LOGS_DIR=$SCRIPT_DIR/logs|g" crontab_magnus.txt

# Instalar novo crontab
crontab crontab_magnus.txt

echo -e "${GREEN}✅ Crontab instalado com sucesso!${NC}"
echo ""

# Mostrar agendamentos instalados
echo -e "${BLUE}📅 Agendamentos ativos:${NC}"
echo ""
crontab -l | grep -v "^#" | grep -v "^$" || echo "Nenhum agendamento ativo"
echo ""

# ============================================================================
# 6. RESUMO DOS AGENDAMENTOS
# ============================================================================

echo "============================================================================"
echo -e "${GREEN}✅ INSTALAÇÃO CONCLUÍDA!${NC}"
echo "============================================================================"
echo ""
echo -e "${BLUE}📅 AGENDAMENTOS CONFIGURADOS:${NC}"
echo ""
echo "  📊 Análise Diária:"
echo "     • Horário: 21:00 (todos os dias)"
echo "     • Script: analise_diaria.py"
echo ""
echo "  📈 Análise de Opções:"
echo "     • Horários: 10:10, 14:00, 16:45 (dias úteis)"
echo "     • Script: analise_opcoes.py"
echo ""
echo "  📋 Resumo Semanal:"
echo "     • Horário: Sábado às 10:00"
echo "     • Script: resumo_semanal.py"
echo ""
echo "  🧹 Limpeza de Logs:"
echo "     • Horário: Domingo às 02:00"
echo "     • Ação: Remove logs com +30 dias"
echo ""
echo "  💾 Backup de Dados:"
echo "     • Horário: Domingo às 03:00"
echo "     • Ação: Backup da base de conhecimento"
echo ""
echo "============================================================================"
echo ""
echo -e "${YELLOW}📝 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "  1. Verificar agendamentos:"
echo "     ${BLUE}crontab -l${NC}"
echo ""
echo "  2. Iniciar bot de comandos (em background):"
echo "     ${BLUE}nohup python3 bot_comandos.py > logs/bot_comandos.log 2>&1 &${NC}"
echo ""
echo "  3. Verificar logs:"
echo "     ${BLUE}tail -f logs/*.log${NC}"
echo ""
echo "  4. Testar análise manualmente:"
echo "     ${BLUE}python3 analise_diaria.py${NC}"
echo ""
echo "============================================================================"
echo ""
echo -e "${GREEN}🚀 Sistema de agendamento pronto para operar!${NC}"
echo ""

