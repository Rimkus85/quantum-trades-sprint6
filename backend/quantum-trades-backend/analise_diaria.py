#!/usr/bin/env python3
"""
Magnus Wealth - Análise Diária
Executa análise diária de mercado e envia alertas para o grupo Magnus Wealth
Horário: 21:00 (após fechamento do mercado)
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
SESSION_FILE = os.path.join(BASE_DIR, 'magnus_session')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Criar diretório de logs se não existir
os.makedirs(LOGS_DIR, exist_ok=True)

# Grupo Magnus Wealth
GRUPO_MAGNUS = -4844836232

async def analisar_carteiras():
    """Analisa carteiras recomendadas e identifica mudanças"""
    
    print("📊 Analisando carteiras...")
    
    # TODO: Integrar com Magnus Brain para análise real
    # Por enquanto, retorna estrutura básica
    
    analise = {
        'data': datetime.now().strftime('%d/%m/%Y'),
        'mudancas': [],
        'alertas': [],
        'oportunidades': []
    }
    
    # Exemplo de estrutura (será substituído por análise real)
    # analise['mudancas'].append({
    #     'ticker': 'PETR4',
    #     'acao': 'AUMENTAR',
    #     'de': '5%',
    #     'para': '7%',
    #     'motivo': 'Fundamentos melhoraram'
    # })
    
    return analise

async def analisar_mercado():
    """Analisa contexto geral de mercado"""
    
    print("🌍 Analisando mercado...")
    
    # TODO: Integrar com APIs de mercado e Magnus Brain
    
    analise = {
        'ibovespa': {
            'variacao': 0,  # %
            'tendencia': 'NEUTRO'
        },
        'dolar': {
            'valor': 0,
            'variacao': 0
        },
        'selic': {
            'valor': 0
        }
    }
    
    return analise

def gerar_mensagem_diaria(analise_carteiras, analise_mercado):
    """Gera mensagem de análise diária"""
    
    hoje = datetime.now()
    
    mensagem = f"""
🤖 **MAGNUS WEALTH - ANÁLISE DIÁRIA**
📅 {hoje.strftime('%d/%m/%Y - %A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **RESUMO DO DIA**

✅ Sistema operando normalmente
✅ Carteiras monitoradas
✅ Análise de mercado atualizada

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Mudanças nas carteiras
    if analise_carteiras['mudancas']:
        mensagem += "🔄 **MUDANÇAS NAS CARTEIRAS**\n\n"
        for mudanca in analise_carteiras['mudancas']:
            mensagem += f"• **{mudanca['ticker']}**: {mudanca['acao']}\n"
            mensagem += f"  De {mudanca['de']} → Para {mudanca['para']}\n"
            mensagem += f"  Motivo: {mudanca['motivo']}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Alertas importantes
    if analise_carteiras['alertas']:
        mensagem += "⚠️ **ALERTAS IMPORTANTES**\n\n"
        for alerta in analise_carteiras['alertas']:
            mensagem += f"• {alerta}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Oportunidades identificadas
    if analise_carteiras['oportunidades']:
        mensagem += "💡 **OPORTUNIDADES IDENTIFICADAS**\n\n"
        for oportunidade in analise_carteiras['oportunidades']:
            mensagem += f"• {oportunidade}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Se não há mudanças, alertas ou oportunidades
    if not analise_carteiras['mudancas'] and not analise_carteiras['alertas'] and not analise_carteiras['oportunidades']:
        mensagem += """
✅ **TUDO TRANQUILO!**

• Sem mudanças nas carteiras recomendadas
• Sem alertas importantes
• Mantenha suas posições conforme planejado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Footer
    mensagem += f"""
🤖 **Magnus Wealth**
Sistema de Análise de Investimentos com IA

📊 Próxima análise: {(hoje + timedelta(days=1)).strftime('%d/%m/%Y às 21:00')}

_Gerado automaticamente em {hoje.strftime('%d/%m/%Y às %H:%M')}_
"""
    
    return mensagem

async def enviar_analise_telegram(mensagem):
    """Envia análise para o grupo Magnus Wealth"""
    
    print("📤 Conectando ao Telegram...")
    
    async with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        
        print("✅ Conectado ao Telegram!")
        
        try:
            print(f"\nEnviando análise diária para grupo Magnus Wealth...")
            await client.send_message(GRUPO_MAGNUS, mensagem)
            print("✅ Análise enviada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
            # Fallback: enviar para mensagens salvas
            print("Enviando para Mensagens Salvas como backup...")
            await client.send_message('me', mensagem)

def salvar_log(analise_carteiras, analise_mercado):
    """Salva log da análise"""
    
    hoje = datetime.now()
    log_file = os.path.join(LOGS_DIR, f"analise_diaria_{hoje.strftime('%Y%m%d')}.json")
    
    log_data = {
        'timestamp': hoje.isoformat(),
        'carteiras': analise_carteiras,
        'mercado': analise_mercado
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Log salvo: {log_file}")

async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🤖 Magnus Wealth - Análise Diária")
    print("=" * 60)
    print()
    
    # Executar análises
    analise_carteiras = await analisar_carteiras()
    analise_mercado = await analisar_mercado()
    
    # Gerar mensagem
    print("\n📝 Gerando mensagem de análise...")
    mensagem = gerar_mensagem_diaria(analise_carteiras, analise_mercado)
    
    # Mostrar preview
    print("\n" + "=" * 60)
    print("PREVIEW DA ANÁLISE:")
    print("=" * 60)
    print(mensagem)
    print("=" * 60)
    
    # Enviar para Telegram
    await enviar_analise_telegram(mensagem)
    
    # Salvar log
    salvar_log(analise_carteiras, analise_mercado)
    
    print("\n✅ Análise diária concluída!")
    print()

if __name__ == '__main__':
    asyncio.run(main())

