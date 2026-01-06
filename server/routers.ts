import { z } from "zod";
import { COOKIE_NAME } from "../shared/const.js";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import {
  sendVerificationEmail,
  sendTwoFactorEmail,
  sendPasswordResetEmail,
  sendWelcomeEmail,
} from "./email";

export const appRouter = router({
  // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Rotas de E-mail
  email: router({
    // Enviar código de verificação de e-mail (cadastro)
    sendVerification: publicProcedure
      .input(
        z.object({
          email: z.string().email(),
          name: z.string().min(1),
          code: z.string().length(6),
        })
      )
      .mutation(async ({ input }) => {
        const result = await sendVerificationEmail(input.email, input.name, input.code);
        return result;
      }),

    // Enviar código 2FA por e-mail
    sendTwoFactor: publicProcedure
      .input(
        z.object({
          email: z.string().email(),
          name: z.string().min(1),
          code: z.string().length(6),
        })
      )
      .mutation(async ({ input }) => {
        const result = await sendTwoFactorEmail(input.email, input.name, input.code);
        return result;
      }),

    // Enviar código de recuperação de senha
    sendPasswordReset: publicProcedure
      .input(
        z.object({
          email: z.string().email(),
          name: z.string().min(1),
          code: z.string().length(6),
        })
      )
      .mutation(async ({ input }) => {
        const result = await sendPasswordResetEmail(input.email, input.name, input.code);
        return result;
      }),

    // Enviar e-mail de boas-vindas
    sendWelcome: publicProcedure
      .input(
        z.object({
          email: z.string().email(),
          name: z.string().min(1),
        })
      )
      .mutation(async ({ input }) => {
        const result = await sendWelcomeEmail(input.email, input.name);
        return result;
      }),
  }),
});

export type AppRouter = typeof appRouter;
