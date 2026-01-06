# Quantum Trades - TODO

## Sprint 1 - Autenticação (CONCLUÍDA)

### QT-01: Ambiente de Desenvolvimento
- [x] Repositório Git inicializado
- [x] Estrutura de pastas configurada
- [x] Frontend React Native com setup inicial
- [x] Configuração do tema e identidade visual
- [x] Geração do logo personalizado

### QT-02: Cadastro de Usuário
- [x] Tela de boas-vindas (Welcome)
- [x] Formulário de cadastro com campos (nome, CPF, e-mail, corretora)
- [x] Validação de CPF no formato xxx.xxx.xxx-xx
- [x] Validação de e-mail
- [x] Validação de senha (mínimo 8 caracteres, 1 maiúscula, 1 número)
- [x] Armazenamento seguro dos dados do usuário
- [x] Feedback de sucesso/erro no cadastro
- [x] Campo de celular com máscara brasileira (XX) XXXXX-XXXX
- [x] Campo de Telegram com checkboxes "Mesmo do celular" e "Não tenho Telegram"
- [x] Validação de e-mail via código de verificação
- [x] Validação matemática de CPF (algoritmo módulo 11)
- [x] Seleção múltipla de corretoras com campo "Outra"
- [x] Checkbox "Não tenho conta em nenhuma corretora"

### QT-03: Login com 2FA
- [x] Tela de login com campos (e-mail, senha, código 2FA)
- [x] Código 2FA enviado por e-mail (ao invés de QR code)
- [x] Validação do código 2FA
- [x] Armazenamento seguro de senha (hash)
- [x] Sessão do usuário persistente

### QT-04: Recuperação de Senha
- [x] Tela de "Esqueci minha senha" em 4 etapas
- [x] Envio de código de recuperação por e-mail
- [x] Validação do código de recuperação
- [x] Tela para redefinição de senha
- [x] Feedback de sucesso na redefinição

### Infraestrutura de E-mail
- [x] Serviço nodemailer no backend
- [x] Templates HTML (verificação, 2FA, recuperação, boas-vindas)
- [x] Rotas tRPC para envio de e-mail
- [ ] **DÉBITO TÉCNICO**: Configurar credenciais SMTP (aguardando contratação de serviço)

## Sprint 2 - Onboarding e Gestão de Planos (EM ANDAMENTO)

### QT-05: Questionário de Perfil de Risco
- [x] Tela de questionário com 5 perguntas
- [x] Cálculo de pontuação baseado nas respostas
- [x] Classificação: Conservador, Moderado, Agressivo
- [x] Tela de resultado com descrição do perfil
- [x] Salvamento do perfil no contexto de autenticação

### QT-06: Termos de Uso e Políticas
- [x] Tela de Termos de Uso
- [x] Tela de Política de Privacidade
- [x] Tela de Política de Risco
- [x] Checkboxes de aceite individual e "aceitar todos"
- [x] Conteúdo expandível para cada documento
- [x] Salvamento do aceite no perfil do usuário

### QT-07: Seleção de Planos de Assinatura
- [x] Tela de seleção de planos (Entrada, Médio, Top)
- [x] Cards com features de cada plano
- [x] Destaque para plano "Mais Popular"
- [x] Banner de trial gratuito
- [x] Garantia de 7 dias
- [ ] **DÉBITO TÉCNICO**: Integração com gateway de pagamento (Stripe/PagSeguro)

### QT-08: Modo Trial
- [x] Tela de boas-vindas ao trial
- [x] Timer com contagem regressiva (7 dias)
- [x] Lista de funcionalidades incluídas
- [x] Banner de incentivo para upgrade
- [x] Salvamento do status de trial no perfil

### Fluxo de Onboarding
- [x] Layout de navegação para onboarding
- [x] Integração do fluxo: Cadastro → 2FA → Perfil de Risco → Termos → Planos → Trial → Dashboard
- [x] Campos de onboarding no UserProfile (termsAccepted, riskProfile, subscriptionStatus, etc.)

## Sprint 3 - Dashboard e Portfólio (PRÓXIMA)

### QT-09: Dashboard Principal
- [ ] Visão geral do portfólio
- [ ] Saldo total e variação
- [ ] Gráfico de evolução patrimonial
- [ ] Indicadores de performance (retorno, win rate)

### QT-10: Listagem de Operações
- [ ] Lista de operações recentes
- [ ] Filtros por período, ativo, status
- [ ] Detalhes da operação

### QT-11: Gestão de Bots
- [ ] Lista de bots configurados
- [ ] Status de cada bot (ativo, pausado, erro)
- [ ] Configuração de estratégias

### QT-12: Alertas e Notificações
- [ ] Central de alertas
- [ ] Configuração de notificações
- [ ] Integração com Telegram

## Testes
- [x] Testes unitários de validação (CPF, e-mail, senha)
- [x] Testes de geração TOTP
- [x] Testes de recuperação de senha
- [x] Testes de segurança (hash de senha)
- [ ] Testes de fluxo de onboarding
- [ ] Testes de integração com backend

## UI/UX
- [x] Splash screen com logo
- [x] Navegação entre telas
- [x] Feedback visual (loading, erros, sucesso)
- [x] Haptics em ações principais
- [x] Toast de erros visível no topo
- [x] Auto-scroll para campos com erro
