#!/usr/bin/env python3
"""
Processa TODOS os vídeos do YouTube identificados
"""

import yt_dlp
import os
import subprocess
import json
import time

# Lista de vídeos do resumo
videos = [
    {'id': 'bM-oC4_tNQQ', 'titulo': 'CARTEIRA RECOMENDADA USA - OUTUBRO 2025', 'duracao': '8min 7s'},
    {'id': 'dm8VlG4esYk', 'titulo': 'COMO GANHAR NA QUEDA NO MERCADO FINANCEIRO', 'duracao': '12min 26s'},
    {'id': 'tGJhDjV2ks0', 'titulo': 'COMO COMPRAR UM ETF', 'duracao': '16min 58s'},
    {'id': 'cOPtYvofIa4', 'titulo': 'CARTEIRA RECOMENDADA STARTMILIONÁRIO - 07/10/2025', 'duracao': '9min 48s'},
    {'id': 'qWtUiE1OoY0', 'titulo': 'COMO SE APOSENTAR COM 20K MENSAL', 'duracao': '17min 59s'},
    {'id': 'hTMnPP00EEs', 'titulo': 'TUTORIAL - COMO SURFAR TENDÊNCIAS COM AÇÕES', 'duracao': '14min 38s'},
    {'id': 'UoL8yh1Vx0g', 'titulo': 'CARTEIRA RECOMENDADA STARTMILIONÁRIO (segunda)', 'duracao': '16min 53s'},
    {'id': 'u4K6SiDImlw', 'titulo': 'CARTEIRA RECOMENDADA IFR - 16/09/2025', 'duracao': '4min 55s'},
]

os.makedirs('youtube_downloads', exist_ok=True)
os.makedirs('youtube_transcriptions', exist_ok=True)
os.makedirs('youtube_knowledge', exist_ok=True)

processados = 0
erros = 0

for video in videos:
    video_id = video['id']
    titulo = video['titulo']
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    print(f"\n{'='*70}")
    print(f"📹 Processando: {titulo}")
    print(f"🆔 ID: {video_id}")
    print(f"{'='*70}")
    
    # Verificar se já foi processado
    knowledge_file = f'youtube_knowledge/{video_id}.json'
    if os.path.exists(knowledge_file):
        print(f"✅ Já processado anteriormente. Pulando...")
        processados += 1
        continue
    
    try:
        # 1. Baixar vídeo
        audio_file = f'youtube_downloads/{video_id}.mp3'
        
        if not os.path.exists(audio_file):
            print("📥 Baixando áudio...")
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'youtube_downloads/{video_id}.%(ext)s',
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                duration = info.get('duration')
                print(f"✅ Baixado! Duração: {duration}s ({duration/60:.1f} min)")
        else:
            print(f"✅ Áudio já existe")
        
        # 2. Transcrever
        transcription_file = f'youtube_transcriptions/{video_id}.txt'
        
        if not os.path.exists(transcription_file):
            print("🎤 Transcrevendo áudio...")
            result = subprocess.run(
                ['manus-speech-to-text', audio_file],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                transcription = result.stdout
                with open(transcription_file, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"✅ Transcrição salva!")
                print(f"📝 Palavras: {len(transcription.split())}")
            else:
                print(f"❌ Erro na transcrição: {result.stderr}")
                erros += 1
                continue
        else:
            print(f"✅ Transcrição já existe")
            with open(transcription_file, 'r', encoding='utf-8') as f:
                transcription = f.read()
        
        # 3. Salvar conhecimento
        knowledge = {
            'video_id': video_id,
            'title': titulo,
            'url': url,
            'transcription': transcription,
            'word_count': len(transcription.split()),
            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Conhecimento salvo em {knowledge_file}")
        processados += 1
        
        # Delay entre vídeos
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        erros += 1
        continue

print(f"\n{'='*70}")
print(f"📊 RESUMO DO PROCESSAMENTO")
print(f"{'='*70}")
print(f"✅ Processados com sucesso: {processados}/{len(videos)}")
print(f"❌ Erros: {erros}")
print(f"{'='*70}")

