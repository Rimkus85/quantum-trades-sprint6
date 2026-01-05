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

type Step = "email" | "code" | "password" | "success";

export default function ForgotPasswordScreen() {
  const colors = useColors();
  const { requestPasswordReset, verifyResetCode, resetPassword } = useLocalAuth();

  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const inputRefs = useRef<(TextInput | null)[]>([]);

  const handleRequestReset = async () => {
    if (!email.trim()) {
      setError("Digite seu e-mail");
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("E-mail inválido");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await requestPasswordReset(email.trim().toLowerCase());
      
      if (result.success) {
        setStep("code");
        setTimeout(() => inputRefs.current[0]?.focus(), 100);
      } else {
        setError(result.error || "Erro ao solicitar recuperação");
      }
    } catch (error) {
      setError("Erro ao solicitar recuperação. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    
    const newCode = [...code];
    newCode[index] = digit;
    setCode(newCode);
    setError("");

    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    if (digit && index === 5) {
      const fullCode = newCode.join("");
      if (fullCode.length === 6) {
        handleVerifyCode(fullCode);
      }
    }
  };

  const handleKeyPress = (index: number, key: string) => {
    if (key === "Backspace" && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyCode = async (codeString?: string) => {
    const fullCode = codeString || code.join("");
    
    if (fullCode.length !== 6) {
      setError("Digite o código de 6 dígitos");
      return;
    }

    setIsLoading(true);
    try {
      const result = await verifyResetCode(email, fullCode);
      
      if (result.success) {
        setStep("password");
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

  const handleResetPassword = async () => {
    if (!newPassword) {
      setError("Digite a nova senha");
      return;
    }

    if (newPassword.length < 8) {
      setError("Senha deve ter no mínimo 8 caracteres");
      return;
    }

    if (!/[A-Z]/.test(newPassword)) {
      setError("Senha deve conter letra maiúscula");
      return;
    }

    if (!/\d/.test(newPassword)) {
      setError("Senha deve conter número");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Senhas não conferem");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await resetPassword(email, code.join(""), newPassword);
      
      if (result.success) {
        if (Platform.OS !== "web") {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
        setStep("success");
      } else {
        setError(result.error || "Erro ao redefinir senha");
      }
    } catch (error) {
      setError("Erro ao redefinir senha. Tente novamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const renderEmailStep = () => (
    <>
      <View style={styles.titleContainer}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Recuperar Senha
        </Text>
        <Text style={[styles.subtitle, { color: colors.muted }]}>
          Digite seu e-mail cadastrado e enviaremos um código de recuperação
        </Text>
      </View>

      {error && (
        <View style={[styles.errorBanner, { backgroundColor: colors.error + "20" }]}>
          <MaterialIcons name="error-outline" size={20} color={colors.error} />
          <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
        </View>
      )}

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
          returnKeyType="done"
          onSubmitEditing={handleRequestReset}
        />
      </View>

      <View style={styles.buttonContainer}>
        <Button
          onPress={handleRequestReset}
          loading={isLoading}
          disabled={isLoading}
          size="lg"
        >
          Enviar Código
        </Button>
      </View>
    </>
  );

  const renderCodeStep = () => (
    <>
      <View style={styles.titleContainer}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Verificar Código
        </Text>
        <Text style={[styles.subtitle, { color: colors.muted }]}>
          Digite o código de 6 dígitos enviado para{"\n"}
          <Text style={{ color: colors.primary }}>{email}</Text>
        </Text>
      </View>

      <View style={styles.codeContainer}>
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
            />
          ))}
        </View>

        {error && (
          <View style={styles.errorContainer}>
            <MaterialIcons name="error-outline" size={16} color={colors.error} />
            <Text style={[styles.errorTextSmall, { color: colors.error }]}>{error}</Text>
          </View>
        )}
      </View>

      <View style={styles.buttonContainer}>
        <Button
          onPress={() => handleVerifyCode()}
          loading={isLoading}
          disabled={isLoading || code.join("").length !== 6}
          size="lg"
        >
          Verificar
        </Button>
      </View>

      <Pressable
        onPress={() => {
          setCode(["", "", "", "", "", ""]);
          handleRequestReset();
        }}
        style={styles.resendLink}
      >
        <Text style={[styles.resendText, { color: colors.muted }]}>
          Não recebeu o código?{" "}
          <Text style={{ color: colors.primary }}>Reenviar</Text>
        </Text>
      </Pressable>
    </>
  );

  const renderPasswordStep = () => (
    <>
      <View style={styles.titleContainer}>
        <Text style={[styles.title, { color: colors.foreground }]}>
          Nova Senha
        </Text>
        <Text style={[styles.subtitle, { color: colors.muted }]}>
          Crie uma nova senha segura para sua conta
        </Text>
      </View>

      {error && (
        <View style={[styles.errorBanner, { backgroundColor: colors.error + "20" }]}>
          <MaterialIcons name="error-outline" size={20} color={colors.error} />
          <Text style={[styles.errorText, { color: colors.error }]}>{error}</Text>
        </View>
      )}

      <View style={styles.form}>
        <PasswordInput
          label="Nova senha"
          placeholder="Mínimo 8 caracteres"
          value={newPassword}
          onChangeText={(value) => {
            setNewPassword(value);
            setError("");
          }}
          leftIcon="lock"
          autoComplete="new-password"
        />

        <PasswordInput
          label="Confirmar nova senha"
          placeholder="Digite a senha novamente"
          value={confirmPassword}
          onChangeText={(value) => {
            setConfirmPassword(value);
            setError("");
          }}
          leftIcon="lock"
          autoComplete="new-password"
          returnKeyType="done"
          onSubmitEditing={handleResetPassword}
        />

        {/* Password Requirements */}
        <View style={styles.requirements}>
          <Text style={[styles.requirementsTitle, { color: colors.muted }]}>
            A senha deve conter:
          </Text>
          <RequirementItem
            met={newPassword.length >= 8}
            text="Mínimo 8 caracteres"
          />
          <RequirementItem
            met={/[A-Z]/.test(newPassword)}
            text="Uma letra maiúscula"
          />
          <RequirementItem
            met={/\d/.test(newPassword)}
            text="Um número"
          />
        </View>
      </View>

      <View style={styles.buttonContainer}>
        <Button
          onPress={handleResetPassword}
          loading={isLoading}
          disabled={isLoading}
          size="lg"
        >
          Redefinir Senha
        </Button>
      </View>
    </>
  );

  const renderSuccessStep = () => (
    <View style={styles.successContainer}>
      <View style={[styles.successIcon, { backgroundColor: colors.success + "20" }]}>
        <MaterialIcons name="check-circle" size={64} color={colors.success} />
      </View>

      <Text style={[styles.successTitle, { color: colors.foreground }]}>
        Senha Redefinida!
      </Text>
      
      <Text style={[styles.successSubtitle, { color: colors.muted }]}>
        Sua senha foi alterada com sucesso. Você já pode fazer login com a nova senha.
      </Text>

      <View style={styles.buttonContainer}>
        <Button
          onPress={() => router.replace("/login" as any)}
          size="lg"
        >
          Fazer Login
        </Button>
      </View>
    </View>
  );

  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
      >
        {/* Header */}
        {step !== "success" && (
          <View style={styles.header}>
            <Pressable
              onPress={() => {
                if (step === "email") {
                  router.back();
                } else if (step === "code") {
                  setStep("email");
                  setCode(["", "", "", "", "", ""]);
                  setError("");
                } else if (step === "password") {
                  setStep("code");
                  setError("");
                }
              }}
              style={({ pressed }) => [styles.backButton, pressed && styles.pressed]}
            >
              <MaterialIcons name="arrow-back" size={24} color={colors.foreground} />
            </Pressable>
            <Text style={[styles.headerTitle, { color: colors.foreground }]}>
              {step === "email" && "Recuperar Senha"}
              {step === "code" && "Verificar Código"}
              {step === "password" && "Nova Senha"}
            </Text>
            <View style={styles.headerSpacer} />
          </View>
        )}

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Logo size="sm" showText={false} />
          </View>

          {step === "email" && renderEmailStep()}
          {step === "code" && renderCodeStep()}
          {step === "password" && renderPasswordStep()}
          {step === "success" && renderSuccessStep()}
        </ScrollView>
      </KeyboardAvoidingView>
    </ScreenContainer>
  );
}

function RequirementItem({ met, text }: { met: boolean; text: string }) {
  const colors = useColors();
  
  return (
    <View style={styles.requirementItem}>
      <MaterialIcons
        name={met ? "check-circle" : "radio-button-unchecked"}
        size={16}
        color={met ? colors.success : colors.muted}
      />
      <Text style={[styles.requirementText, { color: met ? colors.success : colors.muted }]}>
        {text}
      </Text>
    </View>
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
    flexGrow: 1,
  },
  logoContainer: {
    alignItems: "center",
    marginVertical: 24,
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
  errorText: {
    flex: 1,
    fontSize: 14,
  },
  form: {
    gap: 16,
  },
  buttonContainer: {
    marginTop: 24,
  },
  codeContainer: {
    marginBottom: 8,
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
  errorTextSmall: {
    fontSize: 12,
  },
  resendLink: {
    alignItems: "center",
    marginTop: 16,
  },
  resendText: {
    fontSize: 14,
  },
  requirements: {
    marginTop: 8,
    padding: 12,
    backgroundColor: "#112240",
    borderRadius: 8,
  },
  requirementsTitle: {
    fontSize: 12,
    marginBottom: 8,
  },
  requirementItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginVertical: 2,
  },
  requirementText: {
    fontSize: 12,
  },
  successContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 40,
  },
  successIcon: {
    width: 120,
    height: 120,
    borderRadius: 60,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 12,
  },
  successSubtitle: {
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
    marginBottom: 32,
  },
});
