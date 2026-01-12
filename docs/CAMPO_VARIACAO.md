# Campo "Variação" nas Operações

## O que é?

O campo `changePercent` (exibido como "Variação" na interface) representa a **variação percentual do preço do ativo desde a data da operação até o momento atual**.

## Exemplo Prático

Se você comprou PETR4 a R$ 33,25 no dia 05/01/2026 e hoje o preço está em R$ 33,85:

```
Variação = ((Preço Atual - Preço da Operação) / Preço da Operação) × 100
Variação = ((33,85 - 33,25) / 33,25) × 100
Variação = +1,8%
```

## Interpretação

- **Positivo (+)**: O ativo valorizou desde a operação → Lucro potencial (compra) ou prejuízo (venda)
- **Negativo (-)**: O ativo desvalorizou desde a operação → Prejuízo potencial (compra) ou lucro (venda)
- **Zero (0)**: O preço está igual ao da operação

## Cor na Interface

- **Verde**: Variação positiva (> 0%)
- **Vermelho**: Variação negativa (< 0%)
- **Cinza**: Sem variação (= 0%)

## Dados Mockados vs Produção

### Mockado (Atual)
```typescript
{
  id: "op1",
  ticker: "PETR4",
  type: "compra",
  quantity: 500,
  price: 33.25,
  total: 16625.00,
  date: "2026-01-05T11:15:00",
  status: "executada",
  changePercent: 1.8,  // ← Valor fixo mockado
}
```

### Produção (Futuro)
```typescript
// O backend calculará em tempo real:
const currentPrice = await getMarketPrice(ticker);
const changePercent = ((currentPrice - operation.price) / operation.price) * 100;
```

## Implementação em Produção

Quando integrar com APIs reais, o cálculo será:

1. **Buscar preço atual** do ativo via API de mercado (B3, Binance, etc.)
2. **Calcular variação** comparando com o preço da operação
3. **Atualizar em tempo real** (websocket ou polling)

### Exemplo de Endpoint

```typescript
// GET /api/operations/:id/variation
{
  "operationId": "op1",
  "ticker": "PETR4",
  "operationPrice": 33.25,
  "currentPrice": 33.85,
  "changePercent": 1.8,
  "changeValue": 0.60,
  "lastUpdate": "2026-01-12T10:30:00Z"
}
```

## Observações Importantes

1. **Opções**: Para opções, a variação considera o prêmio (preço da opção), não o preço do ativo subjacente
2. **Cripto**: Usa preço em tempo real de exchanges (alta volatilidade)
3. **Ações**: Usa último preço negociado na B3 (pode ter delay de 15min em dados gratuitos)
4. **Horário de Mercado**: Fora do horário de negociação, usa o último preço de fechamento

## Próximos Passos

- [ ] Integrar com API de cotações em tempo real
- [ ] Implementar websocket para atualização automática
- [ ] Adicionar indicador de "última atualização"
- [ ] Considerar custos de corretagem no cálculo de lucro/prejuízo real
