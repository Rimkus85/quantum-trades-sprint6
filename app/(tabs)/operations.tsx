/**
 * Tela de Operações - QT-11
 * Lista de operações recentes com filtros
 */

import React, { useState, useMemo } from "react";
import {
  ScrollView,
  Text,
  View,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  FlatList,
} from "react-native";
import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";
import { LineChart } from "@/components/charts/line-chart";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

import {
  MOCK_OPERATIONS,
  MOCK_PERFORMANCE_30D,
  formatCurrency,
  formatPercent,
  type Operation,
} from "@/lib/mock-data";

// Filtros disponíveis
const FILTERS = {
  period: [
    { id: "all", label: "Todos" },
    { id: "today", label: "Hoje" },
    { id: "week", label: "Semana" },
    { id: "month", label: "Mês" },
  ],
  type: [
    { id: "all", label: "Todos" },
    { id: "compra", label: "Compra" },
    { id: "venda", label: "Venda" },
  ],
  status: [
    { id: "all", label: "Todos" },
    { id: "executada", label: "Executada" },
    { id: "pendente", label: "Pendente" },
    { id: "cancelada", label: "Cancelada" },
  ],
};

export default function OperationsScreen() {
  const colors = useColors();
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState("all");
  const [selectedType, setSelectedType] = useState("all");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const handleFilterChange = (filterType: string, value: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    if (filterType === "period") {
      setSelectedPeriod(value);
    } else if (filterType === "type") {
      setSelectedType(value);
    }
  };

  const toggleFilters = () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setShowFilters(!showFilters);
  };

  // Filtrar operações
  const filteredOperations = useMemo(() => {
    let result = [...MOCK_OPERATIONS];

    // Filtro por tipo
    if (selectedType !== "all") {
      result = result.filter((op) => op.type === selectedType);
    }

    // Filtro por período
    if (selectedPeriod !== "all") {
      const now = new Date();
      const filterDate = new Date();

      switch (selectedPeriod) {
        case "today":
          filterDate.setHours(0, 0, 0, 0);
          break;
        case "week":
          filterDate.setDate(now.getDate() - 7);
          break;
        case "month":
          filterDate.setMonth(now.getMonth() - 1);
          break;
      }

      result = result.filter((op) => new Date(op.date) >= filterDate);
    }

    return result;
  }, [selectedPeriod, selectedType]);

  // Estatísticas das operações filtradas
  const stats = useMemo(() => {
    const total = filteredOperations.length;
    const compras = filteredOperations.filter((op) => op.type === "compra").length;
    const vendas = filteredOperations.filter((op) => op.type === "venda").length;
    const positivas = filteredOperations.filter((op) => op.changePercent > 0).length;
    const winRate = total > 0 ? ((positivas / total) * 100).toFixed(1) : "0";

    return { total, compras, vendas, winRate };
  }, [filteredOperations]);

  return (
    <ScreenContainer className="p-0">
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.headerTitle, { color: colors.foreground }]}>
            Operações
          </Text>
          <TouchableOpacity
            onPress={toggleFilters}
            style={[styles.filterButton, { backgroundColor: colors.surface }]}
          >
            <MaterialIcons
              name="filter-list"
              size={20}
              color={showFilters ? colors.primary : colors.muted}
            />
          </TouchableOpacity>
        </View>

        {/* Gráfico de Performance */}
        <View style={[styles.chartCard, { backgroundColor: colors.surface }]}>
          <Text style={[styles.chartTitle, { color: colors.foreground }]}>
            Performance do Período
          </Text>
          <LineChart
            data={MOCK_PERFORMANCE_30D}
            height={150}
            lineColor={colors.primary}
            showLabels={false}
          />
        </View>

        {/* Estatísticas Rápidas */}
        <View style={styles.statsRow}>
          <View style={[styles.statItem, { backgroundColor: colors.surface }]}>
            <Text style={[styles.statValue, { color: colors.foreground }]}>
              {stats.total}
            </Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>Total</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: colors.surface }]}>
            <Text style={[styles.statValue, { color: colors.success }]}>
              {stats.compras}
            </Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>Compras</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: colors.surface }]}>
            <Text style={[styles.statValue, { color: colors.error }]}>
              {stats.vendas}
            </Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>Vendas</Text>
          </View>
          <View style={[styles.statItem, { backgroundColor: colors.surface }]}>
            <Text style={[styles.statValue, { color: colors.primary }]}>
              {stats.winRate}%
            </Text>
            <Text style={[styles.statLabel, { color: colors.muted }]}>Win Rate</Text>
          </View>
        </View>

        {/* Filtros */}
        {showFilters && (
          <View style={[styles.filtersContainer, { backgroundColor: colors.surface }]}>
            <Text style={[styles.filterTitle, { color: colors.foreground }]}>
              Período
            </Text>
            <View style={styles.filterOptions}>
              {FILTERS.period.map((filter) => (
                <TouchableOpacity
                  key={filter.id}
                  onPress={() => handleFilterChange("period", filter.id)}
                  style={[
                    styles.filterChip,
                    {
                      backgroundColor:
                        selectedPeriod === filter.id
                          ? colors.primary
                          : colors.background,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.filterChipText,
                      {
                        color:
                          selectedPeriod === filter.id
                            ? colors.background
                            : colors.foreground,
                      },
                    ]}
                  >
                    {filter.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={[styles.filterTitle, { color: colors.foreground }]}>
              Tipo
            </Text>
            <View style={styles.filterOptions}>
              {FILTERS.type.map((filter) => (
                <TouchableOpacity
                  key={filter.id}
                  onPress={() => handleFilterChange("type", filter.id)}
                  style={[
                    styles.filterChip,
                    {
                      backgroundColor:
                        selectedType === filter.id
                          ? colors.primary
                          : colors.background,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.filterChipText,
                      {
                        color:
                          selectedType === filter.id
                            ? colors.background
                            : colors.foreground,
                      },
                    ]}
                  >
                    {filter.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* Lista de Operações */}
        <FlatList
          data={filteredOperations}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <OperationCard
              operation={item}
              onPress={() => setSelectedOperation(item)}
            />
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyState}>
              <MaterialIcons name="history" size={48} color={colors.muted} />
              <Text style={[styles.emptyText, { color: colors.muted }]}>
                Nenhuma operação encontrada
              </Text>
            </View>
          }
        />

        {/* Modal de Detalhes */}
        {selectedOperation && (
          <OperationDetails
            operation={selectedOperation}
            onClose={() => setSelectedOperation(null)}
          />
        )}
      </View>
    </ScreenContainer>
  );
}

// Componente de Card de Operação
function OperationCard({
  operation,
  onPress,
}: {
  operation: Operation;
  onPress: () => void;
}) {
  const colors = useColors();
  const isPositive = operation.changePercent >= 0;
  const isBuy = operation.type === "compra";

  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.operationCard, { backgroundColor: colors.surface }]}
    >
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
        <Text style={[styles.operationDetails, { color: colors.muted }]}>
          {operation.quantity} @ {formatCurrency(operation.price)}
        </Text>
        <Text style={[styles.operationDate, { color: colors.muted }]}>
          {formatOperationDate(operation.date)}
        </Text>
      </View>

      <View style={styles.operationRight}>
        <Text style={[styles.operationTotal, { color: colors.foreground }]}>
          {formatCurrency(operation.total)}
        </Text>
        <View style={styles.operationChangeRow}>
          <Text
            style={[
              styles.operationChange,
              { color: isPositive ? colors.success : colors.error },
            ]}
          >
            {formatPercent(operation.changePercent)}
          </Text>
          <MaterialIcons
            name={isPositive ? "arrow-upward" : "arrow-downward"}
            size={16}
            color={isPositive ? colors.success : colors.error}
          />
        </View>
      </View>
    </TouchableOpacity>
  );
}

// Componente de Detalhes da Operação
function OperationDetails({
  operation,
  onClose,
}: {
  operation: Operation;
  onClose: () => void;
}) {
  const colors = useColors();
  const isPositive = operation.changePercent >= 0;
  const isBuy = operation.type === "compra";

  return (
    <View style={[styles.detailsOverlay, { backgroundColor: "rgba(0,0,0,0.5)" }]}>
      <View style={[styles.detailsModal, { backgroundColor: colors.background }]}>
        <View style={styles.detailsHeader}>
          <Text style={[styles.detailsTitle, { color: colors.foreground }]}>
            Detalhes da Operação
          </Text>
          <TouchableOpacity onPress={onClose}>
            <MaterialIcons name="close" size={24} color={colors.muted} />
          </TouchableOpacity>
        </View>

        <View style={styles.detailsContent}>
          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Ativo
            </Text>
            <Text style={[styles.detailsValue, { color: colors.foreground }]}>
              {operation.ticker}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Tipo
            </Text>
            <View
              style={[
                styles.detailsTypeBadge,
                { backgroundColor: isBuy ? colors.success + "20" : colors.error + "20" },
              ]}
            >
              <Text
                style={[
                  styles.detailsTypeText,
                  { color: isBuy ? colors.success : colors.error },
                ]}
              >
                {operation.type.charAt(0).toUpperCase() + operation.type.slice(1)}
              </Text>
            </View>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Quantidade
            </Text>
            <Text style={[styles.detailsValue, { color: colors.foreground }]}>
              {operation.quantity}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Preço
            </Text>
            <Text style={[styles.detailsValue, { color: colors.foreground }]}>
              {formatCurrency(operation.price)}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Total
            </Text>
            <Text style={[styles.detailsValue, { color: colors.foreground }]}>
              {formatCurrency(operation.total)}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Variação
            </Text>
            <Text
              style={[
                styles.detailsValue,
                { color: isPositive ? colors.success : colors.error },
              ]}
            >
              {formatPercent(operation.changePercent)}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Data/Hora
            </Text>
            <Text style={[styles.detailsValue, { color: colors.foreground }]}>
              {formatFullDate(operation.date)}
            </Text>
          </View>

          <View style={styles.detailsRow}>
            <Text style={[styles.detailsLabel, { color: colors.muted }]}>
              Status
            </Text>
            <View
              style={[
                styles.statusBadge,
                { backgroundColor: getStatusColor(operation.status, colors) + "20" },
              ]}
            >
              <Text
                style={[
                  styles.statusText,
                  { color: getStatusColor(operation.status, colors) },
                ]}
              >
                {operation.status.charAt(0).toUpperCase() + operation.status.slice(1)}
              </Text>
            </View>
          </View>
        </View>

        <TouchableOpacity
          onPress={onClose}
          style={[styles.closeButton, { backgroundColor: colors.primary }]}
        >
          <Text style={[styles.closeButtonText, { color: colors.background }]}>
            Fechar
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

// Funções auxiliares
function formatOperationDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatFullDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function getStatusColor(status: string, colors: any): string {
  switch (status) {
    case "executada":
      return colors.success;
    case "pendente":
      return colors.warning;
    case "cancelada":
      return colors.error;
    default:
      return colors.muted;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: "700",
  },
  filterButton: {
    padding: 10,
    borderRadius: 12,
  },
  chartCard: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  chartTitle: {
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 16,
  },
  statItem: {
    flex: 1,
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  statValue: {
    fontSize: 18,
    fontWeight: "700",
  },
  statLabel: {
    fontSize: 10,
    marginTop: 2,
  },
  filtersContainer: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 16,
  },
  filterTitle: {
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
  },
  filterOptions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 16,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  filterChipText: {
    fontSize: 13,
    fontWeight: "500",
  },
  listContent: {
    paddingBottom: 100,
    gap: 8,
  },
  operationCard: {
    flexDirection: "row",
    justifyContent: "space-between",
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
  operationDetails: {
    fontSize: 12,
    marginTop: 4,
  },
  operationDate: {
    fontSize: 11,
    marginTop: 2,
  },
  operationRight: {
    alignItems: "flex-end",
  },
  operationTotal: {
    fontSize: 16,
    fontWeight: "600",
  },
  operationChangeRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 4,
  },
  operationChange: {
    fontSize: 14,
    fontWeight: "600",
  },
  emptyState: {
    alignItems: "center",
    paddingVertical: 48,
  },
  emptyText: {
    fontSize: 14,
    marginTop: 12,
  },
  detailsOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  detailsModal: {
    width: "100%",
    maxWidth: 400,
    borderRadius: 20,
    padding: 20,
  },
  detailsHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  detailsTitle: {
    fontSize: 18,
    fontWeight: "600",
  },
  detailsContent: {
    gap: 16,
  },
  detailsRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  detailsLabel: {
    fontSize: 14,
  },
  detailsValue: {
    fontSize: 14,
    fontWeight: "600",
  },
  detailsTypeBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
  },
  detailsTypeText: {
    fontSize: 13,
    fontWeight: "600",
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 13,
    fontWeight: "600",
  },
  closeButton: {
    marginTop: 24,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  closeButtonText: {
    fontSize: 16,
    fontWeight: "600",
  },
});
