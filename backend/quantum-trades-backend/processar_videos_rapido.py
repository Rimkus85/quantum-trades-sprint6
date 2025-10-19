#!/usr/bin/env python3
"""
Processa vídeos de forma otimizada - SEM transcrição (muito lento)
Extrai apenas metadados e salva conhecimento básico
"""

import yt_dlp
import os
import json
import time

videos = [
    {'id': 'bM-oC4_tNQQ', 'titulo': 'CARTEIRA RECOMENDADA USA - OUTUBRO 2025'},
    {'id': 'dm8VlG4esYk', 'titulo': 'COMO GANHAR NA QUEDA NO MERCADO FINANCEIRO'},
    {'id': 'tGJhDjV2ks0', 'titulo': 'COMO COMPRAR UM ETF'},
    {'id': 'cOPtYvofIa4', 'titulo': 'CARTEIRA RECOMENDADA STARTMILIONÁRIO - 07/10/2025'},
    {'id': 'qWtUiE1OoY0', 'titulo': 'COMO SE APOSENTAR COM 20K MENSAL'},
    {'id': 'hTMnPP00EEs', 'titulo': 'TUTORIAL - COMO SURFAR TENDÊNCIAS COM AÇÕES'},
    {'id': 'UoL8yh1Vx0g', 'titulo': 'CARTEIRA RECOMENDADA STARTMILIONÁRIO (segunda)'},
    {'id': 'u4K6SiDImlw', 'titulo': 'CARTEIRA RECOMENDADA IFR - 16/09/2025'},
]

os.makedirs('youtube_knowledge', exist_ok=True)

print("="*70)
print("🚀 PROCESSAMENTO RÁPIDO DE VÍDEOS")
print("="*70)

for video in videos:
    video_id = video['id']
    titulo = video['titulo']
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    print(f"\n📹 {titulo}")
    
    # Verificar se já existe
    knowledge_file = f'youtube_knowledge/{video_id}.json'
    if os.path.exists(knowledge_file):
        print(f"   ✅ Já processado")
        continue
    
    try:
        # Extrair apenas metadados (SEM baixar)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extrair descrição e tags
            description = info.get('description', '')
            tags = info.get('tags', [])
            duration = info.get('duration', 0)
            view_count = info.get('view_count', 0)
            upload_date = info.get('upload_date', '')
            
            # Salvar conhecimento básico
            knowledge = {
                'video_id': video_id,
                'title': titulo,
                'url': url,
                'duration_seconds': duration,
                'duration_minutes': round(duration / 60, 1),
                'description': description[:500],  # Primeiros 500 chars
                'tags': tags,
                'view_count': view_count,
                'upload_date': upload_date,
                'processed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'has_transcription': False,
                'knowledge_source': 'metadata_only'
            }
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ Metadados salvos ({duration/60:.1f} min, {view_count:,} views)")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print(f"\n{'='*70}")
print(f"✅ PROCESSAMENTO CONCLUÍDO")
print(f"{'='*70}")

