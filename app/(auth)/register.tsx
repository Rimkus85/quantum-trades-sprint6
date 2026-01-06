import React, { useState, useRef } from "react";
import { View, Text, ScrollView, Pressable, StyleSheet, KeyboardAvoidingView, Platform, Switch } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Input, PasswordInput, CPFInput } from "@/components/ui/input";
import { MultiSelect } from "@/components/ui/multi-select";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import { useToast } from "@/components/ui/toast";
import { validateCPF, validateBroker, getBrokerOptions } from "@/lib/validators";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

// Use broker options from validators
const BROKERS = getBrokerOptions();

// Field order for scroll positioning
const FIELD_ORDER = ["name", "email", "cpf", "brokers", "customBroker", "password", "confirmPassword"];

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
    customBroker: "",
    password: "",
    confirmPassword: "",
  });

  const [noBrokerAccount, setNoBrokerAccount] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const scrollToField = (fieldName: string) => {
    const position = fieldPositions.current[fieldName];
    if (position !== undefined && scrollViewRef.current) {
      scrollViewRef.current.scrollTo({ y: Math.max(0, position - 100), animated: true });
    }
  };

  const handleNoBrokerToggle = (value: boolean) => {
    setNoBrokerAccount(value);
    if (value) {
      // Clear broker selection when toggling on
      setFormData(prev => ({ ...prev, brokers: [], customBroker: "" }));
      setErrors(prev => ({ ...prev, brokers: "", customBroker: "" }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Validate name
    if (!formData.name.trim()) {
      newErrors.name = "Nome é obrigatório";
    } else if (formData.name.trim().split(" ").length < 2) {
      newErrors.name = "Digite seu nome completo";
    }

    // Validate email
    if (!formData.email.trim()) {
      newErrors.email = "E-mail é obrigatório";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "E-mail inválido";
    }

    // Validate CPF with mathematical validation
    if (!formData.cpf) {
      newErrors.cpf = "CPF é obrigatório";
    } else {
      const cpfValidation = validateCPF(formData.cpf);
      if (!cpfValidation.valid) {
        newErrors.cpf = cpfValidation.error || "CPF inválido";
      }
    }

    // Validate brokers (only if user has broker account)
    if (!noBrokerAccount) {
      if (formData.brokers.length === 0) {
        newErrors.brokers = "Selecione pelo menos uma corretora";
      }

      // Validate custom broker if "other" is selected
      if (formData.brokers.includes("other")) {
        if (!formData.customBroker.trim()) {
          newErrors.customBroker = "Digite o nome da corretora";
        } else {
          const brokerValidation = validateBroker(formData.customBroker);
          if (!brokerValidation.valid) {
            newErrors.customBroker = brokerValidation.error || "Corretora não encontrada";
          }
        }
      }
    }

    // Validate password
    if (!formData.password) {
      newErrors.password = "Senha é obrigatória";
    } else if (formData.password.length < 8) {
      newErrors.password = "Mínimo 8 caracteres";
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = "Deve conter letra maiúscula";
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = "Deve conter número";
    }

    // Validate password confirmation
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
      // Build broker list (replace "other" with custom broker name)
      let brokerValue = "";
      if (!noBrokerAccount) {
        const brokerList = formData.brokers.map(b => 
          b === "other" ? formData.customBroker : b
        );
        brokerValue = brokerList.join(",");
      } else {
        brokerValue = "Nenhuma";
      }

      const result = await register({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        cpf: formData.cpf,
        broker: brokerValue,
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

            {/* No Broker Account Checkbox */}
            <View style={[styles.checkboxContainer, { backgroundColor: colors.surface }]}>
              <Pressable
                onPress={() => handleNoBrokerToggle(!noBrokerAccount)}
                style={styles.checkboxPressable}
              >
                <View style={[
                  styles.checkbox,
                  { borderColor: noBrokerAccount ? colors.primary : colors.border },
                  noBrokerAccount && { backgroundColor: colors.primary }
                ]}>
                  {noBrokerAccount && (
                    <MaterialIcons name="check" size={16} color={colors.background} />
                  )}
                </View>
                <Text style={[styles.checkboxLabel, { color: colors.foreground }]}>
                  Não tenho conta em nenhuma corretora
                </Text>
              </Pressable>
              {noBrokerAccount && (
                <Text style={[styles.checkboxHint, { color: colors.muted }]}>
                  Você poderá vincular uma corretora posteriormente nas configurações
                </Text>
              )}
            </View>

            {/* Broker Selection - Only show if user has broker account */}
            {!noBrokerAccount && (
              <View onLayout={(e) => handleFieldLayout("brokers", e.nativeEvent.layout.y)}>
                <MultiSelect
                  label="Corretoras"
                  placeholder="Selecione suas corretoras"
                  options={BROKERS}
                  selectedValues={formData.brokers}
                  onSelectionChange={(values) => updateField("brokers", values)}
                  error={errors.brokers}
                  allowCustom={true}
                  customValue={formData.customBroker}
                  onCustomValueChange={(value) => updateField("customBroker", value)}
                  customError={errors.customBroker}
                />
              </View>
            )}

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
  checkboxContainer: {
    padding: 16,
    borderRadius: 12,
    marginVertical: 8,
  },
  checkboxPressable: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  checkboxLabel: {
    fontSize: 14,
    fontWeight: "500",
    flex: 1,
  },
  checkboxHint: {
    fontSize: 12,
    marginTop: 8,
    marginLeft: 36,
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
    marginBottom: 16,
  },
  loginLink: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  loginText: {
    fontSize: 14,
  },
  loginLinkText: {
    fontSize: 14,
    fontWeight: "600",
  },
});
