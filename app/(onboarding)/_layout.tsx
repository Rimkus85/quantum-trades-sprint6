/**
 * Layout para rotas de onboarding
 * Fluxo: Perfil de Risco → Termos de Uso → Planos → Trial
 */

import { Stack } from "expo-router";
import { useColors } from "@/hooks/use-colors";

export default function OnboardingLayout() {
  const colors = useColors();

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="risk-profile" />
      <Stack.Screen name="terms" />
      <Stack.Screen name="plans" />
      <Stack.Screen name="trial" />
    </Stack>
  );
}
