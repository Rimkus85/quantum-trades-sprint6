/**
 * Tela de Menu/Perfil - Configurações e informações do usuário
 */

import React from "react";
import {
  ScrollView,
  Text,
  View,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

export default function MenuScreen() {
  const colors = useColors();
  const { user, logout } = useLocalAuth();

  const handleLogout = async () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    Alert.alert(
      "Sair da conta",
      "Tem certeza que deseja sair?",
      [
        { text: "Cancelar", style: "cancel" },
        {
          text: "Sair",
          style: "destructive",
          onPress: async () => {
            await logout();
            router.replace("/(auth)/welcome" as any);
          },
        },
      ]
    );
  };

  const handlePress = (action: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    
    // Placeholder para navegação futura
    Alert.alert("Em breve", `A funcionalidade "${action}" estará disponível em breve.`);
  };

  return (
    <ScreenContainer className="p-0">
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header do Perfil */}
        <View style={[styles.profileHeader, { backgroundColor: colors.surface }]}>
          <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
            <Text style={styles.avatarText}>
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </Text>
          </View>
          <Text style={[styles.userName, { color: colors.foreground }]}>
            {user?.name || "Usuário"}
          </Text>
          <Text style={[styles.userEmail, { color: colors.muted }]}>
            {user?.email}
          </Text>
          
          {/* Badge de Plano */}
          <View style={[styles.planBadge, { backgroundColor: colors.primary + "20" }]}>
            <MaterialIcons name="star" size={16} color={colors.primary} />
            <Text style={[styles.planText, { color: colors.primary }]}>
              {user?.subscriptionStatus === "trial" 
                ? "Trial (7 dias)" 
                : getPlanLabel(user?.selectedPlan)}
            </Text>
          </View>
        </View>

        {/* Informações da Conta */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.muted }]}>
            CONTA
          </Text>
          
          <View style={[styles.menuGroup, { backgroundColor: colors.surface }]}>
            <MenuItem
              icon="person"
              label="Dados Pessoais"
              onPress={() => handlePress("Dados Pessoais")}
            />
            <MenuItem
              icon="security"
              label="Segurança"
              sublabel="2FA ativado"
              onPress={() => handlePress("Segurança")}
            />
            <MenuItem
              icon="credit-card"
              label="Assinatura"
              sublabel={user?.subscriptionStatus === "trial" ? "Trial" : getPlanLabel(user?.selectedPlan)}
              onPress={() => handlePress("Assinatura")}
            />
          </View>
        </View>

        {/* Perfil de Investidor */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.muted }]}>
            PERFIL DE INVESTIDOR
          </Text>
          
          <View style={[styles.menuGroup, { backgroundColor: colors.surface }]}>
            <MenuItem
              icon="assessment"
              label="Perfil de Risco"
              sublabel={getRiskProfileLabel(user?.riskProfile)}
              onPress={() => handlePress("Perfil de Risco")}
            />
            <MenuItem
              icon="account-balance"
              label="Corretoras"
              sublabel={getBrokerLabel(user?.broker)}
              onPress={() => handlePress("Corretoras")}
            />
          </View>
        </View>

        {/* Configurações */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.muted }]}>
            CONFIGURAÇÕES
          </Text>
          
          <View style={[styles.menuGroup, { backgroundColor: colors.surface }]}>
            <MenuItem
              icon="notifications"
              label="Notificações"
              onPress={() => handlePress("Notificações")}
            />
            <MenuItem
              icon="palette"
              label="Aparência"
              sublabel="Escuro"
              onPress={() => handlePress("Aparência")}
            />
            <MenuItem
              icon="language"
              label="Idioma"
              sublabel="Português (BR)"
              onPress={() => handlePress("Idioma")}
            />
          </View>
        </View>

        {/* Integrações */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.muted }]}>
            INTEGRAÇÕES
          </Text>
          
          <View style={[styles.menuGroup, { backgroundColor: colors.surface }]}>
            <MenuItem
              icon="send"
              label="Telegram"
              sublabel={user?.telegram ? "Conectado" : "Não conectado"}
              onPress={() => handlePress("Telegram")}
            />
            <MenuItem
              icon="sync"
              label="Cedro OMS"
              sublabel="Em breve"
              onPress={() => handlePress("Cedro OMS")}
              disabled
            />
          </View>
        </View>

        {/* Suporte */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.muted }]}>
            SUPORTE
          </Text>
          
          <View style={[styles.menuGroup, { backgroundColor: colors.surface }]}>
            <MenuItem
              icon="help"
              label="Central de Ajuda"
              onPress={() => handlePress("Central de Ajuda")}
            />
            <MenuItem
              icon="chat"
              label="Fale Conosco"
              onPress={() => handlePress("Fale Conosco")}
            />
            <MenuItem
              icon="description"
              label="Termos de Uso"
              onPress={() => handlePress("Termos de Uso")}
            />
            <MenuItem
              icon="privacy-tip"
              label="Política de Privacidade"
              onPress={() => handlePress("Política de Privacidade")}
            />
          </View>
        </View>

        {/* Logout */}
        <TouchableOpacity
          onPress={handleLogout}
          style={[styles.logoutButton, { backgroundColor: colors.error + "15" }]}
        >
          <MaterialIcons name="logout" size={20} color={colors.error} />
          <Text style={[styles.logoutText, { color: colors.error }]}>
            Sair da Conta
          </Text>
        </TouchableOpacity>

        {/* Versão */}
        <Text style={[styles.version, { color: colors.muted }]}>
          Quantum Trades v1.0.0 (MVP)
        </Text>
      </ScrollView>
    </ScreenContainer>
  );
}

// Componente de Item de Menu
function MenuItem({
  icon,
  label,
  sublabel,
  onPress,
  disabled = false,
}: {
  icon: keyof typeof MaterialIcons.glyphMap;
  label: string;
  sublabel?: string;
  onPress: () => void;
  disabled?: boolean;
}) {
  const colors = useColors();

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled}
      style={[styles.menuItem, disabled && styles.menuItemDisabled]}
    >
      <View style={[styles.menuIconContainer, { backgroundColor: colors.primary + "15" }]}>
        <MaterialIcons name={icon} size={20} color={colors.primary} />
      </View>
      <View style={styles.menuContent}>
        <Text style={[styles.menuLabel, { color: colors.foreground }]}>
          {label}
        </Text>
        {sublabel && (
          <Text style={[styles.menuSublabel, { color: colors.muted }]}>
            {sublabel}
          </Text>
        )}
      </View>
      <MaterialIcons name="chevron-right" size={20} color={colors.muted} />
    </TouchableOpacity>
  );
}

// Funções auxiliares
function getRiskProfileLabel(profile?: string): string {
  const labels: Record<string, string> = {
    conservador: "Conservador",
    moderado: "Moderado",
    agressivo: "Agressivo",
  };
  return labels[profile || ""] || "Não definido";
}

function getPlanLabel(plan?: string): string {
  const labels: Record<string, string> = {
    entrada: "Plano Entrada",
    medio: "Plano Médio",
    top: "Plano Top",
  };
  return labels[plan || ""] || "Não selecionado";
}

function getBrokerLabel(broker?: string): string {
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
  profileHeader: {
    alignItems: "center",
    padding: 24,
    borderRadius: 16,
    marginTop: 20,
    marginBottom: 24,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: "700",
    color: "#fff",
  },
  userName: {
    fontSize: 22,
    fontWeight: "700",
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    marginBottom: 12,
  },
  planBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 6,
  },
  planText: {
    fontSize: 13,
    fontWeight: "600",
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: "600",
    letterSpacing: 1,
    marginBottom: 8,
    marginLeft: 4,
  },
  menuGroup: {
    borderRadius: 16,
    overflow: "hidden",
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 0.5,
    borderBottomColor: "#1e3a5f",
  },
  menuItemDisabled: {
    opacity: 0.5,
  },
  menuIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  menuContent: {
    flex: 1,
  },
  menuLabel: {
    fontSize: 15,
    fontWeight: "500",
  },
  menuSublabel: {
    fontSize: 12,
    marginTop: 2,
  },
  logoutButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
    borderRadius: 12,
    gap: 8,
    marginBottom: 16,
  },
  logoutText: {
    fontSize: 16,
    fontWeight: "600",
  },
  version: {
    textAlign: "center",
    fontSize: 12,
    marginBottom: 24,
  },
});
