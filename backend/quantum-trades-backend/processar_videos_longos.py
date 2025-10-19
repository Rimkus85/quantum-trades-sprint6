#!/usr/bin/env python3
"""
Script melhorado para processar vídeos longos do Tio Huli
Suporta vídeos de qualquer duração, com processamento em chunks
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent
VIDEOS_DIR = BASE_DIR / "youtube_videos"
TRANSCRIPTIONS_DIR = BASE_DIR / "youtube_transcriptions"
KNOWLEDGE_DIR = BASE_DIR / "youtube_knowledge"
PROGRESS_FILE = BASE_DIR / "video_processing_progress.json"

# Criar diretórios
VIDEOS_DIR.mkdir(exist_ok=True)
TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)
KNOWLEDGE_DIR.mkdir(exist_ok=True)

def load_progress():
    """Carrega progresso de processamento"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    """Salva progresso de processamento"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def download_video(url, video_id):
    """Baixa vídeo do YouTube ou plataforma"""
    print(f"\n📥 Baixando vídeo: {video_id}")
    
    output_path = VIDEOS_DIR / f"{video_id}.mp4"
    
    if output_path.exists():
        print(f"✅ Vídeo já existe: {output_path}")
        return str(output_path)
    
    try:
        # Tentar com yt-dlp primeiro (suporta mais plataformas)
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(VIDEOS_DIR / f"{video_id}.%(ext)s"),
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            # Procurar arquivo baixado (pode ser .mp3, .m4a, etc)
            for ext in ['.mp3', '.m4a', '.webm', '.mp4']:
                audio_file = VIDEOS_DIR / f"{video_id}{ext}"
                if audio_file.exists():
                    print(f"✅ Vídeo baixado: {audio_file}")
                    return str(audio_file)
        
        print(f"❌ Erro ao baixar: {result.stderr}")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout ao baixar vídeo")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def split_audio(audio_file, chunk_duration=600):
    """
    Divide áudio em chunks de N segundos (padrão: 10 minutos)
    Retorna lista de caminhos dos chunks
    """
    print(f"\n✂️ Dividindo áudio em chunks de {chunk_duration}s...")
    
    base_name = Path(audio_file).stem
    chunks_dir = VIDEOS_DIR / f"{base_name}_chunks"
    chunks_dir.mkdir(exist_ok=True)
    
    # Usar ffmpeg para dividir
    try:
        # Primeiro, descobrir duração total
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_file
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        total_duration = float(result.stdout.strip())
        
        print(f"📊 Duração total: {total_duration:.0f}s ({total_duration/60:.1f} min)")
        
        # Dividir em chunks
        chunks = []
        chunk_num = 0
        start_time = 0
        
        while start_time < total_duration:
            chunk_file = chunks_dir / f"chunk_{chunk_num:03d}.mp3"
            
            if not chunk_file.exists():
                cmd = [
                    "ffmpeg",
                    "-i", audio_file,
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-acodec", "libmp3lame",
                    "-ar", "16000",  # 16kHz (suficiente para voz)
                    "-ac", "1",  # Mono
                    "-y",
                    str(chunk_file)
                ]
                
                subprocess.run(cmd, capture_output=True, timeout=120)
            
            if chunk_file.exists():
                chunks.append(str(chunk_file))
                print(f"  ✅ Chunk {chunk_num}: {start_time:.0f}s - {start_time+chunk_duration:.0f}s")
            
            chunk_num += 1
            start_time += chunk_duration
        
        print(f"✅ {len(chunks)} chunks criados")
        return chunks
        
    except Exception as e:
        print(f"❌ Erro ao dividir áudio: {e}")
        return [audio_file]  # Retorna arquivo original se falhar

def transcribe_chunk(chunk_file, chunk_num):
    """Transcreve um chunk de áudio"""
    print(f"  🎤 Transcrevendo chunk {chunk_num}...")
    
    try:
        result = subprocess.run(
            ["manus-speech-to-text", chunk_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos por chunk
        )
        
        if result.returncode == 0:
            # Extrair texto da saída
            output = result.stdout
            if "Transcrição:" in output:
                text = output.split("Transcrição:")[1].strip()
                return text
            return output.strip()
        else:
            print(f"    ⚠️ Erro na transcrição: {result.stderr}")
            return ""
            
    except subprocess.TimeoutExpired:
        print(f"    ⏱️ Timeout no chunk {chunk_num}")
        return ""
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return ""

def transcribe_video(audio_file, video_id):
    """Transcreve vídeo completo (dividindo em chunks se necessário)"""
    print(f"\n🎤 Transcrevendo vídeo: {video_id}")
    
    transcription_file = TRANSCRIPTIONS_DIR / f"{video_id}.txt"
    
    if transcription_file.exists():
        print(f"✅ Transcrição já existe: {transcription_file}")
        return str(transcription_file)
    
    # Dividir em chunks
    chunks = split_audio(audio_file, chunk_duration=600)  # 10 minutos por chunk
    
    # Transcrever cada chunk
    full_transcription = []
    
    for i, chunk in enumerate(chunks):
        text = transcribe_chunk(chunk, i)
        if text:
            full_transcription.append(text)
        
        # Pequena pausa entre chunks
        time.sleep(2)
    
    # Juntar tudo
    final_text = "\n\n".join(full_transcription)
    
    # Salvar
    with open(transcription_file, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"✅ Transcrição salva: {transcription_file}")
    print(f"📊 Total de palavras: {len(final_text.split())}")
    
    return str(transcription_file)

def extract_knowledge(transcription_file, video_id, video_title):
    """Extrai conhecimento da transcrição"""
    print(f"\n🧠 Extraindo conhecimento: {video_id}")
    
    knowledge_file = KNOWLEDGE_DIR / f"{video_id}.json"
    
    if knowledge_file.exists():
        print(f"✅ Conhecimento já existe: {knowledge_file}")
        return str(knowledge_file)
    
    # Ler transcrição
    with open(transcription_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Extrair conceitos-chave (análise simples)
    knowledge = {
        "video_id": video_id,
        "titulo": video_title,
        "palavras_chave": extract_keywords(text),
        "conceitos": extract_concepts(text),
        "estrategias": extract_strategies(text),
        "tickers_mencionados": extract_tickers(text),
        "transcricao_completa": text,
        "total_palavras": len(text.split())
    }
    
    # Salvar
    with open(knowledge_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Conhecimento extraído: {knowledge_file}")
    
    return str(knowledge_file)

def extract_keywords(text):
    """Extrai palavras-chave do texto"""
    keywords = []
    
    # Palavras-chave de opções
    opcoes_keywords = ["call", "put", "strike", "vencimento", "prêmio", "opções", "exercício"]
    
    # Palavras-chave de cripto
    cripto_keywords = ["bitcoin", "btc", "ethereum", "eth", "binance", "cripto", "blockchain", "altcoin"]
    
    # Palavras-chave de estratégias
    estrategia_keywords = ["estratégia", "setup", "entrada", "saída", "stop", "alvo", "risco", "retorno"]
    
    text_lower = text.lower()
    
    for keyword in opcoes_keywords + cripto_keywords + estrategia_keywords:
        if keyword in text_lower:
            keywords.append(keyword)
    
    return list(set(keywords))

def extract_concepts(text):
    """Extrai conceitos principais"""
    concepts = []
    
    # Buscar por padrões de conceitos
    if "análise técnica" in text.lower():
        concepts.append("Análise Técnica")
    if "análise fundamentalista" in text.lower():
        concepts.append("Análise Fundamentalista")
    if "gestão de risco" in text.lower():
        concepts.append("Gestão de Risco")
    if "diversificação" in text.lower():
        concepts.append("Diversificação")
    
    return concepts

def extract_strategies(text):
    """Extrai estratégias mencionadas"""
    strategies = []
    
    # Padrões de estratégias
    if "buy and hold" in text.lower():
        strategies.append("Buy and Hold")
    if "swing trade" in text.lower():
        strategies.append("Swing Trade")
    if "day trade" in text.lower():
        strategies.append("Day Trade")
    if "dollar cost averaging" in text.lower() or "dca" in text.lower():
        strategies.append("Dollar Cost Averaging (DCA)")
    
    return strategies

def extract_tickers(text):
    """Extrai tickers mencionados"""
    import re
    
    # Padrão para ações brasileiras (XXXX3, XXXX4, etc)
    br_pattern = r'\b[A-Z]{4}[0-9]{1,2}\b'
    
    # Padrão para criptos
    crypto_pattern = r'\b(BTC|ETH|SOL|ADA|BNB|USDT|USDC|XRP|DOT|LINK|UNI|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|VET|SAND|MANA|GALA|ENJ|AXS|ICP|FIL|AAVE|COMP|SNX|CRV|YFI|SUSHI|BAL|UMA|REN|LRC|ZRX|BAT|KNC|BAND|STORJ|RUNE|LUNA|FLOW|EGLD|ONE|ALICE|TLM|SXP|DYDX|IMX|GMT|APE|OP|ARB|BLUR|PEPE|FLOKI|SHIB|DOGE)\b'
    
    tickers = []
    
    # Buscar ações BR
    br_matches = re.findall(br_pattern, text)
    tickers.extend(br_matches)
    
    # Buscar criptos
    crypto_matches = re.findall(crypto_pattern, text, re.IGNORECASE)
    tickers.extend([c.upper() for c in crypto_matches])
    
    return list(set(tickers))

def process_video(url, video_id, video_title):
    """Processa um vídeo completo"""
    print(f"\n{'='*80}")
    print(f"🎬 PROCESSANDO: {video_title}")
    print(f"{'='*80}")
    
    # Verificar progresso
    progress = load_progress()
    
    if video_id in progress and progress[video_id].get('status') == 'completed':
        print(f"✅ Vídeo já processado anteriormente")
        return progress[video_id]
    
    # Atualizar progresso
    progress[video_id] = {
        'titulo': video_title,
        'url': url,
        'status': 'processing',
        'inicio': time.time()
    }
    save_progress(progress)
    
    try:
        # 1. Download
        audio_file = download_video(url, video_id)
        if not audio_file:
            raise Exception("Falha no download")
        
        progress[video_id]['audio_file'] = audio_file
        save_progress(progress)
        
        # 2. Transcrição
        transcription_file = transcribe_video(audio_file, video_id)
        if not transcription_file:
            raise Exception("Falha na transcrição")
        
        progress[video_id]['transcription_file'] = transcription_file
        save_progress(progress)
        
        # 3. Extração de conhecimento
        knowledge_file = extract_knowledge(transcription_file, video_id, video_title)
        
        progress[video_id]['knowledge_file'] = knowledge_file
        progress[video_id]['status'] = 'completed'
        progress[video_id]['fim'] = time.time()
        progress[video_id]['duracao'] = progress[video_id]['fim'] - progress[video_id]['inicio']
        
        save_progress(progress)
        
        print(f"\n✅ VÍDEO PROCESSADO COM SUCESSO!")
        print(f"⏱️ Tempo total: {progress[video_id]['duracao']:.0f}s")
        
        return progress[video_id]
        
    except Exception as e:
        print(f"\n❌ ERRO AO PROCESSAR VÍDEO: {e}")
        progress[video_id]['status'] = 'failed'
        progress[video_id]['erro'] = str(e)
        save_progress(progress)
        return None

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 processar_videos_longos.py <arquivo_links.txt>")
        print("Ou: python3 processar_videos_longos.py <url> <video_id> <titulo>")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        # Processar arquivo de links
        links_file = sys.argv[1]
        
        with open(links_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('|')
                if len(parts) >= 2:
                    url = parts[0].strip()
                    video_id = parts[1].strip()
                    video_title = parts[2].strip() if len(parts) > 2 else video_id
                    
                    process_video(url, video_id, video_title)
    else:
        # Processar vídeo único
        url = sys.argv[1]
        video_id = sys.argv[2]
        video_title = sys.argv[3] if len(sys.argv) > 3 else video_id
        
        process_video(url, video_id, video_title)
    
    print(f"\n{'='*80}")
    print("🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

