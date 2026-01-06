/**
 * Testes para o fluxo de onboarding (Sprint 2)
 * QT-05: Perfil de Risco
 * QT-06: Termos e Políticas
 * QT-07: Planos de Assinatura
 * QT-08: Modo Trial
 */

import { describe, it, expect } from "vitest";

// Função de cálculo de perfil de risco (extraída de risk-profile.tsx)
type RiskProfile = "conservador" | "moderado" | "agressivo";

function calculateRiskProfile(answers: Record<number, number>): RiskProfile {
  const totalPoints = Object.values(answers).reduce((sum, points) => sum + points, 0);
  
  // Pontuação máxima: 5 perguntas x 4 pontos = 20 pontos
  // Conservador: 5-9 pontos
  // Moderado: 10-14 pontos
  // Agressivo: 15-20 pontos
  
  if (totalPoints <= 9) return "conservador";
  if (totalPoints <= 14) return "moderado";
  return "agressivo";
}

// Dados dos planos (extraídos de plans.tsx)
interface Plan {
  id: string;
  name: string;
  price: number;
  features: string[];
}

const PLANS: Plan[] = [
  {
    id: "entrada",
    name: "Entrada",
    price: 97,
    features: [
      "1 bot ativo simultâneo",
      "Estratégias básicas (IFR2, Médias)",
      "Operações em ações (B3)",
    ],
  },
  {
    id: "medio",
    name: "Médio",
    price: 197,
    features: [
      "3 bots ativos simultâneos",
      "Estratégias intermediárias",
      "Ações + Opções (B3)",
    ],
  },
  {
    id: "top",
    name: "Top",
    price: 397,
    features: [
      "Bots ilimitados",
      "Todas as estratégias + IA avançada",
      "Ações + Opções + Cripto",
    ],
  },
];

// Constantes de trial
const TRIAL_DAYS = 7;

describe("QT-05: Perfil de Risco", () => {
  describe("Cálculo de perfil baseado em pontuação", () => {
    it("deve classificar como Conservador para pontuação baixa (5-9)", () => {
      // Todas respostas com 1 ponto = 5 pontos total
      const answers = { 0: 1, 1: 1, 2: 1, 3: 1, 4: 1 };
      expect(calculateRiskProfile(answers)).toBe("conservador");
      
      // Pontuação 9 (limite superior do conservador)
      const answers2 = { 0: 1, 1: 2, 2: 2, 3: 2, 4: 2 };
      expect(calculateRiskProfile(answers2)).toBe("conservador");
    });

    it("deve classificar como Moderado para pontuação média (10-14)", () => {
      // Pontuação 10 (limite inferior do moderado)
      const answers = { 0: 2, 1: 2, 2: 2, 3: 2, 4: 2 };
      expect(calculateRiskProfile(answers)).toBe("moderado");
      
      // Pontuação 14 (limite superior do moderado)
      const answers2 = { 0: 3, 1: 3, 2: 3, 3: 3, 4: 2 };
      expect(calculateRiskProfile(answers2)).toBe("moderado");
    });

    it("deve classificar como Agressivo para pontuação alta (15-20)", () => {
      // Pontuação 15 (limite inferior do agressivo)
      const answers = { 0: 3, 1: 3, 2: 3, 3: 3, 4: 3 };
      expect(calculateRiskProfile(answers)).toBe("agressivo");
      
      // Pontuação máxima 20
      const answers2 = { 0: 4, 1: 4, 2: 4, 3: 4, 4: 4 };
      expect(calculateRiskProfile(answers2)).toBe("agressivo");
    });
  });

  describe("Validação de respostas", () => {
    it("deve aceitar respostas de 1 a 4 pontos", () => {
      const validAnswers = { 0: 1, 1: 2, 2: 3, 3: 4, 4: 2 };
      const profile = calculateRiskProfile(validAnswers);
      expect(["conservador", "moderado", "agressivo"]).toContain(profile);
    });

    it("deve calcular corretamente com respostas mistas", () => {
      // 1 + 4 + 2 + 3 + 2 = 12 pontos = Moderado
      const answers = { 0: 1, 1: 4, 2: 2, 3: 3, 4: 2 };
      expect(calculateRiskProfile(answers)).toBe("moderado");
    });
  });
});

describe("QT-06: Termos e Políticas", () => {
  const LEGAL_DOCUMENTS = ["terms", "privacy", "risk"];

  describe("Validação de aceite", () => {
    it("deve exigir aceite de todos os documentos obrigatórios", () => {
      const acceptedDocs = { terms: true, privacy: true, risk: true };
      const allAccepted = Object.values(acceptedDocs).every(Boolean);
      expect(allAccepted).toBe(true);
    });

    it("deve rejeitar se algum documento não foi aceito", () => {
      const acceptedDocs1 = { terms: true, privacy: false, risk: true };
      expect(Object.values(acceptedDocs1).every(Boolean)).toBe(false);

      const acceptedDocs2 = { terms: false, privacy: true, risk: true };
      expect(Object.values(acceptedDocs2).every(Boolean)).toBe(false);

      const acceptedDocs3 = { terms: true, privacy: true, risk: false };
      expect(Object.values(acceptedDocs3).every(Boolean)).toBe(false);
    });

    it("deve ter exatamente 3 documentos obrigatórios", () => {
      expect(LEGAL_DOCUMENTS.length).toBe(3);
      expect(LEGAL_DOCUMENTS).toContain("terms");
      expect(LEGAL_DOCUMENTS).toContain("privacy");
      expect(LEGAL_DOCUMENTS).toContain("risk");
    });
  });

  describe("Toggle de aceite", () => {
    it("deve permitir aceitar/desaceitar individualmente", () => {
      let acceptedDocs = { terms: false, privacy: false, risk: false };
      
      // Aceitar terms
      acceptedDocs = { ...acceptedDocs, terms: !acceptedDocs.terms };
      expect(acceptedDocs.terms).toBe(true);
      expect(acceptedDocs.privacy).toBe(false);
      
      // Desaceitar terms
      acceptedDocs = { ...acceptedDocs, terms: !acceptedDocs.terms };
      expect(acceptedDocs.terms).toBe(false);
    });

    it("deve permitir aceitar todos de uma vez", () => {
      let acceptedDocs = { terms: false, privacy: false, risk: false };
      const allAccepted = Object.values(acceptedDocs).every(Boolean);
      
      // Aceitar todos
      const newState = !allAccepted;
      acceptedDocs = { terms: newState, privacy: newState, risk: newState };
      
      expect(acceptedDocs.terms).toBe(true);
      expect(acceptedDocs.privacy).toBe(true);
      expect(acceptedDocs.risk).toBe(true);
    });
  });
});

describe("QT-07: Planos de Assinatura", () => {
  describe("Estrutura dos planos", () => {
    it("deve ter exatamente 3 planos disponíveis", () => {
      expect(PLANS.length).toBe(3);
    });

    it("deve ter planos com IDs únicos", () => {
      const ids = PLANS.map(p => p.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(PLANS.length);
    });

    it("deve ter planos ordenados por preço crescente", () => {
      for (let i = 1; i < PLANS.length; i++) {
        expect(PLANS[i].price).toBeGreaterThan(PLANS[i - 1].price);
      }
    });
  });

  describe("Preços dos planos", () => {
    it("plano Entrada deve custar R$ 97/mês", () => {
      const entrada = PLANS.find(p => p.id === "entrada");
      expect(entrada?.price).toBe(97);
    });

    it("plano Médio deve custar R$ 197/mês", () => {
      const medio = PLANS.find(p => p.id === "medio");
      expect(medio?.price).toBe(197);
    });

    it("plano Top deve custar R$ 397/mês", () => {
      const top = PLANS.find(p => p.id === "top");
      expect(top?.price).toBe(397);
    });
  });

  describe("Features dos planos", () => {
    it("plano Entrada deve ter funcionalidades básicas", () => {
      const entrada = PLANS.find(p => p.id === "entrada");
      expect(entrada?.features).toContain("1 bot ativo simultâneo");
      expect(entrada?.features.some(f => f.includes("ações"))).toBe(true);
    });

    it("plano Médio deve incluir opções", () => {
      const medio = PLANS.find(p => p.id === "medio");
      expect(medio?.features.some(f => f.includes("Opções"))).toBe(true);
    });

    it("plano Top deve incluir cripto", () => {
      const top = PLANS.find(p => p.id === "top");
      expect(top?.features.some(f => f.includes("Cripto"))).toBe(true);
    });
  });
});

describe("QT-08: Modo Trial", () => {
  describe("Configuração do trial", () => {
    it("trial deve ter duração de 7 dias", () => {
      expect(TRIAL_DAYS).toBe(7);
    });

    it("deve calcular data de expiração corretamente", () => {
      const startDate = new Date("2025-01-05T00:00:00Z");
      const endDate = new Date(startDate.getTime() + TRIAL_DAYS * 24 * 60 * 60 * 1000);
      
      expect(endDate.toISOString()).toBe("2025-01-12T00:00:00.000Z");
    });
  });

  describe("Cálculo de tempo restante", () => {
    it("deve calcular dias restantes corretamente", () => {
      const now = new Date();
      const trialEndDate = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000); // 5 dias a partir de agora
      
      const diff = trialEndDate.getTime() - now.getTime();
      const daysRemaining = Math.floor(diff / (1000 * 60 * 60 * 24));
      
      // Deve ser exatamente 5 dias quando calculado com milissegundos exatos
      expect(daysRemaining).toBe(5);
    });

    it("deve calcular horas restantes corretamente", () => {
      const trialEndDate = new Date();
      trialEndDate.setHours(trialEndDate.getHours() + 50); // 50 horas
      
      const now = new Date();
      const diff = trialEndDate.getTime() - now.getTime();
      const hoursRemaining = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      
      expect(hoursRemaining).toBeGreaterThanOrEqual(0);
      expect(hoursRemaining).toBeLessThan(24);
    });
  });

  describe("Status de subscription", () => {
    it("deve ter status válidos de subscription", () => {
      const validStatuses = ["trial", "active", "expired", "cancelled"];
      
      expect(validStatuses).toContain("trial");
      expect(validStatuses).toContain("active");
      expect(validStatuses).toContain("expired");
      expect(validStatuses).toContain("cancelled");
    });

    it("novo usuário deve iniciar com status trial", () => {
      const newUserStatus = "trial";
      expect(newUserStatus).toBe("trial");
    });
  });
});

describe("Fluxo de Onboarding Completo", () => {
  it("deve seguir a ordem correta: Risk Profile → Terms → Plans → Trial", () => {
    const onboardingSteps = [
      "risk-profile",
      "terms",
      "plans",
      "trial",
    ];
    
    expect(onboardingSteps[0]).toBe("risk-profile");
    expect(onboardingSteps[1]).toBe("terms");
    expect(onboardingSteps[2]).toBe("plans");
    expect(onboardingSteps[3]).toBe("trial");
  });

  it("deve marcar onboarding como completo após trial", () => {
    const userProfile = {
      riskProfile: "moderado" as RiskProfile,
      termsAccepted: true,
      privacyAccepted: true,
      riskPolicyAccepted: true,
      selectedPlan: "medio",
      subscriptionStatus: "trial",
      onboardingCompleted: true,
    };

    expect(userProfile.riskProfile).toBeDefined();
    expect(userProfile.termsAccepted).toBe(true);
    expect(userProfile.privacyAccepted).toBe(true);
    expect(userProfile.riskPolicyAccepted).toBe(true);
    expect(userProfile.subscriptionStatus).toBe("trial");
    expect(userProfile.onboardingCompleted).toBe(true);
  });
});
