#!/usr/bin/env python3
"""
Teste de conexão com Telegram.
Verifica se consegue conectar e ler mensagens.
"""

import os
import asyncio
from dotenv import load_dotenv
from services.telegram_service import TelegramService

# Carregar variáveis de ambiente
load_dotenv()

async def test_telegram():
    """Testa conexão com Telegram."""
    print("=" * 80)
    print("TESTE DE CONEXÃO COM TELEGRAM")
    print("=" * 80)
    
    # Obter credenciais
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    group_username = os.getenv('TELEGRAM_GROUP_USERNAME')
    
    print(f"\n✓ Credenciais carregadas:")
    print(f"  API ID: {api_id}")
    print(f"  API Hash: {api_hash[:10]}...")
    print(f"  Phone: {phone}")
    print(f"  Group: {group_username}")
    
    # Criar serviço
    print(f"\n⏳ Criando serviço do Telegram...")
    telegram = TelegramService(api_id, api_hash, phone)
    
    # Tentar conectar
    print(f"\n⏳ Conectando ao Telegram...")
    connected = await telegram.connect()
    
    if not connected:
        print("\n❌ Falha ao conectar ao Telegram")
        print("\nPossíveis razões:")
        print("  1. Credenciais incorretas")
        print("  2. Número de telefone não cadastrado")
        print("  3. Necessário autenticação manual (código SMS)")
        return False
    
    print(f"\n✓ Conectado com sucesso!")
    
    # Tentar obter informações do usuário
    try:
        me = await telegram.client.get_me()
        print(f"\n✓ Usuário autenticado:")
        print(f"  Nome: {me.first_name} {me.last_name or ''}")
        print(f"  Username: @{me.username or 'N/A'}")
        print(f"  ID: {me.id}")
    except Exception as e:
        print(f"\n⚠ Não foi possível obter informações do usuário: {e}")
    
    # Tentar acessar o grupo
    if group_username:
        print(f"\n⏳ Tentando acessar grupo: {group_username}")
        try:
            entity = await telegram.client.get_entity(group_username)
            print(f"\n✓ Grupo encontrado:")
            print(f"  Nome: {entity.title}")
            print(f"  ID: {entity.id}")
            
            # Tentar ler mensagens
            print(f"\n⏳ Lendo últimas 10 mensagens do grupo...")
            messages = await telegram.read_messages(group_username, limit=10)
            
            print(f"\n✓ {len(messages)} mensagens lidas:")
            for i, msg in enumerate(messages[:5], 1):
                print(f"\n  Mensagem {i}:")
                print(f"    Data: {msg.get('date', 'N/A')}")
                print(f"    Texto: {msg.get('text', 'N/A')[:100]}...")
                
        except Exception as e:
            print(f"\n❌ Erro ao acessar grupo: {e}")
            print(f"\nPossíveis razões:")
            print(f"  1. Grupo não existe ou username incorreto")
            print(f"  2. Você não é membro do grupo")
            print(f"  3. Grupo é privado")
    
    # Listar grupos/canais disponíveis
    print(f"\n⏳ Listando seus grupos/canais...")
    try:
        dialogs = await telegram.client.get_dialogs(limit=20)
        print(f"\n✓ Você tem acesso a {len(dialogs)} conversas:")
        
        groups = [d for d in dialogs if d.is_group or d.is_channel]
        if groups:
            print(f"\n  Grupos/Canais disponíveis:")
            for d in groups[:10]:
                username = f"@{d.entity.username}" if hasattr(d.entity, 'username') and d.entity.username else "Sem username"
                print(f"    - {d.name} ({username})")
        else:
            print(f"\n  ⚠ Nenhum grupo/canal encontrado")
            
    except Exception as e:
        print(f"\n⚠ Erro ao listar grupos: {e}")
    
    # Desconectar
    await telegram.disconnect()
    print(f"\n✓ Desconectado do Telegram")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    asyncio.run(test_telegram())
