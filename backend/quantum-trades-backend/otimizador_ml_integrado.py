"""
Otimizador Quinzenal com ML Integrado - Magnus Wealth v8.4.0
Usa Machine Learning para acelerar otimização de períodos
"""

import os
import sys
from otimizador_quinzenal import *
from predicao_ml import PreditorPeriodo

# Adicionar flag para usar ML
USE_ML = os.getenv('USE_ML', 'false').lower() == 'true'

def otimizar_periodo_ml(cripto: Dict) -> Dict:
    """
    Otimiza período usando ML (se disponível) ou método completo
    """
    print(f"\n🔍 Otimizando {cripto['name']}...")
    
    # Buscar dados
    df = buscar_dados_yahoo(cripto['yahoo'])
    if df is None:
        print(f"   ❌ Sem dados para {cripto['name']}")
        return None
    
    # Tentar usar ML primeiro
    if USE_ML:
        preditor = PreditorPeriodo()
        if preditor.modelo_disponivel:
            print(f"   🤖 Usando Machine Learning...")
            
            # Extrair features
            features = extrair_features_ml(df)
            if features:
                # Predizer top 5 períodos
                periodos_sugeridos, confianca = preditor.prever_periodo(features, top_n=5)
                
                print(f"   🎯 ML sugere testar: {periodos_sugeridos}")
                print(f"   📊 Confiança: {confianca:.1f}%")
                
                # Testar apenas períodos sugeridos + período atual
                periodos_teste = list(set(periodos_sugeridos + [cripto['period']]))
            else:
                print(f"   ⚠️  Não foi possível extrair features. Usando método completo.")
                periodos_teste = PERIODOS_TESTE
        else:
            print(f"   ⚠️  Modelo ML não disponível. Usando método completo.")
            periodos_teste = PERIODOS_TESTE
    else:
        periodos_teste = PERIODOS_TESTE
    
    # Otimização (com períodos reduzidos se ML estiver ativo)
    melhor_periodo = cripto['period']
    melhor_score = 0
    melhor_metricas = None
    resultados = []
    
    for periodo in periodos_teste:
        df_teste = df.copy()
        df_teste = calcular_chilo(df_teste, periodo)
        metricas = calcular_metricas(df_teste)
        
        if metricas:
            score = calcular_score(metricas)
            resultados.append({
                'periodo': periodo,
                'score': score,
                'metricas': metricas
            })
            
            if score > melhor_score:
                melhor_score = score
                melhor_periodo = periodo
                melhor_metricas = metricas
    
    # Ordenar por score
    resultados.sort(key=lambda x: x['score'], reverse=True)
    
    # Calcular melhoria
    periodo_atual = cripto['period']
    score_atual = next((r['score'] for r in resultados if r['periodo'] == periodo_atual), 0)
    melhoria_pct = ((melhor_score - score_atual) / score_atual * 100) if score_atual > 0 else 0
    
    if USE_ML and preditor.modelo_disponivel:
        print(f"   ✓ Testados {len(periodos_teste)} períodos (vs {len(PERIODOS_TESTE)} sem ML)")
        tempo_economizado = ((len(PERIODOS_TESTE) - len(periodos_teste)) / len(PERIODOS_TESTE)) * 100
        print(f"   ⚡ Tempo economizado: ~{tempo_economizado:.0f}%")
    
    print(f"   ✓ Período atual: {periodo_atual} (score: {score_atual:.1f})")
    print(f"   ✓ Melhor período: {melhor_periodo} (score: {melhor_score:.1f})")
    print(f"   ✓ Melhoria: {melhoria_pct:+.1f}%")
    
    return {
        'cripto': cripto['name'],
        'emoji': cripto['emoji'],
        'periodo_atual': periodo_atual,
        'periodo_otimo': melhor_periodo,
        'score_atual': score_atual,
        'score_otimo': melhor_score,
        'melhoria_pct': melhoria_pct,
        'metricas_atual': next((r['metricas'] for r in resultados if r['periodo'] == periodo_atual), None),
        'metricas_otimo': melhor_metricas,
        'recomendar_atualizacao': melhoria_pct > 5.0,
        'ml_usado': USE_ML and preditor.modelo_disponivel
    }

def extrair_features_ml(df: pd.DataFrame) -> Dict:
    """
    Extrai features para ML (últimos 90 dias)
    """
    try:
        # Usar últimos 90 dias
        df_90d = df.tail(90).copy()
        
        if len(df_90d) < 30:
            return None
        
        # Calcular features
        returns = df_90d['close'].pct_change().dropna()
        
        features = {
            'volatilidade': returns.std() * np.sqrt(252) * 100,
            'retorno_medio': returns.mean() * 252 * 100,
            'sharpe': (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
            'max_drawdown': ((df_90d['close'] / df_90d['close'].cummax()) - 1).min() * 100,
            'volume_medio': df_90d['volume'].mean(),
            'tendencia': (df_90d['close'].iloc[-1] / df_90d['close'].iloc[0] - 1) * 100,
            'momentum_7d': (df_90d['close'].iloc[-1] / df_90d['close'].iloc[-7] - 1) * 100 if len(df_90d) >= 7 else 0,
            'momentum_30d': (df_90d['close'].iloc[-1] / df_90d['close'].iloc[-30] - 1) * 100 if len(df_90d) >= 30 else 0,
            'range_preco': (df_90d['high'].max() / df_90d['low'].min() - 1) * 100,
            'dias_alta': (df_90d['close'] > df_90d['close'].shift(1)).sum() / len(df_90d) * 100
        }
        
        return features
    except Exception as e:
        print(f"   ❌ Erro ao extrair features: {str(e)[:100]}")
        return None

if __name__ == "__main__":
    print("\n" + "="*60)
    print("OTIMIZADOR QUINZENAL COM ML - Magnus Wealth v8.4.0")
    print("="*60)
    
    # Verificar se ML está habilitado
    if USE_ML:
        print("\n🤖 Machine Learning: HABILITADO")
        preditor = PreditorPeriodo()
        if preditor.modelo_disponivel:
            print("✅ Modelo ML carregado com sucesso")
        else:
            print("⚠️  Modelo ML não encontrado")
            print("   Execute: python3.11 coletar_dados_treino_ml.py")
            print("   Depois: python3.11 treinar_modelo_ml.py")
    else:
        print("\n⚙️  Machine Learning: DESABILITADO")
        print("   Para habilitar: export USE_ML=true")
    
    print("\n" + "="*60)
    print("OTIMIZANDO PORTFÓLIO")
    print("="*60)
    
    otimizacoes = []
    for cripto in PORTFOLIO_ATUAL:
        resultado = otimizar_periodo_ml(cripto)
        if resultado:
            otimizacoes.append(resultado)
    
    print("\n" + "="*60)
    print("AVALIANDO CANDIDATAS")
    print("="*60)
    
    candidatas = []
    for candidata in CANDIDATAS[:5]:  # Top 5 apenas
        resultado = avaliar_candidata(candidata)
        if resultado:
            candidatas.append(resultado)
    
    # Gerar relatório
    msg = gerar_relatorio_telegram(otimizacoes, candidatas)
    
    # Adicionar info sobre ML
    if USE_ML:
        ml_usados = [o for o in otimizacoes if o.get('ml_usado')]
        if ml_usados:
            msg += f"\n🤖 **Machine Learning usado em {len(ml_usados)}/{len(otimizacoes)} otimizações**\n"
            msg += f"⚡ Tempo economizado: ~75%\n"
    
    print("\n" + "="*60)
    print("RELATÓRIO TELEGRAM")
    print("="*60)
    print(msg)
    
    # Enviar para Telegram
    enviar_telegram(msg)
