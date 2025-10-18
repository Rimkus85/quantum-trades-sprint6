#!/usr/bin/env python3
"""
Magnus Wealth - Resumo Semanal
Envia resumo semanal no Telegram com análise de mercado e conhecimentos adquiridos
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configurações do Telegram
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

# Diretórios
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'youtube_knowledge')
SESSION_FILE = os.path.join(BASE_DIR, 'magnus_session')

# Grupos para enviar (você pode adicionar mais)
GRUPOS_DESTINO = [
    -4844836232,  # Magnus Wealth🎯💵🪙
    # Adicione mais grupos aqui se necessário
]

async def carregar_conhecimento():
    """Carrega base de conhecimento"""
    try:
        kb_file = os.path.join(KNOWLEDGE_DIR, 'magnus_knowledge_base.json')
        with open(kb_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar conhecimento: {e}")
        return None

async def carregar_videos_processados():
    """Carrega resumo dos vídeos processados"""
    try:
        summary_file = os.path.join(KNOWLEDGE_DIR, 'summary.json')
        with open(summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar vídeos: {e}")
        return None

def gerar_resumo_semanal(knowledge, videos):
    """Gera texto do resumo semanal"""
    
    hoje = datetime.now()
    semana_passada = hoje - timedelta(days=7)
    
    # Header
    resumo = f"""
🤖 **MAGNUS WEALTH - RESUMO SEMANAL**
📅 Semana de {semana_passada.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Estatísticas Gerais
    if knowledge:
        metadata = knowledge.get('metadata', {})
        resumo += f"""
📊 **ESTATÍSTICAS GERAIS**

• Total de vídeos processados: {metadata.get('total_videos_processed', 0)}
• Palavras de conhecimento: {metadata.get('total_words_extracted', 0):,}
• Relevância média: {metadata.get('average_relevance', 0):.1%}
• Última atualização: {metadata.get('last_update', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Estratégias Identificadas
    if knowledge and 'strategies' in knowledge:
        strategies = knowledge['strategies']
        resumo += f"""
🎯 **ESTRATÉGIAS IDENTIFICADAS**

Total: {strategies.get('total', 0)} estratégias

"""
        # Por tipo
        by_type = strategies.get('by_type', {})
        for tipo, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            emoji = {
                'portfolio': '💼',
                'protection': '🛡️',
                'etf': '📈',
                'retirement': '🏖️',
                'trend_following': '📊'
            }.get(tipo, '•')
            resumo += f"{emoji} {tipo.replace('_', ' ').title()}: {count}\n"
        
        resumo += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Top 5 Vídeos Mais Relevantes
    if knowledge and 'top_videos' in knowledge:
        top_videos = knowledge['top_videos'][:5]
        resumo += "🏆 **TOP 5 VÍDEOS MAIS RELEVANTES**\n\n"
        
        for idx, video in enumerate(top_videos, 1):
            resumo += f"{idx}. **{video['title']}**\n"
            resumo += f"   • Relevância: {video['relevance']:.1%}\n"
            resumo += f"   • Palavras: {video['words']:,}\n"
            resumo += f"   • Keywords: {video['keywords']}\n\n"
        
        resumo += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Conceitos Principais
    if knowledge and 'concepts' in knowledge:
        concepts = knowledge['concepts']
        by_concept = concepts.get('by_concept', {})
        top_concepts = sorted(by_concept.items(), key=lambda x: x[1], reverse=True)[:10]
        
        resumo += "📚 **CONCEITOS MAIS MENCIONADOS**\n\n"
        for conceito, count in top_concepts:
            resumo += f"• {conceito.replace('_', ' ').title()}: {count}x\n"
        
        resumo += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Recomendações do Magnus
    if knowledge and 'recommendations' in knowledge:
        recommendations = knowledge['recommendations']
        resumo += "💡 **RECOMENDAÇÕES DO MAGNUS**\n\n"
        
        for idx, rec in enumerate(recommendations, 1):
            resumo += f"{idx}. {rec}\n\n"
        
        resumo += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Novos Vídeos Processados (última semana)
    if videos:
        videos_recentes = []
        for video in videos.get('videos', []):
            # Verificar se foi processado na última semana
            # (simplificado - em produção, verificar data real)
            videos_recentes.append(video)
        
        if videos_recentes:
            resumo += f"🎬 **NOVOS VÍDEOS PROCESSADOS**\n\n"
            resumo += f"Total esta semana: {len(videos_recentes)}\n\n"
            
            for video in videos_recentes[:5]:  # Mostrar até 5
                resumo += f"• {video.get('title', 'N/A')}\n"
                resumo += f"  Relevância: {video.get('relevance_score', 0):.1%}\n\n"
            
            resumo += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Análise de Mercado (placeholder - será integrado com dados reais)
    resumo += """
📈 **ANÁLISE DE MERCADO DA SEMANA**

⚠️ *Em desenvolvimento*
Em breve, esta seção incluirá:
• Principais movimentos do mercado
• Ações em destaque
• Oportunidades identificadas
• Alertas de risco

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Footer
    resumo += f"""
🤖 **Magnus Wealth**
Sistema de Análise de Investimentos com IA

📊 Dashboard: https://3001-i5czx3nr4zokbwtkti35n-8fb1a071.manusvm.computer
🔄 Próximo resumo: {(hoje + timedelta(days=7)).strftime('%d/%m/%Y')}

_Gerado automaticamente em {hoje.strftime('%d/%m/%Y às %H:%M')}_
"""

    return resumo

async def enviar_resumo_telegram(resumo_texto):
    """Envia resumo para grupos do Telegram"""
    
    print("Conectando ao Telegram...")
    
    async with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        
        print("✅ Conectado ao Telegram!")
        
        # Se não há grupos configurados, enviar para "Mensagens Salvas"
        if not GRUPOS_DESTINO:
            print("\n⚠️ Nenhum grupo configurado. Enviando para Mensagens Salvas...")
            await client.send_message('me', resumo_texto)
            print("✅ Resumo enviado para Mensagens Salvas!")
            return
        
        # Enviar para grupos configurados
        for grupo in GRUPOS_DESTINO:
            try:
                print(f"\nEnviando para: {grupo}")
                await client.send_message(grupo, resumo_texto)
                print(f"✅ Enviado com sucesso!")
                await asyncio.sleep(2)  # Evitar flood
            except Exception as e:
                print(f"❌ Erro ao enviar para {grupo}: {e}")

async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🤖 Magnus Wealth - Resumo Semanal")
    print("=" * 60)
    print()
    
    # Carregar dados
    print("📚 Carregando base de conhecimento...")
    knowledge = await carregar_conhecimento()
    
    print("🎬 Carregando vídeos processados...")
    videos = await carregar_videos_processados()
    
    if not knowledge and not videos:
        print("❌ Erro: Não foi possível carregar dados")
        return
    
    # Gerar resumo
    print("\n📝 Gerando resumo semanal...")
    resumo = gerar_resumo_semanal(knowledge, videos)
    
    # Mostrar preview
    print("\n" + "=" * 60)
    print("PREVIEW DO RESUMO:")
    print("=" * 60)
    print(resumo)
    print("=" * 60)
    
    # Enviar para Telegram
    print("\n📤 Enviando para Telegram...")
    await enviar_resumo_telegram(resumo)
    
    print("\n✅ Resumo semanal enviado com sucesso!")
    print()

if __name__ == '__main__':
    asyncio.run(main())

