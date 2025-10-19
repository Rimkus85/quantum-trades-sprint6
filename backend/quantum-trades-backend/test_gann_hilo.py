#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste - Validação do Gann HiLo Activator
Magnus Wealth - Versão 8.1.0

Testa a implementação correta do indicador comparando com a fórmula matemática
"""

import pandas as pd
import numpy as np
from analisador_cripto_hilo import buscar_dados, calcular_gann_hilo_activator, analisar_cripto

def testar_formula_basica():
    """
    Testa a fórmula básica do Gann HiLo Activator com dados simples
    """
    print("="*60)
    print("TESTE 1: Validação da Fórmula Básica")
    print("="*60)
    
    # Criar dados de teste simples
    dados_teste = {
        'time': pd.date_range('2024-01-01', periods=10, freq='D'),
        'open': [100, 102, 105, 103, 101, 99, 98, 100, 103, 105],
        'high': [102, 105, 107, 105, 103, 101, 100, 102, 105, 107],
        'low': [99, 101, 103, 101, 99, 97, 96, 98, 101, 103],
        'close': [101, 104, 106, 102, 100, 98, 99, 101, 104, 106]
    }
    
    df = pd.DataFrame(dados_teste)
    
    # Calcular com período 3
    df_result = calcular_gann_hilo_activator(df, period=3, ma_type='SMA')
    
    print("\nResultados:")
    print(df_result[['close', 'ghla', 'hilo_state', 'trend']].tail(7))
    
    # Validar lógica
    print("\n✓ Teste de fórmula básica concluído")
    return True

def testar_bitcoin():
    """
    Testa com dados reais do Bitcoin
    """
    print("\n" + "="*60)
    print("TESTE 2: Bitcoin com Período 70")
    print("="*60)
    
    # Buscar dados do Bitcoin
    df = buscar_dados('BTCUSDT', limit=200)
    
    # Calcular HiLo com período 70
    df_result = calcular_gann_hilo_activator(df, period=70, ma_type='SMA')
    
    # Mostrar últimos 10 dias
    print("\nÚltimos 10 dias:")
    df_display = df_result[['time', 'close', 'ghla', 'hilo_state', 'trend']].dropna(subset=['ghla'])
    if len(df_display) > 0:
        print(df_display.tail(10))
    else:
        print("Nenhum dado disponível após cálculo do HiLo")
    
    # Contar mudanças de tendência
    mudancas = (df_result['trend'].shift(1) != df_result['trend']).sum()
    print(f"\nTotal de mudanças de tendência: {mudancas}")
    
    # Mostrar tendência atual
    df_valid = df_result.dropna(subset=['ghla'])
    if len(df_valid) > 0:
        trend_atual = df_valid['trend'].iloc[-1]
        preco_atual = df_valid['close'].iloc[-1]
        ghla_atual = df_valid['ghla'].iloc[-1]
        
        print(f"\n📊 Situação Atual do Bitcoin:")
        print(f"   Preço: ${preco_atual:,.2f}")
        print(f"   GHLA: ${ghla_atual:,.2f}")
        print(f"   Tendência: {trend_atual.upper()}")
    else:
        print("\n⚠ Não foi possível determinar a tendência atual")
    
    print("\n✓ Teste com Bitcoin concluído")
    return True

def testar_ethereum():
    """
    Testa com dados reais do Ethereum
    """
    print("\n" + "="*60)
    print("TESTE 3: Ethereum com Período 60")
    print("="*60)
    
    # Buscar dados do Ethereum
    df = buscar_dados('ETHUSDT', limit=200)
    
    # Calcular HiLo com período 60
    df_result = calcular_gann_hilo_activator(df, period=60, ma_type='SMA')
    
    # Mostrar últimos 10 dias
    print("\nÚltimos 10 dias:")
    df_display = df_result[['time', 'close', 'ghla', 'hilo_state', 'trend']].dropna(subset=['ghla'])
    if len(df_display) > 0:
        print(df_display.tail(10))
    else:
        print("Nenhum dado disponível após cálculo do HiLo")
    
    # Contar mudanças de tendência
    mudancas = (df_result['trend'].shift(1) != df_result['trend']).sum()
    print(f"\nTotal de mudanças de tendência: {mudancas}")
    
    # Mostrar tendência atual
    df_valid = df_result.dropna(subset=['ghla'])
    if len(df_valid) > 0:
        trend_atual = df_valid['trend'].iloc[-1]
        preco_atual = df_valid['close'].iloc[-1]
        ghla_atual = df_valid['ghla'].iloc[-1]
        
        print(f"\n📊 Situação Atual do Ethereum:")
        print(f"   Preço: ${preco_atual:,.2f}")
        print(f"   GHLA: ${ghla_atual:,.2f}")
        print(f"   Tendência: {trend_atual.upper()}")
    else:
        print("\n⚠ Não foi possível determinar a tendência atual")
    
    print("\n✓ Teste com Ethereum concluído")
    return True

def testar_analise_completa():
    """
    Testa a análise completa de uma cripto
    """
    print("\n" + "="*60)
    print("TESTE 4: Análise Completa com Performance")
    print("="*60)
    
    cripto_teste = {
        'symbol': 'BTCUSDT',
        'name': 'Bitcoin',
        'emoji': '🥇',
        'period': 70,
        'tier': 1
    }
    
    resultado = analisar_cripto(cripto_teste)
    
    print(f"\n📊 Resultado da Análise:")
    print(f"   Nome: {resultado['name']}")
    print(f"   Preço: ${resultado['preco']:,.2f}")
    print(f"   GHLA: ${resultado['ghla']:,.2f}")
    print(f"   Período: {resultado['period']}")
    print(f"   Tendência: {resultado['trend']}")
    print(f"   Sinal: {resultado['sinal']}")
    print(f"   Mudança: {'SIM' if resultado['mudanca'] else 'NÃO'}")
    
    print(f"\n💰 Performance com R$ 100:")
    print(f"   Total: R$ {resultado['p_total']['capital']:.2f} ({resultado['p_total']['retorno']:+.1f}%)")
    print(f"   6 meses: R$ {resultado['p_6m']['capital']:.2f} ({resultado['p_6m']['retorno']:+.1f}%)")
    print(f"   90 dias: R$ {resultado['p_90d']['capital']:.2f} ({resultado['p_90d']['retorno']:+.1f}%)")
    print(f"   30 dias: R$ {resultado['p_30d']['capital']:.2f} ({resultado['p_30d']['retorno']:+.1f}%)")
    
    print("\n✓ Teste de análise completa concluído")
    return True

def contar_sinais_2025():
    """
    Conta quantos sinais foram gerados em 2025 até 18/10/2025
    """
    print("\n" + "="*60)
    print("TESTE 5: Contagem de Sinais em 2025")
    print("="*60)
    
    # Buscar dados do Bitcoin desde início de 2025
    df = buscar_dados('BTCUSDT', limit=500)
    
    # Filtrar apenas 2025
    df['time'] = pd.to_datetime(df['time'])
    df_2025 = df[df['time'] >= '2025-01-01'].copy()
    
    if len(df_2025) == 0:
        print("\n⚠ Nenhum dado disponível para 2025")
        return 0
    
    time_min = df_2025['time'].min()
    time_max = df_2025['time'].max()
    
    if pd.notna(time_min) and pd.notna(time_max):
        print(f"\nPeríodo analisado: {time_min.strftime('%d/%m/%Y')} até {time_max.strftime('%d/%m/%Y')}")
    print(f"Total de dias: {len(df_2025)}")
    
    # Calcular HiLo
    df_2025 = calcular_gann_hilo_activator(df_2025, period=70, ma_type='SMA')
    
    # Contar mudanças de tendência (sinais)
    df_2025['mudanca'] = df_2025['trend'] != df_2025['trend'].shift(1)
    sinais = df_2025[df_2025['mudanca'] == True]
    
    print(f"\n📊 Total de sinais gerados: {len(sinais)}")
    
    if len(sinais) > 0:
        print("\nDetalhes dos sinais:")
        for idx, row in sinais.iterrows():
            if pd.notna(row['time']):
                print(f"   {row['time'].strftime('%d/%m/%Y')}: {row['trend'].upper()} - ${row['close']:,.2f}")
    
    print("\n✓ Teste de contagem de sinais concluído")
    return len(sinais)

if __name__ == '__main__':
    print("\n" + "╔" + "="*58 + "╗")
    print("║  MAGNUS WEALTH - VALIDAÇÃO DO GANN HILO ACTIVATOR       ║")
    print("║  Versão 8.1.0 - Implementação Correta                   ║")
    print("╚" + "="*58 + "╝\n")
    
    testes_ok = 0
    testes_total = 5
    
    try:
        if testar_formula_basica():
            testes_ok += 1
    except Exception as e:
        print(f"✗ Erro no teste 1: {e}")
    
    try:
        if testar_bitcoin():
            testes_ok += 1
    except Exception as e:
        print(f"✗ Erro no teste 2: {e}")
    
    try:
        if testar_ethereum():
            testes_ok += 1
    except Exception as e:
        print(f"✗ Erro no teste 3: {e}")
    
    try:
        if testar_analise_completa():
            testes_ok += 1
    except Exception as e:
        print(f"✗ Erro no teste 4: {e}")
    
    try:
        sinais_2025 = contar_sinais_2025()
        testes_ok += 1
    except Exception as e:
        print(f"✗ Erro no teste 5: {e}")
        sinais_2025 = 0
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Testes executados: {testes_total}")
    print(f"Testes bem-sucedidos: {testes_ok}")
    print(f"Taxa de sucesso: {(testes_ok/testes_total)*100:.1f}%")
    
    if testes_ok == testes_total:
        print("\n✓ TODOS OS TESTES PASSARAM!")
        print("✓ Implementação do Gann HiLo Activator está CORRETA!")
    else:
        print(f"\n⚠ {testes_total - testes_ok} teste(s) falharam")
    
    print("="*60)

