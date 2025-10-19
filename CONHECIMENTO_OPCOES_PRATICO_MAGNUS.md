# 📊 Guia Completo e Prático de Opções - Magnus Wealth

> **Objetivo:** Dominar opções do zero com foco em setups práticos, alvos, stops e proteção de carteira.

---

## 📚 PARTE 1: Fundamentos Práticos

### 1.1 O Que São Opções (Explicação Simples)

**Opção = Direito de comprar ou vender algo por um preço combinado**

**Exemplo Real:**
- PETR4 está a R$ 40,00 hoje
- Você compra uma **CALL** (opção de compra) com strike R$ 42,00 por R$ 1,50
- Se PETR4 subir para R$ 45,00, você pode exercer e comprar por R$ 42,00
- **Lucro:** R$ 45,00 - R$ 42,00 - R$ 1,50 = **R$ 1,50 por ação**
- **Retorno:** 100% (investiu R$ 1,50, ganhou R$ 1,50)

Se PETR4 não subir, você perde apenas os R$ 1,50 (prêmio pago).

---

### 1.2 Calls vs Puts

| Tipo | O Que É | Quando Usar | Exemplo |
|------|---------|-------------|---------|
| **CALL** | Direito de **comprar** | Acredita que vai **subir** | PETR4 a R$ 40, compra call R$ 42 |
| **PUT** | Direito de **vender** | Acredita que vai **cair** | VALE3 a R$ 70, compra put R$ 68 |

---

### 1.3 Comprado vs Vendido (Titular vs Lançador)

#### **COMPRADO (Titular)**
- Você **PAGA** o prêmio
- Tem o **DIREITO** de exercer
- **Risco:** Limitado ao prêmio pago
- **Retorno:** Ilimitado (calls) ou alto (puts)

**Exemplo:**
- Compra PETR K420 por R$ 1,50
- Risco máximo: R$ 1,50
- Se PETR4 subir para R$ 50, lucro de R$ 6,50 (433%)

#### **VENDIDO (Lançador)**
- Você **RECEBE** o prêmio
- Tem a **OBRIGAÇÃO** de entregar
- **Risco:** Alto (pode ser ilimitado)
- **Retorno:** Limitado ao prêmio recebido

**Exemplo:**
- Vende PETR K420 por R$ 1,50
- Recebe R$ 1,50 imediatamente
- Se PETR4 subir para R$ 50, prejuízo de R$ 6,50

---

### 1.4 Como Ler a Cadeia de Opções

```
Ativo: PETR4 = R$ 40,00

CALLS                           PUTS
Código    Strike   Prêmio      Código    Strike   Prêmio
PETRC380  38,00    3,20        PETRW380  38,00    0,50
PETRC400  40,00    1,80        PETRW400  40,00    1,50
PETRC420  42,00    0,80        PETRW420  42,00    3,00
```

**Como escolher:**
- **Calls:** Quanto mais longe do preço atual, mais barato (mas mais difícil de lucrar)
- **Puts:** Quanto mais longe do preço atual, mais barato (mas mais difícil de lucrar)

---

### 1.5 Moneyness (ITM, ATM, OTM)

| Tipo | Significado | Call | Put | Prêmio |
|------|-------------|------|-----|--------|
| **ITM** | In The Money (No Dinheiro) | Strike < Preço Atual | Strike > Preço Atual | Alto |
| **ATM** | At The Money (No Preço) | Strike = Preço Atual | Strike = Preço Atual | Médio |
| **OTM** | Out of The Money (Fora) | Strike > Preço Atual | Strike < Preço Atual | Baixo |

**Exemplo (PETR4 = R$ 40,00):**
- Call K38 = ITM (já está no dinheiro, prêmio R$ 3,20)
- Call K40 = ATM (no preço, prêmio R$ 1,80)
- Call K42 = OTM (fora, prêmio R$ 0,80)

**Regra Prática:**
- **ITM:** Mais caro, mais seguro, menos alavancagem
- **OTM:** Mais barato, mais arriscado, mais alavancagem
- **ATM:** Equilíbrio entre risco e retorno

---

### 1.6 Greeks Essenciais (Simplificado)

#### **Delta (Δ)**
- Quanto a opção se move quando o ativo sobe R$ 1,00
- **Call:** 0 a 1 (ex: Delta 0,50 = se PETR4 sobe R$ 1, call sobe R$ 0,50)
- **Put:** 0 a -1 (ex: Delta -0,50 = se PETR4 sobe R$ 1, put cai R$ 0,50)

**Uso Prático:**
- Delta 0,80 = Opção se move quase igual ao ativo (ITM)
- Delta 0,20 = Opção se move pouco (OTM)

#### **Theta (Θ)**
- Quanto você **PERDE por dia** por causa do tempo
- Exemplo: Theta -0,05 = você perde R$ 0,05 por dia

**Uso Prático:**
- **Comprado:** Theta é seu inimigo (você perde todo dia)
- **Vendido:** Theta é seu amigo (você ganha todo dia)

#### **Vega (ν)**
- Quanto a opção se move com a volatilidade
- Exemplo: Vega 0,10 = se volatilidade sobe 1%, opção sobe R$ 0,10

**Uso Prático:**
- Volatilidade alta = Opções mais caras
- Volatilidade baixa = Opções mais baratas

---

## 🎯 PARTE 2: Setups Práticos de Entrada

### Setup 1: Compra de Call em Rompimento 🚀

**Quando Usar:**
- Ativo rompeu resistência importante
- Volume acima da média
- Tendência de alta confirmada

**Como Executar:**
1. Identifique resistência no gráfico
2. Aguarde rompimento com volume
3. Compre call ATM ou ligeiramente OTM
4. Vencimento: 15-30 dias

**Exemplo Real:**
```
PETR4 = R$ 39,50 (resistência em R$ 40,00)
↓
Rompe R$ 40,00 com volume 2x maior
↓
Compra: PETRC420 por R$ 0,80
Alvo: R$ 2,00 (150% de lucro)
Stop: R$ 0,40 (50% de perda)
```

**Gestão:**
- Risco: 3% do capital
- R/R: 1:3 (arrisca 1 para ganhar 3)
- Sai quando: Atingir alvo OU virar tendência de baixa

---

### Setup 2: Compra de Put em Queda 📉

**Quando Usar:**
- Ativo perdeu suporte importante
- Padrão de reversão de baixa (topo duplo, ombro-cabeça-ombro)
- Notícias negativas

**Como Executar:**
1. Identifique suporte no gráfico
2. Aguarde perda do suporte
3. Compre put ATM ou ligeiramente OTM
4. Vencimento: 15-30 dias

**Exemplo Real:**
```
VALE3 = R$ 70,50 (suporte em R$ 70,00)
↓
Perde R$ 70,00 com volume alto
↓
Compra: VALEW680 por R$ 1,20
Alvo: R$ 3,00 (150% de lucro)
Stop: R$ 0,60 (50% de perda)
```

**Gestão:**
- Risco: 3% do capital
- R/R: 1:2,5
- Sai quando: Atingir alvo OU encontrar novo suporte

---

### Setup 3: Venda Coberta (Proteção + Renda) 💰

**Quando Usar:**
- Você TEM as ações na carteira
- Mercado lateral ou leve alta
- Quer gerar renda extra

**Como Executar:**
1. Possui 100 ações de PETR4 a R$ 40,00
2. Vende 1 call OTM (ex: K42) por R$ 0,80
3. Recebe R$ 80,00 de prêmio
4. Se PETR4 não subir de R$ 42, você fica com o prêmio

**Exemplo Real:**
```
Carteira: 1.000 ações PETR4 a R$ 40,00 = R$ 40.000
↓
Vende: 10 calls PETRC420 por R$ 0,80 = Recebe R$ 800
↓
Cenário 1: PETR4 fica em R$ 41,00 no vencimento
→ Você fica com as ações + R$ 800 (2% de retorno extra)

Cenário 2: PETR4 sobe para R$ 44,00
→ Suas ações são exercidas a R$ 42,00
→ Lucro: R$ 2,00 por ação + R$ 0,80 de prêmio = R$ 2,80 (7%)
```

**Gestão:**
- Risco: Limitado (você já tem as ações)
- Retorno: 1-3% ao mês
- Ideal para: Carteira de longo prazo

---

### Setup 4: Trava de Alta (Bull Call Spread) 📊

**Quando Usar:**
- Acredita em alta moderada
- Quer reduzir custo da operação
- Volatilidade está alta

**Como Executar:**
1. Compra call ATM
2. Vende call OTM (mais longe)
3. Reduz custo mas limita ganho

**Exemplo Real:**
```
PETR4 = R$ 40,00
↓
Compra: PETRC400 por R$ 1,80
Vende: PETRC440 por R$ 0,60
↓
Custo líquido: R$ 1,20
Ganho máximo: R$ 2,80 (se PETR4 chegar em R$ 44)
Retorno máximo: 233%
```

**Gestão:**
- Risco: R$ 1,20 (custo da trava)
- Retorno: R$ 2,80 (ganho máximo)
- R/R: 1:2,3

---

### Setup 5: Financiamento (Zerar Custo) 🎁

**Quando Usar:**
- Comprou uma call e está com lucro
- Quer travar lucro mas manter posição
- Mercado ainda pode subir mais

**Como Executar:**
1. Comprou call por R$ 1,00
2. Call valorizou para R$ 2,00
3. Vende call mais OTM por R$ 1,00
4. Recupera investimento inicial

**Exemplo Real:**
```
Dia 1: Compra PETRC400 por R$ 1,00
↓
Dia 5: PETRC400 vale R$ 2,00 (100% de lucro)
↓
Vende PETRC440 por R$ 1,00
↓
Resultado: Custo zerado, ainda tem PETRC400 aberta
Se PETR4 subir mais, continua lucrando
Se cair, não perde nada (já recuperou investimento)
```

**Gestão:**
- Risco: Zero (já recuperou investimento)
- Retorno: Ilimitado até o strike vendido
- Ideal para: Operações que já deram certo

---

## 🛡️ PARTE 3: Proteção de Carteira (Hedge)

### 3.1 Compra de Put Protetora

**Objetivo:** Proteger carteira de ações contra quedas

**Como Funciona:**
- Você tem R$ 100.000 em ações
- Compra puts do índice (IBOV) ou das próprias ações
- Se mercado cair, puts sobem e compensam perda

**Exemplo Real:**
```
Carteira: R$ 100.000 em ações (PETR4, VALE3, ITUB4)
IBOV = 120.000 pontos
↓
Compra: 10 puts IBOVW120 por R$ 500 cada = R$ 5.000
↓
Cenário 1: IBOV cai para 110.000 (-8,3%)
→ Carteira perde R$ 8.300
→ Puts valem R$ 10.000 (lucro de R$ 5.000)
→ Perda líquida: R$ 3.300 (3,3% ao invés de 8,3%)

Cenário 2: IBOV sobe para 130.000 (+8,3%)
→ Carteira ganha R$ 8.300
→ Puts perdem R$ 5.000
→ Ganho líquido: R$ 3.300 (3,3% ao invés de 8,3%)
```

**Gestão:**
- Custo: 2-5% do patrimônio por ano
- Proteção: 50-80% das quedas
- Renovar: A cada 2-3 meses

---

### 3.2 Collar (Proteção + Renda)

**Objetivo:** Proteger carteira SEM CUSTO (ou com custo reduzido)

**Como Funciona:**
1. Compra put protetora (paga prêmio)
2. Vende call OTM (recebe prêmio)
3. Prêmio recebido compensa prêmio pago

**Exemplo Real:**
```
Carteira: 1.000 ações PETR4 a R$ 40,00 = R$ 40.000
↓
Compra: 10 puts PETRW380 por R$ 0,80 = Paga R$ 800
Vende: 10 calls PETRC440 por R$ 0,80 = Recebe R$ 800
↓
Custo líquido: R$ 0 (zerou)

Proteção: Se PETR4 cair abaixo de R$ 38, você está protegido
Limitação: Se PETR4 subir acima de R$ 44, você vende as ações
```

**Gestão:**
- Custo: Zero ou muito baixo
- Proteção: Boa (limita perdas)
- Desvantagem: Limita ganhos também

---

### 3.3 Put Spread (Proteção Barata)

**Objetivo:** Proteger carteira com custo reduzido

**Como Funciona:**
1. Compra put ATM (proteção)
2. Vende put OTM (reduz custo)
3. Proteção parcial mas mais barata

**Exemplo Real:**
```
Carteira: R$ 100.000 em ações
IBOV = 120.000
↓
Compra: IBOVW120 por R$ 1.000
Vende: IBOVW110 por R$ 400
↓
Custo líquido: R$ 600

Proteção: Se IBOV cair até 110.000 (-8,3%)
Abaixo de 110.000, proteção para de funcionar
```

**Gestão:**
- Custo: 40-60% menor que put simples
- Proteção: Parcial (até o strike vendido)
- Ideal para: Quem quer proteção barata

---

## 📋 PARTE 4: Alvos e Stops por Setup

### Tabela de Gestão

| Setup | Alvo | Stop | R/R | Holding Time |
|-------|------|------|-----|--------------|
| Compra Call Rompimento | 100-200% | 50% | 1:2 ou 1:3 | 5-15 dias |
| Compra Put Queda | 100-150% | 50% | 1:2 | 3-10 dias |
| Venda Coberta | 50-100% do prêmio | Recompra se ativo cair 5% | 1:1 | Até vencimento |
| Trava de Alta | Ganho máximo | Perda máxima | 1:2 | Até vencimento |
| Financiamento | Ilimitado | Zero (já zerou custo) | ∞ | Até vencimento |
| Put Protetora | N/A (é seguro) | Deixa expirar | N/A | 60-90 dias |

---

## 🎯 PARTE 5: Checklist de Operação

### Antes de Entrar

- [ ] Analisei o gráfico do ativo?
- [ ] Identifiquei suporte/resistência?
- [ ] Confirmei volume acima da média?
- [ ] Escolhi o strike correto (ATM ou OTM)?
- [ ] Verifiquei o vencimento (15-30 dias)?
- [ ] Calculei o risco (3% do capital)?
- [ ] Defini alvo e stop?
- [ ] Verifiquei a volatilidade implícita?

### Durante a Operação

- [ ] Monitorei o preço do ativo?
- [ ] Verifiquei se mantém a tendência?
- [ ] Ajustei stop se necessário?
- [ ] Considerei financiar se lucro > 100%?

### Ao Sair

- [ ] Atingi o alvo?
- [ ] Bateu o stop?
- [ ] Virou a tendência?
- [ ] Faltam menos de 7 dias para vencimento?
- [ ] Registrei a operação para análise?

---

## 📊 PARTE 6: Estratégia de Gestão de Risco

### Regras de Ouro

1. **Nunca arrisque mais de 3% do capital por operação**
   - Capital: R$ 10.000 → Risco máximo: R$ 300

2. **Máximo de 5 operações simultâneas**
   - Evita overtrading
   - Mantém foco

3. **Stop loss SEMPRE**
   - Comprado: 50% de perda
   - Vendido: Recompra se ativo se mover 5% contra você

4. **Take profit parcial**
   - Lucro de 100%: Realiza 50%, deixa 50% correr
   - Lucro de 200%: Realiza 75%, deixa 25% correr

5. **Evite opções com menos de 7 dias para vencimento**
   - Theta acelera muito
   - Risco de perda total aumenta

---

## 🧠 PARTE 7: Erros Comuns e Como Evitar

### Erro 1: Comprar Opção Muito OTM
**Problema:** Opção muito barata mas ativo precisa subir MUITO  
**Solução:** Prefira ATM ou ligeiramente OTM

### Erro 2: Segurar Até o Vencimento
**Problema:** Theta corrói o valor rapidamente  
**Solução:** Saia com 7-10 dias de antecedência

### Erro 3: Não Usar Stop Loss
**Problema:** Perda de 100% do capital investido  
**Solução:** SEMPRE defina stop de 50%

### Erro 4: Operar Sem Análise
**Problema:** Entrar "no feeling" sem setup  
**Solução:** Use os setups documentados

### Erro 5: Vender Descoberto
**Problema:** Risco ilimitado  
**Solução:** Sempre venda coberto ou use travas

---

## 📈 PARTE 8: Exemplos de Operações Reais

### Operação 1: Day Trade com Call

```
Data: 15/10/2025
Ativo: PETR4 = R$ 39,80
Setup: Rompimento de R$ 40,00

09:30 - PETR4 rompe R$ 40,00 com volume
09:35 - Compra PETRC400 por R$ 1,50
10:15 - PETRC400 em R$ 2,00 (+33%)
10:20 - Realiza 50% em R$ 2,00
11:30 - PETRC400 em R$ 2,80 (+87%)
11:35 - Realiza restante em R$ 2,80

Resultado: 
- 50% vendido em R$ 2,00 = +33%
- 50% vendido em R$ 2,80 = +87%
- Média: +60% no dia
```

### Operação 2: Swing Trade com Put

```
Data: 10/10/2025
Ativo: VALE3 = R$ 71,00
Setup: Topo duplo + perda de suporte

Dia 1 - Compra VALEW700 por R$ 1,80
Dia 3 - VALE3 cai para R$ 68,50
Dia 3 - VALEW700 em R$ 3,20 (+78%)
Dia 3 - Realiza em R$ 3,20

Resultado: +78% em 3 dias
```

### Operação 3: Venda Coberta Mensal

```
Mês: Outubro/2025
Carteira: 1.000 ações ITUB4 a R$ 28,00

Dia 1 - Vende 10 calls ITUBC300 por R$ 0,60 = Recebe R$ 600
Dia 30 - ITUB4 fecha em R$ 29,50 (calls expiram sem valor)

Resultado: 
- Ganho com ações: +5,4% (R$ 28 → R$ 29,50)
- Ganho com calls: +2,1% (R$ 600 / R$ 28.000)
- Total: +7,5% no mês
```

---

## 🎓 PARTE 9: Recursos e Ferramentas

### Plataformas Recomendadas
- **ProfitChart** (análise técnica + execução)
- **TradeMap** (análise de opções)
- **OpLab** (calculadora de opções)

### Indicadores Úteis
- **Médias Móveis** (20, 50, 200)
- **RSI** (sobrecompra/sobrevenda)
- **Volume** (confirmação de movimentos)
- **Bandas de Bollinger** (volatilidade)

### Sites de Análise
- **B3** (cadeia de opções oficial)
- **Investing.com** (cotações em tempo real)
- **TradingView** (gráficos avançados)

---

## 🚀 PARTE 10: Plano de Ação Imediato

### Semana 1: Fundamentos
- [ ] Ler Parte 1 completa
- [ ] Abrir conta em corretora (se não tiver)
- [ ] Acessar ProfitChart
- [ ] Estudar cadeia de opções de 3 ativos

### Semana 2: Simulação
- [ ] Escolher 1 setup (recomendo Setup 1)
- [ ] Simular 10 operações no papel
- [ ] Calcular resultados
- [ ] Ajustar estratégia

### Semana 3: Primeira Operação Real
- [ ] Separar R$ 300-500 para teste
- [ ] Executar Setup 1 ou Setup 2
- [ ] Seguir TODAS as regras
- [ ] Registrar resultado

### Semana 4: Proteção
- [ ] Implementar put protetora na carteira
- [ ] Testar collar
- [ ] Avaliar custo x benefício

---

## 📝 Conclusão

Opções são uma ferramenta **poderosa** mas exigem:
- ✅ Conhecimento técnico
- ✅ Disciplina de gestão
- ✅ Controle emocional
- ✅ Prática constante

**Comece pequeno, aprenda rápido, escale devagar.**

O Magnus Brain agora tem todo esse conhecimento integrado e vai usar nas análises e recomendações! 🧠🚀

---

**Última atualização:** 19/10/2025  
**Versão:** 1.0  
**Autor:** Magnus Wealth AI

