import React, { useState, useEffect, useRef } from "react";
import { View, Text, TextInput, Pressable, StyleSheet, Alert, ScrollView } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Clipboard from "expo-clipboard";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

export default function Setup2FAScreen() {
  const colors = useColors();
  const { setupTwoFactor, verifyTwoFactor } = useLocalAuth();

  const [secret, setSecret] = useState("");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const inputRefs = useRef<(TextInput | null)[]>([]);

  useEffect(() => {
    loadSecret();
  }, []);

  const loadSecret = async () => {
    try {
      const result = await setupTwoFactor();
      setSecret(result.secret);
    } catch (error) {
      console.error("Error loading 2FA secret:", error);
      Alert.alert("Erro", "Não foi possível carregar as configurações de 2FA");
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
        router.replace("/(tabs)" as any);
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

  const copySecret = async () => {
    await Clipboard.setStringAsync(secret);
    setCopied(true);
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setTimeout(() => setCopied(false), 2000);
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
          <Logo size="sm" showText={false} />
        </View>

        {/* Title */}
        <View style={styles.titleContainer}>
          <Text style={[styles.title, { color: colors.foreground }]}>
            Configurar Autenticação
          </Text>
          <Text style={[styles.subtitle, { color: colors.muted }]}>
            Para sua segurança, configure a autenticação em dois fatores (2FA)
          </Text>
        </View>

        {/* Instructions */}
        <View style={[styles.instructionsCard, { backgroundColor: colors.surface }]}>
          <View style={styles.instructionStep}>
            <View style={[styles.stepNumber, { backgroundColor: colors.primary }]}>
              <Text style={[styles.stepNumberText, { color: colors.background }]}>1</Text>
            </View>
            <Text style={[styles.instructionText, { color: colors.foreground }]}>
              Baixe o Google Authenticator ou outro app de autenticação
            </Text>
          </View>

          <View style={styles.instructionStep}>
            <View style={[styles.stepNumber, { backgroundColor: colors.primary }]}>
              <Text style={[styles.stepNumberText, { color: colors.background }]}>2</Text>
            </View>
            <Text style={[styles.instructionText, { color: colors.foreground }]}>
              Adicione uma nova conta e digite a chave abaixo
            </Text>
          </View>

          <View style={styles.instructionStep}>
            <View style={[styles.stepNumber, { backgroundColor: colors.primary }]}>
              <Text style={[styles.stepNumberText, { color: colors.background }]}>3</Text>
            </View>
            <Text style={[styles.instructionText, { color: colors.foreground }]}>
              Digite o código de 6 dígitos gerado pelo app
            </Text>
          </View>
        </View>

        {/* Secret Key */}
        <View style={styles.secretContainer}>
          <Text style={[styles.secretLabel, { color: colors.muted }]}>
            Sua chave secreta:
          </Text>
          <Pressable
            onPress={copySecret}
            style={({ pressed }) => [
              styles.secretBox,
              { backgroundColor: colors.surface, borderColor: colors.border },
              pressed && styles.pressed,
            ]}
          >
            <Text style={[styles.secretText, { color: colors.primary }]}>
              {secret}
            </Text>
            <MaterialIcons
              name={copied ? "check" : "content-copy"}
              size={20}
              color={copied ? colors.success : colors.muted}
            />
          </Pressable>
          {copied && (
            <Text style={[styles.copiedText, { color: colors.success }]}>
              Chave copiada!
            </Text>
          )}
        </View>

        {/* Code Input */}
        <View style={styles.codeContainer}>
          <Text style={[styles.codeLabel, { color: colors.foreground }]}>
            Digite o código do autenticador:
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
            Verificar e Finalizar
          </Button>
        </View>

        {/* Security Note */}
        <View style={[styles.securityNote, { backgroundColor: colors.warning + "15" }]}>
          <MaterialIcons name="security" size={20} color={colors.warning} />
          <Text style={[styles.securityText, { color: colors.muted }]}>
            Guarde sua chave secreta em local seguro. Você precisará dela para recuperar o acesso à sua conta.
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
  instructionsCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    gap: 16,
  },
  instructionStep: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  stepNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  stepNumberText: {
    fontSize: 12,
    fontWeight: "700",
  },
  instructionText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  secretContainer: {
    marginBottom: 24,
  },
  secretLabel: {
    fontSize: 12,
    marginBottom: 8,
  },
  secretBox: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  secretText: {
    fontSize: 16,
    fontWeight: "600",
    letterSpacing: 2,
    flex: 1,
  },
  copiedText: {
    fontSize: 12,
    marginTop: 4,
    textAlign: "center",
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
    marginBottom: 24,
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
