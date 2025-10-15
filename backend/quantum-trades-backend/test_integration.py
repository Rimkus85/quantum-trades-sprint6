#!/usr/bin/env python3
"""
Script de teste para validar a integração do backend Magnus Wealth.
Testa os módulos sem necessidade de credenciais do Telegram.
"""

import json
from modules.carteira_parser import CarteiraParser, parse_telegram_messages, get_recommendations_summary


def test_parser():
    """Testa o parser de carteiras."""
    print("=" * 70)
    print("TESTE DO PARSER DE CARTEIRAS")
    print("=" * 70)
    
    # Dados de teste
    test_messages = [
        {
            "id": 1001,
            "date": "2025-10-15T09:00:00",
            "sender_id": 123456789,
            "text": "📊 Carteira Recomendada - Outubro 2025\n\nAlocação sugerida:\nPETR4 - 30%\nVALE3 - 25%\nITUB4 - 20%\nBBDC4 - 15%\nWEGE3 - 10%\n\nTotal: 100%",
            "is_reply": False,
            "views": 250
        },
        {
            "id": 1002,
            "date": "2025-10-15T10:30:00",
            "sender_id": 123456789,
            "text": "🔔 ALERTA DE COMPRA\n\nRecomendação: COMPRA de PETR4\nPreço alvo: R$ 42,00\nStop loss: R$ 38,50\n\nFundamento: Resultados do 3Q acima do esperado",
            "is_reply": False,
            "views": 180
        },
        {
            "id": 1003,
            "date": "2025-10-15T11:45:00",
            "sender_id": 123456789,
            "text": "⚠️ Ajuste de posição\n\nVENDA parcial de VALE3\nReduzir exposição de 25% para 15%\n\nMotivo: Realização de lucros após alta de 12%",
            "is_reply": False,
            "views": 165
        }
    ]
    
    print("\n✓ Dados de teste carregados")
    print(f"  Total de mensagens: {len(test_messages)}")
    
    # Testar parser
    parser = CarteiraParser()
    carteiras = parser.parse_messages(test_messages)
    
    print(f"\n✓ Parser executado com sucesso")
    print(f"  Carteiras extraídas: {len(carteiras)}")
    
    # Gerar estatísticas
    stats = parser.generate_statistics()
    
    print("\n📊 ESTATÍSTICAS:")
    print(f"  Total de carteiras: {stats['total_carteiras']}")
    print(f"  Tickers únicos: {stats['total_tickers_unicos']}")
    
    print("\n🏆 Top Tickers:")
    for ticker, count in list(stats['tickers_mais_mencionados'].items())[:5]:
        print(f"  {ticker}: {count} menções")
    
    print("\n📋 Distribuição de Recomendações:")
    for tipo, count in stats['distribuicao_recomendacoes'].items():
        print(f"  {tipo.capitalize()}: {count}")
    
    # Testar funções auxiliares
    print("\n" + "=" * 70)
    print("TESTE DE FUNÇÕES AUXILIARES")
    print("=" * 70)
    
    report = parse_telegram_messages(test_messages)
    print(f"\n✓ parse_telegram_messages: OK")
    print(f"  Total analisado: {report['total_mensagens_analisadas']}")
    
    summary = get_recommendations_summary(test_messages)
    print(f"\n✓ get_recommendations_summary: OK")
    print(f"  Top tickers: {summary['top_tickers'][:3]}")
    print(f"  Compras: {summary['compras']}")
    print(f"  Vendas: {summary['vendas']}")
    
    return True


def test_api_structure():
    """Testa a estrutura da API."""
    print("\n" + "=" * 70)
    print("TESTE DE ESTRUTURA DA API")
    print("=" * 70)
    
    try:
        from app import app
        print("\n✓ app.py importado com sucesso")
        
        # Verificar rotas
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"{','.join(rule.methods)} {rule.rule}")
        
        print(f"\n✓ Total de rotas: {len(routes)}")
        print("\nRotas disponíveis:")
        for route in sorted(routes):
            print(f"  {route}")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Erro ao importar app: {e}")
        return False


def main():
    """Função principal de teste."""
    print("\n" + "=" * 70)
    print("MAGNUS WEALTH - TESTE DE INTEGRAÇÃO")
    print("=" * 70)
    
    success = True
    
    # Teste 1: Parser
    try:
        if not test_parser():
            success = False
    except Exception as e:
        print(f"\n✗ Erro no teste do parser: {e}")
        success = False
    
    # Teste 2: API
    try:
        if not test_api_structure():
            success = False
    except Exception as e:
        print(f"\n✗ Erro no teste da API: {e}")
        success = False
    
    # Resultado final
    print("\n" + "=" * 70)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
    print("=" * 70)
    
    return success


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

