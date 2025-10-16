import os, asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def main():
    client = TelegramClient('magnus_session', os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    await client.connect()
    
    # Encontrar grupo
    dialogs = await client.get_dialogs()
    grupo = None
    for d in dialogs:
        if 'Magnus Wealth' in d.title:
            grupo = d
            break
    
    if not grupo:
        print("Grupo não encontrado")
        await client.disconnect()
        return
    
    print(f"Grupo: {grupo.title}\n")
    print("=" * 80)
    print("ÚLTIMAS MENSAGENS:")
    print("=" * 80)
    
    messages = await client.get_messages(grupo, limit=20)
    
    for msg in reversed(messages):
        if msg.text:
            sender = "Magnus" if msg.out else msg.sender_id
            print(f"\n[{msg.date.strftime('%H:%M:%S')}] {sender}:")
            print(msg.text[:200])
            if len(msg.text) > 200:
                print("...")
    
    await client.disconnect()

asyncio.run(main())
