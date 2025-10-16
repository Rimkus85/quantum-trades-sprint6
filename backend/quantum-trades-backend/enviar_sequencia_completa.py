#!/usr/bin/env python3
import os, asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

async def enviar_sequencia_completa():
    client = TelegramClient('magnus_session', os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
    await client.connect()
    
    # Encontrar grupo
    dialogs = await client.get_dialogs()
    grupo = None
    for d in dialogs:
        if 'Magnus Wealth' in d.title:
            grupo = d
            break
    
    if not grupo:
        print("❌ Grupo não encontrado")
        await client.disconnect()
        return
    
    print(f"✅ Grupo encontrado: {grupo.title}\n")
    print("=" * 80)
    
    # ==================== 1. BOAS-VINDAS ====================
    print("1️⃣ Enviando BOAS-VINDAS...")
    
    boas_vindas = """🤖 **Olá! Sou o Magnus!**

Sou uma **IA de assessoria financeira** alimentada pela **Quantum Trade**, a super mega blaster ferramenta de automação do mercado financeiro que possibilita executar análises, monitoramento e recomendações de forma **totalmente autônoma**!

---

🏆 **Bem-vindo ao Grupo Exclusivo!**

Você faz parte de um **seleto grupo** que terá acesso privilegiado às minhas análises e recomendações em tempo real.

Minhas análises são baseadas em:
✅ Análise fundamentalista completa (balanços, indicadores, múltiplos)
✅ Análise técnica (tendências, suportes, resistências)
✅ Análise setorial e macroeconômica
✅ Monitoramento contínuo do mercado 24/7

---

📊 **O que você vai receber aqui:**

**1️⃣ CARTEIRAS RECOMENDADAS**

Você receberá **3 perfis de carteiras** com ações, FIIs e ETFs:

📈 **AGRESSIVA** - Para quem busca maior retorno
• 46% em ações brasileiras selecionadas
• 25% em SP500 (diversificação internacional)
• 25% em Tesouro Selic (proteção)
• Retorno esperado: 15-25% ao ano

📊 **MODERADA** - Perfil balanceado
• 25% em ações brasileiras blue chips
• 25% em SP500 (diversificação internacional)
• 50% em Tesouro Selic (segurança)
• Retorno esperado: 10-15% ao ano

🛡️ **CONSERVADORA** - Maior segurança
• 10% em ações de primeira linha
• 20% em SP500 (exposição controlada)
• 70% em Tesouro Selic (máxima proteção)
• Retorno esperado: 8-12% ao ano

**Análise diária:** Todos os dias às **21:00 (horário de Brasília)**
**Alertas:** Só envio mensagem quando houver **mudança real** (entrada ou saída)

---

**2️⃣ OPÇÕES**

Recomendações de operações com opções baseadas em análise técnica e identificação de oportunidades:

🟢 **MONTAGEM** - Nova posição identificada
🔄 **ROLAGEM** - Ajuste de posição existente
🔴 **DESMONTAGEM** - Realização de lucro

**Análises diárias:**
• 🕙 **10:10** - Logo após abertura do mercado
• 🕑 **14:00** - Meio do dia
• 🕔 **16:45** - Antes do fechamento

**Alertas:** Só envio quando houver **oportunidade real**

---

**3️⃣ CRIPTOMOEDAS**

Análises e oportunidades em criptoativos baseadas em análise técnica:

₿ Bitcoin
Ξ Ethereum
🪙 Altcoins selecionadas

**Análise diária:** Todos os dias às **21:00 (horário de Brasília)**
**Alertas:** Só envio quando houver **oportunidade de entrada ou saída**

---

**4️⃣ RELATÓRIOS MENSAIS**

Todo **final de mês**, você receberá um **relatório completo em PDF** com:

📈 Performance de cada carteira
📊 Resultados acumulados desde o início
🎯 Taxa de acerto em opções
🏆 Melhores trades do mês
📉 Contexto de mercado
🔮 Perspectivas para o próximo mês

---

⚠️ **IMPORTANTE - Como funciona a dinâmica:**

🔕 **SEM SPAM!**

Eu **NÃO vou encher** o grupo de mensagens!

✅ Só envio alertas quando há **mudanças reais**
✅ Análises acontecem automaticamente em **background**
✅ Você só recebe notificação quando **precisa agir**

📅 **Rotina Automática:**

**Segunda a Sexta:**
• 10:10 - Análise de opções (silenciosa)
• 14:00 - Análise de opções (silenciosa)
• 16:45 - Análise de opções (silenciosa)
• 21:00 - Análise de ações/FIIs/cripto (silenciosa)

**Final do Mês:**
• Relatório completo em PDF

**Início do Mês:**
• Carteiras atualizadas (se houver mudanças)

---

🚀 **Vamos começar!**

Logo abaixo, vou enviar as **CARTEIRAS DE OUTUBRO/2025** com análise detalhada de cada ativo!

Escolha o perfil que mais se adequa ao seu objetivo e tolerância a risco.

---

⚠️ **Aviso Legal:**

As recomendações aqui apresentadas são baseadas em análises automatizadas e **não constituem recomendação de investimento**. Sempre consulte um profissional certificado e invista apenas o que pode perder.

---

**🤖 Magnus AI**
*Powered by Quantum Trade*
Iniciado em: 16/10/2025

---

*Dúvidas? Perguntas? Fique à vontade! Estou aqui para ajudar!* 💬"""
    
    await client.send_message(grupo, boas_vindas)
    print("✅ Boas-vindas enviada!\n")
    await asyncio.sleep(3)
    
    # ==================== 2. CARTEIRA AGRESSIVA ====================
    print("2️⃣ Enviando CARTEIRA AGRESSIVA...")
    
    agressiva = """📊 **CARTEIRA AGRESSIVA - OUTUBRO/2025**

**Perfil:** Alta exposição a ações (46.67%)
**Risco:** Alto
**Retorno Esperado:** 15-25% ao ano

---

**COMPOSIÇÃO (17 ativos - 100%):**

🌎 **Internacional (25%)**
• IVVB11 - 25.00% (S&P 500)

💰 **Renda Fixa (25%)**
• LFTB11 - 25.00% (Tesouro Selic)

📈 **Ações Brasileiras (50%):**

🏦 **Bancos (10%)**
• BBAS3 - 3.33%
• BRSR6 - 3.33%
• BMGB4 - 3.33%

⛽ **Petróleo (6.66%)**
• PETR4 - 3.33%
• PRIO3 - 3.33%

⚙️ **Siderurgia/Mineração (9.99%)**
• USIM5 - 3.33%
• GOAU4 - 3.33%
• BRAP4 - 3.33%

🚚 **Logística (6.66%)**
• LOGG3 - 3.33%
• DEXP3 - 3.33%

🌾 **Agronegócio (3.33%)**
• SMTO3 - 3.33%

🔫 **Defesa (3.33%)**
• TASA4 - 3.33%

🪵 **Madeira (3.33%)**
• EUCA4 - 3.33%

🎓 **Educação (3.33%)**
• ALLD3 - 3.33%

🏭 **Máquinas (3.33%)**
• ROMI3 - 3.33%

---

✅ Diversificada em 9 setores
✅ 50% proteção (Selic + SP500)
✅ Exposição internacional

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025

*Análises diárias às 21:00. Alertas só se houver mudança.*"""
    
    await client.send_message(grupo, agressiva)
    print("✅ Carteira AGRESSIVA enviada!\n")
    await asyncio.sleep(2)
    
    # ==================== 3. CARTEIRA MODERADA ====================
    print("3️⃣ Enviando CARTEIRA MODERADA...")
    
    moderada = """📊 **CARTEIRA MODERADA - OUTUBRO/2025**

**Perfil:** Balanceada (25% ações)
**Risco:** Médio
**Retorno Esperado:** 10-15% ao ano

---

**COMPOSIÇÃO (17 ativos - 100%):**

💰 **Renda Fixa (50%)**
• LFTB11 - 50.00%

🌎 **Internacional (25%)**
• IVVB11 - 25.00%

📈 **Ações Brasileiras (25%):**

🏦 **Bancos (5%)**
• BBAS3 - 1.67%
• BRSR6 - 1.67%
• BMGB4 - 1.67%

⛽ **Petróleo (3.34%)**
• PETR4 - 1.67%
• PRIO3 - 1.67%

⚙️ **Siderurgia/Mineração (5%)**
• USIM5 - 1.67%
• GOAU4 - 1.67%
• BRAP4 - 1.67%

🚚 **Logística (3.34%)**
• LOGG3 - 1.67%
• DEXP3 - 1.67%

🌾 **Agronegócio (1.67%)**
• SMTO3 - 1.67%

🔫 **Defesa (1.67%)**
• TASA4 - 1.67%

🪵 **Madeira (1.67%)**
• EUCA4 - 1.67%

🎓 **Educação (1.67%)**
• ALLD3 - 1.67%

🏭 **Máquinas (1.67%)**
• ROMI3 - 1.67%

---

✅ 75% em ativos de baixo risco
✅ Diversificação em 9 setores
✅ Exposição reduzida a volatilidade

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025"""
    
    await client.send_message(grupo, moderada)
    print("✅ Carteira MODERADA enviada!\n")
    await asyncio.sleep(2)
    
    # ==================== 4. CARTEIRA CONSERVADORA ====================
    print("4️⃣ Enviando CARTEIRA CONSERVADORA...")
    
    conservadora = """📊 **CARTEIRA CONSERVADORA - OUTUBRO/2025**

**Perfil:** Baixa exposição a ações (10%)
**Risco:** Baixo
**Retorno Esperado:** 8-12% ao ano

---

**COMPOSIÇÃO (7 ativos - 100%):**

💰 **Renda Fixa (70%)**
• LFTB11 - 70.00%

🌎 **Internacional (20%)**
• IVVB11 - 20.00%

📈 **Ações Brasileiras (10%):**

🏦 **Bancos (4%)**
• BBAS3 - 2.00%
• ITUB4 - 2.00%

⛽ **Petróleo (2%)**
• PETR4 - 2.00%

⚙️ **Mineração (2%)**
• VALE3 - 2.00%

🏭 **Equipamentos (2%)**
• WEGE3 - 2.00%

---

✅ 90% em ativos de baixo risco
✅ Apenas blue chips
✅ Máxima proteção de capital

📅 **Validade:** Outubro/2025
⏰ **Próxima revisão:** 01/11/2025"""
    
    await client.send_message(grupo, conservadora)
    print("✅ Carteira CONSERVADORA enviada!\n")
    await asyncio.sleep(2)
    
    # ==================== 5. MENSAGEM FINAL + ARQUIVOS ====================
    print("5️⃣ Enviando MENSAGEM FINAL...")
    
    final = """✅ **Carteiras de Outubro enviadas!**

---

📄 **ARQUIVOS DISPONÍVEIS:**

1️⃣ **PDF Detalhado** (12 páginas)
• Análise fundamentalista de cada ativo
• Explicação do porquê de cada escolha
• Valores mínimos recomendados
• Como montar passo a passo

2️⃣ **Planilha Excel Interativa**
• Digite seu valor total a investir
• Cálculo automático de alocação
• 3 carteiras em abas separadas
• Pronto para usar!

---

💡 **COMO USAR A PLANILHA:**

1. Abra no Excel ou Google Sheets
2. Escolha a aba da sua carteira
3. Digite o valor total na célula amarela (B6)
4. Pronto! A planilha calcula tudo automaticamente

---

📊 **Monitoramento Ativo:**

Estou analisando o mercado continuamente:
• Opções: 3x ao dia (10:10, 14:00, 16:45)
• Ações/FIIs/Cripto: 1x ao dia (21:00)

Você só receberá mensagens quando houver **ação necessária**!

---

🤖 **Magnus está ON!**

Sistema de automação ativado. Bons investimentos! 🚀"""
    
    await client.send_message(grupo, final)
    print("✅ Mensagem final enviada!\n")
    await asyncio.sleep(2)
    
    # ==================== 6. PDF ====================
    print("6️⃣ Enviando PDF...")
    
    await client.send_file(
        grupo,
        'Carteiras_Magnus_Outubro_2025.pdf',
        caption="📊 **Análise Detalhada das Carteiras - Outubro/2025**\n\nAnálise fundamentalista completa de cada ativo!"
    )
    print("✅ PDF enviado!\n")
    await asyncio.sleep(2)
    
    # ==================== 7. EXCEL ====================
    print("7️⃣ Enviando EXCEL...")
    
    await client.send_file(
        grupo,
        'Carteiras_Magnus_Outubro_2025.xlsx',
        caption="📈 **Planilha Interativa - Calculadora de Alocação**\n\nDigite seu valor total e a planilha calcula automaticamente!"
    )
    print("✅ Excel enviado!\n")
    
    print("=" * 80)
    print("🎉 SEQUÊNCIA COMPLETA ENVIADA COM SUCESSO!")
    print("=" * 80)
    
    await client.disconnect()

asyncio.run(enviar_sequencia_completa())

