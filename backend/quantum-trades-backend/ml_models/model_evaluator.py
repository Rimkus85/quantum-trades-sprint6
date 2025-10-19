#!/usr/bin/env python3
"""
Magnus Wealth - Model Evaluator
Avaliador de performance de modelos de Machine Learning
"""

import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class ModelEvaluator:
    """
    Avaliador de performance de modelos de ML
    """
    
    def __init__(self):
        """Inicializa o avaliador"""
        pass
    
    # ========================================================================
    # MÉTRICAS PARA REGRESSÃO (Predição de Preços)
    # ========================================================================
    
    def evaluate_regression(
        self,
        y_true: List[float],
        y_pred: List[float]
    ) -> Dict:
        """
        Avalia modelo de regressão
        
        Args:
            y_true: Valores reais
            y_pred: Valores previstos
            
        Returns:
            Dicionário com métricas
        """
        y_true_array = np.array(y_true)
        y_pred_array = np.array(y_pred)
        
        # MAE (Mean Absolute Error)
        mae = mean_absolute_error(y_true_array, y_pred_array)
        
        # MSE (Mean Squared Error)
        mse = mean_squared_error(y_true_array, y_pred_array)
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(mse)
        
        # R² Score
        r2 = r2_score(y_true_array, y_pred_array)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true_array - y_pred_array) / y_true_array)) * 100
        
        # Erro médio
        mean_error = np.mean(y_pred_array - y_true_array)
        
        return {
            'mae': round(float(mae), 4),
            'mse': round(float(mse), 4),
            'rmse': round(float(rmse), 4),
            'r2_score': round(float(r2), 4),
            'mape': round(float(mape), 2),
            'mean_error': round(float(mean_error), 4)
        }
    
    def evaluate_price_predictor(
        self,
        actual_prices: List[float],
        predicted_prices: List[float]
    ) -> Dict:
        """
        Avalia preditor de preços
        
        Args:
            actual_prices: Preços reais
            predicted_prices: Preços previstos
            
        Returns:
            Avaliação detalhada
        """
        # Métricas de regressão
        metrics = self.evaluate_regression(actual_prices, predicted_prices)
        
        # Calcular acurácia direcional (se previu corretamente a direção)
        direction_accuracy = self.calculate_direction_accuracy(
            actual_prices,
            predicted_prices
        )
        
        # Classificar qualidade do modelo
        quality = self.classify_model_quality(metrics['r2_score'])
        
        return {
            'metrics': metrics,
            'direction_accuracy': round(direction_accuracy, 2),
            'quality': quality,
            'n_samples': len(actual_prices)
        }
    
    def calculate_direction_accuracy(
        self,
        actual_prices: List[float],
        predicted_prices: List[float]
    ) -> float:
        """
        Calcula acurácia de direção (subida/descida)
        
        Args:
            actual_prices: Preços reais
            predicted_prices: Preços previstos
            
        Returns:
            Acurácia percentual
        """
        if len(actual_prices) < 2:
            return 0.0
        
        correct = 0
        total = 0
        
        for i in range(1, len(actual_prices)):
            # Direção real
            actual_direction = 1 if actual_prices[i] > actual_prices[i-1] else 0
            
            # Direção prevista
            pred_direction = 1 if predicted_prices[i] > predicted_prices[i-1] else 0
            
            if actual_direction == pred_direction:
                correct += 1
            
            total += 1
        
        return (correct / total * 100) if total > 0 else 0.0
    
    def classify_model_quality(self, r2_score: float) -> str:
        """
        Classifica qualidade do modelo baseado no R²
        
        Args:
            r2_score: R² Score
            
        Returns:
            Classificação (excelente, bom, regular, ruim)
        """
        if r2_score >= 0.9:
            return 'excelente'
        elif r2_score >= 0.7:
            return 'bom'
        elif r2_score >= 0.5:
            return 'regular'
        else:
            return 'ruim'
    
    # ========================================================================
    # MÉTRICAS PARA CLASSIFICAÇÃO (Análise de Sentimento)
    # ========================================================================
    
    def evaluate_classification(
        self,
        y_true: List[int],
        y_pred: List[int],
        labels: List[str] = None
    ) -> Dict:
        """
        Avalia modelo de classificação
        
        Args:
            y_true: Classes reais
            y_pred: Classes previstas
            labels: Nomes das classes
            
        Returns:
            Dicionário com métricas
        """
        # Accuracy
        accuracy = accuracy_score(y_true, y_pred)
        
        # Precision, Recall, F1 (weighted average)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        return {
            'accuracy': round(float(accuracy), 4),
            'precision': round(float(precision), 4),
            'recall': round(float(recall), 4),
            'f1_score': round(float(f1), 4)
        }
    
    def evaluate_sentiment_analyzer(
        self,
        true_sentiments: List[str],
        predicted_sentiments: List[str]
    ) -> Dict:
        """
        Avalia analisador de sentimento
        
        Args:
            true_sentiments: Sentimentos reais
            predicted_sentiments: Sentimentos previstos
            
        Returns:
            Avaliação detalhada
        """
        # Mapear sentimentos para números
        sentiment_map = {'negative': 0, 'neutral': 1, 'positive': 2}
        
        y_true = [sentiment_map.get(s, 1) for s in true_sentiments]
        y_pred = [sentiment_map.get(s, 1) for s in predicted_sentiments]
        
        # Métricas de classificação
        metrics = self.evaluate_classification(y_true, y_pred)
        
        # Calcular matriz de confusão simplificada
        confusion = self.calculate_confusion_matrix(true_sentiments, predicted_sentiments)
        
        return {
            'metrics': metrics,
            'confusion_matrix': confusion,
            'n_samples': len(true_sentiments)
        }
    
    def calculate_confusion_matrix(
        self,
        true_labels: List[str],
        pred_labels: List[str]
    ) -> Dict:
        """
        Calcula matriz de confusão simplificada
        
        Args:
            true_labels: Labels reais
            pred_labels: Labels previstos
            
        Returns:
            Matriz de confusão
        """
        labels = ['negative', 'neutral', 'positive']
        matrix = {label: {pred: 0 for pred in labels} for label in labels}
        
        for true_label, pred_label in zip(true_labels, pred_labels):
            if true_label in labels and pred_label in labels:
                matrix[true_label][pred_label] += 1
        
        return matrix
    
    # ========================================================================
    # MÉTRICAS PARA OTIMIZAÇÃO DE PORTFÓLIO
    # ========================================================================
    
    def evaluate_portfolio_optimizer(
        self,
        actual_returns: List[float],
        predicted_returns: List[float],
        actual_volatility: float,
        predicted_volatility: float
    ) -> Dict:
        """
        Avalia otimizador de portfólio
        
        Args:
            actual_returns: Retornos reais
            predicted_returns: Retornos previstos
            actual_volatility: Volatilidade real
            predicted_volatility: Volatilidade prevista
            
        Returns:
            Avaliação detalhada
        """
        # Erro de retorno
        return_error = abs(np.mean(actual_returns) - np.mean(predicted_returns))
        
        # Erro de volatilidade
        volatility_error = abs(actual_volatility - predicted_volatility)
        
        # Correlação entre retornos reais e previstos
        correlation = np.corrcoef(actual_returns, predicted_returns)[0, 1]
        
        return {
            'return_error': round(float(return_error), 4),
            'volatility_error': round(float(volatility_error), 4),
            'correlation': round(float(correlation), 4),
            'n_samples': len(actual_returns)
        }
    
    # ========================================================================
    # RELATÓRIO CONSOLIDADO
    # ========================================================================
    
    def generate_model_report(
        self,
        model_name: str,
        model_type: str,
        evaluation_results: Dict
    ) -> Dict:
        """
        Gera relatório consolidado de um modelo
        
        Args:
            model_name: Nome do modelo
            model_type: Tipo (regression, classification, portfolio)
            evaluation_results: Resultados da avaliação
            
        Returns:
            Relatório completo
        """
        from datetime import datetime
        
        report = {
            'model_name': model_name,
            'model_type': model_type,
            'evaluation': evaluation_results,
            'evaluated_at': datetime.now().isoformat()
        }
        
        # Adicionar recomendações
        if model_type == 'regression':
            r2 = evaluation_results.get('metrics', {}).get('r2_score', 0)
            quality = evaluation_results.get('quality', 'unknown')
            
            if quality == 'excelente':
                report['recommendation'] = 'Modelo pronto para produção'
            elif quality == 'bom':
                report['recommendation'] = 'Modelo aceitável, considere refinamento'
            else:
                report['recommendation'] = 'Modelo precisa de melhorias significativas'
        
        elif model_type == 'classification':
            accuracy = evaluation_results.get('metrics', {}).get('accuracy', 0)
            
            if accuracy >= 0.8:
                report['recommendation'] = 'Modelo com boa acurácia'
            elif accuracy >= 0.6:
                report['recommendation'] = 'Modelo aceitável, pode ser melhorado'
            else:
                report['recommendation'] = 'Modelo precisa de ajustes'
        
        return report


# ============================================================================
# TESTES
# ============================================================================

if __name__ == '__main__':
    """Testes do avaliador de modelos"""
    
    evaluator = ModelEvaluator()
    
    print("=" * 60)
    print("TESTE DO AVALIADOR DE MODELOS")
    print("=" * 60)
    
    # Teste 1: Avaliação de Regressão
    print("\n1. Avaliação de Modelo de Regressão:")
    
    np.random.seed(42)
    y_true = [30 + i * 0.1 for i in range(50)]
    y_pred = [val + np.random.normal(0, 0.5) for val in y_true]
    
    result = evaluator.evaluate_price_predictor(y_true, y_pred)
    
    print(f"   MAE: {result['metrics']['mae']:.4f}")
    print(f"   RMSE: {result['metrics']['rmse']:.4f}")
    print(f"   R² Score: {result['metrics']['r2_score']:.4f}")
    print(f"   MAPE: {result['metrics']['mape']:.2f}%")
    print(f"   Acurácia Direcional: {result['direction_accuracy']:.2f}%")
    print(f"   Qualidade: {result['quality']}")
    
    # Teste 2: Avaliação de Classificação
    print("\n2. Avaliação de Classificação (Sentimento):")
    
    true_sentiments = ['positive', 'negative', 'neutral', 'positive', 'positive']
    pred_sentiments = ['positive', 'negative', 'positive', 'positive', 'neutral']
    
    result = evaluator.evaluate_sentiment_analyzer(true_sentiments, pred_sentiments)
    
    print(f"   Accuracy: {result['metrics']['accuracy']:.4f}")
    print(f"   Precision: {result['metrics']['precision']:.4f}")
    print(f"   Recall: {result['metrics']['recall']:.4f}")
    print(f"   F1 Score: {result['metrics']['f1_score']:.4f}")
    
    # Teste 3: Relatório Consolidado
    print("\n3. Relatório Consolidado:")
    
    report = evaluator.generate_model_report(
        model_name='PricePredictor_PETR4',
        model_type='regression',
        evaluation_results=result
    )
    
    print(f"   Modelo: {report['model_name']}")
    print(f"   Tipo: {report['model_type']}")
    print(f"   Recomendação: {report.get('recommendation', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)

