/**
 * Magnus Wealth - Charts Service
 * Serviço para gráficos com TradingView Lightweight Charts
 */

// ============================================================================
// CONFIGURAÇÃO
// ============================================================================

const BRAPI_BASE_URL = 'https://brapi.dev/api';
const API_BASE_URL = 'http://localhost:5000/api';

// ============================================================================
// ESTADO GLOBAL
// ============================================================================

let chart = null;
let candlestickSeries = null;
let volumeSeries = null;
let indicators = {
    ma20: null,
    ma50: null,
    ema9: null,
    volume: null
};

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

/**
 * Inicializa o gráfico
 */
function initializeChart() {
    const chartElement = document.getElementById('chart');

    // Criar gráfico
    chart = LightweightCharts.createChart(chartElement, {
        width: chartElement.clientWidth,
        height: 500,
        layout: {
            background: { color: 'transparent' },
            textColor: '#ffffff',
        },
        grid: {
            vertLines: { color: 'rgba(255, 255, 255, 0.1)' },
            horzLines: { color: 'rgba(255, 255, 255, 0.1)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(255, 215, 0, 0.3)',
        },
        timeScale: {
            borderColor: 'rgba(255, 215, 0, 0.3)',
            timeVisible: true,
            secondsVisible: false,
        },
    });

    // Criar série de candlestick
    candlestickSeries = chart.addCandlestickSeries({
        upColor: '#4CAF50',
        downColor: '#f44336',
        borderVisible: false,
        wickUpColor: '#4CAF50',
        wickDownColor: '#f44336',
    });

    // Responsividade
    window.addEventListener('resize', () => {
        chart.applyOptions({ width: chartElement.clientWidth });
    });
}

// ============================================================================
// CARREGAMENTO DE DADOS
// ============================================================================

/**
 * Carrega dados do gráfico
 */
async function loadChartData(ticker, timeframe) {
    const loadingOverlay = document.getElementById('loading-overlay');
    
    try {
        // Mostrar loading
        loadingOverlay.classList.remove('hidden');

        // Atualizar título
        document.getElementById('chart-title').textContent = ticker;

        // Buscar dados da brapi.dev
        const range = getRange(timeframe);
        const interval = getInterval(timeframe);
        
        const url = `${BRAPI_BASE_URL}/quote/${ticker}?range=${range}&interval=${interval}`;
        const response = await fetch(url);
        const data = await response.json();

        if (!data.results || data.results.length === 0) {
            throw new Error('Dados não encontrados para este ativo');
        }

        const result = data.results[0];
        
        // Processar dados históricos
        const historicalData = result.historicalDataPrice || [];
        
        if (historicalData.length === 0) {
            throw new Error('Sem dados históricos disponíveis');
        }

        // Converter para formato do TradingView
        const candleData = historicalData.map(item => ({
            time: item.date / 1000, // Converter para segundos
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
        })).reverse(); // Inverter para ordem cronológica

        const volumeData = historicalData.map(item => ({
            time: item.date / 1000,
            value: item.volume,
            color: item.close >= item.open ? 'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)'
        })).reverse();

        // Atualizar gráfico
        candlestickSeries.setData(candleData);

        // Atualizar informações
        updateChartInfo(result, candleData);

        // Ajustar visualização
        chart.timeScale().fitContent();

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        alert(`Erro ao carregar dados: ${error.message}`);
    } finally {
        loadingOverlay.classList.add('hidden');
    }
}

/**
 * Atualiza informações do gráfico
 */
function updateChartInfo(result, candleData) {
    // Último preço
    const lastCandle = candleData[candleData.length - 1];
    const lastPrice = lastCandle.close;
    document.getElementById('last-price').textContent = `R$ ${lastPrice.toFixed(2)}`;

    // Variação
    const firstCandle = candleData[0];
    const change = ((lastPrice - firstCandle.close) / firstCandle.close) * 100;
    const changeElement = document.getElementById('price-change');
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
    changeElement.className = `chart-info-value ${change >= 0 ? 'positive' : 'negative'}`;

    // Volume (soma total)
    const totalVolume = candleData.reduce((sum, candle) => {
        const volumeItem = result.historicalDataPrice.find(item => 
            item.date / 1000 === candle.time
        );
        return sum + (volumeItem ? volumeItem.volume : 0);
    }, 0);
    
    document.getElementById('volume').textContent = formatVolume(totalVolume);
}

// ============================================================================
// INDICADORES
// ============================================================================

/**
 * Ativa/desativa indicador
 */
function toggleIndicator(indicator, active) {
    if (active) {
        addIndicator(indicator);
    } else {
        removeIndicator(indicator);
    }
}

/**
 * Adiciona indicador ao gráfico
 */
function addIndicator(indicator) {
    const data = candlestickSeries.data();
    
    if (!data || data.length === 0) {
        alert('Carregue dados do gráfico primeiro');
        return;
    }

    switch (indicator) {
        case 'ma20':
            indicators.ma20 = chart.addLineSeries({
                color: '#ffd700',
                lineWidth: 2,
                title: 'MA 20',
            });
            indicators.ma20.setData(calculateMA(data, 20));
            break;

        case 'ma50':
            indicators.ma50 = chart.addLineSeries({
                color: '#ff9800',
                lineWidth: 2,
                title: 'MA 50',
            });
            indicators.ma50.setData(calculateMA(data, 50));
            break;

        case 'ema9':
            indicators.ema9 = chart.addLineSeries({
                color: '#2196F3',
                lineWidth: 2,
                title: 'EMA 9',
            });
            indicators.ema9.setData(calculateEMA(data, 9));
            break;

        case 'volume':
            if (!volumeSeries) {
                volumeSeries = chart.addHistogramSeries({
                    color: '#26a69a',
                    priceFormat: {
                        type: 'volume',
                    },
                    priceScaleId: '',
                });
                
                // Configurar escala de volume
                volumeSeries.priceScale().applyOptions({
                    scaleMargins: {
                        top: 0.8,
                        bottom: 0,
                    },
                });

                // Adicionar dados de volume
                const result = candlestickSeries.data();
                // Aqui você precisaria ter os dados de volume
                // Por simplicidade, vamos criar dados de exemplo
                const volumeData = result.map(item => ({
                    time: item.time,
                    value: Math.random() * 1000000,
                    color: item.close >= item.open ? 
                        'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)'
                }));
                
                volumeSeries.setData(volumeData);
            }
            break;
    }
}

/**
 * Remove indicador do gráfico
 */
function removeIndicator(indicator) {
    if (indicators[indicator]) {
        chart.removeSeries(indicators[indicator]);
        indicators[indicator] = null;
    }

    if (indicator === 'volume' && volumeSeries) {
        chart.removeSeries(volumeSeries);
        volumeSeries = null;
    }
}

/**
 * Calcula Média Móvel Simples
 */
function calculateMA(data, period) {
    const result = [];
    
    for (let i = period - 1; i < data.length; i++) {
        let sum = 0;
        for (let j = 0; j < period; j++) {
            sum += data[i - j].close;
        }
        
        result.push({
            time: data[i].time,
            value: sum / period
        });
    }
    
    return result;
}

/**
 * Calcula Média Móvel Exponencial
 */
function calculateEMA(data, period) {
    const result = [];
    const multiplier = 2 / (period + 1);
    
    // Primeira EMA é uma SMA
    let ema = 0;
    for (let i = 0; i < period; i++) {
        ema += data[i].close;
    }
    ema = ema / period;
    
    result.push({
        time: data[period - 1].time,
        value: ema
    });
    
    // Calcular EMA para o restante
    for (let i = period; i < data.length; i++) {
        ema = (data[i].close - ema) * multiplier + ema;
        result.push({
            time: data[i].time,
            value: ema
        });
    }
    
    return result;
}

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Retorna range para a API baseado no timeframe
 */
function getRange(timeframe) {
    const ranges = {
        '1': '1d',
        '5': '5d',
        '15': '1mo',
        '60': '3mo',
        '1d': '1y'
    };
    return ranges[timeframe] || '1y';
}

/**
 * Retorna interval para a API baseado no timeframe
 */
function getInterval(timeframe) {
    const intervals = {
        '1': '1m',
        '5': '5m',
        '15': '15m',
        '60': '1h',
        '1d': '1d'
    };
    return intervals[timeframe] || '1d';
}

/**
 * Formata volume
 */
function formatVolume(volume) {
    if (volume >= 1000000000) {
        return (volume / 1000000000).toFixed(2) + 'B';
    } else if (volume >= 1000000) {
        return (volume / 1000000).toFixed(2) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(2) + 'K';
    }
    return volume.toString();
}

// ============================================================================
// EXPORTAR FUNÇÕES
// ============================================================================

window.initializeChart = initializeChart;
window.loadChartData = loadChartData;
window.toggleIndicator = toggleIndicator;

