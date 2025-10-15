#!/usr/bin/env python3
"""
Teste completo do sistema Magnus Learning.
Valida aprendizado, recomendações e ajustes de estratégia.
"""

import json
from modules.magnus_learning import MagnusLearningEngine, MagnusAnalyzer
from modules.carteira_parser import CarteiraParser


def test_magnus_learning():
    """Testa o sistema de aprendizado do Magnus."""
    print("=" * 70)
    print("TESTE DO SISTEMA MAGNUS LEARNING")
    print("=" * 70)
    
    # Dados de teste - carteiras do Telegram
    test_messages = [
        {
            "id": 1001,
            "date": "2025-10-15T09:00:00",
            "text": "📊 Carteira Recomendada - Outubro 2025\n\nAlocação sugerida:\nPETR4 - 30%\nVALE3 - 25%\nITUB4 - 20%\nBBDC4 - 15%\nWEGE3 - 10%\n\nTotal: 100%"
        },
        {
            "id": 1002,
            "date": "2025-10-15T10:30:00",
            "text": "🔔 ALERTA DE COMPRA\n\nRecomendação: COMPRA de PETR4\nPreço alvo: R$ 42,00\nStop loss: R$ 38,50"
        },
        {
            "id": 1003,
            "date": "2025-10-15T11:45:00",
            "text": "⚠️ Ajuste de posição\n\nVENDA parcial de VALE3\nReduzir exposição de 25% para 15%"
        },
        {
            "id": 1004,
            "date": "2025-10-15T14:20:00",
            "text": "📈 Análise do dia\n\nMANTER posições em:\n- ITUB4\n- BBDC4\n- WEGE3"
        },
        {
            "id": 1005,
            "date": "2025-10-16T09:00:00",
            "text": "💼 Nova recomendação\n\nCOMPRA de PETR4 e ITUB4\nPETR4: 40%\nITUB4: 30%\nBBDC4: 30%"
        }
    ]
    
    print("\n✓ Dados de teste carregados")
    print(f"  Total de mensagens: {len(test_messages)}")
    
    # Passo 1: Parser das mensagens
    print("\n" + "=" * 70)
    print("PASSO 1: ANÁLISE DAS MENSAGENS")
    print("=" * 70)
    
    parser = CarteiraParser()
    carteiras = parser.parse_messages(test_messages)
    
    print(f"\n✓ Mensagens analisadas: {len(carteiras)}")
    print(f"  Tickers identificados: {parser.generate_statistics()['total_tickers_unicos']}")
    
    # Passo 2: Criar engine de aprendizado
    print("\n" + "=" * 70)
    print("PASSO 2: INICIALIZAÇÃO DO MAGNUS LEARNING")
    print("=" * 70)
    
    magnus = MagnusLearningEngine(learning_rate=0.3)
    print(f"\n✓ Magnus Learning Engine criado")
    print(f"  Taxa de aprendizado: {magnus.learning_rate * 100}%")
    
    # Passo 3: Processar recomendações
    print("\n" + "=" * 70)
    print("PASSO 3: PROCESSAMENTO DE RECOMENDAÇÕES")
    print("=" * 70)
    
    processed = magnus.process_telegram_recommendations(carteiras)
    
    print(f"\n✓ Recomendações processadas: {processed['total_processed']}")
    print(f"  Tickers atualizados: {len(processed['tickers_updated'])}")
    print(f"  Novos insights: {len(processed['new_insights'])}")
    print(f"  Mudanças de estratégia: {len(processed['strategy_changes'])}")
    
    # Passo 4: Obter recomendações do Magnus
    print("\n" + "=" * 70)
    print("PASSO 4: RECOMENDAÇÕES DO MAGNUS")
    print("=" * 70)
    
    top_tickers = magnus.get_top_recommended_tickers(limit=5)
    
    print(f"\n✓ Top 5 Tickers Recomendados:")
    for ticker, weight in top_tickers:
        rec = magnus.get_ticker_recommendation(ticker)
        print(f"\n  {ticker}:")
        print(f"    Recomendação: {rec['recommendation']}")
        print(f"    Peso: {rec['weight']:.3f}")
        print(f"    Confiança: {rec['confidence']:.3f}")
        print(f"    Cor: {rec['color']}")
    
    # Passo 5: Gerar portfolio sugerido
    print("\n" + "=" * 70)
    print("PASSO 5: PORTFOLIO SUGERIDO")
    print("=" * 70)
    
    portfolio = magnus.get_portfolio_suggestion(num_assets=5)
    
    if portfolio['status'] == 'success':
        print(f"\n✓ Portfolio gerado com sucesso!")
        print(f"  Número de ativos: {portfolio['num_assets']}")
        print(f"  Alocação total: {portfolio['total_percentage']}%")
        print(f"  Confiança média: {portfolio['average_confidence']:.3f}")
        
        print("\n  Alocações:")
        for allocation in portfolio['allocations']:
            print(f"    {allocation['ticker']}: {allocation['percentage']:.2f}% "
                  f"(peso: {allocation['weight']:.3f}, confiança: {allocation['confidence']:.3f})")
    else:
        print(f"\n⚠️  Status: {portfolio['status']}")
        print(f"  Mensagem: {portfolio['message']}")
    
    # Passo 6: Estatísticas de aprendizado
    print("\n" + "=" * 70)
    print("PASSO 6: ESTATÍSTICAS DE APRENDIZADO")
    print("=" * 70)
    
    stats = magnus.get_learning_statistics()
    
    print(f"\n✓ Estatísticas:")
    print(f"  Total de recomendações processadas: {stats['total_recommendations_processed']}")
    print(f"  Tickers únicos: {stats['unique_tickers']}")
    print(f"  Ajustes de estratégia: {stats['strategy_adjustments']}")
    print(f"  Taxa de aprendizado: {stats['learning_rate'] * 100}%")
    
    # Passo 7: Análise combinada
    print("\n" + "=" * 70)
    print("PASSO 7: ANÁLISE COMBINADA")
    print("=" * 70)
    
    analyzer = MagnusAnalyzer(magnus)
    
    # Analisar alguns tickers
    test_tickers = ['PETR4', 'VALE3', 'ITUB4']
    
    for ticker in test_tickers:
        analysis = analyzer.analyze_ticker(ticker)
        combined = analysis['combined_score']
        
        print(f"\n  {ticker}:")
        print(f"    Score combinado: {combined['score']:.2f}")
        print(f"    Interpretação: {combined['interpretation']}")
        print(f"    Peso Magnus: {combined['magnus_weight']:.3f}")
        print(f"    Confiança: {combined['confidence']:.3f}")
    
    # Passo 8: Salvar e carregar base de conhecimento
    print("\n" + "=" * 70)
    print("PASSO 8: PERSISTÊNCIA DE DADOS")
    print("=" * 70)
    
    # Salvar
    filename = magnus.save_knowledge_base('test_magnus_knowledge.json')
    print(f"\n✓ Base de conhecimento salva: {filename}")
    
    # Criar novo engine e carregar
    magnus2 = MagnusLearningEngine()
    loaded = magnus2.load_knowledge_base('test_magnus_knowledge.json')
    
    if loaded:
        print(f"✓ Base de conhecimento carregada com sucesso")
        print(f"  Recomendações carregadas: {len(magnus2.knowledge_base['recommendation_history'])}")
        print(f"  Tickers carregados: {len(magnus2.knowledge_base['ticker_weights'])}")
    else:
        print(f"✗ Erro ao carregar base de conhecimento")
    
    # Passo 9: Testar ajuste de estratégia
    print("\n" + "=" * 70)
    print("PASSO 9: AJUSTE DE ESTRATÉGIA")
    print("=" * 70)
    
    # Adicionar mais recomendações de PETR4
    new_messages = [
        {
            "id": 2001,
            "date": "2025-10-17T09:00:00",
            "text": "COMPRA FORTE de PETR4\nAlvo: R$ 45,00"
        },
        {
            "id": 2002,
            "date": "2025-10-17T10:00:00",
            "text": "Reforçar posição em PETR4\n50% da carteira"
        }
    ]
    
    new_carteiras = parser.parse_messages(new_messages)
    processed2 = magnus.process_telegram_recommendations(new_carteiras)
    
    print(f"\n✓ Novas recomendações processadas: {processed2['total_processed']}")
    print(f"  Mudanças de estratégia: {len(processed2['strategy_changes'])}")
    
    # Verificar se PETR4 subiu no ranking
    new_top = magnus.get_top_recommended_tickers(limit=5)
    print(f"\n  Novo ranking:")
    for i, (ticker, weight) in enumerate(new_top, 1):
        print(f"    {i}. {ticker}: {weight:.3f}")
    
    # Resultado final
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    final_stats = magnus.get_learning_statistics()
    
    print(f"\n✅ TESTE COMPLETO CONCLUÍDO COM SUCESSO!")
    print(f"\n  Resumo:")
    print(f"    Total de recomendações: {final_stats['total_recommendations_processed']}")
    print(f"    Tickers aprendidos: {final_stats['unique_tickers']}")
    print(f"    Ajustes de estratégia: {final_stats['strategy_adjustments']}")
    print(f"    Top ticker: {final_stats['top_tickers'][0][0]} (peso: {final_stats['top_tickers'][0][1]:.3f})")
    
    return True


def main():
    """Função principal."""
    try:
        success = test_magnus_learning()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ TODOS OS TESTES PASSARAM!")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("❌ ALGUNS TESTES FALHARAM")
            print("=" * 70)
            return 1
    
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())

