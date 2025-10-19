#!/usr/bin/env python3
"""
API Flask para o Magnus Wealth - Quantum Trades.
Fornece endpoints para integração com Telegram e análise de carteiras.
"""

import os
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from services.telegram_service import TelegramService, TelegramCarteirasReader
from modules.carteira_parser import CarteiraParser, parse_telegram_messages, get_recommendations_summary
from modules.magnus_learning import MagnusLearningEngine, MagnusAnalyzer
from ml_models.sentiment_analyzer import SentimentAnalyzer
from ml_models.price_predictor import PricePredictor
from ml_models.portfolio_optimizer import PortfolioOptimizer
from ml_models.backtester import Backtester
from ml_models.model_evaluator import ModelEvaluator
from services.historical_data_service import HistoricalDataService

# Carregar variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurações
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
TELEGRAM_GROUP = os.getenv('TELEGRAM_GROUP_USERNAME')

# Instâncias globais
telgram_service = None
magnus_engine = MagnusLearningEngine(learning_rate=0.3)
magnus_analyzer = MagnusAnalyzer(magnus_engine)

# Modelos de ML
sentiment_analyzer = SentimentAnalyzer()
price_predictor = PricePredictor()
portfolio_optimizer = PortfolioOptimizer()

# Backtesting e Performance
backtester = Backtester(initial_capital=10000)
model_evaluator = ModelEvaluator()
historical_data_service = HistoricalDataService()

# Tentar carregar base de conhecimento existente
magnus_engine.load_knowledge_base()


def get_telegram_service():
    """Retorna ou cria instância do serviço do Telegram."""
    global telegram_service
    if telegram_service is None:
        if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
            return None
        telegram_service = TelegramService(TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE)
    return telegram_service


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check."""
    return jsonify({
        'status': 'ok',
        'service': 'Magnus Wealth API',
        'version': '1.1.0',
        'telegram_configured': all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]),
        'magnus_learning': {
            'enabled': True,
            'last_update': magnus_engine.last_update,
            'total_recommendations': len(magnus_engine.knowledge_base['recommendation_history'])
        }
    })


@app.route('/api/telegram/config', methods=['GET'])
def get_telegram_config():
    """Retorna status da configuração do Telegram."""
    return jsonify({
        'configured': all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]),
        'has_api_id': bool(TELEGRAM_API_ID),
        'has_api_hash': bool(TELEGRAM_API_HASH),
        'has_phone': bool(TELEGRAM_PHONE),
        'has_group': bool(TELEGRAM_GROUP)
    })


@app.route('/api/telegram/messages', methods=['GET'])
def get_telegram_messages():
    """
    Lê mensagens do grupo do Telegram.
    
    Query params:
        - group: Username ou ID do grupo (opcional, usa padrão se não fornecido)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado',
            'message': 'Configure as variáveis de ambiente TELEGRAM_API_ID, TELEGRAM_API_HASH e TELEGRAM_PHONE'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado',
            'message': 'Forneça o parâmetro "group" ou configure TELEGRAM_GROUP_USERNAME'
        }), 400
    
    try:
        # Executar leitura assíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def read():
            await service.connect()
            messages = await service.read_messages(group, limit)
            await service.disconnect()
            return messages
        
        messages = loop.run_until_complete(read())
        loop.close()
        
        return jsonify({
            'success': True,
            'total': len(messages),
            'group': group,
            'messages': messages
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao ler mensagens',
            'message': str(e)
        }), 500


@app.route('/api/telegram/carteiras', methods=['GET'])
def get_carteiras():
    """
    Lê e filtra mensagens sobre carteiras do Telegram.
    
    Query params:
        - group: Username ou ID do grupo (opcional)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado'
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def read():
            reader = TelegramCarteirasReader(service)
            await service.connect()
            carteiras = await reader.read_carteiras(group, limit)
            await service.disconnect()
            return carteiras
        
        carteiras = loop.run_until_complete(read())
        loop.close()
        
        return jsonify({
            'success': True,
            'total': len(carteiras),
            'group': group,
            'carteiras': carteiras
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao ler carteiras',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/parse', methods=['POST'])
def parse_carteiras():
    """
    Analisa mensagens e extrai informações estruturadas.
    
    Body:
        - messages: Lista de mensagens do Telegram
    """
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({
            'error': 'Mensagens não fornecidas',
            'message': 'Envie um JSON com a chave "messages" contendo a lista de mensagens'
        }), 400
    
    try:
        messages = data['messages']
        report = parse_telegram_messages(messages)
        
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao processar mensagens',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/summary', methods=['POST'])
def get_carteiras_summary():
    """
    Retorna resumo das recomendações.
    
    Body:
        - messages: Lista de mensagens do Telegram
    """
    data = request.get_json()
    
    if not data or 'messages' not in data:
        return jsonify({
            'error': 'Mensagens não fornecidas'
        }), 400
    
    try:
        messages = data['messages']
        summary = get_recommendations_summary(messages)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar resumo',
            'message': str(e)
        }), 500


@app.route('/api/carteiras/analyze', methods=['GET'])
def analyze_carteiras_from_telegram():
    """
    Endpoint completo: lê do Telegram e retorna análise.
    
    Query params:
        - group: Username ou ID do grupo (opcional)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado'
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process():
            # Ler mensagens
            reader = TelegramCarteirasReader(service)
            await service.connect()
            carteiras = await reader.read_carteiras(group, limit)
            await service.disconnect()
            
            # Analisar
            parser = CarteiraParser()
            parser.parse_messages(carteiras)
            report = parser.generate_report()
            
            return report
        
        report = loop.run_until_complete(process())
        loop.close()
        
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar carteiras',
            'message': str(e)
        }), 500


# ============================================================================
# NOVOS ENDPOINTS - MAGNUS LEARNING
# ============================================================================

@app.route('/api/magnus/learn', methods=['POST'])
def magnus_learn():
    """
    Processa recomendações do Telegram e atualiza aprendizado do Magnus.
    
    Body:
        - carteiras: Lista de carteiras analisadas
    """
    data = request.get_json()
    
    if not data or 'carteiras' not in data:
        return jsonify({
            'error': 'Carteiras não fornecidas',
            'message': 'Envie um JSON com a chave "carteiras" contendo a lista de carteiras'
        }), 400
    
    try:
        carteiras = data['carteiras']
        processed = magnus_engine.process_telegram_recommendations(carteiras)
        
        # Salvar base de conhecimento
        magnus_engine.save_knowledge_base()
        
        return jsonify({
            'success': True,
            'processed': processed,
            'statistics': magnus_engine.get_learning_statistics()
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao processar aprendizado',
            'message': str(e)
        }), 500


@app.route('/api/magnus/learn-from-telegram', methods=['GET'])
def magnus_learn_from_telegram():
    """
    Lê do Telegram, analisa e atualiza aprendizado do Magnus automaticamente.
    
    Query params:
        - group: Username ou ID do grupo (opcional)
        - limit: Número de mensagens (padrão: 100)
    """
    service = get_telegram_service()
    if not service:
        return jsonify({
            'error': 'Telegram não configurado'
        }), 400
    
    group = request.args.get('group', TELEGRAM_GROUP)
    limit = int(request.args.get('limit', 100))
    
    if not group:
        return jsonify({
            'error': 'Grupo não especificado'
        }), 400
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def process():
            # Ler mensagens
            reader = TelegramCarteirasReader(service)
            await service.connect()
            carteiras_raw = await reader.read_carteiras(group, limit)
            await service.disconnect()
            
            # Analisar
            parser = CarteiraParser()
            carteiras = parser.parse_messages(carteiras_raw)
            
            return carteiras
        
        carteiras = loop.run_until_complete(process())
        loop.close()
        
        # Processar aprendizado
        processed = magnus_engine.process_telegram_recommendations(carteiras)
        
        # Salvar base de conhecimento
        magnus_engine.save_knowledge_base()
        
        return jsonify({
            'success': True,
            'total_messages': len(carteiras),
            'processed': processed,
            'statistics': magnus_engine.get_learning_statistics()
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao processar aprendizado',
            'message': str(e)
        }), 500


@app.route('/api/magnus/recommendations', methods=['GET'])
def get_magnus_recommendations():
    """
    Retorna recomendações do Magnus baseadas no aprendizado.
    
    Query params:
        - limit: Número de recomendações (padrão: 10)
    """
    limit = int(request.args.get('limit', 10))
    
    try:
        top_tickers = magnus_engine.get_top_recommended_tickers(limit=limit)
        
        recommendations = []
        for ticker, weight in top_tickers:
            rec = magnus_engine.get_ticker_recommendation(ticker)
            recommendations.append(rec)
        
        return jsonify({
            'success': True,
            'total': len(recommendations),
            'recommendations': recommendations,
            'statistics': magnus_engine.get_learning_statistics()
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar recomendações',
            'message': str(e)
        }), 500


@app.route('/api/magnus/recommendation/<ticker>', methods=['GET'])
def get_ticker_recommendation(ticker: str):
    """
    Retorna recomendação do Magnus para um ticker específico.
    
    Path params:
        - ticker: Código do ticker (ex: PETR4)
    """
    try:
        recommendation = magnus_engine.get_ticker_recommendation(ticker.upper())
        
        return jsonify({
            'success': True,
            'recommendation': recommendation
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar recomendação',
            'message': str(e)
        }), 500


@app.route('/api/magnus/portfolio', methods=['GET'])
def get_magnus_portfolio():
    """
    Gera sugestão de portfolio do Magnus.
    
    Query params:
        - num_assets: Número de ativos (padrão: 5)
    """
    num_assets = int(request.args.get('num_assets', 5))
    
    try:
        portfolio = magnus_engine.get_portfolio_suggestion(num_assets=num_assets)
        
        return jsonify({
            'success': True,
            'portfolio': portfolio
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao gerar portfolio',
            'message': str(e)
        }), 500


@app.route('/api/magnus/analyze/<ticker>', methods=['GET'])
def analyze_ticker_with_magnus(ticker: str):
    """
    Analisa um ticker combinando dados de mercado e aprendizado do Magnus.
    
    Path params:
        - ticker: Código do ticker (ex: PETR4)
    """
    try:
        analysis = magnus_analyzer.analyze_ticker(ticker.upper())
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar ticker',
            'message': str(e)
        }), 500


@app.route('/api/magnus/statistics', methods=['GET'])
def get_magnus_statistics():
    """Retorna estatísticas do aprendizado do Magnus."""
    try:
        stats = magnus_engine.get_learning_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter estatísticas',
            'message': str(e)
        }), 500


@app.route('/api/magnus/reset', methods=['POST'])
def reset_magnus_knowledge():
    """Reseta a base de conhecimento do Magnus."""
    try:
        magnus_engine.reset_knowledge()
        magnus_engine.save_knowledge_base()
        
        return jsonify({
            'success': True,
            'message': 'Base de conhecimento resetada com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao resetar conhecimento',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINTS DE MACHINE LEARNING
# ============================================================================

@app.route('/api/ml/sentiment/analyze', methods=['POST'])
def analyze_sentiment():
    """
    Analisa sentimento de um texto.
    
    Body:
        - text: Texto a ser analisado
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({
            'error': 'Campo "text" é obrigatório'
        }), 400
    
    try:
        result = sentiment_analyzer.analyze_text(data['text'])
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar sentimento',
            'message': str(e)
        }), 500


@app.route('/api/ml/sentiment/ticker/<ticker>', methods=['GET'])
def analyze_ticker_sentiment(ticker: str):
    """
    Analisa sentimento agregado para um ticker.
    
    Path params:
        - ticker: Código do ticker (ex: PETR4)
    
    Query params:
        - limit: Número de mensagens (padrão: 100)
    """
    limit = int(request.args.get('limit', 100))
    
    try:
        # Buscar mensagens do Telegram
        service = get_telegram_service()
        if not service:
            return jsonify({
                'error': 'Telegram não configurado'
            }), 503
        
        messages = asyncio.run(service.get_messages(limit=limit))
        
        # Analisar sentimento
        result = sentiment_analyzer.analyze_ticker_sentiment(ticker.upper(), messages)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar sentimento do ticker',
            'message': str(e)
        }), 500


@app.route('/api/ml/sentiment/market', methods=['GET'])
def analyze_market_sentiment():
    """
    Analisa sentimento geral do mercado.
    
    Query params:
        - limit: Número de mensagens (padrão: 100)
    """
    limit = int(request.args.get('limit', 100))
    
    try:
        # Buscar mensagens do Telegram
        service = get_telegram_service()
        if not service:
            return jsonify({
                'error': 'Telegram não configurado'
            }), 503
        
        messages = asyncio.run(service.get_messages(limit=limit))
        
        # Analisar sentimento
        result = sentiment_analyzer.get_market_sentiment(messages)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao analisar sentimento do mercado',
            'message': str(e)
        }), 500


@app.route('/api/ml/predict/train', methods=['POST'])
def train_price_predictor():
    """
    Treina modelo de previsão de preços.
    
    Body:
        - ticker: Código do ticker
        - prices: Lista de preços históricos
        - dates: Lista de datas (opcional)
    """
    data = request.get_json()
    
    if not data or 'ticker' not in data or 'prices' not in data:
        return jsonify({
            'error': 'Campos "ticker" e "prices" são obrigatórios'
        }), 400
    
    try:
        result = price_predictor.train_model(
            ticker=data['ticker'],
            prices=data['prices'],
            dates=data.get('dates')
        )
        
        return jsonify({
            'success': True,
            'training': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao treinar modelo',
            'message': str(e)
        }), 500


@app.route('/api/ml/predict/price/<ticker>', methods=['POST'])
def predict_price(ticker: str):
    """
    Prevê preços futuros de um ticker.
    
    Path params:
        - ticker: Código do ticker
    
    Body:
        - prices: Lista de preços históricos recentes
        - days: Número de dias a prever (padrão: 7)
    """
    data = request.get_json()
    
    if not data or 'prices' not in data:
        return jsonify({
            'error': 'Campo "prices" é obrigatório'
        }), 400
    
    try:
        days = data.get('days', 7)
        
        result = price_predictor.predict_next_days(
            ticker=ticker.upper(),
            prices=data['prices'],
            days=days
        )
        
        return jsonify({
            'success': True,
            'prediction': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao prever preços',
            'message': str(e)
        }), 500


@app.route('/api/ml/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """
    Otimiza portfólio de ativos.
    
    Body:
        - prices_history: Dicionário {ticker: [preços]}
        - risk_tolerance: Tolerância ao risco (conservative, moderate, aggressive)
        - optimization_type: Tipo de otimização (sharpe, min_volatility)
    """
    data = request.get_json()
    
    if not data or 'prices_history' not in data:
        return jsonify({
            'error': 'Campo "prices_history" é obrigatório'
        }), 400
    
    try:
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        optimization_type = data.get('optimization_type', 'sharpe')
        
        if optimization_type == 'sharpe':
            result = portfolio_optimizer.optimize_sharpe_ratio(
                prices_history=data['prices_history'],
                risk_tolerance=risk_tolerance
            )
        else:
            result = portfolio_optimizer.optimize_min_volatility(
                prices_history=data['prices_history']
            )
        
        return jsonify({
            'success': True,
            'portfolio': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao otimizar portfólio',
            'message': str(e)
        }), 500


@app.route('/api/ml/models/status', methods=['GET'])
def get_models_status():
    """
    Retorna status dos modelos de ML.
    """
    try:
        trained_models = price_predictor.list_trained_models()
        
        return jsonify({
            'success': True,
            'models': {
                'sentiment_analyzer': {
                    'status': 'ready',
                    'positive_words': len(sentiment_analyzer.positive_words),
                    'negative_words': len(sentiment_analyzer.negative_words)
                },
                'price_predictor': {
                    'status': 'ready',
                    'trained_tickers': trained_models,
                    'total_models': len(trained_models)
                },
                'portfolio_optimizer': {
                    'status': 'ready'
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao obter status dos modelos',
            'message': str(e)
        }), 500


# ============================================================================
# ENDPOINTS DE BACKTESTING E PERFORMANCE
# ============================================================================

@app.route('/api/historical/<ticker>', methods=['GET'])
def get_historical_data(ticker: str):
    """
    Busca dados históricos de um ticker.
    
    Path params:
        - ticker: Código do ticker
    
    Query params:
        - period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        - use_cache: Se deve usar cache (default: true)
    """
    period = request.args.get('period', '1y')
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    try:
        data = historical_data_service.get_historical_data(
            ticker=ticker.upper(),
            period=period,
            use_cache=use_cache
        )
        
        if not data:
            return jsonify({
                'error': 'Dados não encontrados para este ticker'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao buscar dados históricos',
            'message': str(e)
        }), 500


@app.route('/api/backtest/buy-and-hold', methods=['POST'])
def run_buy_and_hold_backtest():
    """
    Executa backtesting de estratégia Buy and Hold.
    
    Body:
        - ticker: Código do ticker
        - period: Período (default: 1y)
        - initial_capital: Capital inicial (default: 10000)
    """
    data = request.get_json()
    
    if not data or 'ticker' not in data:
        return jsonify({
            'error': 'Campo "ticker" é obrigatório'
        }), 400
    
    try:
        ticker = data['ticker'].upper()
        period = data.get('period', '1y')
        initial_capital = data.get('initial_capital', 10000)
        
        # Buscar dados históricos
        historical_data = historical_data_service.get_historical_data(ticker, period)
        
        if not historical_data:
            return jsonify({
                'error': 'Dados históricos não encontrados'
            }), 404
        
        # Extrair preços e datas
        prices = [item['close'] for item in historical_data['data']]
        dates = [item['date'] for item in historical_data['data']]
        
        # Executar backtest
        bt = Backtester(initial_capital=initial_capital)
        result = bt.backtest_buy_and_hold(ticker, prices, dates)
        
        # Salvar resultado
        filepath = bt.save_result(result)
        result['saved_to'] = filepath
        
        return jsonify({
            'success': True,
            'backtest': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao executar backtest',
            'message': str(e)
        }), 500


@app.route('/api/backtest/portfolio', methods=['POST'])
def run_portfolio_backtest():
    """
    Executa backtesting de portfólio.
    
    Body:
        - allocations: Dicionário {ticker: peso}
        - period: Período (default: 1y)
        - initial_capital: Capital inicial (default: 10000)
    """
    data = request.get_json()
    
    if not data or 'allocations' not in data:
        return jsonify({
            'error': 'Campo "allocations" é obrigatório'
        }), 400
    
    try:
        allocations = data['allocations']
        period = data.get('period', '1y')
        initial_capital = data.get('initial_capital', 10000)
        
        # Buscar dados históricos de todos os tickers
        tickers = list(allocations.keys())
        historical_data = historical_data_service.get_multiple_tickers(tickers, period)
        
        # Extrair preços
        prices_history = {}
        dates = None
        
        for ticker, data_item in historical_data.items():
            prices_history[ticker] = [item['close'] for item in data_item['data']]
            if dates is None:
                dates = [item['date'] for item in data_item['data']]
        
        # Executar backtest
        bt = Backtester(initial_capital=initial_capital)
        result = bt.backtest_portfolio(allocations, prices_history, dates)
        
        # Salvar resultado
        filepath = bt.save_result(result)
        result['saved_to'] = filepath
        
        return jsonify({
            'success': True,
            'backtest': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao executar backtest de portfólio',
            'message': str(e)
        }), 500


@app.route('/api/performance/evaluate-predictor', methods=['POST'])
def evaluate_price_predictor_performance():
    """
    Avalia performance do preditor de preços.
    
    Body:
        - actual_prices: Preços reais
        - predicted_prices: Preços previstos
    """
    data = request.get_json()
    
    if not data or 'actual_prices' not in data or 'predicted_prices' not in data:
        return jsonify({
            'error': 'Campos "actual_prices" e "predicted_prices" são obrigatórios'
        }), 400
    
    try:
        result = model_evaluator.evaluate_price_predictor(
            actual_prices=data['actual_prices'],
            predicted_prices=data['predicted_prices']
        )
        
        return jsonify({
            'success': True,
            'evaluation': result
        })
    
    except Exception as e:
        return jsonify({
            'error': 'Erro ao avaliar preditor',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("MAGNUS WEALTH API - Quantum Trades")
    print("=" * 60)
    print(f"Telegram configurado: {all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE])}")
    print(f"Grupo padrão: {TELEGRAM_GROUP or 'Não configurado'}")
    print(f"Magnus Learning: Ativado")
    print(f"Recomendações processadas: {len(magnus_engine.knowledge_base['recommendation_history'])}")
    print("=" * 60)
    print("\nEndpoints disponíveis:")
    print("  GET  /api/health")
    print("  GET  /api/telegram/config")
    print("  GET  /api/telegram/messages")
    print("  GET  /api/telegram/carteiras")
    print("  POST /api/carteiras/parse")
    print("  POST /api/carteiras/summary")
    print("  GET  /api/carteiras/analyze")
    print("\nMagnus Learning:")
    print("  POST /api/magnus/learn")
    print("  GET  /api/magnus/learn-from-telegram")
    print("  GET  /api/magnus/recommendations")
    print("  GET  /api/magnus/recommendation/<ticker>")
    print("  GET  /api/magnus/portfolio")
    print("  GET  /api/magnus/analyze/<ticker>")
    print("  GET  /api/magnus/statistics")
    print("  POST /api/magnus/reset")
    print("\nIniciando servidor...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

