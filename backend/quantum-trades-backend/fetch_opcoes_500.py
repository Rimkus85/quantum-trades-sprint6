import os, asyncio, json
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def main():
    client = TelegramClient('magnus_session', os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    await client.connect()
    
    entity = await client.get_entity(-1002018374487)
    print(f"Buscando mensagens de {entity.title}...")
    
    messages = await client.get_messages(entity, limit=500)
    
    data = [{'date': m.date.strftime('%Y-%m-%d %H:%M:%S'), 'text': m.text, 'message_id': m.id} 
            for m in messages if m.text]
    
    with open('opcoes_messages_500.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(data)} mensagens salvas")
    await client.disconnect()

asyncio.run(main())
