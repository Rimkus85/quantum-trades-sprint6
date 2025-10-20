#!/usr/bin/env python3
"""
Magnus Wealth - Polling Client
Roda no Termux e busca comandos do servidor Manus
"""

import requests
import time
import json

# Configurações
SERVIDOR_MANUS = "https://5001-ib34pqn2vi38fss1puv5n-a559137e.manusvm.computer"
MAGNUS_LOCAL = "http://localhost:5000"
INTERVALO = 5  # segundos

print("═══════════════════════════════════════")
print("  MAGNUS WEALTH - POLLING CLIENT")
print("═══════════════════════════════════════\n")
print(f"Servidor Manus: {SERVIDOR_MANUS}")
print(f"Magnus Local: {MAGNUS_LOCAL}")
print(f"Intervalo: {INTERVALO}s\n")

while True:
    try:
        # 1. Buscar comandos pendentes do servidor Manus
        r = requests.get(f"{SERVIDOR_MANUS}/api/commands/pending", timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            commands = data.get('commands', [])
            
            if commands:
                print(f"\n📥 {len(commands)} comando(s) recebido(s)")
                
                for cmd in commands:
                    cmd_id = cmd['id']
                    endpoint = cmd['endpoint']
                    payload = cmd.get('payload', {})
                    
                    print(f"  Executando: {endpoint}")
                    
                    try:
                        # 2. Executar comando localmente
                        local_r = requests.post(
                            f"{MAGNUS_LOCAL}{endpoint}",
                            json=payload,
                            timeout=30
                        )
                        
                        result = {
                            'status': 'success' if local_r.ok else 'error',
                            'response': local_r.json() if local_r.ok else {'error': local_r.text}
                        }
                        
                        print(f"  ✓ Executado: {result['status']}")
                        
                    except Exception as e:
                        result = {
                            'status': 'error',
                            'response': {'error': str(e)}
                        }
                        print(f"  ✗ Erro: {e}")
                    
                    # 3. Enviar resultado de volta
                    requests.post(
                        f"{SERVIDOR_MANUS}/api/commands/{cmd_id}/result",
                        json=result,
                        timeout=10
                    )
        
        # Aguardar próximo ciclo
        time.sleep(INTERVALO)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        break
    except Exception as e:
        print(f"✗ Erro no polling: {e}")
        time.sleep(INTERVALO)

print("\n✓ Cliente encerrado")

