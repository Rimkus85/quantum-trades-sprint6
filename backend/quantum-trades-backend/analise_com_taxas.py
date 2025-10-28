"""
Análise de Períodos CHiLo com Taxas Reais da Binance
Magnus Wealth - Versão 8.3.0
Compara períodos considerando custos operacionais
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Taxas Binance Futuros USDⓈ-M (Usuário Regular)
TAXA_TAKER = 0.0005  # 0.05% por operação
TAXA_ROUND_TRIP = 0.001  # 0.10% (entrada + saída)

def calcular_chilo(df, period):
    """Calcula indicador CHiLo"""
    df['hilo_high'] = df['high'].rolling(window=period).mean()
    df['hilo_low'] = df['low'].rolling(window=period).mean()
    
    df['trend'] = 0
    for i in range(period, len(df)):
        if df['close'].iloc[i] > df['hilo_high'].iloc[i]:
            df.loc[df.index[i], 'trend'] = 1  # Bullish
        elif df['close'].iloc[i] < df['hilo_low'].iloc[i]:
            df.loc[df.index[i], 'trend'] = -1  # Bearish
        else:
            df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
    
    return df

def analisar_periodo_com_taxas(symbol, period, days=90):
    """Analisa período com taxas reais"""
    print(f"\n{'='*60}")
    print(f"Analisando {symbol} - CHiLo {period} - Últimos {days} dias")
    print(f"{'='*60}")
    
    # Buscar dados
    ticker = yf.Ticker(symbol)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days+period+10)
    df = ticker.history(start=start_date, end=end_date)
    
    if df.empty:
        print(f"❌ Sem dados para {symbol}")
        return None
    
    # Preparar dados
    df.columns = df.columns.str.lower()
    df = df[['open', 'high', 'low', 'close', 'volume']].copy()
    df = df.dropna()
    
    # Calcular CHiLo
    df = calcular_chilo(df, period)
    df = df.iloc[period:].copy()  # Remover período de warmup
    
    # Limitar aos últimos N dias
    df = df.tail(days)
    
    # Detectar mudanças de tendência (sinais de trade)
    df['signal'] = df['trend'].diff()
    trades = df[df['signal'] != 0].copy()
    num_trades = len(trades)
    
    # Calcular retorno bruto
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['returns'] * df['trend'].shift(1)
    
    retorno_bruto = (1 + df['strategy_returns']).prod() - 1
    
    # Calcular custos
    custo_total = num_trades * TAXA_TAKER
    
    # Retorno líquido
    retorno_liquido = retorno_bruto - custo_total
    
    # Métricas
    trades_por_mes = num_trades / (days / 30)
    custo_anual_estimado = (num_trades / days) * 365 * TAXA_TAKER
    
    # Análise de acurácia
    if num_trades > 0:
        trades['price_entry'] = trades['close']
        trades['price_exit'] = trades['close'].shift(-1)
        trades['trade_return'] = (trades['price_exit'] - trades['price_entry']) / trades['price_entry']
        trades['correct'] = ((trades['signal'] > 0) & (trades['trade_return'] > 0)) | \
                           ((trades['signal'] < 0) & (trades['trade_return'] < 0))
        acuracia = trades['correct'].sum() / len(trades) * 100
    else:
        acuracia = 0
    
    # Volatilidade e Sharpe
    volatilidade = df['strategy_returns'].std() * np.sqrt(252)
    sharpe = (retorno_liquido * (365/days)) / volatilidade if volatilidade > 0 else 0
    
    # Resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   Retorno Bruto:        {retorno_bruto*100:+.2f}%")
    print(f"   Número de Trades:     {num_trades}")
    print(f"   Custo Total:          {custo_total*100:.3f}%")
    print(f"   Retorno Líquido:      {retorno_liquido*100:+.2f}%")
    print(f"\n📈 MÉTRICAS:")
    print(f"   Trades/mês:           {trades_por_mes:.1f}")
    print(f"   Custo anual estimado: {custo_anual_estimado*100:.2f}%")
    print(f"   Acurácia:             {acuracia:.1f}%")
    print(f"   Volatilidade:         {volatilidade*100:.1f}%")
    print(f"   Sharpe Ratio:         {sharpe:.2f}")
    
    return {
        'period': period,
        'retorno_bruto': retorno_bruto,
        'retorno_liquido': retorno_liquido,
        'num_trades': num_trades,
        'custo_total': custo_total,
        'trades_por_mes': trades_por_mes,
        'custo_anual': custo_anual_estimado,
        'acuracia': acuracia,
        'volatilidade': volatilidade,
        'sharpe': sharpe
    }

def comparar_periodos(symbol, period1, period2, days=90):
    """Compara dois períodos"""
    print(f"\n{'#'*60}")
    print(f"COMPARAÇÃO: {symbol}")
    print(f"CHiLo {period1} vs CHiLo {period2}")
    print(f"{'#'*60}")
    
    r1 = analisar_periodo_com_taxas(symbol, period1, days)
    r2 = analisar_periodo_com_taxas(symbol, period2, days)
    
    if r1 and r2:
        print(f"\n{'='*60}")
        print(f"RESUMO COMPARATIVO - Últimos {days} dias")
        print(f"{'='*60}")
        
        print(f"\n{'Métrica':<25} {'CHiLo '+str(period1):>15} {'CHiLo '+str(period2):>15} {'Diferença':>15}")
        print(f"{'-'*70}")
        
        diff_ret = (r2['retorno_liquido'] - r1['retorno_liquido']) * 100
        print(f"{'Retorno Líquido':<25} {r1['retorno_liquido']*100:>14.2f}% {r2['retorno_liquido']*100:>14.2f}% {diff_ret:>+14.2f}%")
        
        diff_trades = r2['num_trades'] - r1['num_trades']
        print(f"{'Número de Trades':<25} {r1['num_trades']:>15} {r2['num_trades']:>15} {diff_trades:>+15}")
        
        diff_custo = (r2['custo_total'] - r1['custo_total']) * 100
        print(f"{'Custo Total':<25} {r1['custo_total']*100:>14.3f}% {r2['custo_total']*100:>14.3f}% {diff_custo:>+14.3f}%")
        
        diff_acur = r2['acuracia'] - r1['acuracia']
        print(f"{'Acurácia':<25} {r1['acuracia']:>14.1f}% {r2['acuracia']:>14.1f}% {diff_acur:>+14.1f}%")
        
        diff_sharpe = r2['sharpe'] - r1['sharpe']
        print(f"{'Sharpe Ratio':<25} {r1['sharpe']:>15.2f} {r2['sharpe']:>15.2f} {diff_sharpe:>+15.2f}")
        
        # Veredito
        print(f"\n{'='*60}")
        print(f"VEREDITO:")
        print(f"{'='*60}")
        
        if r2['retorno_liquido'] > r1['retorno_liquido']:
            melhoria = ((r2['retorno_liquido'] / r1['retorno_liquido']) - 1) * 100 if r1['retorno_liquido'] != 0 else 0
            print(f"✅ CHiLo {period2} é MELHOR (+{diff_ret:.2f}% retorno líquido)")
            if diff_trades > 0:
                print(f"⚠️  Mas requer {diff_trades} trades a mais (+{diff_custo:.3f}% em custos)")
        else:
            piora = ((r1['retorno_liquido'] / r2['retorno_liquido']) - 1) * 100 if r2['retorno_liquido'] != 0 else 0
            print(f"❌ CHiLo {period2} é PIOR ({diff_ret:.2f}% retorno líquido)")
            if diff_trades > 0:
                print(f"⚠️  E ainda requer {diff_trades} trades a mais (+{diff_custo:.3f}% em custos)")
        
        return r1, r2

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ANÁLISE COM TAXAS REAIS DA BINANCE")
    print("Magnus Wealth v8.3.0")
    print("="*60)
    print(f"\nTaxa Taker: {TAXA_TAKER*100}% por operação")
    print(f"Taxa Round-trip: {TAXA_ROUND_TRIP*100}% (entrada + saída)")
    
    # Ethereum: 50 vs 45
    comparar_periodos('ETH-USD', 50, 45, days=90)
    
    # Solana: 45 vs 7
    comparar_periodos('SOL-USD', 45, 7, days=90)
    
    # Algorand: 40 vs 10
    comparar_periodos('ALGO-USD', 40, 10, days=90)
    
    print("\n" + "="*60)
    print("ANÁLISE CONCLUÍDA")
    print("="*60)
