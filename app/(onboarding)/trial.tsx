/**
 * Tela de Modo Trial (QT-08)
 * 
 * Apresenta:
 * - Timer do período de teste
 * - Funcionalidades disponíveis
 * - Incentivo para contratação
 */

import { useState, useEffect } from "react";
import { ScrollView, Text, View, TouchableOpacity, Alert } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { useLocalAuth } from "@/lib/auth-context";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Duração do trial em dias
const TRIAL_DAYS = 7;

// Funcionalidades do trial
const TRIAL_FEATURES = [
  {
    icon: "🤖",
    title: "1 Bot Ativo",
    description: "Crie e teste um bot de trading automatizado",
  },
  {
    icon: "📊",
    title: "Dashboard Completo",
    description: "Visualize seu portfólio e operações em tempo real",
  },
  {
    icon: "🎯",
    title: "Estratégias Básicas",
    description: "Acesso às estratégias IFR2 e Cruzamento de Médias",
  },
  {
    icon: "📱",
    title: "Alertas no App",
    description: "Receba notificações sobre suas operações",
  },
  {
    icon: "🔒",
    title: "Modo Simulação",
    description: "Opere sem risco real durante o período de teste",
  },
  {
    icon: "📈",
    title: "Backtesting",
    description: "Teste suas estratégias com dados históricos",
  },
];

export default function TrialScreen() {
  const { updateProfile, user } = useLocalAuth();
  const [loading, setLoading] = useState(false);
  const [daysRemaining, setDaysRemaining] = useState(TRIAL_DAYS);
  const [hoursRemaining, setHoursRemaining] = useState(0);
  const [minutesRemaining, setMinutesRemaining] = useState(0);

  // Calcular tempo restante do trial
  useEffect(() => {
    const calculateTimeRemaining = () => {
      // Em produção, usaria a data de início do trial do backend
      const trialEndDate = new Date();
      trialEndDate.setDate(trialEndDate.getDate() + TRIAL_DAYS);
      
      const now = new Date();
      const diff = trialEndDate.getTime() - now.getTime();
      
      if (diff > 0) {
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        setDaysRemaining(days);
        setHoursRemaining(hours);
        setMinutesRemaining(minutes);
      }
    };

    calculateTimeRemaining();
    const interval = setInterval(calculateTimeRemaining, 60000); // Atualiza a cada minuto

    return () => clearInterval(interval);
  }, []);

  const handleStartTrial = async () => {
    setLoading(true);
    try {
      // Salvar início do trial
      await updateProfile({
        subscriptionStatus: "trial",
        trialStartDate: new Date().toISOString(),
        trialEndDate: new Date(Date.now() + TRIAL_DAYS * 24 * 60 * 60 * 1000).toISOString(),
        onboardingCompleted: true,
      });

      if (Platform.OS !== "web") {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      // Navegar para o dashboard principal
      router.replace("/(tabs)" as any);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível iniciar o trial. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    router.push("/(onboarding)/plans" as any);
  };

  return (
    <ScreenContainer className="p-6">
      <ScrollView 
        contentContainerStyle={{ flexGrow: 1, paddingBottom: 120 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Logo */}
        <View className="items-center mb-6">
          <Logo size="md" />
        </View>

        {/* Header */}
        <View className="items-center mb-6">
          <Text className="text-3xl font-bold text-foreground text-center">
            Bem-vindo ao Trial!
          </Text>
          <Text className="text-base text-muted text-center mt-2">
            Experimente todas as funcionalidades por {TRIAL_DAYS} dias grátis
          </Text>
        </View>

        {/* Timer Card */}
        <View className="bg-surface rounded-2xl p-6 border border-border mb-6">
          <Text className="text-sm text-muted text-center mb-4">
            Seu período de teste expira em:
          </Text>
          
          <View className="flex-row justify-center items-center gap-4">
            {/* Dias */}
            <View className="items-center">
              <View className="bg-primary/20 rounded-xl px-4 py-3 min-w-[70px]">
                <Text className="text-3xl font-bold text-primary text-center">
                  {daysRemaining}
                </Text>
              </View>
              <Text className="text-xs text-muted mt-1">dias</Text>
            </View>

            <Text className="text-2xl text-muted">:</Text>

            {/* Horas */}
            <View className="items-center">
              <View className="bg-surface border border-border rounded-xl px-4 py-3 min-w-[70px]">
                <Text className="text-3xl font-bold text-foreground text-center">
                  {hoursRemaining.toString().padStart(2, "0")}
                </Text>
              </View>
              <Text className="text-xs text-muted mt-1">horas</Text>
            </View>

            <Text className="text-2xl text-muted">:</Text>

            {/* Minutos */}
            <View className="items-center">
              <View className="bg-surface border border-border rounded-xl px-4 py-3 min-w-[70px]">
                <Text className="text-3xl font-bold text-foreground text-center">
                  {minutesRemaining.toString().padStart(2, "0")}
                </Text>
              </View>
              <Text className="text-xs text-muted mt-1">min</Text>
            </View>
          </View>
        </View>

        {/* Funcionalidades incluídas */}
        <View className="mb-6">
          <Text className="text-lg font-bold text-foreground mb-4">
            O que está incluído no Trial:
          </Text>
          
          <View className="gap-3">
            {TRIAL_FEATURES.map((feature, index) => (
              <View 
                key={index}
                className="bg-surface rounded-xl p-4 border border-border flex-row items-center"
              >
                <Text style={{ fontSize: 28 }} className="mr-4">
                  {feature.icon}
                </Text>
                <View className="flex-1">
                  <Text className="text-base font-semibold text-foreground">
                    {feature.title}
                  </Text>
                  <Text className="text-sm text-muted">
                    {feature.description}
                  </Text>
                </View>
                <Text className="text-success text-lg">✓</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Banner de upgrade */}
        <TouchableOpacity
          onPress={handleUpgrade}
          className="bg-primary/10 border border-primary/30 rounded-xl p-4 mb-6"
        >
          <View className="flex-row items-center">
            <Text style={{ fontSize: 28 }} className="mr-3">⭐</Text>
            <View className="flex-1">
              <Text className="text-primary font-bold text-base">
                Desbloqueie todo o potencial
              </Text>
              <Text className="text-muted text-xs mt-0.5">
                Assine agora e ganhe 20% de desconto no primeiro mês
              </Text>
            </View>
            <Text className="text-primary">→</Text>
          </View>
        </TouchableOpacity>

        {/* Aviso */}
        <View className="p-4 bg-surface rounded-xl border border-border">
          <Text className="text-xs text-muted text-center leading-4">
            🔒 Durante o trial, todas as operações são simuladas. 
            Nenhum valor real será movimentado. Você pode cancelar a qualquer momento.
          </Text>
        </View>
      </ScrollView>

      {/* Botão fixo */}
      <View className="absolute bottom-0 left-0 right-0 p-6 bg-background border-t border-border">
        <Button
          onPress={handleStartTrial}
          variant="primary"
          loading={loading}
        >
          Começar Meu Trial Grátis
        </Button>
        <Text className="text-xs text-muted text-center mt-3">
          Sem cartão de crédito necessário
        </Text>
      </View>
    </ScreenContainer>
  );
}
