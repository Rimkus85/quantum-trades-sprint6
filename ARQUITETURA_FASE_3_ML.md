# 🤖 ARQUITETURA - FASE 3: MACHINE LEARNING E IA

**Projeto:** Magnus Wealth  
**Versão Alvo:** 7.3.0  
**Data:** 18/10/2025  
**Foco:** Inteligência Artificial e Aprendizado de Máquina

---

## 📋 VISÃO GERAL

A Fase 3 representa o **coração inteligente** do Magnus Wealth. Nesta fase, implementaremos modelos de Machine Learning para transformar o sistema em uma verdadeira plataforma de investimentos orientada por IA, capaz de analisar sentimentos, prever movimentos de mercado e otimizar portfólios automaticamente.

---

## 🎯 OBJETIVOS DA FASE 3

1. **Análise de Sentimento:** Processar notícias e mensagens do Telegram para identificar sentimentos (positivo, negativo, neutro) sobre ativos
2. **Previsão de Preços:** Utilizar modelos de séries temporais para prever movimentos futuros de preços
3. **Otimização de Portfólio:** Implementar algoritmos para sugerir alocações ótimas baseadas em risco e retorno

---

## 🏗️ ARQUITETURA PROPOSTA

### Estrutura Atual (v7.2.0)

```
quantum-trades-sprint6/
├── backend/
│   └── quantum-trades-backend/
│       ├── app.py (API Flask)
│       ├── app_websocket.py (WebSocket Server)
│       ├── modules/
│       │   ├── magnus_learning.py (Sistema de aprendizado básico)
│       │   └── carteira_parser.py
│       └── services/
│           └── telegram_service.py
│
└── frontend/
    └── (páginas e scripts existentes)
```

### Estrutura Proposta (v7.3.0)

```
quantum-trades-sprint6/
├── backend/
│   └── quantum-trades-backend/
│       ├── app.py (API Flask - EXPANDIDA)
│       │   └── Novos endpoints:
│       │       ├── /api/ml/sentiment/analyze
│       │       ├── /api/ml/sentiment/ticker/<ticker>
│       │       ├── /api/ml/predict/price/<ticker>
│       │       ├── /api/ml/portfolio/optimize
│       │       └── /api/ml/models/status
│       │
│       ├── ml_models/ (NOVO)
│       │   ├── __init__.py
│       │   ├── sentiment_analyzer.py (Análise de sentimento)
│       │   ├── price_predictor.py (Previsão de preços)
│       │   ├── portfolio_optimizer.py (Otimização de portfólio)
│       │   └── model_trainer.py (Treinamento de modelos)
│       │
│       ├── data/ (NOVO)
│       │   ├── models/ (Modelos treinados salvos)
│       │   ├── training/ (Dados de treinamento)
│       │   └── predictions/ (Previsões salvas)
│       │
│       └── (arquivos existentes)
│
└── frontend/
    ├── painel_ia_ml.html (NOVO)
    │   └── Visualização de previsões e sentimentos
    │
    └── js/
        └── ml_service.js (NOVO)
```

---

## 🔌 COMPONENTES DA FASE 3

### 1. **Análise de Sentimento** 😊😐😢

**Objetivo:** Analisar o sentimento de notícias e mensagens do Telegram sobre ativos específicos.

**Abordagem:**

Utilizaremos uma combinação de técnicas:

1. **Análise Léxica (Dicionário de Sentimentos):**
   - Palavras positivas: "lucro", "crescimento", "alta", "valorização", "otimista"
   - Palavras negativas: "prejuízo", "queda", "desvalorização", "pessimista", "crise"
   - Pontuação: +1 para positivas, -1 para negativas

2. **Modelo Pré-Treinado (Opcional):**
   - Utilizar modelos de NLP como `transformers` (BERT em português)
   - Requer mais recursos computacionais

**Decisão:** Começar com análise léxica (leve e rápida) e evoluir para modelos pré-treinados se necessário.

**Implementação:**

```python
class SentimentAnalyzer:
    def __init__(self):
        self.positive_words = [...]
        self.negative_words = [...]
    
    def analyze_text(self, text):
        """Analisa sentimento de um texto"""
        score = 0
        words = text.lower().split()
        
        for word in words:
            if word in self.positive_words:
                score += 1
            elif word in self.negative_words:
                score -= 1
        
        # Normalizar score
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': min(abs(score) / len(words), 1.0)
        }
    
    def analyze_ticker_sentiment(self, ticker, messages):
        """Analisa sentimento agregado para um ticker"""
        sentiments = []
        
        for msg in messages:
            if ticker in msg['text']:
                result = self.analyze_text(msg['text'])
                sentiments.append(result)
        
        # Calcular sentimento médio
        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        
        return {
            'ticker': ticker,
            'sentiment': 'positive' if avg_score > 0 else 'negative' if avg_score < 0 else 'neutral',
            'average_score': avg_score,
            'total_messages': len(sentiments)
        }
```

**Endpoints:**

```
POST /api/ml/sentiment/analyze
Body: { "text": "PETR4 teve lucro recorde no trimestre" }
Response: { "sentiment": "positive", "score": 2, "confidence": 0.67 }

GET /api/ml/sentiment/ticker/PETR4
Response: { "ticker": "PETR4", "sentiment": "positive", "average_score": 1.5, "total_messages": 10 }
```

### 2. **Previsão de Preços** 📈

**Objetivo:** Prever o preço futuro de um ativo com base em dados históricos.

**Abordagem:**

Utilizaremos modelos de séries temporais:

1. **Média Móvel Simples (SMA):**
   - Mais simples, baseline
   - Previsão = média dos últimos N dias

2. **Regressão Linear:**
   - Modelo estatístico básico
   - Captura tendências lineares

3. **ARIMA (AutoRegressive Integrated Moving Average):**
   - Modelo clássico para séries temporais
   - Captura sazonalidade e tendências

**Decisão:** Implementar **Regressão Linear** e **ARIMA** para comparação.

**Implementação:**

```python
from sklearn.linear_model import LinearRegression
import numpy as np

class PricePredictor:
    def __init__(self):
        self.models = {}
    
    def prepare_data(self, prices):
        """Prepara dados para treinamento"""
        X = np.arange(len(prices)).reshape(-1, 1)  # Dias
        y = np.array(prices)  # Preços
        return X, y
    
    def train_linear_regression(self, ticker, prices):
        """Treina modelo de regressão linear"""
        X, y = self.prepare_data(prices)
        
        model = LinearRegression()
        model.fit(X, y)
        
        self.models[ticker] = model
        
        return {
            'ticker': ticker,
            'model_type': 'linear_regression',
            'r2_score': model.score(X, y)
        }
    
    def predict_next_days(self, ticker, days=7):
        """Prevê preços para os próximos N dias"""
        if ticker not in self.models:
            raise ValueError(f"Modelo não treinado para {ticker}")
        
        model = self.models[ticker]
        
        # Gerar índices futuros
        last_index = len(model.coef_)
        future_X = np.arange(last_index, last_index + days).reshape(-1, 1)
        
        # Prever
        predictions = model.predict(future_X)
        
        return {
            'ticker': ticker,
            'predictions': [
                {
                    'day': i + 1,
                    'predicted_price': float(price)
                }
                for i, price in enumerate(predictions)
            ]
        }
```

**Endpoints:**

```
POST /api/ml/predict/train
Body: { "ticker": "PETR4", "prices": [30.5, 31.2, 30.8, ...] }
Response: { "ticker": "PETR4", "model_type": "linear_regression", "r2_score": 0.85 }

GET /api/ml/predict/price/PETR4?days=7
Response: {
  "ticker": "PETR4",
  "predictions": [
    { "day": 1, "predicted_price": 31.5 },
    { "day": 2, "predicted_price": 31.7 },
    ...
  ]
}
```

### 3. **Otimização de Portfólio** 💼

**Objetivo:** Sugerir a alocação ideal de ativos para maximizar retorno e minimizar risco.

**Abordagem:**

Implementaremos a **Teoria Moderna de Portfólio (Modern Portfolio Theory - MPT)** de Markowitz:

1. **Cálculo de Retornos Esperados:**
   - Média histórica de retornos de cada ativo

2. **Cálculo de Volatilidade (Risco):**
   - Desvio padrão dos retornos

3. **Matriz de Covariância:**
   - Correlação entre ativos

4. **Otimização:**
   - Maximizar Sharpe Ratio (retorno/risco)
   - Restrições: soma dos pesos = 100%, pesos >= 0%

**Implementação:**

```python
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self):
        self.returns = {}
        self.volatilities = {}
        self.covariance_matrix = None
    
    def calculate_returns(self, prices_history):
        """Calcula retornos esperados"""
        returns = {}
        
        for ticker, prices in prices_history.items():
            prices_array = np.array(prices)
            daily_returns = np.diff(prices_array) / prices_array[:-1]
            returns[ticker] = np.mean(daily_returns)
        
        self.returns = returns
        return returns
    
    def calculate_volatility(self, prices_history):
        """Calcula volatilidade (risco)"""
        volatilities = {}
        
        for ticker, prices in prices_history.items():
            prices_array = np.array(prices)
            daily_returns = np.diff(prices_array) / prices_array[:-1]
            volatilities[ticker] = np.std(daily_returns)
        
        self.volatilities = volatilities
        return volatilities
    
    def optimize_portfolio(self, tickers, risk_tolerance='moderate'):
        """Otimiza portfólio usando MPT"""
        n_assets = len(tickers)
        
        # Função objetivo: maximizar Sharpe Ratio
        def sharpe_ratio(weights):
            portfolio_return = sum(weights[i] * self.returns[tickers[i]] for i in range(n_assets))
            portfolio_volatility = np.sqrt(
                sum(sum(
                    weights[i] * weights[j] * self.covariance_matrix[i][j]
                    for j in range(n_assets)
                ) for i in range(n_assets))
            )
            return -(portfolio_return / portfolio_volatility)  # Negativo para maximizar
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: sum(w) - 1}  # Soma = 100%
        ]
        
        # Limites
        bounds = [(0, 1) for _ in range(n_assets)]  # 0% a 100%
        
        # Chute inicial
        initial_weights = [1/n_assets] * n_assets
        
        # Otimizar
        result = minimize(
            sharpe_ratio,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'tickers': tickers,
            'weights': [float(w) for w in result.x],
            'expected_return': sum(result.x[i] * self.returns[tickers[i]] for i in range(n_assets)),
            'expected_volatility': float(np.sqrt(sum(sum(
                result.x[i] * result.x[j] * self.covariance_matrix[i][j]
                for j in range(n_assets)
            ) for i in range(n_assets))))
        }
```

**Endpoints:**

```
POST /api/ml/portfolio/optimize
Body: {
  "tickers": ["PETR4", "VALE3", "ITUB4"],
  "prices_history": {
    "PETR4": [30.5, 31.2, ...],
    "VALE3": [65.3, 66.1, ...],
    "ITUB4": [25.8, 26.0, ...]
  },
  "risk_tolerance": "moderate"
}

Response: {
  "tickers": ["PETR4", "VALE3", "ITUB4"],
  "weights": [0.35, 0.45, 0.20],
  "expected_return": 0.025,
  "expected_volatility": 0.018
}
```

---

## 📊 INTEGRAÇÃO COM FRONTEND

### Painel de IA e ML

Criar nova página `painel_ia_ml.html` para visualizar:

1. **Sentimento de Mercado:**
   - Cards com sentimento de cada ticker
   - Gráfico de linha mostrando evolução do sentimento ao longo do tempo

2. **Previsões de Preço:**
   - Gráfico com histórico + previsões futuras
   - Intervalo de confiança

3. **Portfólio Otimizado:**
   - Gráfico de pizza mostrando alocação sugerida
   - Comparação com portfólio atual

**Wireframe:**

```
┌─────────────────────────────────────────────────┐
│  PAINEL DE IA E MACHINE LEARNING                │
├─────────────────────────────────────────────────┤
│  📊 Sentimento de Mercado                       │
│  ┌───────────┬───────────┬───────────┐         │
│  │ PETR4 😊  │ VALE3 😐  │ ITUB4 😢  │         │
│  │ Positivo  │ Neutro    │ Negativo  │         │
│  │ Score: +2 │ Score: 0  │ Score: -1 │         │
│  └───────────┴───────────┴───────────┘         │
├─────────────────────────────────────────────────┤
│  📈 Previsão de Preços (PETR4)                  │
│  ┌───────────────────────────────────────────┐ │
│  │        Histórico    │    Previsão         │ │
│  │  35 ┤         ╱─────┼─────╱               │ │
│  │  30 ┤    ╱───╱      │   ╱                 │ │
│  │  25 ┴────────────────┴──────────────────  │ │
│  │     Jan  Fev  Mar  Abr  Mai  Jun         │ │
│  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│  💼 Portfólio Otimizado                         │
│  ┌───────────────────────────────────────────┐ │
│  │        🥧 Alocação Sugerida               │ │
│  │                                           │ │
│  │     PETR4: 35%                            │ │
│  │     VALE3: 45%                            │ │
│  │     ITUB4: 20%                            │ │
│  │                                           │ │
│  │  Retorno Esperado: 2.5% ao mês            │ │
│  │  Risco (Volatilidade): 1.8%               │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 🧪 DEPENDÊNCIAS

Bibliotecas Python necessárias:

```bash
pip install numpy scipy scikit-learn pandas
```

**Opcional (para modelos avançados):**
```bash
pip install transformers torch statsmodels
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 3.1: Análise de Sentimento
- [ ] Criar `ml_models/sentiment_analyzer.py`
- [ ] Implementar dicionário de palavras positivas/negativas
- [ ] Criar método `analyze_text()`
- [ ] Criar método `analyze_ticker_sentiment()`
- [ ] Adicionar endpoints na API
- [ ] Testar com mensagens do Telegram

### Fase 3.2: Previsão de Preços
- [ ] Criar `ml_models/price_predictor.py`
- [ ] Implementar Regressão Linear
- [ ] Implementar ARIMA (opcional)
- [ ] Criar método `train_model()`
- [ ] Criar método `predict_next_days()`
- [ ] Adicionar endpoints na API
- [ ] Testar com dados históricos

### Fase 3.3: Otimização de Portfólio
- [ ] Criar `ml_models/portfolio_optimizer.py`
- [ ] Implementar cálculo de retornos
- [ ] Implementar cálculo de volatilidade
- [ ] Implementar matriz de covariância
- [ ] Implementar otimização (Sharpe Ratio)
- [ ] Adicionar endpoints na API
- [ ] Testar com múltiplos ativos

### Fase 3.4: Frontend
- [ ] Criar `painel_ia_ml.html`
- [ ] Criar `js/ml_service.js`
- [ ] Implementar visualização de sentimentos
- [ ] Implementar visualização de previsões
- [ ] Implementar visualização de portfólio otimizado

---

## 🚀 CRONOGRAMA ESTIMADO

| Fase | Descrição | Tempo Estimado |
|---|---|---|
| **3.1** | Análise de Sentimento | 5-8 horas |
| **3.2** | Previsão de Preços | 8-13 horas |
| **3.3** | Otimização de Portfólio | 8-13 horas |
| **3.4** | Frontend | 5-8 horas |
| **Testes** | Validação completa | 3-5 horas |
| **Documentação** | Atualização de docs | 2-3 horas |
| **TOTAL** | | **31-50 horas** |

---

## 🎯 RESULTADO ESPERADO

Ao final da Fase 3, o Magnus Wealth terá:

✅ Análise de sentimento em tempo real  
✅ Previsões de preços baseadas em ML  
✅ Sugestões de portfólio otimizado  
✅ Interface visual para insights de IA  
✅ Sistema completo de investimentos orientado por IA

---

**Magnus Wealth v7.3.0** - Arquitetura da Fase 3 (ML e IA) 🤖

