import os, asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def main():
    client = TelegramClient('magnus_session', os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    
    print("🔐 Conectando ao Telegram...")
    await client.start(phone=os.getenv('TELEGRAM_PHONE'))
    
    print("✅ Sessão renovada com sucesso!")
    
    me = await client.get_me()
    print(f"👤 Logado como: {me.first_name}")
    
    await client.disconnect()

asyncio.run(main())
