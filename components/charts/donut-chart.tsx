/**
 * Componente de Gráfico de Rosca (Donut) para Distribuição de Ativos
 * Usa react-native-svg para renderização
 */

import React, { useMemo } from "react";
import { View, Text, StyleSheet } from "react-native";
import Svg, { Circle, G } from "react-native-svg";
import { useColors } from "@/hooks/use-colors";

interface DonutSegment {
  value: number;
  color: string;
  label: string;
}

interface DonutChartProps {
  data: DonutSegment[];
  size?: number;
  strokeWidth?: number;
  centerLabel?: string;
  centerValue?: string;
  centerSubtitle?: string;
}

export function DonutChart({
  data,
  size = 200,
  strokeWidth = 24,
  centerLabel,
  centerValue,
  centerSubtitle,
}: DonutChartProps) {
  const colors = useColors();
  
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;

  // Calcular segmentos
  const segments = useMemo(() => {
    const total = data.reduce((sum, d) => sum + d.value, 0);
    if (total === 0) return [];

    let currentOffset = 0;
    return data.map((segment) => {
      const percentage = segment.value / total;
      const strokeDasharray = `${circumference * percentage} ${circumference * (1 - percentage)}`;
      const strokeDashoffset = -currentOffset;
      currentOffset += circumference * percentage;

      return {
        ...segment,
        percentage,
        strokeDasharray,
        strokeDashoffset,
      };
    });
  }, [data, circumference]);

  if (data.length === 0) {
    return (
      <View style={[styles.container, { width: size, height: size }]}>
        <Text style={[styles.emptyText, { color: colors.muted }]}>
          Sem dados
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { width: size, height: size }]}>
      <Svg width={size} height={size}>
        {/* Círculo de fundo */}
        <Circle
          cx={center}
          cy={center}
          r={radius}
          stroke={colors.border}
          strokeWidth={strokeWidth}
          fill="none"
          opacity={0.3}
        />

        {/* Segmentos do gráfico */}
        <G rotation={-90} origin={`${center}, ${center}`}>
          {segments.map((segment, index) => (
            <Circle
              key={index}
              cx={center}
              cy={center}
              r={radius}
              stroke={segment.color}
              strokeWidth={strokeWidth}
              strokeDasharray={segment.strokeDasharray}
              strokeDashoffset={segment.strokeDashoffset}
              strokeLinecap="round"
              fill="none"
            />
          ))}
        </G>
      </Svg>

      {/* Conteúdo central */}
      <View style={styles.centerContent}>
        {centerLabel && (
          <Text style={[styles.centerLabel, { color: colors.muted }]}>
            {centerLabel}
          </Text>
        )}
        {centerValue && (
          <Text style={[styles.centerValue, { color: colors.foreground }]}>
            {centerValue}
          </Text>
        )}
        {centerSubtitle && (
          <Text style={[styles.centerSubtitle, { color: colors.success }]}>
            {centerSubtitle}
          </Text>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  emptyText: {
    fontSize: 14,
  },
  centerContent: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  centerLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  centerValue: {
    fontSize: 20,
    fontWeight: "700",
  },
  centerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
});
