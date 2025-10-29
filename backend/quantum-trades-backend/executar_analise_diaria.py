#!/usr/bin/env python3
"""
Wrapper Inteligente para Análise Diária
Magnus Wealth - Sistema de Execução Garantida às 21:05 GMT-3

Funcionalidades:
- Lock de execução diária (evita duplicatas)
- Logging detalhado de horários
- Validação de timezone
- Auto-recuperação de falhas
"""

import os
import sys
import json
import pytz
from datetime import datetime, timedelta
from pathlib import Path

# Diretório de locks e logs
LOCK_DIR = Path(__file__).parent / "locks"
LOG_DIR = Path(__file__).parent / "logs"
LOCK_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Timezone de Brasília
TZ_BRASILIA = pytz.timezone('America/Sao_Paulo')

def get_today_lock_file():
    """Retorna caminho do arquivo de lock de hoje"""
    hoje = datetime.now(TZ_BRASILIA).strftime('%Y-%m-%d')
    return LOCK_DIR / f"analise_{hoje}.lock"

def get_log_file():
    """Retorna caminho do arquivo de log"""
    return LOG_DIR / "execucoes_diarias.jsonl"

def ja_executou_hoje():
    """Verifica se já executou hoje"""
    lock_file = get_today_lock_file()
    
    if lock_file.exists():
        # Ler dados do lock
        try:
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
            
            # Verificar se foi sucesso
            if lock_data.get('status') == 'success':
                print(f"✅ Análise já executada hoje às {lock_data.get('horario_br')}")
                return True
            else:
                print(f"⚠️ Execução anterior falhou, tentando novamente...")
                return False
        except:
            return False
    
    return False

def registrar_execucao(status, mensagem=""):
    """Registra execução no lock e no log"""
    agora_utc = datetime.now(pytz.UTC)
    agora_br = agora_utc.astimezone(TZ_BRASILIA)
    
    lock_file = get_today_lock_file()
    log_file = get_log_file()
    
    # Dados da execução
    dados = {
        'data': agora_br.strftime('%Y-%m-%d'),
        'horario_utc': agora_utc.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'horario_br': agora_br.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'timestamp_utc': agora_utc.timestamp(),
        'timestamp_br': agora_br.timestamp(),
        'status': status,
        'mensagem': mensagem,
        'horario_alvo': '21:05 GMT-3',
        'diferenca_minutos': calcular_diferenca_21_05(agora_br)
    }
    
    # Salvar lock
    with open(lock_file, 'w') as f:
        json.dump(dados, f, indent=2)
    
    # Append no log
    with open(log_file, 'a') as f:
        f.write(json.dumps(dados) + '\n')
    
    return dados

def calcular_diferenca_21_05(horario_br):
    """Calcula diferença em minutos do horário alvo (21:05)"""
    alvo = horario_br.replace(hour=21, minute=5, second=0, microsecond=0)
    
    # Se passou de 21:05, calcular para o dia seguinte
    if horario_br.hour > 21 or (horario_br.hour == 21 and horario_br.minute > 5):
        alvo = alvo + timedelta(days=1)
    
    diferenca = (horario_br - alvo).total_seconds() / 60
    return round(diferenca, 2)

def imprimir_banner():
    """Imprime banner com informações de execução"""
    agora_utc = datetime.now(pytz.UTC)
    agora_br = agora_utc.astimezone(TZ_BRASILIA)
    
    print("=" * 80)
    print("🚀 MAGNUS WEALTH - ANÁLISE DIÁRIA DE CRIPTOMOEDAS")
    print("=" * 80)
    print(f"📅 Data: {agora_br.strftime('%d/%m/%Y')}")
    print(f"🕐 Horário UTC: {agora_utc.strftime('%H:%M:%S %Z')}")
    print(f"🕐 Horário BR:  {agora_br.strftime('%H:%M:%S %Z')}")
    print(f"🎯 Alvo: 21:05 GMT-3")
    print(f"📊 Diferença: {calcular_diferenca_21_05(agora_br):+.2f} minutos")
    print("=" * 80)

def limpar_locks_antigos():
    """Remove locks com mais de 7 dias"""
    try:
        limite = datetime.now(TZ_BRASILIA) - timedelta(days=7)
        
        for lock_file in LOCK_DIR.glob("analise_*.lock"):
            # Extrair data do nome do arquivo
            try:
                data_str = lock_file.stem.replace('analise_', '')
                data_lock = datetime.strptime(data_str, '%Y-%m-%d')
                data_lock = TZ_BRASILIA.localize(data_lock)
                
                if data_lock < limite:
                    lock_file.unlink()
                    print(f"🗑️  Removido lock antigo: {lock_file.name}")
            except:
                continue
    except Exception as e:
        print(f"⚠️  Erro ao limpar locks: {e}")

def executar_analise():
    """Executa o script de análise"""
    script_path = Path(__file__).parent / "analisador_cripto_hilo_bot.py"
    
    print(f"\n▶️  Executando: {script_path.name}")
    print("-" * 80)
    
    # Executar script
    import subprocess
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        text=True
    )
    
    print("-" * 80)
    
    return result.returncode == 0

def main():
    """Função principal"""
    imprimir_banner()
    
    # Verificar se já executou hoje
    if ja_executou_hoje():
        print("\n✅ Análise já executada hoje com sucesso!")
        print("💡 Para forçar nova execução, delete o arquivo de lock:")
        print(f"   {get_today_lock_file()}")
        return 0
    
    # Limpar locks antigos
    limpar_locks_antigos()
    
    # Executar análise
    try:
        sucesso = executar_analise()
        
        if sucesso:
            dados = registrar_execucao('success', 'Análise executada com sucesso')
            print("\n" + "=" * 80)
            print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
            print(f"🕐 Horário BR: {dados['horario_br']}")
            print(f"📊 Diferença do alvo (21:05): {dados['diferenca_minutos']:+.2f} minutos")
            print("=" * 80)
            return 0
        else:
            dados = registrar_execucao('error', 'Erro na execução da análise')
            print("\n" + "=" * 80)
            print("❌ ERRO NA EXECUÇÃO!")
            print(f"🕐 Horário BR: {dados['horario_br']}")
            print("=" * 80)
            return 1
            
    except Exception as e:
        dados = registrar_execucao('error', f'Exceção: {str(e)}')
        print("\n" + "=" * 80)
        print(f"❌ EXCEÇÃO: {e}")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
