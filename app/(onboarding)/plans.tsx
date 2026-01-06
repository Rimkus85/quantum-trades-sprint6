/**
 * Tela de Seleção de Planos (QT-07)
 * 
 * Apresenta os planos disponíveis:
 * - Entrada (básico)
 * - Médio (intermediário)
 * - Top (premium)
 * 
 * Integração com pagamento como débito técnico
 */

import { useState } from "react";
import { ScrollView, Text, View, TouchableOpacity, Alert } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { useLocalAuth } from "@/lib/auth-context";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Definição dos planos
interface Plan {
  id: string;
  name: string;
  price: number;
  priceLabel: string;
  description: string;
  features: string[];
  highlighted?: boolean;
  badge?: string;
}

const PLANS: Plan[] = [
  {
    id: "entrada",
    name: "Entrada",
    price: 97,
    priceLabel: "R$ 97/mês",
    description: "Ideal para quem está começando no trading automatizado",
    features: [
      "1 bot ativo simultâneo",
      "Estratégias básicas (IFR2, Médias)",
      "Operações em ações (B3)",
      "Alertas via app",
      "Suporte por e-mail",
      "Limite: R$ 10.000/mês operado",
    ],
  },
  {
    id: "medio",
    name: "Médio",
    price: 197,
    priceLabel: "R$ 197/mês",
    description: "Para traders que buscam diversificação e mais controle",
    features: [
      "3 bots ativos simultâneos",
      "Estratégias intermediárias",
      "Ações + Opções (B3)",
      "Alertas via app e Telegram",
      "Suporte prioritário",
      "Limite: R$ 50.000/mês operado",
      "Backtesting básico",
    ],
    highlighted: true,
    badge: "Mais Popular",
  },
  {
    id: "top",
    name: "Top",
    price: 397,
    priceLabel: "R$ 397/mês",
    description: "Máximo poder para traders profissionais",
    features: [
      "Bots ilimitados",
      "Todas as estratégias + IA avançada",
      "Ações + Opções + Cripto",
      "Alertas multicanal personalizados",
      "Suporte VIP com gerente dedicado",
      "Sem limite de operações",
      "Backtesting avançado",
      "API para integrações",
      "Relatórios fiscais automáticos",
    ],
    badge: "Premium",
  },
];

export default function PlansScreen() {
  const { updateProfile } = useLocalAuth();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSelectPlan = (planId: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setSelectedPlan(planId);
  };

  const handleSubscribe = async () => {
    if (!selectedPlan) {
      Alert.alert("Atenção", "Selecione um plano para continuar.");
      return;
    }

    setLoading(true);
    try {
      // TODO: Integrar com gateway de pagamento (Stripe, PagSeguro, etc.)
      // Por enquanto, apenas salva o plano selecionado e inicia trial
      
      await updateProfile({
        selectedPlan: selectedPlan,
        subscriptionStatus: "trial",
        trialStartDate: new Date().toISOString(),
      });

      if (Platform.OS !== "web") {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      // Navegar para tela de trial
      router.push("/(onboarding)/trial" as any);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível processar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleStartTrial = () => {
    // Iniciar trial sem selecionar plano específico
    router.push("/(onboarding)/trial" as any);
  };

  return (
    <ScreenContainer className="p-6">
      <ScrollView 
        contentContainerStyle={{ flexGrow: 1, paddingBottom: 120 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mb-6">
          <Text className="text-2xl font-bold text-foreground">
            Escolha seu Plano
          </Text>
          <Text className="text-sm text-muted mt-1">
            Selecione o plano ideal para seus objetivos
          </Text>
        </View>

        {/* Trial Banner */}
        <TouchableOpacity
          onPress={handleStartTrial}
          className="bg-primary/10 border border-primary/30 rounded-xl p-4 mb-6"
        >
          <View className="flex-row items-center">
            <Text style={{ fontSize: 28 }} className="mr-3">🎁</Text>
            <View className="flex-1">
              <Text className="text-primary font-bold text-base">
                Experimente Grátis por 7 Dias
              </Text>
              <Text className="text-muted text-xs mt-0.5">
                Teste todas as funcionalidades sem compromisso
              </Text>
            </View>
            <Text className="text-primary">→</Text>
          </View>
        </TouchableOpacity>

        {/* Planos */}
        <View className="gap-4">
          {PLANS.map((plan) => (
            <TouchableOpacity
              key={plan.id}
              onPress={() => handleSelectPlan(plan.id)}
              className={`rounded-xl border-2 overflow-hidden ${
                selectedPlan === plan.id
                  ? "border-primary"
                  : plan.highlighted
                  ? "border-primary/50"
                  : "border-border"
              }`}
            >
              {/* Badge */}
              {plan.badge && (
                <View 
                  className={`py-1 px-3 ${
                    plan.highlighted ? "bg-primary" : "bg-surface"
                  }`}
                >
                  <Text 
                    className={`text-xs font-bold text-center ${
                      plan.highlighted ? "text-background" : "text-muted"
                    }`}
                  >
                    {plan.badge}
                  </Text>
                </View>
              )}

              <View className="p-4 bg-surface">
                {/* Header do plano */}
                <View className="flex-row items-center justify-between mb-2">
                  <View className="flex-row items-center">
                    {/* Radio button */}
                    <View 
                      className={`w-6 h-6 rounded-full border-2 items-center justify-center mr-3 ${
                        selectedPlan === plan.id
                          ? "border-primary bg-primary"
                          : "border-muted"
                      }`}
                    >
                      {selectedPlan === plan.id && (
                        <View className="w-2.5 h-2.5 rounded-full bg-background" />
                      )}
                    </View>
                    <Text className="text-xl font-bold text-foreground">
                      {plan.name}
                    </Text>
                  </View>
                  <Text className="text-xl font-bold text-primary">
                    {plan.priceLabel}
                  </Text>
                </View>

                {/* Descrição */}
                <Text className="text-sm text-muted mb-3">
                  {plan.description}
                </Text>

                {/* Features */}
                <View className="gap-2">
                  {plan.features.map((feature, index) => (
                    <View key={index} className="flex-row items-start">
                      <Text className="text-success mr-2">✓</Text>
                      <Text className="text-sm text-foreground flex-1">
                        {feature}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Garantia */}
        <View className="mt-6 p-4 bg-surface rounded-xl border border-border">
          <View className="flex-row items-center">
            <Text style={{ fontSize: 24 }} className="mr-3">🛡️</Text>
            <View className="flex-1">
              <Text className="text-sm font-semibold text-foreground">
                Garantia de 7 dias
              </Text>
              <Text className="text-xs text-muted">
                Não ficou satisfeito? Devolvemos 100% do valor.
              </Text>
            </View>
          </View>
        </View>

        {/* Aviso de pagamento */}
        <View className="mt-4 p-3 bg-warning/10 rounded-lg border border-warning/30">
          <Text className="text-xs text-muted text-center">
            💳 Pagamento processado de forma segura via cartão de crédito.
            Cancele a qualquer momento.
          </Text>
        </View>
      </ScrollView>

      {/* Botões fixos */}
      <View className="absolute bottom-0 left-0 right-0 p-6 bg-background border-t border-border">
        <Button
          onPress={handleSubscribe}
          variant="primary"
          disabled={!selectedPlan}
          loading={loading}
        >
          {selectedPlan 
            ? `Assinar ${PLANS.find(p => p.id === selectedPlan)?.name}`
            : "Selecione um plano"
          }
        </Button>
        <TouchableOpacity
          onPress={handleStartTrial}
          className="mt-3 py-2"
        >
          <Text className="text-primary text-center text-sm">
            Começar período de teste gratuito
          </Text>
        </TouchableOpacity>
      </View>
    </ScreenContainer>
  );
}
