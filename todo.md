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

## Sprint 2 - Onboarding e Gestão de Planos (CONCLUÍDA)

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
- [x] Testes de onboarding (27 testes passando)

## Sprint 3 - Dashboard e Visualização de Dados (CONCLUÍDA)

### QT-09: Dashboard Principal com Resumo da Carteira
- [x] Cards de resumo: valor total, retorno, número de trades
- [x] Dados mockados inicialmente (preparado para integração futura)
- [x] Indicadores de variação (positivo/negativo com cores)
- [x] Header com saudação ao usuário e status do mercado
- [x] Pull-to-refresh para atualizar dados
- [x] Estatísticas rápidas: Operações, Win Rate, Retorno Médio

### QT-10: Distribuição do Portfólio por Classe de Ativo
- [x] Cards para cada classe: Ações, Opções, Cripto
- [x] Percentual de alocação por classe
- [x] Funcionalidade de expandir para ver detalhes dos ativos
- [x] Gráfico de rosca (donut) com distribuição
- [x] Tela dedicada de Portfólio com detalhamento completo

### QT-11: Lista de Operações Recentes
- [x] Tabela com 10 operações mais recentes
- [x] Colunas: ativo, tipo, quantidade, preço, data, status
- [x] Indicadores visuais de compra/venda e lucro/prejuízo
- [x] Link para ver todas as operações
- [x] Tela dedicada de Operações com filtros
- [x] Modal de detalhes da operação

### QT-12: Gráfico de Performance da Carteira
- [x] Gráfico de linha com evolução patrimonial
- [x] Seletor de período (1S, 1M, 3M, 1A, MAX)
- [x] Componente LineChart com react-native-svg
- [x] Gradiente e ponto destacado no final

### Navegação e Layout
- [x] Tab bar com ícones: Dashboard, Portfólio, Operações, Menu
- [x] Header fixo com logo e notificações
- [x] Pull-to-refresh para atualizar dados
- [x] Tela de Menu/Perfil do usuário
- [x] Tela de Notificações
- [x] Registro da rota (onboarding) no root layout

### Testes Sprint 3
- [x] Testes de dados do portfólio (5 testes)
- [x] Testes de estatísticas de trading (5 testes)
- [x] Testes de classes de ativos (4 testes)
- [x] Testes de ativos individuais (4 testes)
- [x] Testes de operações recentes (9 testes)
- [x] Testes de gráfico de performance (10 testes)
- [x] Testes de integração (3 testes)
- [x] Total: 42 testes passando

### Correções
- [x] Corrigido erro "Failed to download remote update" no Expo Go
- [x] Adicionada rota (onboarding) no app/_layout.tsx

## Melhorias de UX/UI (CONCLUÍDA)

### Melhorias Visuais e Interação
- [x] Opção de expansão rotacional do gráfico no dashboard (modo paisagem)
- [x] Alterar cores amarelas dos ícones e seleção do menu para branco
- [x] Implementar efeitos de transição suaves entre telas (fadeSlide animation)
- [x] Animações de entrada/saída de componentes (AnimatedScreen, AnimatedCard)
- [x] Transições de navegação fluidas com spring animations
- [x] Componente ExpandableChart com rotação automática para paisagem
- [x] Componente SlideTransition para drilldown ao clicar
- [x] DrilldownCard com zoom e slide

## Sprint 4 - Motor de IA e Bots (PRÓXIMA)

### QT-13: Motor de Decisão IA v1
- [ ] Implementação em Python
- [ ] Setups básicos: Cruzamento de Médias, IFR2

### QT-14: Orquestrador de Ordens
- [ ] Modo DEMO para testes
- [ ] Salvamento de ordens no banco

### QT-15: Listagem de Bots
- [ ] Tela com lista de bots
- [ ] Status: ativo, pausado, erro

### QT-16: Criação de Bots
- [ ] Formulário de configuração
- [ ] Seleção de estratégia

## Sprint 5 - Integrações e Alertas (FUTURA)

### QT-17: Integração Cedro OMS
- [ ] Adapter para Cedro OMS
- [ ] Conexão com sandbox

### QT-18: Alertas Telegram
- [ ] Integração com API do Telegram
- [ ] Serviço de notificação

### QT-19: Alertas de Preço
- [ ] Cadastro de alertas
- [ ] Monitoramento de preços

## Testes Totais
- [x] Testes de autenticação (12 testes)
- [x] Testes de onboarding (27 testes)
- [x] Testes de dashboard (42 testes)
- [x] **Total: 81 testes passando**

## UI/UX
- [x] Splash screen com logo
- [x] Navegação entre telas
- [x] Feedback visual (loading, erros, sucesso)
- [x] Haptics em ações principais
- [x] Toast de erros visível no topo
- [x] Auto-scroll para campos com erro
- [x] Gráficos interativos (LineChart, DonutChart, ExpandableChart)
- [x] Pull-to-refresh em todas as listas
- [x] Transições slide com drilldown
- [x] Animações spring suaves

## Débitos Técnicos
- [ ] Configurar credenciais SMTP para envio de e-mail
- [ ] Integração com gateway de pagamento (Stripe/PagSeguro)
- [ ] Integração com APIs de mercado reais (B3, Cripto)
- [ ] Substituir dados mockados por dados reais do backend


## Correções Urgentes (CONCLUÍDA)
- [x] Corrigir erro de assets do Expo (limpar cache e reinstalar)
- [x] Documentar bypass de código de verificação (qualquer 6 dígitos funciona)
- [x] Criar CREDENCIAIS_TESTE.md com instruções completas

## Correção de Validação de E-mail (CONCLUÍDA)
- [x] Corrigir função verifyEmailCode para aceitar qualquer código de 6 dígitos

## Correção de Erro de Comunicação Expo (CONCLUÍDA)
- [x] Investigar erro "Failed to download remote update"
- [x] Reiniciar servidor Metro completamente
- [x] Verificar conectividade e assets

## Correções de Gráfico e UX (CONCLUÍDA)
- [x] Rótulos de data já existiam no eixo X do gráfico
- [x] Corrigir distorção do gráfico em modo horizontal (dimensões dinâmicas)
- [x] Fazer gráfico expandir para tela cheia no modal (60% largura em paisagem)
- [x] Documentar campo "variação" nos cards de operações (docs/CAMPO_VARIACAO.md)

## Preparação para Produção (CONCLUÍDA)
- [x] Documentar arquitetura de integração com APIs reais (docs/INTEGRACAO_PRODUCAO.md)
- [x] Definir endpoints e autenticação para B3/corretoras (Cedro OMS, Binance)
- [x] Planejar estrutura de dados real vs mock (DataProvider interface)
- [x] Criar roadmap de implementação em 6 fases (6-10 semanas)
