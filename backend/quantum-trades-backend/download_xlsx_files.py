#!/usr/bin/env python3
"""
Baixa arquivos XLSX do grupo Carteira Recomendada
"""
import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from datetime import datetime

load_dotenv()

async def download_xlsx():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    group_id = int(os.getenv('TELEGRAM_GROUP_ID'))
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("=" * 80)
    print("BAIXANDO ARQUIVOS XLSX - Carteira Recomendada")
    print("=" * 80)
    
    # Criar diretório para downloads
    download_dir = 'downloads/carteiras'
    os.makedirs(download_dir, exist_ok=True)
    
    try:
        entity = await client.get_entity(group_id)
        print(f"\n✓ Grupo: {entity.title}")
        
        # Ler mensagens (vamos buscar mais para encontrar arquivos)
        print(f"\n⏳ Buscando mensagens com arquivos...")
        messages = await client.get_messages(entity, limit=200)
        
        xlsx_files = []
        
        for msg in messages:
            if msg.document:
                # Verificar se é XLSX
                filename = None
                for attr in msg.document.attributes:
                    if hasattr(attr, 'file_name'):
                        filename = attr.file_name
                        break
                
                if filename and (filename.endswith('.xlsx') or filename.endswith('.xls')):
                    xlsx_files.append({
                        'message': msg,
                        'filename': filename,
                        'date': msg.date,
                        'size': msg.document.size
                    })
        
        print(f"\n✅ Encontrados {len(xlsx_files)} arquivos XLSX\n")
        print("=" * 80)
        
        if not xlsx_files:
            print("\n⚠ Nenhum arquivo XLSX encontrado nas últimas 200 mensagens")
            print("   As carteiras podem estar em:")
            print("   - Mensagens mais antigas")
            print("   - Formato diferente (PDF, imagens)")
            print("   - Links externos")
            return
        
        # Baixar arquivos
        for i, file_info in enumerate(xlsx_files, 1):
            msg = file_info['message']
            filename = file_info['filename']
            date = file_info['date'].strftime("%Y-%m-%d")
            size_mb = file_info['size'] / (1024 * 1024)
            
            print(f"\n📥 {i}/{len(xlsx_files)}: {filename}")
            print(f"   Data: {date}")
            print(f"   Tamanho: {size_mb:.2f} MB")
            
            # Nome do arquivo com data
            safe_filename = f"{date}_{filename}"
            filepath = os.path.join(download_dir, safe_filename)
            
            if os.path.exists(filepath):
                print(f"   ⏭ Já existe, pulando...")
                continue
            
            print(f"   ⏳ Baixando...")
            await client.download_media(msg.document, filepath)
            print(f"   ✓ Salvo em: {filepath}")
        
        print("\n" + "=" * 80)
        print(f"✅ DOWNLOAD CONCLUÍDO")
        print(f"   Total de arquivos: {len(xlsx_files)}")
        print(f"   Diretório: {download_dir}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(download_xlsx())
