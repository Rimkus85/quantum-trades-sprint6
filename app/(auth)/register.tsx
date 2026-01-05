import React, { useState } from "react";
import { View, Text, ScrollView, Pressable, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Input, PasswordInput, CPFInput } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

const BROKERS = [
  { label: "XP Investimentos", value: "xp" },
  { label: "BTG Pactual", value: "btg" },
  { label: "Clear Corretora", value: "clear" },
  { label: "Rico Investimentos", value: "rico" },
  { label: "Inter Invest", value: "inter" },
  { label: "Nubank Investimentos", value: "nubank" },
  { label: "Binance", value: "binance" },
  { label: "Mercado Bitcoin", value: "mercadobitcoin" },
  { label: "Outra", value: "other" },
];

export default function RegisterScreen() {
  const colors = useColors();
  const { register } = useLocalAuth();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    cpf: "",
    broker: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Nome é obrigatório";
    } else if (formData.name.trim().split(" ").length < 2) {
      newErrors.name = "Digite seu nome completo";
    }

    if (!formData.email.trim()) {
      newErrors.email = "E-mail é obrigatório";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "E-mail inválido";
    }

    if (!formData.cpf) {
      newErrors.cpf = "CPF é obrigatório";
    } else if (!/^\d{3}\.\d{3}\.\d{3}-\d{2}$/.test(formData.cpf)) {
      newErrors.cpf = "CPF inválido";
    }

    if (!formData.broker) {
      newErrors.broker = "Selecione uma corretora";
    }

    if (!formData.password) {
      newErrors.password = "Senha é obrigatória";
    } else if (formData.password.length < 8) {
      newErrors.password = "Mínimo 8 caracteres";
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = "Deve conter letra maiúscula";
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = "Deve conter número";
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Senhas não conferem";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const result = await register({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        cpf: formData.cpf,
        broker: formData.broker,
        password: formData.password,
      });

      if (result.success && result.requiresTwoFactor) {
        router.push("/setup-2fa" as any);
      } else if (!result.success) {
        setErrors({ general: result.error || "Erro ao criar conta" });
      }
    } catch (error) {
      setErrors({ general: "Erro ao criar conta. Tente novamente." });
    } finally {
      setIsLoading(false);
    }
  };

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

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
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>Criar Conta</Text>
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
            <Logo size="sm" />
          </View>

          {/* Error Message */}
          {errors.general && (
            <View style={[styles.errorBanner, { backgroundColor: colors.error + "20" }]}>
              <MaterialIcons name="error-outline" size={20} color={colors.error} />
              <Text style={[styles.errorText, { color: colors.error }]}>{errors.general}</Text>
            </View>
          )}

          {/* Form */}
          <View style={styles.form}>
            <Input
              label="Nome completo"
              placeholder="Digite seu nome completo"
              value={formData.name}
              onChangeText={(value) => updateField("name", value)}
              error={errors.name}
              leftIcon="person"
              autoCapitalize="words"
              autoComplete="name"
            />

            <Input
              label="E-mail"
              placeholder="seu@email.com"
              value={formData.email}
              onChangeText={(value) => updateField("email", value)}
              error={errors.email}
              leftIcon="email"
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />

            <CPFInput
              label="CPF"
              value={formData.cpf}
              onChangeText={(value) => updateField("cpf", value)}
              error={errors.cpf}
              leftIcon="badge"
            />

            <Select
              label="Corretora principal"
              placeholder="Selecione sua corretora"
              value={formData.broker}
              options={BROKERS}
              onValueChange={(value) => updateField("broker", value)}
              error={errors.broker}
            />

            <PasswordInput
              label="Senha"
              placeholder="Mínimo 8 caracteres"
              value={formData.password}
              onChangeText={(value) => updateField("password", value)}
              error={errors.password}
              leftIcon="lock"
              autoComplete="new-password"
            />

            <PasswordInput
              label="Confirmar senha"
              placeholder="Digite a senha novamente"
              value={formData.confirmPassword}
              onChangeText={(value) => updateField("confirmPassword", value)}
              error={errors.confirmPassword}
              leftIcon="lock"
              autoComplete="new-password"
            />

            {/* Password Requirements */}
            <View style={styles.requirements}>
              <Text style={[styles.requirementsTitle, { color: colors.muted }]}>
                A senha deve conter:
              </Text>
              <RequirementItem
                met={formData.password.length >= 8}
                text="Mínimo 8 caracteres"
              />
              <RequirementItem
                met={/[A-Z]/.test(formData.password)}
                text="Uma letra maiúscula"
              />
              <RequirementItem
                met={/\d/.test(formData.password)}
                text="Um número"
              />
            </View>
          </View>

          {/* Submit Button */}
          <View style={styles.buttonContainer}>
            <Button
              onPress={handleSubmit}
              loading={isLoading}
              disabled={isLoading}
              size="lg"
            >
              Continuar
            </Button>
          </View>

          {/* Login Link */}
          <View style={styles.loginLink}>
            <Text style={[styles.loginText, { color: colors.muted }]}>
              Já tem uma conta?{" "}
            </Text>
            <Pressable onPress={() => router.push("/login" as any)}>
              <Text style={[styles.loginLinkText, { color: colors.primary }]}>
                Fazer login
              </Text>
            </Pressable>
          </View>
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
  },
  logoContainer: {
    alignItems: "center",
    marginBottom: 24,
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
  buttonContainer: {
    marginTop: 24,
  },
  loginLink: {
    flexDirection: "row",
    justifyContent: "center",
    marginTop: 16,
  },
  loginText: {
    fontSize: 14,
  },
  loginLinkText: {
    fontSize: 14,
    fontWeight: "600",
  },
});
