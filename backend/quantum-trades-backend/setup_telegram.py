#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Telegram - Autenticação e Obtenção do ID do Grupo
Magnus Wealth
"""

import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

def setup_telegram():
    """
    Autentica no Telegram e obtém o ID do grupo
    """
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    group_name = os.getenv('TELEGRAM_GROUP_USERNAME')
    
    print('═══════════════════════════════════════════════════')
    print('  MAGNUS WEALTH - SETUP TELEGRAM')
    print('═══════════════════════════════════════════════════\n')
    print(f'📱 Telefone: {phone}')
    print(f'👥 Grupo: {group_name}\n')
    
    # Criar cliente Telegram
    client = TelegramClient('magnus_session', api_id, api_hash)
    
    print('🔐 Conectando ao Telegram...\n')
    client.start(phone=phone)
    
    print('✓ Autenticação bem-sucedida!\n')
    print('📋 Buscando grupos e canais...\n')
    
    # Listar todos os diálogos (grupos, canais, conversas)
    dialogs = client.get_dialogs()
    
    print(f'Total de diálogos encontrados: {len(dialogs)}\n')
    print('═══════════════════════════════════════════════════')
    print('GRUPOS E CANAIS DISPONÍVEIS:')
    print('═══════════════════════════════════════════════════\n')
    
    group_found = None
    
    for dialog in dialogs:
        if dialog.is_group or dialog.is_channel:
            print(f'📁 {dialog.name}')
            print(f'   ID: {dialog.id}')
            print(f'   Tipo: {"Grupo" if dialog.is_group else "Canal"}')
            print()
            
            # Verificar se é o grupo procurado
            if group_name.lower() in dialog.name.lower():
                group_found = dialog
                print(f'   ✓ GRUPO ENCONTRADO!')
                print()
    
    print('═══════════════════════════════════════════════════\n')
    
    if group_found:
        print(f'✓ Grupo "{group_found.name}" encontrado!')
        print(f'📋 ID do grupo: {group_found.id}\n')
        print('Atualizando arquivo .env...')
        
        # Ler arquivo .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Adicionar ou atualizar TELEGRAM_GROUP_ID
        group_id_found = False
        for i, line in enumerate(lines):
            if line.startswith('TELEGRAM_GROUP_ID='):
                lines[i] = f'TELEGRAM_GROUP_ID={group_found.id}\n'
                group_id_found = True
                break
        
        if not group_id_found:
            # Adicionar após TELEGRAM_GROUP_USERNAME
            for i, line in enumerate(lines):
                if line.startswith('TELEGRAM_GROUP_USERNAME='):
                    lines.insert(i+1, f'TELEGRAM_GROUP_ID={group_found.id}\n')
                    break
        
        # Salvar arquivo .env
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print('✓ Arquivo .env atualizado!\n')
        print('Testando envio de mensagem...\n')
        
        # Enviar mensagem de teste
        try:
            client.send_message(
                group_found.id,
                '🚀 *MAGNUS WEALTH - SISTEMA ATIVADO*\n\n'
                '✓ Autenticação configurada com sucesso!\n'
                '✓ Sessão persistente criada\n'
                '✓ Pronto para enviar análises automáticas\n\n'
                '📊 Sistema: Gann HiLo Activator v8.3.0\n'
                '🎯 TOP 8 Criptomoedas\n'
                '⏰ Execução: Diária às 21h',
                parse_mode='markdown'
            )
            print('✓ Mensagem de teste enviada com sucesso!')
        except Exception as e:
            print(f'✗ Erro ao enviar mensagem: {e}')
    else:
        print(f'✗ Grupo "{group_name}" não encontrado!')
        print('Por favor, verifique o nome do grupo no arquivo .env')
    
    print('\n═══════════════════════════════════════════════════')
    print('Setup concluído!')
    print('═══════════════════════════════════════════════════')
    
    client.disconnect()

if __name__ == '__main__':
    setup_telegram()

