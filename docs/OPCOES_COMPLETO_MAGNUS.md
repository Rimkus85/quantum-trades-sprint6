# 📊 OPÇÕES - GUIA COMPLETO MAGNUS

## 🎯 ÍNDICE

1. Fundamentos de Opções
2. As Gregas
3. Estratégias de Alavancagem
4. Estratégias de Proteção
5. Estratégias de Renda
6. Estruturas Avançadas
7. Como Magnus Usa Opções
8. Gestão de Risco em Opções

---

# PARTE 1: FUNDAMENTOS DE OPÇÕES

## O Que São Opções?

**Opção** = Direito (não obrigação) de comprar ou vender um ativo a um preço fixo até uma data específica.

**Componentes:**
- **Ativo-objeto:** Ação subjacente (ex: PETR4)
- **Strike (preço de exercício):** Preço fixado
- **Vencimento:** Data limite
- **Prêmio:** Preço da opção

---

## Tipos de Opções

### CALL (Opção de Compra)

**O que é:** Direito de COMPRAR o ativo ao strike

**Quando usar:** Aposta em ALTA do ativo

**Exemplo:**
```
Compra Call PETR4 strike R$ 40
Vencimento: 30 dias
Prêmio: R$ 2,00

Cenário 1 (Alta):
PETR4 vai para R$ 50
Lucro = (R$ 50 - R$ 40) - R$ 2 = R$ 8,00 (+400%)

Cenário 2 (Baixa):
PETR4 vai para R$ 35
Perda = R$ 2,00 (prêmio) (-100%)
```

**Características:**
- Lucro potencial: ILIMITADO
- Perda máxima: Prêmio pago
- Alavancagem: Alta

---

### PUT (Opção de Venda)

**O que é:** Direito de VENDER o ativo ao strike

**Quando usar:** Aposta em QUEDA do ativo ou PROTEÇÃO

**Exemplo:**
```
Compra Put PETR4 strike R$ 40
Vencimento: 30 dias
Prêmio: R$ 2,00

Cenário 1 (Queda):
PETR4 vai para R$ 30
Lucro = (R$ 40 - R$ 30) - R$ 2 = R$ 8,00 (+400%)

Cenário 2 (Alta):
PETR4 vai para R$ 50
Perda = R$ 2,00 (prêmio) (-100%)
```

**Características:**
- Lucro potencial: Strike - Prêmio (limitado a zero)
- Perda máxima: Prêmio pago
- Uso: Especulação ou proteção

---

## Moneyness (Relação Preço vs Strike)

### ITM (In The Money) - Dentro do Dinheiro

**Call ITM:** Preço do ativo > Strike
- Ex: PETR4 a R$ 45, Call strike R$ 40

**Put ITM:** Preço do ativo < Strike
- Ex: PETR4 a R$ 35, Put strike R$ 40

**Características:**
- Valor intrínseco positivo
- Prêmio mais caro
- Delta alto (> 0,50)
- Menos alavancagem, mais segurança

---

### ATM (At The Money) - No Dinheiro

**Call/Put ATM:** Preço do ativo ≈ Strike
- Ex: PETR4 a R$ 40, strike R$ 40

**Características:**
- Sem valor intrínseco (só valor extrínseco)
- Prêmio médio
- Delta ≈ 0,50
- Equilíbrio alavancagem/risco

---

### OTM (Out of The Money) - Fora do Dinheiro

**Call OTM:** Preço do ativo < Strike
- Ex: PETR4 a R$ 35, Call strike R$ 40

**Put OTM:** Preço do ativo > Strike
- Ex: PETR4 a R$ 45, Put strike R$ 40

**Características:**
- Sem valor intrínseco (só valor extrínseco)
- Prêmio barato
- Delta baixo (< 0,50)
- Alta alavancagem, alto risco

---

## Valor Intrínseco vs Extrínseco

### Valor Intrínseco

**O que é:** Quanto a opção vale SE exercida AGORA

**Cálculo:**
- Call: MAX(Preço - Strike, 0)
- Put: MAX(Strike - Preço, 0)

**Exemplo:**
```
PETR4 a R$ 45
Call strike R$ 40

Valor intrínseco = R$ 45 - R$ 40 = R$ 5,00
```

---

### Valor Extrínseco (Tempo)

**O que é:** Prêmio ACIMA do valor intrínseco

**Cálculo:**
- Valor extrínseco = Prêmio - Valor intrínseco

**Exemplo:**
```
PETR4 a R$ 45
Call strike R$ 40
Prêmio = R$ 7,00

Valor intrínseco = R$ 5,00
Valor extrínseco = R$ 7 - R$ 5 = R$ 2,00
```

**Fatores que afetam:**
- Tempo até vencimento (mais tempo = mais valor)
- Volatilidade (mais volátil = mais valor)
- Juros

---

# PARTE 2: AS GREGAS

## Delta (Δ)

**O que é:** Quanto a opção varia para cada R$ 1 de variação do ativo

**Valores:**
- Call: 0 a +1
- Put: 0 a -1

**Interpretação:**
```
Delta 0,50 = Opção sobe/desce R$ 0,50 para cada R$ 1 do ativo
Delta 0,80 = Opção sobe/desce R$ 0,80 para cada R$ 1 do ativo
```

**Uso:**
- Delta alto (> 0,70) = Comporta-se quase como ação
- Delta médio (0,40-0,60) = Equilíbrio
- Delta baixo (< 0,30) = Alta alavancagem, alto risco

**Hedge:**
- Delta 0,50 = Comprar 2 calls equivale a 1 ação
- Delta 1,00 = Comprar 1 call equivale a 1 ação

---

## Gamma (Γ)

**O que é:** Quanto o DELTA varia para cada R$ 1 de variação do ativo

**Interpretação:**
- Gamma alto = Delta muda rápido (opção ATM)
- Gamma baixo = Delta muda devagar (opção ITM/OTM)

**Uso:**
- Gamma alto = Risco de mudança rápida
- Importante para ajuste de hedge

---

## Theta (Θ)

**O que é:** Quanto a opção PERDE por dia (decaimento temporal)

**Valores:**
- Sempre negativo para comprador
- Sempre positivo para vendedor

**Interpretação:**
```
Theta -0,10 = Opção perde R$ 0,10 por dia
Theta -0,50 = Opção perde R$ 0,50 por dia
```

**Comportamento:**
- Acelera próximo ao vencimento
- ATM tem maior Theta

**Uso:**
- Comprador: Theta é inimigo (tempo corrói)
- Vendedor: Theta é amigo (ganha com tempo)

---

## Vega (ν)

**O que é:** Quanto a opção varia para cada 1% de mudança na volatilidade

**Interpretação:**
```
Vega 0,20 = Opção sobe R$ 0,20 se volatilidade subir 1%
```

**Uso:**
- Volatilidade alta = Opções mais caras
- Volatilidade baixa = Opções mais baratas
- Comprador: Quer volatilidade alta
- Vendedor: Quer volatilidade baixa

---

## Rho (ρ)

**O que é:** Quanto a opção varia para cada 1% de mudança nos juros

**Importância:** Menor (juros mudam devagar)

---

# PARTE 3: ESTRATÉGIAS DE ALAVANCAGEM

## 1. COMPRA DE CALL (Long Call)

**Objetivo:** Multiplicar ganhos em movimento de ALTA

**Quando usar:**
- Expectativa de alta forte
- Quer alavancagem
- Capital limitado

**Setup:**
```
Ativo: PETR4 a R$ 40
Expectativa: Alta para R$ 50 em 30 dias

Opção 1 (Comprar ação):
• Investe: R$ 4.000 (100 ações)
• Se sobe para R$ 50: Lucro = R$ 1.000 (+25%)

Opção 2 (Comprar call):
• Call strike R$ 40, prêmio R$ 2
• Investe: R$ 200 (1 lote = 100 calls)
• Se sobe para R$ 50: Lucro = R$ 800 (+400%)
```

**Vantagens:**
- Alavancagem alta
- Risco limitado (só prêmio)
- Capital menor

**Desvantagens:**
- Perde tudo se não subir
- Theta corrói valor
- Precisa subir RÁPIDO

**Gestão:**
- Strike: ATM ou ligeiramente OTM
- Vencimento: 30-60 dias
- Stop loss: -50% do prêmio
- Realização: +100-300%

---

## 2. COMPRA DE PUT (Long Put)

**Objetivo:** Lucrar com QUEDA

**Quando usar:**
- Expectativa de queda forte
- Quer alavancagem na baixa
- Mercado em pânico

**Setup:**
```
Ativo: PETR4 a R$ 40
Expectativa: Queda para R$ 30 em 30 dias

Compra Put strike R$ 40, prêmio R$ 2
Investe: R$ 200

Se cai para R$ 30:
Lucro = (R$ 40 - R$ 30 - R$ 2) × 100 = R$ 800 (+400%)
```

**Vantagens:**
- Alavancagem na queda
- Risco limitado
- Não precisa vender ação descoberto

**Desvantagens:**
- Perde tudo se não cair
- Theta corrói
- Difícil acertar timing

**Gestão:**
- Strike: ATM
- Vencimento: 30-45 dias
- Stop loss: -50%
- Realização: +150-250%

---

## 3. CALL SPREAD (Trava de Alta)

**Objetivo:** Alavancagem com risco controlado

**Como funciona:**
- Compra call strike baixo
- Vende call strike alto
- Reduz custo, limita ganho

**Setup:**
```
PETR4 a R$ 40
Expectativa: Alta moderada para R$ 48

Compra Call strike R$ 40, prêmio R$ 3
Vende Call strike R$ 50, prêmio R$ 1

Custo líquido: R$ 3 - R$ 1 = R$ 2
Lucro máximo: (R$ 50 - R$ 40) - R$ 2 = R$ 8 (+400%)
Perda máxima: R$ 2 (-100%)
```

**Vantagens:**
- Custo menor que call simples
- Risco limitado
- Theta parcialmente neutralizado

**Desvantagens:**
- Lucro limitado
- Precisa subir até strike vendido

**Quando usar:**
- Alta moderada esperada
- Volatilidade alta (prêmios caros)

---

# PARTE 4: ESTRATÉGIAS DE PROTEÇÃO

## 1. PUT PROTETORA (Protective Put / Seguro)

**Objetivo:** Proteger carteira de quedas

**Como funciona:**
- Tem ações
- Compra put
- Se cair, put compensa perda

**Setup:**
```
Carteira: 100 PETR4 a R$ 40 (R$ 4.000)
Medo: Queda para R$ 30

Compra Put strike R$ 38, prêmio R$ 1,50
Custo: R$ 150

Cenário 1 (Queda para R$ 30):
• Perda nas ações: -R$ 1.000
• Ganho na put: (R$ 38 - R$ 30 - R$ 1,50) × 100 = +R$ 650
• Perda líquida: -R$ 350 (protegeu 65%)

Cenário 2 (Sobe para R$ 50):
• Ganho nas ações: +R$ 1.000
• Perda na put: -R$ 150
• Ganho líquido: +R$ 850
```

**Vantagens:**
- Protege contra quedas
- Mantém exposição à alta
- Dorme tranquilo

**Desvantagens:**
- Custa prêmio (seguro)
- Reduz ganho se subir

**Quando usar:**
- Tem ações e quer proteger
- Mercado volátil
- Evento importante (eleições, balanço)

**Gestão:**
- Strike: 5-10% abaixo do preço
- Vencimento: 60-90 dias
- Renova se necessário

---

## 2. COLLAR (Colar)

**Objetivo:** Proteção GRATUITA (ou quase)

**Como funciona:**
- Tem ações
- Compra put (proteção)
- Vende call (financia put)

**Setup:**
```
Carteira: 100 PETR4 a R$ 40

Compra Put strike R$ 36, prêmio R$ 1,50
Vende Call strike R$ 44, prêmio R$ 1,50

Custo líquido: R$ 0 (collar zero-cost)

Cenário 1 (Queda para R$ 30):
• Perda limitada a R$ 4 por ação (R$ 40 - R$ 36)

Cenário 2 (Sobe para R$ 50):
• Ganho limitado a R$ 4 por ação (R$ 44 - R$ 40)
• Call vendida trava ganho

Cenário 3 (Fica entre R$ 36-44):
• Sem custo, sem ganho/perda extra
```

**Vantagens:**
- Proteção gratuita
- Risco limitado

**Desvantagens:**
- Ganho também limitado
- "Vende" potencial de alta

**Quando usar:**
- Quer proteção sem custo
- Não espera alta forte
- Período de incerteza

---

## 3. PUT SPREAD (Trava de Baixa como Hedge)

**Objetivo:** Proteção mais barata que put simples

**Como funciona:**
- Compra put strike alto
- Vende put strike baixo
- Reduz custo, limita proteção

**Setup:**
```
Carteira: 100 PETR4 a R$ 40

Compra Put strike R$ 38, prêmio R$ 2
Vende Put strike R$ 34, prêmio R$ 0,80

Custo líquido: R$ 1,20

Cenário (Queda para R$ 30):
• Perda nas ações: -R$ 1.000
• Ganho na trava: (R$ 38 - R$ 34) - R$ 1,20 = R$ 2,80 × 100 = R$ 280
• Proteção parcial
```

**Vantagens:**
- Mais barato que put simples
- Alguma proteção

**Desvantagens:**
- Proteção limitada
- Complexo

---

# PARTE 5: ESTRATÉGIAS DE RENDA

## 1. VENDA COBERTA (Covered Call)

**Objetivo:** Gerar renda extra com ações que já tem

**Como funciona:**
- Tem ações
- Vende call OTM
- Recebe prêmio
- Se não subir até strike, embolsa prêmio

**Setup:**
```
Carteira: 100 PETR4 a R$ 40

Vende Call strike R$ 44, prêmio R$ 1,50
Recebe: R$ 150

Cenário 1 (Fica em R$ 42):
• Ganho nas ações: +R$ 200
• Embolsa prêmio: +R$ 150
• Total: +R$ 350 (+8,75% em 30 dias)

Cenário 2 (Sobe para R$ 48):
• Ações "chamadas" a R$ 44
• Ganho: (R$ 44 - R$ 40) + R$ 1,50 = R$ 5,50 (+13,75%)
• Perde alta acima de R$ 44

Cenário 3 (Cai para R$ 35):
• Perda nas ações: -R$ 500
• Prêmio compensa: +R$ 150
• Perda líquida: -R$ 350 (-8,75%)
```

**Vantagens:**
- Renda extra mensal
- Reduz custo médio
- Funciona em lateralização

**Desvantagens:**
- Limita ganho se subir forte
- Não protege de quedas

**Quando usar:**
- Tem ações e quer renda
- Mercado lateral ou alta moderada
- Não espera alta forte

**Gestão:**
- Strike: 5-10% acima do preço (OTM)
- Vencimento: 30-45 dias
- Renovar mensalmente
- Se "chamado", aceita ou recompra

---

## 2. CASH-SECURED PUT (Put Vendida com Garantia)

**Objetivo:** "Ser pago para comprar barato"

**Como funciona:**
- Quer comprar ação a preço menor
- Vende put no strike desejado
- Recebe prêmio
- Se cair, compra barato
- Se não cair, embolsa prêmio

**Setup:**
```
Quer comprar PETR4, mas acha R$ 40 caro
Preço justo: R$ 36

Vende Put strike R$ 36, prêmio R$ 1,50
Recebe: R$ 150
Reserva: R$ 3.600 (para comprar se exercida)

Cenário 1 (Cai para R$ 34):
• Compra PETR4 a R$ 36 (exercida)
• Custo real: R$ 36 - R$ 1,50 = R$ 34,50
• Comprou no preço que queria!

Cenário 2 (Fica em R$ 40):
• Put expira sem valor
• Embolsa R$ 150 (+4,17% em 30 dias)
• Repete no mês seguinte
```

**Vantagens:**
- Renda enquanto aguarda preço
- Compra com desconto se cair
- Ganha se não cair

**Desvantagens:**
- Capital parado (reserva)
- Pode cair muito abaixo do strike

**Quando usar:**
- Quer comprar ação específica
- Acha preço atual caro
- Tem capital disponível

---

## 3. IRON CONDOR (Condor de Ferro)

**Objetivo:** Lucrar com lateralização

**Como funciona:**
- Vende call OTM + put OTM (recebe prêmio)
- Compra call mais OTM + put mais OTM (proteção)
- Lucra se ficar entre os strikes vendidos

**Setup:**
```
PETR4 a R$ 40
Expectativa: Lateral entre R$ 36-44

Vende Put strike R$ 38, prêmio R$ 1,50
Compra Put strike R$ 34, prêmio R$ 0,50

Vende Call strike R$ 42, prêmio R$ 1,50
Compra Call strike R$ 46, prêmio R$ 0,50

Crédito líquido: (R$ 1,50 + R$ 1,50) - (R$ 0,50 + R$ 0,50) = R$ 2,00
Lucro máximo: R$ 200 (se ficar entre R$ 38-42)
Perda máxima: R$ 200 (se sair muito da faixa)
```

**Vantagens:**
- Lucra com lateral
- Theta positivo (tempo ajuda)
- Risco definido

**Desvantagens:**
- Lucro limitado
- Perde se romper faixa
- Complexo

**Quando usar:**
- Mercado lateral
- Baixa volatilidade esperada
- Trader experiente

---

# PARTE 6: ESTRUTURAS AVANÇADAS

## 1. BUTTERFLY (Borboleta)

**Objetivo:** Lucrar se ficar exatamente no strike central

**Setup:**
```
Compra 1 call strike R$ 38
Vende 2 calls strike R$ 40
Compra 1 call strike R$ 42

Lucro máximo: Se PETR4 ficar exatamente em R$ 40
```

**Uso:** Aposta em preço específico

---

## 2. STRADDLE (Compra de Volatilidade)

**Objetivo:** Lucrar com movimento forte (qualquer direção)

**Setup:**
```
Compra Call strike R$ 40
Compra Put strike R$ 40

Lucra se:
• Subir MUITO (call ganha)
• Cair MUITO (put ganha)

Perde se:
• Ficar parado (ambas perdem valor)
```

**Quando usar:**
- Evento importante (balanço, eleição)
- Espera movimento forte
- Não sabe direção

---

## 3. STRANGLE (Straddle Mais Barato)

**Objetivo:** Igual straddle, mas mais barato

**Setup:**
```
Compra Call strike R$ 42 (OTM)
Compra Put strike R$ 38 (OTM)

Mais barato que straddle
Precisa de movimento MAIOR para lucrar
```

---

## 4. CALENDAR SPREAD (Spread de Tempo)

**Objetivo:** Lucrar com decaimento temporal diferente

**Setup:**
```
Vende call vencimento próximo
Compra call vencimento longe

Lucra se:
• Call vendida perde valor rápido (Theta)
• Call comprada mantém valor
```

**Uso:** Trader avançado

---

# PARTE 7: COMO MAGNUS USA OPÇÕES

## 🎯 ESTRATÉGIA MAGNUS - OPÇÕES

### REGRA GERAL

**Opções = 10-20% da carteira total**

**Divisão:**
- 5-10%: Alavancagem (calls)
- 5-10%: Proteção (puts)
- 0-5%: Renda (vendas cobertas)

---

### USO 1: ALAVANCAGEM (Pílulas com Calls)

**Quando:**
- Identificou oportunidade de alta forte
- Quer multiplicar ganho
- Prazo curto (2-8 semanas)

**Setup Magnus:**
```
SITUAÇÃO:
• Small cap rompendo base
• Fibonacci 50% após rompimento
• Volume 5x
• Fundamentos ok

AÇÃO:
• Compra call ATM ou ligeiramente OTM
• Vencimento: 45-60 dias
• Alocação: 1-2% da carteira
• Stop loss: -50% do prêmio
• Alvo: +150-300%

EXEMPLO:
Carteira: R$ 100.000
Aloca: R$ 2.000 em calls LWSA3

Se der certo (+200%): Ganha R$ 4.000
Se der errado (-100%): Perde R$ 2.000
```

**Gestão:**
- Máximo 3 posições simultâneas
- Realiza parcial em +100%
- Trailing stop após +150%

---

### USO 2: PROTEÇÃO (Hedge de Carteira)

**Quando:**
- Mercado volátil
- Evento importante
- Quer dormir tranquilo

**Setup Magnus:**
```
SITUAÇÃO:
• Carteira: R$ 100.000 em ações
• Eleições em 30 dias
• Medo de queda

AÇÃO:
• Compra puts ATM ou ligeiramente OTM
• Vencimento: Após evento
• Alocação: 2-5% da carteira
• Strike: 10% abaixo do preço

EXEMPLO:
Compra puts IBOV strike 120.000
Prêmio: R$ 3.000 (3% da carteira)

Se cair 15%:
• Perda na carteira: -R$ 15.000
• Ganho nas puts: ~R$ 8.000
• Perda líquida: -R$ 7.000 (protegeu 53%)

Se subir:
• Ganho na carteira: +R$ 10.000
• Perda nas puts: -R$ 3.000
• Ganho líquido: +R$ 7.000
```

**Gestão:**
- Renova se evento se estender
- Aceita custo como "seguro"
- Não espera lucrar com put

---

### USO 3: RENDA (Venda Coberta)

**Quando:**
- Tem ações blue chip
- Mercado lateral
- Quer renda extra

**Setup Magnus:**
```
SITUAÇÃO:
• Tem 1.000 PETR4 a R$ 40
• Mercado lateral
• Não espera alta forte

AÇÃO:
• Vende 10 calls strike R$ 44 (10% acima)
• Vencimento: 30 dias
• Prêmio: R$ 1,50 por ação
• Recebe: R$ 1.500

RESULTADO MENSAL:
• Se ficar abaixo de R$ 44: Embolsa R$ 1.500 (+3,75%)
• Repete mês seguinte
• Renda anual: ~40-50% (se repetir 12x)

GESTÃO:
• Se subir muito (> R$ 46): Recompra call
• Se "chamado": Aceita venda ou rola
```

**Regras:**
- Só em ações que não quer vender
- Strike 5-10% acima
- Renova mensalmente

---

### USO 4: TRAVA DE ALTA (Call Spread)

**Quando:**
- Alta moderada esperada
- Volatilidade alta (calls caras)
- Quer reduzir custo

**Setup Magnus:**
```
SITUAÇÃO:
• VALE3 a R$ 60
• Expectativa: R$ 70 em 60 dias
• Call ATM muito cara (R$ 5)

AÇÃO:
• Compra call strike R$ 60, prêmio R$ 5
• Vende call strike R$ 70, prêmio R$ 2
• Custo líquido: R$ 3

RESULTADO:
• Se chegar a R$ 70+: Lucro = R$ 7 (+233%)
• Se ficar em R$ 60: Perda = R$ 3 (-100%)
• Breakeven: R$ 63
```

**Vantagens vs Call Simples:**
- Custo 40% menor (R$ 3 vs R$ 5)
- Lucro limitado, mas aceitável
- Menos exposição a Theta

---

## 🎯 MATRIZ DE DECISÃO MAGNUS - OPÇÕES

| Objetivo | Estratégia | Alocação | Prazo |
|----------|-----------|----------|-------|
| Multiplicar ganho | Long Call | 1-2% | 30-60d |
| Proteger carteira | Protective Put | 2-5% | 60-90d |
| Renda mensal | Covered Call | 5-10% | 30d |
| Alta moderada | Call Spread | 2-3% | 45-60d |
| Evento importante | Straddle | 1-2% | Até evento |
| Proteção barata | Put Spread | 2-3% | 60d |

---

# PARTE 8: GESTÃO DE RISCO EM OPÇÕES

## REGRAS DE OURO MAGNUS

### 1. Limite de Exposição

**Máximo 20% da carteira em opções**

**Divisão:**
- Compras (calls/puts): Máximo 15%
- Vendas cobertas: Sem limite (tem ação)
- Vendas descobertas: NUNCA

---

### 2. Diversificação

**Máximo 3 posições simultâneas em opções especulativas**

**Não concentrar:**
- Mesmo ativo
- Mesmo vencimento
- Mesma estratégia

---

### 3. Stop Loss

**Compra de calls/puts:**
- Stop: -50% do prêmio
- Ou: -2% da carteira total

**Venda coberta:**
- Recompra se subir muito (> 2x prêmio recebido)

---

### 4. Realização de Lucro

**Calls especulativas:**
- Realiza 50% em +100%
- Realiza 30% em +200%
- Deixa 20% correr com trailing stop

**Vendas cobertas:**
- Deixa expirar se OTM
- Recompra se ITM e quer manter ação

---

### 5. Vencimento

**Nunca comprar opções com:**
- Menos de 30 dias (Theta alto)
- Mais de 90 dias (prêmio caro)

**Ideal:**
- 45-60 dias para especulação
- 60-90 dias para proteção

---

### 6. Moneyness

**Para alavancagem (calls):**
- Preferir ATM ou ligeiramente OTM
- Evitar muito OTM (loteria)

**Para proteção (puts):**
- ATM ou ligeiramente OTM
- Strike 5-10% abaixo do preço

**Para renda (vendas):**
- OTM (5-10% fora)
- Delta 0,20-0,30

---

### 7. Volatilidade

**Comprar opções quando:**
- Volatilidade BAIXA (prêmios baratos)
- Espera aumento de volatilidade

**Vender opções quando:**
- Volatilidade ALTA (prêmios caros)
- Espera redução de volatilidade

---

### 8. Theta

**Comprador:**
- Theta é inimigo
- Precisa de movimento RÁPIDO
- Não segurar até vencimento

**Vendedor:**
- Theta é amigo
- Tempo trabalha a favor
- Deixar expirar se OTM

---

## ERROS COMUNS A EVITAR

❌ **Comprar muito OTM** (loteria)
❌ **Segurar até expiração** (Theta máximo)
❌ **Vender descoberto** (risco ilimitado)
❌ **Alocar muito** (> 20% da carteira)
❌ **Ignorar Theta** (tempo corrói)
❌ **Comprar com volatilidade alta** (prêmios caros)
❌ **Não ter stop loss**
❌ **Operar sem entender**

---

## CHECKLIST MAGNUS - ANTES DE OPERAR

✅ Entendo a estratégia?
✅ Risco é aceitável (< 2% da carteira)?
✅ Tenho stop loss definido?
✅ Vencimento adequado (45-60d)?
✅ Volatilidade favorável?
✅ Theta aceitável?
✅ Tenho plano de saída?
✅ Diversificação ok?

**Se todas ✅ → PODE OPERAR**
**Se alguma ❌ → NÃO OPERAR**

---

# CONCLUSÃO

## 🎯 OPÇÕES NO MAGNUS

**Papel das Opções:**
- Complemento (10-20% da carteira)
- Não substitui ações
- Ferramenta tática

**Usos Principais:**
1. **Alavancagem** (pílulas mensais)
2. **Proteção** (hedge de eventos)
3. **Renda** (venda coberta)

**Estratégias Core:**
1. Long Call (alavancagem)
2. Protective Put (proteção)
3. Covered Call (renda)
4. Call Spread (alta moderada)

**Gestão de Risco:**
- Máximo 20% da carteira
- Stop loss sempre
- Diversificação
- Vencimento 45-60 dias

---

**Magnus agora domina opções! 📊✅**

