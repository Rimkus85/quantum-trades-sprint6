#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def find_group():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("=" * 80)
    print("BUSCANDO GRUPO: 'carteira recomendada' + 'tio huli'")
    print("=" * 80)
    
    dialogs = await client.get_dialogs()
    
    print(f"\nProcurando em {len(dialogs)} conversas...\n")
    
    found = []
    
    for d in dialogs:
        name_lower = d.name.lower()
        
        # Buscar grupos que contenham ambas as palavras
        if 'carteira' in name_lower and 'tio huli' in name_lower:
            found.append(d)
            print(f"✅ ENCONTRADO!")
            print(f"   Nome: {d.name}")
            print(f"   ID: {d.entity.id}")
            if hasattr(d.entity, 'username') and d.entity.username:
                print(f"   Username: @{d.entity.username}")
            
            # Ler mensagens
            try:
                messages = await client.get_messages(d.entity, limit=10)
                print(f"   Mensagens: {len(messages)} disponíveis\n")
                
                print("   📝 ÚLTIMAS 5 MENSAGENS:")
                for i, msg in enumerate(messages[:5], 1):
                    if msg.text:
                        date = msg.date.strftime("%d/%m/%Y %H:%M")
                        preview = msg.text[:150].replace('\n', ' ')
                        print(f"\n   {i}. [{date}]")
                        print(f"      {preview}...")
            except Exception as e:
                print(f"   ⚠ Erro ao ler: {e}")
            
            print("\n" + "=" * 80)
    
    # Se não encontrou, mostrar grupos similares
    if not found:
        print("\n❌ Nenhum grupo encontrado com AMBAS as palavras")
        print("\nGrupos com 'carteira':")
        for d in dialogs:
            if 'carteira' in d.name.lower():
                print(f"  - {d.name}")
        
        print("\nGrupos com 'tio huli':")
        for d in dialogs:
            if 'tio huli' in d.name.lower():
                print(f"  - {d.name}")
    else:
        print(f"\n✅ Total encontrado: {len(found)} grupo(s)")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(find_group())
