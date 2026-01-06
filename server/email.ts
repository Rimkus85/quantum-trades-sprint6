/**
 * Serviço de E-mail - Quantum Trades
 * 
 * Este módulo gerencia o envio de e-mails transacionais.
 * 
 * CONFIGURAÇÃO (Débito Técnico):
 * Configure as seguintes variáveis de ambiente no painel administrativo:
 * - SMTP_HOST: Servidor SMTP (ex: smtp.gmail.com, smtp.sendgrid.net)
 * - SMTP_PORT: Porta SMTP (ex: 587 para TLS, 465 para SSL)
 * - SMTP_USER: Usuário/e-mail de autenticação
 * - SMTP_PASS: Senha ou API key
 * - SMTP_FROM: E-mail remetente (ex: noreply@quantumtrades.com.br)
 * - SMTP_FROM_NAME: Nome do remetente (ex: Quantum Trades)
 */

import nodemailer from "nodemailer";
import type { Transporter } from "nodemailer";

// Configuração do transporter (será criado sob demanda)
let transporter: Transporter | null = null;

// Verifica se as configurações de SMTP estão disponíveis
function isEmailConfigured(): boolean {
  return !!(
    process.env.SMTP_HOST &&
    process.env.SMTP_PORT &&
    process.env.SMTP_USER &&
    process.env.SMTP_PASS
  );
}

// Cria ou retorna o transporter existente
function getTransporter(): Transporter | null {
  if (!isEmailConfigured()) {
    console.warn("[EMAIL] SMTP não configurado. E-mails serão simulados no console.");
    return null;
  }

  if (!transporter) {
    transporter = nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || "587"),
      secure: process.env.SMTP_PORT === "465", // true para 465, false para outras portas
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    });
  }

  return transporter;
}

// Interface para opções de e-mail
interface EmailOptions {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

// Função principal de envio de e-mail
export async function sendEmail(options: EmailOptions): Promise<{ success: boolean; error?: string }> {
  const transport = getTransporter();
  
  const fromName = process.env.SMTP_FROM_NAME || "Quantum Trades";
  const fromEmail = process.env.SMTP_FROM || "noreply@quantumtrades.com.br";
  
  if (!transport) {
    // Modo de simulação - apenas loga no console
    console.log("═══════════════════════════════════════════════════════════");
    console.log("[EMAIL SIMULADO]");
    console.log(`Para: ${options.to}`);
    console.log(`De: ${fromName} <${fromEmail}>`);
    console.log(`Assunto: ${options.subject}`);
    console.log("───────────────────────────────────────────────────────────");
    console.log(options.text || options.html.replace(/<[^>]*>/g, ""));
    console.log("═══════════════════════════════════════════════════════════");
    return { success: true };
  }

  try {
    await transport.sendMail({
      from: `"${fromName}" <${fromEmail}>`,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
    });
    
    console.log(`[EMAIL] Enviado com sucesso para ${options.to}`);
    return { success: true };
  } catch (error) {
    console.error("[EMAIL] Erro ao enviar:", error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : "Erro desconhecido ao enviar e-mail" 
    };
  }
}

// Templates de e-mail

/**
 * Template: Verificação de E-mail (Cadastro)
 */
export function emailVerificationTemplate(name: string, code: string): { subject: string; html: string; text: string } {
  const subject = `[Quantum Trades] Código de verificação: ${code}`;
  
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verificação de E-mail</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0A192F; font-family: 'Montserrat', Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0A192F;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #112240; border-radius: 12px; overflow: hidden;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding: 40px 40px 20px;">
              <img src="https://manus.storage.googleapis.com/quantum-trades-logo.png" alt="Quantum Trades" width="180" style="display: block;">
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 20px 40px;">
              <h1 style="color: #FFD700; font-size: 24px; font-weight: 700; margin: 0 0 20px; text-align: center;">
                Verifique seu e-mail
              </h1>
              
              <p style="color: #FFFFFF; font-size: 16px; line-height: 24px; margin: 0 0 20px;">
                Olá <strong>${name}</strong>,
              </p>
              
              <p style="color: #8892B0; font-size: 14px; line-height: 22px; margin: 0 0 30px;">
                Bem-vindo ao Quantum Trades! Para completar seu cadastro, use o código de verificação abaixo:
              </p>
              
              <!-- Code Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center">
                    <div style="background-color: #0A192F; border: 2px solid #FFD700; border-radius: 8px; padding: 20px 40px; display: inline-block;">
                      <span style="color: #FFD700; font-size: 32px; font-weight: 700; letter-spacing: 8px;">${code}</span>
                    </div>
                  </td>
                </tr>
              </table>
              
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 30px 0 0; text-align: center;">
                Este código expira em <strong style="color: #FFFFFF;">10 minutos</strong>.
              </p>
              
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 10px 0 0; text-align: center;">
                Se você não solicitou este código, ignore este e-mail.
              </p>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 30px 40px; border-top: 1px solid #233554;">
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 0; text-align: center;">
                © ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.<br>
                Plataforma de Trading Autônomo com IA
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();

  const text = `
Quantum Trades - Verificação de E-mail

Olá ${name},

Bem-vindo ao Quantum Trades! Para completar seu cadastro, use o código de verificação abaixo:

${code}

Este código expira em 10 minutos.

Se você não solicitou este código, ignore este e-mail.

© ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
  `.trim();

  return { subject, html, text };
}

/**
 * Template: Código 2FA por E-mail
 */
export function twoFactorEmailTemplate(name: string, code: string): { subject: string; html: string; text: string } {
  const subject = `[Quantum Trades] Seu código de acesso: ${code}`;
  
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Código de Acesso</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0A192F; font-family: 'Montserrat', Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0A192F;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #112240; border-radius: 12px; overflow: hidden;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding: 40px 40px 20px;">
              <img src="https://manus.storage.googleapis.com/quantum-trades-logo.png" alt="Quantum Trades" width="180" style="display: block;">
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 20px 40px;">
              <h1 style="color: #FFD700; font-size: 24px; font-weight: 700; margin: 0 0 20px; text-align: center;">
                Código de Acesso
              </h1>
              
              <p style="color: #FFFFFF; font-size: 16px; line-height: 24px; margin: 0 0 20px;">
                Olá <strong>${name}</strong>,
              </p>
              
              <p style="color: #8892B0; font-size: 14px; line-height: 22px; margin: 0 0 30px;">
                Use o código abaixo para configurar a autenticação de dois fatores na sua conta:
              </p>
              
              <!-- Code Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center">
                    <div style="background-color: #0A192F; border: 2px solid #FFD700; border-radius: 8px; padding: 20px 40px; display: inline-block;">
                      <span style="color: #FFD700; font-size: 32px; font-weight: 700; letter-spacing: 8px;">${code}</span>
                    </div>
                  </td>
                </tr>
              </table>
              
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 30px 0 0; text-align: center;">
                Este código expira em <strong style="color: #FFFFFF;">5 minutos</strong>.
              </p>
            </td>
          </tr>
          
          <!-- Security Notice -->
          <tr>
            <td style="padding: 0 40px 30px;">
              <div style="background-color: #0A192F; border-radius: 8px; padding: 16px;">
                <p style="color: #FFD700; font-size: 12px; font-weight: 600; margin: 0 0 8px;">
                  🔒 Dica de Segurança
                </p>
                <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 0;">
                  Nunca compartilhe este código com ninguém. A equipe do Quantum Trades nunca solicitará seu código por telefone ou mensagem.
                </p>
              </div>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 30px 40px; border-top: 1px solid #233554;">
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 0; text-align: center;">
                © ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();

  const text = `
Quantum Trades - Código de Acesso

Olá ${name},

Use o código abaixo para configurar a autenticação de dois fatores na sua conta:

${code}

Este código expira em 5 minutos.

🔒 Dica de Segurança: Nunca compartilhe este código com ninguém. A equipe do Quantum Trades nunca solicitará seu código por telefone ou mensagem.

© ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
  `.trim();

  return { subject, html, text };
}

/**
 * Template: Recuperação de Senha
 */
export function passwordResetTemplate(name: string, code: string): { subject: string; html: string; text: string } {
  const subject = `[Quantum Trades] Recuperação de senha: ${code}`;
  
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recuperação de Senha</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0A192F; font-family: 'Montserrat', Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0A192F;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #112240; border-radius: 12px; overflow: hidden;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding: 40px 40px 20px;">
              <img src="https://manus.storage.googleapis.com/quantum-trades-logo.png" alt="Quantum Trades" width="180" style="display: block;">
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 20px 40px;">
              <h1 style="color: #FFD700; font-size: 24px; font-weight: 700; margin: 0 0 20px; text-align: center;">
                Recuperação de Senha
              </h1>
              
              <p style="color: #FFFFFF; font-size: 16px; line-height: 24px; margin: 0 0 20px;">
                Olá <strong>${name}</strong>,
              </p>
              
              <p style="color: #8892B0; font-size: 14px; line-height: 22px; margin: 0 0 30px;">
                Recebemos uma solicitação para redefinir a senha da sua conta. Use o código abaixo para continuar:
              </p>
              
              <!-- Code Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                <tr>
                  <td align="center">
                    <div style="background-color: #0A192F; border: 2px solid #FFD700; border-radius: 8px; padding: 20px 40px; display: inline-block;">
                      <span style="color: #FFD700; font-size: 32px; font-weight: 700; letter-spacing: 8px;">${code}</span>
                    </div>
                  </td>
                </tr>
              </table>
              
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 30px 0 0; text-align: center;">
                Este código expira em <strong style="color: #FFFFFF;">15 minutos</strong>.
              </p>
              
              <p style="color: #DC3545; font-size: 12px; line-height: 18px; margin: 20px 0 0; text-align: center;">
                Se você não solicitou a recuperação de senha, altere sua senha imediatamente e entre em contato com nosso suporte.
              </p>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 30px 40px; border-top: 1px solid #233554;">
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 0; text-align: center;">
                © ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();

  const text = `
Quantum Trades - Recuperação de Senha

Olá ${name},

Recebemos uma solicitação para redefinir a senha da sua conta. Use o código abaixo para continuar:

${code}

Este código expira em 15 minutos.

⚠️ Se você não solicitou a recuperação de senha, altere sua senha imediatamente e entre em contato com nosso suporte.

© ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
  `.trim();

  return { subject, html, text };
}

/**
 * Template: Boas-vindas após cadastro completo
 */
export function welcomeEmailTemplate(name: string): { subject: string; html: string; text: string } {
  const subject = `Bem-vindo ao Quantum Trades, ${name}! 🚀`;
  
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bem-vindo ao Quantum Trades</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0A192F; font-family: 'Montserrat', Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0A192F;">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #112240; border-radius: 12px; overflow: hidden;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding: 40px 40px 20px;">
              <img src="https://manus.storage.googleapis.com/quantum-trades-logo.png" alt="Quantum Trades" width="180" style="display: block;">
            </td>
          </tr>
          
          <!-- Content -->
          <tr>
            <td style="padding: 20px 40px;">
              <h1 style="color: #FFD700; font-size: 28px; font-weight: 700; margin: 0 0 20px; text-align: center;">
                Bem-vindo ao Quantum Trades! 🚀
              </h1>
              
              <p style="color: #FFFFFF; font-size: 16px; line-height: 24px; margin: 0 0 20px;">
                Olá <strong>${name}</strong>,
              </p>
              
              <p style="color: #8892B0; font-size: 14px; line-height: 22px; margin: 0 0 20px;">
                Sua conta foi criada com sucesso! Agora você tem acesso à plataforma de trading autônomo mais avançada do mercado.
              </p>
              
              <!-- Features -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 30px 0;">
                <tr>
                  <td style="padding: 12px; background-color: #0A192F; border-radius: 8px; margin-bottom: 10px;">
                    <p style="color: #FFD700; font-size: 14px; font-weight: 600; margin: 0 0 4px;">
                      🤖 IA Avançada
                    </p>
                    <p style="color: #8892B0; font-size: 12px; margin: 0;">
                      Análise preditiva de mercado em tempo real
                    </p>
                  </td>
                </tr>
                <tr><td style="height: 10px;"></td></tr>
                <tr>
                  <td style="padding: 12px; background-color: #0A192F; border-radius: 8px;">
                    <p style="color: #FFD700; font-size: 14px; font-weight: 600; margin: 0 0 4px;">
                      ⏰ Trading 24/7
                    </p>
                    <p style="color: #8892B0; font-size: 12px; margin: 0;">
                      Opera automaticamente enquanto você descansa
                    </p>
                  </td>
                </tr>
                <tr><td style="height: 10px;"></td></tr>
                <tr>
                  <td style="padding: 12px; background-color: #0A192F; border-radius: 8px;">
                    <p style="color: #FFD700; font-size: 14px; font-weight: 600; margin: 0 0 4px;">
                      🌍 Multi-Mercados
                    </p>
                    <p style="color: #8892B0; font-size: 12px; margin: 0;">
                      B3, NYSE, NASDAQ e Crypto em uma única plataforma
                    </p>
                  </td>
                </tr>
              </table>
              
              <p style="color: #8892B0; font-size: 14px; line-height: 22px; margin: 0 0 30px; text-align: center;">
                Acesse o app e comece a explorar suas possibilidades!
              </p>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 30px 40px; border-top: 1px solid #233554;">
              <p style="color: #8892B0; font-size: 12px; line-height: 18px; margin: 0; text-align: center;">
                © ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.<br>
                <a href="https://quantumtrades.com.br" style="color: #FFD700; text-decoration: none;">quantumtrades.com.br</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();

  const text = `
Bem-vindo ao Quantum Trades! 🚀

Olá ${name},

Sua conta foi criada com sucesso! Agora você tem acesso à plataforma de trading autônomo mais avançada do mercado.

✨ O que você pode fazer:

🤖 IA Avançada - Análise preditiva de mercado em tempo real
⏰ Trading 24/7 - Opera automaticamente enquanto você descansa
🌍 Multi-Mercados - B3, NYSE, NASDAQ e Crypto em uma única plataforma

Acesse o app e comece a explorar suas possibilidades!

© ${new Date().getFullYear()} Quantum Trades. Todos os direitos reservados.
quantumtrades.com.br
  `.trim();

  return { subject, html, text };
}

// Funções de conveniência para envio

export async function sendVerificationEmail(to: string, name: string, code: string) {
  const template = emailVerificationTemplate(name, code);
  return sendEmail({ to, ...template });
}

export async function sendTwoFactorEmail(to: string, name: string, code: string) {
  const template = twoFactorEmailTemplate(name, code);
  return sendEmail({ to, ...template });
}

export async function sendPasswordResetEmail(to: string, name: string, code: string) {
  const template = passwordResetTemplate(name, code);
  return sendEmail({ to, ...template });
}

export async function sendWelcomeEmail(to: string, name: string) {
  const template = welcomeEmailTemplate(name);
  return sendEmail({ to, ...template });
}
