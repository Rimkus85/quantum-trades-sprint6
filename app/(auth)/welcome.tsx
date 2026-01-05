import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";


export default function WelcomeScreen() {
  const colors = useColors();

  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <View style={styles.container}>
        {/* Logo Section */}
        <View style={styles.logoSection}>
          <Logo size="xl" showText />
        </View>

        {/* Content Section */}
        <View style={styles.contentSection}>
          <Text style={[styles.title, { color: colors.foreground }]}>
            Bem-vindo ao{"\n"}
            <Text style={{ color: colors.primary }}>Quantum Trades</Text>
          </Text>
          
          <Text style={[styles.subtitle, { color: colors.muted }]}>
            Automatize suas estratégias de investimento com nossa IA avançada. 
            Trading 24/7, gestão de risco inteligente e acesso a múltiplos mercados.
          </Text>

          {/* Features */}
          <View style={styles.features}>
            <FeatureItem
              icon="🤖"
              title="IA Avançada"
              description="Análise preditiva de mercado"
            />
            <FeatureItem
              icon="⏰"
              title="24/7 Autônomo"
              description="Opera enquanto você descansa"
            />
            <FeatureItem
              icon="🌍"
              title="Multi-Mercados"
              description="B3, NYSE, NASDAQ, Crypto"
            />
          </View>
        </View>

        {/* Buttons Section */}
        <View style={styles.buttonsSection}>
          <Button
            onPress={() => router.push("/register" as any)}
            variant="primary"
            size="lg"
          >
            Criar Conta
          </Button>
          
          <Button
            onPress={() => router.push("/login" as any)}
            variant="outline"
            size="lg"
          >
            Já tenho conta
          </Button>
        </View>

        {/* Footer */}
        <Text style={[styles.footer, { color: colors.muted }]}>
          Ao continuar, você concorda com nossos Termos de Uso e Política de Privacidade
        </Text>
      </View>
    </ScreenContainer>
  );
}

function FeatureItem({ icon, title, description }: { icon: string; title: string; description: string }) {
  const colors = useColors();
  
  return (
    <View style={styles.featureItem}>
      <Text style={styles.featureIcon}>{icon}</Text>
      <View style={styles.featureText}>
        <Text style={[styles.featureTitle, { color: colors.primary }]}>{title}</Text>
        <Text style={[styles.featureDescription, { color: colors.muted }]}>{description}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: "space-between",
  },
  logoSection: {
    alignItems: "center",
    paddingTop: 40,
  },
  contentSection: {
    flex: 1,
    justifyContent: "center",
    paddingVertical: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 16,
    lineHeight: 40,
  },
  subtitle: {
    fontSize: 16,
    textAlign: "center",
    lineHeight: 24,
    marginBottom: 32,
  },
  features: {
    gap: 16,
  },
  featureItem: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#112240",
    padding: 16,
    borderRadius: 12,
  },
  featureIcon: {
    fontSize: 28,
    marginRight: 16,
  },
  featureText: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 2,
  },
  featureDescription: {
    fontSize: 14,
  },
  buttonsSection: {
    gap: 12,
    paddingBottom: 16,
  },
  footer: {
    fontSize: 12,
    textAlign: "center",
    paddingBottom: 16,
  },
});
