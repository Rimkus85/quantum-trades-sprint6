#!/usr/bin/env python3
"""
Treinamento de Modelo ML para Predição de Inversão
Magnus Wealth v9.0.0

Treina modelo para prever inversão de tendência no candle diário
baseado em padrões multi-timeframe
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import joblib
import json
import os
from datetime import datetime

# Diretório de dados e modelos
DATA_DIR = 'ml_data_8anos'
MODEL_DIR = 'ml_models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Carregar criptomoedas do portfolio_config.json
from portfolio_manager import PortfolioManager

try:
    portfolio = PortfolioManager()
    CRIPTOS = [c['name'] for c in portfolio.obter_criptos_ativas()]
    print(f"✅ Carregadas {len(CRIPTOS)} criptomoedas ativas do portfolio_config.json")
except Exception as e:
    print(f"⚠️ Erro ao carregar portfolio_config.json: {e}")
    print("⚠️ Usando lista padrão de criptomoedas")
    CRIPTOS = ['Bitcoin', 'Ethereum', 'Binance Coin', 'Solana', 'Chainlink', 'Uniswap', 'Algorand', 'VeChain']

def carregar_dataset(arquivo='dataset_ml_inversao_8anos.csv'):
    """
    Carrega dataset gerado pelo coletor
    """
    filepath = f"{DATA_DIR}/{arquivo}"
    
    if not os.path.exists(filepath):
        print(f"❌ Dataset não encontrado: {filepath}")
        print(f"Execute primeiro: python3 coletor_dados_ml_8anos.py")
        return None
    
    print(f"📊 Carregando dataset: {filepath}")
    df = pd.read_csv(filepath)
    
    print(f"✓ Dataset carregado: {len(df)} amostras")
    print(f"✓ Colunas: {list(df.columns)}")
    
    return df

def preparar_features(df):
    """
    Prepara features e target para treinamento
    """
    print("\n🔧 Preparando features...")
    
    # Remover linhas com valores nulos
    df_clean = df.dropna()
    print(f"✓ Após remover nulos: {len(df_clean)} amostras")
    
    # Features: estados e candles virados de cada timeframe
    feature_cols = []
    for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
        feature_cols.append(f'{tf}_estado')
        feature_cols.append(f'{tf}_candles_virados')
    
    # Verificar se todas as features existem
    missing_cols = [col for col in feature_cols if col not in df_clean.columns]
    if missing_cols:
        print(f"⚠️ Colunas faltando: {missing_cols}")
        return None, None, None
    
    X = df_clean[feature_cols]
    y = df_clean['virou_diario'].astype(int)
    
    print(f"✓ Features: {X.shape}")
    print(f"✓ Target: {y.shape}")
    print(f"✓ Taxa de inversão: {y.sum() / len(y) * 100:.2f}%")
    
    return X, y, feature_cols

def treinar_modelo_por_cripto(cripto, X_train, X_test, y_train, y_test, feature_cols):
    """
    Treina modelo específico para uma criptomoeda
    """
    print(f"\n{'='*80}")
    print(f"🤖 TREINANDO MODELO: {cripto}")
    print(f"{'='*80}")
    
    # Tentar Random Forest e Gradient Boosting
    modelos = {
        'RandomForest': RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    melhor_modelo = None
    melhor_score = 0
    melhor_nome = None
    
    for nome, modelo in modelos.items():
        print(f"\n📊 Testando {nome}...")
        
        # Treinar
        modelo.fit(X_train, y_train)
        
        # Predizer
        y_pred = modelo.predict(X_test)
        y_pred_proba = modelo.predict_proba(X_test)[:, 1]
        
        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        try:
            auc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc = 0
        
        print(f"   Acurácia: {accuracy:.4f}")
        print(f"   Precisão: {precision:.4f}")
        print(f"   Recall: {recall:.4f}")
        print(f"   F1-Score: {f1:.4f}")
        print(f"   AUC-ROC: {auc:.4f}")
        
        # Matriz de confusão
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n   Matriz de Confusão:")
        print(f"   {cm}")
        
        # Escolher melhor modelo baseado em F1-Score
        if f1 > melhor_score:
            melhor_score = f1
            melhor_modelo = modelo
            melhor_nome = nome
    
    print(f"\n✅ Melhor modelo: {melhor_nome} (F1: {melhor_score:.4f})")
    
    # Importância das features (se disponível)
    if hasattr(melhor_modelo, 'feature_importances_'):
        importancias = pd.DataFrame({
            'feature': feature_cols,
            'importance': melhor_modelo.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📊 Top 5 Features mais importantes:")
        for idx, row in importancias.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
    
    return melhor_modelo, melhor_nome, melhor_score

def treinar_todos_modelos():
    """
    Treina modelos para todas as criptomoedas
    """
    print("=" * 80)
    print("TREINAMENTO DE MODELOS ML - MAGNUS WEALTH v9.0.0")
    print("=" * 80)
    
    # Carregar dataset
    df = carregar_dataset()
    if df is None:
        return
    
    # Preparar features
    X, y, feature_cols = preparar_features(df)
    if X is None:
        return
    
    # Resultados
    resultados = {
        'timestamp': datetime.now().isoformat(),
        'total_amostras': len(df),
        'modelos': {}
    }
    
    # Treinar modelo para cada cripto
    for cripto in CRIPTOS:
        print(f"\n{'='*80}")
        print(f"🪙 CRIPTO: {cripto}")
        print(f"{'='*80}")
        
        # Filtrar dados da cripto
        df_cripto = df[df['cripto'] == cripto].copy()
        
        if len(df_cripto) < 100:
            print(f"⚠️ Dados insuficientes para {cripto}: {len(df_cripto)} amostras")
            continue
        
        print(f"✓ Amostras disponíveis: {len(df_cripto)}")
        
        # Preparar features da cripto
        X_cripto = df_cripto[feature_cols]
        y_cripto = df_cripto['virou_diario'].astype(int)
        
        # Verificar se há inversões suficientes
        inversoes = y_cripto.sum()
        taxa_inversao = inversoes / len(y_cripto) * 100
        
        print(f"✓ Inversões: {inversoes} ({taxa_inversao:.2f}%)")
        
        if inversoes < 10:
            print(f"⚠️ Inversões insuficientes para treinar modelo")
            continue
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X_cripto, y_cripto, 
            test_size=0.2, 
            random_state=42,
            stratify=y_cripto if inversoes > 20 else None
        )
        
        print(f"✓ Treino: {len(X_train)} amostras")
        print(f"✓ Teste: {len(X_test)} amostras")
        
        # Treinar modelo
        modelo, nome_modelo, score = treinar_modelo_por_cripto(
            cripto, X_train, X_test, y_train, y_test, feature_cols
        )
        
        if modelo is None:
            continue
        
        # Salvar modelo
        model_file = f"{MODEL_DIR}/{cripto.replace(' ', '_').lower()}_inversao.pkl"
        joblib.dump(modelo, model_file)
        print(f"\n💾 Modelo salvo: {model_file}")
        
        # Salvar metadados
        resultados['modelos'][cripto] = {
            'tipo_modelo': nome_modelo,
            'f1_score': float(score),
            'total_amostras': len(df_cripto),
            'inversoes': int(inversoes),
            'taxa_inversao': float(taxa_inversao),
            'arquivo': model_file,
            'features': feature_cols
        }
    
    # Salvar resumo
    resumo_file = f"{MODEL_DIR}/resumo_treinamento_inversao.json"
    with open(resumo_file, 'w') as f:
        json.dump(resultados, f, indent=2)
    
    print(f"\n{'='*80}")
    print("✅ TREINAMENTO CONCLUÍDO")
    print(f"{'='*80}")
    print(f"\n📊 Resumo:")
    print(f"   Modelos treinados: {len(resultados['modelos'])}")
    print(f"   Resumo salvo: {resumo_file}")
    
    # Estatísticas gerais
    if resultados['modelos']:
        scores = [m['f1_score'] for m in resultados['modelos'].values()]
        print(f"\n📈 Performance dos Modelos:")
        print(f"   F1-Score médio: {np.mean(scores):.4f}")
        print(f"   F1-Score mínimo: {np.min(scores):.4f}")
        print(f"   F1-Score máximo: {np.max(scores):.4f}")
        
        print(f"\n🏆 Melhores Modelos:")
        top_modelos = sorted(
            resultados['modelos'].items(), 
            key=lambda x: x[1]['f1_score'], 
            reverse=True
        )[:3]
        
        for cripto, info in top_modelos:
            print(f"   {cripto}: F1={info['f1_score']:.4f} ({info['tipo_modelo']})")

def testar_predicao(cripto='Bitcoin'):
    """
    Testa predição com modelo treinado
    """
    print(f"\n{'='*80}")
    print(f"🧪 TESTE DE PREDIÇÃO: {cripto}")
    print(f"{'='*80}")
    
    # Carregar modelo
    model_file = f"{MODEL_DIR}/{cripto.replace(' ', '_').lower()}_inversao.pkl"
    
    if not os.path.exists(model_file):
        print(f"❌ Modelo não encontrado: {model_file}")
        return
    
    modelo = joblib.load(model_file)
    print(f"✓ Modelo carregado: {model_file}")
    
    # Criar exemplo de features
    # Exemplo: todos timeframes em alta (estado=1) com vários candles virados
    exemplo = {
        '15m_estado': 1,
        '15m_candles_virados': 20,
        '30m_estado': 1,
        '30m_candles_virados': 18,
        '1h_estado': 1,
        '1h_candles_virados': 10,
        '6h_estado': 1,
        '6h_candles_virados': 3,
        '8h_estado': 1,
        '8h_candles_virados': 2,
        '12h_estado': 1,
        '12h_candles_virados': 2
    }
    
    X_exemplo = pd.DataFrame([exemplo])
    
    # Predizer
    predicao = modelo.predict(X_exemplo)[0]
    probabilidade = modelo.predict_proba(X_exemplo)[0]
    
    print(f"\n📊 Exemplo de Features:")
    for key, value in exemplo.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Predição:")
    print(f"   Vai virar? {'SIM' if predicao == 1 else 'NÃO'}")
    print(f"   Probabilidade NÃO virar: {probabilidade[0]:.2%}")
    print(f"   Probabilidade VIRAR: {probabilidade[1]:.2%}")
    
    if probabilidade[1] > 0.70:
        print(f"\n✅ SINAL DE EXECUÇÃO (probabilidade > 70%)")
    else:
        print(f"\n⏳ Aguardar (probabilidade < 70%)")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'testar':
        # Modo teste
        cripto = sys.argv[2] if len(sys.argv) > 2 else 'Bitcoin'
        testar_predicao(cripto)
    else:
        # Modo treinamento
        treinar_todos_modelos()
        
        # Testar com Bitcoin
        print(f"\n{'='*80}")
        testar_predicao('Bitcoin')
