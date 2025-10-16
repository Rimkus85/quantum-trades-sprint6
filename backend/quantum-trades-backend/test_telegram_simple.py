#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def test():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    print("=" * 80)
    print("CONECTANDO AO TELEGRAM")
    print("=" * 80)
    print(f"\nTelefone: {phone}")
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    
    await client.start(phone=phone)
    
    print("\n✓ Conectado com sucesso!")
    
    # Obter informações do usuário
    me = await client.get_me()
    print(f"\n✓ Usuário: {me.first_name} {me.last_name or ''}")
    print(f"  Username: @{me.username or 'N/A'}")
    print(f"  ID: {me.id}")
    
    # Listar grupos
    print(f"\n⏳ Buscando grupos...")
    dialogs = await client.get_dialogs()
    
    groups = []
    for d in dialogs:
        if d.is_group or d.is_channel:
            groups.append(d)
    
    print(f"\n✓ Encontrados {len(groups)} grupos/canais:")
    for i, d in enumerate(groups, 1):
        username = f"@{d.entity.username}" if hasattr(d.entity, 'username') and d.entity.username else ""
        print(f"\n  {i}. {d.name}")
        if username:
            print(f"     Username: {username}")
        print(f"     ID: {d.entity.id}")
        
        # Verificar se é o grupo que procuramos
        if "tio huli" in d.name.lower() or "carteira" in d.name.lower():
            print(f"     ⭐ POSSÍVEL GRUPO ALVO!")
            
            # Tentar ler mensagens
            try:
                messages = await client.get_messages(d.entity, limit=5)
                print(f"     ✓ {len(messages)} mensagens recentes:")
                for msg in messages[:3]:
                    if msg.text:
                        preview = msg.text[:80].replace('\n', ' ')
                        print(f"       - {preview}...")
            except Exception as e:
                print(f"     ⚠ Erro ao ler mensagens: {e}")
    
    await client.disconnect()
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)

if __name__ == '__main__':
    asyncio.run(test())
