#!/usr/bin/env python3
"""
Script de Inicialização do Grupo Magnus.
Envia mensagem de boas-vindas e carteiras de outubro.
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


async def start_grupo(group_name: str):
    """
    Inicia o grupo Magnus com mensagens de boas-vindas e carteiras.
    
    Args:
        group_name: Nome do grupo criado pelo usuário
    """
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    client = TelegramClient('magnus_session', api_id, api_hash)
    await client.connect()
    
    print("=" * 80)
    print("INICIANDO GRUPO MAGNUS")
    print("=" * 80)
    
    # Encontrar o grupo
    print(f"\n🔍 Procurando grupo: {group_name}")
    dialogs = await client.get_dialogs()
    
    grupo = None
    for dialog in dialogs:
        if group_name.lower() in dialog.title.lower():
            grupo = dialog
            print(f"✅ Grupo encontrado: {dialog.title}")
            break
    
    if not grupo:
        print(f"❌ Grupo '{group_name}' não encontrado!")
        print("\nGrupos disponíveis:")
        for dialog in dialogs[:10]:
            print(f"  - {dialog.title}")
        await client.disconnect()
        return
    
    # 1. Mensagem de Boas-Vindas
    print("\n📱 Enviando mensagem de boas-vindas...")
    
    data_inicio = datetime.now().strftime('%d/%m/%Y')
    
    boas_vindas = f"""🤖 **Olá! Sou o Magnus!**

Sou uma **IA de assessoria financeira** alimentada pela **Quantum Trade**, a super mega blaster ferramenta de automação do mercado financeiro que possibilita executar análises, monitoramento e recomendações de forma **totalmente autônoma**!

---

🏆 **Bem-vindo ao Grupo Exclusivo!**

Você faz parte de um **seleto grupo** que terá acesso privilegiado às minhas análises e recomendações em tempo real!

---

📊 **O que você vai receber aqui:**

**1️⃣ CARTEIRAS RECOMENDADAS**
• 3 perfis: AGRESSIVA, MODERADA, CONSERVADORA
• Ações, FIIs e ETFs
• Análise diária às 21:00
• Alertas só quando houver mudança

**2️⃣ OPÇÕES**
• Montagens, rolagens e desmontagens
• 3 análises diárias: 10:10, 14:00, 16:45
• Baseado em operações vencedoras

**3️⃣ CRIPTOMOEDAS**
• Oportunidades de entrada/saída
• Análise diária às 21:00

**4️⃣ RELATÓRIOS MENSAIS**
• Performance detalhada em PDF
• Resultados acumulados
• Taxa de acerto

---

⚠️ **IMPORTANTE - Como funciona:**

🔕 **SEM SPAM!**
• Análises acontecem em background
• Você só recebe alerta quando precisa agir
• Nada de encher o grupo!

📅 **Rotina Automática:**
• 10:10, 14:00, 16:45 - Opções (silencioso)
• 21:00 - Ações/FIIs/Cripto (silencioso)
• Final do mês - Relatório PDF
• Início do mês - Carteiras atualizadas

---

🧠 **Como eu aprendo:**
• Analiso centenas de mensagens de especialistas
• Identifico padrões de operações vencedoras
• Evito erros de operações perdedoras
• Ajusto estratégias baseado em performance real

---

🚀 **Vamos começar!**

Logo abaixo, vou enviar as **CARTEIRAS DE OUTUBRO/2025**!

---

⚠️ **Aviso Legal:**
As recomendações são baseadas em análises automatizadas e não constituem recomendação de investimento. Sempre consulte um profissional certificado.

---

**🤖 Magnus AI**
*Powered by Quantum Trade*
Iniciado em: {data_inicio}"""
    
    await client.send_message(grupo, boas_vindas)
    print("✅ Boas-vindas enviadas!")
    
    # Aguardar 2 segundos
    await asyncio.sleep(2)
    
    # 2. Carteira AGRESSIVA
    print("\n📊 Enviando Carteira AGRESSIVA...")
    
    carteira_agressiva = """📊 **CARTEIRA AGRESSIVA - OUTUBRO/2025**

**Perfil:** Alta exposição a ações (46.67%)
**Risco:** Alto
**Retorno Esperado:** 15-25% ao ano

---

**COMPOSIÇÃO (17 ativos - 100%):**

🌎 **Internacional (25%)**
• IVVB11 - 25.00% (S&P 500)

💰 **Renda Fixa (25%)**
• LFTB11 - 25.00% (Tesouro Selic)

📈 **Ações Brasileiras (50%)**

🏦 **Bancos (10%)**
• BBAS3 - 3.33% (Banco do Brasil)
• BRSR6 - 3.33% (Banrisul)
• BMGB4 - 3.33% (Banco BMG)

⛽ **Petróleo & Gás (6.66%)**
• PETR4 - 3.33% (Petrobras)
• PRIO3 - 3.33% (PetroRio)

⚙️ **Siderurgia & Mineração (9.99%)**
• USIM5 - 3.33% (Usiminas)
• GOAU4 - 3.33% (Gerdau Met)
• BRAP4 - 3.33% (Bradespar)

🚚 **Logística (6.66%)**
• LOGG3 - 3.33% (Log Commercial)
• DEXP3 - 3.33% (Dexxos)

🌾 **Agronegócio (3.33%)**
• SMTO3 - 3.33% (São Martinho)

🔫 **Defesa (3.33%)**
• TASA4 - 3.33% (Taurus)

🪵 **Madeira (3.33%)**
• EUCA4 - 3.33% (Eucatex)

🎓 **Educação (3.33%)**
• ALLD3 - 3.33% (Allied)

🏭 **Máquinas (3.33%)**
• ROMI3 - 3.33% (Romi)

---

**✅ Carteira diversificada em 9 setores**
**✅ Proteção com 50% em ativos de baixo risco**
**✅ Exposição internacional via SP500**

---

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025

*Análises diárias às 21:00. Alertas só se houver mudança.*"""
    
    await client.send_message(grupo, carteira_agressiva)
    print("✅ Carteira AGRESSIVA enviada!")
    
    await asyncio.sleep(2)
    
    # 3. Carteira MODERADA
    print("\n📊 Enviando Carteira MODERADA...")
    
    carteira_moderada = """📊 **CARTEIRA MODERADA - OUTUBRO/2025**

**Perfil:** Balanceada (25% ações)
**Risco:** Médio
**Retorno Esperado:** 10-15% ao ano

---

**COMPOSIÇÃO (17 ativos - 100%):**

💰 **Renda Fixa (50%)**
• LFTB11 - 50.00% (Tesouro Selic)

🌎 **Internacional (25%)**
• IVVB11 - 25.00% (S&P 500)

📈 **Ações Brasileiras (25%)**

🏦 **Bancos (5%)**
• BBAS3 - 1.67% (Banco do Brasil)
• BRSR6 - 1.67% (Banrisul)
• BMGB4 - 1.67% (Banco BMG)

⛽ **Petróleo & Gás (3.34%)**
• PETR4 - 1.67% (Petrobras)
• PRIO3 - 1.67% (PetroRio)

⚙️ **Siderurgia & Mineração (5%)**
• USIM5 - 1.67% (Usiminas)
• GOAU4 - 1.67% (Gerdau Met)
• BRAP4 - 1.67% (Bradespar)

🚚 **Logística (3.34%)**
• LOGG3 - 1.67% (Log Commercial)
• DEXP3 - 1.67% (Dexxos)

🌾 **Agronegócio (1.67%)**
• SMTO3 - 1.67% (São Martinho)

🔫 **Defesa (1.67%)**
• TASA4 - 1.67% (Taurus)

🪵 **Madeira (1.67%)**
• EUCA4 - 1.67% (Eucatex)

🎓 **Educação (1.67%)**
• ALLD3 - 1.67% (Allied)

🏭 **Máquinas (1.67%)**
• ROMI3 - 1.67% (Romi)

---

**✅ 75% em ativos de baixo risco**
**✅ Diversificação em 9 setores**
**✅ Exposição reduzida a volatilidade**

---

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025

*Análises diárias às 21:00. Alertas só se houver mudança.*"""
    
    await client.send_message(grupo, carteira_moderada)
    print("✅ Carteira MODERADA enviada!")
    
    await asyncio.sleep(2)
    
    # 4. Carteira CONSERVADORA
    print("\n📊 Enviando Carteira CONSERVADORA...")
    
    carteira_conservadora = """📊 **CARTEIRA CONSERVADORA - OUTUBRO/2025**

**Perfil:** Baixa exposição a ações (10%)
**Risco:** Baixo
**Retorno Esperado:** 8-12% ao ano

---

**COMPOSIÇÃO (7 ativos - 100%):**

💰 **Renda Fixa (70%)**
• LFTB11 - 70.00% (Tesouro Selic)

🌎 **Internacional (20%)**
• IVVB11 - 20.00% (S&P 500)

📈 **Ações Brasileiras (10%)**

🏦 **Bancos (4%)**
• BBAS3 - 2.00% (Banco do Brasil)
• ITUB4 - 2.00% (Itaú)

⛽ **Petróleo & Gás (2%)**
• PETR4 - 2.00% (Petrobras)

⚙️ **Mineração (2%)**
• VALE3 - 2.00% (Vale)

🏭 **Equipamentos (2%)**
• WEGE3 - 2.00% (WEG)

---

**✅ 90% em ativos de baixo risco**
**✅ Apenas blue chips em ações**
**✅ Máxima proteção de capital**

---

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025

*Análises diárias às 21:00. Alertas só se houver mudança.*"""
    
    await client.send_message(grupo, carteira_conservadora)
    print("✅ Carteira CONSERVADORA enviada!")
    
    await asyncio.sleep(2)
    
    # 5. Mensagem Final
    print("\n📱 Enviando mensagem final...")
    
    mensagem_final = """✅ **Carteiras de Outubro enviadas!**

---

🎯 **Próximos Passos:**

1️⃣ **Escolha seu perfil** (AGRESSIVA, MODERADA ou CONSERVADORA)

2️⃣ **Ajuste conforme seu capital** - Os percentuais são sugestões, adapte ao seu patrimônio

3️⃣ **Aguarde os alertas** - Você será notificado quando houver mudanças

---

📊 **Monitoramento Ativo:**

Estou analisando o mercado continuamente:
• Opções: 3x ao dia (10:10, 14:00, 16:45)
• Ações/FIIs/Cripto: 1x ao dia (21:00)

Você só receberá mensagens quando houver **ação necessária**!

---

🤖 **Magnus está ON!**

Sistema de automação ativado. Bons investimentos! 🚀"""
    
    await client.send_message(grupo, mensagem_final)
    print("✅ Mensagem final enviada!")
    
    print("\n" + "=" * 80)
    print("✅ GRUPO INICIADO COM SUCESSO!")
    print("=" * 80)
    print(f"\n📱 Grupo: {grupo.title}")
    print(f"📅 Data: {data_inicio}")
    print(f"🤖 Status: ATIVO")
    
    await client.disconnect()


async def main():
    """Função principal."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 start_grupo.py <nome_do_grupo>")
        print("\nExemplo: python3 start_grupo.py 'Magnus Alerts'")
        return
    
    group_name = sys.argv[1]
    await start_grupo(group_name)


if __name__ == '__main__':
    asyncio.run(main())

