import React from "react";
import { Pressable, Text, ActivityIndicator, StyleSheet, ViewStyle, TextStyle } from "react-native";
import { cn } from "@/lib/utils";
import { useColors } from "@/hooks/use-colors";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

interface ButtonProps {
  children: React.ReactNode;
  onPress?: () => void;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  textClassName?: string;
  fullWidth?: boolean;
}

export function Button({
  children,
  onPress,
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  className,
  textClassName,
  fullWidth = true,
}: ButtonProps) {
  const colors = useColors();

  const handlePress = () => {
    if (disabled || loading) return;
    
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    
    onPress?.();
  };

  const getVariantStyles = (): { container: ViewStyle; text: TextStyle } => {
    switch (variant) {
      case "primary":
        return {
          container: {
            backgroundColor: disabled ? colors.muted : colors.primary,
          },
          text: {
            color: colors.background,
          },
        };
      case "secondary":
        return {
          container: {
            backgroundColor: colors.surface,
          },
          text: {
            color: colors.foreground,
          },
        };
      case "outline":
        return {
          container: {
            backgroundColor: "transparent",
            borderWidth: 1,
            borderColor: disabled ? colors.muted : colors.primary,
          },
          text: {
            color: disabled ? colors.muted : colors.primary,
          },
        };
      case "ghost":
        return {
          container: {
            backgroundColor: "transparent",
          },
          text: {
            color: disabled ? colors.muted : colors.primary,
          },
        };
      default:
        return {
          container: {},
          text: {},
        };
    }
  };

  const getSizeStyles = (): { container: ViewStyle; text: TextStyle } => {
    switch (size) {
      case "sm":
        return {
          container: { paddingVertical: 8, paddingHorizontal: 16 },
          text: { fontSize: 14 },
        };
      case "md":
        return {
          container: { paddingVertical: 14, paddingHorizontal: 24 },
          text: { fontSize: 16 },
        };
      case "lg":
        return {
          container: { paddingVertical: 18, paddingHorizontal: 32 },
          text: { fontSize: 18 },
        };
      default:
        return {
          container: {},
          text: {},
        };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <Pressable
      onPress={handlePress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.container,
        variantStyles.container,
        sizeStyles.container,
        fullWidth && styles.fullWidth,
        pressed && !disabled && styles.pressed,
        disabled && styles.disabled,
      ]}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === "primary" ? colors.background : colors.primary}
        />
      ) : (
        <Text
          className={cn("font-semibold text-center", textClassName)}
          style={[variantStyles.text, sizeStyles.text]}
        >
          {children}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "row",
  },
  fullWidth: {
    width: "100%",
  },
  pressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  disabled: {
    opacity: 0.5,
  },
});
