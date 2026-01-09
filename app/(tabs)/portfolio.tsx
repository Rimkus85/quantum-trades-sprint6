/**
 * Tela de Portfólio - QT-10
 * Distribuição detalhada por classe de ativo
 */

import React, { useState } from "react";
import {
  ScrollView,
  Text,
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from "react-native";
import { ScreenContainer } from "@/components/screen-container";
import { AnimatedScreen } from "@/components/animated-screen";
import { useColors } from "@/hooks/use-colors";
import { DonutChart } from "@/components/charts/donut-chart";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

import {
  MOCK_PORTFOLIO,
  MOCK_ASSET_CLASSES,
  formatCurrency,
  formatPercent,
  type AssetClass,
  type Asset,
} from "@/lib/mock-data";

export default function PortfolioScreen() {
  const colors = useColors();
  const [refreshing, setRefreshing] = useState(false);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleSelectClass = (classId: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setSelectedClass(selectedClass === classId ? null : classId);
  };

  // Preparar dados para o gráfico de rosca
  const donutData = MOCK_ASSET_CLASSES.map((ac) => ({
    value: ac.value,
    color: ac.color,
    label: ac.name,
  }));

  const selectedAssetClass = selectedClass
    ? MOCK_ASSET_CLASSES.find((ac) => ac.id === selectedClass)
    : null;

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
          />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>
            Meu Portfólio
          </Text>
        </View>

        {/* Resumo Total */}
        <View style={[styles.summaryCard, { backgroundColor: colors.surface }]}>
          <Text style={[styles.summaryLabel, { color: colors.muted }]}>
            Patrimônio Total
          </Text>
          <Text style={[styles.summaryValue, { color: colors.foreground }]}>
            {formatCurrency(MOCK_PORTFOLIO.totalValue)}
          </Text>
          <View style={styles.summaryChange}>
            <MaterialIcons
              name={MOCK_PORTFOLIO.totalChangePercent >= 0 ? "trending-up" : "trending-down"}
              size={18}
              color={MOCK_PORTFOLIO.totalChangePercent >= 0 ? colors.success : colors.error}
            />
            <Text
              style={[
                styles.summaryChangeText,
                {
                  color:
                    MOCK_PORTFOLIO.totalChangePercent >= 0
                      ? colors.success
                      : colors.error,
                },
              ]}
            >
              {formatPercent(MOCK_PORTFOLIO.totalChangePercent)} hoje
            </Text>
          </View>
        </View>

        {/* Gráfico de Distribuição */}
        <View style={[styles.chartSection, { backgroundColor: colors.surface }]}>
          <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
            Distribuição de Ativos
          </Text>

          <View style={styles.donutContainer}>
            <DonutChart
              data={donutData}
              size={220}
              strokeWidth={28}
              centerLabel="Total investido"
              centerValue={formatCurrency(MOCK_PORTFOLIO.totalValue)}
              centerSubtitle={`+${MOCK_PORTFOLIO.monthlyChangePercent}% · Mês`}
            />
          </View>

          {/* Legenda */}
          <View style={styles.legend}>
            {MOCK_ASSET_CLASSES.map((assetClass) => (
              <TouchableOpacity
                key={assetClass.id}
                onPress={() => handleSelectClass(assetClass.id)}
                style={[
                  styles.legendItem,
                  selectedClass === assetClass.id && {
                    backgroundColor: assetClass.color + "20",
                    borderRadius: 8,
                  },
                ]}
              >
                <View
                  style={[styles.legendDot, { backgroundColor: assetClass.color }]}
                />
                <View style={styles.legendInfo}>
                  <Text style={[styles.legendName, { color: colors.foreground }]}>
                    {assetClass.name}
                  </Text>
                  <Text style={[styles.legendPercent, { color: colors.muted }]}>
                    {assetClass.percentage.toFixed(2)}%
                  </Text>
                </View>
                <Text style={[styles.legendValue, { color: colors.foreground }]}>
                  {formatCurrency(assetClass.value)}
                </Text>
                <MaterialIcons
                  name="chevron-right"
                  size={20}
                  color={colors.muted}
                />
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Detalhes da Classe Selecionada */}
        {selectedAssetClass && (
          <View style={[styles.detailsSection, { backgroundColor: colors.surface }]}>
            <View style={styles.detailsHeader}>
              <View
                style={[
                  styles.detailsIndicator,
                  { backgroundColor: selectedAssetClass.color },
                ]}
              />
              <Text style={[styles.detailsTitle, { color: colors.foreground }]}>
                {selectedAssetClass.name}
              </Text>
              <TouchableOpacity onPress={() => setSelectedClass(null)}>
                <MaterialIcons name="close" size={20} color={colors.muted} />
              </TouchableOpacity>
            </View>

            <View style={styles.detailsSummary}>
              <View style={styles.detailsSummaryItem}>
                <Text style={[styles.detailsSummaryLabel, { color: colors.muted }]}>
                  Valor Total
                </Text>
                <Text style={[styles.detailsSummaryValue, { color: colors.foreground }]}>
                  {formatCurrency(selectedAssetClass.value)}
                </Text>
              </View>
              <View style={styles.detailsSummaryItem}>
                <Text style={[styles.detailsSummaryLabel, { color: colors.muted }]}>
                  Participação
                </Text>
                <Text style={[styles.detailsSummaryValue, { color: colors.foreground }]}>
                  {selectedAssetClass.percentage.toFixed(2)}%
                </Text>
              </View>
              <View style={styles.detailsSummaryItem}>
                <Text style={[styles.detailsSummaryLabel, { color: colors.muted }]}>
                  Ativos
                </Text>
                <Text style={[styles.detailsSummaryValue, { color: colors.foreground }]}>
                  {selectedAssetClass.assets.length}
                </Text>
              </View>
            </View>

            {/* Lista de Ativos */}
            <View style={styles.assetsList}>
              {selectedAssetClass.assets.map((asset) => (
                <AssetCard key={asset.ticker} asset={asset} />
              ))}
            </View>
          </View>
        )}

        {/* Lista de Todos os Ativos (quando nenhuma classe selecionada) */}
        {!selectedClass && (
          <View style={styles.allAssetsSection}>
            <Text style={[styles.sectionTitle, { color: colors.foreground }]}>
              Todos os Ativos
            </Text>

            {MOCK_ASSET_CLASSES.map((assetClass) => (
              <View key={assetClass.id} style={styles.classGroup}>
                <View style={styles.classGroupHeader}>
                  <View
                    style={[
                      styles.classGroupIndicator,
                      { backgroundColor: assetClass.color },
                    ]}
                  />
                  <Text style={[styles.classGroupTitle, { color: colors.foreground }]}>
                    {assetClass.name}
                  </Text>
                </View>

                {assetClass.assets.map((asset) => (
                  <AssetCard key={asset.ticker} asset={asset} compact />
                ))}
              </View>
            ))}
          </View>
        )}
      </ScrollView>
      </AnimatedScreen>
    </ScreenContainer>
  );
}

// Componente de Card de Ativo
function AssetCard({ asset, compact = false }: { asset: Asset; compact?: boolean }) {
  const colors = useColors();
  const isPositive = asset.changePercent >= 0;

  return (
    <View style={[styles.assetCard, { backgroundColor: colors.surface }, compact && styles.assetCardCompact]}>
      <View style={styles.assetCardLeft}>
        <Text style={[styles.assetTicker, { color: colors.foreground }]}>
          {asset.ticker}
        </Text>
        <Text style={[styles.assetName, { color: colors.muted }]}>
          {asset.name}
        </Text>
        {!compact && (
          <Text style={[styles.assetQuantity, { color: colors.muted }]}>
            {asset.quantity} unidades
          </Text>
        )}
      </View>

      <View style={styles.assetCardRight}>
        <Text style={[styles.assetValue, { color: colors.foreground }]}>
          {formatCurrency(asset.value)}
        </Text>
        <View style={styles.assetChangeRow}>
          <Text
            style={[
              styles.assetChange,
              { color: isPositive ? colors.success : colors.error },
            ]}
          >
            {formatPercent(asset.changePercent)}
          </Text>
          <MaterialIcons
            name={isPositive ? "arrow-upward" : "arrow-downward"}
            size={14}
            color={isPositive ? colors.success : colors.error}
          />
        </View>
        {!compact && (
          <Text style={[styles.assetPrice, { color: colors.muted }]}>
            @ {formatCurrency(asset.currentPrice)}
          </Text>
        )}
      </View>
    </View>
  );
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
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: "700",
  },
  summaryCard: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  summaryLabel: {
    fontSize: 14,
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 32,
    fontWeight: "700",
    marginBottom: 8,
  },
  summaryChange: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  summaryChangeText: {
    fontSize: 14,
    fontWeight: "500",
  },
  chartSection: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 16,
  },
  donutContainer: {
    alignItems: "center",
    marginBottom: 20,
  },
  legend: {
    gap: 8,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  legendInfo: {
    flex: 1,
  },
  legendName: {
    fontSize: 15,
    fontWeight: "500",
  },
  legendPercent: {
    fontSize: 12,
    marginTop: 2,
  },
  legendValue: {
    fontSize: 15,
    fontWeight: "600",
    marginRight: 8,
  },
  detailsSection: {
    padding: 20,
    borderRadius: 16,
    marginBottom: 16,
  },
  detailsHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  detailsIndicator: {
    width: 4,
    height: 24,
    borderRadius: 2,
    marginRight: 12,
  },
  detailsTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: "600",
  },
  detailsSummary: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#1e3a5f",
  },
  detailsSummaryItem: {
    alignItems: "center",
  },
  detailsSummaryLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  detailsSummaryValue: {
    fontSize: 16,
    fontWeight: "600",
  },
  assetsList: {
    gap: 12,
  },
  assetCard: {
    padding: 16,
    borderRadius: 12,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  assetCardCompact: {
    padding: 12,
    marginBottom: 8,
    marginLeft: 24,
    borderLeftWidth: 2,
    borderLeftColor: "#1e3a5f",
    borderRadius: 0,
    borderTopRightRadius: 8,
    borderBottomRightRadius: 8,
  },
  assetCardLeft: {
    flex: 1,
  },
  assetTicker: {
    fontSize: 16,
    fontWeight: "600",
  },
  assetName: {
    fontSize: 12,
    marginTop: 2,
  },
  assetQuantity: {
    fontSize: 11,
    marginTop: 4,
  },
  assetCardRight: {
    alignItems: "flex-end",
  },
  assetValue: {
    fontSize: 16,
    fontWeight: "600",
  },
  assetChangeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 2,
    marginTop: 2,
  },
  assetChange: {
    fontSize: 13,
    fontWeight: "500",
  },
  assetPrice: {
    fontSize: 11,
    marginTop: 4,
  },
  allAssetsSection: {
    marginBottom: 24,
  },
  classGroup: {
    marginBottom: 16,
  },
  classGroupHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  classGroupIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  classGroupTitle: {
    fontSize: 14,
    fontWeight: "600",
  },
});
