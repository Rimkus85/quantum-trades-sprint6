#!/usr/bin/env python3
"""
Processador Automático de Novos Vídeos
Processa apenas vídeos do YouTube que ainda não foram processados
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import re

class NewVideoProcessor:
    """Processa automaticamente novos vídeos do Telegram"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.knowledge_dir = self.base_dir / 'youtube_knowledge'
        self.youtube_links_file = self.base_dir / 'youtube_links.txt'
        self.summary_file = self.knowledge_dir / 'summary.json'
        self.knowledge_base_file = self.knowledge_dir / 'magnus_knowledge_base.json'
        
        # Criar diretório se não existir
        self.knowledge_dir.mkdir(exist_ok=True)
    
    def load_processed_videos(self) -> Set[str]:
        """Carrega lista de vídeos já processados"""
        processed = set()
        
        if self.summary_file.exists():
            with open(self.summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
                for video in summary.get('videos', []):
                    video_id = video.get('video_id')
                    if video_id:
                        processed.add(video_id)
        
        return processed
    
    def extract_video_id(self, url: str) -> str:
        """Extrai ID do vídeo da URL do YouTube"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/live\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def load_youtube_links(self) -> List[str]:
        """Carrega links do YouTube do arquivo"""
        if not self.youtube_links_file.exists():
            print(f"❌ Arquivo não encontrado: {self.youtube_links_file}")
            return []
        
        with open(self.youtube_links_file, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
        
        return links
    
    def get_new_videos(self) -> List[Dict[str, str]]:
        """Identifica vídeos novos que ainda não foram processados"""
        all_links = self.load_youtube_links()
        processed_ids = self.load_processed_videos()
        
        new_videos = []
        
        for url in all_links:
            video_id = self.extract_video_id(url)
            
            if video_id and video_id not in processed_ids:
                new_videos.append({
                    'video_id': video_id,
                    'url': url
                })
        
        return new_videos
    
    def process_video(self, video: Dict[str, str]) -> bool:
        """
        Processa um único vídeo
        
        Returns:
            True se processado com sucesso, False caso contrário
        """
        video_id = video['video_id']
        url = video['url']
        
        print(f"\n{'='*60}")
        print(f"🎬 Processando: {video_id}")
        print(f"{'='*60}")
        
        try:
            # 1. Obter informações do vídeo
            print("1️⃣ Obtendo informações...")
            info_cmd = f'yt-dlp --dump-json --no-download "{url}"'
            info_result = subprocess.run(
                info_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if info_result.returncode != 0:
                print(f"❌ Erro ao obter informações")
                return False
            
            video_info = json.loads(info_result.stdout)
            title = video_info.get('title', 'Unknown')
            duration = video_info.get('duration', 0)
            
            print(f"✅ Título: {title}")
            print(f"   Duração: {duration//60}min {duration%60}s")
            
            # Pular vídeos muito longos (mais de 60 minutos)
            if duration > 3600:
                print(f"⏭️ Vídeo muito longo ({duration//60}min), pulando...")
                return False
            
            # 2. Baixar áudio
            print("2️⃣ Baixando áudio...")
            audio_file = self.base_dir / f"{video_id}.mp3"
            
            download_cmd = f'yt-dlp -x --audio-format mp3 -o "{audio_file}" "{url}"'
            download_result = subprocess.run(
                download_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if download_result.returncode != 0 or not audio_file.exists():
                print(f"❌ Erro ao baixar áudio")
                return False
            
            print(f"✅ Áudio baixado: {audio_file.name}")
            
            # 3. Transcrever
            print("3️⃣ Transcrevendo áudio...")
            transcribe_cmd = f'manus-speech-to-text "{audio_file}"'
            transcribe_result = subprocess.run(
                transcribe_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if transcribe_result.returncode != 0:
                print(f"❌ Erro ao transcrever")
                # Limpar arquivo de áudio
                if audio_file.exists():
                    audio_file.unlink()
                return False
            
            transcription = transcribe_result.stdout
            print(f"✅ Transcrição concluída: {len(transcription)} caracteres")
            
            # 4. Extrair conhecimento
            print("4️⃣ Extraindo conhecimento...")
            
            # Keywords de investimento
            keywords = [
                'ação', 'ações', 'opção', 'opções', 'call', 'put',
                'carteira', 'portfolio', 'diversificação',
                'risco', 'retorno', 'lucro', 'prejuízo',
                'fibonacci', 'suporte', 'resistência', 'tendência',
                'stop', 'gain', 'loss', 'indicador',
                'dividendo', 'provento', 'jscp',
                'valuation', 'ebitda', 'receita',
                'ibovespa', 'sp500', 'nasdaq',
                'etf', 'fii', 'reit'
            ]
            
            transcription_lower = transcription.lower()
            word_count = len(transcription.split())
            keyword_count = sum(1 for kw in keywords if kw in transcription_lower)
            relevance = min(keyword_count / 10, 1.0)  # Max 100%
            
            print(f"✅ Conhecimento extraído")
            print(f"   Palavras: {word_count:,}")
            print(f"   Relevância: {relevance:.1%}")
            print(f"   Keywords: {keyword_count}")
            
            # 5. Salvar dados
            video_data = {
                'video_id': video_id,
                'title': title,
                'channel': video_info.get('channel', 'Unknown'),
                'duration': duration,
                'upload_date': video_info.get('upload_date', ''),
                'description': video_info.get('description', ''),
                'transcription': transcription,
                'relevance_score': relevance,
                'keyword_count': keyword_count,
                'processed_at': datetime.now().isoformat(),
                'word_count': word_count
            }
            
            video_file = self.knowledge_dir / f"{video_id}.json"
            with open(video_file, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Dados salvos: {video_file.name}")
            
            # Limpar arquivo de áudio
            if audio_file.exists():
                audio_file.unlink()
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"⏱️ Timeout ao processar vídeo")
            return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    
    def update_summary(self):
        """Atualiza arquivo de resumo com todos os vídeos processados"""
        print("\n📊 Atualizando resumo...")
        
        videos = []
        total_words = 0
        total_relevance = 0
        
        # Carregar todos os vídeos processados
        for video_file in self.knowledge_dir.glob('*.json'):
            if video_file.name in ['summary.json', 'magnus_knowledge_base.json']:
                continue
            
            with open(video_file, 'r', encoding='utf-8') as f:
                video_data = json.load(f)
                videos.append(video_data)
                total_words += video_data.get('word_count', 0)
                total_relevance += video_data.get('relevance_score', 0)
        
        # Ordenar por relevância
        videos.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        avg_relevance = total_relevance / len(videos) if videos else 0
        
        summary = {
            'total_videos': len(videos),
            'total_errors': 0,  # Não rastreamos erros neste script
            'processed_at': datetime.now().isoformat(),
            'average_relevance': avg_relevance,
            'total_words': total_words,
            'videos': videos
        }
        
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Resumo atualizado: {len(videos)} vídeos")
    
    def update_knowledge_base(self):
        """Atualiza base de conhecimento do Magnus"""
        print("\n🧠 Atualizando base de conhecimento...")
        
        try:
            # Executar integrador
            integrator_path = self.base_dir / 'modules' / 'video_knowledge_integrator.py'
            
            if integrator_path.exists():
                result = subprocess.run(
                    ['python3', str(integrator_path)],
                    cwd=str(self.base_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅ Base de conhecimento atualizada")
                else:
                    print(f"⚠️ Aviso ao atualizar base: {result.stderr}")
            else:
                print(f"⚠️ Integrador não encontrado: {integrator_path}")
                
        except Exception as e:
            print(f"⚠️ Erro ao atualizar base: {str(e)}")
    
    def run(self):
        """Executa processamento de novos vídeos"""
        print("="*60)
        print("🤖 Magnus - Processador Automático de Novos Vídeos")
        print("="*60)
        print()
        
        # Identificar novos vídeos
        new_videos = self.get_new_videos()
        
        if not new_videos:
            print("✅ Nenhum vídeo novo para processar")
            print("   Todos os vídeos já foram processados!")
            return
        
        print(f"📹 Encontrados {len(new_videos)} novos vídeos para processar")
        print()
        
        # Processar cada vídeo
        success_count = 0
        error_count = 0
        
        for i, video in enumerate(new_videos, 1):
            print(f"\n[{i}/{len(new_videos)}] Processando vídeo...")
            
            if self.process_video(video):
                success_count += 1
            else:
                error_count += 1
        
        # Atualizar resumo e base de conhecimento
        if success_count > 0:
            self.update_summary()
            self.update_knowledge_base()
        
        # Resumo final
        print("\n" + "="*60)
        print("📊 RESUMO DO PROCESSAMENTO")
        print("="*60)
        print(f"✅ Processados com sucesso: {success_count}")
        print(f"❌ Erros: {error_count}")
        print(f"📊 Total de vídeos novos: {len(new_videos)}")
        print("="*60)
        print()
        
        if success_count > 0:
            print("✅ Base de conhecimento atualizada!")
            print(f"   Localização: {self.knowledge_base_file}")
        
        print("\n🎉 Processamento concluído!")


if __name__ == "__main__":
    processor = NewVideoProcessor()
    processor.run()

