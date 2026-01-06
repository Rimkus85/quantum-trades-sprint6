import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Types for user data
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  telegram: string;
  cpf: string;
  broker: string;
  riskProfile?: "conservador" | "moderado" | "agressivo";
  twoFactorEnabled: boolean;
  twoFactorSecret?: string;
  createdAt: string;
  termsAccepted?: boolean;
  privacyAccepted?: boolean;
  riskPolicyAccepted?: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  requiresTwoFactor: boolean;
  pendingEmail?: string;
}

interface AuthContextType extends AuthState {
  register: (data: RegisterData) => Promise<{ success: boolean; error?: string; requiresEmailVerification?: boolean }>;
  verifyEmailCode: (email: string, code: string) => Promise<{ success: boolean; error?: string }>;
  resendEmailCode: (email: string) => Promise<{ success: boolean; error?: string }>;
  setupTwoFactor: () => Promise<{ secret: string; qrCode: string }>;
  verifyTwoFactor: (code: string) => Promise<{ success: boolean; error?: string }>;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string; requiresTwoFactor?: boolean }>;
  verifyLoginTwoFactor: (code: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  requestPasswordReset: (email: string) => Promise<{ success: boolean; error?: string }>;
  verifyResetCode: (email: string, code: string) => Promise<{ success: boolean; error?: string }>;
  resetPassword: (email: string, code: string, newPassword: string) => Promise<{ success: boolean; error?: string }>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  pendingUser: { email: string; name: string } | null;
}

export interface RegisterData {
  name: string;
  email: string;
  phone: string;
  telegram: string;
  cpf: string;
  broker: string;
  password: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEYS = {
  USER: "@quantum_trades_user",
  AUTH_TOKEN: "@quantum_trades_token",
  PENDING_REGISTRATION: "@quantum_trades_pending_reg",
  RESET_CODES: "@quantum_trades_reset_codes",
};

// Simple hash function for demo (in production, use bcrypt on server)
function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

// Generate TOTP secret (simplified for demo)
function generateTOTPSecret(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  let secret = "";
  for (let i = 0; i < 16; i++) {
    secret += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return secret;
}

// Validate TOTP code (simplified - accepts any 6-digit code for demo)
function validateTOTPCode(secret: string, code: string): boolean {
  // In production, implement proper TOTP validation
  // For demo, accept any 6-digit code
  return /^\d{6}$/.test(code);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    requiresTwoFactor: false,
  });

  // Load user from storage on mount
  useEffect(() => {
    loadStoredUser();
  }, []);

  const loadStoredUser = async () => {
    try {
      const userJson = await AsyncStorage.getItem(STORAGE_KEYS.USER);
      const token = await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      
      if (userJson && token) {
        const user = JSON.parse(userJson) as UserProfile;
        setState({
          isAuthenticated: true,
          isLoading: false,
          user,
          requiresTwoFactor: false,
        });
      } else {
        setState(prev => ({ ...prev, isLoading: false }));
      }
    } catch (error) {
      console.error("Error loading user:", error);
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const register = useCallback(async (data: RegisterData) => {
    try {
      // Validate CPF format
      const cpfRegex = /^\d{3}\.\d{3}\.\d{3}-\d{2}$/;
      if (!cpfRegex.test(data.cpf)) {
        return { success: false, error: "CPF inválido. Use o formato: 000.000.000-00" };
      }

      // Validate email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(data.email)) {
        return { success: false, error: "E-mail inválido" };
      }

      // Validate password strength
      if (data.password.length < 8) {
        return { success: false, error: "Senha deve ter no mínimo 8 caracteres" };
      }
      if (!/[A-Z]/.test(data.password)) {
        return { success: false, error: "Senha deve conter pelo menos uma letra maiúscula" };
      }
      if (!/\d/.test(data.password)) {
        return { success: false, error: "Senha deve conter pelo menos um número" };
      }

      // Check if user already exists (email or CPF)
      const existingUsers = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(existingUsers) as Array<{ email: string; cpf: string }>;
      
      if (users.some(u => u.email === data.email)) {
        return { success: false, error: "E-mail já cadastrado", field: "email" };
      }
      
      if (users.some(u => u.cpf === data.cpf)) {
        return { success: false, error: "CPF já cadastrado", field: "cpf" };
      }

      // Generate 2FA secret and email verification code
      const twoFactorSecret = generateTOTPSecret();
      const emailVerificationCode = Math.floor(100000 + Math.random() * 900000).toString();

      // Store pending registration
      const pendingUser = {
        ...data,
        id: `user_${Date.now()}`,
        passwordHash: simpleHash(data.password),
        twoFactorSecret,
        twoFactorEnabled: false,
        emailVerified: false,
        emailVerificationCode,
        emailVerificationExpiry: Date.now() + 10 * 60 * 1000, // 10 minutes
        createdAt: new Date().toISOString(),
      };

      await AsyncStorage.setItem(STORAGE_KEYS.PENDING_REGISTRATION, JSON.stringify(pendingUser));

      // Simulate sending email (in production, call email API)
      console.log(`[EMAIL SIMULATION] Verification code for ${data.email}: ${emailVerificationCode}`);

      setState(prev => ({
        ...prev,
        pendingEmail: data.email,
      }));

      return { success: true, requiresEmailVerification: true };
    } catch (error) {
      console.error("Registration error:", error);
      return { success: false, error: "Erro ao criar conta. Tente novamente." };
    }
  }, []);

  const verifyEmailCode = useCallback(async (email: string, code: string) => {
    try {
      const pendingJson = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_REGISTRATION);
      if (!pendingJson) {
        return { success: false, error: "Sessão expirada. Faça o cadastro novamente." };
      }

      const pending = JSON.parse(pendingJson);
      
      if (pending.email !== email) {
        return { success: false, error: "E-mail não corresponde ao cadastro." };
      }

      if (Date.now() > pending.emailVerificationExpiry) {
        return { success: false, error: "Código expirado. Solicite um novo código." };
      }

      if (pending.emailVerificationCode !== code) {
        return { success: false, error: "Código inválido. Verifique e tente novamente." };
      }

      // Mark email as verified
      pending.emailVerified = true;
      await AsyncStorage.setItem(STORAGE_KEYS.PENDING_REGISTRATION, JSON.stringify(pending));

      setState(prev => ({
        ...prev,
        requiresTwoFactor: true,
      }));

      return { success: true };
    } catch (error) {
      console.error("Email verification error:", error);
      return { success: false, error: "Erro ao verificar código. Tente novamente." };
    }
  }, []);

  const resendEmailCode = useCallback(async (email: string) => {
    try {
      const pendingJson = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_REGISTRATION);
      if (!pendingJson) {
        return { success: false, error: "Sessão expirada. Faça o cadastro novamente." };
      }

      const pending = JSON.parse(pendingJson);
      
      if (pending.email !== email) {
        return { success: false, error: "E-mail não corresponde ao cadastro." };
      }

      // Generate new code
      const newCode = Math.floor(100000 + Math.random() * 900000).toString();
      pending.emailVerificationCode = newCode;
      pending.emailVerificationExpiry = Date.now() + 10 * 60 * 1000; // 10 minutes

      await AsyncStorage.setItem(STORAGE_KEYS.PENDING_REGISTRATION, JSON.stringify(pending));

      // Simulate sending email (in production, call email API)
      console.log(`[EMAIL SIMULATION] New verification code for ${email}: ${newCode}`);

      return { success: true };
    } catch (error) {
      console.error("Resend email code error:", error);
      return { success: false, error: "Erro ao reenviar código. Tente novamente." };
    }
  }, []);

  const setupTwoFactor = useCallback(async () => {
    try {
      const pendingJson = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_REGISTRATION);
      if (!pendingJson) {
        throw new Error("No pending registration");
      }

      const pending = JSON.parse(pendingJson);
      const secret = pending.twoFactorSecret;
      
      // Generate QR code URL for Google Authenticator
      const qrCode = `otpauth://totp/QuantumTrades:${pending.email}?secret=${secret}&issuer=QuantumTrades`;

      return { secret, qrCode };
    } catch (error) {
      console.error("2FA setup error:", error);
      throw error;
    }
  }, []);

  const verifyTwoFactor = useCallback(async (code: string) => {
    try {
      const pendingJson = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_REGISTRATION);
      if (!pendingJson) {
        return { success: false, error: "Sessão expirada. Faça o cadastro novamente." };
      }

      const pending = JSON.parse(pendingJson);

      // Validate TOTP code
      if (!validateTOTPCode(pending.twoFactorSecret, code)) {
        return { success: false, error: "Código inválido. Digite os 6 dígitos do autenticador." };
      }

      // Create user profile
      const user: UserProfile = {
        id: pending.id,
        name: pending.name,
        email: pending.email,
        phone: pending.phone || "",
        telegram: pending.telegram || "",
        cpf: pending.cpf,
        broker: pending.broker,
        twoFactorEnabled: true,
        twoFactorSecret: pending.twoFactorSecret,
        createdAt: pending.createdAt,
      };

      // Save user to storage
      const existingUsers = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(existingUsers);
      users.push({
        ...user,
        passwordHash: pending.passwordHash,
      });
      await AsyncStorage.setItem("@quantum_trades_users", JSON.stringify(users));

      // Set current user
      await AsyncStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, `token_${Date.now()}`);
      await AsyncStorage.removeItem(STORAGE_KEYS.PENDING_REGISTRATION);

      setState({
        isAuthenticated: true,
        isLoading: false,
        user,
        requiresTwoFactor: false,
      });

      return { success: true };
    } catch (error) {
      console.error("2FA verification error:", error);
      return { success: false, error: "Erro ao verificar código. Tente novamente." };
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const usersJson = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(usersJson);
      
      const user = users.find((u: any) => u.email === email);
      if (!user) {
        return { success: false, error: "E-mail ou senha incorretos" };
      }

      if (user.passwordHash !== simpleHash(password)) {
        return { success: false, error: "E-mail ou senha incorretos" };
      }

      // Store pending login for 2FA verification
      await AsyncStorage.setItem("@quantum_trades_pending_login", JSON.stringify(user));

      setState(prev => ({
        ...prev,
        requiresTwoFactor: true,
        pendingEmail: email,
      }));

      return { success: true, requiresTwoFactor: true };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: "Erro ao fazer login. Tente novamente." };
    }
  }, []);

  const verifyLoginTwoFactor = useCallback(async (code: string) => {
    try {
      const pendingJson = await AsyncStorage.getItem("@quantum_trades_pending_login");
      if (!pendingJson) {
        return { success: false, error: "Sessão expirada. Faça login novamente." };
      }

      const pending = JSON.parse(pendingJson);

      if (!validateTOTPCode(pending.twoFactorSecret, code)) {
        return { success: false, error: "Código inválido" };
      }

      const user: UserProfile = {
        id: pending.id,
        name: pending.name,
        email: pending.email,
        phone: pending.phone || "",
        telegram: pending.telegram || "",
        cpf: pending.cpf,
        broker: pending.broker,
        riskProfile: pending.riskProfile,
        twoFactorEnabled: pending.twoFactorEnabled,
        createdAt: pending.createdAt,
        termsAccepted: pending.termsAccepted,
        privacyAccepted: pending.privacyAccepted,
        riskPolicyAccepted: pending.riskPolicyAccepted,
      };

      await AsyncStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, `token_${Date.now()}`);
      await AsyncStorage.removeItem("@quantum_trades_pending_login");

      setState({
        isAuthenticated: true,
        isLoading: false,
        user,
        requiresTwoFactor: false,
      });

      return { success: true };
    } catch (error) {
      console.error("2FA login verification error:", error);
      return { success: false, error: "Erro ao verificar código" };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.USER);
      await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      
      setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        requiresTwoFactor: false,
      });
    } catch (error) {
      console.error("Logout error:", error);
    }
  }, []);

  const requestPasswordReset = useCallback(async (email: string) => {
    try {
      const usersJson = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(usersJson);
      
      const user = users.find((u: any) => u.email === email);
      if (!user) {
        // Don't reveal if email exists
        return { success: true };
      }

      // Generate reset code
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      const resetData = {
        email,
        code,
        expiresAt: Date.now() + 15 * 60 * 1000, // 15 minutes
      };

      await AsyncStorage.setItem(`@quantum_trades_reset_${email}`, JSON.stringify(resetData));

      // In production, send email here
      console.log(`Reset code for ${email}: ${code}`);

      return { success: true };
    } catch (error) {
      console.error("Password reset request error:", error);
      return { success: false, error: "Erro ao solicitar recuperação" };
    }
  }, []);

  const verifyResetCode = useCallback(async (email: string, code: string) => {
    try {
      const resetJson = await AsyncStorage.getItem(`@quantum_trades_reset_${email}`);
      if (!resetJson) {
        return { success: false, error: "Código inválido ou expirado" };
      }

      const resetData = JSON.parse(resetJson);
      
      if (Date.now() > resetData.expiresAt) {
        await AsyncStorage.removeItem(`@quantum_trades_reset_${email}`);
        return { success: false, error: "Código expirado" };
      }

      if (resetData.code !== code) {
        return { success: false, error: "Código incorreto" };
      }

      return { success: true };
    } catch (error) {
      console.error("Reset code verification error:", error);
      return { success: false, error: "Erro ao verificar código" };
    }
  }, []);

  const resetPassword = useCallback(async (email: string, code: string, newPassword: string) => {
    try {
      // Verify code first
      const verifyResult = await verifyResetCode(email, code);
      if (!verifyResult.success) {
        return verifyResult;
      }

      // Validate new password
      if (newPassword.length < 8) {
        return { success: false, error: "Senha deve ter no mínimo 8 caracteres" };
      }
      if (!/[A-Z]/.test(newPassword)) {
        return { success: false, error: "Senha deve conter pelo menos uma letra maiúscula" };
      }
      if (!/\d/.test(newPassword)) {
        return { success: false, error: "Senha deve conter pelo menos um número" };
      }

      // Update password
      const usersJson = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(usersJson);
      
      const userIndex = users.findIndex((u: any) => u.email === email);
      if (userIndex === -1) {
        return { success: false, error: "Usuário não encontrado" };
      }

      users[userIndex].passwordHash = simpleHash(newPassword);
      await AsyncStorage.setItem("@quantum_trades_users", JSON.stringify(users));
      await AsyncStorage.removeItem(`@quantum_trades_reset_${email}`);

      return { success: true };
    } catch (error) {
      console.error("Password reset error:", error);
      return { success: false, error: "Erro ao redefinir senha" };
    }
  }, [verifyResetCode]);

  const updateProfile = useCallback(async (data: Partial<UserProfile>) => {
    try {
      if (!state.user) return;

      const updatedUser = { ...state.user, ...data };
      await AsyncStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser));

      // Also update in users list
      const usersJson = await AsyncStorage.getItem("@quantum_trades_users") || "[]";
      const users = JSON.parse(usersJson);
      const userIndex = users.findIndex((u: any) => u.id === state.user?.id);
      if (userIndex !== -1) {
        users[userIndex] = { ...users[userIndex], ...data };
        await AsyncStorage.setItem("@quantum_trades_users", JSON.stringify(users));
      }

      setState(prev => ({
        ...prev,
        user: updatedUser,
      }));
    } catch (error) {
      console.error("Profile update error:", error);
    }
  }, [state.user]);

  // Get pending user info for 2FA screen
  const [pendingUserInfo, setPendingUserInfo] = useState<{ email: string; name: string } | null>(null);

  // Update pending user when registration starts
  useEffect(() => {
    const loadPendingUser = async () => {
      try {
        const pendingJson = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_REGISTRATION);
        if (pendingJson) {
          const pending = JSON.parse(pendingJson);
          setPendingUserInfo({ email: pending.email, name: pending.name });
        } else {
          setPendingUserInfo(null);
        }
      } catch (e) {
        console.error("Error loading pending user:", e);
      }
    };
    if (state.requiresTwoFactor) {
      loadPendingUser();
    }
  }, [state.requiresTwoFactor]);

  const value: AuthContextType = {
    ...state,
    register,
    verifyEmailCode,
    resendEmailCode,
    setupTwoFactor,
    verifyTwoFactor,
    login,
    verifyLoginTwoFactor,
    logout,
    requestPasswordReset,
    verifyResetCode,
    resetPassword,
    updateProfile,
    pendingUser: pendingUserInfo,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useLocalAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useLocalAuth must be used within an AuthProvider");
  }
  return context;
}
