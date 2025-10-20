#!/usr/bin/env python3
"""
Magnus Wealth - Command Server
Servidor no Manus que gerencia comandos para o Termux
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# Fila de comandos
commands_queue = []
commands_results = {}
command_id_counter = 0
lock = threading.Lock()

@app.route('/api/commands/pending', methods=['GET'])
def get_pending_commands():
    """Retorna comandos pendentes para o cliente"""
    global commands_queue
    
    with lock:
        pending = [c for c in commands_queue if c['status'] == 'pending']
        
        # Marcar como enviados
        for cmd in pending:
            cmd['status'] = 'sent'
            cmd['sent_at'] = datetime.now().isoformat()
        
        return jsonify({'commands': pending})

@app.route('/api/commands/<int:cmd_id>/result', methods=['POST'])
def receive_result(cmd_id):
    """Recebe resultado de um comando executado"""
    global commands_results
    
    data = request.json
    
    with lock:
        commands_results[cmd_id] = {
            'result': data,
            'received_at': datetime.now().isoformat()
        }
        
        # Marcar comando como completo
        for cmd in commands_queue:
            if cmd['id'] == cmd_id:
                cmd['status'] = 'completed'
                cmd['result'] = data
                break
    
    return jsonify({'status': 'ok'})

@app.route('/api/commands/send', methods=['POST'])
def send_command():
    """Envia um novo comando para o cliente"""
    global command_id_counter, commands_queue
    
    data = request.json
    endpoint = data.get('endpoint')
    payload = data.get('payload', {})
    
    with lock:
        command_id_counter += 1
        cmd = {
            'id': command_id_counter,
            'endpoint': endpoint,
            'payload': payload,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        commands_queue.append(cmd)
    
    # Aguardar resultado (timeout 60s)
    timeout = 60
    start = time.time()
    
    while time.time() - start < timeout:
        if command_id_counter in commands_results:
            return jsonify({
                'status': 'success',
                'command_id': command_id_counter,
                'result': commands_results[command_id_counter]
            })
        time.sleep(0.5)
    
    return jsonify({
        'status': 'timeout',
        'command_id': command_id_counter,
        'message': 'Comando enviado mas sem resposta'
    }), 408

@app.route('/api/commands/status', methods=['GET'])
def get_status():
    """Status do servidor de comandos"""
    with lock:
        return jsonify({
            'total_commands': len(commands_queue),
            'pending': len([c for c in commands_queue if c['status'] == 'pending']),
            'sent': len([c for c in commands_queue if c['status'] == 'sent']),
            'completed': len([c for c in commands_queue if c['status'] == 'completed']),
            'results_count': len(commands_results)
        })

@app.route('/health')
def health():
    return jsonify({'status': 'online'})

if __name__ == '__main__':
    print('═══════════════════════════════════════')
    print('  MAGNUS WEALTH - COMMAND SERVER')
    print('═══════════════════════════════════════\n')
    print('✓ Servidor iniciado em http://0.0.0.0:5001\n')
    
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

