#!/usr/bin/env python3
import os, asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from datetime import datetime

load_dotenv()

async def enviar_tudo():
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
        print("❌ Grupo não encontrado")
        await client.disconnect()
        return
    
    print(f"✅ Grupo encontrado: {grupo.title}\n")
    
    # 1. Mensagem atualizada com arquivos
    msg_final = f"""✅ **Carteiras de Outubro enviadas!**

---

📄 **ARQUIVOS DISPONÍVEIS:**

1️⃣ **PDF Detalhado** (12 páginas)
• Análise fundamentalista de cada ativo
• Explicação do porquê de cada escolha
• Valores mínimos recomendados
• Como montar passo a passo

2️⃣ **Planilha Excel Interativa**
• Digite seu valor total a investir
• Cálculo automático de alocação
• 3 carteiras em abas separadas
• Pronto para usar!

---

💡 **COMO USAR A PLANILHA:**

1. Abra no Excel ou Google Sheets
2. Escolha a aba da sua carteira
3. Digite o valor total na célula amarela (B6)
4. Pronto! A planilha calcula tudo automaticamente

---

📊 **Monitoramento Ativo:**

Estou analisando o mercado continuamente:
• Opções: 3x ao dia (10:10, 14:00, 16:45)
• Ações/FIIs/Cripto: 1x ao dia (21:00)

Você só receberá mensagens quando houver **ação necessária**!

---

🤖 **Magnus está ON!**

Sistema de automação ativado. Bons investimentos! 🚀"""
    
    print("📱 Enviando mensagem...")
    await client.send_message(grupo, msg_final)
    print("✅ Mensagem enviada!\n")
    
    await asyncio.sleep(2)
    
    # 2. Enviar PDF
    print("📄 Enviando PDF...")
    await client.send_file(
        grupo, 
        'Carteiras_Magnus_Outubro_2025.pdf',
        caption="📊 **Análise Detalhada das Carteiras - Outubro/2025**\n\nAnálise fundamentalista completa de cada ativo!"
    )
    print("✅ PDF enviado!\n")
    
    await asyncio.sleep(2)
    
    # 3. Enviar Excel
    print("📊 Enviando Excel...")
    await client.send_file(
        grupo,
        'Carteiras_Magnus_Outubro_2025.xlsx',
        caption="📈 **Planilha Interativa - Calculadora de Alocação**\n\nDigite seu valor total e a planilha calcula automaticamente!"
    )
    print("✅ Excel enviado!\n")
    
    print("=" * 80)
    print("✅ TUDO ENVIADO COM SUCESSO!")
    print("=" * 80)
    
    await client.disconnect()

asyncio.run(enviar_tudo())
