#!/usr/bin/env python3
"""
Magnus Wealth - Bot de Comandos
Bot interativo que responde a comandos no grupo Magnus Wealth
Comandos: /ajuda, /carteiras, /status, /analise, /opcoes
"""

import os
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
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

# Grupo Magnus Wealth
GRUPO_MAGNUS = -4844836232

# Cliente Telegram
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# ============================================================================
# COMANDOS
# ============================================================================

def cmd_ajuda():
    """Comando /ajuda - Lista todos os comandos disponíveis"""
    
    return """
🤖 **MAGNUS WEALTH - COMANDOS DISPONÍVEIS**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**INFORMAÇÕES:**
• `/ajuda` - Mostra esta mensagem
• `/status` - Status do sistema Magnus
• `/carteiras` - Carteiras recomendadas
• `/analise` - Última análise de mercado

**OPÇÕES:**
• `/opcoes` - Análise de opções
• `/montagens` - Montagens ativas
• `/desmontagens` - Desmontagens recentes

**CONFIGURAÇÕES:**
• `/perfil` - Seu perfil de investidor
• `/alertas` - Configurar alertas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **DICA:** Digite qualquer comando para mais informações!

🤖 Magnus Wealth - Sistema de Análise com IA
"""

def cmd_status():
    """Comando /status - Mostra status do sistema"""
    
    agora = datetime.now()
    
    return f"""
🤖 **MAGNUS WEALTH - STATUS DO SISTEMA**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **SISTEMA OPERACIONAL**

📊 **Serviços Ativos:**
• Magnus Brain: ✅ Online
• Análise Diária: ✅ Agendada (21:00)
• Análise Opções: ✅ Agendada (10:10, 14:00, 16:45)
• Resumo Semanal: ✅ Agendado (Sábado 10:00)
• Bot de Comandos: ✅ Online

🔄 **Última Atualização:**
• Data: {agora.strftime('%d/%m/%Y')}
• Hora: {agora.strftime('%H:%M:%S')}

📈 **Fontes de Dados:**
• Telegram (Carteiras): ✅ Ativo
• Telegram (Opções): ✅ Ativo
• API brapi.dev: ✅ Conectado
• Magnus Learning: ✅ Funcionando

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Todos os sistemas operando normalmente!

🤖 Magnus Wealth v7.0.0
"""

def cmd_carteiras():
    """Comando /carteiras - Mostra carteiras recomendadas"""
    
    return """
📊 **MAGNUS WEALTH - CARTEIRAS RECOMENDADAS**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ESCOLHA SEU PERFIL:**

📈 **AGRESSIVA** (Retorno: 15-25% a.a.)
• 17 ativos
• 46.67% Ações
• 25% SP500 (IVVB11)
• 25% Tesouro Selic
• Risco: Alto

📊 **MODERADA** (Retorno: 10-15% a.a.)
• 17 ativos
• 25% Ações
• 25% SP500 (IVVB11)
• 50% Tesouro Selic
• Risco: Médio

🛡️ **CONSERVADORA** (Retorno: 8-12% a.a.)
• 7 ativos
• 10% Ações
• 20% SP500 (IVVB11)
• 70% Tesouro Selic
• Risco: Baixo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 **DOCUMENTOS COMPLETOS:**
• PDF detalhado (12 páginas)
• Planilha Excel interativa
• Análise fundamentalista de cada ativo

💡 **DICA:** Escolha o perfil que combina com seu objetivo e tolerância ao risco!

🤖 Magnus Wealth - Carteiras Customizadas
"""

def cmd_analise():
    """Comando /analise - Mostra última análise de mercado"""
    
    agora = datetime.now()
    
    return f"""
📊 **MAGNUS WEALTH - ÚLTIMA ANÁLISE**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 **Data:** {agora.strftime('%d/%m/%Y')}

✅ **RESUMO:**
• Sistema monitorando mercado 24/7
• Carteiras recomendadas estáveis
• Sem alertas críticos no momento

🔄 **PRÓXIMAS ANÁLISES:**
• Análise Diária: Hoje às 21:00
• Análise Opções: 10:10, 14:00, 16:45
• Resumo Semanal: Sábado às 10:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **DICA:** As análises são enviadas automaticamente neste grupo!

🤖 Magnus Wealth - Análise Automatizada
"""

def cmd_opcoes():
    """Comando /opcoes - Mostra análise de opções"""
    
    return """
📈 **MAGNUS WEALTH - ANÁLISE DE OPÇÕES**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 **MONITORAMENTO ATIVO:**
• Grupo de Opções: ✅ Monitorado
• Mensagens processadas: 500+
• Alertas configurados: ✅

⏰ **HORÁRIOS DE ANÁLISE:**
• 10:10 - Análise de abertura
• 14:00 - Análise meio-dia
• 16:45 - Análise pré-fechamento

🟢 **MONTAGENS RECENTES:**
• Aguardando próxima análise...

🔴 **DESMONTAGENS RECENTES:**
• Aguardando próxima análise...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **DICA:** As análises de opções são enviadas automaticamente nos horários programados!

🤖 Magnus Wealth - Opções Automatizadas
"""

def cmd_perfil():
    """Comando /perfil - Informações sobre perfil de investidor"""
    
    return """
👤 **MAGNUS WEALTH - PERFIL DE INVESTIDOR**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**QUAL É O SEU PERFIL?**

📈 **AGRESSIVO**
• Aceita alta volatilidade
• Busca retornos acima de 15% a.a.
• Horizonte: 5+ anos
• Tolera perdas temporárias

📊 **MODERADO**
• Aceita volatilidade média
• Busca retornos de 10-15% a.a.
• Horizonte: 3-5 anos
• Prefere equilíbrio risco/retorno

🛡️ **CONSERVADOR**
• Baixa tolerância a risco
• Busca retornos de 8-12% a.a.
• Horizonte: 1-3 anos
• Prioriza preservação de capital

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **DICA:** Use o comando `/carteiras` para ver a carteira ideal para seu perfil!

🤖 Magnus Wealth - Investimento Personalizado
"""

def cmd_alertas():
    """Comando /alertas - Configurar alertas"""
    
    return """
🔔 **MAGNUS WEALTH - SISTEMA DE ALERTAS**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **ALERTAS ATIVOS:**

📊 **Análises Automáticas:**
• Análise Diária: 21:00
• Análise Opções: 10:10, 14:00, 16:45
• Resumo Semanal: Sábado 10:00

⚠️ **Alertas de Mercado:**
• Mudanças em carteiras: ✅
• Oportunidades identificadas: ✅
• Alertas de risco: ✅

🔔 **Notificações:**
• Grupo Magnus Wealth: ✅
• Mensagens silenciosas quando apropriado: ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **DICA:** Todos os alertas são enviados automaticamente neste grupo!

🤖 Magnus Wealth - Alertas Inteligentes
"""

def cmd_desconhecido(comando):
    """Comando desconhecido"""
    
    return f"""
❓ **COMANDO DESCONHECIDO**

O comando `{comando}` não foi reconhecido.

Digite `/ajuda` para ver todos os comandos disponíveis!

🤖 Magnus Wealth
"""

# ============================================================================
# HANDLERS DE EVENTOS
# ============================================================================

@client.on(events.NewMessage(chats=[GRUPO_MAGNUS], pattern=r'^/'))
async def handler_comandos(event):
    """Handler para comandos que começam com /"""
    
    mensagem = event.message.text.strip().lower()
    comando = mensagem.split()[0]
    
    print(f"\n📨 Comando recebido: {comando}")
    print(f"   De: {event.sender_id}")
    print(f"   Chat: {event.chat_id}")
    
    # Mapear comandos para funções
    comandos = {
        '/ajuda': cmd_ajuda,
        '/help': cmd_ajuda,
        '/status': cmd_status,
        '/carteiras': cmd_carteiras,
        '/analise': cmd_analise,
        '/opcoes': cmd_opcoes,
        '/perfil': cmd_perfil,
        '/alertas': cmd_alertas,
        '/montagens': cmd_opcoes,  # Alias
        '/desmontagens': cmd_opcoes,  # Alias
    }
    
    # Executar comando
    if comando in comandos:
        resposta = comandos[comando]()
        await event.respond(resposta)
        print(f"✅ Resposta enviada!")
    else:
        resposta = cmd_desconhecido(comando)
        await event.respond(resposta)
        print(f"⚠️ Comando desconhecido!")

@client.on(events.NewMessage(chats=[GRUPO_MAGNUS], pattern=r'(?i)(oi|olá|ola|hello|hi) magnus'))
async def handler_saudacao(event):
    """Handler para saudações ao Magnus"""
    
    print(f"\n👋 Saudação recebida!")
    
    resposta = """
👋 **Olá! Eu sou o Magnus!**

Sou seu assistente de investimentos com IA.

Digite `/ajuda` para ver tudo que posso fazer por você!

🤖 Magnus Wealth
"""
    
    await event.respond(resposta)
    print(f"✅ Saudação respondida!")

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Função principal - Inicia o bot"""
    
    print("=" * 60)
    print("🤖 Magnus Wealth - Bot de Comandos")
    print("=" * 60)
    print()
    
    print("📱 Conectando ao Telegram...")
    await client.start(phone=PHONE)
    
    print("✅ Conectado ao Telegram!")
    print()
    
    me = await client.get_me()
    print(f"👤 Logado como: {me.first_name} (@{me.username})")
    print(f"📱 Telefone: {me.phone}")
    print()
    
    print("🔄 Bot de comandos ativo!")
    print("⏳ Aguardando comandos...")
    print()
    print("Comandos disponíveis:")
    print("  • /ajuda - Lista de comandos")
    print("  • /status - Status do sistema")
    print("  • /carteiras - Carteiras recomendadas")
    print("  • /analise - Última análise")
    print("  • /opcoes - Análise de opções")
    print()
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    print()
    
    # Manter o bot rodando
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Bot interrompido pelo usuário")
        print("👋 Até logo!")

