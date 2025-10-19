#!/usr/bin/env python3
"""
Magnus Wealth - Análise de Opções
Executa análise de opções em horários estratégicos
Horários: 10:10, 14:00, 16:45 (dias úteis)
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

# Grupo de Opções (Tio Huli)
GRUPO_OPCOES = None  # TODO: Adicionar ID do grupo de opções

async def analisar_opcoes_recentes():
    """Analisa mensagens recentes sobre opções"""
    
    print("📊 Analisando opções...")
    
    # TODO: Integrar com serviço de leitura do Telegram
    # Por enquanto, retorna estrutura básica
    
    analise = {
        'timestamp': datetime.now().isoformat(),
        'montagens': [],
        'desmontagens': [],
        'alertas': []
    }
    
    # Exemplo de estrutura (será substituído por análise real)
    # analise['montagens'].append({
    #     'ticker': 'PETR4',
    #     'strike': 'R$ 40,00',
    #     'vencimento': '15/11/2025',
    #     'tipo': 'CALL',
    #     'estrategia': 'Venda coberta'
    # })
    
    return analise

def determinar_horario():
    """Determina qual horário de análise está sendo executado"""
    
    agora = datetime.now()
    hora = agora.hour
    minuto = agora.minute
    
    if hora == 10 and minuto >= 10:
        return "ABERTURA", "10:10"
    elif hora == 14:
        return "MEIO-DIA", "14:00"
    elif hora == 16 and minuto >= 45:
        return "FECHAMENTO", "16:45"
    else:
        return "MANUAL", agora.strftime("%H:%M")

def gerar_mensagem_opcoes(analise, periodo, horario):
    """Gera mensagem de análise de opções"""
    
    hoje = datetime.now()
    
    # Emoji por período
    emoji_periodo = {
        'ABERTURA': '🌅',
        'MEIO-DIA': '☀️',
        'FECHAMENTO': '🌆',
        'MANUAL': '🔔'
    }
    
    mensagem = f"""
{emoji_periodo.get(periodo, '🔔')} **MAGNUS - ANÁLISE DE OPÇÕES**
📅 {hoje.strftime('%d/%m/%Y')} - {periodo} ({horario})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

    # Montagens detectadas
    if analise['montagens']:
        mensagem += "🟢 **MONTAGENS DETECTADAS**\n\n"
        for montagem in analise['montagens']:
            mensagem += f"• **{montagem['ticker']}** - {montagem['tipo']}\n"
            mensagem += f"  Strike: {montagem['strike']}\n"
            mensagem += f"  Vencimento: {montagem['vencimento']}\n"
            mensagem += f"  Estratégia: {montagem['estrategia']}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Desmontagens detectadas
    if analise['desmontagens']:
        mensagem += "🔴 **DESMONTAGENS DETECTADAS**\n\n"
        for desmontagem in analise['desmontagens']:
            mensagem += f"• **{desmontagem['ticker']}** - {desmontagem['tipo']}\n"
            mensagem += f"  Strike: {desmontagem['strike']}\n"
            mensagem += f"  Motivo: {desmontagem['motivo']}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Alertas
    if analise['alertas']:
        mensagem += "⚠️ **ALERTAS**\n\n"
        for alerta in analise['alertas']:
            mensagem += f"• {alerta}\n\n"
        mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Se não há atividade
    if not analise['montagens'] and not analise['desmontagens'] and not analise['alertas']:
        mensagem += """
✅ **SEM ATIVIDADE NO MOMENTO**

• Sem novas montagens detectadas
• Sem desmontagens necessárias
• Mantenha suas posições atuais

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Próxima análise
    proxima_analise = {
        'ABERTURA': '14:00',
        'MEIO-DIA': '16:45',
        'FECHAMENTO': '10:10 (próximo dia útil)',
        'MANUAL': 'Conforme agendamento'
    }
    
    mensagem += f"""
🤖 **Magnus Wealth**
Análise de Opções Automatizada

🔄 Próxima análise: {proxima_analise.get(periodo, 'N/A')}

_Gerado automaticamente em {hoje.strftime('%d/%m/%Y às %H:%M')}_
"""
    
    return mensagem

async def enviar_analise_telegram(mensagem, silencioso=False):
    """Envia análise para o grupo Magnus Wealth"""
    
    print("📤 Conectando ao Telegram...")
    
    async with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        await client.start(phone=PHONE)
        
        print("✅ Conectado ao Telegram!")
        
        try:
            # Se não há atividade e é horário de meio-dia, enviar silenciosamente
            if silencioso:
                print(f"\nEnviando análise (silenciosa) para grupo Magnus Wealth...")
            else:
                print(f"\nEnviando análise para grupo Magnus Wealth...")
            
            await client.send_message(
                GRUPO_MAGNUS, 
                mensagem,
                silent=silencioso  # Não notificar se for análise vazia no meio do dia
            )
            print("✅ Análise enviada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao enviar: {e}")
            # Fallback: enviar para mensagens salvas
            print("Enviando para Mensagens Salvas como backup...")
            await client.send_message('me', mensagem)

def salvar_log(analise, periodo, horario):
    """Salva log da análise"""
    
    hoje = datetime.now()
    log_file = os.path.join(LOGS_DIR, f"analise_opcoes_{hoje.strftime('%Y%m%d_%H%M')}.json")
    
    log_data = {
        'timestamp': hoje.isoformat(),
        'periodo': periodo,
        'horario': horario,
        'analise': analise
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Log salvo: {log_file}")

async def main():
    """Função principal"""
    
    print("=" * 60)
    print("🤖 Magnus Wealth - Análise de Opções")
    print("=" * 60)
    print()
    
    # Determinar horário
    periodo, horario = determinar_horario()
    print(f"⏰ Período: {periodo} ({horario})")
    
    # Executar análise
    analise = await analisar_opcoes_recentes()
    
    # Gerar mensagem
    print("\n📝 Gerando mensagem de análise...")
    mensagem = gerar_mensagem_opcoes(analise, periodo, horario)
    
    # Mostrar preview
    print("\n" + "=" * 60)
    print("PREVIEW DA ANÁLISE:")
    print("=" * 60)
    print(mensagem)
    print("=" * 60)
    
    # Determinar se deve enviar silenciosamente
    # (se não há atividade e é meio-dia, enviar silencioso)
    silencioso = (
        periodo == "MEIO-DIA" and 
        not analise['montagens'] and 
        not analise['desmontagens'] and 
        not analise['alertas']
    )
    
    # Enviar para Telegram
    await enviar_analise_telegram(mensagem, silencioso)
    
    # Salvar log
    salvar_log(analise, periodo, horario)
    
    print("\n✅ Análise de opções concluída!")
    print()

if __name__ == '__main__':
    asyncio.run(main())

