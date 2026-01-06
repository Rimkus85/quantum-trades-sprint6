import React, { useState, useEffect, useRef } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, Alert, ScrollView } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import { useToast } from "@/components/ui/toast";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

export default function Setup2FAScreen() {
  const colors = useColors();
  const { setupTwoFactor, verifyTwoFactor, pendingUser } = useLocalAuth();
  const { showToast } = useToast();

  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const inputRefs = useRef<(TextInput | null)[]>([]);

  useEffect(() => {
    sendCodeToEmail();
  }, []);

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const sendCodeToEmail = async () => {
    try {
      const result = await setupTwoFactor();
      
      // In production, this would send the code via email
      // For now, we simulate the email sending
      console.log("2FA Code sent to email:", result.secret);
      
      setEmailSent(true);
      setResendCooldown(60); // 60 seconds cooldown
      
      showToast(
        `Código enviado para ${maskEmail(pendingUser?.email || "")}`,
        "success"
      );
    } catch (error) {
      console.error("Error sending 2FA code:", error);
      showToast("Erro ao enviar código. Tente novamente.", "error");
    }
  };

  const maskEmail = (email: string): string => {
    if (!email) return "seu e-mail";
    const [local, domain] = email.split("@");
    if (!domain) return email;
    const maskedLocal = local.length > 2 
      ? local[0] + "*".repeat(local.length - 2) + local[local.length - 1]
      : local;
    return `${maskedLocal}@${domain}`;
  };

  const handleResendCode = async () => {
    if (resendCooldown > 0) return;
    
    setIsLoading(true);
    try {
      await sendCodeToEmail();
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeChange = (index: number, value: string) => {
    // Only accept digits
    const digit = value.replace(/\D/g, "").slice(-1);
    
    const newCode = [...code];
    newCode[index] = digit;
    setCode(newCode);
    setError("");

    // Auto-focus next input
    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when complete
    if (digit && index === 5) {
      const fullCode = newCode.join("");
      if (fullCode.length === 6) {
        handleVerify(fullCode);
      }
    }
  };

  const handleKeyPress = (index: number, key: string) => {
    if (key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (codeString?: string) => {
    const fullCode = codeString || code.join("");
    
    if (fullCode.length !== 6) {
      setError("Digite o código de 6 dígitos");
      return;
    }

    setIsLoading(true);
    try {
      const result = await verifyTwoFactor(fullCode);
      
      if (result.success) {
        if (Platform.OS !== "web") {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        showToast("Conta verificada com sucesso!", "success");
        // Após verificação, ir para onboarding (perfil de risco)
        router.replace("/(onboarding)/risk-profile" as any);
      } else {
        setError(result.error || "Código inválido");
        setCode(["", "", "", "", "", ""]);
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

  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.header}>
          <Pressable
            onPress={() => router.back()}
            style={({ pressed }) => [styles.backButton, pressed && styles.pressed]}
          >
            <MaterialIcons name="arrow-back" size={24} color={colors.foreground} />
          </Pressable>
        </View>

        {/* Logo */}
        <View style={styles.logoContainer}>
          <Logo size="sm" />
        </View>

        {/* Title */}
        <View style={styles.titleContainer}>
          <Text style={[styles.title, { color: colors.foreground }]}>
            Verificação de Segurança
          </Text>
          <Text style={[styles.subtitle, { color: colors.muted }]}>
            Para sua segurança, enviamos um código de verificação para seu e-mail
          </Text>
        </View>

        {/* Email Sent Confirmation */}
        <View style={[styles.emailCard, { backgroundColor: colors.surface }]}>
          <View style={[styles.emailIconContainer, { backgroundColor: colors.primary + "20" }]}>
            <MaterialIcons name="email" size={32} color={colors.primary} />
          </View>
          
          <Text style={[styles.emailSentText, { color: colors.foreground }]}>
            Código enviado para:
          </Text>
          <Text style={[styles.emailAddress, { color: colors.primary }]}>
            {maskEmail(pendingUser?.email || "")}
          </Text>
          
          <View style={styles.emailTips}>
            <View style={styles.tipItem}>
              <MaterialIcons name="info-outline" size={16} color={colors.muted} />
              <Text style={[styles.tipText, { color: colors.muted }]}>
                Verifique também a pasta de spam
              </Text>
            </View>
            <View style={styles.tipItem}>
              <MaterialIcons name="timer" size={16} color={colors.muted} />
              <Text style={[styles.tipText, { color: colors.muted }]}>
                O código expira em 10 minutos
              </Text>
            </View>
          </View>
        </View>

        {/* Code Input */}
        <View style={styles.codeContainer}>
          <Text style={[styles.codeLabel, { color: colors.foreground }]}>
            Digite o código de 6 dígitos:
          </Text>
          
          <View style={styles.codeInputs}>
            {code.map((digit, index) => (
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
                returnKeyType={index === 5 ? "done" : "next"}
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
        <View style={styles.buttonContainer}>
          <Button
            onPress={() => handleVerify()}
            loading={isLoading}
            disabled={isLoading || code.join("").length !== 6}
            size="lg"
          >
            Verificar Código
          </Button>
        </View>

        {/* Resend Code */}
        <View style={styles.resendContainer}>
          <Text style={[styles.resendText, { color: colors.muted }]}>
            Não recebeu o código?
          </Text>
          <Pressable
            onPress={handleResendCode}
            disabled={resendCooldown > 0 || isLoading}
            style={({ pressed }) => [pressed && styles.pressed]}
          >
            <Text
              style={[
                styles.resendLink,
                {
                  color: resendCooldown > 0 ? colors.muted : colors.primary,
                },
              ]}
            >
              {resendCooldown > 0
                ? `Reenviar em ${resendCooldown}s`
                : "Reenviar código"}
            </Text>
          </Pressable>
        </View>

        {/* Security Note */}
        <View style={[styles.securityNote, { backgroundColor: colors.warning + "15" }]}>
          <MaterialIcons name="security" size={20} color={colors.warning} />
          <Text style={[styles.securityText, { color: colors.muted }]}>
            Nunca compartilhe este código com ninguém. A equipe do Quantum Trades nunca solicitará seu código de verificação.
          </Text>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  header: {
    paddingVertical: 12,
  },
  backButton: {
    padding: 8,
    borderRadius: 8,
    alignSelf: "flex-start",
  },
  pressed: {
    opacity: 0.7,
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 24,
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
  emailCard: {
    padding: 24,
    borderRadius: 16,
    marginBottom: 24,
    alignItems: "center",
  },
  emailIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  emailSentText: {
    fontSize: 14,
    marginBottom: 4,
  },
  emailAddress: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 16,
  },
  emailTips: {
    gap: 8,
    width: "100%",
  },
  tipItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  tipText: {
    fontSize: 12,
  },
  codeContainer: {
    marginBottom: 24,
  },
  codeLabel: {
    fontSize: 14,
    fontWeight: "500",
    marginBottom: 12,
    textAlign: "center",
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
  buttonContainer: {
    marginBottom: 16,
  },
  resendContainer: {
    alignItems: "center",
    marginBottom: 24,
  },
  resendText: {
    fontSize: 14,
    marginBottom: 4,
  },
  resendLink: {
    fontSize: 14,
    fontWeight: "600",
  },
  securityNote: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    padding: 16,
    borderRadius: 12,
  },
  securityText: {
    flex: 1,
    fontSize: 12,
    lineHeight: 18,
  },
});
