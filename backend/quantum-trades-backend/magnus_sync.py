#!/usr/bin/env python3
"""
Sistema de Sincronização Automática do Magnus.
Processa carteiras e vídeos do Telegram automaticamente.
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Adicionar diretório ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from modules.xlsx_processor import XLSXProcessor
from modules.carteira_integrator import CarteiraIntegrator
from modules.youtube_extractor import YouTubeExtractor
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


class MagnusSync:
    """Sistema de sincronização automática."""
    
    def __init__(self):
        """Inicializa o sistema."""
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.carteiras_group_id = int(os.getenv('TELEGRAM_GROUP_ID'))
        self.opcoes_group_id = -1002018374487  # [NOVA SALA DE OPÇÕES]
        
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'carteiras': {},
            'videos': {},
            'opcoes': {},
            'errors': []
        }
    
    async def sync_all(self):
        """Sincroniza todos os dados."""
        print("=" * 80)
        print("MAGNUS SYNC - SINCRONIZAÇÃO AUTOMÁTICA")
        print("=" * 80)
        print(f"\nIniciado em: {self.stats['start_time']}")
        
        # 1. Baixar arquivos XLSX
        await self._sync_carteiras_xlsx()
        
        # 2. Processar e integrar carteiras
        self._process_carteiras()
        
        # 3. Extrair vídeos
        await self._sync_videos()
        
        # 4. Processar opções (futuro)
        await self._sync_opcoes()
        
        # 5. Gerar relatório
        self._generate_report()
        
        print("\n" + "=" * 80)
        print("✅ SINCRONIZAÇÃO CONCLUÍDA")
        print("=" * 80)
    
    async def _sync_carteiras_xlsx(self):
        """Sincroniza arquivos XLSX de carteiras."""
        print("\n" + "=" * 80)
        print("1. SINCRONIZANDO CARTEIRAS XLSX")
        print("=" * 80)
        
        try:
            client = TelegramClient('magnus_session', self.api_id, self.api_hash)
            await client.connect()
            
            entity = await client.get_entity(self.carteiras_group_id)
            print(f"\n✓ Grupo: {entity.title}")
            
            # Criar diretório
            download_dir = 'downloads/carteiras'
            os.makedirs(download_dir, exist_ok=True)
            
            # Buscar mensagens
            print(f"\n⏳ Buscando arquivos XLSX...")
            messages = await client.get_messages(entity, limit=200)
            
            xlsx_files = []
            for msg in messages:
                if msg.document:
                    filename = None
                    for attr in msg.document.attributes:
                        if hasattr(attr, 'file_name'):
                            filename = attr.file_name
                            break
                    
                    if filename and (filename.endswith('.xlsx') or filename.endswith('.xls')):
                        date = msg.date.strftime("%Y-%m-%d")
                        safe_filename = f"{date}_{filename}"
                        filepath = os.path.join(download_dir, safe_filename)
                        
                        if not os.path.exists(filepath):
                            print(f"\n📥 Baixando: {filename}")
                            await client.download_media(msg.document, filepath)
                            xlsx_files.append(safe_filename)
            
            self.stats['carteiras']['files_downloaded'] = len(xlsx_files)
            print(f"\n✅ {len(xlsx_files)} novos arquivos baixados")
            
            await client.disconnect()
            
        except Exception as e:
            error = f"Erro ao sincronizar XLSX: {e}"
            print(f"\n❌ {error}")
            self.stats['errors'].append(error)
    
    def _process_carteiras(self):
        """Processa carteiras e integra ao Magnus."""
        print("\n" + "=" * 80)
        print("2. PROCESSANDO CARTEIRAS")
        print("=" * 80)
        
        try:
            integrator = CarteiraIntegrator()
            stats = integrator.process_and_integrate()
            
            self.stats['carteiras'].update(stats)
            
        except Exception as e:
            error = f"Erro ao processar carteiras: {e}"
            print(f"\n❌ {error}")
            self.stats['errors'].append(error)
    
    async def _sync_videos(self):
        """Sincroniza vídeos do YouTube."""
        print("\n" + "=" * 80)
        print("3. SINCRONIZANDO VÍDEOS DO YOUTUBE")
        print("=" * 80)
        
        try:
            extractor = YouTubeExtractor()
            videos = await extractor.extract_videos(limit=200)
            extractor.save_to_json()
            
            self.stats['videos']['total'] = len(videos)
            self.stats['videos']['ids'] = len(extractor.get_video_ids())
            
        except Exception as e:
            error = f"Erro ao sincronizar vídeos: {e}"
            print(f"\n❌ {error}")
            self.stats['errors'].append(error)
    
    async def _sync_opcoes(self):
        """Sincroniza sala de opções."""
        print("\n" + "=" * 80)
        print("4. SINCRONIZANDO SALA DE OPÇÕES")
        print("=" * 80)
        
        try:
            client = TelegramClient('magnus_session', self.api_id, self.api_hash)
            await client.connect()
            
            entity = await client.get_entity(self.opcoes_group_id)
            print(f"\n✓ Grupo: {entity.title}")
            
            # Ler mensagens
            print(f"\n⏳ Lendo mensagens...")
            messages = await client.get_messages(entity, limit=50)
            
            opcoes_data = []
            for msg in messages:
                if msg.text:
                    opcoes_data.append({
                        'date': msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                        'text': msg.text[:200]  # Primeiros 200 caracteres
                    })
            
            # Salvar
            with open('opcoes_messages.json', 'w', encoding='utf-8') as f:
                json.dump(opcoes_data, f, ensure_ascii=False, indent=2)
            
            self.stats['opcoes']['messages'] = len(opcoes_data)
            print(f"\n✅ {len(opcoes_data)} mensagens lidas")
            
            await client.disconnect()
            
        except Exception as e:
            error = f"Erro ao sincronizar opções: {e}"
            print(f"\n❌ {error}")
            self.stats['errors'].append(error)
    
    def _generate_report(self):
        """Gera relatório da sincronização."""
        self.stats['end_time'] = datetime.now().isoformat()
        
        # Salvar relatório
        with open('sync_report.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO DE SINCRONIZAÇÃO")
        print("=" * 80)
        
        print(f"\n⏱ Horário: {self.stats['start_time']} → {self.stats['end_time']}")
        
        print(f"\n📊 CARTEIRAS:")
        for key, value in self.stats['carteiras'].items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for k, v in value.items():
                    print(f"     {k}: {v}")
            else:
                print(f"   {key}: {value}")
        
        print(f"\n🎥 VÍDEOS:")
        for key, value in self.stats['videos'].items():
            print(f"   {key}: {value}")
        
        print(f"\n📈 OPÇÕES:")
        for key, value in self.stats['opcoes'].items():
            print(f"   {key}: {value}")
        
        if self.stats['errors']:
            print(f"\n⚠ ERROS ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"   - {error}")
        
        print(f"\n✓ Relatório salvo em: sync_report.json")


async def main():
    """Função principal."""
    sync = MagnusSync()
    await sync.sync_all()


if __name__ == '__main__':
    asyncio.run(main())

