/**
 * Componente de Transição Slide
 * Simula transições de slides de apresentação com drilldown ao clicar
 */

import React, { useEffect } from "react";
import { StyleSheet, Dimensions } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSpring,
  Easing,
  runOnJS,
} from "react-native-reanimated";

interface SlideTransitionProps {
  children: React.ReactNode;
  direction?: "left" | "right" | "up" | "down";
  duration?: number;
  delay?: number;
  onComplete?: () => void;
}

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get("window");

export function SlideTransition({
  children,
  direction = "right",
  duration = 400,
  delay = 0,
  onComplete,
}: SlideTransitionProps) {
  const opacity = useSharedValue(0);
  const translateX = useSharedValue(
    direction === "left" ? -SCREEN_WIDTH * 0.3 : direction === "right" ? SCREEN_WIDTH * 0.3 : 0
  );
  const translateY = useSharedValue(
    direction === "up" ? -SCREEN_HEIGHT * 0.1 : direction === "down" ? SCREEN_HEIGHT * 0.1 : 0
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      opacity.value = withTiming(
        1,
        {
          duration,
          easing: Easing.bezier(0.4, 0.0, 0.2, 1),
        },
        (finished) => {
          if (finished && onComplete) {
            runOnJS(onComplete)();
          }
        }
      );

      if (direction === "left" || direction === "right") {
        translateX.value = withSpring(0, {
          damping: 20,
          stiffness: 90,
          mass: 0.8,
        });
      }

      if (direction === "up" || direction === "down") {
        translateY.value = withSpring(0, {
          damping: 20,
          stiffness: 90,
          mass: 0.8,
        });
      }
    }, delay);

    return () => clearTimeout(timer);
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateX: translateX.value }, { translateY: translateY.value }],
  }));

  return <Animated.View style={[styles.container, animatedStyle]}>{children}</Animated.View>;
}

/**
 * Componente de Drilldown Card
 * Card com animação de zoom e slide ao clicar
 */
interface DrilldownCardProps {
  children: React.ReactNode;
  onPress?: () => void;
  delay?: number;
  style?: any;
}

export function DrilldownCard({ children, onPress, delay = 0, style }: DrilldownCardProps) {
  const opacity = useSharedValue(0);
  const scale = useSharedValue(0.9);
  const translateY = useSharedValue(20);
  const pressScale = useSharedValue(1);

  useEffect(() => {
    const timer = setTimeout(() => {
      opacity.value = withTiming(1, {
        duration: 350,
        easing: Easing.out(Easing.cubic),
      });

      scale.value = withSpring(1, {
        damping: 18,
        stiffness: 100,
      });

      translateY.value = withSpring(0, {
        damping: 18,
        stiffness: 100,
      });
    }, delay);

    return () => clearTimeout(timer);
  }, [delay]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [
      { scale: scale.value * pressScale.value },
      { translateY: translateY.value },
    ],
  }));

  const handlePressIn = () => {
    pressScale.value = withSpring(0.96, {
      damping: 15,
      stiffness: 300,
    });
  };

  const handlePressOut = () => {
    pressScale.value = withSpring(1, {
      damping: 15,
      stiffness: 300,
    });
  };

  return (
    <Animated.View style={[styles.container, animatedStyle, style]}>
      {onPress ? (
        <Animated.View
          onTouchStart={handlePressIn}
          onTouchEnd={handlePressOut}
          onTouchCancel={handlePressOut}
        >
          {children}
        </Animated.View>
      ) : (
        children
      )}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
  },
});
