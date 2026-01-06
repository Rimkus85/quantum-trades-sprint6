import React, { useState, useRef, useEffect } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import { useToast } from "@/components/ui/toast";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

const CODE_LENGTH = 6;

export default function VerifyEmailScreen() {
  const colors = useColors();
  const { verifyEmailCode, resendEmailCode } = useLocalAuth();
  const { showToast } = useToast();
  const params = useLocalSearchParams<{ email: string }>();
  const email = params.email || "";

  const [code, setCode] = useState<string[]>(Array(CODE_LENGTH).fill(""));
  const [isLoading, setIsLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(60);
  const [canResend, setCanResend] = useState(false);

  const inputRefs = useRef<(TextInput | null)[]>([]);

  // Countdown timer for resend
  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [resendCooldown]);

  const handleCodeChange = (index: number, value: string) => {
    // Only allow digits
    const digit = value.replace(/\D/g, "").slice(-1);
    
    const newCode = [...code];
    newCode[index] = digit;
    setCode(newCode);

    // Auto-advance to next input
    if (digit && index < CODE_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all digits are filled
    if (digit && index === CODE_LENGTH - 1) {
      const fullCode = newCode.join("");
      if (fullCode.length === CODE_LENGTH) {
        handleVerify(fullCode);
      }
    }
  };

  const handleKeyPress = (index: number, key: string) => {
    if (key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (codeToVerify?: string) => {
    const fullCode = codeToVerify || code.join("");
    
    if (fullCode.length !== CODE_LENGTH) {
      showToast("Digite o código de 6 dígitos", "error");
      return;
    }

    setIsLoading(true);
    try {
      const result = await verifyEmailCode(email, fullCode);
      
      if (result.success) {
        showToast("E-mail verificado com sucesso!", "success");
        router.push("/setup-2fa" as any);
      } else {
        showToast(result.error || "Código inválido", "error");
        // Clear code on error
        setCode(Array(CODE_LENGTH).fill(""));
        inputRefs.current[0]?.focus();
      }
    } catch (error) {
      showToast("Erro ao verificar código. Tente novamente.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend) return;

    setCanResend(false);
    setResendCooldown(60);

    try {
      const result = await resendEmailCode(email);
      if (result.success) {
        showToast("Novo código enviado para seu e-mail", "success");
      } else {
        showToast(result.error || "Erro ao reenviar código", "error");
      }
    } catch (error) {
      showToast("Erro ao reenviar código", "error");
    }
  };

  const maskedEmail = email.replace(/(.{2})(.*)(@.*)/, "$1***$3");

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
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>Verificar E-mail</Text>
          <View style={styles.headerSpacer} />
        </View>

        <View style={styles.content}>
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Logo size="sm" />
          </View>

          {/* Icon */}
          <View style={[styles.iconContainer, { backgroundColor: colors.primary + "20" }]}>
            <MaterialIcons name="mark-email-read" size={48} color={colors.primary} />
          </View>

          {/* Title */}
          <Text style={[styles.title, { color: colors.foreground }]}>
            Verifique seu e-mail
          </Text>

          {/* Description */}
          <Text style={[styles.description, { color: colors.muted }]}>
            Enviamos um código de 6 dígitos para{"\n"}
            <Text style={{ color: colors.primary, fontWeight: "600" }}>{maskedEmail}</Text>
          </Text>

          {/* Code Input */}
          <View style={styles.codeContainer}>
            {code.map((digit, index) => (
              <TextInput
                key={index}
                ref={(ref) => { inputRefs.current[index] = ref; }}
                style={[
                  styles.codeInput,
                  {
                    backgroundColor: colors.surface,
                    borderColor: digit ? colors.primary : colors.border,
                    color: colors.foreground,
                  },
                ]}
                value={digit}
                onChangeText={(value) => handleCodeChange(index, value)}
                onKeyPress={({ nativeEvent }) => handleKeyPress(index, nativeEvent.key)}
                keyboardType="number-pad"
                maxLength={1}
                selectTextOnFocus
                autoFocus={index === 0}
              />
            ))}
          </View>

          {/* Verify Button */}
          <View style={styles.buttonContainer}>
            <Button
              onPress={() => handleVerify()}
              loading={isLoading}
              disabled={isLoading || code.join("").length !== CODE_LENGTH}
              size="lg"
            >
              Verificar
            </Button>
          </View>

          {/* Resend Link */}
          <View style={styles.resendContainer}>
            <Text style={[styles.resendText, { color: colors.muted }]}>
              Não recebeu o código?{" "}
            </Text>
            {canResend ? (
              <Pressable onPress={handleResend}>
                <Text style={[styles.resendLink, { color: colors.primary }]}>
                  Reenviar
                </Text>
              </Pressable>
            ) : (
              <Text style={[styles.resendCooldown, { color: colors.muted }]}>
                Aguarde {resendCooldown}s
              </Text>
            )}
          </View>

          {/* Help Text */}
          <View style={[styles.helpContainer, { backgroundColor: colors.surface }]}>
            <MaterialIcons name="info-outline" size={18} color={colors.muted} />
            <Text style={[styles.helpText, { color: colors.muted }]}>
              Verifique sua caixa de spam caso não encontre o e-mail na caixa de entrada.
            </Text>
          </View>
        </View>
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
  content: {
    flex: 1,
    paddingHorizontal: 24,
    alignItems: "center",
  },
  logoContainer: {
    marginBottom: 24,
  },
  iconContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 12,
    textAlign: "center",
  },
  description: {
    fontSize: 14,
    textAlign: "center",
    lineHeight: 22,
    marginBottom: 32,
  },
  codeContainer: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 32,
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
  buttonContainer: {
    width: "100%",
    marginBottom: 24,
  },
  resendContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 24,
  },
  resendText: {
    fontSize: 14,
  },
  resendLink: {
    fontSize: 14,
    fontWeight: "600",
  },
  resendCooldown: {
    fontSize: 14,
  },
  helpContainer: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 10,
    padding: 16,
    borderRadius: 12,
    width: "100%",
  },
  helpText: {
    fontSize: 12,
    lineHeight: 18,
    flex: 1,
  },
});
