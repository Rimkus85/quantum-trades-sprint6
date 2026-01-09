/**
 * Componente de Tela Animada
 * Adiciona transições suaves de entrada/saída
 */

import React, { useEffect } from "react";
import { View, StyleSheet } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSpring,
  Easing,
} from "react-native-reanimated";

interface AnimatedScreenProps {
  children: React.ReactNode;
  type?: "fade" | "slide" | "scale" | "fadeSlide";
  duration?: number;
  delay?: number;
}

export function AnimatedScreen({
  children,
  type = "fadeSlide",
  duration = 400,
  delay = 0,
}: AnimatedScreenProps) {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(20);
  const scale = useSharedValue(0.95);

  useEffect(() => {
    const timer = setTimeout(() => {
      opacity.value = withTiming(1, {
        duration,
        easing: Easing.out(Easing.cubic),
      });

      if (type === "slide" || type === "fadeSlide") {
        translateY.value = withSpring(0, {
          damping: 20,
          stiffness: 90,
        });
      }

      if (type === "scale") {
        scale.value = withSpring(1, {
          damping: 15,
          stiffness: 100,
        });
      }
    }, delay);

    return () => clearTimeout(timer);
  }, []);

  const animatedStyle = useAnimatedStyle(() => {
    const baseStyle: any = {
      opacity: opacity.value,
    };

    if (type === "slide" || type === "fadeSlide") {
      baseStyle.transform = [{ translateY: translateY.value }];
    }

    if (type === "scale") {
      baseStyle.transform = [{ scale: scale.value }];
    }

    return baseStyle;
  });

  return (
    <Animated.View style={[styles.container, animatedStyle]}>
      {children}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
