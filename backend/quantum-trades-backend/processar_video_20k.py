#!/usr/bin/env python3
"""
Processa vídeo sobre aposentadoria com 20k
"""

import yt_dlp
import os
import subprocess
import json

video_id = 'qWtUiE1OoY0'
url = f'https://www.youtube.com/watch?v={video_id}'

# 1. Baixar vídeo
print("📥 Baixando vídeo...")
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': f'youtube_downloads/{video_id}.%(ext)s',
    'quiet': False
}

os.makedirs('youtube_downloads', exist_ok=True)
os.makedirs('youtube_transcriptions', exist_ok=True)

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    title = info.get('title')
    duration = info.get('duration')
    print(f'✅ Baixado: {title}')
    print(f'⏱️  Duração: {duration}s ({duration/60:.1f} min)')

# 2. Transcrever
audio_file = f'youtube_downloads/{video_id}.mp3'
transcription_file = f'youtube_transcriptions/{video_id}.txt'

print("\n🎤 Transcrevendo áudio...")
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
    print(f'✅ Transcrição salva: {transcription_file}')
    print(f'📝 Palavras: {len(transcription.split())}')
    
    # Salvar conhecimento
    knowledge = {
        'video_id': video_id,
        'title': title,
        'url': url,
        'duration': duration,
        'transcription': transcription,
        'word_count': len(transcription.split())
    }
    
    with open(f'youtube_knowledge/{video_id}.json', 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ Conhecimento salvo!')
else:
    print(f'❌ Erro na transcrição: {result.stderr}')

