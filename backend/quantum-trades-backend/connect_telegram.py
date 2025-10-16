#!/usr/bin/env python3
"""
Script para conectar ao Telegram e listar grupos.
Usa senha automática se configurada.
"""
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

async def connect_and_list_groups():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    password = os.getenv('TELEGRAM_PASSWORD')
    
    print("=" * 80)
    print("MAGNUS - CONEXÃO COM TELEGRAM")
    print("=" * 80)
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    
    try:
        print(f"\n⏳ Conectando com {phone}...")
        await client.connect()
        
        # Verificar se já está autorizado
        if not await client.is_user_authorized():
            print("⏳ Autenticação necessária...")
            
            # Enviar código
            await client.send_code_request(phone)
            print("✓ Código enviado para seu Telegram")
            
            # Solicitar código
            code = input("\nDigite o código recebido: ")
            
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # Senha de 2FA necessária
                if password:
                    print("⏳ Usando senha configurada...")
                    await client.sign_in(password=password)
                else:
                    pwd = input("Digite sua senha do Telegram: ")
                    await client.sign_in(password=pwd)
        
        print("\n✅ CONECTADO COM SUCESSO!")
        
        # Obter informações do usuário
        me = await client.get_me()
        print(f"\n👤 Usuário: {me.first_name} {me.last_name or ''}")
        print(f"   ID: {me.id}")
        if me.username:
            print(f"   Username: @{me.username}")
        
        # Listar grupos
        print(f"\n⏳ Buscando grupos e canais...")
        dialogs = await client.get_dialogs()
        
        groups = [d for d in dialogs if d.is_group or d.is_channel]
        
        print(f"\n📊 GRUPOS/CANAIS ENCONTRADOS: {len(groups)}")
        print("=" * 80)
        
        target_group = None
        
        for i, d in enumerate(groups, 1):
            print(f"\n{i}. 📁 {d.name}")
            print(f"   ID: {d.entity.id}")
            
            if hasattr(d.entity, 'username') and d.entity.username:
                print(f"   Username: @{d.entity.username}")
            
            # Verificar se é o grupo alvo
            name_lower = d.name.lower()
            if any(keyword in name_lower for keyword in ['tio huli', 'carteira', 'recomendada']):
                print(f"   ⭐ GRUPO ALVO IDENTIFICADO!")
                target_group = d
                
                # Tentar ler mensagens
                try:
                    print(f"   ⏳ Lendo mensagens recentes...")
                    messages = await client.get_messages(d.entity, limit=10)
                    print(f"   ✓ {len(messages)} mensagens disponíveis")
                    
                    print(f"\n   📝 ÚLTIMAS 5 MENSAGENS:")
                    for j, msg in enumerate(messages[:5], 1):
                        if msg.text:
                            date = msg.date.strftime("%d/%m/%Y %H:%M")
                            preview = msg.text[:100].replace('\n', ' ')
                            print(f"\n      {j}. [{date}]")
                            print(f"         {preview}...")
                        
                except Exception as e:
                    print(f"   ⚠ Erro ao ler mensagens: {e}")
        
        if target_group:
            print(f"\n" + "=" * 80)
            print(f"✅ GRUPO ALVO CONFIGURADO: {target_group.name}")
            print(f"   ID: {target_group.entity.id}")
            print("=" * 80)
            
            # Salvar ID do grupo no .env
            env_path = '.env'
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Adicionar ou atualizar TELEGRAM_GROUP_ID
            found = False
            for i, line in enumerate(lines):
                if line.startswith('TELEGRAM_GROUP_ID='):
                    lines[i] = f'TELEGRAM_GROUP_ID={target_group.entity.id}\n'
                    found = True
                    break
            
            if not found:
                lines.insert(5, f'TELEGRAM_GROUP_ID={target_group.entity.id}\n')
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            print(f"\n✓ ID do grupo salvo no .env")
        else:
            print(f"\n⚠ Grupo alvo não identificado automaticamente")
            print(f"   Por favor, identifique manualmente na lista acima")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()
        print(f"\n✓ Desconectado")

if __name__ == '__main__':
    asyncio.run(connect_and_list_groups())
