/**
 * Validadores para dados financeiros brasileiros
 * Quantum Trades - Sistema de Trading Multi-Corretora
 */

// Lista de corretoras conhecidas/válidas no Brasil
export const KNOWN_BROKERS = [
  // Corretoras de Valores
  { name: "XP Investimentos", cnpj: "02.332.886/0001-04" },
  { name: "BTG Pactual", cnpj: "30.306.294/0001-45" },
  { name: "Clear Corretora", cnpj: "02.332.886/0011-78" },
  { name: "Rico Investimentos", cnpj: "02.332.886/0001-04" },
  { name: "Inter Invest", cnpj: "18.945.670/0001-46" },
  { name: "Nubank Investimentos", cnpj: "30.680.829/0001-43" },
  { name: "Modal Mais", cnpj: "05.389.174/0001-01" },
  { name: "Genial Investimentos", cnpj: "27.652.684/0001-62" },
  { name: "Ágora Investimentos", cnpj: "74.014.747/0001-35" },
  { name: "Guide Investimentos", cnpj: "65.913.436/0001-17" },
  { name: "Órama", cnpj: "13.293.225/0001-25" },
  { name: "Warren", cnpj: "92.875.780/0001-31" },
  { name: "Easynvest", cnpj: "62.169.875/0001-79" },
  { name: "Toro Investimentos", cnpj: "29.162.769/0001-98" },
  { name: "Mirae Asset", cnpj: "12.392.983/0001-38" },
  { name: "Terra Investimentos", cnpj: "03.751.794/0001-13" },
  { name: "Necton", cnpj: "52.904.364/0001-08" },
  { name: "CM Capital", cnpj: "02.671.743/0001-19" },
  { name: "Ativa Investimentos", cnpj: "33.775.974/0001-04" },
  { name: "Nova Futura", cnpj: "04.257.795/0001-79" },
  // Exchanges de Criptomoedas
  { name: "Binance", cnpj: null },
  { name: "Mercado Bitcoin", cnpj: "18.213.434/0001-35" },
  { name: "Foxbit", cnpj: "18.977.608/0001-90" },
  { name: "NovaDAX", cnpj: "28.883.293/0001-00" },
  { name: "Coinbase", cnpj: null },
  { name: "Kraken", cnpj: null },
  { name: "Bybit", cnpj: null },
  { name: "OKX", cnpj: null },
  { name: "Bitget", cnpj: null },
  { name: "KuCoin", cnpj: null },
  { name: "Gate.io", cnpj: null },
  { name: "Crypto.com", cnpj: null },
  { name: "Bitstamp", cnpj: null },
  { name: "Gemini", cnpj: null },
  { name: "BitcoinTrade", cnpj: "21.830.817/0001-10" },
  { name: "Bitso", cnpj: null },
  { name: "Ripio", cnpj: null },
];

// CPFs com sequências repetidas que são matematicamente válidos mas não existem
const INVALID_CPF_SEQUENCES = [
  "00000000000",
  "11111111111",
  "22222222222",
  "33333333333",
  "44444444444",
  "55555555555",
  "66666666666",
  "77777777777",
  "88888888888",
  "99999999999",
];

/**
 * Valida CPF usando o algoritmo oficial de módulo 11
 * @param cpf - CPF com ou sem formatação (000.000.000-00 ou 00000000000)
 * @returns Objeto com resultado da validação
 */
export function validateCPF(cpf: string): { valid: boolean; error?: string } {
  // Remove formatação
  const cleanCPF = cpf.replace(/\D/g, "");

  // Verifica se tem 11 dígitos
  if (cleanCPF.length !== 11) {
    return { valid: false, error: "CPF deve ter 11 dígitos" };
  }

  // Verifica sequências inválidas
  if (INVALID_CPF_SEQUENCES.includes(cleanCPF)) {
    return { valid: false, error: "CPF inválido (sequência não permitida)" };
  }

  // Calcula primeiro dígito verificador
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanCPF[i]) * (10 - i);
  }
  let remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;
  
  if (remainder !== parseInt(cleanCPF[9])) {
    return { valid: false, error: "CPF inválido (dígito verificador incorreto)" };
  }

  // Calcula segundo dígito verificador
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleanCPF[i]) * (11 - i);
  }
  remainder = (sum * 10) % 11;
  if (remainder === 10 || remainder === 11) remainder = 0;

  if (remainder !== parseInt(cleanCPF[10])) {
    return { valid: false, error: "CPF inválido (dígito verificador incorreto)" };
  }

  return { valid: true };
}

/**
 * Valida se a corretora existe na lista de corretoras conhecidas
 * @param brokerName - Nome da corretora
 * @returns Objeto com resultado da validação
 */
export function validateBroker(brokerName: string): { valid: boolean; error?: string; suggestion?: string } {
  const normalizedName = brokerName.trim().toLowerCase();
  
  if (!normalizedName) {
    return { valid: false, error: "Nome da corretora é obrigatório" };
  }

  // Busca exata (case insensitive)
  const exactMatch = KNOWN_BROKERS.find(
    b => b.name.toLowerCase() === normalizedName
  );
  
  if (exactMatch) {
    return { valid: true };
  }

  // Busca parcial para sugestão
  const partialMatches = KNOWN_BROKERS.filter(
    b => b.name.toLowerCase().includes(normalizedName) ||
         normalizedName.includes(b.name.toLowerCase())
  );

  if (partialMatches.length > 0) {
    return {
      valid: false,
      error: "Corretora não encontrada",
      suggestion: `Você quis dizer: ${partialMatches[0].name}?`,
    };
  }

  // Busca por similaridade (Levenshtein simplificado)
  const similarBroker = findSimilarBroker(normalizedName);
  if (similarBroker) {
    return {
      valid: false,
      error: "Corretora não encontrada",
      suggestion: `Você quis dizer: ${similarBroker}?`,
    };
  }

  return {
    valid: false,
    error: "Corretora não encontrada. Verifique o nome ou selecione uma da lista.",
  };
}

/**
 * Encontra corretora similar usando distância de Levenshtein simplificada
 */
function findSimilarBroker(input: string): string | null {
  let minDistance = Infinity;
  let closestBroker: string | null = null;

  for (const broker of KNOWN_BROKERS) {
    const distance = levenshteinDistance(input, broker.name.toLowerCase());
    if (distance < minDistance && distance <= 3) {
      minDistance = distance;
      closestBroker = broker.name;
    }
  }

  return closestBroker;
}

/**
 * Calcula distância de Levenshtein entre duas strings
 */
function levenshteinDistance(a: string, b: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Valida formato de e-mail
 */
export function validateEmail(email: string): { valid: boolean; error?: string } {
  const trimmed = email.trim();
  
  if (!trimmed) {
    return { valid: false, error: "E-mail é obrigatório" };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(trimmed)) {
    return { valid: false, error: "Formato de e-mail inválido" };
  }

  // Verifica domínios comuns com erros de digitação
  const domain = trimmed.split("@")[1]?.toLowerCase();
  const commonDomains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"];
  const typos: Record<string, string> = {
    "gmial.com": "gmail.com",
    "gmal.com": "gmail.com",
    "gmail.com.br": "gmail.com",
    "hotmal.com": "hotmail.com",
    "hotmail.com.br": "hotmail.com",
    "outllok.com": "outlook.com",
    "outlok.com": "outlook.com",
  };

  if (typos[domain]) {
    return {
      valid: false,
      error: `Você quis dizer @${typos[domain]}?`,
    };
  }

  return { valid: true };
}

/**
 * Gera código de verificação de 6 dígitos
 */
export function generateVerificationCode(): string {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

/**
 * Formata CPF para exibição
 */
export function formatCPF(cpf: string): string {
  const clean = cpf.replace(/\D/g, "");
  return clean.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
}

/**
 * Lista de corretoras para o dropdown
 */
export function getBrokerOptions(): Array<{ label: string; value: string }> {
  const options = KNOWN_BROKERS.map(b => ({
    label: b.name,
    value: b.name.toLowerCase().replace(/\s+/g, "_"),
  }));
  
  // Adiciona opção "Outra" no final
  options.push({ label: "Outra", value: "other" });
  
  return options;
}
