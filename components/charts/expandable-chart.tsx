/**
 * Componente de Gráfico Expansível com Rotação
 * Permite expandir o gráfico em tela cheia com orientação paisagem
 */

import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  Dimensions,
  Platform,
} from "react-native";
import { LineChart } from "./line-chart";
import MaterialIcons from "@expo/vector-icons/MaterialIcons";
import { useColors } from "@/hooks/use-colors";
import * as Haptics from "expo-haptics";
import * as ScreenOrientation from "expo-screen-orientation";

interface DataPoint {
  date: string;
  value: number;
}

interface ExpandableChartProps {
  data: DataPoint[];
  title?: string;
  subtitle?: string;
  height?: number;
  showGrid?: boolean;
  showLabels?: boolean;
  lineColor?: string;
}

export function ExpandableChart({
  data,
  title = "Performance",
  subtitle,
  height = 200,
  showGrid = true,
  showLabels = true,
  lineColor,
}: ExpandableChartProps) {
  const colors = useColors();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLandscape, setIsLandscape] = useState(false);

  const handleExpand = async () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    setIsExpanded(true);

    // Forçar orientação paisagem em dispositivos móveis
    if (Platform.OS !== "web") {
      try {
        await ScreenOrientation.lockAsync(
          ScreenOrientation.OrientationLock.LANDSCAPE
        );
        setIsLandscape(true);
      } catch (error) {
        console.log("Não foi possível rotacionar a tela:", error);
      }
    }
  };

  const handleClose = async () => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    // Restaurar orientação retrato
    if (Platform.OS !== "web" && isLandscape) {
      try {
        await ScreenOrientation.lockAsync(
          ScreenOrientation.OrientationLock.PORTRAIT
        );
        setIsLandscape(false);
      } catch (error) {
        console.log("Não foi possível restaurar orientação:", error);
      }
    }

    setIsExpanded(false);
  };

  const screenDimensions = Dimensions.get("window");
  const expandedHeight = isLandscape
    ? screenDimensions.width * 0.7
    : screenDimensions.height * 0.6;

  return (
    <>
      {/* Gráfico Normal */}
      <View style={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={[styles.title, { color: colors.foreground }]}>
              {title}
            </Text>
            {subtitle && (
              <Text style={[styles.subtitle, { color: colors.muted }]}>
                {subtitle}
              </Text>
            )}
          </View>
          <TouchableOpacity
            onPress={handleExpand}
            style={[styles.expandButton, { backgroundColor: colors.surface }]}
          >
            <MaterialIcons name="fullscreen" size={20} color={colors.primary} />
          </TouchableOpacity>
        </View>

        <LineChart
          data={data}
          height={height}
          showGrid={showGrid}
          showLabels={showLabels}
          lineColor={lineColor}
        />
      </View>

      {/* Modal Expandido */}
      <Modal
        visible={isExpanded}
        animationType="fade"
        transparent={false}
        onRequestClose={handleClose}
      >
        <View
          style={[
            styles.modalContainer,
            { backgroundColor: colors.background },
          ]}
        >
          {/* Header do Modal */}
          <View style={styles.modalHeader}>
            <View>
              <Text style={[styles.modalTitle, { color: colors.foreground }]}>
                {title}
              </Text>
              {subtitle && (
                <Text style={[styles.modalSubtitle, { color: colors.muted }]}>
                  {subtitle}
                </Text>
              )}
            </View>
            <TouchableOpacity
              onPress={handleClose}
              style={[
                styles.closeButton,
                { backgroundColor: colors.surface },
              ]}
            >
              <MaterialIcons
                name="close"
                size={24}
                color={colors.foreground}
              />
            </TouchableOpacity>
          </View>

          {/* Gráfico Expandido */}
          <View style={styles.chartContainer}>
            <LineChart
              data={data}
              height={expandedHeight}
              showGrid={true}
              showLabels={true}
              lineColor={lineColor}
            />
          </View>

          {/* Estatísticas */}
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={[styles.statLabel, { color: colors.muted }]}>
                Mínimo
              </Text>
              <Text style={[styles.statValue, { color: colors.foreground }]}>
                {formatCurrency(Math.min(...data.map((d) => d.value)))}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statLabel, { color: colors.muted }]}>
                Máximo
              </Text>
              <Text style={[styles.statValue, { color: colors.foreground }]}>
                {formatCurrency(Math.max(...data.map((d) => d.value)))}
              </Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statLabel, { color: colors.muted }]}>
                Atual
              </Text>
              <Text style={[styles.statValue, { color: colors.primary }]}>
                {formatCurrency(data[data.length - 1]?.value || 0)}
              </Text>
            </View>
          </View>

          {/* Dica de Rotação */}
          {!isLandscape && Platform.OS !== "web" && (
            <View style={styles.rotationHint}>
              <MaterialIcons
                name="screen-rotation"
                size={20}
                color={colors.muted}
              />
              <Text style={[styles.rotationText, { color: colors.muted }]}>
                Gire o dispositivo para melhor visualização
              </Text>
            </View>
          )}
        </View>
      </Modal>
    </>
  );
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value);
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  title: {
    fontSize: 16,
    fontWeight: "600",
  },
  subtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  expandButton: {
    padding: 8,
    borderRadius: 8,
  },
  modalContainer: {
    flex: 1,
    padding: 20,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 24,
    marginTop: 40,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: "700",
  },
  modalSubtitle: {
    fontSize: 14,
    marginTop: 4,
  },
  closeButton: {
    padding: 10,
    borderRadius: 12,
  },
  chartContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    marginTop: 24,
    paddingTop: 24,
    borderTopWidth: 1,
    borderTopColor: "#1e3a5f",
  },
  statItem: {
    alignItems: "center",
  },
  statLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  statValue: {
    fontSize: 18,
    fontWeight: "600",
  },
  rotationHint: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 16,
    gap: 8,
  },
  rotationText: {
    fontSize: 12,
  },
});
