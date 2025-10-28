"""
Treinamento do Modelo de Machine Learning
Magnus Wealth - Versão 1.0

Treina modelo Random Forest para prever período ótimo CHiLo
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
from datetime import datetime

def carregar_dataset(caminho: str = '/home/ubuntu/dataset_treino_ml.csv') -> pd.DataFrame:
    """
    Carrega dataset de treinamento
    """
    print(f"📂 Carregando dataset: {caminho}")
    df = pd.DataFrame(caminho)
    print(f"   ✓ {len(df)} amostras carregadas")
    print(f"   ✓ {df['cripto'].nunique()} criptos")
    print(f"   ✓ Período: {df['data'].min()} a {df['data'].max()}")
    return df

def preparar_dados(df: pd.DataFrame):
    """
    Prepara dados para treinamento
    """
    print("\n🔧 Preparando dados...")
    
    # Features (X)
    feature_cols = [
        'atr_14', 'std_20', 'volatility_ratio',
        'ma_slope', 'trend_strength', 'volume_ratio',
        'roc_10', 'rsi_14', 'autocorr_5', 'autocorr_10'
    ]
    
    X = df[feature_cols].values
    y = df['periodo_otimo'].values
    
    print(f"   ✓ Features: {len(feature_cols)}")
    print(f"   ✓ Amostras: {len(X)}")
    
    # Split: 70% treino, 15% validação, 15% teste
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42
    )
    
    print(f"   ✓ Treino: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   ✓ Validação: {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
    print(f"   ✓ Teste: {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
    
    # Normalização
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    return {
        'X_train': X_train_scaled,
        'X_val': X_val_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train,
        'y_val': y_val,
        'y_test': y_test,
        'scaler': scaler,
        'feature_cols': feature_cols
    }

def treinar_modelo(dados: dict):
    """
    Treina modelo Random Forest
    """
    print("\n🤖 Treinando modelo Random Forest...")
    
    modelo = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    modelo.fit(dados['X_train'], dados['y_train'])
    
    print("   ✓ Modelo treinado!")
    
    return modelo

def avaliar_modelo(modelo, dados: dict):
    """
    Avalia performance do modelo
    """
    print("\n📊 Avaliando modelo...")
    
    # Predições
    y_train_pred = modelo.predict(dados['X_train'])
    y_val_pred = modelo.predict(dados['X_val'])
    y_test_pred = modelo.predict(dados['X_test'])
    
    # Métricas
    mae_train = mean_absolute_error(dados['y_train'], y_train_pred)
    mae_val = mean_absolute_error(dados['y_val'], y_val_pred)
    mae_test = mean_absolute_error(dados['y_test'], y_test_pred)
    
    r2_train = r2_score(dados['y_train'], y_train_pred)
    r2_val = r2_score(dados['y_val'], y_val_pred)
    r2_test = r2_score(dados['y_test'], y_test_pred)
    
    print(f"\n   MAE (Mean Absolute Error):")
    print(f"   • Treino: {mae_train:.2f} períodos")
    print(f"   • Validação: {mae_val:.2f} períodos")
    print(f"   • Teste: {mae_test:.2f} períodos")
    
    print(f"\n   R² Score:")
    print(f"   • Treino: {r2_train:.3f}")
    print(f"   • Validação: {r2_val:.3f}")
    print(f"   • Teste: {r2_test:.3f}")
    
    # Feature importance
    print(f"\n   📈 Importância das Features:")
    importances = modelo.feature_importances_
    for i, col in enumerate(dados['feature_cols']):
        print(f"   • {col}: {importances[i]:.3f}")
    
    # Cross-validation
    print(f"\n   🔄 Cross-Validation (5-fold):")
    cv_scores = cross_val_score(
        modelo, dados['X_train'], dados['y_train'],
        cv=5, scoring='neg_mean_absolute_error', n_jobs=-1
    )
    print(f"   • MAE médio: {-cv_scores.mean():.2f} ± {cv_scores.std():.2f}")
    
    metricas = {
        'mae_train': float(mae_train),
        'mae_val': float(mae_val),
        'mae_test': float(mae_test),
        'r2_train': float(r2_train),
        'r2_val': float(r2_val),
        'r2_test': float(r2_test),
        'cv_mae_mean': float(-cv_scores.mean()),
        'cv_mae_std': float(cv_scores.std()),
        'feature_importance': {
            col: float(imp) 
            for col, imp in zip(dados['feature_cols'], importances)
        }
    }
    
    return metricas

def salvar_modelo(modelo, scaler, metricas: dict, feature_cols: list):
    """
    Salva modelo e metadados
    """
    print("\n💾 Salvando modelo...")
    
    # Salvar modelo
    modelo_path = '/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/modelo_periodo_ml.pkl'
    joblib.dump(modelo, modelo_path)
    print(f"   ✓ Modelo salvo: {modelo_path}")
    
    # Salvar scaler
    scaler_path = '/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/scaler_ml.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"   ✓ Scaler salvo: {scaler_path}")
    
    # Salvar metadados
    metadados = {
        'versao': '1.0',
        'data_treino': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'feature_cols': feature_cols,
        'metricas': metricas
    }
    
    metadata_path = '/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/modelo_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadados, f, indent=2)
    print(f"   ✓ Metadados salvos: {metadata_path}")

def main():
    print('═══════════════════════════════════════════════════')
    print('  TREINAMENTO DO MODELO ML')
    print('  Magnus Wealth - Versão 1.0')
    print('═══════════════════════════════════════════════════\n')
    
    # 1. Carregar dataset
    df = carregar_dataset()
    
    # 2. Preparar dados
    dados = preparar_dados(df)
    
    # 3. Treinar modelo
    modelo = treinar_modelo(dados)
    
    # 4. Avaliar modelo
    metricas = avaliar_modelo(modelo, dados)
    
    # 5. Salvar modelo
    salvar_modelo(modelo, dados['scaler'], metricas, dados['feature_cols'])
    
    # 6. Validação final
    print("\n✅ VALIDAÇÃO FINAL")
    if metricas['mae_test'] < 10:
        print(f"   ✅ MAE teste ({metricas['mae_test']:.2f}) < 10 períodos - EXCELENTE!")
    elif metricas['mae_test'] < 15:
        print(f"   ⚠️  MAE teste ({metricas['mae_test']:.2f}) < 15 períodos - ACEITÁVEL")
    else:
        print(f"   ❌ MAE teste ({metricas['mae_test']:.2f}) >= 15 períodos - PRECISA MELHORAR")
    
    if metricas['r2_test'] > 0.7:
        print(f"   ✅ R² teste ({metricas['r2_test']:.3f}) > 0.7 - EXCELENTE!")
    elif metricas['r2_test'] > 0.5:
        print(f"   ⚠️  R² teste ({metricas['r2_test']:.3f}) > 0.5 - ACEITÁVEL")
    else:
        print(f"   ❌ R² teste ({metricas['r2_test']:.3f}) <= 0.5 - PRECISA MELHORAR")
    
    print("\n═══════════════════════════════════════════════════")
    print("✓ Treinamento concluído!")
    print("═══════════════════════════════════════════════════")

if __name__ == '__main__':
    main()

