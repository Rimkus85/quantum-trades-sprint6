/**
 * Dados mockados para o Dashboard (Sprint 3)
 * Em produção, estes dados virão do backend/API
 */

// Tipos
export interface PortfolioSummary {
  totalValue: number;
  totalChange: number;
  totalChangePercent: number;
  monthlyChange: number;
  monthlyChangePercent: number;
}

export interface AssetClass {
  id: string;
  name: string;
  value: number;
  percentage: number;
  color: string;
  assets: Asset[];
}

export interface Asset {
  ticker: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  change: number;
  changePercent: number;
}

export interface Operation {
  id: string;
  ticker: string;
  type: "compra" | "venda";
  quantity: number;
  price: number;
  total: number;
  date: string;
  status: "executada" | "pendente" | "cancelada";
  changePercent: number;
}

export interface PerformancePoint {
  date: string;
  value: number;
}

// Dados mockados do portfólio
export const MOCK_PORTFOLIO: PortfolioSummary = {
  totalValue: 125430.00,
  totalChange: 2340.50,
  totalChangePercent: 1.9,
  monthlyChange: 965.82,
  monthlyChangePercent: 0.77,
};

// Classes de ativos mockadas
export const MOCK_ASSET_CLASSES: AssetClass[] = [
  {
    id: "acoes",
    name: "Ações",
    value: 68750.00,
    percentage: 54.84,
    color: "#3B82F6", // Azul
    assets: [
      {
        ticker: "PETR4",
        name: "Petrobras PN",
        quantity: 500,
        avgPrice: 32.50,
        currentPrice: 33.25,
        value: 16625.00,
        change: 375.00,
        changePercent: 2.3,
      },
      {
        ticker: "VALE3",
        name: "Vale ON",
        quantity: 300,
        avgPrice: 68.00,
        currentPrice: 69.22,
        value: 20766.00,
        change: 366.00,
        changePercent: 1.8,
      },
      {
        ticker: "ITUB4",
        name: "Itaú Unibanco PN",
        quantity: 400,
        avgPrice: 32.00,
        currentPrice: 31.84,
        value: 12736.00,
        change: -64.00,
        changePercent: -0.5,
      },
      {
        ticker: "BBDC4",
        name: "Bradesco PN",
        quantity: 600,
        avgPrice: 14.50,
        currentPrice: 14.95,
        value: 8970.00,
        change: 270.00,
        changePercent: 3.1,
      },
      {
        ticker: "WEGE3",
        name: "WEG ON",
        quantity: 200,
        avgPrice: 48.00,
        currentPrice: 50.02,
        value: 10004.00,
        change: 404.00,
        changePercent: 4.2,
      },
    ],
  },
  {
    id: "opcoes",
    name: "Opções",
    value: 54560.00,
    percentage: 43.51,
    color: "#60A5FA", // Azul claro
    assets: [
      {
        ticker: "PETRK325",
        name: "Call PETR4 K32.5",
        quantity: 1000,
        avgPrice: 2.50,
        currentPrice: 2.85,
        value: 2850.00,
        change: 350.00,
        changePercent: 14.0,
      },
      {
        ticker: "VALEM680",
        name: "Call VALE3 M68",
        quantity: 500,
        avgPrice: 4.20,
        currentPrice: 4.55,
        value: 2275.00,
        change: 175.00,
        changePercent: 8.3,
      },
    ],
  },
  {
    id: "cripto",
    name: "Cripto",
    value: 2120.00,
    percentage: 1.65,
    color: "#1E40AF", // Azul escuro
    assets: [
      {
        ticker: "BTC",
        name: "Bitcoin",
        quantity: 0.015,
        avgPrice: 95000.00,
        currentPrice: 98500.00,
        value: 1477.50,
        change: 52.50,
        changePercent: 3.7,
      },
      {
        ticker: "ETH",
        name: "Ethereum",
        quantity: 0.25,
        avgPrice: 2400.00,
        currentPrice: 2570.00,
        value: 642.50,
        change: 42.50,
        changePercent: 7.1,
      },
    ],
  },
];

// Operações recentes mockadas
export const MOCK_OPERATIONS: Operation[] = [
  {
    id: "op1",
    ticker: "PETR4",
    type: "compra",
    quantity: 100,
    price: 33.25,
    total: 3325.00,
    date: "2026-01-05T14:30:00",
    status: "executada",
    changePercent: 2.3,
  },
  {
    id: "op2",
    ticker: "VALE3",
    type: "venda",
    quantity: 50,
    price: 69.22,
    total: 3461.00,
    date: "2026-01-05T11:15:00",
    status: "executada",
    changePercent: 1.8,
  },
  {
    id: "op3",
    ticker: "ITUB4",
    type: "compra",
    quantity: 200,
    price: 31.84,
    total: 6368.00,
    date: "2026-01-04T16:45:00",
    status: "executada",
    changePercent: -0.5,
  },
  {
    id: "op4",
    ticker: "BBDC4",
    type: "compra",
    quantity: 300,
    price: 14.95,
    total: 4485.00,
    date: "2026-01-04T10:20:00",
    status: "executada",
    changePercent: 3.1,
  },
  {
    id: "op5",
    ticker: "WEGE3",
    type: "venda",
    quantity: 100,
    price: 50.02,
    total: 5002.00,
    date: "2026-01-03T15:30:00",
    status: "executada",
    changePercent: 4.2,
  },
  {
    id: "op6",
    ticker: "BTC",
    type: "compra",
    quantity: 0.005,
    price: 98500.00,
    total: 492.50,
    date: "2026-01-03T09:00:00",
    status: "executada",
    changePercent: 3.7,
  },
  {
    id: "op7",
    ticker: "PETRK325",
    type: "compra",
    quantity: 500,
    price: 2.85,
    total: 1425.00,
    date: "2026-01-02T14:00:00",
    status: "executada",
    changePercent: 14.0,
  },
  {
    id: "op8",
    ticker: "MGLU3",
    type: "venda",
    quantity: 200,
    price: 8.50,
    total: 1700.00,
    date: "2026-01-02T11:30:00",
    status: "executada",
    changePercent: -2.1,
  },
  {
    id: "op9",
    ticker: "ETH",
    type: "compra",
    quantity: 0.1,
    price: 2570.00,
    total: 257.00,
    date: "2026-01-01T18:00:00",
    status: "executada",
    changePercent: 7.1,
  },
  {
    id: "op10",
    ticker: "ABEV3",
    type: "compra",
    quantity: 400,
    price: 12.80,
    total: 5120.00,
    date: "2025-12-30T10:00:00",
    status: "executada",
    changePercent: 1.5,
  },
];

// Dados de performance para o gráfico (últimos 30 dias)
export const MOCK_PERFORMANCE_30D: PerformancePoint[] = [
  { date: "2025-12-06", value: 118500 },
  { date: "2025-12-07", value: 119200 },
  { date: "2025-12-08", value: 118800 },
  { date: "2025-12-09", value: 119500 },
  { date: "2025-12-10", value: 120100 },
  { date: "2025-12-11", value: 119800 },
  { date: "2025-12-12", value: 120500 },
  { date: "2025-12-13", value: 121200 },
  { date: "2025-12-14", value: 120800 },
  { date: "2025-12-15", value: 121500 },
  { date: "2025-12-16", value: 122000 },
  { date: "2025-12-17", value: 121700 },
  { date: "2025-12-18", value: 122300 },
  { date: "2025-12-19", value: 122800 },
  { date: "2025-12-20", value: 122500 },
  { date: "2025-12-21", value: 123000 },
  { date: "2025-12-22", value: 122700 },
  { date: "2025-12-23", value: 123200 },
  { date: "2025-12-24", value: 123500 },
  { date: "2025-12-25", value: 123800 },
  { date: "2025-12-26", value: 123500 },
  { date: "2025-12-27", value: 124000 },
  { date: "2025-12-28", value: 124300 },
  { date: "2025-12-29", value: 124000 },
  { date: "2025-12-30", value: 124500 },
  { date: "2025-12-31", value: 124800 },
  { date: "2026-01-01", value: 124500 },
  { date: "2026-01-02", value: 125000 },
  { date: "2026-01-03", value: 124700 },
  { date: "2026-01-04", value: 125100 },
  { date: "2026-01-05", value: 125430 },
];

// Dados de performance para diferentes períodos
export const MOCK_PERFORMANCE_7D: PerformancePoint[] = MOCK_PERFORMANCE_30D.slice(-7);
export const MOCK_PERFORMANCE_90D: PerformancePoint[] = [
  { date: "2025-10-07", value: 105000 },
  { date: "2025-10-14", value: 106500 },
  { date: "2025-10-21", value: 108000 },
  { date: "2025-10-28", value: 109500 },
  { date: "2025-11-04", value: 111000 },
  { date: "2025-11-11", value: 112500 },
  { date: "2025-11-18", value: 114000 },
  { date: "2025-11-25", value: 115500 },
  { date: "2025-12-02", value: 117000 },
  { date: "2025-12-09", value: 119500 },
  { date: "2025-12-16", value: 122000 },
  { date: "2025-12-23", value: 123500 },
  { date: "2025-12-30", value: 124500 },
  { date: "2026-01-05", value: 125430 },
];

// Estatísticas de trading
export interface TradingStats {
  totalTrades: number;
  winRate: number;
  profitFactor: number;
  avgReturn: number;
  bestTrade: number;
  worstTrade: number;
}

export const MOCK_TRADING_STATS: TradingStats = {
  totalTrades: 47,
  winRate: 68.1,
  profitFactor: 2.3,
  avgReturn: 1.85,
  bestTrade: 14.0,
  worstTrade: -5.2,
};

// Função para formatar valores em Real
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

// Função para formatar percentual
export function formatPercent(value: number, showSign: boolean = true): string {
  const sign = showSign && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

// Função para formatar data
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

// Função para obter dados de performance por período
export function getPerformanceData(period: "7d" | "30d" | "90d" | "1a" | "max"): PerformancePoint[] {
  switch (period) {
    case "7d":
      return MOCK_PERFORMANCE_7D;
    case "30d":
      return MOCK_PERFORMANCE_30D;
    case "90d":
      return MOCK_PERFORMANCE_90D;
    case "1a":
    case "max":
      return MOCK_PERFORMANCE_90D; // Simplificado para o MVP
    default:
      return MOCK_PERFORMANCE_30D;
  }
}
