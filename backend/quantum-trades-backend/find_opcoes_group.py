#!/usr/bin/env python3
"""
Busca grupo Sala de Opções.
"""
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def find_opcoes():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("=" * 80)
    print("BUSCANDO: SALA DE OPÇÕES")
    print("=" * 80)
    
    try:
        dialogs = await client.get_dialogs()
        
        # Buscar por "opções" ou "opcoes"
        found = []
        for dialog in dialogs:
            title = dialog.title.lower()
            if 'opç' in title or 'opc' in title:
                found.append({
                    'title': dialog.title,
                    'id': dialog.id,
                    'is_group': dialog.is_group,
                    'is_channel': dialog.is_channel
                })
        
        print(f"\n✅ Encontrados {len(found)} grupos/canais com 'opções':\n")
        
        for i, item in enumerate(found, 1):
            print(f"{i}. {item['title']}")
            print(f"   ID: {item['id']}")
            print(f"   Grupo: {item['is_group']}, Canal: {item['is_channel']}")
            print()
        
        if not found:
            print("⚠ Nenhum grupo encontrado com 'opções'")
            print("\nBuscando por 'tio huli'...")
            
            for dialog in dialogs:
                title = dialog.title.lower()
                if 'tio' in title and 'huli' in title:
                    print(f"\n- {dialog.title} (ID: {dialog.id})")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(find_opcoes())
