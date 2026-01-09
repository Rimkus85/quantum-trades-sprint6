# Análise do Vídeo de Referência - App Financeiro

## Características Visuais Identificadas

### 1. **Paleta de Cores**
- Fundo: Azul escuro profundo (#0A192F similar)
- Elementos de destaque: Azul neon/ciano brilhante
- Texto primário: Branco
- Texto secundário: Cinza claro
- Botões: Branco/cinza claro com texto escuro

### 2. **Transições e Animações**
- **Modal de ofertas**: Slide vertical suave de baixo para cima
- **Troca de abas**: Fade + slide horizontal (Conta Genial ↔ Investimentos)
- **Cards expansíveis**: Animação de altura com easing suave
- **Elementos de lista**: Aparecem com fade-in sequencial
- **Botões flutuantes**: Scale + bounce ao pressionar

### 3. **Efeitos Visuais Premium**
- **Glassmorphism**: Cards com efeito de vidro fosco
- **Gradientes sutis**: Bordas com brilho azul neon
- **Sombras profundas**: Drop shadows para criar profundidade
- **Blur backgrounds**: Fundo desfocado em modals
- **Indicadores de progresso**: Dots animados para carrosséis

### 4. **Interações**
- **Pull-to-refresh**: Animação circular suave
- **Swipe entre telas**: Gesture horizontal fluido
- **Tap feedback**: Scale 0.95 com haptic
- **Long press**: Vibração + menu contextual
- **Scroll parallax**: Header com efeito de profundidade

### 5. **Layout e Espaçamento**
- Padding generoso (20-24px)
- Cards com border-radius grande (16-20px)
- Espaçamento vertical consistente (16px entre elementos)
- Tipografia hierárquica clara
- Bottom sheet para ações secundárias

## Implementações Necessárias

### ✅ Já Implementado
- Cores azul escuro de fundo
- Transições fade+slide entre telas
- Animações de entrada de componentes
- Scale animation em pressables

### 🔄 A Melhorar
1. **Adicionar glassmorphism nos cards**
   - Backdrop blur
   - Bordas com gradiente sutil
   
2. **Melhorar transições de modal**
   - Slide de baixo para cima
   - Backdrop com fade
   
3. **Adicionar parallax no scroll**
   - Header com efeito de profundidade
   
4. **Implementar bottom sheet**
   - Para detalhes de operações
   - Para filtros

5. **Adicionar micro-interações**
   - Bounce em botões importantes
   - Shimmer em loading states
   - Progress indicators animados

## Referências de Timing
- Fade: 300-400ms
- Slide: 350-450ms
- Scale: 150-200ms
- Bounce: 400-500ms com spring
- Easing: cubic-bezier(0.4, 0.0, 0.2, 1)
