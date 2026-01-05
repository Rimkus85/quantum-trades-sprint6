import React from "react";
import { ScrollView, Text, View, Pressable, StyleSheet } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";

export default function DashboardScreen() {
  const colors = useColors();
  const { user, logout } = useLocalAuth();

  const handleLogout = async () => {
    await logout();
    router.replace("/(auth)/welcome" as any);
  };

  return (
    <ScreenContainer className="p-0">
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Logo size="sm" showText={false} />
          <View style={styles.headerRight}>
            <Pressable
              onPress={handleLogout}
              style={({ pressed }) => [
                styles.logoutButton,
                { backgroundColor: colors.surface },
                pressed && styles.pressed,
              ]}
            >
              <MaterialIcons name="logout" size={20} color={colors.muted} />
            </Pressable>
          </View>
        </View>

        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <Text style={[styles.welcomeText, { color: colors.muted }]}>
            Bem-vindo de volta,
          </Text>
          <Text style={[styles.userName, { color: colors.foreground }]}>
            {user?.name?.split(" ")[0] || "Trader"}
          </Text>
        </View>

        {/* Portfolio Card */}
        <View style={[styles.portfolioCard, { backgroundColor: colors.surface }]}>
          <Text style={[styles.portfolioLabel, { color: colors.muted }]}>
            Seu Portfólio
          </Text>
          <Text style={[styles.portfolioValue, { color: colors.foreground }]}>
            R$ 0,00
          </Text>
          <View style={styles.portfolioChange}>
            <MaterialIcons name="trending-up" size={16} color={colors.success} />
            <Text style={[styles.portfolioChangeText, { color: colors.success }]}>
              +R$ 0,00 (0,00%)
            </Text>
          </View>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsRow}>
          <StatCard
            title="Operações"
            value="0"
            icon="swap-horiz"
            color={colors.primary}
          />
          <StatCard
            title="Win Rate"
            value="0%"
            icon="trending-up"
            color={colors.success}
          />
        </View>

        {/* Recent Operations */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
            Operações Recentes
          </Text>
          
          <View style={[styles.emptyState, { backgroundColor: colors.surface }]}>
            <MaterialIcons name="history" size={48} color={colors.muted} />
            <Text style={[styles.emptyTitle, { color: colors.foreground }]}>
              Nenhuma operação ainda
            </Text>
            <Text style={[styles.emptySubtitle, { color: colors.muted }]}>
              Suas operações aparecerão aqui quando você começar a operar
            </Text>
          </View>
        </View>

        {/* Features Coming Soon */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
            Em Breve
          </Text>
          
          <View style={styles.featuresList}>
            <FeatureItem
              icon="smart-toy"
              title="Bots de Trading"
              description="Automatize suas estratégias"
              color={colors.primary}
            />
            <FeatureItem
              icon="show-chart"
              title="Análise de Mercado"
              description="Dados em tempo real"
              color={colors.warning}
            />
            <FeatureItem
              icon="security"
              title="Gestão de Risco"
              description="Proteção inteligente"
              color={colors.success}
            />
          </View>
        </View>

        {/* User Info */}
        <View style={[styles.userInfoCard, { backgroundColor: colors.surface }]}>
          <View style={styles.userInfoHeader}>
            <MaterialIcons name="person" size={24} color={colors.primary} />
            <Text style={[styles.userInfoTitle, { color: colors.foreground }]}>
              Informações da Conta
            </Text>
          </View>
          
          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>E-mail</Text>
            <Text style={[styles.userInfoValue, { color: colors.foreground }]}>{user?.email}</Text>
          </View>
          
          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>Corretora</Text>
            <Text style={[styles.userInfoValue, { color: colors.foreground }]}>
              {getBrokerName(user?.broker)}
            </Text>
          </View>
          
          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>2FA</Text>
            <View style={styles.userInfo2FA}>
              <MaterialIcons
                name="verified-user"
                size={16}
                color={colors.success}
              />
              <Text style={[styles.userInfoValue, { color: colors.success }]}>
                Ativado
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: string; icon: keyof typeof MaterialIcons.glyphMap; color: string }) {
  const colors = useColors();
  
  return (
    <View style={[styles.statCard, { backgroundColor: colors.surface }]}>
      <View style={[styles.statIcon, { backgroundColor: color + "20" }]}>
        <MaterialIcons name={icon} size={20} color={color} />
      </View>
      <Text style={[styles.statValue, { color: colors.foreground }]}>{value}</Text>
      <Text style={[styles.statTitle, { color: colors.muted }]}>{title}</Text>
    </View>
  );
}

function FeatureItem({ icon, title, description, color }: { icon: keyof typeof MaterialIcons.glyphMap; title: string; description: string; color: string }) {
  const colors = useColors();
  
  return (
    <View style={[styles.featureItem, { backgroundColor: colors.surface }]}>
      <View style={[styles.featureIcon, { backgroundColor: color + "20" }]}>
        <MaterialIcons name={icon} size={24} color={color} />
      </View>
      <View style={styles.featureText}>
        <Text style={[styles.featureTitle, { color: colors.foreground }]}>{title}</Text>
        <Text style={[styles.featureDescription, { color: colors.muted }]}>{description}</Text>
      </View>
      <MaterialIcons name="chevron-right" size={20} color={colors.muted} />
    </View>
  );
}

function getBrokerName(broker?: string): string {
  const brokers: Record<string, string> = {
    xp: "XP Investimentos",
    btg: "BTG Pactual",
    clear: "Clear Corretora",
    rico: "Rico Investimentos",
    inter: "Inter Invest",
    nubank: "Nubank Investimentos",
    binance: "Binance",
    mercadobitcoin: "Mercado Bitcoin",
    other: "Outra",
  };
  return brokers[broker || ""] || "Não informada";
}

const styles = StyleSheet.create({
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 100,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 16,
  },
  headerRight: {
    flexDirection: "row",
    gap: 12,
  },
  logoutButton: {
    padding: 10,
    borderRadius: 12,
  },
  pressed: {
    opacity: 0.7,
  },
  welcomeSection: {
    marginBottom: 20,
  },
  welcomeText: {
    fontSize: 14,
  },
  userName: {
    fontSize: 28,
    fontWeight: "700",
  },
  portfolioCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  portfolioLabel: {
    fontSize: 14,
    marginBottom: 4,
  },
  portfolioValue: {
    fontSize: 32,
    fontWeight: "700",
    marginBottom: 8,
  },
  portfolioChange: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  portfolioChangeText: {
    fontSize: 14,
    fontWeight: "500",
  },
  statsRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  statIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "700",
  },
  statTitle: {
    fontSize: 12,
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 12,
  },
  emptyState: {
    padding: 32,
    borderRadius: 16,
    alignItems: "center",
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "600",
    marginTop: 12,
    marginBottom: 4,
  },
  emptySubtitle: {
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
  featuresList: {
    gap: 12,
  },
  featureItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  featureIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  featureText: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "600",
  },
  featureDescription: {
    fontSize: 12,
    marginTop: 2,
  },
  userInfoCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 24,
  },
  userInfoHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 16,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1e3a5f",
  },
  userInfoTitle: {
    fontSize: 16,
    fontWeight: "600",
  },
  userInfoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
  },
  userInfoLabel: {
    fontSize: 14,
  },
  userInfoValue: {
    fontSize: 14,
    fontWeight: "500",
  },
  userInfo2FA: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
});
