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

## Mapa de Telas - Sprint 1

### 1. Splash Screen
- Logo Quantum Trades centralizado
- Fundo #0A192F
- Animação sutil de entrada

### 2. Tela de Boas-vindas (Welcome)
- Logo no topo
- Título: "Bem-vindo ao Quantum Trades"
- Subtítulo: "Automatize suas estratégias com nossa IA"
- Botão "Criar Conta" (primário)
- Botão "Já tenho conta" (secundário)

### 3. Tela de Cadastro (Register)
- Header com botão voltar e título "Criar Conta"
- Campos do formulário:
  - Nome completo
  - CPF (máscara xxx.xxx.xxx-xx)
  - E-mail
  - Corretora (dropdown)
  - Senha
  - Confirmar senha
- Botão "Continuar" (vai para configuração 2FA)

### 4. Tela de Configuração 2FA
- Instruções para configurar Google Authenticator
- QR Code para escanear
- Campo para inserir código de verificação
- Botão "Verificar e Finalizar"

### 5. Tela de Login
- Logo no topo
- Campo E-mail
- Campo Senha
- Campo Código 2FA
- Botão "Entrar"
- Link "Esqueci minha senha"

### 6. Tela de Recuperação de Senha
- Header com botão voltar
- Campo E-mail
- Botão "Enviar código"
- (Após envio) Campo código de verificação
- Campos Nova senha e Confirmar senha
- Botão "Redefinir senha"

### 7. Dashboard (Tela Principal pós-login)
- Header fixo com logo, status de mercado, notificações
- Cards de resumo (valor carteira, retorno, trades)
- Navegação por tabs no bottom

---

## Fluxos de Usuário

### Fluxo de Cadastro
1. Welcome → Toca "Criar Conta"
2. Register → Preenche dados → Toca "Continuar"
3. Setup 2FA → Escaneia QR → Insere código → Toca "Verificar"
4. Sucesso → Redirecionado para Dashboard

### Fluxo de Login
1. Welcome → Toca "Já tenho conta"
2. Login → Preenche e-mail, senha, código 2FA → Toca "Entrar"
3. Sucesso → Redirecionado para Dashboard

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

### Validações
- CPF: formato xxx.xxx.xxx-xx com validação de dígitos
- E-mail: formato válido
- Senha: mínimo 8 caracteres, 1 maiúscula, 1 número
- Código 2FA: 6 dígitos numéricos

### Acessibilidade
- Contraste adequado (texto branco em fundo escuro)
- Tamanhos de fonte legíveis (mínimo 14px corpo)
- Áreas de toque mínimo 44x44 pontos
