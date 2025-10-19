#!/usr/bin/env python3
"""
Magnus Wealth - Teste Completo do Sistema
Valida todas as funcionalidades implementadas na v7.0.0 + Fase 1
"""

import os
import sys
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

def test_estrutura_arquivos():
    """Testa se todos os arquivos necessários existem"""
    
    print_section("TESTE 1: Estrutura de Arquivos")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    arquivos_necessarios = {
        'Scripts de Análise': [
            'analise_diaria.py',
            'analise_opcoes.py',
            'resumo_semanal.py',
            'bot_comandos.py'
        ],
        'Configuração': [
            'crontab_magnus.txt',
            'setup_agendamento.sh',
            '.env.example',
            'Procfile',
            'railway.json'
        ],
        'Documentação': [
            'AGENDAMENTO_README.md',
            'DEPLOY_RAILWAY.md',
            'README.md'
        ],
        'Dados': [
            'magnus_session.session'
        ]
    }
    
    total_tests = 0
    passed_tests = 0
    
    for categoria, arquivos in arquivos_necessarios.items():
        print(f"\n  {Colors.BOLD}{categoria}:{Colors.END}")
        for arquivo in arquivos:
            total_tests += 1
            caminho = os.path.join(base_dir, arquivo)
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

def test_sintaxe_python():
    """Testa sintaxe dos scripts Python"""
    
    print_section("TESTE 2: Sintaxe Python")
    
    scripts = [
        'analise_diaria.py',
        'analise_opcoes.py',
        'resumo_semanal.py',
        'bot_comandos.py'
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for script in scripts:
        total_tests += 1
        try:
            with open(script, 'r') as f:
                compile(f.read(), script, 'exec')
            print_test(f"{script}", True, "Sintaxe válida")
            passed_tests += 1
        except SyntaxError as e:
            print_test(f"{script}", False, f"Erro de sintaxe: {e}")
        except FileNotFoundError:
            print_test(f"{script}", False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_dependencias():
    """Testa se as dependências estão instaladas"""
    
    print_section("TESTE 3: Dependências Python")
    
    dependencias = {
        'telethon': 'Telegram API',
        'dotenv': 'Variáveis de ambiente',
        'flask': 'API REST (opcional)',
        'asyncio': 'Async/await (built-in)'
    }
    
    total_tests = 0
    passed_tests = 0
    
    for modulo, descricao in dependencias.items():
        total_tests += 1
        try:
            if modulo == 'dotenv':
                __import__('dotenv')
            else:
                __import__(modulo)
            print_test(f"{modulo}", True, descricao)
            passed_tests += 1
        except ImportError:
            print_test(f"{modulo}", False, f"{descricao} - Não instalado")
    
    return passed_tests, total_tests

def test_configuracao_cron():
    """Testa configuração do crontab"""
    
    print_section("TESTE 4: Configuração Crontab")
    
    total_tests = 0
    passed_tests = 0
    
    # Verificar arquivo crontab_magnus.txt
    total_tests += 1
    if os.path.exists('crontab_magnus.txt'):
        with open('crontab_magnus.txt', 'r') as f:
            conteudo = f.read()
        
        # Verificar agendamentos essenciais
        agendamentos = {
            'Análise Diária (21:00)': '0 21 * * *',
            'Análise Opções (10:10)': '10 10 * * 1-5',
            'Análise Opções (14:00)': '0 14 * * 1-5',
            'Análise Opções (16:45)': '45 16 * * 1-5',
            'Resumo Semanal (Sábado 10:00)': '0 10 * * 6'
        }
        
        for nome, padrao in agendamentos.items():
            total_tests += 1
            if padrao in conteudo:
                print_test(nome, True, f"Agendado: {padrao}")
                passed_tests += 1
            else:
                print_test(nome, False, "Agendamento não encontrado")
        
        passed_tests += 1
        print_test("crontab_magnus.txt", True, "Arquivo existe")
    else:
        print_test("crontab_magnus.txt", False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_estrutura_diretorios():
    """Testa se os diretórios necessários podem ser criados"""
    
    print_section("TESTE 5: Estrutura de Diretórios")
    
    diretorios = ['logs', 'backups', 'youtube_knowledge']
    
    total_tests = 0
    passed_tests = 0
    
    for diretorio in diretorios:
        total_tests += 1
        caminho = os.path.join(os.path.dirname(__file__), diretorio)
        
        # Verificar se existe ou pode ser criado
        if os.path.exists(caminho):
            print_test(f"{diretorio}/", True, "Diretório existe")
            passed_tests += 1
        else:
            # Tentar criar
            try:
                os.makedirs(caminho, exist_ok=True)
                print_test(f"{diretorio}/", True, "Diretório criado")
                passed_tests += 1
            except Exception as e:
                print_test(f"{diretorio}/", False, f"Erro ao criar: {e}")
    
    return passed_tests, total_tests

def test_configuracao_deploy():
    """Testa arquivos de configuração de deploy"""
    
    print_section("TESTE 6: Configuração de Deploy")
    
    total_tests = 0
    passed_tests = 0
    
    # Verificar Procfile
    total_tests += 1
    if os.path.exists('Procfile'):
        with open('Procfile', 'r') as f:
            conteudo = f.read()
        if 'bot:' in conteudo and 'python3 bot_comandos.py' in conteudo:
            print_test("Procfile", True, "Configurado para Railway/Heroku")
            passed_tests += 1
        else:
            print_test("Procfile", False, "Configuração incorreta")
    else:
        print_test("Procfile", False, "Arquivo não encontrado")
    
    # Verificar railway.json
    total_tests += 1
    if os.path.exists('railway.json'):
        try:
            with open('railway.json', 'r') as f:
                config = json.load(f)
            if 'deploy' in config and 'startCommand' in config['deploy']:
                print_test("railway.json", True, "Configuração válida")
                passed_tests += 1
            else:
                print_test("railway.json", False, "Configuração incompleta")
        except json.JSONDecodeError:
            print_test("railway.json", False, "JSON inválido")
    else:
        print_test("railway.json", False, "Arquivo não encontrado")
    
    # Verificar .env.example
    total_tests += 1
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            conteudo = f.read()
        variaveis = ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_PHONE']
        todas_presentes = all(var in conteudo for var in variaveis)
        
        if todas_presentes:
            print_test(".env.example", True, "Template completo")
            passed_tests += 1
        else:
            print_test(".env.example", False, "Variáveis faltando")
    else:
        print_test(".env.example", False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

def test_documentacao():
    """Testa se a documentação está completa"""
    
    print_section("TESTE 7: Documentação")
    
    total_tests = 0
    passed_tests = 0
    
    documentos = {
        'AGENDAMENTO_README.md': 5000,  # Tamanho mínimo em bytes
        'DEPLOY_RAILWAY.md': 5000,
        'README.md': 1000
    }
    
    for doc, tamanho_min in documentos.items():
        total_tests += 1
        if os.path.exists(doc):
            tamanho = os.path.getsize(doc)
            if tamanho >= tamanho_min:
                print_test(
                    doc, 
                    True, 
                    f"Completo ({tamanho/1024:.1f} KB)"
                )
                passed_tests += 1
            else:
                print_test(
                    doc, 
                    False, 
                    f"Incompleto ({tamanho} bytes < {tamanho_min} bytes)"
                )
        else:
            print_test(doc, False, "Arquivo não encontrado")
    
    return passed_tests, total_tests

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa todos os testes"""
    
    print_header("MAGNUS WEALTH - TESTE COMPLETO DO SISTEMA v7.0.0")
    
    print(f"{Colors.BOLD}Data:{Colors.END} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{Colors.BOLD}Versão:{Colors.END} 7.0.0 + Fase 1 (Consolidação e Automação)")
    
    # Executar todos os testes
    resultados = []
    
    resultados.append(test_estrutura_arquivos())
    resultados.append(test_sintaxe_python())
    resultados.append(test_dependencias())
    resultados.append(test_configuracao_cron())
    resultados.append(test_estrutura_diretorios())
    resultados.append(test_configuracao_deploy())
    resultados.append(test_documentacao())
    
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
        print(f"{Colors.GREEN}{Colors.BOLD}✅ SISTEMA APROVADO!{Colors.END}")
        print(f"{Colors.GREEN}O sistema está pronto para deploy.{Colors.END}")
        return 0
    elif percentual >= 70:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SISTEMA PARCIALMENTE APROVADO{Colors.END}")
        print(f"{Colors.YELLOW}Alguns testes falharam. Revise antes do deploy.{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SISTEMA REPROVADO{Colors.END}")
        print(f"{Colors.RED}Muitos testes falharam. Corrija os problemas antes de prosseguir.{Colors.END}")
        return 2

if __name__ == '__main__':
    sys.exit(main())

