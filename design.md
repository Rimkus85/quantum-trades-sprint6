# Quantum Trades - Design System

## Visão Geral

Aplicação móvel de trading automatizado com IA. Design focado em **mobile portrait (9:16)** e **uso com uma mão**, seguindo Apple Human Interface Guidelines.

---

## Identidade Visual

### Paleta de Cores

| Token | Light Mode | Dark Mode | Uso |
|-------|------------|-----------|-----|
| **background** | #0A192F | #0A192F | Fundo principal (Azul Noturno) |
| **foreground** | #FFFFFF | #FFFFFF | Texto principal |
| **primary** | #FFD700 | #FFD700 | Destaques, CTAs (Dourado Quantum) |
| **surface** | #112240 | #112240 | Cards e superfícies elevadas |
| **muted** | #8892B0 | #8892B0 | Texto secundário |
| **border** | #233554 | #233554 | Bordas e divisores |
| **success** | #28A745 | #4ADE80 | Lucros, ganhos, alta |
| **warning** | #F59E0B | #FBBF24 | Alertas |
| **error** | #DC3545 | #F87171 | Perdas, prejuízos, baixa |

### Tipografia

- **Fonte Principal**: Montserrat
- **Títulos (H1, H2)**: Bold (700)
- **Subtítulos e Botões**: SemiBold (600)
- **Corpo de texto**: Regular (400)

### Componentes

- **Cards**: border-radius 8px-12px, background surface
- **Botões Primários**: background primary (#FFD700), text background (#0A192F)
- **Inputs**: border border, background surface, text foreground

---

## Mapa de Telas - Sprint 1 (Autenticação)

### 1. Splash Screen
- Logo Quantum Trades centralizado
- Fundo #0A192F
- Animação sutil de entrada

### 2. Tela de Boas-vindas (Welcome)
- Logo no topo
- Subtítulo: "Automatize suas estratégias com nossa IA"
- Botão "Criar Conta" (primário)
- Botão "Já tenho conta" (secundário)

### 3. Tela de Cadastro (Register)
- Header com botão voltar e título "Criar Conta"
- Campos do formulário:
  - Nome completo
  - CPF (máscara xxx.xxx.xxx-xx, validação módulo 11)
  - E-mail
  - Celular (máscara (XX) XXXXX-XXXX)
  - Telegram (com checkboxes "Mesmo do celular" e "Não tenho")
  - Corretora (seleção múltipla + campo "Outra" + checkbox "Não tenho conta")
  - Senha e Confirmar senha
- Botão "Continuar" (vai para verificação de e-mail)

### 4. Tela de Verificação de E-mail
- Instruções para verificar código enviado por e-mail
- Campo de 6 dígitos para código
- Botão "Verificar"
- Link "Reenviar código" (com cooldown de 60s)

### 5. Tela de Configuração 2FA
- Instruções para código enviado por e-mail
- Campo de 6 dígitos para código
- Botão "Verificar e Finalizar"
- Link "Reenviar código"

### 6. Tela de Login
- Logo no topo
- Campo E-mail
- Campo Senha
- Botão "Entrar" (envia código 2FA por e-mail)
- Link "Esqueci minha senha"

### 7. Tela de Recuperação de Senha (4 etapas)
- Etapa 1: Inserir e-mail
- Etapa 2: Inserir código de verificação
- Etapa 3: Definir nova senha
- Etapa 4: Confirmação de sucesso

---

## Mapa de Telas - Sprint 2 (Onboarding)

### 8. Tela de Perfil de Risco (Risk Profile)
- Header com título "Perfil de Investidor"
- Barra de progresso (5 perguntas)
- Pergunta atual com 4 opções de resposta
- Botões "Voltar" e "Próxima"
- Tela de resultado com:
  - Ícone do perfil (🛡️ Conservador, ⚖️ Moderado, 🚀 Agressivo)
  - Descrição do perfil
  - Características e recomendações
  - Botão "Continuar"

### 9. Tela de Termos e Políticas (Terms)
- Header com título "Termos e Políticas"
- Lista de documentos:
  - 📋 Termos de Uso (obrigatório)
  - 🔒 Política de Privacidade (obrigatório)
  - ⚠️ Política de Risco (obrigatório)
- Cada documento:
  - Título e resumo
  - Botão expandir para ver conteúdo completo
  - Checkbox de aceite individual
- Checkbox "Aceitar todos os documentos"
- Aviso de risco em destaque
- Botão "Continuar" (habilitado quando todos aceitos)

### 10. Tela de Seleção de Planos (Plans)
- Header com título "Escolha seu Plano"
- Banner de trial gratuito (7 dias)
- Cards de planos:
  - **Entrada** (R$ 97/mês): 1 bot, estratégias básicas, ações
  - **Médio** (R$ 197/mês): 3 bots, ações + opções, badge "Mais Popular"
  - **Top** (R$ 397/mês): ilimitado, ações + opções + cripto, badge "Premium"
- Cada card com:
  - Nome e preço
  - Lista de features com checkmarks
  - Radio button de seleção
- Garantia de 7 dias
- Botão "Assinar [Plano]"
- Link "Começar período de teste gratuito"

### 11. Tela de Trial (Trial)
- Logo centralizado
- Título "Bem-vindo ao Trial!"
- Timer de contagem regressiva (dias:horas:minutos)
- Lista de funcionalidades incluídas:
  - 🤖 1 Bot Ativo
  - 📊 Dashboard Completo
  - 🎯 Estratégias Básicas
  - 📱 Alertas no App
  - 🔒 Modo Simulação
  - 📈 Backtesting
- Banner de incentivo para upgrade
- Aviso de operações simuladas
- Botão "Começar Meu Trial Grátis"

---

## Mapa de Telas - Sprint 3 (Dashboard) - PLANEJADO

### 12. Dashboard Principal
- Header fixo com logo, status de mercado, notificações
- Cards de resumo:
  - Valor total da carteira
  - Variação do dia (%)
  - Número de operações ativas
- Gráfico de evolução patrimonial (últimos 30 dias)
- Lista de operações recentes
- Tab bar com navegação

### 13. Tela de Portfólio
- Lista de ativos em carteira
- Valor e variação de cada ativo
- Gráfico de alocação (pizza)
- Filtros por tipo (ações, opções, cripto)

### 14. Tela de Operações
- Lista de operações (abertas e fechadas)
- Filtros por período, status, ativo
- Detalhes de cada operação
- Indicadores de performance

### 15. Tela de Bots
- Lista de bots configurados
- Status de cada bot (ativo, pausado, erro)
- Botão para criar novo bot
- Configuração de estratégias

---

## Fluxos de Usuário

### Fluxo de Cadastro Completo
1. Welcome → Toca "Criar Conta"
2. Register → Preenche dados → Toca "Continuar"
3. Verify Email → Insere código → Toca "Verificar"
4. Setup 2FA → Insere código do e-mail → Toca "Verificar"
5. Risk Profile → Responde 5 perguntas → Vê resultado → Toca "Continuar"
6. Terms → Aceita todos os documentos → Toca "Continuar"
7. Plans → Seleciona plano ou trial → Toca "Assinar" ou "Trial"
8. Trial → Toca "Começar Meu Trial Grátis"
9. Dashboard → Usuário logado e pronto para usar

### Fluxo de Login
1. Welcome → Toca "Já tenho conta"
2. Login → Preenche e-mail e senha → Toca "Entrar"
3. (Código 2FA enviado por e-mail)
4. Login → Insere código 2FA → Toca "Verificar"
5. Dashboard → Usuário logado

### Fluxo de Recuperação de Senha
1. Login → Toca "Esqueci minha senha"
2. Forgot Password → Insere e-mail → Toca "Enviar código"
3. Insere código recebido por e-mail
4. Define nova senha → Toca "Redefinir"
5. Sucesso → Redirecionado para Login

---

## Diretrizes de UX

### Feedback Visual
- Botões com scale 0.97 ao pressionar
- Haptics leves em ações principais
- Loading states em todas as operações assíncronas
- Mensagens de erro claras e específicas
- Toast de erros visível no topo da tela
- Auto-scroll para campos com erro

### Validações
- CPF: formato xxx.xxx.xxx-xx com validação módulo 11
- E-mail: formato válido + verificação por código
- Celular: formato (XX) XXXXX-XXXX
- Senha: mínimo 8 caracteres, 1 maiúscula, 1 número
- Código 2FA: 6 dígitos numéricos
- Corretoras: validação contra lista de 37 corretoras conhecidas

### Acessibilidade
- Contraste adequado (texto branco em fundo escuro)
- Tamanhos de fonte legíveis (mínimo 14px corpo)
- Áreas de toque mínimo 44x44 pontos
- Checkboxes com área de toque ampliada
