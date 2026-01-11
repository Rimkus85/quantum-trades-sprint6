# Credenciais de Teste - Quantum Trades

## 🔑 Bypass de Código de Verificação

O sistema **já aceita qualquer código de 6 dígitos** para verificação de e-mail e 2FA.

**Código universal recomendado:** `123456`

Isso funciona porque a função `validateTOTPCode` em `lib/auth-context.tsx` (linha 94-98) está configurada para ambiente de desenvolvimento:

```typescript
function validateTOTPCode(secret: string, code: string): boolean {
  // In production, implement proper TOTP validation
  // For demo, accept any 6-digit code
  return /^\d{6}$/.test(code);
}
```

## 📝 Como Criar Conta de Teste

1. **Abra o app** no Expo Go
2. **Toque em "Criar Conta"**
3. **Preencha o formulário:**
   - Nome: Qualquer nome
   - CPF: Use um CPF válido (ex: `123.456.789-09`)
   - E-mail: Qualquer e-mail (ex: `teste@quantum.com`)
   - Celular: `(11) 98765-4321`
   - Telegram: Marque "Mesmo do celular"
   - Corretoras: Selecione qualquer uma
   - Senha: Mínimo 8 caracteres, 1 maiúscula, 1 número (ex: `Teste@123`)

4. **Código de verificação:** Digite `123456` (ou qualquer 6 dígitos)
5. **Código 2FA:** Digite `123456` novamente
6. **Pronto!** Você será redirecionado para o onboarding

## 👥 Usuários Pré-Cadastrados (AsyncStorage)

Como o sistema usa AsyncStorage local, **não há usuários pré-cadastrados**. Cada dispositivo mantém seus próprios dados.

Para testar o **login**, você precisa:
1. Criar uma conta primeiro (passos acima)
2. Fazer logout
3. Fazer login com as mesmas credenciais

## 🔐 Validação de CPF

O sistema valida CPF usando o algoritmo Módulo 11. CPFs válidos para teste:

- `123.456.789-09` ✅
- `111.444.777-35` ✅
- `123.456.789-10` ❌ (inválido)

## 📧 E-mails de Verificação

**Importante:** O sistema **NÃO envia e-mails reais** porque as credenciais SMTP não estão configuradas.

O código de verificação é apenas **simulado** e aceita qualquer sequência de 6 dígitos.

## 🚀 Fluxo Completo de Teste

1. **Welcome Screen** → Toque em "Criar Conta"
2. **Cadastro** → Preencha e envie
3. **Verificação de E-mail** → Digite `123456`
4. **Setup 2FA** → Digite `123456`
5. **Perfil de Risco** → Responda 5 perguntas
6. **Termos e Políticas** → Aceite todos
7. **Seleção de Plano** → Escolha um plano
8. **Modo Trial** → Inicie trial gratuito
9. **Dashboard** → Explore o app!

## 🛠️ Troubleshooting

### Erro "Sessão expirada"
- Limpe o cache do AsyncStorage
- Crie uma nova conta

### Erro "Código inválido"
- Certifique-se de digitar exatamente 6 dígitos
- Qualquer combinação funciona: `000000`, `111111`, `123456`, etc.

### Erro de carregamento no Expo Go
- Feche completamente o Expo Go
- Limpe o cache do app
- Escaneie o QR code novamente

## 📱 Link do Expo Go

```
exps://8081-i0bimae93gw0q360vs0f9-03545e4d.us1.manus.computer
```

## 🔄 Reset Completo

Para começar do zero:

```javascript
// No console do React Native Debugger ou DevTools
import AsyncStorage from '@react-native-async-storage/async-storage';
await AsyncStorage.clear();
```

Ou reinstale o app no Expo Go.
