# 🔄 Otimizador Quinzenal Magnus Wealth

## 📋 Visão Geral

Script Python que otimiza automaticamente o portfólio de criptomoedas a cada 15 dias.

**Funcionalidades:**
- Otimização de períodos CHiLo (3-60)
- Avaliação de novas candidatas (Top 50)
- Recomendações de substituição ou expansão
- Relatório detalhado no Telegram

## 🚀 Execução

### Automática (GitHub Actions)
- **Frequência:** Dias 1 e 16 de cada mês
- **Horário:** 22:00 BR (01:00 UTC)
- **Workflow:** `.github/workflows/otimizacao-quinzenal.yml`

### Manual
```bash
cd backend/quantum-trades-backend
python3 otimizador_quinzenal.py
```

## ⏱️ Tempo de Execução

**Estimativa:** 30-40 minutos

**Breakdown:**
- Otimização de 8 criptos: ~20 min (20 períodos × 8 = 160 testes)
- Avaliação de 15 candidatas: ~15 min (20 períodos × 15 = 300 testes)
- Geração de relatório: ~1 min
- Envio ao Telegram: <1 min

**Total:** ~460 testes de backtesting

## 📊 Métricas Calculadas

### 1. Taxa de Acerto (40%)
- % de sinais corretos
- Mínimo: 55%
- Ideal: >65%

### 2. Sharpe Ratio (30%)
- Retorno ajustado ao risco
- Mínimo: 0.5
- Ideal: >1.0

### 3. Retorno Total (30%)
- Performance vs buy & hold
- Mínimo: +10% vs BH
- Ideal: +20% vs BH

**Score final:** 0-100 (ponderado)

## 🎯 Critérios de Decisão

### Atualização de Período
- Melhoria >5% no score
- Automática (não requer aprovação)

### Substituição de Cripto
- Candidata 20% superior à pior do portfólio
- **Requer aprovação manual**

### Expansão do Portfólio
- Candidata com score >70
- Nenhuma cripto atual com score <60
- **Requer aprovação manual**

## 📤 Relatório

**Enviado para:** Telegram (grupo Magnus Wealth)

**Contém:**
1. Otimizações de período recomendadas
2. Top 5 candidatas
3. Recomendação final (substituição/expansão/manter)
4. Métricas detalhadas
5. Impacto esperado

## 🔧 Configuração

**Secrets necessários:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

**Dependências:**
```bash
pip install yfinance python-dotenv requests numpy pandas
```

## 📁 Arquivos Gerados

**Relatório:** `/home/ubuntu/relatorio_otimizacao_YYYYMMDD_HHMMSS.md`

## ⚠️ Limitações

1. **Máximo 2 criptos adicionadas** por quinzena
2. **Máximo 1 substituição** por quinzena
3. **Período de carência:** 30 dias para novas criptos

## 🐛 Troubleshooting

### Erro: "Sem dados para [CRIPTO]"
- Yahoo Finance pode estar indisponível
- Símbolo pode ter mudado
- Verificar conectividade

### Erro: "Taxa de acerto muito baixa"
- Normal para algumas candidatas
- Indica que a cripto não é adequada

### Timeout no GitHub Actions
- Execução pode levar até 40 minutos
- Aumentar timeout no workflow se necessário

## 📝 Changelog

**v1.0 (27/10/2025)**
- Versão inicial
- Períodos 3-60 (20 testes)
- 3 métricas (sem drawdown)
- Suporte a expansão de portfólio

---

**Versão:** 1.0  
**Última atualização:** 27/10/2025

