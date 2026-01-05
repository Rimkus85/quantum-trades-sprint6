import React, { useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Input, PasswordInput, CPFInput } from "@/components/ui/input";
import { MultiSelect } from "@/components/ui/multi-select";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import { useToast } from "@/components/ui/toast";
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
  { label: "Foxbit", value: "foxbit" },
  { label: "NovaDAX", value: "novadax" },
  { label: "Outra", value: "other" },
];

// Field order for scroll positioning
const FIELD_ORDER = ["name", "email", "cpf", "brokers", "password", "confirmPassword"];

export default function RegisterScreen() {
  const colors = useColors();
  const { register } = useLocalAuth();
  const { showToast } = useToast();
  const scrollViewRef = useRef<ScrollView>(null);
  const fieldPositions = useRef<Record<string, number>>({});

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    cpf: "",
    brokers: [] as string[],
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const scrollToField = (fieldName: string) => {
    const position = fieldPositions.current[fieldName];
    if (position !== undefined && scrollViewRef.current) {
      scrollViewRef.current.scrollTo({ y: Math.max(0, position - 100), animated: true });
    }
  };

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

    if (formData.brokers.length === 0) {
      newErrors.brokers = "Selecione pelo menos uma corretora";
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
    
    // If there are errors, show toast and scroll to first error
    if (Object.keys(newErrors).length > 0) {
      const firstErrorField = FIELD_ORDER.find(field => newErrors[field]);
      if (firstErrorField) {
        const errorMessage = newErrors[firstErrorField];
        showToast(errorMessage, "error", {
          label: "Ver",
          onPress: () => scrollToField(firstErrorField),
        });
        scrollToField(firstErrorField);
      }
      return false;
    }
    
    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const result = await register({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        cpf: formData.cpf,
        broker: formData.brokers.join(","),
        password: formData.password,
      });

      if (result.success && result.requiresTwoFactor) {
        showToast("Conta criada! Configure o 2FA para continuar.", "success");
        router.push("/setup-2fa" as any);
      } else if (!result.success) {
        // Handle specific field errors (e.g., duplicate email/CPF)
        const fieldError = (result as any).field;
        if (fieldError) {
          setErrors({ [fieldError]: result.error || "Erro" });
          scrollToField(fieldError);
        }
        showToast(result.error || "Erro ao criar conta", "error");
      }
    } catch (error) {
      showToast("Erro ao criar conta. Tente novamente.", "error");
    } finally {
      setIsLoading(false);
    }
  };

  const updateField = (field: string, value: string | string[]) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  const handleFieldLayout = (fieldName: string, y: number) => {
    fieldPositions.current[fieldName] = y;
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
          ref={scrollViewRef}
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo */}
          <View style={styles.logoContainer}>
            <Logo size="sm" />
          </View>

          {/* Form */}
          <View style={styles.form}>
            <View onLayout={(e) => handleFieldLayout("name", e.nativeEvent.layout.y)}>
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
            </View>

            <View onLayout={(e) => handleFieldLayout("email", e.nativeEvent.layout.y)}>
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
            </View>

            <View onLayout={(e) => handleFieldLayout("cpf", e.nativeEvent.layout.y)}>
              <CPFInput
                label="CPF"
                value={formData.cpf}
                onChangeText={(value) => updateField("cpf", value)}
                error={errors.cpf}
                leftIcon="badge"
              />
            </View>

            <View onLayout={(e) => handleFieldLayout("brokers", e.nativeEvent.layout.y)}>
              <MultiSelect
                label="Corretoras"
                placeholder="Selecione suas corretoras"
                options={BROKERS}
                selectedValues={formData.brokers}
                onSelectionChange={(values) => updateField("brokers", values)}
                error={errors.brokers}
              />
            </View>

            <View onLayout={(e) => handleFieldLayout("password", e.nativeEvent.layout.y)}>
              <PasswordInput
                label="Senha"
                placeholder="Mínimo 8 caracteres"
                value={formData.password}
                onChangeText={(value) => updateField("password", value)}
                error={errors.password}
                leftIcon="lock"
                autoComplete="new-password"
              />
            </View>

            <View onLayout={(e) => handleFieldLayout("confirmPassword", e.nativeEvent.layout.y)}>
              <PasswordInput
                label="Confirmar senha"
                placeholder="Digite a senha novamente"
                value={formData.confirmPassword}
                onChangeText={(value) => updateField("confirmPassword", value)}
                error={errors.confirmPassword}
                leftIcon="lock"
                autoComplete="new-password"
              />
            </View>

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
  form: {
    gap: 8,
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
