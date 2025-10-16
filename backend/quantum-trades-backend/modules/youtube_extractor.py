"""
Extrator de URLs de vídeos do YouTube do Telegram.
"""

import os
import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


class YouTubeExtractor:
    """Extrai URLs de vídeos do YouTube do Telegram."""
    
    def __init__(self):
        """Inicializa o extrator."""
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.group_id = int(os.getenv('TELEGRAM_GROUP_ID'))
        self.client = None
        self.videos = []
    
    async def extract_videos(self, limit: int = 100) -> List[Dict]:
        """
        Extrai URLs de vídeos do YouTube.
        
        Args:
            limit: Número de mensagens a processar
            
        Returns:
            Lista de vídeos encontrados
        """
        print("=" * 80)
        print("EXTRAÇÃO DE VÍDEOS DO YOUTUBE")
        print("=" * 80)
        
        self.client = TelegramClient('magnus_session', self.api_id, self.api_hash)
        await self.client.connect()
        
        try:
            # Obter entidade do grupo
            entity = await self.client.get_entity(self.group_id)
            print(f"\n✓ Grupo: {entity.title}")
            
            # Ler mensagens
            print(f"\n⏳ Lendo últimas {limit} mensagens...")
            messages = await self.client.get_messages(entity, limit=limit)
            
            # Extrair URLs
            youtube_pattern = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/live/)[^\s]+)'
            
            for msg in messages:
                if msg.text:
                    urls = re.findall(youtube_pattern, msg.text)
                    for url in urls:
                        # Limpar URL
                        url = url.split('?')[0] if '?' in url and 'v=' not in url else url
                        
                        video = {
                            'url': url,
                            'date': msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                            'message_id': msg.id,
                            'extracted_at': datetime.now().isoformat()
                        }
                        
                        self.videos.append(video)
            
            # Remover duplicatas
            unique_videos = []
            seen_urls = set()
            for video in self.videos:
                if video['url'] not in seen_urls:
                    unique_videos.append(video)
                    seen_urls.add(video['url'])
            
            self.videos = unique_videos
            
            print(f"\n✅ {len(self.videos)} vídeos únicos encontrados")
            
            # Mostrar últimos 10
            print(f"\n📹 ÚLTIMOS 10 VÍDEOS:")
            for i, video in enumerate(self.videos[:10], 1):
                print(f"\n  {i}. {video['date']}")
                print(f"     {video['url']}")
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await self.client.disconnect()
        
        return self.videos
    
    def save_to_json(self, output_file: str = 'youtube_videos.json'):
        """
        Salva vídeos em JSON.
        
        Args:
            output_file: Arquivo de saída
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.videos, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Vídeos salvos em: {output_file}")
    
    def get_video_ids(self) -> List[str]:
        """
        Extrai IDs dos vídeos do YouTube.
        
        Returns:
            Lista de IDs
        """
        ids = []
        for video in self.videos:
            url = video['url']
            
            # Extrair ID
            if 'v=' in url:
                video_id = url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[1].split('?')[0]
            elif '/live/' in url:
                video_id = url.split('/live/')[1].split('?')[0]
            else:
                continue
            
            ids.append(video_id)
        
        return ids


async def main():
    """Função principal."""
    extractor = YouTubeExtractor()
    
    # Extrair vídeos
    videos = await extractor.extract_videos(limit=200)
    
    # Salvar
    extractor.save_to_json()
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de vídeos: {len(videos)}")
    
    # IDs
    ids = extractor.get_video_ids()
    print(f"   IDs extraídos: {len(ids)}")
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO CONCLUÍDA")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())

