import React from "react";
import { View, StyleSheet } from "react-native";
import { Image } from "expo-image";

interface LogoProps {
  size?: "xs" | "sm" | "md" | "lg" | "xl";
}

const SIZES = {
  xs: { width: 80, height: 60 },
  sm: { width: 120, height: 90 },
  md: { width: 180, height: 135 },
  lg: { width: 240, height: 180 },
  xl: { width: 320, height: 240 },
};

/**
 * Logo component that displays the Quantum Trades logo.
 * The PNG already contains the "QUANTUM TRADES" text, so no additional text is rendered.
 */
export function Logo({ size = "md" }: LogoProps) {
  const dimensions = SIZES[size];

  return (
    <View style={styles.container}>
      <Image
        source={require("@/assets/images/logo.png")}
        style={{
          width: dimensions.width,
          height: dimensions.height,
        }}
        contentFit="contain"
        transition={200}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
  },
});
