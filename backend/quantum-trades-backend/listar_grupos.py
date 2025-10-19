#!/usr/bin/env python3
"""
Lista todos os grupos e canais do Telegram
"""

import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

# Carregar variáveis de ambiente
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
PASSWORD = os.getenv('TELEGRAM_PASSWORD')

async def listar_grupos():
    """Lista todos os grupos e canais"""
    
    client = TelegramClient('magnus_session', API_ID, API_HASH)
    
    await client.start(phone=PHONE, password=PASSWORD)
    
    print("=" * 70)
    print("GRUPOS E CANAIS DO TELEGRAM")
    print("=" * 70)
    
    dialogs = await client.get_dialogs()
    
    grupos = []
    canais = []
    
    for dialog in dialogs:
        if dialog.is_group:
            grupos.append(dialog)
        elif dialog.is_channel:
            canais.append(dialog)
    
    print(f"\n📊 GRUPOS ({len(grupos)}):")
    print("-" * 70)
    for i, grupo in enumerate(grupos, 1):
        print(f"{i}. {grupo.name}")
        print(f"   ID: {grupo.id}")
        print()
    
    print(f"\n📢 CANAIS ({len(canais)}):")
    print("-" * 70)
    for i, canal in enumerate(canais, 1):
        print(f"{i}. {canal.name}")
        print(f"   ID: {canal.id}")
        print()
    
    print("=" * 70)
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(listar_grupos())

