# Arquitetura da Fase 4: Backtesting e Performance

**Versão:** 7.4.0  
**Data:** 18/10/2025  
**Autor:** Manus AI

---

## 1. Visão Geral

A Fase 4 tem como objetivo implementar um **sistema completo de backtesting e avaliação de performance** para validar as estratégias e modelos de Machine Learning do Magnus Wealth com dados históricos reais. Isso garantirá que as previsões e recomendações sejam confiáveis e baseadas em evidências.

## 2. Objetivos

1. **Validar modelos de ML** com dados históricos
2. **Medir acurácia** das previsões de preços
3. **Avaliar performance** das recomendações de portfólio
4. **Identificar pontos de melhoria** nos algoritmos
5. **Gerar relatórios** de performance detalhados

## 3. Componentes a Implementar

### 3.1. Sistema de Backtesting

**Arquivo:** `ml_models/backtester.py`

**Funcionalidades:**
- Simular estratégias de trading com dados históricos
- Calcular retornos acumulados
- Comparar com benchmark (Ibovespa, CDI)
- Gerar relatórios de performance

**Métricas:**
- **Retorno Total:** Percentual de ganho/perda
- **Sharpe Ratio:** Retorno ajustado ao risco
- **Maximum Drawdown:** Maior queda acumulada
- **Win Rate:** Percentual de operações vencedoras
- **Profit Factor:** Razão lucro/prejuízo

### 3.2. Avaliador de Modelos de ML

**Arquivo:** `ml_models/model_evaluator.py`

**Funcionalidades:**
- Avaliar acurácia do preditor de preços
- Medir performance do analisador de sentimento
- Validar otimizador de portfólio
- Gerar métricas de qualidade

**Métricas:**
- **MAE (Mean Absolute Error):** Erro médio absoluto
- **RMSE (Root Mean Squared Error):** Raiz do erro quadrático médio
- **R² Score:** Coeficiente de determinação
- **Accuracy:** Acurácia de classificação (sentimento)
- **F1 Score:** Média harmônica de precisão e recall

### 3.3. Coletor de Dados Históricos

**Arquivo:** `services/historical_data_service.py`

**Funcionalidades:**
- Buscar dados históricos de ações (brapi.dev)
- Armazenar dados localmente (cache)
- Atualizar dados periodicamente
- Fornecer dados para backtesting

**APIs a integrar:**
- **brapi.dev:** Cotações históricas (gratuito)
- **Yahoo Finance:** Dados complementares
- **Backup local:** CSV/JSON para cache

### 3.4. Gerador de Relatórios

**Arquivo:** `modules/performance_reporter.py`

**Funcionalidades:**
- Gerar relatórios de backtesting
- Criar gráficos de performance
- Comparar estratégias
- Exportar resultados (PDF, JSON)

**Visualizações:**
- Curva de retorno acumulado
- Drawdown ao longo do tempo
- Distribuição de retornos
- Comparação com benchmark

## 4. Arquitetura de Dados

### 4.1. Estrutura de Diretórios

```
backend/quantum-trades-backend/
├── ml_models/
│   ├── backtester.py          # Sistema de backtesting
│   ├── model_evaluator.py     # Avaliador de modelos
│   └── ...
├── services/
│   ├── historical_data_service.py  # Coletor de dados
│   └── ...
├── modules/
│   ├── performance_reporter.py     # Gerador de relatórios
│   └── ...
├── data/
│   ├── historical/            # Dados históricos em cache
│   ├── backtests/             # Resultados de backtests
│   └── reports/               # Relatórios gerados
```

### 4.2. Formato de Dados Históricos

```json
{
  "ticker": "PETR4",
  "period": "1y",
  "data": [
    {
      "date": "2024-10-18",
      "open": 30.50,
      "high": 31.20,
      "low": 30.10,
      "close": 30.80,
      "volume": 1500000
    }
  ]
}
```

### 4.3. Formato de Resultado de Backtest

```json
{
  "strategy": "ml_portfolio_optimization",
  "period": "2024-01-01 to 2025-10-18",
  "initial_capital": 10000,
  "final_capital": 12500,
  "metrics": {
    "total_return": 25.0,
    "sharpe_ratio": 1.8,
    "max_drawdown": -8.5,
    "win_rate": 65.0,
    "profit_factor": 2.1
  },
  "trades": [...]
}
```

## 5. Fluxo de Backtesting

```
1. Coletar Dados Históricos
   ↓
2. Preparar Dados (normalização, features)
   ↓
3. Dividir em Treino/Teste (80/20)
   ↓
4. Treinar Modelo com Dados de Treino
   ↓
5. Simular Estratégia com Dados de Teste
   ↓
6. Calcular Métricas de Performance
   ↓
7. Gerar Relatório e Visualizações
```

## 6. Endpoints da API

Novos endpoints a serem implementados:

| Método | Endpoint                          | Descrição                                    |
|--------|-----------------------------------|----------------------------------------------|
| `GET`  | `/api/backtest/run`               | Executa backtesting de uma estratégia        |
| `GET`  | `/api/backtest/results/<id>`      | Retorna resultados de um backtest            |
| `GET`  | `/api/backtest/list`              | Lista todos os backtests executados          |
| `GET`  | `/api/historical/<ticker>`        | Busca dados históricos de um ticker          |
| `GET`  | `/api/performance/models`         | Avalia performance dos modelos de ML         |
| `GET`  | `/api/performance/report/<id>`    | Gera relatório de performance                |

## 7. Frontend

### 7.1. Página de Backtesting

**Arquivo:** `frontend/painel_backtesting.html`

**Seções:**
- **Configuração:** Escolher estratégia, período, capital inicial
- **Execução:** Botão para iniciar backtest
- **Resultados:** Métricas e gráficos de performance
- **Histórico:** Lista de backtests anteriores

### 7.2. Visualizações

- **Gráfico de Retorno Acumulado:** Linha do tempo mostrando evolução do capital
- **Gráfico de Drawdown:** Visualização das quedas
- **Tabela de Métricas:** Sharpe, Win Rate, etc.
- **Comparação com Benchmark:** Lado a lado com Ibovespa

## 8. Tecnologias e Bibliotecas

| Biblioteca       | Uso                                          |
|------------------|----------------------------------------------|
| `pandas`         | Manipulação de dados históricos              |
| `numpy`          | Cálculos numéricos                           |
| `matplotlib`     | Geração de gráficos                          |
| `scikit-learn`   | Métricas de avaliação de modelos             |
| `requests`       | Chamadas à API de dados históricos           |

## 9. Cronograma de Implementação

| Fase | Componente                    | Tempo Estimado |
|------|-------------------------------|----------------|
| 4.1  | Coletor de Dados Históricos   | 1-2h           |
| 4.2  | Sistema de Backtesting        | 2-3h           |
| 4.3  | Avaliador de Modelos          | 1-2h           |
| 4.4  | Gerador de Relatórios         | 1-2h           |
| 4.5  | Endpoints da API              | 1h             |
| 4.6  | Frontend de Backtesting       | 2-3h           |
| 4.7  | Testes e Validação            | 1h             |
| **Total** |                          | **9-14h**      |

## 10. Critérios de Sucesso

- ✅ Sistema de backtesting funcionando com dados reais
- ✅ Métricas de performance calculadas corretamente
- ✅ Relatórios gerados automaticamente
- ✅ Frontend interativo e responsivo
- ✅ 100% de aprovação nos testes
- ✅ Zero regressões nas funcionalidades existentes

---

**Próximo Passo:** Implementar o coletor de dados históricos.

