/**
 * Tela de Questionário de Perfil de Risco (QT-05)
 * 
 * Questionário para determinar o perfil de investidor:
 * - Conservador
 * - Moderado
 * - Agressivo
 */

import { useState } from "react";
import { ScrollView, Text, View, TouchableOpacity, Alert } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { useLocalAuth } from "@/lib/auth-context";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Perguntas do questionário de perfil de risco
const QUESTIONS = [
  {
    id: 1,
    question: "Qual é o seu principal objetivo ao investir?",
    options: [
      { text: "Preservar meu capital com segurança", points: 1 },
      { text: "Crescimento moderado com algum risco", points: 2 },
      { text: "Maximizar retornos, aceitando riscos maiores", points: 3 },
    ],
  },
  {
    id: 2,
    question: "Como você reagiria se seus investimentos caíssem 20% em um mês?",
    options: [
      { text: "Venderia tudo para evitar mais perdas", points: 1 },
      { text: "Manteria e aguardaria a recuperação", points: 2 },
      { text: "Compraria mais aproveitando os preços baixos", points: 3 },
    ],
  },
  {
    id: 3,
    question: "Qual é o seu horizonte de investimento?",
    options: [
      { text: "Curto prazo (menos de 1 ano)", points: 1 },
      { text: "Médio prazo (1 a 5 anos)", points: 2 },
      { text: "Longo prazo (mais de 5 anos)", points: 3 },
    ],
  },
  {
    id: 4,
    question: "Qual porcentagem da sua renda você pode investir mensalmente?",
    options: [
      { text: "Até 10%", points: 1 },
      { text: "Entre 10% e 30%", points: 2 },
      { text: "Mais de 30%", points: 3 },
    ],
  },
  {
    id: 5,
    question: "Qual é a sua experiência com investimentos?",
    options: [
      { text: "Iniciante - nunca investi antes", points: 1 },
      { text: "Intermediário - já investi em renda fixa e ações", points: 2 },
      { text: "Avançado - opero derivativos, opções e cripto", points: 3 },
    ],
  },
  {
    id: 6,
    question: "Como você se sente em relação à volatilidade do mercado?",
    options: [
      { text: "Prefiro estabilidade, mesmo com retornos menores", points: 1 },
      { text: "Aceito alguma volatilidade por retornos melhores", points: 2 },
      { text: "Volatilidade é oportunidade de ganho", points: 3 },
    ],
  },
  {
    id: 7,
    question: "Você possui reserva de emergência (6+ meses de despesas)?",
    options: [
      { text: "Não, ainda estou construindo", points: 1 },
      { text: "Sim, tenho uma reserva básica", points: 2 },
      { text: "Sim, tenho reserva sólida e posso arriscar mais", points: 3 },
    ],
  },
];

// Perfis de risco
type RiskProfile = "conservador" | "moderado" | "agressivo";

const PROFILES: Record<RiskProfile, { title: string; description: string; color: string; icon: string }> = {
  conservador: {
    title: "Conservador",
    description: "Você prioriza a segurança do capital. Recomendamos estratégias de baixo risco com foco em preservação patrimonial.",
    color: "#3B82F6", // Azul
    icon: "🛡️",
  },
  moderado: {
    title: "Moderado",
    description: "Você busca equilíbrio entre risco e retorno. Recomendamos uma carteira diversificada com exposição controlada.",
    color: "#FFD700", // Dourado
    icon: "⚖️",
  },
  agressivo: {
    title: "Agressivo",
    description: "Você busca maximizar retornos e aceita riscos maiores. Recomendamos estratégias mais arrojadas com gestão de risco.",
    color: "#EF4444", // Vermelho
    icon: "🚀",
  },
};

function calculateProfile(answers: Record<number, number>): RiskProfile {
  const totalPoints = Object.values(answers).reduce((sum, points) => sum + points, 0);
  const maxPoints = QUESTIONS.length * 3;
  const percentage = (totalPoints / maxPoints) * 100;

  if (percentage <= 40) return "conservador";
  if (percentage <= 70) return "moderado";
  return "agressivo";
}

export default function RiskProfileScreen() {
  const { updateProfile } = useLocalAuth();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [showResult, setShowResult] = useState(false);
  const [profile, setProfile] = useState<RiskProfile | null>(null);

  const handleAnswer = (points: number) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    const newAnswers = { ...answers, [QUESTIONS[currentQuestion].id]: points };
    setAnswers(newAnswers);

    if (currentQuestion < QUESTIONS.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calcular perfil
      const calculatedProfile = calculateProfile(newAnswers);
      setProfile(calculatedProfile);
      setShowResult(true);
    }
  };

  const handleContinue = async () => {
    if (!profile) return;

    try {
      // Salvar perfil de risco no contexto de autenticação
      await updateProfile({ riskProfile: profile });
      
      if (Platform.OS !== "web") {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      // Navegar para a próxima tela (Termos de Uso)
      router.push("/(onboarding)/terms" as any);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível salvar seu perfil. Tente novamente.");
    }
  };

  const handleBack = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const progress = ((currentQuestion + 1) / QUESTIONS.length) * 100;

  // Tela de resultado
  if (showResult && profile) {
    const profileData = PROFILES[profile];

    return (
      <ScreenContainer className="p-6">
        <ScrollView 
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
        >
          <View className="flex-1 justify-center items-center">
            {/* Ícone do perfil */}
            <Text style={{ fontSize: 80 }}>{profileData.icon}</Text>

            {/* Título */}
            <Text className="text-3xl font-bold text-foreground mt-6 text-center">
              Seu Perfil de Investidor
            </Text>

            {/* Badge do perfil */}
            <View 
              className="mt-4 px-6 py-2 rounded-full"
              style={{ backgroundColor: profileData.color }}
            >
              <Text className="text-lg font-bold text-background">
                {profileData.title}
              </Text>
            </View>

            {/* Descrição */}
            <Text className="text-base text-muted text-center mt-6 px-4 leading-6">
              {profileData.description}
            </Text>

            {/* Card informativo */}
            <View className="w-full bg-surface rounded-xl p-4 mt-8 border border-border">
              <Text className="text-sm text-muted text-center">
                Este perfil será usado para personalizar suas estratégias de trading e recomendações de bots. Você pode alterá-lo a qualquer momento nas configurações.
              </Text>
            </View>

            {/* Botão continuar */}
            <View className="w-full mt-8">
              <Button
                onPress={handleContinue}
                variant="primary"
              >
                Continuar
              </Button>
            </View>

            {/* Refazer questionário */}
            <TouchableOpacity
              onPress={() => {
                setShowResult(false);
                setCurrentQuestion(0);
                setAnswers({});
                setProfile(null);
              }}
              className="mt-4"
            >
              <Text className="text-primary text-sm">
                Refazer questionário
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </ScreenContainer>
    );
  }

  // Tela de perguntas
  const question = QUESTIONS[currentQuestion];

  return (
    <ScreenContainer className="p-6">
      <ScrollView 
        contentContainerStyle={{ flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mb-6">
          <Text className="text-2xl font-bold text-foreground">
            Perfil de Risco
          </Text>
          <Text className="text-sm text-muted mt-1">
            Responda às perguntas para identificarmos seu perfil
          </Text>
        </View>

        {/* Barra de progresso */}
        <View className="mb-6">
          <View className="flex-row justify-between mb-2">
            <Text className="text-xs text-muted">
              Pergunta {currentQuestion + 1} de {QUESTIONS.length}
            </Text>
            <Text className="text-xs text-primary font-semibold">
              {Math.round(progress)}%
            </Text>
          </View>
          <View className="h-2 bg-surface rounded-full overflow-hidden">
            <View 
              className="h-full bg-primary rounded-full"
              style={{ width: `${progress}%` }}
            />
          </View>
        </View>

        {/* Pergunta */}
        <View className="flex-1">
          <Text className="text-lg font-semibold text-foreground mb-6">
            {question.question}
          </Text>

          {/* Opções */}
          <View className="gap-3">
            {question.options.map((option, index) => (
              <TouchableOpacity
                key={index}
                onPress={() => handleAnswer(option.points)}
                className="bg-surface border border-border rounded-xl p-4 active:opacity-80"
                
              >
                <View className="flex-row items-center">
                  <View className="w-8 h-8 rounded-full bg-background border border-border items-center justify-center mr-3">
                    <Text className="text-muted font-semibold">
                      {String.fromCharCode(65 + index)}
                    </Text>
                  </View>
                  <Text className="text-foreground flex-1 leading-5">
                    {option.text}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Botão voltar */}
        {currentQuestion > 0 && (
          <TouchableOpacity
            onPress={handleBack}
            className="mt-6 py-3"
          >
            <Text className="text-primary text-center">
              ← Voltar para pergunta anterior
            </Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </ScreenContainer>
  );
}
