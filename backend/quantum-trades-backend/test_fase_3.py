#!/usr/bin/env python3
"""
Magnus Wealth - Teste da Fase 3
Valida todas as funcionalidades implementadas na Fase 3 (Machine Learning e IA)
"""

import os
import sys
import numpy as np
from datetime import datetime

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        print(f"       {details}")

def print_section(name):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}📋 {name}{Colors.END}")
    print(f"{Colors.YELLOW}{'─'*70}{Colors.END}")

# ============================================================================
# TESTES
# ============================================================================

def test_ml_modules():
    """Testa se os módulos de ML foram criados"""
    
    print_section("TESTE 1: Módulos de ML")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(backend_dir, 'ml_models')
    
    total_tests = 0
    passed_tests = 0
    
    # Verificar diretório ml_models
    total_tests += 1
    if os.path.exists(ml_dir):
        print_test("Diretório ml_models/", True)
        passed_tests += 1
    else:
        print_test("Diretório ml_models/", False, "Não encontrado")
    
    # Verificar arquivos
    arquivos = [
        '__init__.py',
        'sentiment_analyzer.py',
        'price_predictor.py',
        'portfolio_optimizer.py'
    ]
    
    for arquivo in arquivos:
        total_tests += 1
        caminho = os.path.join(ml_dir, arquivo)
        
        if os.path.exists(caminho):
            tamanho = os.path.getsize(caminho)
            tamanho_kb = tamanho / 1024
            print_test(f"ml_models/{arquivo}", True, f"Tamanho: {tamanho_kb:.1f} KB")
            passed_tests += 1
        else:
            print_test(f"ml_models/{arquivo}", False, "Não encontrado")
    
    return passed_tests, total_tests

def test_sentiment_analyzer():
    """Testa o analisador de sentimento"""
    
    print_section("TESTE 2: Analisador de Sentimento")
    
    total_tests = 0
    passed_tests = 0
    
    try:
        from ml_models.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        # Teste 1: Texto positivo
        total_tests += 1
        result = analyzer.analyze_text("PETR4 teve lucro recorde, ações sobem forte")
        if result['sentiment'] == 'positive' and result['score'] > 0:
            print_test("Texto positivo", True, f"Score: {result['score']}")
            passed_tests += 1
        else:
            print_test("Texto positivo", False, f"Esperado: positive, Obtido: {result['sentiment']}")
        
        # Teste 2: Texto negativo
        total_tests += 1
        result = analyzer.analyze_text("VALE3 despenca com prejuízo e queda de preços")
        if result['sentiment'] == 'negative' and result['score'] < 0:
            print_test("Texto negativo", True, f"Score: {result['score']}")
            passed_tests += 1
        else:
            print_test("Texto negativo", False, f"Esperado: negative, Obtido: {result['sentiment']}")
        
        # Teste 3: Análise de ticker
        total_tests += 1
        messages = [
            {'text': 'PETR4 teve lucro recorde', 'date': '2025-10-18'},
            {'text': 'PETR4 valoriza forte', 'date': '2025-10-18'},
        ]
        result = analyzer.analyze_ticker_sentiment('PETR4', messages)
        if result['ticker'] == 'PETR4' and result['total_messages'] == 2:
            print_test("Análise de ticker", True, f"Sentimento: {result['sentiment']}")
            passed_tests += 1
        else:
            print_test("Análise de ticker", False)
        
        # Teste 4: Sentimento de mercado
        total_tests += 1
        result = analyzer.get_market_sentiment(messages)
        if 'sentiment' in result and 'emoji' in result:
            print_test("Sentimento de mercado", True, f"{result['emoji']} {result['sentiment']}")
            passed_tests += 1
        else:
            print_test("Sentimento de mercado", False)
        
    except Exception as e:
        print_test("Import SentimentAnalyzer", False, str(e))
        total_tests += 4
    
    return passed_tests, total_tests

def test_price_predictor():
    """Testa o preditor de preços"""
    
    print_section("TESTE 3: Preditor de Preços")
    
    total_tests = 0
    passed_tests = 0
    
    try:
        from ml_models.price_predictor import PricePredictor
        
        predictor = PricePredictor()
        
        # Gerar dados sintéticos
        np.random.seed(42)
        prices = [30 + i * 0.1 + np.random.normal(0, 0.5) for i in range(60)]
        
        # Teste 1: Treinamento
        total_tests += 1
        try:
            result = predictor.train_model('TEST4', prices)
            if result['ticker'] == 'TEST4' and 'train_r2' in result:
                print_test("Treinamento de modelo", True, f"R²: {result['train_r2']:.4f}")
                passed_tests += 1
            else:
                print_test("Treinamento de modelo", False)
        except Exception as e:
            print_test("Treinamento de modelo", False, str(e))
        
        # Teste 2: Previsão
        total_tests += 1
        try:
            result = predictor.predict_next_days('TEST4', prices, days=7)
            if 'predictions' in result and len(result['predictions']) == 7:
                print_test("Previsão de preços", True, f"Tendência: {result['trend']}")
                passed_tests += 1
            else:
                print_test("Previsão de preços", False)
        except Exception as e:
            print_test("Previsão de preços", False, str(e))
        
        # Teste 3: Salvamento/carregamento
        total_tests += 1
        models = predictor.list_trained_models()
        if 'TEST4' in models:
            print_test("Salvamento de modelo", True, f"{len(models)} modelo(s)")
            passed_tests += 1
        else:
            print_test("Salvamento de modelo", False)
        
    except Exception as e:
        print_test("Import PricePredictor", False, str(e))
        total_tests += 3
    
    return passed_tests, total_tests

def test_portfolio_optimizer():
    """Testa o otimizador de portfólio"""
    
    print_section("TESTE 4: Otimizador de Portfólio")
    
    total_tests = 0
    passed_tests = 0
    
    try:
        from ml_models.portfolio_optimizer import PortfolioOptimizer
        
        optimizer = PortfolioOptimizer()
        
        # Gerar dados sintéticos
        np.random.seed(42)
        prices_history = {
            'PETR4': [30 + i * 0.1 + np.random.normal(0, 1) for i in range(60)],
            'VALE3': [50 + i * 0.05 + np.random.normal(0, 0.5) for i in range(60)],
            'ITUB4': [25 + i * 0.02 + np.random.normal(0, 0.2) for i in range(60)]
        }
        
        # Teste 1: Cálculo de retornos
        total_tests += 1
        returns = optimizer.calculate_returns(prices_history)
        if len(returns) == 3 and all(ticker in returns for ticker in prices_history.keys()):
            print_test("Cálculo de retornos", True, f"{len(returns)} ativos")
            passed_tests += 1
        else:
            print_test("Cálculo de retornos", False)
        
        # Teste 2: Cálculo de volatilidade
        total_tests += 1
        volatilities = optimizer.calculate_volatility(prices_history)
        if len(volatilities) == 3:
            print_test("Cálculo de volatilidade", True)
            passed_tests += 1
        else:
            print_test("Cálculo de volatilidade", False)
        
        # Teste 3: Otimização (Sharpe)
        total_tests += 1
        try:
            result = optimizer.optimize_sharpe_ratio(prices_history, risk_tolerance='moderate')
            if 'allocations' in result and 'portfolio_metrics' in result:
                sharpe = result['portfolio_metrics']['sharpe_ratio']
                print_test("Otimização Sharpe Ratio", True, f"Sharpe: {sharpe:.2f}")
                passed_tests += 1
            else:
                print_test("Otimização Sharpe Ratio", False)
        except Exception as e:
            print_test("Otimização Sharpe Ratio", False, str(e))
        
        # Teste 4: Otimização (Mínima Volatilidade)
        total_tests += 1
        try:
            result = optimizer.optimize_min_volatility(prices_history)
            if 'allocations' in result:
                vol = result['portfolio_metrics']['volatility']
                print_test("Otimização Mín. Volatilidade", True, f"Vol: {vol:.2f}%")
                passed_tests += 1
            else:
                print_test("Otimização Mín. Volatilidade", False)
        except Exception as e:
            print_test("Otimização Mín. Volatilidade", False, str(e))
        
    except Exception as e:
        print_test("Import PortfolioOptimizer", False, str(e))
        total_tests += 4
    
    return passed_tests, total_tests

def test_api_endpoints():
    """Testa se os endpoints foram adicionados à API"""
    
    print_section("TESTE 5: Endpoints da API")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(backend_dir, 'app.py')
    
    total_tests = 0
    passed_tests = 0
    
    if not os.path.exists(app_path):
        print_test("app.py", False, "Não encontrado")
        return 0, 6
    
    with open(app_path, 'r') as f:
        conteudo = f.read()
    
    endpoints = {
        '/api/ml/sentiment/analyze': '@app.route(\'/api/ml/sentiment/analyze\'',
        '/api/ml/sentiment/ticker': '@app.route(\'/api/ml/sentiment/ticker',
        '/api/ml/predict/train': '@app.route(\'/api/ml/predict/train\'',
        '/api/ml/predict/price': '@app.route(\'/api/ml/predict/price',
        '/api/ml/portfolio/optimize': '@app.route(\'/api/ml/portfolio/optimize\'',
        '/api/ml/models/status': '@app.route(\'/api/ml/models/status\''
    }
    
    for endpoint, pattern in endpoints.items():
        total_tests += 1
        if pattern in conteudo:
            print_test(endpoint, True, "Implementado")
            passed_tests += 1
        else:
            print_test(endpoint, False, "Não encontrado")
    
    return passed_tests, total_tests

def test_frontend():
    """Testa se o frontend foi criado"""
    
    print_section("TESTE 6: Frontend de IA e ML")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    
    total_tests = 0
    passed_tests = 0
    
    # Verificar página HTML
    total_tests += 1
    html_path = os.path.join(frontend_dir, 'painel_ia_ml.html')
    if os.path.exists(html_path):
        tamanho = os.path.getsize(html_path)
        tamanho_kb = tamanho / 1024
        print_test("painel_ia_ml.html", True, f"Tamanho: {tamanho_kb:.1f} KB")
        passed_tests += 1
    else:
        print_test("painel_ia_ml.html", False, "Não encontrado")
    
    # Verificar serviço JS
    total_tests += 1
    js_path = os.path.join(frontend_dir, 'js', 'ml_service.js')
    if os.path.exists(js_path):
        tamanho = os.path.getsize(js_path)
        tamanho_kb = tamanho / 1024
        print_test("js/ml_service.js", True, f"Tamanho: {tamanho_kb:.1f} KB")
        passed_tests += 1
    else:
        print_test("js/ml_service.js", False, "Não encontrado")
    
    # Verificar responsividade
    if os.path.exists(html_path):
        total_tests += 1
        with open(html_path, 'r') as f:
            conteudo = f.read()
        
        has_viewport = 'viewport' in conteudo and 'width=device-width' in conteudo
        has_media_queries = '@media' in conteudo
        
        if has_viewport and has_media_queries:
            print_test("Responsividade", True, "Viewport + Media Queries")
            passed_tests += 1
        else:
            print_test("Responsividade", False)
    
    return passed_tests, total_tests

def test_compatibilidade():
    """Testa compatibilidade com versões anteriores"""
    
    print_section("TESTE 7: Compatibilidade com v7.2.0")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    
    arquivos_existentes = [
        'dashboard_final.html',
        'painel_telegram.html',
        'graficos_avancados.html',
        'cotacoes_tempo_real.html',
        'js/telegram_service.js',
        'js/charts_service.js',
        'js/websocket_service.js'
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for arquivo in arquivos_existentes:
        total_tests += 1
        caminho = os.path.join(frontend_dir, arquivo)
        
        if os.path.exists(caminho):
            print_test(arquivo, True, "Preservado")
            passed_tests += 1
        else:
            print_test(arquivo, False, "REMOVIDO!")
    
    return passed_tests, total_tests

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa todos os testes"""
    
    print_header("MAGNUS WEALTH - TESTE DA FASE 3 v7.3.0")
    
    print(f"{Colors.BOLD}Data:{Colors.END} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Colors.BOLD}Versão:{Colors.END} 7.3.0 (Machine Learning e IA)")
    
    # Executar todos os testes
    resultados = []
    
    resultados.append(test_ml_modules())
    resultados.append(test_sentiment_analyzer())
    resultados.append(test_price_predictor())
    resultados.append(test_portfolio_optimizer())
    resultados.append(test_api_endpoints())
    resultados.append(test_frontend())
    resultados.append(test_compatibilidade())
    
    # Calcular totais
    total_passed = sum(r[0] for r in resultados)
    total_tests = sum(r[1] for r in resultados)
    percentual = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    
    print(f"{Colors.BOLD}Total de testes:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}Testes passados:{Colors.END} {total_passed}")
    print(f"{Colors.RED}{Colors.BOLD}Testes falhados:{Colors.END} {total_tests - total_passed}")
    print(f"{Colors.BOLD}Taxa de sucesso:{Colors.END} {percentual:.1f}%")
    
    # Status final
    print()
    if percentual >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ FASE 3 APROVADA!{Colors.END}")
        print(f"{Colors.GREEN}Todos os modelos de ML foram implementados com sucesso.{Colors.END}")
        return 0
    elif percentual >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  FASE 3 PARCIALMENTE APROVADA{Colors.END}")
        print(f"{Colors.YELLOW}Alguns testes falharam. Revise antes de prosseguir.{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ FASE 3 REPROVADA{Colors.END}")
        print(f"{Colors.RED}Muitos testes falharam. Corrija os problemas.{Colors.END}")
        return 2

if __name__ == '__main__':
    sys.exit(main())

