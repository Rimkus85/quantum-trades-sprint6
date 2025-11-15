#!/usr/bin/env python3
"""
Coletor Rápido de Dados para ML - Magnus Wealth v9.0.0

Versão otimizada para produção rápida:
- 2 anos de dados (suficiente para ML)
- Usa períodos do portfolio_config.json (não otimiza)
- Tempo estimado: 10-15 minutos
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
import time

# Importar portfolio manager
from portfolio_manager import PortfolioManager

# Configurações
TIMEFRAMES = {
    '15m': '60d',    # 60 dias de dados de 15 min
    '30m': '60d',    # 60 dias de dados de 30 min
    '1h': '730d',    # 2 anos de dados de 1 hora
    '6h': '730d',    # 2 anos
    '8h': '730d',    # 2 anos
    '12h': '730d',   # 2 anos
    '1d': '730d'     # 2 anos de dados diários
}

def calcular_chilo(df, period):
    """
    Calcula CHiLo (Custom HiLo)
    """
    # Médias móveis
    hima = df['High'].rolling(window=period).mean()
    loma = df['Low'].rolling(window=period).mean()
    
    # CHiLo
    chilo = pd.Series(index=df.index, dtype=float)
    trend = pd.Series(index=df.index, dtype=int)
    
    for i in range(period, len(df)):
        if df['Close'].iloc[i] > hima.iloc[i-1]:
            chilo.iloc[i] = loma.iloc[i]
            trend.iloc[i] = 1  # Verde
        elif df['Close'].iloc[i] < loma.iloc[i-1]:
            chilo.iloc[i] = hima.iloc[i]
            trend.iloc[i] = 0  # Vermelho
        else:
            chilo.iloc[i] = chilo.iloc[i-1]
            trend.iloc[i] = trend.iloc[i-1]
    
    return chilo, trend

def contar_candles_virados(trend):
    """
    Conta quantos candles consecutivos na mesma direção
    """
    if len(trend) == 0 or pd.isna(trend.iloc[-1]):
        return 0
    
    estado_atual = trend.iloc[-1]
    count = 0
    
    for i in range(len(trend)-1, -1, -1):
        if pd.isna(trend.iloc[i]):
            break
        if trend.iloc[i] == estado_atual:
            count += 1
        else:
            break
    
    return count

def coletar_dados_cripto(cripto, timeframes_config):
    """
    Coleta dados de uma criptomoeda em múltiplos timeframes
    """
    print(f"\n{'='*80}")
    print(f"🪙 {cripto['name']} ({cripto['yahoo']})")
    print(f"{'='*80}")
    
    dados_cripto = []
    period_chilo = cripto['period_chilo']
    
    # Coletar dados diários (referência)
    print(f"\n📊 Coletando dados diários...")
    try:
        ticker = yf.Ticker(cripto['yahoo'])
        df_daily = ticker.history(period='730d', interval='1d')
        
        if df_daily.empty:
            print(f"❌ Sem dados para {cripto['name']}")
            return []
        
        print(f"✅ {len(df_daily)} candles diários coletados")
        
        # Calcular CHiLo diário
        chilo_daily, trend_daily = calcular_chilo(df_daily, period_chilo)
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados diários: {e}")
        return []
    
    # Coletar dados de outros timeframes
    dados_timeframes = {}
    
    for tf, period in timeframes_config.items():
        if tf == '1d':
            continue  # Já coletamos
        
        print(f"\n📈 Timeframe {tf}...")
        try:
            df_tf = ticker.history(period=period, interval=tf)
            
            if df_tf.empty:
                print(f"⚠️  Sem dados para {tf}")
                continue
            
            # Calcular CHiLo
            chilo_tf, trend_tf = calcular_chilo(df_tf, period_chilo)
            
            # Guardar último estado e candles virados
            if len(trend_tf) > 0 and not pd.isna(trend_tf.iloc[-1]):
                estado = int(trend_tf.iloc[-1])
                candles_virados = contar_candles_virados(trend_tf)
                dados_timeframes[tf] = {
                    'estado': estado,
                    'candles_virados': candles_virados
                }
                print(f"✅ Estado: {'🟢' if estado == 1 else '🔴'}, Virados: {candles_virados}")
            else:
                print(f"⚠️  Dados insuficientes")
                
        except Exception as e:
            print(f"❌ Erro em {tf}: {e}")
    
    # Gerar amostras de treinamento
    print(f"\n🔄 Gerando amostras de treinamento...")
    
    # Para cada dia, verificar se houve inversão
    for i in range(period_chilo + 1, len(df_daily)):
        # Verificar se houve inversão no dia seguinte
        if i + 1 < len(df_daily):
            trend_hoje = trend_daily.iloc[i]
            trend_amanha = trend_daily.iloc[i + 1]
            
            if pd.isna(trend_hoje) or pd.isna(trend_amanha):
                continue
            
            inverteu = 1 if trend_hoje != trend_amanha else 0
            
            # Criar amostra com estados dos timeframes
            amostra = {
                'cripto': cripto['name'],
                'data': df_daily.index[i].strftime('%Y-%m-%d'),
                'inverteu_proximo_dia': inverteu
            }
            
            # Adicionar estados dos timeframes (simulado com dados diários)
            # Em produção real, isso viria dos dados de cada timeframe
            for tf in ['15m', '30m', '1h', '6h', '8h', '12h']:
                if tf in dados_timeframes:
                    amostra[f'{tf}_estado'] = dados_timeframes[tf]['estado']
                    amostra[f'{tf}_candles_virados'] = dados_timeframes[tf]['candles_virados']
                else:
                    amostra[f'{tf}_estado'] = int(trend_hoje)
                    amostra[f'{tf}_candles_virados'] = contar_candles_virados(trend_daily.iloc[:i+1])
            
            dados_cripto.append(amostra)
    
    print(f"\n✅ {len(dados_cripto)} amostras geradas para {cripto['name']}")
    
    return dados_cripto

def main():
    """
    Função principal
    """
    print("="*80)
    print("COLETOR RÁPIDO DE DADOS ML - MAGNUS WEALTH v9.0.0")
    print("="*80)
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    inicio = time.time()
    
    # Carregar portfólio
    print("📦 Carregando portfólio...")
    manager = PortfolioManager()
    criptos = manager.obter_criptos_ativas()
    print(f"✅ {len(criptos)} criptomoedas ativas")
    
    # Coletar dados de todas as criptos
    todos_dados = []
    
    for i, cripto in enumerate(criptos, 1):
        print(f"\n\n{'#'*80}")
        print(f"# CRIPTO {i}/{len(criptos)}")
        print(f"{'#'*80}")
        
        dados_cripto = coletar_dados_cripto(cripto, TIMEFRAMES)
        todos_dados.extend(dados_cripto)
        
        # Delay para evitar rate limit
        if i < len(criptos):
            print(f"\n⏳ Aguardando 2 segundos...")
            time.sleep(2)
    
    # Salvar dataset
    print(f"\n\n{'='*80}")
    print("💾 SALVANDO DATASET")
    print(f"{'='*80}")
    
    df_final = pd.DataFrame(todos_dados)
    
    # Criar diretório se não existir
    output_dir = Path('ml_data_8anos')
    output_dir.mkdir(exist_ok=True)
    
    # Salvar CSV
    output_file = output_dir / 'dataset_inversao_completo.csv'
    df_final.to_csv(output_file, index=False)
    
    print(f"\n✅ Dataset salvo: {output_file}")
    print(f"📊 Total de amostras: {len(df_final)}")
    print(f"🪙 Criptomoedas: {df_final['cripto'].nunique()}")
    
    # Estatísticas
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   - Inversões: {df_final['inverteu_proximo_dia'].sum()} ({df_final['inverteu_proximo_dia'].mean()*100:.1f}%)")
    print(f"   - Não inversões: {(1-df_final['inverteu_proximo_dia']).sum()} ({(1-df_final['inverteu_proximo_dia'].mean())*100:.1f}%)")
    
    # Amostras por cripto
    print(f"\n🪙 AMOSTRAS POR CRIPTO:")
    for cripto in df_final['cripto'].unique():
        count = len(df_final[df_final['cripto'] == cripto])
        print(f"   - {cripto}: {count}")
    
    # Tempo total
    tempo_total = time.time() - inicio
    print(f"\n⏱️  TEMPO TOTAL: {tempo_total/60:.1f} minutos")
    print(f"✅ COLETA CONCLUÍDA COM SUCESSO!")
    print("="*80)

if __name__ == '__main__':
    main()
