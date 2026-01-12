/**
 * Componente de Gráfico de Linha para Performance
 * Usa react-native-svg para renderização
 */

import React, { useMemo } from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";
import Svg, { Path, Line, Circle, Defs, LinearGradient, Stop } from "react-native-svg";
import { useColors } from "@/hooks/use-colors";

interface DataPoint {
  date: string;
  value: number;
}

interface LineChartProps {
  data: DataPoint[];
  height?: number;
  width?: number;  // Largura customizada
  showGrid?: boolean;
  showLabels?: boolean;
  lineColor?: string;
  gradientColor?: string;
}

export function LineChart({
  data,
  height = 200,
  width,
  showGrid = true,
  showLabels = true,
  lineColor,
  gradientColor,
}: LineChartProps) {
  const colors = useColors();
  const chartLineColor = lineColor || colors.primary;
  const chartGradientColor = gradientColor || colors.primary;

  const screenWidth = Dimensions.get("window").width;
  const chartWidth = width || (screenWidth - 40); // Usar width customizado ou padrão
  const chartHeight = height;
  const paddingTop = 20;
  const paddingBottom = showLabels ? 30 : 10;
  const paddingLeft = 10;
  const paddingRight = 10;

  const graphWidth = chartWidth - paddingLeft - paddingRight;
  const graphHeight = chartHeight - paddingTop - paddingBottom;

  // Calcular valores min/max e escala
  const { minValue, maxValue, pathD, areaD, points } = useMemo(() => {
    if (data.length === 0) {
      return { minValue: 0, maxValue: 0, pathD: "", areaD: "", points: [] };
    }

    const values = data.map((d) => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Adicionar margem de 5% para visualização
    const range = max - min;
    const margin = range * 0.05;
    const adjustedMin = min - margin;
    const adjustedMax = max + margin;

    // Calcular pontos do gráfico
    const pts = data.map((d, i) => {
      const x = paddingLeft + (i / (data.length - 1)) * graphWidth;
      const y = paddingTop + graphHeight - ((d.value - adjustedMin) / (adjustedMax - adjustedMin)) * graphHeight;
      return { x, y, value: d.value, date: d.date };
    });

    // Criar path da linha
    const linePathD = pts
      .map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`))
      .join(" ");

    // Criar path da área (para gradiente)
    const areaPathD = `${linePathD} L ${pts[pts.length - 1].x} ${chartHeight - paddingBottom} L ${pts[0].x} ${chartHeight - paddingBottom} Z`;

    return {
      minValue: adjustedMin,
      maxValue: adjustedMax,
      pathD: linePathD,
      areaD: areaPathD,
      points: pts,
    };
  }, [data, graphWidth, graphHeight, paddingLeft, paddingTop, paddingBottom, chartHeight]);

  if (data.length === 0) {
    return (
      <View style={[styles.container, { height }]}>
        <Text style={[styles.emptyText, { color: colors.muted }]}>
          Sem dados disponíveis
        </Text>
      </View>
    );
  }

  // Linhas de grade horizontais
  const gridLines = showGrid ? [0, 0.25, 0.5, 0.75, 1] : [];

  return (
    <View style={[styles.container, { height: chartHeight }]}>
      <Svg width={chartWidth} height={chartHeight}>
        <Defs>
          <LinearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0" stopColor={chartGradientColor} stopOpacity="0.3" />
            <Stop offset="1" stopColor={chartGradientColor} stopOpacity="0" />
          </LinearGradient>
        </Defs>

        {/* Linhas de grade */}
        {gridLines.map((ratio, i) => {
          const y = paddingTop + graphHeight * (1 - ratio);
          return (
            <Line
              key={i}
              x1={paddingLeft}
              y1={y}
              x2={chartWidth - paddingRight}
              y2={y}
              stroke={colors.border}
              strokeWidth={0.5}
              strokeDasharray="4,4"
            />
          );
        })}

        {/* Área com gradiente */}
        <Path d={areaD} fill="url(#areaGradient)" />

        {/* Linha do gráfico */}
        <Path
          d={pathD}
          stroke={chartLineColor}
          strokeWidth={2.5}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Ponto final destacado */}
        {points.length > 0 && (
          <>
            <Circle
              cx={points[points.length - 1].x}
              cy={points[points.length - 1].y}
              r={6}
              fill={chartLineColor}
              opacity={0.3}
            />
            <Circle
              cx={points[points.length - 1].x}
              cy={points[points.length - 1].y}
              r={4}
              fill={chartLineColor}
            />
          </>
        )}
      </Svg>

      {/* Labels de data */}
      {showLabels && data.length > 1 && (
        <View style={styles.labelsContainer}>
          <Text style={[styles.label, { color: colors.muted }]}>
            {formatDateLabel(data[0].date)}
          </Text>
          <Text style={[styles.label, { color: colors.muted }]}>
            {formatDateLabel(data[Math.floor(data.length / 2)].date)}
          </Text>
          <Text style={[styles.label, { color: colors.muted }]}>
            {formatDateLabel(data[data.length - 1].date)}
          </Text>
        </View>
      )}
    </View>
  );
}

function formatDateLabel(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "short",
  }).format(date);
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    justifyContent: "center",
    alignItems: "center",
  },
  emptyText: {
    fontSize: 14,
  },
  labelsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "100%",
    paddingHorizontal: 10,
    position: "absolute",
    bottom: 5,
  },
  label: {
    fontSize: 10,
  },
});
