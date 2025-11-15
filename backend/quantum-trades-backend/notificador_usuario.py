#!/usr/bin/env python3
"""
Notificador de Usuário
Magnus Wealth v9.0.0
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class NotificadorUsuario:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_id = os.getenv('TELEGRAM_USER_ID')
    
    def enviar_mensagem(self, user_id: str, mensagem: str) -> bool:
        if not self.bot_token:
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': user_id,
            'text': mensagem,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json().get('ok', False)
        except:
            return False
    
    def notificar_erro_usuario(self, erro: str, contexto: str = "", traceback: str = "") -> bool:
        if not self.user_id:
            return False
        msg = f"🚨 *ERRO*\n\n📍 {contexto}\n\n❌ {erro}"
        return self.enviar_mensagem(self.user_id, msg)
    
    def notificar_sucesso_usuario(self, mensagem: str) -> bool:
        if not self.user_id:
            return False
        return self.enviar_mensagem(self.user_id, f"✅ {mensagem}")
    
    def notificar_alerta_usuario(self, mensagem: str) -> bool:
        if not self.user_id:
            return False
        return self.enviar_mensagem(self.user_id, f"⚠️ {mensagem}")
    
    def notificar_ordem_executada(self, cripto: str, tipo: str, quantidade: float, preco: float, motivo: str) -> bool:
        if not self.user_id:
            return False
        emoji = "🟢" if tipo == "COMPRA" else "🔴"
        msg = f"{emoji} *{tipo}*\n🪙 {cripto}\n💰 ${preco:,.2f}\n📦 {quantidade:.8f}\n📝 {motivo}"
        return self.enviar_mensagem(self.user_id, msg)
