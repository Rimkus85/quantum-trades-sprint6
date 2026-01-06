# Quantum Trades - Sprint 1 TODO

## QT-01: Ambiente de Desenvolvimento
- [x] Repositório Git inicializado
- [x] Estrutura de pastas configurada
- [x] Frontend React Native com setup inicial
- [x] Configuração do tema e identidade visual
- [x] Geração do logo personalizado

## QT-02: Cadastro de Usuário
- [x] Tela de boas-vindas (Welcome)
- [x] Formulário de cadastro com campos (nome, CPF, e-mail, corretora)
- [x] Validação de CPF no formato xxx.xxx.xxx-xx
- [x] Validação de e-mail
- [x] Validação de senha (mínimo 8 caracteres, 1 maiúscula, 1 número)
- [x] Armazenamento seguro dos dados do usuário
- [x] Feedback de sucesso/erro no cadastro

## QT-03: Login com 2FA
- [x] Tela de login com campos (e-mail, senha, código 2FA)
- [x] Tela de configuração do 2FA (QR Code)
- [x] Integração com Google Authenticator (TOTP)
- [x] Validação do código 2FA
- [x] Armazenamento seguro de senha (hash)
- [x] Sessão do usuário persistente

## QT-04: Recuperação de Senha
- [x] Tela de "Esqueci minha senha"
- [x] Envio de código de recuperação por e-mail (simulado)
- [x] Validação do código de recuperação
- [x] Tela para redefinição de senha
- [x] Feedback de sucesso na redefinição

## UI/UX
- [x] Splash screen com logo
- [x] Dashboard básico (placeholder para Sprint 3)
- [x] Navegação entre telas
- [x] Feedback visual (loading, erros, sucesso)
- [x] Haptics em ações principais

## Testes
- [x] Testes unitários de validação (CPF, e-mail, senha)
- [x] Testes de geração TOTP
- [x] Testes de recuperação de senha
- [x] Testes de segurança (hash de senha)

## Correções
- [x] Corrigir logo: usar PNG cortado com texto e remover texto duplicado do componente
- [x] Corrigir sobreposição de texto na tela Welcome (remover texto duplicado sobre o logo)
- [x] Alterar seleção de corretora para permitir múltiplas seleções
- [x] Corrigir problema de carregamento no Expo Go (era cache)
- [x] Implementar feedback visual de erros (toast/alert + auto-scroll para campo com erro)
- [x] Validar CPF/e-mail duplicado no cadastro
- [x] Campo "Outra" corretora: abrir campo de texto quando selecionado
- [x] Validação de corretora: verificar se existe na lista conhecida
- [x] Validação matemática de CPF (algoritmo módulo 11 + sequências inválidas)
- [x] Enviar código 2FA por e-mail ao invés de exibir QR code em tela
- [x] Remover mensagem "Validação matemática de dígitos" do campo CPF
- [x] Adicionar checkbox "Não tenho conta em nenhuma corretora" que desabilita seleção de corretoras
- [x] Adicionar campo de celular com máscara brasileira (XX) XXXXX-XXXX
- [x] Adicionar campo de usuário do Telegram com checkboxes "Mesmo do celular" e "Não tenho Telegram"
- [x] Implementar validação de e-mail via código de verificação antes de finalizar cadastro
