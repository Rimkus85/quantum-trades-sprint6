#!/usr/bin/env python3
import os
from telethon.sync import TelegramClient

# Carregar credenciais
api_id = 20866496
api_hash = "b3634619ea4d9c7d039a372801165bbf"
group_id = -4844836232

# Exemplo CRIPTO
msg_cripto = """🟢 **Bitcoin (BTC)** 🥇

📊 **Sinal:** COMPRA
💰 **Preço Atual:** $67,234.50

🎯 **Entrada Sugerida:** $67,234.50
🔝 **Teto de Entrada:** $68,579.19 (2% acima)
🛑 **Stop Loss:** Quando HiLo virar vermelho (dinâmico)
✅ **Stop Gain:** Quando HiLo virar vermelho

📈 **Gestão:**
• Risco: 3% do capital
• Posição: Comprado

⚙️ **Configuração:**
• HiLo Período: 70
• Tier: 1 (Baixo Risco)

📊 **PERFORMANCE HISTÓRICA (R$ 100):**
🎯 Desde Início: R$ 384,20 (+284%)
📅 6 Meses: R$ 156,80 (+57%)
📅 90 Dias: R$ 124,50 (+25%)
📅 30 Dias: R$ 108,30 (+8%)

⚠️ DISCLAIMER: Alto risco. Fins educacionais.
🕐 19/10/2025 21:00 | Custom HiLo Parize"""

# Exemplo OPÇÃO
msg_opcao = """📈 COMPRA DE CALL

🏢 PETRÓLEO BRASILEIRO S.A. (PETR4)
💰 Cotação: R$ 40,00

📅 VENCIMENTO: 18/11/2025
🎲 CÓDIGO: PETR4K40

📊 QUANTIDADE:
• Mínima: 100 | Ideal: 300 | Máxima: 500

💵 CUSTO LIMITE: R$ 2,10 (não pague mais!)
✅ STOP GAIN: R$ 4,20 a R$ 6,30 (100-200%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ANÁLISE:

🎯 Setup: Rompimento de Resistência
🔔 Gatilho: Rompeu R$ 39,50 com volume 2x
📈 Mercado: Ibovespa +1,8%, Brent +3,2%
📊 Ativo: +5,2% em 5 dias, RSI 62

💡 Fundamento:
1. Rompimento confirmado com volume
2. Tendência de alta estabelecida
3. Momentum forte (MAs alinhadas)
4. R/R 1:2 (risco R$ 2,10 → ganho R$ 4,20+)
5. Espaço para R$ 42-43

🎲 Saída:
• Stop: ZERO (deixar virar pó)
• Alvo 1: R$ 4,20 (realizar 50%)
• Alvo 2: R$ 6,30 (realizar resto)

━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ DISCLAIMER: Alto risco. Perda total possível.
Fins educacionais. Não é recomendação.

🕐 19/10/2025 10:10 | Magnus Wealth"""

try:
    with TelegramClient('magnus_session', api_id, api_hash) as client:
        client.send_message(group_id, "📨 **EXEMPLOS DE MENSAGENS MAGNUS WEALTH**\n\n" + "="*40)
        client.send_message(group_id, msg_cripto)
        client.send_message(group_id, msg_opcao)
        client.send_message(group_id, "="*40 + "\n\n✅ Exemplos enviados com sucesso!")
        print("✅ Mensagens enviadas!")
except Exception as e:
    print(f"❌ Erro: {e}")
