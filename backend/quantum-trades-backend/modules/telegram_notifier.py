"""
Sistema de Notificações via Telegram.
Envia alertas automáticos para o usuário.
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


class TelegramNotifier:
    """Envia notificações via Telegram."""
    
    def __init__(self):
        """Inicializa o notificador."""
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.client = None
        self.alerts_group = None
    
    async def connect(self):
        """Conecta ao Telegram."""
        self.client = TelegramClient('magnus_session', self.api_id, self.api_hash)
        await self.client.connect()
        print("✓ Conectado ao Telegram")
    
    async def disconnect(self):
        """Desconecta do Telegram."""
        if self.client:
            await self.client.disconnect()
    
    async def create_alerts_group(self, group_name: str = "Magnus Alerts"):
        """
        Cria grupo de alertas.
        
        Args:
            group_name: Nome do grupo
        """
        try:
            # Criar grupo
            self.alerts_group = await self.client.create_group(
                title=group_name,
                users=[]  # Apenas você
            )
            
            # Enviar mensagem de boas-vindas
            await self.send_to_alerts_group(
                "🤖 **Magnus Alerts**\n\n"
                "Bem-vindo ao sistema de alertas automáticos do Magnus!\n\n"
                "Você receberá notificações sobre:\n"
                "• Novas carteiras recomendadas\n"
                "• Alertas de opções\n"
                "• Mudanças de estratégia\n"
                "• Relatórios diários\n\n"
                f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            
            print(f"✓ Grupo '{group_name}' criado com sucesso")
            return self.alerts_group
            
        except Exception as e:
            print(f"⚠ Erro ao criar grupo: {e}")
            # Se já existe, tentar encontrar
            dialogs = await self.client.get_dialogs()
            for dialog in dialogs:
                if dialog.title == group_name:
                    self.alerts_group = dialog
                    print(f"✓ Grupo '{group_name}' encontrado")
                    return self.alerts_group
    
    async def send_to_me(self, message: str):
        """
        Envia mensagem para você mesmo (Saved Messages).
        
        Args:
            message: Mensagem a enviar
        """
        try:
            await self.client.send_message('me', message)
            print(f"✓ Mensagem enviada para Saved Messages")
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
    
    async def send_to_alerts_group(self, message: str):
        """
        Envia mensagem para o grupo de alertas.
        
        Args:
            message: Mensagem a enviar
        """
        if not self.alerts_group:
            # Enviar para Saved Messages se grupo não existe
            await self.send_to_me(message)
            return
        
        try:
            await self.client.send_message(self.alerts_group, message)
            print(f"✓ Alerta enviado para grupo")
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")
    
    async def send_file(self, file_path: str, caption: str = ""):
        """
        Envia arquivo para Saved Messages.
        
        Args:
            file_path: Caminho do arquivo
            caption: Legenda do arquivo
        """
        try:
            await self.client.send_file('me', file_path, caption=caption)
            print(f"✓ Arquivo enviado: {file_path}")
        except Exception as e:
            print(f"❌ Erro ao enviar arquivo: {e}")
    
    async def notify_new_carteira(self, carteira: Dict):
        """
        Notifica sobre nova carteira.
        
        Args:
            carteira: Dados da carteira
        """
        message = (
            "📊 **NOVA CARTEIRA DETECTADA**\n\n"
            f"Tipo: {carteira.get('tipo', 'N/A')}\n"
            f"Data: {carteira.get('data', 'N/A')}\n"
            f"Ativos: {carteira.get('total_ativos', 0)}\n\n"
            "Top 5 alocações:\n"
        )
        
        for ativo in carteira.get('top_5', []):
            message += f"• {ativo['ticker']}: {ativo['percentual']:.1f}%\n"
        
        message += f"\n✅ Processada pelo Magnus Learning"
        
        await self.send_to_me(message)
    
    async def notify_new_opcao(self, opcao: Dict):
        """
        Notifica sobre novo alerta de opção.
        
        Args:
            opcao: Dados da opção
        """
        message = (
            f"🎯 **ALERTA DE OPÇÃO**\n\n"
            f"Tipo: {opcao.get('alert_type', 'N/A')}\n"
            f"Ativo: {opcao.get('ticker', 'N/A')}\n"
            f"Estrutura: {opcao.get('structure', 'N/A')}\n"
        )
        
        if opcao.get('strike'):
            message += f"Strike: {opcao['strike']}\n"
        
        if opcao.get('expiration'):
            message += f"Vencimento: {opcao['expiration']}\n"
        
        if opcao.get('profit_pct'):
            message += f"\n💰 Lucro: {opcao['profit_pct']:.0f}%"
        
        await self.send_to_me(message)
    
    async def notify_daily_report(self, stats: Dict):
        """
        Envia relatório diário.
        
        Args:
            stats: Estatísticas do dia
        """
        message = (
            "📈 **RELATÓRIO DIÁRIO DO MAGNUS**\n\n"
            f"Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "📊 Carteiras:\n"
            f"• Processadas: {stats.get('carteiras_processadas', 0)}\n"
            f"• Posições ativas: {stats.get('posicoes_ativas', 0)}\n"
            f"• Tickers únicos: {stats.get('tickers_unicos', 0)}\n\n"
            "🎯 Opções:\n"
            f"• Alertas: {stats.get('alertas_opcoes', 0)}\n"
            f"• Vencedoras: {stats.get('opcoes_vencedoras', 0)}\n"
            f"• Taxa de acerto: {stats.get('win_rate', 0):.1f}%\n\n"
            "🧠 Magnus Learning:\n"
            f"• Modo: {stats.get('modo_estrategia', 'N/A')}\n"
            f"• Confiança média: {stats.get('confianca_media', 0):.1f}%\n\n"
            "✅ Sincronização completa"
        )
        
        await self.send_to_me(message)
    
    async def notify_strategy_change(self, old_strategy: str, new_strategy: str, reason: str):
        """
        Notifica sobre mudança de estratégia.
        
        Args:
            old_strategy: Estratégia anterior
            new_strategy: Nova estratégia
            reason: Motivo da mudança
        """
        message = (
            "⚠️ **MUDANÇA DE ESTRATÉGIA**\n\n"
            f"De: {old_strategy}\n"
            f"Para: {new_strategy}\n\n"
            f"Motivo:\n{reason}\n\n"
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        await self.send_to_me(message)


async def test_notifier():
    """Testa o notificador."""
    print("=" * 80)
    print("TESTE DO SISTEMA DE NOTIFICAÇÕES")
    print("=" * 80)
    
    notifier = TelegramNotifier()
    
    try:
        # Conectar
        await notifier.connect()
        
        # Enviar mensagem de teste
        print("\n📱 Enviando mensagem de teste...")
        await notifier.send_to_me(
            "🤖 **Teste do Magnus Notifier**\n\n"
            f"Sistema de notificações funcionando!\n"
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        
        # Testar notificação de carteira
        print("\n📊 Testando notificação de carteira...")
        await notifier.notify_new_carteira({
            'tipo': 'AGRESSIVA',
            'data': '07/10/2025',
            'total_ativos': 17,
            'top_5': [
                {'ticker': 'IVVB11', 'percentual': 25.0},
                {'ticker': 'LFTB11', 'percentual': 25.0},
                {'ticker': 'PETR4', 'percentual': 3.33},
                {'ticker': 'VALE3', 'percentual': 3.33},
                {'ticker': 'BBAS3', 'percentual': 3.33}
            ]
        })
        
        # Testar notificação de opção
        print("\n🎯 Testando notificação de opção...")
        await notifier.notify_new_opcao({
            'alert_type': 'Desmontagem',
            'ticker': 'PYPL',
            'structure': 'Compra de Call',
            'profit_pct': 150.0
        })
        
        # Testar relatório diário
        print("\n📈 Testando relatório diário...")
        await notifier.notify_daily_report({
            'carteiras_processadas': 3,
            'posicoes_ativas': 51,
            'tickers_unicos': 21,
            'alertas_opcoes': 5,
            'opcoes_vencedoras': 2,
            'win_rate': 66.7,
            'modo_estrategia': 'MODERATE',
            'confianca_media': 75.5
        })
        
        print("\n" + "=" * 80)
        print("✅ TESTES CONCLUÍDOS")
        print("=" * 80)
        print("\n📱 Verifique suas mensagens no Telegram (Saved Messages)")
        
    finally:
        await notifier.disconnect()


if __name__ == '__main__':
    asyncio.run(test_notifier())

