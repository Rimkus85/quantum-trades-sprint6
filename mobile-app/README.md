# 📱 Magnus Wealth - App Android

## Proxy Binance para Trading Automático

**Versão:** 1.0.0  
**Função:** Ponte entre servidor Manus e Binance usando IP do celular

---

## 🎯 O QUE FAZ

O app funciona como **proxy/ponte**:

```
Servidor Manus → Analisa e decide
       ↓
Envia comando HTTP para App
       ↓
App executa na Binance (seu IP sem bloqueio)
       ↓
Retorna resultado para Manus
```

---

## ✅ VANTAGENS

1. **Usa seu IP** (sem bloqueio Brasil)
2. **Roda em segundo plano** (tela desligada)
3. **Simples** (só recebe e executa)
4. **Seguro** (chaves ficam no celular)
5. **Logs** enviados para Manus

---

## 📦 INSTALAÇÃO

### Opção 1: APK Pronto (Recomendado)

1. Baixe o APK
2. Instale no Android
3. Abra o app
4. Cole API Key e Secret
5. Clique em "Conectar Binance"
6. Pronto!

### Opção 2: Compilar do Código

```bash
cd /home/ubuntu/quantum-trades-sprint6/mobile-app
buildozer android debug
```

---

## ⚙️ CONFIGURAÇÃO

### 1. No App (Celular)

1. Abra o app Magnus Wealth
2. Cole sua **API Key** da Binance
3. Cole seu **API Secret** da Binance
4. Clique em **"Conectar Binance"**
5. Aguarde confirmação: "✅ Online e pronto"

### 2. No Servidor (Manus)

Edite `.env`:

```env
# URL do app no celular
APP_URL=http://192.168.1.XXX:5000
```

**Como descobrir o IP do celular:**
- Android: Configurações → Wi-Fi → IP
- Exemplo: `192.168.1.105`

---

## 🔌 ENDPOINTS DO APP

### GET /health
Verifica se app está online

**Response:**
```json
{
  "status": "online",
  "binance_connected": true
}
```

### POST /execute
Executa ordem na Binance

**Body:**
```json
{
  "action": "open_long",
  "symbol": "BTCUSDT",
  "quantity": 0.001,
  "leverage": 12
}
```

**Actions:**
- `open_long`: Abre posição LONG
- `open_short`: Abre posição SHORT
- `close_position`: Fecha posição

**Response:**
```json
{
  "status": "success",
  "order_id": "12345678",
  "symbol": "BTCUSDT",
  "action": "open_long"
}
```

### GET /positions
Retorna posições abertas

**Response:**
```json
{
  "positions": [
    {
      "symbol": "BTCUSDT",
      "amount": "0.001",
      "entry_price": "109317.00",
      "unrealized_pnl": "12.50"
    }
  ]
}
```

### GET /logs
Retorna últimos 50 logs

---

## 🔒 SEGURANÇA

### ✅ Proteções Implementadas

1. **Chaves no celular** (não vão para servidor)
2. **IP fixo** (cadastrar na Binance)
3. **Margem isolada** (automática)
4. **Logs locais** (auditoria)

### ⚠️ Recomendações

1. **Cadastre IP do Wi-Fi** na Binance API
2. **Não habilite withdrawals** na API
3. **Use Wi-Fi estável** (não 4G)
4. **Mantenha celular carregando**

---

## 🔋 ECONOMIA DE BATERIA

O app é otimizado para rodar 24/7:

- **Servidor leve** (Flask)
- **Sem interface** quando em segundo plano
- **Wake lock** apenas quando necessário
- **Consumo:** ~2-3% bateria/hora

**Recomendação:** Deixar celular na tomada

---

## 📊 MONITORAMENTO

### No App

- Status de conexão
- Últimos 10 logs
- Botão para reconectar

### No Servidor Manus

```python
# Verificar se app está online
trader.verificar_app()

# Ver posições abertas
requests.get(f"{APP_URL}/positions")

# Ver logs do app
requests.get(f"{APP_URL}/logs")
```

---

## 🐛 TROUBLESHOOTING

### App não conecta à Binance

1. Verificar API Key e Secret
2. Verificar permissões da API (Futures habilitado)
3. Verificar IP cadastrado na Binance

### Servidor não alcança o app

1. Verificar se celular e servidor estão na mesma rede
2. Verificar IP do celular
3. Verificar firewall do celular
4. Testar: `curl http://192.168.1.XXX:5000/health`

### App fecha sozinho

1. Desabilitar otimização de bateria para o app
2. Permitir execução em segundo plano
3. Android: Configurações → Apps → Magnus Wealth → Bateria → Sem restrições

---

## 📝 LOGS

### No Celular

- Salvos em: `/sdcard/magnus_logs.txt`
- Últimos 50 no app

### No Servidor

- Salvos em: `/logs/trader.log`
- Incluem comandos enviados e respostas

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Instalar app no celular
2. ✅ Configurar API Keys
3. ✅ Conectar Binance
4. ✅ Anotar IP do celular
5. ✅ Configurar APP_URL no servidor
6. ✅ Testar conexão
7. ✅ Ativar trading automático

---

## 📞 SUPORTE

**Problemas com o app:**
- Verificar logs no celular
- Testar endpoints manualmente
- Verificar conexão de rede

**Problemas com trading:**
- Verificar logs do servidor
- Verificar posições na Binance
- Verificar saldo disponível

---

**Versão:** 1.0.0  
**Data:** 19/10/2025  
**Autor:** Magnus Wealth Team

