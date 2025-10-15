#!/usr/bin/env python3
"""
Serviço de integração com Telegram para o Magnus Wealth.
Responsável por ler mensagens de grupos contendo recomendações de carteiras.
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from telethon import TelegramClient, events
from telethon.tl.types import Message


class TelegramService:
    """Serviço para integração com Telegram."""
    
    def __init__(self, api_id: str, api_hash: str, phone: str, session_name: str = 'magnus_session'):
        """
        Inicializa o serviço do Telegram.
        
        Args:
            api_id: ID da API do Telegram
            api_hash: Hash da API do Telegram
            phone: Número de telefone para autenticação
            session_name: Nome da sessão (arquivo .session)
        """
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.phone = phone
        self.messages_cache = []
        self.is_connected = False
    
    async def connect(self):
        """Conecta ao Telegram."""
        try:
            await self.client.start(phone=self.phone)
            self.is_connected = True
            print("✓ Telegram conectado com sucesso!")
            return True
        except Exception as e:
            print(f"✗ Erro ao conectar ao Telegram: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Desconecta do Telegram."""
        if self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            print("✓ Telegram desconectado")
    
    async def get_group_entity(self, group_identifier: str):
        """
        Obtém a entidade do grupo.
        
        Args:
            group_identifier: Username (@grupo) ou ID numérico do grupo
            
        Returns:
            Entidade do grupo ou None
        """
        try:
            entity = await self.client.get_entity(group_identifier)
            return entity
        except Exception as e:
            print(f"✗ Erro ao obter grupo: {e}")
            return None
    
    async def read_messages(self, group_identifier: str, limit: int = 100) -> List[Dict]:
        """
        Lê mensagens de um grupo.
        
        Args:
            group_identifier: Username (@grupo) ou ID numérico do grupo
            limit: Número máximo de mensagens a ler
            
        Returns:
            Lista de mensagens em formato de dicionário
        """
        if not self.is_connected:
            await self.connect()
        
        entity = await self.get_group_entity(group_identifier)
        if not entity:
            return []
        
        messages = []
        async for message in self.client.iter_messages(entity, limit=limit):
            if message.text:
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'sender_id': message.sender_id,
                    'text': message.text,
                    'is_reply': message.is_reply,
                    'views': message.views if hasattr(message, 'views') else None
                }
                messages.append(msg_data)
        
        self.messages_cache = messages
        return messages
    
    async def monitor_messages(self, group_identifier: str, callback=None):
        """
        Monitora novas mensagens em tempo real.
        
        Args:
            group_identifier: Username (@grupo) ou ID numérico do grupo
            callback: Função a ser chamada quando nova mensagem chegar
        """
        if not self.is_connected:
            await self.connect()
        
        entity = await self.get_group_entity(group_identifier)
        if not entity:
            return
        
        @self.client.on(events.NewMessage(chats=entity))
        async def handler(event):
            message = event.message
            msg_data = {
                'id': message.id,
                'date': message.date.isoformat(),
                'sender_id': message.sender_id,
                'text': message.text,
                'is_reply': message.is_reply
            }
            
            self.messages_cache.append(msg_data)
            
            if callback:
                await callback(msg_data)
        
        await self.client.run_until_disconnected()
    
    def save_messages(self, filename: str = 'telegram_messages.json'):
        """
        Salva mensagens em arquivo JSON.
        
        Args:
            filename: Nome do arquivo de saída
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.messages_cache, f, ensure_ascii=False, indent=2)
        return filename
    
    def get_cached_messages(self) -> List[Dict]:
        """Retorna mensagens em cache."""
        return self.messages_cache


class TelegramCarteirasReader:
    """Leitor especializado para mensagens de carteiras."""
    
    def __init__(self, telegram_service: TelegramService):
        """
        Inicializa o leitor de carteiras.
        
        Args:
            telegram_service: Instância do TelegramService
        """
        self.telegram_service = telegram_service
        self.carteiras = []
    
    async def read_carteiras(self, group_identifier: str, limit: int = 100) -> List[Dict]:
        """
        Lê e filtra mensagens relacionadas a carteiras.
        
        Args:
            group_identifier: Username (@grupo) ou ID numérico do grupo
            limit: Número máximo de mensagens a ler
            
        Returns:
            Lista de mensagens filtradas sobre carteiras
        """
        messages = await self.telegram_service.read_messages(group_identifier, limit)
        
        # Filtrar mensagens relevantes
        keywords = ['carteira', 'recomendação', 'ação', 'ações', 'compra', 'venda', 
                   'ticker', 'PETR', 'VALE', 'ITUB', 'BBDC', '%']
        
        filtered = []
        for msg in messages:
            text_lower = msg['text'].lower()
            if any(keyword in text_lower for keyword in keywords):
                filtered.append(msg)
        
        self.carteiras = filtered
        return filtered
    
    def get_carteiras(self) -> List[Dict]:
        """Retorna carteiras filtradas."""
        return self.carteiras
    
    def save_carteiras(self, filename: str = 'carteiras_telegram.json'):
        """
        Salva carteiras em arquivo JSON.
        
        Args:
            filename: Nome do arquivo de saída
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.carteiras, f, ensure_ascii=False, indent=2)
        return filename


# Exemplo de uso
async def main():
    """Função principal de exemplo."""
    # Configurações (devem vir de variáveis de ambiente)
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    group = os.getenv('TELEGRAM_GROUP_USERNAME')
    
    if not all([api_id, api_hash, phone, group]):
        print("❌ Configurações do Telegram não encontradas!")
        print("Configure as variáveis de ambiente:")
        print("  TELEGRAM_API_ID")
        print("  TELEGRAM_API_HASH")
        print("  TELEGRAM_PHONE")
        print("  TELEGRAM_GROUP_USERNAME")
        return
    
    # Criar serviço
    telegram_service = TelegramService(api_id, api_hash, phone)
    
    # Conectar
    await telegram_service.connect()
    
    # Ler mensagens
    messages = await telegram_service.read_messages(group, limit=100)
    print(f"✓ {len(messages)} mensagens lidas")
    
    # Salvar mensagens
    telegram_service.save_messages()
    
    # Desconectar
    await telegram_service.disconnect()


if __name__ == '__main__':
    asyncio.run(main())

