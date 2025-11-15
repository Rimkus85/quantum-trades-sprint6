#!/usr/bin/env python3
"""
Bot de Acesso ao Grupo - Magnus Wealth v9.0.0
Gerencia acesso de usuários ao grupo de sinais via código
"""

import os
import asyncio
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerChannel
from dotenv import load_dotenv
from database_usuarios import DatabaseUsuarios, validar_codigo, usuario_autorizado
from notificador_usuario import NotificadorUsuario
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Telegram
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ID do grupo de sinais
GRUPO_SINAIS_ID = int(os.getenv('TELEGRAM_CHAT_ID', '-1003183162741'))

# Sessão do bot
SESSION_FILE = 'bot_acesso_session'

# Banco de dados
db = DatabaseUsuarios()
notificador = NotificadorUsuario()

# Cliente do bot
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)


@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """
    Handler para comando /start
    Inicia processo de validação de código
    """
    user_id = event.sender_id
    user = await event.get_sender()
    username = user.username if hasattr(user, 'username') else None
    first_name = user.first_name if hasattr(user, 'first_name') else 'Usuário'
    
    # Verificar se usuário já está cadastrado
    if db.usuario_autorizado(user_id):
        usuario_info = db.obter_usuario(user_id)
        
        await event.respond(
            f"✅ Olá {first_name}!\n\n"
            f"Você já está cadastrado no Magnus Wealth.\n\n"
            f"📊 **Seu Plano:** {usuario_info['plano'].upper()}\n"
            f"📅 **Cadastro:** {usuario_info['data_cadastro'][:10]}\n\n"
            f"💬 **Grupo de Sinais:** Magnus Wealth\n\n"
            f"Se você ainda não está no grupo, será adicionado automaticamente.\n\n"
            f"📚 **Comandos Disponíveis:**\n"
            f"/status - Ver status da sua conta\n"
            f"/ajuda - Ver ajuda e comandos"
        )
        
        # Tentar adicionar ao grupo se ainda não foi adicionado
        if not usuario_info.get('grupo_adicionado', False):
            try:
                await adicionar_usuario_grupo(user_id, username)
                db.marcar_grupo_adicionado(user_id)
                await event.respond("✅ Você foi adicionado ao grupo de sinais!")
            except Exception as e:
                await event.respond(
                    f"⚠️ Não foi possível adicionar você ao grupo automaticamente.\n\n"
                    f"Por favor, entre no grupo usando este link:\n"
                    f"[Link do Grupo]\n\n"
                    f"Ou aguarde que um administrador irá adicioná-lo."
                )
        
        return
    
    # Usuário novo - solicitar código
    await event.respond(
        f"👋 Olá {first_name}! Bem-vindo ao **Magnus Wealth**!\n\n"
        f"🤖 Sou o bot de acesso ao grupo de sinais de criptomoedas.\n\n"
        f"Para acessar o grupo, você precisa de um **código de acesso**.\n\n"
        f"🔑 **Como obter seu código:**\n"
        f"1. Entre em contato com nossa equipe\n"
        f"2. Escolha seu plano (Básico, Premium ou VIP)\n"
        f"3. Receba seu código único\n\n"
        f"📝 **Já tem um código?**\n"
        f"Digite: `/codigo SEU_CODIGO`\n\n"
        f"Exemplo: `/codigo MAGNUS-A1B2C3D4`\n\n"
        f"📞 **Contato:**\n"
        f"Email: contato@magnuswealth.com\n"
        f"Telegram: @MagnusSupport"
    )


@events.register(events.NewMessage(pattern=r'/codigo (.+)'))
async def codigo_handler(event):
    """
    Handler para validação de código
    Formato: /codigo MAGNUS-XXXXXXXX
    """
    user_id = event.sender_id
    user = await event.get_sender()
    username = user.username if hasattr(user, 'username') else None
    first_name = user.first_name if hasattr(user, 'first_name') else 'Usuário'
    
    # Extrair código
    codigo = event.pattern_match.group(1).strip().upper()
    
    # Verificar se usuário já está cadastrado
    if db.usuario_autorizado(user_id):
        await event.respond(
            "⚠️ Você já está cadastrado no Magnus Wealth!\n\n"
            "Use /status para ver suas informações."
        )
        return
    
    # Validar código
    await event.respond("🔍 Validando código...")
    
    if validar_codigo(codigo, user_id, username):
        # Código válido - usuário cadastrado
        usuario_info = db.obter_usuario(user_id)
        
        await event.respond(
            f"✅ **CÓDIGO VALIDADO COM SUCESSO!**\n\n"
            f"🎉 Bem-vindo ao Magnus Wealth, {usuario_info['nome']}!\n\n"
            f"📊 **Seu Plano:** {usuario_info['plano'].upper()}\n"
            f"📅 **Data de Cadastro:** {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"Você será adicionado ao grupo de sinais em instantes..."
        )
        
        # Adicionar ao grupo
        try:
            await adicionar_usuario_grupo(user_id, username)
            db.marcar_grupo_adicionado(user_id)
            
            await event.respond(
                "✅ **ACESSO LIBERADO!**\n\n"
                "Você foi adicionado ao grupo **Magnus Wealth - Sinais**!\n\n"
                "📊 Lá você receberá:\n"
                "• Análises diárias de criptomoedas\n"
                "• Sinais de compra/venda\n"
                "• Alertas de mudança de tendência\n"
                "• Otimizações quinzenais\n\n"
                "🚀 Bons trades!"
            )
            
            # Notificar admin
            await notificar_admin_novo_usuario(usuario_info)
            
        except Exception as e:
            await event.respond(
                f"⚠️ Seu código foi validado, mas houve um problema ao adicionar você ao grupo.\n\n"
                f"Por favor, aguarde que um administrador irá adicioná-lo manualmente.\n\n"
                f"Erro: {str(e)}"
            )
            
            # Notificar admin do erro
            await notificar_admin_erro_adicao(usuario_info, str(e))
    
    else:
        # Código inválido
        await event.respond(
            "❌ **CÓDIGO INVÁLIDO**\n\n"
            "O código informado não é válido ou já foi utilizado.\n\n"
            "Verifique se:\n"
            "• Digitou o código corretamente\n"
            "• O código não foi usado antes\n"
            "• O código não expirou\n\n"
            "💡 **Precisa de ajuda?**\n"
            "Entre em contato com nosso suporte:\n"
            "Email: contato@magnuswealth.com\n"
            "Telegram: @MagnusSupport"
        )


@events.register(events.NewMessage(pattern='/status'))
async def status_handler(event):
    """
    Handler para comando /status
    Mostra informações do usuário
    """
    user_id = event.sender_id
    
    if not db.usuario_autorizado(user_id):
        await event.respond(
            "⚠️ Você não está cadastrado.\n\n"
            "Use /start para se cadastrar."
        )
        return
    
    usuario_info = db.obter_usuario(user_id)
    
    status = "✅ Ativo" if usuario_info.get('ativo') else "❌ Inativo"
    grupo = "✅ Sim" if usuario_info.get('grupo_adicionado') else "⏳ Pendente"
    
    await event.respond(
        f"📊 **STATUS DA SUA CONTA**\n\n"
        f"👤 **Nome:** {usuario_info['nome']}\n"
        f"📧 **Email:** {usuario_info['email']}\n"
        f"💎 **Plano:** {usuario_info['plano'].upper()}\n"
        f"📅 **Cadastro:** {usuario_info['data_cadastro'][:10]}\n"
        f"🔑 **Código Usado:** {usuario_info['codigo_usado']}\n"
        f"📊 **Status:** {status}\n"
        f"💬 **No Grupo:** {grupo}\n\n"
        f"📚 **Comandos:**\n"
        f"/ajuda - Ver ajuda e comandos"
    )


@events.register(events.NewMessage(pattern='/ajuda'))
async def ajuda_handler(event):
    """
    Handler para comando /ajuda
    Mostra comandos disponíveis
    """
    await event.respond(
        "📚 **AJUDA - MAGNUS WEALTH BOT**\n\n"
        "🤖 **Comandos Disponíveis:**\n\n"
        "/start - Iniciar bot e cadastro\n"
        "/codigo <código> - Validar código de acesso\n"
        "/status - Ver status da sua conta\n"
        "/ajuda - Ver esta mensagem\n\n"
        "💡 **Como funciona:**\n"
        "1. Use /start para iniciar\n"
        "2. Obtenha seu código de acesso\n"
        "3. Use /codigo para validar\n"
        "4. Seja adicionado ao grupo automaticamente\n\n"
        "📞 **Suporte:**\n"
        "Email: contato@magnuswealth.com\n"
        "Telegram: @MagnusSupport\n\n"
        "🚀 Magnus Wealth - Sinais de Criptomoedas"
    )


async def adicionar_usuario_grupo(user_id: int, username: str = None):
    """
    Adiciona usuário ao grupo de sinais
    
    Args:
        user_id: ID do usuário no Telegram
        username: Username do usuário (opcional)
    """
    try:
        # Obter entidade do grupo
        grupo = await client.get_entity(GRUPO_SINAIS_ID)
        
        # Adicionar usuário
        await client(InviteToChannelRequest(
            grupo,
            [user_id]
        ))
        
        print(f"✓ Usuário {user_id} adicionado ao grupo")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar usuário {user_id}: {e}")
        raise


async def notificar_admin_novo_usuario(usuario_info: dict):
    """
    Notifica admin sobre novo usuário cadastrado
    """
    try:
        admin_id = int(os.getenv('TELEGRAM_USER_ID', '0'))
        if admin_id == 0:
            return
        
        msg = (
            f"🎉 **NOVO USUÁRIO CADASTRADO**\n\n"
            f"👤 **Nome:** {usuario_info['nome']}\n"
            f"📧 **Email:** {usuario_info['email']}\n"
            f"💎 **Plano:** {usuario_info['plano'].upper()}\n"
            f"🆔 **Telegram ID:** {usuario_info['telegram_user_id']}\n"
            f"👤 **Username:** @{usuario_info.get('telegram_username', 'N/A')}\n"
            f"📅 **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"✅ Usuário adicionado ao grupo com sucesso!"
        )
        
        await client.send_message(admin_id, msg)
        
    except Exception as e:
        print(f"❌ Erro ao notificar admin: {e}")


async def notificar_admin_erro_adicao(usuario_info: dict, erro: str):
    """
    Notifica admin sobre erro ao adicionar usuário
    """
    try:
        admin_id = int(os.getenv('TELEGRAM_USER_ID', '0'))
        if admin_id == 0:
            return
        
        msg = (
            f"⚠️ **ERRO AO ADICIONAR USUÁRIO**\n\n"
            f"👤 **Nome:** {usuario_info['nome']}\n"
            f"🆔 **Telegram ID:** {usuario_info['telegram_user_id']}\n"
            f"👤 **Username:** @{usuario_info.get('telegram_username', 'N/A')}\n\n"
            f"❌ **Erro:** {erro}\n\n"
            f"⚠️ **Ação necessária:** Adicionar usuário manualmente ao grupo"
        )
        
        await client.send_message(admin_id, msg)
        
    except Exception as e:
        print(f"❌ Erro ao notificar admin: {e}")


async def main():
    """
    Função principal do bot
    """
    print("=" * 80)
    print("BOT DE ACESSO AO GRUPO - MAGNUS WEALTH")
    print("=" * 80)
    
    # Conectar bot
    await client.start(bot_token=BOT_TOKEN)
    
    print("\n✅ Bot conectado!")
    print(f"📊 Grupo de sinais: {GRUPO_SINAIS_ID}")
    
    # Estatísticas
    stats = db.estatisticas()
    print(f"\n📊 Estatísticas:")
    print(f"   👥 Usuários ativos: {stats['usuarios_ativos']}")
    print(f"   🔑 Códigos pendentes: {stats['codigos_pendentes']}")
    
    # Registrar handlers
    client.add_event_handler(start_handler)
    client.add_event_handler(codigo_handler)
    client.add_event_handler(status_handler)
    client.add_event_handler(ajuda_handler)
    
    print("\n🤖 Bot rodando... (Ctrl+C para parar)")
    print("=" * 80)
    
    # Manter bot rodando
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
