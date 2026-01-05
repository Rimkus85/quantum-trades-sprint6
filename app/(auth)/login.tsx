import React, { useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, StyleSheet, KeyboardAvoidingView, Platform, TextInput } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Input, PasswordInput } from "@/components/ui/input";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";

export default function LoginScreen() {
  const colors = useColors();
  const { login, verifyLoginTwoFactor, requiresTwoFactor } = useLocalAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [twoFactorCode, setTwoFactorCode] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showTwoFactor, setShowTwoFactor] = useState(false);

  const inputRefs = useRef<(TextInput | null)[]>([]);

  const handleLogin = async () => {
    if (!email.trim()) {
      setError("Digite seu e-mail");
      return;
    }
    if (!password) {
      setError("Digite sua senha");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await login(email.trim().toLowerCase(), password);
      
      if (result.success && result.requiresTwoFactor) {
        setShowTwoFactor(true);
        setTimeout(() => inputRefs.current[0]?.focus(), 100);
      } else if (!result.success) {
        setError(result.error || "Erro ao fazer login");
        if (Platform.OS !== "web") {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        }
      }
    } catch (error) {
      setError("Erro ao fazer login. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    
    const newCode = [...twoFactorCode];
    newCode[index] = digit;
    setTwoFactorCode(newCode);
    setError("");

    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    if (digit && index === 5) {
      const fullCode = newCode.join("");
      if (fullCode.length === 6) {
        handleVerifyTwoFactor(fullCode);
      }
    }
  };

  const handleKeyPress = (index: number, key: string) => {
    if (key === "Backspace" && !twoFactorCode[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyTwoFactor = async (codeString?: string) => {
    const fullCode = codeString || twoFactorCode.join("");
    
    if (fullCode.length !== 6) {
      setError("Digite o código de 6 dígitos");
      return;
    }

    setIsLoading(true);
    try {
      const result = await verifyLoginTwoFactor(fullCode);
      
      if (result.success) {
        if (Platform.OS !== "web") {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        router.replace("/(tabs)" as any);
      } else {
        setError(result.error || "Código inválido");
        setTwoFactorCode(["", "", "", "", "", ""]);
        inputRefs.current[0]?.focus();
        if (Platform.OS !== "web") {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        }
      }
    } catch (error) {
      setError("Erro ao verificar código");
    } finally {
      setIsLoading(false);
    }
  };

  if (showTwoFactor) {
    return (
      <ScreenContainer edges={["top", "bottom", "left", "right"]}>
        <KeyboardAvoidingView
          behavior={Platform.OS === "ios" ? "padding" : "height"}
          style={styles.keyboardView}
        >
          {/* Header */}
          <View style={styles.header}>
            <Pressable
              onPress={() => setShowTwoFactor(false)}
              style={({ pressed }) => [styles.backButton, pressed && styles.pressed]}
            >
              <MaterialIcons name="arrow-back" size={24} color={colors.foreground} />
            </Pressable>
            <Text style={[styles.headerTitle, { color: colors.foreground }]}>Verificação</Text>
            <View style={styles.headerSpacer} />
          </View>

          <ScrollView
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            {/* Logo */}
            <View style={styles.logoContainer}>
              <Logo size="md" showText={false} />
            </View>

            {/* Title */}
            <View style={styles.titleContainer}>
              <Text style={[styles.title, { color: colors.foreground }]}>
                Autenticação 2FA
              </Text>
              <Text style={[styles.subtitle, { color: colors.muted }]}>
                Digite o código de 6 dígitos do seu aplicativo autenticador
              </Text>
            </View>

            {/* Code Input */}
            <View style={styles.codeContainer}>
              <View style={styles.codeInputs}>
                {twoFactorCode.map((digit, index) => (
                  <TextInput
                    key={index}
                    ref={(ref) => { inputRefs.current[index] = ref; }}
                    style={[
                      styles.codeInput,
                      {
                        backgroundColor: colors.surface,
                        borderColor: digit ? colors.primary : error ? colors.error : colors.border,
                        color: colors.foreground,
                      },
                    ]}
                    value={digit}
                    onChangeText={(value) => handleCodeChange(index, value)}
                    onKeyPress={({ nativeEvent }) => handleKeyPress(index, nativeEvent.key)}
                    keyboardType="number-pad"
                    maxLength={1}
                    selectTextOnFocus
                  />
                ))}
              </View>

              {error && (
                <View style={styles.errorContainer}>
                  <MaterialIcons name="error-outline" size={16} color={colors.error} />
                  <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
                </View>
              )}
            </View>

            {/* Submit Button */}
            <Button
              onPress={() => handleVerifyTwoFactor()}
              loading={isLoading}
              disabled={isLoading || twoFactorCode.join("").length !== 6}
              size="lg"
            >
              Verificar
            </Button>
          </ScrollView>
        </KeyboardAvoidingView>
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
      >
        {/* Header */}
        <View style={styles.header}>
          <Pressable
            onPress={() => router.back()}
            style={({ pressed }) => [styles.backButton, pressed && styles.pressed]}
          >
            <MaterialIcons name="arrow-back" size={24} color={colors.foreground} />
          </Pressable>
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>Login</Text>
          <View style={styles.headerSpacer} />
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Logo size="lg" showText />
          </View>

          {/* Error Message */}
          {error && (
            <View style={[styles.errorBanner, { backgroundColor: colors.error + "20" }]}>
              <MaterialIcons name="error-outline" size={20} color={colors.error} />
              <Text style={[styles.errorBannerText, { color: colors.error }]}>{error}</Text>
            </View>
          )}

          {/* Form */}
          <View style={styles.form}>
            <Input
              label="E-mail"
              placeholder="seu@email.com"
              value={email}
              onChangeText={(value) => {
                setEmail(value);
                setError("");
              }}
              leftIcon="email"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
              returnKeyType="next"
            />

            <PasswordInput
              label="Senha"
              placeholder="Digite sua senha"
              value={password}
              onChangeText={(value) => {
                setPassword(value);
                setError("");
              }}
              leftIcon="lock"
              autoComplete="password"
              returnKeyType="done"
              onSubmitEditing={handleLogin}
            />

            {/* Forgot Password */}
            <Pressable
              onPress={() => router.push("/forgot-password" as any)}
              style={styles.forgotPassword}
            >
              <Text style={[styles.forgotPasswordText, { color: colors.primary }]}>
                Esqueci minha senha
              </Text>
            </Pressable>
          </View>

          {/* Submit Button */}
          <View style={styles.buttonContainer}>
            <Button
              onPress={handleLogin}
              loading={isLoading}
              disabled={isLoading}
              size="lg"
            >
              Entrar
            </Button>
          </View>

          {/* Register Link */}
          <View style={styles.registerLink}>
            <Text style={[styles.registerText, { color: colors.muted }]}>
              Não tem uma conta?{" "}
            </Text>
            <Pressable onPress={() => router.push("/register" as any)}>
              <Text style={[styles.registerLinkText, { color: colors.primary }]}>
                Criar conta
              </Text>
            </Pressable>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  keyboardView: {
    flex: 1,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    padding: 8,
    borderRadius: 8,
  },
  pressed: {
    opacity: 0.7,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: "600",
  },
  headerSpacer: {
    width: 40,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  logoContainer: {
    alignItems: "center",
    marginVertical: 32,
  },
  titleContainer: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
  errorBanner: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    gap: 8,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 14,
  },
  form: {
    gap: 16,
  },
  forgotPassword: {
    alignSelf: "flex-end",
  },
  forgotPasswordText: {
    fontSize: 14,
    fontWeight: "500",
  },
  buttonContainer: {
    marginTop: 32,
  },
  registerLink: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 16,
  },
  registerText: {
    fontSize: 14,
  },
  registerLinkText: {
    fontSize: 14,
    fontWeight: "600",
  },
  codeContainer: {
    marginBottom: 24,
  },
  codeInputs: {
    flexDirection: "row",
    justifyContent: "center",
    gap: 8,
  },
  codeInput: {
    width: 48,
    height: 56,
    borderRadius: 12,
    borderWidth: 2,
    fontSize: 24,
    fontWeight: "700",
    textAlign: "center",
  },
  errorContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    marginTop: 8,
  },
  errorText: {
    fontSize: 12,
  },
});
