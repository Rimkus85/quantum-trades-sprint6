#!/usr/bin/env python3
"""
Magnus Wealth - Price Predictor
Preditor de preços usando modelos de Machine Learning
"""

import os
import json
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

class PricePredictor:
    """
    Preditor de preços usando Regressão Linear e features técnicas
    """
    
    def __init__(self, models_dir='data/models'):
        """
        Inicializa o preditor
        
        Args:
            models_dir: Diretório para salvar modelos treinados
        """
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.metadata = {}
        
        # Criar diretório se não existir
        os.makedirs(models_dir, exist_ok=True)
    
    def calculate_technical_features(self, prices: List[float]) -> np.ndarray:
        """
        Calcula features técnicas a partir dos preços
        
        Args:
            prices: Lista de preços históricos
            
        Returns:
            Array numpy com features
        """
        prices_array = np.array(prices)
        n = len(prices_array)
        
        features = []
        
        for i in range(n):
            # Features básicas
            current_price = prices_array[i]
            
            # Médias móveis
            if i >= 5:
                ma5 = np.mean(prices_array[i-5:i+1])
            else:
                ma5 = current_price
            
            if i >= 10:
                ma10 = np.mean(prices_array[i-10:i+1])
            else:
                ma10 = current_price
            
            if i >= 20:
                ma20 = np.mean(prices_array[i-20:i+1])
            else:
                ma20 = current_price
            
            # Retorno (variação percentual)
            if i > 0:
                returns = (current_price - prices_array[i-1]) / prices_array[i-1]
            else:
                returns = 0
            
            # Volatilidade (desvio padrão dos últimos 5 dias)
            if i >= 5:
                volatility = np.std(prices_array[i-5:i+1])
            else:
                volatility = 0
            
            # Momentum (diferença entre MA5 e MA20)
            momentum = ma5 - ma20
            
            # RSI simplificado (últimos 14 dias)
            if i >= 14:
                gains = []
                losses = []
                for j in range(i-13, i+1):
                    change = prices_array[j] - prices_array[j-1]
                    if change > 0:
                        gains.append(change)
                    else:
                        losses.append(abs(change))
                
                avg_gain = np.mean(gains) if gains else 0
                avg_loss = np.mean(losses) if losses else 0
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
            else:
                rsi = 50  # Neutro
            
            # Adicionar features
            features.append([
                current_price,
                ma5,
                ma10,
                ma20,
                returns,
                volatility,
                momentum,
                rsi,
                i  # Índice temporal
            ])
        
        return np.array(features)
    
    def prepare_data(self, prices: List[float], lookback: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara dados para treinamento
        
        Args:
            prices: Lista de preços históricos
            lookback: Número de dias anteriores para usar como features
            
        Returns:
            Tupla (X, y) com features e targets
        """
        # Calcular features técnicas
        features = self.calculate_technical_features(prices)
        
        X = []
        y = []
        
        # Criar janelas deslizantes
        for i in range(lookback, len(features)):
            # Features: últimos N dias
            X.append(features[i-lookback:i].flatten())
            
            # Target: preço do próximo dia
            y.append(prices[i])
        
        return np.array(X), np.array(y)
    
    def train_model(self, ticker: str, prices: List[float], dates: Optional[List[str]] = None) -> Dict:
        """
        Treina modelo de previsão para um ticker
        
        Args:
            ticker: Ticker do ativo
            prices: Lista de preços históricos
            dates: Lista de datas correspondentes (opcional)
            
        Returns:
            Dicionário com métricas de treinamento
        """
        ticker = ticker.upper()
        
        if len(prices) < 30:
            raise ValueError(f"Necessário pelo menos 30 dias de histórico. Fornecido: {len(prices)}")
        
        # Preparar dados
        X, y = self.prepare_data(prices, lookback=5)
        
        # Dividir em treino e teste (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Normalizar features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Treinar modelo
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Avaliar
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        # Salvar modelo e scaler
        self.models[ticker] = model
        self.scalers[ticker] = scaler
        self.metadata[ticker] = {
            'ticker': ticker,
            'trained_at': datetime.now().isoformat(),
            'n_samples': len(prices),
            'train_r2': float(train_r2),
            'test_r2': float(test_r2),
            'train_rmse': float(train_rmse),
            'test_rmse': float(test_rmse),
            'last_price': float(prices[-1]),
            'lookback': 5
        }
        
        # Salvar em disco
        self._save_model(ticker)
        
        return {
            'ticker': ticker,
            'model_type': 'linear_regression',
            'train_r2': round(train_r2, 4),
            'test_r2': round(test_r2, 4),
            'train_rmse': round(train_rmse, 4),
            'test_rmse': round(test_rmse, 4),
            'n_samples': len(prices),
            'status': 'trained'
        }
    
    def predict_next_days(self, ticker: str, prices: List[float], days: int = 7) -> Dict:
        """
        Prevê preços para os próximos N dias
        
        Args:
            ticker: Ticker do ativo
            prices: Lista de preços históricos recentes
            days: Número de dias a prever
            
        Returns:
            Dicionário com previsões
        """
        ticker = ticker.upper()
        
        # Carregar modelo se não estiver em memória
        if ticker not in self.models:
            self._load_model(ticker)
        
        if ticker not in self.models:
            raise ValueError(f"Modelo não treinado para {ticker}")
        
        model = self.models[ticker]
        scaler = self.scalers[ticker]
        lookback = self.metadata[ticker]['lookback']
        
        # Preparar dados atuais
        current_prices = prices[-30:] if len(prices) > 30 else prices  # Últimos 30 dias
        predictions = []
        
        # Fazer previsões iterativas
        for day in range(days):
            # Calcular features
            features = self.calculate_technical_features(current_prices)
            
            # Pegar últimos lookback dias
            X = features[-lookback:].flatten().reshape(1, -1)
            
            # Normalizar
            X_scaled = scaler.transform(X)
            
            # Prever
            predicted_price = model.predict(X_scaled)[0]
            
            # Adicionar à lista de previsões
            predictions.append({
                'day': day + 1,
                'predicted_price': round(float(predicted_price), 2)
            })
            
            # Adicionar previsão ao histórico para próxima iteração
            current_prices.append(predicted_price)
        
        # Calcular tendência
        first_pred = predictions[0]['predicted_price']
        last_pred = predictions[-1]['predicted_price']
        current_price = prices[-1]
        
        trend_change = ((last_pred - current_price) / current_price) * 100
        
        if trend_change > 2:
            trend = 'bullish'
            emoji = '📈'
        elif trend_change < -2:
            trend = 'bearish'
            emoji = '📉'
        else:
            trend = 'neutral'
            emoji = '➡️'
        
        return {
            'ticker': ticker,
            'current_price': round(float(current_price), 2),
            'predictions': predictions,
            'trend': trend,
            'trend_emoji': emoji,
            'trend_change_percent': round(trend_change, 2),
            'model_metadata': self.metadata.get(ticker, {})
        }
    
    def _save_model(self, ticker: str):
        """Salva modelo em disco"""
        ticker = ticker.upper()
        
        if ticker not in self.models:
            return
        
        # Salvar modelo
        model_path = os.path.join(self.models_dir, f'{ticker}_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(self.models[ticker], f)
        
        # Salvar scaler
        scaler_path = os.path.join(self.models_dir, f'{ticker}_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scalers[ticker], f)
        
        # Salvar metadata
        metadata_path = os.path.join(self.models_dir, f'{ticker}_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata[ticker], f, indent=2)
    
    def _load_model(self, ticker: str):
        """Carrega modelo do disco"""
        ticker = ticker.upper()
        
        model_path = os.path.join(self.models_dir, f'{ticker}_model.pkl')
        scaler_path = os.path.join(self.models_dir, f'{ticker}_scaler.pkl')
        metadata_path = os.path.join(self.models_dir, f'{ticker}_metadata.json')
        
        if not os.path.exists(model_path):
            return
        
        # Carregar modelo
        with open(model_path, 'rb') as f:
            self.models[ticker] = pickle.load(f)
        
        # Carregar scaler
        with open(scaler_path, 'rb') as f:
            self.scalers[ticker] = pickle.load(f)
        
        # Carregar metadata
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata[ticker] = json.load(f)
    
    def get_model_info(self, ticker: str) -> Optional[Dict]:
        """Retorna informações sobre um modelo treinado"""
        ticker = ticker.upper()
        
        if ticker not in self.metadata:
            self._load_model(ticker)
        
        return self.metadata.get(ticker)
    
    def list_trained_models(self) -> List[str]:
        """Lista todos os modelos treinados"""
        models = []
        
        if not os.path.exists(self.models_dir):
            return models
        
        for filename in os.listdir(self.models_dir):
            if filename.endswith('_model.pkl'):
                ticker = filename.replace('_model.pkl', '')
                models.append(ticker)
        
        return sorted(models)


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do preditor de preços"""
    
    predictor = PricePredictor()
    
    print("=" * 60)
    print("TESTE DO PREDITOR DE PREÇOS")
    print("=" * 60)
    
    # Gerar dados sintéticos (tendência de alta com ruído)
    np.random.seed(42)
    base_price = 30.0
    trend = 0.05  # 5% de crescimento
    noise = 0.5
    
    prices = []
    for i in range(60):
        price = base_price * (1 + trend * i / 60) + np.random.normal(0, noise)
        prices.append(price)
    
    print(f"\n1. Dados Sintéticos Gerados:")
    print(f"   Total de dias: {len(prices)}")
    print(f"   Preço inicial: R$ {prices[0]:.2f}")
    print(f"   Preço final: R$ {prices[-1]:.2f}")
    print(f"   Variação: {((prices[-1] - prices[0]) / prices[0] * 100):.2f}%")
    
    # Treinar modelo
    print(f"\n2. Treinando Modelo:")
    result = predictor.train_model('TEST4', prices)
    print(f"   Ticker: {result['ticker']}")
    print(f"   Modelo: {result['model_type']}")
    print(f"   R² (treino): {result['train_r2']:.4f}")
    print(f"   R² (teste): {result['test_r2']:.4f}")
    print(f"   RMSE (treino): R$ {result['train_rmse']:.4f}")
    print(f"   RMSE (teste): R$ {result['test_rmse']:.4f}")
    
    # Fazer previsões
    print(f"\n3. Previsões para os Próximos 7 Dias:")
    predictions = predictor.predict_next_days('TEST4', prices, days=7)
    print(f"   Preço atual: R$ {predictions['current_price']:.2f}")
    print(f"   Tendência: {predictions['trend']} {predictions['trend_emoji']}")
    print(f"   Variação esperada: {predictions['trend_change_percent']:.2f}%")
    print(f"\n   Previsões:")
    for pred in predictions['predictions']:
        print(f"     Dia {pred['day']}: R$ {pred['predicted_price']:.2f}")
    
    # Listar modelos
    print(f"\n4. Modelos Treinados:")
    models = predictor.list_trained_models()
    print(f"   Total: {len(models)}")
    for model in models:
        info = predictor.get_model_info(model)
        if info:
            print(f"   - {model}: R² = {info.get('test_r2', 0):.4f}")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

