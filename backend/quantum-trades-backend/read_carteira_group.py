#!/usr/bin/env python3
"""
Lê mensagens do grupo Carteira Recomendada - Tio Huli
"""
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def read_group():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    group_id = int(os.getenv('TELEGRAM_GROUP_ID'))
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("=" * 80)
    print("LENDO GRUPO: 📊Carteira Recomendada - Tio Huli")
    print("=" * 80)
    
    try:
        # Obter entidade do grupo
        entity = await client.get_entity(group_id)
        print(f"\n✓ Grupo: {entity.title}")
        print(f"  ID: {entity.id}")
        
        # Ler mensagens
        print(f"\n⏳ Lendo últimas 50 mensagens...")
        messages = await client.get_messages(entity, limit=50)
        
        print(f"\n✅ {len(messages)} mensagens lidas\n")
        print("=" * 80)
        
        for i, msg in enumerate(messages, 1):
            if msg.text:
                date = msg.date.strftime("%d/%m/%Y %H:%M")
                print(f"\n📝 MENSAGEM {i} - [{date}]")
                print("-" * 80)
                print(msg.text)
                print("-" * 80)
        
        print("\n" + "=" * 80)
        print(f"✅ TOTAL: {len([m for m in messages if m.text])} mensagens com texto")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(read_group())
