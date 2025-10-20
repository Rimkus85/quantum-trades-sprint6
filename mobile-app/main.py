#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Magnus Wealth - App Android Proxy Binance
Versão 1.0.0

App simples que funciona como ponte entre servidor Manus e Binance
- Recebe comandos HTTP do servidor
- Executa ordens na Binance usando IP do celular
- Retorna resultado
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from flask import Flask, request, jsonify
from threading import Thread
from binance.client import Client
import json
import os

# Servidor Flask para receber comandos
flask_app = Flask(__name__)

# Cliente Binance (será inicializado com as chaves)
binance_client = None
api_key = ""
api_secret = ""

# Log de operações
logs = []

def add_log(msg):
    """Adiciona log"""
    logs.append(msg)
    print(msg)

@flask_app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'online',
        'binance_connected': binance_client is not None
    })

@flask_app.route('/execute', methods=['POST'])
def execute_order():
    """
    Endpoint para executar ordens na Binance
    
    Body JSON:
    {
        "action": "open_long" | "open_short" | "close_position",
        "symbol": "BTCUSDT",
        "quantity": 0.001,
        "leverage": 12
    }
    """
    try:
        if not binance_client:
            return jsonify({'error': 'Binance não configurada'}), 400
        
        data = request.json
        action = data.get('action')
        symbol = data.get('symbol')
        quantity = data.get('quantity')
        leverage = data.get('leverage', 12)
        
        add_log(f"📥 Comando recebido: {action} {symbol} {quantity}")
        
        # Configurar alavancagem
        binance_client.futures_change_leverage(
            symbol=symbol,
            leverage=leverage
        )
        
        # Configurar margem isolada
        try:
            binance_client.futures_change_margin_type(
                symbol=symbol,
                marginType='ISOLATED'
            )
        except:
            pass  # Já está isolado
        
        # Executar ordem
        if action == 'open_long':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            add_log(f"✅ LONG aberto: {order['orderId']}")
            
        elif action == 'open_short':
            order = binance_client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            add_log(f"✅ SHORT aberto: {order['orderId']}")
            
        elif action == 'close_position':
            # Obter posição atual
            positions = binance_client.futures_position_information(symbol=symbol)
            pos = next((p for p in positions if float(p['positionAmt']) != 0), None)
            
            if pos:
                amt = float(pos['positionAmt'])
                side = 'SELL' if amt > 0 else 'BUY'
                
                order = binance_client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=abs(amt)
                )
                add_log(f"✅ Posição fechada: {order['orderId']}")
            else:
                add_log(f"⚠️ Nenhuma posição aberta em {symbol}")
                return jsonify({'status': 'no_position'})
        
        return jsonify({
            'status': 'success',
            'order_id': order.get('orderId'),
            'symbol': symbol,
            'action': action
        })
        
    except Exception as e:
        add_log(f"❌ Erro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/positions', methods=['GET'])
def get_positions():
    """Retorna posições abertas"""
    try:
        if not binance_client:
            return jsonify({'error': 'Binance não configurada'}), 400
        
        positions = binance_client.futures_position_information()
        open_positions = [
            {
                'symbol': p['symbol'],
                'amount': p['positionAmt'],
                'entry_price': p['entryPrice'],
                'unrealized_pnl': p['unRealizedProfit']
            }
            for p in positions if float(p['positionAmt']) != 0
        ]
        
        return jsonify({'positions': open_positions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flask_app.route('/logs', methods=['GET'])
def get_logs():
    """Retorna logs"""
    return jsonify({'logs': logs[-50:]})  # Últimos 50 logs

def run_flask():
    """Roda servidor Flask em thread separada"""
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

class MagnusApp(App):
    """App principal"""
    
    def build(self):
        """Constrói interface"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        layout.add_widget(Label(
            text='Magnus Wealth\nProxy Binance',
            size_hint=(1, 0.2),
            font_size='24sp',
            bold=True
        ))
        
        # Status
        self.status_label = Label(
            text='Status: Aguardando configuração',
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.status_label)
        
        # API Key
        layout.add_widget(Label(text='API Key:', size_hint=(1, 0.05)))
        self.api_key_input = TextInput(
            hint_text='Cole sua API Key aqui',
            multiline=False,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.api_key_input)
        
        # API Secret
        layout.add_widget(Label(text='API Secret:', size_hint=(1, 0.05)))
        self.api_secret_input = TextInput(
            hint_text='Cole seu API Secret aqui',
            multiline=False,
            password=True,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.api_secret_input)
        
        # Botão conectar
        btn_connect = Button(
            text='Conectar Binance',
            size_hint=(1, 0.1),
            on_press=self.connect_binance
        )
        layout.add_widget(btn_connect)
        
        # Logs
        layout.add_widget(Label(text='Logs:', size_hint=(1, 0.05)))
        self.log_label = Label(
            text='Aguardando...',
            size_hint=(1, 0.3),
            halign='left',
            valign='top'
        )
        self.log_label.bind(size=self.log_label.setter('text_size'))
        layout.add_widget(self.log_label)
        
        # Iniciar servidor Flask
        Thread(target=run_flask, daemon=True).start()
        add_log("🚀 Servidor iniciado na porta 5000")
        
        # Atualizar logs periodicamente
        Clock.schedule_interval(self.update_logs, 1.0)
        
        return layout
    
    def connect_binance(self, instance):
        """Conecta à Binance"""
        global binance_client, api_key, api_secret
        
        api_key = self.api_key_input.text.strip()
        api_secret = self.api_secret_input.text.strip()
        
        if not api_key or not api_secret:
            add_log("❌ Preencha API Key e Secret")
            return
        
        try:
            binance_client = Client(api_key, api_secret)
            binance_client.ping()
            
            add_log("✅ Conectado à Binance!")
            self.status_label.text = 'Status: ✅ Online e pronto'
            
            # Salvar credenciais
            with open('/sdcard/magnus_config.json', 'w') as f:
                json.dump({'api_key': api_key, 'api_secret': api_secret}, f)
            
        except Exception as e:
            add_log(f"❌ Erro ao conectar: {str(e)}")
            self.status_label.text = f'Status: ❌ Erro'
    
    def update_logs(self, dt):
        """Atualiza logs na tela"""
        self.log_label.text = '\n'.join(logs[-10:])

if __name__ == '__main__':
    MagnusApp().run()

