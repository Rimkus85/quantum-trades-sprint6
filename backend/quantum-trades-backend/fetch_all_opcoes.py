import os
import asyncio
import json
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def fetch_all():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    opcoes_group_id = -1002018374487
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("Buscando TODAS as mensagens da Sala de Opções...")
    print("Isso pode levar alguns minutos...")
    
    entity = await client.get_entity(opcoes_group_id)
    messages = await client.get_messages(entity, limit=None)  # TODAS
    
    opcoes_data = []
    for msg in messages:
        if msg.text:
            opcoes_data.append({
                'date': msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                'text': msg.text,
                'message_id': msg.id
            })
    
    with open('opcoes_messages_full.json', 'w', encoding='utf-8') as f:
        json.dump(opcoes_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(opcoes_data)} mensagens salvas em opcoes_messages_full.json")
    
    await client.disconnect()

asyncio.run(fetch_all())
