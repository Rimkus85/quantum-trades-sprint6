# Taxas de Trading - Binance Futuros USDⓈ-M

**Fonte:** https://www.binance.com/pt/fee/futureFee  
**Data de captura:** 28/10/2025  
**Aplicável a:** Futuros USDⓈ-M (contratos perpétuos)

---

## 📊 Tabela de Taxas por Nível VIP

### Formato: Maker/Taker

| Nível | Volume 30 dias (USD) | Saldo BNB | USDT Maker/Taker | Com BNB 10% desconto |
|-------|---------------------|-----------|------------------|---------------------|
| **Usuário Regular** | < 15.000.000 | ≥ 0 | **0.0200%/0.0500%** | 0.0180%/0.0450% |
| VIP 1 | ≥ 15.000.000 | ≥ 25 | 0.0160%/0.0400% | 0.0144%/0.0360% |
| VIP 2 | ≥ 50.000.000 | ≥ 100 | 0.0140%/0.0350% | 0.0126%/0.0315% |
| VIP 3 | ≥ 100.000.000 | ≥ 250 | 0.0120%/0.0320% | 0.0108%/0.0288% |
| VIP 4 | ≥ 600.000.000 | ≥ 500 | 0.0100%/0.0300% | 0.0090%/0.0270% |
| VIP 5 | ≥ 1.000.000.000 | ≥ 1.000 | 0.0080%/0.0270% | 0.0072%/0.0243% |
| VIP 6 | ≥ 2.500.000.000 | ≥ 1.750 | 0.0060%/0.0250% | 0.0054%/0.0225% |
| VIP 7 | ≥ 5.000.000.000 | ≥ 3.000 | 0.0040%/0.0220% | 0.0036%/0.0198% |
| VIP 8 | ≥ 12.500.000.000 | ≥ 4.500 | 0.0020%/0.0200% | 0.0018%/0.0180% |
| VIP 9 | ≥ 25.000.000.000 | ≥ 5.500 | 0.0000%/0.0170% | 0.0000%/0.0153% |

---

## 🎯 Taxas Aplicáveis ao Magnus Wealth

**Perfil assumido:** Usuário Regular (sem volume VIP)

### Taxas Padrão (sem BNB):
- **Maker:** 0.0200% (0.02%)
- **Taker:** 0.0500% (0.05%)

### Taxas com desconto BNB 10%:
- **Maker:** 0.0180% (0.018%)
- **Taker:** 0.0450% (0.045%)

---

## 💡 Definições

**Maker:** Ordem que adiciona liquidez ao livro (limit order que não executa imediatamente)
- Exemplo: Colocar ordem de compra abaixo do preço atual

**Taker:** Ordem que remove liquidez do livro (market order ou limit que executa imediatamente)
- Exemplo: Comprar pelo preço de mercado

**Estratégia CHiLo:** Como opera com sinais de tendência (compra/venda no fechamento), **assume-se 100% Taker**

---

## 📈 Impacto nas Análises

### Cenário Conservador (sem BNB):
- **Taxa por trade:** 0.05% (Taker)
- **Taxa round-trip:** 0.10% (entrada + saída)

### Cenário Otimista (com BNB):
- **Taxa por trade:** 0.045% (Taker com desconto)
- **Taxa round-trip:** 0.09% (entrada + saída)

### Exemplo Prático:
- **Trade de $10.000:**
  - Entrada: $10.000 × 0.05% = **$5**
  - Saída: $10.000 × 0.05% = **$5**
  - **Total:** $10 por round-trip (0.10%)

- **100 trades/ano:**
  - Custo total: **$1.000** em taxas
  - Impacto no retorno: **-10%** ao ano

---

## ⚠️ Considerações Importantes

1. **Períodos curtos = Mais trades = Mais custos**
   - CHiLo 3: ~100-150 trades/ano = $1.000-1.500 em taxas
   - CHiLo 40: ~10-15 trades/ano = $100-150 em taxas

2. **Slippage não incluído**
   - Diferença entre preço esperado e executado
   - Pode adicionar 0.01-0.05% por trade

3. **Funding rate não incluído**
   - Taxa de financiamento de contratos perpétuos
   - Pode ser positiva ou negativa
   - Varia conforme mercado

4. **Imposto não incluído**
   - 15% sobre ganhos (legislação brasileira)
   - Deve ser considerado no resultado final

---

## 🔧 Implementação nas Análises

### Fórmula de Retorno Líquido:
```
Retorno Líquido = Retorno Bruto - (Número de Trades × Taxa Round-Trip)
```

### Exemplo:
- Retorno Bruto: +20%
- Trades: 100
- Taxa: 0.10% por round-trip
- **Retorno Líquido: +20% - 10% = +10%**

---

## 📝 Notas

- Taxas podem mudar sem aviso prévio
- Volume é calculado nos últimos 30 dias
- Inclui todos os volumes de Futuros USDⓈ-M e COIN-M
- Desconto BNB requer saldo mínimo de BNB na conta
- Contratos ETH/BTC seguem tabela de taxas USDT

**Última atualização:** 28/10/2025
