#!/usr/bin/env python3
"""
Treinador Rápido de Modelos ML - Magnus Wealth v9.0.0

Treina modelos de predição de inversão de tendência
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
from pathlib import Path
from datetime import datetime
import time

def treinar_modelo_cripto(df_cripto, cripto_nome):
    """
    Treina modelo para uma criptomoeda
    """
    print(f"\n{'='*80}")
    print(f"🤖 TREINANDO: {cripto_nome}")
    print(f"{'='*80}")
    
    # Preparar features
    feature_cols = [col for col in df_cripto.columns if col not in ['cripto', 'data', 'inverteu_proximo_dia']]
    
    X = df_cripto[feature_cols]
    y = df_cripto['inverteu_proximo_dia']
    
    print(f"📊 Amostras: {len(df_cripto)}")
    print(f"📈 Features: {len(feature_cols)}")
    print(f"🔄 Inversões: {y.sum()} ({y.mean()*100:.1f}%)")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n🔧 Treinando modelos...")
    
    # Random Forest
    print(f"   🌲 Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    f1_rf = f1_score(y_test, y_pred_rf)
    print(f"      F1-Score: {f1_rf:.4f}")
    
    # Gradient Boosting
    print(f"   🚀 Gradient Boosting...")
    gb = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    f1_gb = f1_score(y_test, y_pred_gb)
    print(f"      F1-Score: {f1_gb:.4f}")
    
    # Escolher melhor
    if f1_rf >= f1_gb:
        melhor_modelo = rf
        melhor_nome = "Random Forest"
        melhor_f1 = f1_rf
        y_pred = y_pred_rf
    else:
        melhor_modelo = gb
        melhor_nome = "Gradient Boosting"
        melhor_f1 = f1_gb
        y_pred = y_pred_gb
    
    print(f"\n🏆 Melhor: {melhor_nome} (F1={melhor_f1:.4f})")
    
    # Métricas detalhadas
    print(f"\n📊 MÉTRICAS:")
    print(f"   - Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"   - Precision: {precision_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"   - Recall:    {recall_score(y_test, y_pred, zero_division=0):.4f}")
    print(f"   - F1-Score:  {f1_score(y_test, y_pred, zero_division=0):.4f}")
    
    try:
        y_proba = melhor_modelo.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)
        print(f"   - ROC-AUC:   {roc_auc:.4f}")
    except:
        pass
    
    # Salvar modelo
    output_dir = Path('ml_models')
    output_dir.mkdir(exist_ok=True)
    
    nome_arquivo = cripto_nome.lower().replace(' ', '_') + '_inversao.pkl'
    output_path = output_dir / nome_arquivo
    
    joblib.dump(melhor_modelo, output_path)
    print(f"\n💾 Modelo salvo: {output_path}")
    
    return {
        'cripto': cripto_nome,
        'modelo': melhor_nome,
        'f1_score': melhor_f1,
        'accuracy': accuracy_score(y_test, y_pred),
        'amostras': len(df_cripto),
        'arquivo': str(output_path)
    }

def main():
    """
    Função principal
    """
    print("="*80)
    print("TREINADOR RÁPIDO DE MODELOS ML - MAGNUS WEALTH v9.0.0")
    print("="*80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    inicio = time.time()
    
    # Carregar dataset
    print("📂 Carregando dataset...")
    dataset_path = Path('ml_data_8anos/dataset_inversao_completo.csv')
    
    if not dataset_path.exists():
        print(f"❌ Dataset não encontrado: {dataset_path}")
        print("Execute primeiro: python3 coletor_rapido_ml.py")
        return
    
    df = pd.read_csv(dataset_path)
    print(f"✅ {len(df)} amostras carregadas")
    print(f"🪙 {df['cripto'].nunique()} criptomoedas")
    
    # Treinar modelo para cada cripto
    resultados = []
    criptos = df['cripto'].unique()
    
    for i, cripto in enumerate(criptos, 1):
        print(f"\n\n{'#'*80}")
        print(f"# MODELO {i}/{len(criptos)}")
        print(f"{'#'*80}")
        
        df_cripto = df[df['cripto'] == cripto].copy()
        resultado = treinar_modelo_cripto(df_cripto, cripto)
        resultados.append(resultado)
    
    # Resumo final
    print(f"\n\n{'='*80}")
    print("📊 RESUMO FINAL")
    print(f"{'='*80}")
    
    df_resultados = pd.DataFrame(resultados)
    
    print(f"\n🏆 MODELOS TREINADOS:")
    for _, row in df_resultados.iterrows():
        print(f"   ✅ {row['cripto']:15s} | {row['modelo']:20s} | F1={row['f1_score']:.4f} | Acc={row['accuracy']:.4f}")
    
    print(f"\n📈 ESTATÍSTICAS GERAIS:")
    print(f"   - F1-Score médio:  {df_resultados['f1_score'].mean():.4f}")
    print(f"   - Accuracy médio:  {df_resultados['accuracy'].mean():.4f}")
    print(f"   - Total amostras:  {df_resultados['amostras'].sum()}")
    
    # Tempo total
    tempo_total = time.time() - inicio
    print(f"\n⏱️  TEMPO TOTAL: {tempo_total/60:.1f} minutos")
    print(f"✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("="*80)

if __name__ == '__main__':
    main()
