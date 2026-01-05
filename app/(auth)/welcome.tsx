import React from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";


export default function WelcomeScreen() {
  const colors = useColors();

  return (
    <ScreenContainer edges={["top", "bottom", "left", "right"]}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Logo Section - O logo PNG já contém o texto "QUANTUM TRADES" */}
        <View style={styles.logoSection}>
          <Logo size="lg" />
        </View>

        {/* Subtitle Section */}
        <View style={styles.subtitleSection}>
          <Text style={[styles.subtitle, { color: colors.muted }]}>
            Automatize suas estratégias de investimento com nossa IA avançada. 
            Trading 24/7, gestão de risco inteligente e acesso a múltiplos mercados.
          </Text>
        </View>

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
      </ScrollView>
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 40,
    paddingBottom: 24,
  },
  logoSection: {
    alignItems: "center",
    marginBottom: 24,
  },
  subtitleSection: {
    marginBottom: 32,
  },
  subtitle: {
    fontSize: 16,
    textAlign: "center",
    lineHeight: 24,
  },
  features: {
    gap: 12,
    marginBottom: 32,
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
    marginBottom: 16,
  },
  footer: {
    fontSize: 12,
    textAlign: "center",
  },
});
