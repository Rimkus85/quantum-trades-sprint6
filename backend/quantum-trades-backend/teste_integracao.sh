#!/bin/bash
echo "================================================================================"
echo "TESTES DE INTEGRAÇÃO - MAGNUS WEALTH v9.0.0"
echo "================================================================================"
echo ""

ERROS=0

# Teste 1: Portfolio Manager
echo "📦 TESTE 1: Portfolio Manager"
python3 -c "from portfolio_manager import PortfolioManager; m = PortfolioManager(); print(f'✅ {len(m.obter_criptos_ativas())} criptos ativas')" || ((ERROS++))
echo ""

# Teste 2: Coletor
echo "📊 TESTE 2: Coletor de Dados"
python3 -c "from coletor_dados_ml_8anos import CRIPTOS; print(f'✅ Coletor carregou {len(CRIPTOS)} criptos')" || ((ERROS++))
echo ""

# Teste 3: Treinador
echo "🤖 TESTE 3: Treinador ML"
python3 -c "from treinar_modelo_inversao import CRIPTOS; print(f'✅ Treinador carregou {len(CRIPTOS)} criptos')" || ((ERROS++))
echo ""

# Teste 4: Monitor
echo "📡 TESTE 4: Monitor Multi-Timeframe"
python3 -c "from monitor_multitimeframe import CRIPTOS; print(f'✅ Monitor carregou {len(CRIPTOS)} criptos')" || ((ERROS++))
echo ""

# Teste 5: Analisador
echo "📈 TESTE 5: Analisador Diário v9"
python3 -c "from analisador_cripto_hilo_bot_v9 import TOP_8; print(f'✅ Analisador carregou {len(TOP_8)} criptos')" || ((ERROS++))
echo ""

# Teste 6: Inicializador
echo "🔧 TESTE 6: Inicializador do Sistema"
python3 inicializar_sistema.py > /dev/null 2>&1 && echo "✅ Sistema inicializado com sucesso" || ((ERROS++))
echo ""

# Teste 7: Arquivos de configuração
echo "⚙️  TESTE 7: Arquivos de Configuração"
test -f portfolio_config.json && echo "✅ portfolio_config.json existe" || ((ERROS++))
test -f config_ordens.json && echo "✅ config_ordens.json existe" || ((ERROS++))
test -f .env && echo "✅ .env existe" || ((ERROS++))
echo ""

# Teste 8: Diretórios
echo "📁 TESTE 8: Estrutura de Diretórios"
test -d ml_data_8anos && echo "✅ ml_data_8anos/ existe" || ((ERROS++))
test -d ml_models && echo "✅ ml_models/ existe" || ((ERROS++))
test -d logs && echo "✅ logs/ existe" || ((ERROS++))
echo ""

# Resultado final
echo "================================================================================"
if [ $ERROS -eq 0 ]; then
    echo "✅ TODOS OS TESTES PASSARAM!"
    echo "================================================================================"
    exit 0
else
    echo "❌ $ERROS TESTE(S) FALHARAM"
    echo "================================================================================"
    exit 1
fi
