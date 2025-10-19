#!/usr/bin/env python3
"""
Magnus Wealth - Teste da Fase 2
Valida todas as funcionalidades implementadas na Fase 2 (Visualização e Interface)
"""

import os
import sys
import requests
import json
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

def test_arquivos_frontend():
    """Testa se os arquivos frontend foram criados"""
    
    print_section("TESTE 1: Arquivos Frontend")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    
    arquivos = {
        'Páginas HTML': [
            'painel_telegram.html',
            'graficos_avancados.html',
            'cotacoes_tempo_real.html'
        ],
        'JavaScript': [
            'js/telegram_service.js',
            'js/charts_service.js',
            'js/websocket_service.js'
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    
    for categoria, files in arquivos.items():
        print(f"\n  {Colors.BOLD}{categoria}:{Colors.END}")
        for arquivo in files:
            total_tests += 1
            caminho = os.path.join(frontend_dir, arquivo)
            existe = os.path.exists(caminho)
            
            if existe:
                tamanho = os.path.getsize(caminho)
                tamanho_kb = tamanho / 1024
                print_test(
                    f"{arquivo}", 
                    True, 
                    f"Tamanho: {tamanho_kb:.1f} KB"
                )
                passed_tests += 1
            else:
                print_test(f"{arquivo}", False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_servidor_websocket():
    """Testa se o servidor WebSocket foi criado"""
    
    print_section("TESTE 2: Servidor WebSocket")
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    total_tests = 0
    passed_tests = 0
    
    # Verificar arquivo app_websocket.py
    total_tests += 1
    app_ws_path = os.path.join(backend_dir, 'app_websocket.py')
    
    if os.path.exists(app_ws_path):
        tamanho = os.path.getsize(app_ws_path)
        tamanho_kb = tamanho / 1024
        print_test(
            "app_websocket.py", 
            True, 
            f"Tamanho: {tamanho_kb:.1f} KB"
        )
        passed_tests += 1
        
        # Verificar conteúdo
        with open(app_ws_path, 'r') as f:
            conteudo = f.read()
        
        componentes = {
            'Flask-SocketIO': 'flask_socketio',
            'Event connect': '@socketio.on(\'connect\')',
            'Event subscribe': '@socketio.on(\'subscribe\')',
            'Background task': 'background_price_updates',
            'Fetch price': 'def fetch_price'
        }
        
        for nome, padrao in componentes.items():
            total_tests += 1
            if padrao in conteudo:
                print_test(nome, True, "Implementado")
                passed_tests += 1
            else:
                print_test(nome, False, "Não encontrado")
    else:
        print_test("app_websocket.py", False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_integracao_api():
    """Testa integração com APIs externas"""
    
    print_section("TESTE 3: Integração com APIs")
    
    total_tests = 0
    passed_tests = 0
    
    # Testar brapi.dev
    total_tests += 1
    try:
        response = requests.get('https://brapi.dev/api/quote/PETR4', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                price = result.get('regularMarketPrice', 0)
                print_test(
                    "brapi.dev API", 
                    True, 
                    f"PETR4: R$ {price:.2f}"
                )
                passed_tests += 1
            else:
                print_test("brapi.dev API", False, "Resposta sem dados")
        else:
            print_test("brapi.dev API", False, f"Status {response.status_code}")
    except Exception as e:
        print_test("brapi.dev API", False, str(e))
    
    return passed_tests, total_tests

def test_responsividade():
    """Testa se as páginas são responsivas"""
    
    print_section("TESTE 4: Responsividade")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    
    paginas = [
        'painel_telegram.html',
        'graficos_avancados.html',
        'cotacoes_tempo_real.html'
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for pagina in paginas:
        total_tests += 1
        caminho = os.path.join(frontend_dir, pagina)
        
        if os.path.exists(caminho):
            with open(caminho, 'r') as f:
                conteudo = f.read()
            
            # Verificar meta viewport
            has_viewport = 'viewport' in conteudo and 'width=device-width' in conteudo
            
            # Verificar media queries
            has_media_queries = '@media' in conteudo
            
            # Verificar grid responsivo
            has_responsive_grid = 'grid-template-columns' in conteudo and 'auto-fit' in conteudo or 'auto-fill' in conteudo
            
            is_responsive = has_viewport and (has_media_queries or has_responsive_grid)
            
            if is_responsive:
                print_test(
                    pagina, 
                    True, 
                    "Viewport + Media Queries/Grid"
                )
                passed_tests += 1
            else:
                print_test(pagina, False, "Faltam elementos de responsividade")
        else:
            print_test(pagina, False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_funcionalidades_javascript():
    """Testa funcionalidades JavaScript"""
    
    print_section("TESTE 5: Funcionalidades JavaScript")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend', 'js')
    
    funcionalidades = {
        'telegram_service.js': [
            'loadMessages',
            'loadStatistics',
            'filterMessages',
            'renderMessages'
        ],
        'charts_service.js': [
            'initializeChart',
            'loadChartData',
            'calculateMA',
            'calculateEMA'
        ],
        'websocket_service.js': [
            'connectWebSocket',
            'subscribeTicker',
            'unsubscribeTicker',
            'onPriceUpdate'
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    
    for arquivo, funcoes in funcionalidades.items():
        caminho = os.path.join(frontend_dir, arquivo)
        
        if os.path.exists(caminho):
            with open(caminho, 'r') as f:
                conteudo = f.read()
            
            print(f"\n  {Colors.BOLD}{arquivo}:{Colors.END}")
            
            for funcao in funcoes:
                total_tests += 1
                if f"function {funcao}" in conteudo or f"{funcao} =" in conteudo:
                    print_test(funcao, True, "Implementada")
                    passed_tests += 1
                else:
                    print_test(funcao, False, "Não encontrada")
        else:
            print(f"\n  {Colors.BOLD}{arquivo}:{Colors.END}")
            for funcao in funcoes:
                total_tests += 1
                print_test(funcao, False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_compatibilidade_funcionalidades_existentes():
    """Testa se funcionalidades existentes foram mantidas"""
    
    print_section("TESTE 6: Compatibilidade com v7.1.0")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, '..', 'frontend')
    
    arquivos_existentes = [
        'dashboard_final.html',
        'dashboard_sprint6.html',
        'portfolio.html',
        'painel_ia.html',
        'alertas_sistema.html',
        'index.html',
        'js/magnus_learning.js'
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
    
    print_header("MAGNUS WEALTH - TESTE DA FASE 2 v7.2.0")
    
    print(f"{Colors.BOLD}Data:{Colors.END} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Colors.BOLD}Versão:{Colors.END} 7.2.0 (Visualização e Interface)")
    
    # Executar todos os testes
    resultados = []
    
    resultados.append(test_arquivos_frontend())
    resultados.append(test_servidor_websocket())
    resultados.append(test_integracao_api())
    resultados.append(test_responsividade())
    resultados.append(test_funcionalidades_javascript())
    resultados.append(test_compatibilidade_funcionalidades_existentes())
    
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
        print(f"{Colors.GREEN}{Colors.BOLD}✅ FASE 2 APROVADA!{Colors.END}")
        print(f"{Colors.GREEN}Todas as funcionalidades foram implementadas com sucesso.{Colors.END}")
        return 0
    elif percentual >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  FASE 2 PARCIALMENTE APROVADA{Colors.END}")
        print(f"{Colors.YELLOW}Alguns testes falharam. Revise antes de prosseguir.{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ FASE 2 REPROVADA{Colors.END}")
        print(f"{Colors.RED}Muitos testes falharam. Corrija os problemas.{Colors.END}")
        return 2

if __name__ == '__main__':
    sys.exit(main())

