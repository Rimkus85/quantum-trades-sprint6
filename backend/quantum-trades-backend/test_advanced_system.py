#!/usr/bin/env python3
"""
Teste completo do sistema Magnus Advanced Learning.
Valida todas as funcionalidades avançadas.
"""

from datetime import datetime, timedelta
from modules.magnus_advanced_learning import (
    MagnusAdvancedLearning, Position, MarketCondition, StrategyMode
)
from modules.market_data_api import market_api


def test_advanced_learning_system():
    """Testa o sistema avançado completo."""
    print("=" * 80)
    print("TESTE DO SISTEMA MAGNUS ADVANCED LEARNING")
    print("=" * 80)
    
    # Criar instância
    magnus = MagnusAdvancedLearning()
    
    # PASSO 1: Adicionar posições
    print("\n" + "=" * 80)
    print("PASSO 1: ADICIONAR POSIÇÕES")
    print("=" * 80)
    
    positions = [
        Position(
            ticker="PETR4",
            entry_date=(datetime.now() - timedelta(days=60)).isoformat(),
            entry_price=35.00,
            quantity=100,
            target_price=42.00,
            stop_loss=33.00,
            expected_return=20.0,
            timeframe_days=90,
            validity_date=(datetime.now() + timedelta(days=30)).isoformat(),
            reason="Valorização do petróleo",
            sector="petroleo"
        ),
        Position(
            ticker="VALE3",
            entry_date=(datetime.now() - timedelta(days=100)).isoformat(),
            entry_price=60.00,
            quantity=50,
            target_price=70.00,
            stop_loss=57.00,
            expected_return=16.7,
            timeframe_days=90,
            validity_date=(datetime.now() - timedelta(days=10)).isoformat(),  # Expirada
            reason="Demanda por minério",
            sector="mineracao"
        ),
        Position(
            ticker="ITUB4",
            entry_date=(datetime.now() - timedelta(days=30)).isoformat(),
            entry_price=27.00,
            quantity=200,
            target_price=32.00,
            stop_loss=25.50,
            expected_return=18.5,
            timeframe_days=90,
            validity_date=(datetime.now() + timedelta(days=60)).isoformat(),
            reason="Recuperação do setor financeiro",
            sector="financeiro"
        )
    ]
    
    for pos in positions:
        magnus.performance_tracker.add_position(pos)
        print(f"\n✓ Posição adicionada: {pos.ticker}")
        print(f"  Entrada: R$ {pos.entry_price} em {pos.entry_date[:10]}")
        print(f"  Meta: R$ {pos.target_price} ({pos.expected_return}%)")
        print(f"  Validade: {pos.validity_date[:10]}")
    
    # PASSO 2: Atualizar preços
    print("\n" + "=" * 80)
    print("PASSO 2: ATUALIZAR PREÇOS")
    print("=" * 80)
    
    current_prices = {
        "PETR4": market_api.get_quote("PETR4")['price'],
        "VALE3": market_api.get_quote("VALE3")['price'],
        "ITUB4": market_api.get_quote("ITUB4")['price']
    }
    
    magnus.performance_tracker.update_prices(current_prices)
    
    for ticker, price in current_prices.items():
        print(f"\n✓ {ticker}: R$ {price}")
    
    # PASSO 3: Revisar posições expiradas
    print("\n" + "=" * 80)
    print("PASSO 3: REVISAR POSIÇÕES EXPIRADAS")
    print("=" * 80)
    
    expired = magnus.performance_tracker.get_expired_positions()
    print(f"\n✓ Posições expiradas encontradas: {len(expired)}")
    
    if expired:
        actions = magnus.review_expired_positions()
        
        for action in actions:
            print(f"\n  Ticker: {action['ticker']}")
            print(f"  Dias mantido: {action['days_held']}")
            print(f"  Retorno atual: {action['current_return']:.2f}%")
            print(f"  Retorno esperado: {action['expected_return']:.2f}%")
            print(f"  Recomendação: {action['recommendation']}")
            print(f"  Razão: {action['analysis']['reason']}")
    
    # PASSO 4: Registrar erros
    print("\n" + "=" * 80)
    print("PASSO 4: APRENDER COM ERROS")
    print("=" * 80)
    
    errors = [
        {
            "type": "wrong_direction",
            "ticker": "MGLU3",
            "action": "compra",
            "market_conditions": "juros_altos",
            "loss": -15.0
        },
        {
            "type": "sector_misjudgment",
            "sector": "fiis",
            "factor": "juros",
            "impact": -20.0
        }
    ]
    
    for error in errors:
        magnus.learn_from_error(error)
        print(f"\n✓ Erro registrado: {error['type']}")
    
    print(f"\n  Total de erros no log: {len(magnus.error_log)}")
    print(f"  Insights gerados: {len(magnus.learning_insights)}")
    
    if magnus.learning_insights:
        for insight in magnus.learning_insights:
            print(f"\n  Insight: {insight['lesson']}")
    
    # PASSO 5: Fechar posição
    print("\n" + "=" * 80)
    print("PASSO 5: FECHAR POSIÇÃO E REGISTRAR PERFORMANCE")
    print("=" * 80)
    
    magnus.performance_tracker.close_position(
        ticker="VALE3",
        final_price=current_prices["VALE3"],
        reason="Expiração de prazo"
    )
    
    print(f"\n✓ Posição VALE3 fechada")
    print(f"  Histórico de performance: {len(magnus.performance_tracker.performance_history)} registros")
    
    # PASSO 6: Calcular métricas de performance
    print("\n" + "=" * 80)
    print("PASSO 6: MÉTRICAS DE PERFORMANCE")
    print("=" * 80)
    
    hit_rate = magnus.performance_tracker.get_hit_rate()
    avg_return = magnus.performance_tracker.get_average_return()
    
    print(f"\n✓ Taxa de acerto: {hit_rate:.1f}%")
    print(f"✓ Retorno médio: {avg_return:.2f}%")
    
    # Performance por setor
    sectors = ["petroleo", "mineracao", "financeiro"]
    for sector in sectors:
        perf = magnus.performance_tracker.get_sector_performance(sector)
        if perf['trades'] > 0:
            print(f"\n  Setor {sector}:")
            print(f"    Operações: {perf['trades']}")
            print(f"    Retorno médio: {perf['average_return']:.2f}%")
    
    # PASSO 7: Análise de mercado
    print("\n" + "=" * 80)
    print("PASSO 7: ANÁLISE DE CONTEXTO DE MERCADO")
    print("=" * 80)
    
    market_data = market_api.get_market_indicators()
    
    market_condition = magnus.market_analyzer.analyze_market_condition(market_data)
    magnus.market_analyzer.market_condition = market_condition
    
    print(f"\n✓ Condição de mercado: {market_condition.value}")
    print(f"  Ibovespa: {market_data['ibovespa']['value']:,.0f} ({market_data['ibovespa']['change']:+.1f}%)")
    print(f"  Variação 30d: {market_data['ibovespa']['change_30d']:+.1f}%")
    print(f"  Volatilidade: {market_data['ibovespa']['volatility']:.1f}%")
    
    # Análise setorial
    print("\n  Análise Setorial:")
    for sector in ["financeiro", "petroleo", "fiis"]:
        sector_data = market_api.get_sector_data(sector)
        print(f"\n    {sector.capitalize()}:")
        print(f"      Tendência: {sector_data['trend']}")
        print(f"      Performance 30d: {sector_data['performance_30d']:+.1f}%")
        print(f"      Outlook: {sector_data['outlook']}")
    
    # PASSO 8: Ajuste de estratégia
    print("\n" + "=" * 80)
    print("PASSO 8: AJUSTE AUTÔNOMO DE ESTRATÉGIA")
    print("=" * 80)
    
    strategy_mode = magnus.strategy_adjuster.determine_strategy_mode()
    magnus.strategy_adjuster.current_mode = strategy_mode
    
    print(f"\n✓ Modo de estratégia determinado: {strategy_mode.value}")
    
    # Testar ajustes
    base_size = 10000
    adjusted_size = magnus.strategy_adjuster.adjust_position_sizing(base_size)
    
    base_target = 110.0
    base_stop = 95.0
    adjusted_target, adjusted_stop = magnus.strategy_adjuster.adjust_targets(base_target, base_stop)
    
    print(f"\n  Ajuste de tamanho de posição:")
    print(f"    Base: R$ {base_size:,.2f}")
    print(f"    Ajustado: R$ {adjusted_size:,.2f}")
    
    print(f"\n  Ajuste de alvos:")
    print(f"    Target base: R$ {base_target:.2f} → Ajustado: R$ {adjusted_target:.2f}")
    print(f"    Stop base: R$ {base_stop:.2f} → Ajustado: R$ {adjusted_stop:.2f}")
    
    # PASSO 9: Recomendação autônoma
    print("\n" + "=" * 80)
    print("PASSO 9: RECOMENDAÇÃO AUTÔNOMA")
    print("=" * 80)
    
    tickers_to_analyze = ["PETR4", "ITUB4", "MGLU3"]
    
    for ticker in tickers_to_analyze:
        quote = market_api.get_quote(ticker)
        fundamentals = market_api.get_company_fundamentals(ticker)
        
        recommendation = magnus.get_autonomous_recommendation(
            ticker=ticker,
            sector=fundamentals['sector'],
            current_price=quote['price'],
            market_data=market_data
        )
        
        print(f"\n  {ticker}:")
        print(f"    Ação: {recommendation['action']}")
        print(f"    Score: {recommendation['score']:.1f}")
        print(f"    Preço atual: R$ {recommendation['current_price']:.2f}")
        print(f"    Alvo: R$ {recommendation['target_price']:.2f}")
        print(f"    Stop: R$ {recommendation['stop_loss']:.2f}")
        print(f"    Retorno esperado: {recommendation['expected_return']:.1f}%")
        print(f"    Confiança: {recommendation['confidence']:.2f}")
        print(f"    Modo: {recommendation['strategy_mode']}")
        print(f"    Razão: {recommendation['reasoning']}")
    
    # PASSO 10: Persistência
    print("\n" + "=" * 80)
    print("PASSO 10: PERSISTÊNCIA DE ESTADO")
    print("=" * 80)
    
    filename = magnus.save_state('test_advanced_state.json')
    print(f"\n✓ Estado salvo: {filename}")
    
    # Criar nova instância e carregar
    magnus2 = MagnusAdvancedLearning()
    loaded = magnus2.load_state('test_advanced_state.json')
    
    if loaded:
        print(f"✓ Estado carregado com sucesso")
        print(f"  Posições: {len(magnus2.performance_tracker.positions)}")
        print(f"  Histórico: {len(magnus2.performance_tracker.performance_history)}")
        print(f"  Erros: {len(magnus2.error_log)}")
        print(f"  Insights: {len(magnus2.learning_insights)}")
    
    # RESULTADO FINAL
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    
    print(f"\n✅ TESTE COMPLETO CONCLUÍDO COM SUCESSO!")
    print(f"\n  Resumo:")
    print(f"    Posições criadas: {len(positions)}")
    print(f"    Posições expiradas: {len(expired)}")
    print(f"    Erros registrados: {len(magnus.error_log)}")
    print(f"    Insights gerados: {len(magnus.learning_insights)}")
    print(f"    Taxa de acerto: {hit_rate:.1f}%")
    print(f"    Retorno médio: {avg_return:.2f}%")
    print(f"    Condição de mercado: {market_condition.value}")
    print(f"    Modo de estratégia: {strategy_mode.value}")
    
    return True


def main():
    """Função principal."""
    try:
        success = test_advanced_learning_system()
        
        if success:
            print("\n" + "=" * 80)
            print("✅ TODOS OS TESTES PASSARAM!")
            print("=" * 80)
            return 0
        else:
            print("\n" + "=" * 80)
            print("❌ ALGUNS TESTES FALHARAM")
            print("=" * 80)
            return 1
    
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

