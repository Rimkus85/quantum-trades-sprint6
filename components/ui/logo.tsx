import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Image } from "expo-image";

interface LogoProps {
  size?: "sm" | "md" | "lg" | "xl";
  showText?: boolean;
}

const SIZES = {
  sm: { image: 40, fontSize: 14, subtitleSize: 10 },
  md: { image: 60, fontSize: 18, subtitleSize: 12 },
  lg: { image: 80, fontSize: 24, subtitleSize: 14 },
  xl: { image: 120, fontSize: 32, subtitleSize: 16 },
};

export function Logo({ size = "md", showText = true }: LogoProps) {
  const dimensions = SIZES[size];

  return (
    <View style={styles.container}>
      <Image
        source={require("@/assets/images/logo_final.png")}
        style={{
          width: dimensions.image,
          height: dimensions.image,
        }}
        contentFit="contain"
      />
      {showText && (
        <View style={styles.textContainer}>
          <Text
            style={[
              styles.title,
              { fontSize: dimensions.fontSize },
            ]}
          >
            QUANTUM
          </Text>
          <Text
            style={[
              styles.subtitle,
              { fontSize: dimensions.subtitleSize },
            ]}
          >
            TRADES
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
  },
  textContainer: {
    alignItems: "center",
    marginTop: 8,
  },
  title: {
    color: "#FFD700",
    fontWeight: "700",
    letterSpacing: 2,
  },
  subtitle: {
    color: "#FFD700",
    fontWeight: "400",
    letterSpacing: 4,
    marginTop: 2,
  },
});
