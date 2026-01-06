/**
 * Tela de Termos de Uso e Políticas (QT-06)
 * 
 * Apresenta e registra aceite de:
 * - Termos de Uso
 * - Política de Privacidade
 * - Política de Risco
 */

import { useState } from "react";
import { ScrollView, Text, View, TouchableOpacity, Alert, Linking } from "react-native";
import { router } from "expo-router";
import { ScreenContainer } from "@/components/screen-container";
import { Button } from "@/components/ui/button";
import { useLocalAuth } from "@/lib/auth-context";
import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

// Documentos legais
const LEGAL_DOCUMENTS = [
  {
    id: "terms",
    title: "Termos de Uso",
    icon: "📋",
    summary: "Regras de uso da plataforma, responsabilidades do usuário e da Quantum Trades, propriedade intelectual e limitações de uso.",
    required: true,
  },
  {
    id: "privacy",
    title: "Política de Privacidade",
    icon: "🔒",
    summary: "Como coletamos, usamos e protegemos seus dados pessoais em conformidade com a LGPD.",
    required: true,
  },
  {
    id: "risk",
    title: "Política de Risco",
    icon: "⚠️",
    summary: "Declaração de riscos associados a investimentos, trading automatizado e mercado financeiro.",
    required: true,
  },
];

// Conteúdo resumido dos termos (em produção, seria carregado de uma API)
const TERMS_CONTENT = {
  terms: `
TERMOS DE USO - QUANTUM TRADES

1. ACEITAÇÃO DOS TERMOS
Ao utilizar a plataforma Quantum Trades, você concorda com estes Termos de Uso. Se não concordar, não utilize nossos serviços.

2. DESCRIÇÃO DO SERVIÇO
A Quantum Trades é uma plataforma de trading automatizado que utiliza inteligência artificial para análise de mercado e execução de operações em nome do usuário.

3. RESPONSABILIDADES DO USUÁRIO
- Fornecer informações verdadeiras e atualizadas
- Manter a segurança de suas credenciais de acesso
- Não utilizar a plataforma para atividades ilegais
- Compreender os riscos associados a investimentos

4. LIMITAÇÕES DE RESPONSABILIDADE
A Quantum Trades não garante resultados financeiros. Investimentos envolvem riscos e perdas podem ocorrer.

5. PROPRIEDADE INTELECTUAL
Todo o conteúdo, algoritmos e tecnologia da plataforma são propriedade da Quantum Trades.

6. MODIFICAÇÕES
Reservamo-nos o direito de modificar estes termos a qualquer momento, com notificação prévia aos usuários.
  `,
  privacy: `
POLÍTICA DE PRIVACIDADE - QUANTUM TRADES

1. DADOS COLETADOS
Coletamos dados pessoais (nome, CPF, e-mail, telefone), dados financeiros (corretoras vinculadas, operações) e dados de uso da plataforma.

2. USO DOS DADOS
Utilizamos seus dados para:
- Fornecer e melhorar nossos serviços
- Executar operações em seu nome
- Enviar comunicações relevantes
- Cumprir obrigações legais

3. COMPARTILHAMENTO
Seus dados podem ser compartilhados com:
- Corretoras vinculadas (para execução de ordens)
- Autoridades regulatórias (quando exigido por lei)
- Prestadores de serviço (sob contrato de confidencialidade)

4. SEGURANÇA
Implementamos medidas técnicas e organizacionais para proteger seus dados, incluindo criptografia e controle de acesso.

5. SEUS DIREITOS (LGPD)
Você tem direito a: acessar, corrigir, excluir seus dados, revogar consentimento e solicitar portabilidade.

6. CONTATO
Para questões sobre privacidade: privacidade@quantumtrades.com.br
  `,
  risk: `
POLÍTICA DE RISCO - QUANTUM TRADES

AVISO IMPORTANTE: LEIA COM ATENÇÃO

1. RISCOS DE INVESTIMENTO
Investimentos em renda variável, opções e criptomoedas envolvem riscos significativos. Você pode perder parte ou todo o capital investido.

2. TRADING AUTOMATIZADO
Sistemas automatizados, incluindo os baseados em IA, não garantem lucros. Decisões passadas não garantem resultados futuros.

3. VOLATILIDADE DE MERCADO
Mercados financeiros são voláteis. Eventos imprevisíveis podem causar perdas significativas em curtos períodos.

4. LIMITAÇÕES DA IA
Nossa IA analisa dados históricos e padrões, mas não pode prever eventos futuros com certeza.

5. RESPONSABILIDADE DO USUÁRIO
Ao utilizar a plataforma, você:
- Reconhece os riscos envolvidos
- Investe apenas capital que pode perder
- Não responsabiliza a Quantum Trades por perdas financeiras

6. CIRCUIT BREAKERS
A plataforma possui mecanismos de proteção (stop loss, circuit breakers) que são OBRIGATÓRIOS e não podem ser desativados.

DECLARO QUE LI E COMPREENDI OS RISCOS ACIMA.
  `,
};

export default function TermsScreen() {
  const { updateProfile } = useLocalAuth();
  const [acceptedDocs, setAcceptedDocs] = useState<Record<string, boolean>>({
    terms: false,
    privacy: false,
    risk: false,
  });
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const allAccepted = Object.values(acceptedDocs).every(Boolean);

  const toggleAccept = (docId: string) => {
    if (Platform.OS !== "web") {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    setAcceptedDocs((prev) => ({
      ...prev,
      [docId]: !prev[docId],
    }));
  };

  const toggleExpand = (docId: string) => {
    setExpandedDoc(expandedDoc === docId ? null : docId);
  };

  const handleContinue = async () => {
    if (!allAccepted) {
      Alert.alert("Atenção", "Você precisa aceitar todos os documentos para continuar.");
      return;
    }

    setLoading(true);
    try {
      // Salvar aceite dos termos no perfil
      await updateProfile({
        termsAccepted: true,
        privacyAccepted: true,
        riskPolicyAccepted: true,
      });

      if (Platform.OS !== "web") {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }

      // Navegar para seleção de planos
      router.push("/(onboarding)/plans" as any);
    } catch (error) {
      Alert.alert("Erro", "Não foi possível salvar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenContainer className="p-6">
      <ScrollView 
        contentContainerStyle={{ flexGrow: 1, paddingBottom: 100 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View className="mb-6">
          <Text className="text-2xl font-bold text-foreground">
            Termos e Políticas
          </Text>
          <Text className="text-sm text-muted mt-1">
            Leia e aceite os documentos abaixo para continuar
          </Text>
        </View>

        {/* Documentos */}
        <View className="gap-4">
          {LEGAL_DOCUMENTS.map((doc) => (
            <View 
              key={doc.id}
              className="bg-surface rounded-xl border border-border overflow-hidden"
            >
              {/* Header do documento */}
              <TouchableOpacity
                onPress={() => toggleExpand(doc.id)}
                className="p-4 flex-row items-center"
              >
                <Text style={{ fontSize: 32 }} className="mr-3">
                  {doc.icon}
                </Text>
                <View className="flex-1">
                  <View className="flex-row items-center">
                    <Text className="text-lg font-semibold text-foreground">
                      {doc.title}
                    </Text>
                    {doc.required && (
                      <View className="ml-2 px-2 py-0.5 bg-error/20 rounded">
                        <Text className="text-xs text-error">Obrigatório</Text>
                      </View>
                    )}
                  </View>
                  <Text className="text-xs text-muted mt-1" numberOfLines={2}>
                    {doc.summary}
                  </Text>
                </View>
                <Text className="text-muted text-xl">
                  {expandedDoc === doc.id ? "▲" : "▼"}
                </Text>
              </TouchableOpacity>

              {/* Conteúdo expandido */}
              {expandedDoc === doc.id && (
                <View className="px-4 pb-4">
                  <View className="bg-background rounded-lg p-4 max-h-64">
                    <ScrollView nestedScrollEnabled>
                      <Text className="text-sm text-muted leading-5">
                        {TERMS_CONTENT[doc.id as keyof typeof TERMS_CONTENT]}
                      </Text>
                    </ScrollView>
                  </View>
                </View>
              )}

              {/* Checkbox de aceite */}
              <TouchableOpacity
                onPress={() => toggleAccept(doc.id)}
                className="px-4 py-3 border-t border-border flex-row items-center"
              >
                <View 
                  className={`w-6 h-6 rounded border-2 items-center justify-center mr-3 ${
                    acceptedDocs[doc.id] 
                      ? "bg-primary border-primary" 
                      : "border-muted"
                  }`}
                >
                  {acceptedDocs[doc.id] && (
                    <Text className="text-background font-bold">✓</Text>
                  )}
                </View>
                <Text className="text-sm text-foreground flex-1">
                  Li e aceito {doc.title === "Termos de Uso" ? "os" : "a"} {doc.title}
                </Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>

        {/* Aceitar todos */}
        <TouchableOpacity
          onPress={() => {
            const newState = !allAccepted;
            setAcceptedDocs({
              terms: newState,
              privacy: newState,
              risk: newState,
            });
            if (Platform.OS !== "web") {
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
            }
          }}
          className="mt-6 py-3 flex-row items-center justify-center"
        >
          <View 
            className={`w-6 h-6 rounded border-2 items-center justify-center mr-3 ${
              allAccepted 
                ? "bg-primary border-primary" 
                : "border-muted"
            }`}
          >
            {allAccepted && (
              <Text className="text-background font-bold">✓</Text>
            )}
          </View>
          <Text className="text-primary font-semibold">
            Aceitar todos os documentos
          </Text>
        </TouchableOpacity>

        {/* Aviso legal */}
        <View className="mt-6 p-4 bg-warning/10 rounded-xl border border-warning/30">
          <Text className="text-sm text-warning font-semibold mb-1">
            ⚠️ Aviso Importante
          </Text>
          <Text className="text-xs text-muted leading-4">
            Ao aceitar, você declara ter lido e compreendido todos os documentos, incluindo os riscos associados a investimentos e trading automatizado.
          </Text>
        </View>
      </ScrollView>

      {/* Botão fixo */}
      <View className="absolute bottom-0 left-0 right-0 p-6 bg-background border-t border-border">
        <Button
          onPress={handleContinue}
          variant="primary"
          disabled={!allAccepted}
          loading={loading}
        >
          Continuar
        </Button>
      </View>
    </ScreenContainer>
  );
}
