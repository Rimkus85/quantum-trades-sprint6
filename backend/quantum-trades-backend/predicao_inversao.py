#!/usr/bin/env python3
"""
Módulo de Predição de Inversão em Tempo Real
Magnus Wealth v9.0.0

Usa modelos treinados para prever inversão de tendência
"""

import joblib
import pandas as pd
import os
from typing import Dict, Optional

MODEL_DIR = 'ml_models'

class PreditorInversao:
    """
    Classe para fazer predições de inversão usando modelos treinados
    """
    
    def __init__(self):
        self.modelos = {}
        self.carregar_modelos()
    
    def carregar_modelos(self):
        """
        Carrega todos os modelos treinados
        """
        if not os.path.exists(MODEL_DIR):
            print(f"⚠️ Diretório de modelos não encontrado: {MODEL_DIR}")
            return
        
        # Procurar por arquivos de modelo
        for arquivo in os.listdir(MODEL_DIR):
            if arquivo.endswith('_inversao.pkl'):
                cripto = arquivo.replace('_inversao.pkl', '').replace('_', ' ').title()
                model_path = os.path.join(MODEL_DIR, arquivo)
                
                try:
                    modelo = joblib.load(model_path)
                    self.modelos[cripto] = modelo
                    print(f"✓ Modelo carregado: {cripto}")
                except Exception as e:
                    print(f"❌ Erro ao carregar modelo {cripto}: {e}")
        
        print(f"\n📊 Total de modelos carregados: {len(self.modelos)}")
    
    def prever(self, cripto: str, features: Dict) -> Optional[Dict]:
        """
        Faz predição para uma criptomoeda
        
        Args:
            cripto: Nome da criptomoeda
            features: Dicionário com features dos timeframes
                {
                    '15m_estado': 1,
                    '15m_candles_virados': 20,
                    '30m_estado': 1,
                    '30m_candles_virados': 18,
                    ...
                }
        
        Returns:
            Dicionário com predição e probabilidade
        """
        if cripto not in self.modelos:
            print(f"⚠️ Modelo não encontrado para {cripto}")
            return None
        
        modelo = self.modelos[cripto]
        
        # Preparar features
        feature_cols = []
        for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
            feature_cols.append(f'{tf}_estado')
            feature_cols.append(f'{tf}_candles_virados')
        
        # Verificar se todas as features estão presentes
        missing = [col for col in feature_cols if col not in features]
        if missing:
            print(f"⚠️ Features faltando: {missing}")
            return None
        
        # Criar DataFrame
        X = pd.DataFrame([{col: features[col] for col in feature_cols}])
        
        # Predizer
        predicao = modelo.predict(X)[0]
        probabilidade = modelo.predict_proba(X)[0]
        
        resultado = {
            'cripto': cripto,
            'vai_virar': bool(predicao),
            'probabilidade_nao_virar': float(probabilidade[0]),
            'probabilidade_virar': float(probabilidade[1]),
            'sinal_execucao': probabilidade[1] > 0.70,
            'features': features
        }
        
        return resultado
    
    def prever_todas(self, features_por_cripto: Dict[str, Dict]) -> Dict:
        """
        Faz predição para múltiplas criptomoedas
        
        Args:
            features_por_cripto: {
                'Bitcoin': {...features...},
                'Ethereum': {...features...},
                ...
            }
        
        Returns:
            Dicionário com predições de todas as criptos
        """
        resultados = {}
        
        for cripto, features in features_por_cripto.items():
            resultado = self.prever(cripto, features)
            if resultado:
                resultados[cripto] = resultado
        
        return resultados
    
    def verificar_criterio_ml(self, cripto: str, features: Dict, threshold: float = 0.70) -> bool:
        """
        Verifica se Critério 2 (ML) está satisfeito
        
        Args:
            cripto: Nome da criptomoeda
            features: Features dos timeframes
            threshold: Threshold de probabilidade (padrão: 0.70)
        
        Returns:
            True se probabilidade > threshold
        """
        resultado = self.prever(cripto, features)
        
        if not resultado:
            return False
        
        return resultado['probabilidade_virar'] > threshold


def exemplo_uso():
    """
    Exemplo de uso do preditor
    """
    print("=" * 80)
    print("EXEMPLO DE USO - PREDITOR DE INVERSÃO")
    print("=" * 80)
    
    # Criar preditor
    preditor = PreditorInversao()
    
    if not preditor.modelos:
        print("\n❌ Nenhum modelo carregado")
        print("Execute primeiro: python3 treinar_modelo_inversao.py")
        return
    
    # Exemplo de features
    # Cenário: Todos timeframes em alta com muitos candles virados
    features_bitcoin = {
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
    
    print("\n📊 Features de Exemplo (Bitcoin):")
    print("   Cenário: Todos timeframes em ALTA com muitos candles virados")
    for key, value in features_bitcoin.items():
        print(f"   {key}: {value}")
    
    # Fazer predição
    print("\n🤖 Fazendo predição...")
    resultado = preditor.prever('Bitcoin', features_bitcoin)
    
    if resultado:
        print(f"\n🎯 RESULTADO DA PREDIÇÃO:")
        print(f"   Cripto: {resultado['cripto']}")
        print(f"   Vai virar? {'SIM' if resultado['vai_virar'] else 'NÃO'}")
        print(f"   Probabilidade NÃO virar: {resultado['probabilidade_nao_virar']:.2%}")
        print(f"   Probabilidade VIRAR: {resultado['probabilidade_virar']:.2%}")
        print(f"   Sinal de execução? {'✅ SIM' if resultado['sinal_execucao'] else '⏳ NÃO'}")
        
        if resultado['sinal_execucao']:
            print(f"\n✅ CRITÉRIO 2 SATISFEITO!")
            print(f"   Probabilidade ({resultado['probabilidade_virar']:.2%}) > 70%")
            print(f"   Sistema pode executar ordem")
    
    # Testar cenário oposto
    print("\n" + "=" * 80)
    print("TESTE: Cenário Oposto (Baixa)")
    print("=" * 80)
    
    features_baixa = {
        '15m_estado': -1,
        '15m_candles_virados': 5,
        '30m_estado': -1,
        '30m_candles_virados': 3,
        '1h_estado': -1,
        '1h_candles_virados': 2,
        '6h_estado': -1,
        '6h_candles_virados': 1,
        '8h_estado': -1,
        '8h_candles_virados': 1,
        '12h_estado': 0,
        '12h_candles_virados': 0
    }
    
    resultado2 = preditor.prever('Bitcoin', features_baixa)
    
    if resultado2:
        print(f"\n🎯 RESULTADO DA PREDIÇÃO:")
        print(f"   Probabilidade VIRAR: {resultado2['probabilidade_virar']:.2%}")
        print(f"   Sinal de execução? {'✅ SIM' if resultado2['sinal_execucao'] else '⏳ NÃO'}")


if __name__ == '__main__':
    exemplo_uso()
