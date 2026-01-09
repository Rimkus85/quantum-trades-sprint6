/**
 * Dashboard Principal - Sprint 3
 * QT-09: Resumo da carteira
 * QT-10: Distribuição por classe de ativo
 * QT-11: Operações recentes
 * QT-12: Gráfico de performance
 */

import React, { useState } from "react";
import { 
  ScrollView, 
  Text, 
  View, 
  Pressable, 
  StyleSheet, 
  RefreshControl,
  TouchableOpacity,
} from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { AnimatedScreen } from "@/components/animated-screen";
import { Logo } from "@/components/ui/logo";
import { useColors } from "@/hooks/use-colors";
import { useLocalAuth } from "@/lib/auth-context";
import { ExpandableChart } from "@/components/charts/expandable-chart";
import { DonutChart } from "@/components/charts/donut-chart";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Importar dados mockados
import {
  MOCK_PORTFOLIO,
  MOCK_ASSET_CLASSES,
  MOCK_OPERATIONS,
  MOCK_TRADING_STATS,
  getPerformanceData,
  formatCurrency,
  formatPercent,
  formatDate,
  type Operation,
  type AssetClass,
} from "@/lib/mock-data";

// Períodos disponíveis para o gráfico
const PERIODS = [
  { id: "7d", label: "1S" },
  { id: "30d", label: "1M" },
  { id: "90d", label: "3M" },
  { id: "1a", label: "1A" },
  { id: "max", label: "MAX" },
] as const;

type PeriodId = typeof PERIODS[number]["id"];

export default function DashboardScreen() {
  const colors = useColors();
  const { user, logout } = useLocalAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodId>("30d");
  const [expandedClass, setExpandedClass] = useState<string | null>(null);

  const handleLogout = async () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    await logout();
    router.replace("/(auth)/welcome" as any);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simular refresh de dados
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handlePeriodChange = (period: PeriodId) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setSelectedPeriod(period);
  };

  const toggleClassExpand = (classId: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setExpandedClass(expandedClass === classId ? null : classId);
  };

  const performanceData = getPerformanceData(selectedPeriod);
  const isPositiveChange = MOCK_PORTFOLIO.totalChangePercent >= 0;

  // Preparar dados para o gráfico de rosca
  const donutData = MOCK_ASSET_CLASSES.map((ac) => ({
    value: ac.value,
    color: ac.color,
    label: ac.name,
  }));

  return (
    <ScreenContainer className="p-0">
      <AnimatedScreen type="fadeSlide" duration={350}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            tintColor={colors.primary}
            colors={[colors.primary]}
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Logo size="sm" />
          <View style={styles.headerRight}>
            <Pressable
              onPress={() => router.push("/(tabs)/notifications" as any)}
              style={({ pressed }) => [
                styles.headerButton,
                { backgroundColor: colors.surface },
                pressed && styles.pressed,
              ]}
            >
              <MaterialIcons name="notifications-none" size={22} color={colors.muted} />
            </Pressable>
            <Pressable
              onPress={handleLogout}
              style={({ pressed }) => [
                styles.headerButton,
                { backgroundColor: colors.surface },
                pressed && styles.pressed,
              ]}
            >
              <MaterialIcons name="logout" size={20} color={colors.muted} />
            </Pressable>
          </View>
        </View>

        {/* QT-09: Resumo do Portfólio */}
        <View style={styles.portfolioSection}>
          <Text style={[styles.portfolioLabel, { color: colors.muted }]}>
            Seu Portfólio
          </Text>
          <Text style={[styles.portfolioValue, { color: colors.foreground }]}>
            {formatCurrency(MOCK_PORTFOLIO.totalValue)}
          </Text>
          <View style={styles.portfolioChange}>
            <MaterialIcons
              name={isPositiveChange ? "trending-up" : "trending-down"}
              size={18}
              color={isPositiveChange ? colors.success : colors.error}
            />
            <Text
              style={[
                styles.portfolioChangeText,
                { color: isPositiveChange ? colors.success : colors.error },
              ]}
            >
              {isPositiveChange ? "+" : ""}
              {formatCurrency(MOCK_PORTFOLIO.totalChange)} ({formatPercent(MOCK_PORTFOLIO.totalChangePercent)})
            </Text>
          </View>
        </View>

        {/* QT-12: Gráfico de Performance */}
        <View style={[styles.chartCard, { backgroundColor: colors.surface }]}>
          <ExpandableChart
            data={performanceData}
            title="Performance da Carteira"
            subtitle={`Período: ${PERIODS.find(p => p.id === selectedPeriod)?.label}`}
            height={200}
            showLabels={false}
            lineColor={colors.primary}
          />
          
          {/* Seletor de período */}
          <View style={styles.periodSelector}>
            {PERIODS.map((period) => (
              <TouchableOpacity
                key={period.id}
                onPress={() => handlePeriodChange(period.id)}
                style={[
                  styles.periodButton,
                  selectedPeriod === period.id && {
                    backgroundColor: colors.primary + "20",
                    borderBottomColor: colors.primary,
                    borderBottomWidth: 2,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.periodText,
                    {
                      color:
                        selectedPeriod === period.id
                          ? colors.primary
                          : colors.muted,
                    },
                  ]}
                >
                  {period.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsRow}>
          <StatCard
            title="Operações"
            value={MOCK_TRADING_STATS.totalTrades.toString()}
            icon="swap-horiz"
            color={colors.primary}
          />
          <StatCard
            title="Win Rate"
            value={`${MOCK_TRADING_STATS.winRate}%`}
            icon="trending-up"
            color={colors.success}
          />
          <StatCard
            title="Retorno Médio"
            value={`${MOCK_TRADING_STATS.avgReturn}%`}
            icon="show-chart"
            color={colors.warning}
          />
        </View>

        {/* QT-10: Distribuição por Classe de Ativo */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
            Distribuição do Portfólio
          </Text>

          <View style={[styles.distributionCard, { backgroundColor: colors.surface }]}>
            {/* Gráfico de Rosca */}
            <View style={styles.donutContainer}>
              <DonutChart
                data={donutData}
                size={180}
                strokeWidth={20}
                centerLabel="Total investido"
                centerValue={formatCurrency(MOCK_PORTFOLIO.totalValue)}
                centerSubtitle={`+${MOCK_PORTFOLIO.monthlyChangePercent}% · Mês`}
              />
            </View>

            {/* Lista de Classes */}
            <View style={styles.classList}>
              {MOCK_ASSET_CLASSES.map((assetClass) => (
                <AssetClassItem
                  key={assetClass.id}
                  assetClass={assetClass}
                  isExpanded={expandedClass === assetClass.id}
                  onToggle={() => toggleClassExpand(assetClass.id)}
                />
              ))}
            </View>
          </View>
        </View>

        {/* QT-11: Operações Recentes */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
              Operações Recentes
            </Text>
            <TouchableOpacity onPress={() => router.push("/(tabs)/operations" as any)}>
              <Text style={[styles.seeAllText, { color: colors.primary }]}>
                Ver todas
              </Text>
            </TouchableOpacity>
          </View>

          <View style={styles.operationsList}>
            {MOCK_OPERATIONS.slice(0, 5).map((operation) => (
              <OperationItem key={operation.id} operation={operation} />
            ))}
          </View>
        </View>

        {/* Informações da Conta */}
        <View style={[styles.userInfoCard, { backgroundColor: colors.surface }]}>
          <View style={styles.userInfoHeader}>
            <MaterialIcons name="person" size={24} color={colors.primary} />
            <Text style={[styles.userInfoTitle, { color: colors.foreground }]}>
              {user?.name || "Trader"}
            </Text>
          </View>

          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>
              Perfil de Risco
            </Text>
            <View style={[styles.badge, { backgroundColor: getBadgeColor(user?.riskProfile, colors) }]}>
              <Text style={styles.badgeText}>
                {getRiskProfileLabel(user?.riskProfile)}
              </Text>
            </View>
          </View>

          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>
              Plano
            </Text>
            <Text style={[styles.userInfoValue, { color: colors.primary }]}>
              {user?.subscriptionStatus === "trial" ? "Trial (7 dias)" : getPlanLabel(user?.selectedPlan)}
            </Text>
          </View>

          <View style={styles.userInfoRow}>
            <Text style={[styles.userInfoLabel, { color: colors.muted }]}>
              2FA
            </Text>
            <View style={styles.userInfo2FA}>
              <MaterialIcons name="verified-user" size={16} color={colors.success} />
              <Text style={[styles.userInfoValue, { color: colors.success }]}>
                Ativado
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
      </AnimatedScreen>
    </ScreenContainer>
  );
}

// Componente de Card de Estatística
function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string;
  icon: keyof typeof MaterialIcons.glyphMap;
  color: string;
}) {
  const colors = useColors();

  return (
    <View style={[styles.statCard, { backgroundColor: colors.surface }]}>
      <View style={[styles.statIcon, { backgroundColor: color + "20" }]}>
        <MaterialIcons name={icon} size={18} color={color} />
      </View>
      <Text style={[styles.statValue, { color: colors.foreground }]}>{value}</Text>
      <Text style={[styles.statTitle, { color: colors.muted }]}>{title}</Text>
    </View>
  );
}

// Componente de Item de Classe de Ativo
function AssetClassItem({
  assetClass,
  isExpanded,
  onToggle,
}: {
  assetClass: AssetClass;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const colors = useColors();

  return (
    <View>
      <TouchableOpacity onPress={onToggle} style={styles.classItem}>
        <View style={[styles.classIndicator, { backgroundColor: assetClass.color }]} />
        <View style={styles.classInfo}>
          <Text style={[styles.className, { color: colors.foreground }]}>
            {assetClass.name}
          </Text>
          <Text style={[styles.classPercent, { color: colors.muted }]}>
            {assetClass.percentage.toFixed(2)}%
          </Text>
        </View>
        <Text style={[styles.classValue, { color: colors.foreground }]}>
          {formatCurrency(assetClass.value)}
        </Text>
        <MaterialIcons
          name={isExpanded ? "expand-less" : "chevron-right"}
          size={20}
          color={colors.muted}
        />
      </TouchableOpacity>

      {/* Lista de ativos expandida */}
      {isExpanded && (
        <View style={[styles.assetsExpanded, { borderLeftColor: assetClass.color }]}>
          {assetClass.assets.map((asset) => (
            <View key={asset.ticker} style={styles.assetItem}>
              <View style={styles.assetInfo}>
                <Text style={[styles.assetTicker, { color: colors.foreground }]}>
                  {asset.ticker}
                </Text>
                <Text style={[styles.assetName, { color: colors.muted }]}>
                  {asset.name}
                </Text>
              </View>
              <View style={styles.assetValues}>
                <Text style={[styles.assetValue, { color: colors.foreground }]}>
                  {formatCurrency(asset.value)}
                </Text>
                <Text
                  style={[
                    styles.assetChange,
                    { color: asset.changePercent >= 0 ? colors.success : colors.error },
                  ]}
                >
                  {formatPercent(asset.changePercent)}
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

// Componente de Item de Operação
function OperationItem({ operation }: { operation: Operation }) {
  const colors = useColors();
  const isPositive = operation.changePercent >= 0;
  const isBuy = operation.type === "compra";

  return (
    <View style={[styles.operationItem, { backgroundColor: colors.surface }]}>
      <View style={styles.operationLeft}>
        <View style={styles.operationHeader}>
          <Text style={[styles.operationTicker, { color: colors.foreground }]}>
            {operation.ticker}
          </Text>
          <View
            style={[
              styles.operationTypeBadge,
              { backgroundColor: isBuy ? colors.success + "20" : colors.error + "20" },
            ]}
          >
            <Text
              style={[
                styles.operationTypeText,
                { color: isBuy ? colors.success : colors.error },
              ]}
            >
              {operation.type.charAt(0).toUpperCase() + operation.type.slice(1)}
            </Text>
          </View>
        </View>
        <Text style={[styles.operationDate, { color: colors.muted }]}>
          {formatDate(operation.date)}
        </Text>
      </View>
      <View style={styles.operationRight}>
        <Text
          style={[
            styles.operationChange,
            { color: isPositive ? colors.success : colors.error },
          ]}
        >
          {formatPercent(operation.changePercent)}
        </Text>
        {isPositive ? (
          <MaterialIcons name="arrow-upward" size={16} color={colors.success} />
        ) : (
          <MaterialIcons name="arrow-downward" size={16} color={colors.error} />
        )}
      </View>
    </View>
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

function getBadgeColor(profile: string | undefined, colors: any): string {
  switch (profile) {
    case "conservador":
      return colors.success + "30";
    case "moderado":
      return colors.warning + "30";
    case "agressivo":
      return colors.error + "30";
    default:
      return colors.muted + "30";
  }
}

function getPlanLabel(plan?: string): string {
  const labels: Record<string, string> = {
    entrada: "Entrada",
    medio: "Médio",
    top: "Top",
  };
  return labels[plan || ""] || "Não selecionado";
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
    gap: 8,
  },
  headerButton: {
    padding: 10,
    borderRadius: 12,
  },
  pressed: {
    opacity: 0.7,
  },
  portfolioSection: {
    marginBottom: 16,
  },
  portfolioLabel: {
    fontSize: 14,
    marginBottom: 4,
  },
  portfolioValue: {
    fontSize: 36,
    fontWeight: "700",
    marginBottom: 4,
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
  chartCard: {
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  periodSelector: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginTop: 16,
  },
  periodButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  periodText: {
    fontSize: 13,
    fontWeight: "600",
  },
  statsRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  statIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 6,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "700",
  },
  statTitle: {
    fontSize: 11,
    marginTop: 2,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 12,
  },
  seeAllText: {
    fontSize: 14,
    fontWeight: "500",
  },
  distributionCard: {
    borderRadius: 16,
    padding: 20,
  },
  donutContainer: {
    alignItems: "center",
    marginBottom: 20,
  },
  classList: {
    gap: 8,
  },
  classItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
  },
  classIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  classInfo: {
    flex: 1,
  },
  className: {
    fontSize: 15,
    fontWeight: "500",
  },
  classPercent: {
    fontSize: 12,
    marginTop: 2,
  },
  classValue: {
    fontSize: 15,
    fontWeight: "600",
    marginRight: 8,
  },
  assetsExpanded: {
    marginLeft: 24,
    paddingLeft: 12,
    borderLeftWidth: 2,
    marginBottom: 8,
  },
  assetItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
  },
  assetInfo: {
    flex: 1,
  },
  assetTicker: {
    fontSize: 14,
    fontWeight: "600",
  },
  assetName: {
    fontSize: 11,
    marginTop: 2,
  },
  assetValues: {
    alignItems: "flex-end",
  },
  assetValue: {
    fontSize: 14,
    fontWeight: "500",
  },
  assetChange: {
    fontSize: 12,
    marginTop: 2,
  },
  operationsList: {
    gap: 8,
  },
  operationItem: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderRadius: 12,
  },
  operationLeft: {
    flex: 1,
  },
  operationHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  operationTicker: {
    fontSize: 16,
    fontWeight: "600",
  },
  operationTypeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  operationTypeText: {
    fontSize: 11,
    fontWeight: "500",
  },
  operationDate: {
    fontSize: 12,
    marginTop: 4,
  },
  operationRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  operationChange: {
    fontSize: 16,
    fontWeight: "600",
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
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#fff",
  },
});
