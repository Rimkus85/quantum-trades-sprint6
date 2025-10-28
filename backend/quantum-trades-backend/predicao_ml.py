"""
Módulo de Predição ML para Otimização de Períodos
Magnus Wealth - Versão 1.0

Usa modelo Random Forest para prever período ótimo CHiLo
"""

import os
import numpy as np
import pandas as pd
import joblib
import json
from typing import Dict, Tuple, List
from datetime import datetime

class PreditorPeriodo:
    """
    Preditor de período ótimo usando Machine Learning
    """
    
    def __init__(self, modelo_path: str = None, scaler_path: str = None, metadata_path: str = None):
        """
        Inicializa preditor
        
        Args:
            modelo_path: Caminho para o modelo treinado
            scaler_path: Caminho para o scaler
            metadata_path: Caminho para os metadados
        """
        # Caminhos padrão
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.modelo_path = modelo_path or os.path.join(base_dir, 'modelo_periodo_ml.pkl')
        self.scaler_path = scaler_path or os.path.join(base_dir, 'scaler_ml.pkl')
        self.metadata_path = metadata_path or os.path.join(base_dir, 'modelo_metadata.json')
        
        # Verificar se modelo existe
        self.modelo_disponivel = os.path.exists(self.modelo_path) and os.path.exists(self.scaler_path)
        
        if self.modelo_disponivel:
            self.carregar_modelo()
        else:
            print("⚠️  Modelo ML não encontrado. Usando otimização completa.")
            self.modelo = None
            self.scaler = None
            self.feature_cols = None
    
    def carregar_modelo(self):
        """
        Carrega modelo e scaler
        """
        try:
            self.modelo = joblib.load(self.modelo_path)
            self.scaler = joblib.load(self.scaler_path)
            
            # Carregar metadados
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.feature_cols = metadata['feature_cols']
                    self.metricas = metadata.get('metricas', {})
            else:
                # Features padrão
                self.feature_cols = [
                    'atr_14', 'std_20', 'volatility_ratio',
                    'ma_slope', 'trend_strength', 'volume_ratio',
                    'roc_10', 'rsi_14', 'autocorr_5', 'autocorr_10'
                ]
            
            print(f"✓ Modelo ML carregado (MAE: {self.metricas.get('mae_test', 'N/A')})")
            
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            self.modelo_disponivel = False
            self.modelo = None
            self.scaler = None
    
    def extrair_features(self, df: pd.DataFrame) -> Dict:
        """
        Extrai features do mercado para ML
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Dict com features extraídas
        """
        # Garantir que temos dados suficientes
        if len(df) < 60:
            return None
        
        try:
            # Calcular ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr_14 = true_range.rolling(14).mean().iloc[-1]
            
            # Volatilidade
            returns = df['close'].pct_change()
            std_20 = returns.rolling(20).std().iloc[-1]
            std_60 = returns.rolling(60).std().iloc[-1]
            volatility_ratio = std_20 / std_60 if std_60 > 0 else 1.0
            
            # Tendência (slope da MA50)
            ma_50 = df['close'].rolling(50).mean()
            if len(ma_50.dropna()) >= 10:
                ma_slope = (ma_50.iloc[-1] - ma_50.iloc[-10]) / 10
            else:
                ma_slope = 0
            
            trend_strength = abs(ma_slope) / std_20 if std_20 > 0 else 0
            
            # Volume
            volume_ma_20 = df['volume'].rolling(20).mean()
            volume_ratio = df['volume'].iloc[-1] / volume_ma_20.iloc[-1] if volume_ma_20.iloc[-1] > 0 else 1.0
            
            # ROC (Rate of Change)
            roc_10 = ((df['close'].iloc[-1] / df['close'].iloc[-11]) - 1) * 100 if len(df) >= 11 else 0
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_14 = (100 - (100 / (1 + rs))).iloc[-1] if len(rs.dropna()) > 0 else 50
            
            # Autocorrelação
            if len(returns.dropna()) >= 10:
                autocorr_5 = returns.autocorr(lag=5)
                autocorr_10 = returns.autocorr(lag=10)
            else:
                autocorr_5 = 0
                autocorr_10 = 0
            
            features = {
                'atr_14': float(atr_14) if not np.isnan(atr_14) else 0,
                'std_20': float(std_20) if not np.isnan(std_20) else 0,
                'volatility_ratio': float(volatility_ratio) if not np.isnan(volatility_ratio) else 1.0,
                'ma_slope': float(ma_slope) if not np.isnan(ma_slope) else 0,
                'trend_strength': float(trend_strength) if not np.isnan(trend_strength) else 0,
                'volume_ratio': float(volume_ratio) if not np.isnan(volume_ratio) else 1.0,
                'roc_10': float(roc_10) if not np.isnan(roc_10) else 0,
                'rsi_14': float(rsi_14) if not np.isnan(rsi_14) else 50,
                'autocorr_5': float(autocorr_5) if not np.isnan(autocorr_5) else 0,
                'autocorr_10': float(autocorr_10) if not np.isnan(autocorr_10) else 0,
            }
            
            return features
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair features: {e}")
            return None
    
    def prever_periodo(self, df: pd.DataFrame) -> Tuple[int, float, List[int]]:
        """
        Prevê período ótimo e confiança
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            Tuple com (periodo_previsto, confianca, top3_periodos)
        """
        if not self.modelo_disponivel:
            return None, 0, []
        
        # Extrair features
        features = self.extrair_features(df)
        if features is None:
            return None, 0, []
        
        try:
            # Preparar features na ordem correta
            X = np.array([[features[col] for col in self.feature_cols]])
            X_scaled = self.scaler.transform(X)
            
            # Predição
            periodo_previsto = int(self.modelo.predict(X_scaled)[0])
            
            # Calcular confiança baseado em variância do ensemble
            predicoes_arvores = [tree.predict(X_scaled)[0] for tree in self.modelo.estimators_[:10]]  # Usar 10 árvores
            std_predicoes = np.std(predicoes_arvores)
            mean_predicoes = np.mean(predicoes_arvores)
            
            # Confiança: quanto menor a variância, maior a confiança
            confianca = max(0, min(1, 1 - (std_predicoes / max(mean_predicoes, 1))))
            
            # Top 3 períodos (baseado em predições das árvores)
            periodos_unicos = sorted(set([int(p) for p in predicoes_arvores]))
            top3 = periodos_unicos[:3] if len(periodos_unicos) >= 3 else periodos_unicos
            
            # Garantir que período previsto está no top3
            if periodo_previsto not in top3:
                top3 = [periodo_previsto] + top3[:2]
            
            return periodo_previsto, confianca, top3
            
        except Exception as e:
            print(f"   ❌ Erro na predição: {e}")
            return None, 0, []
    
    def classificar_padrao(self, df: pd.DataFrame) -> str:
        """
        Classifica padrão de mercado (heurística simples)
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            String com padrão: 'tendencia_forte', 'lateralizacao', 'alta_volatilidade', 'reversao'
        """
        features = self.extrair_features(df)
        if features is None:
            return 'desconhecido'
        
        # Heurísticas simples
        if features['trend_strength'] > 2.0:
            return 'tendencia_forte'
        elif features['volatility_ratio'] > 1.5:
            return 'alta_volatilidade'
        elif abs(features['roc_10']) < 5:
            return 'lateralizacao'
        else:
            return 'reversao'

# Instância global (singleton)
_preditor_global = None

def get_preditor() -> PreditorPeriodo:
    """
    Retorna instância global do preditor (singleton)
    """
    global _preditor_global
    if _preditor_global is None:
        _preditor_global = PreditorPeriodo()
    return _preditor_global

