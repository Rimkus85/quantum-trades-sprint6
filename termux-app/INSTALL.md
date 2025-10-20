# 📱 Magnus Wealth - Instalação Termux

## Guia Completo de Instalação

---

## 📋 PASSO 1: Instalar Termux

1. Abra a **Play Store**
2. Busque por **"Termux"**
3. Instale o app oficial (F-Droid é melhor, mas Play Store funciona)
4. Abra o Termux

---

## 🔧 PASSO 2: Configurar Termux

Cole os comandos abaixo no Termux (um de cada vez):

```bash
# Atualizar pacotes
pkg update -y && pkg upgrade -y

# Instalar Python
pkg install python -y

# Instalar dependências
pip install flask python-binance

# Permitir acesso ao armazenamento
termux-setup-storage

# Criar diretório
mkdir -p ~/magnus
cd ~/magnus
```

---

## 📥 PASSO 3: Baixar o App

```bash
# Baixar script
curl -o magnus_proxy.py https://raw.githubusercontent.com/Rimkus85/quantum-trades-sprint6/master/termux-app/magnus_proxy.py

# Dar permissão de execução
chmod +x magnus_proxy.py
```

---

## 🚀 PASSO 4: Executar

```bash
# Rodar o app
python magnus_proxy.py
```

Você verá:
```
═══════════════════════════════════════════════════
  MAGNUS WEALTH - PROXY BINANCE TERMUX
  Versão 1.0.0
═══════════════════════════════════════════════════

⚠️ Configure suas API Keys em /config

✓ Servidor iniciado em http://0.0.0.0:5000
✓ Acesse pelo navegador para configurar

📱 Mantenha o Termux aberto em segundo plano
🔋 Recomendado: deixar celular carregando
```

---

## 🌐 PASSO 5: Configurar API Keys

### Opção A: Pelo Navegador (Recomendado)

1. Descubra o IP do celular:
   ```bash
   ifconfig wlan0 | grep inet
   ```
   Exemplo: `192.168.1.105`

2. No navegador do celular, acesse:
   ```
   http://192.168.1.105:5000/config
   ```

3. Cole sua **API Key** e **API Secret**
4. Clique em **Conectar**
5. Aguarde: "✓ Conectado à Binance com sucesso"

### Opção B: Via Comando

```bash
curl -X POST http://localhost:5000/config \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "SUA_API_KEY_AQUI",
    "api_secret": "SEU_API_SECRET_AQUI"
  }'
```

---

## ✅ PASSO 6: Verificar Conexão

```bash
# Testar health
curl http://localhost:5000/health
```

Resposta esperada:
```json
{
  "status": "online",
  "binance_connected": true,
  "timestamp": "2025-10-19T23:00:00"
}
```

---

## 🔄 PASSO 7: Manter Rodando em Segundo Plano

### Opção A: Termux Wake Lock (Simples)

1. Instale Termux:API:
   ```bash
   pkg install termux-api -y
   ```

2. Rode com wake lock:
   ```bash
   termux-wake-lock
   python magnus_proxy.py
   ```

3. Minimize o Termux (não feche!)

### Opção B: Tmux (Avançado)

```bash
# Instalar tmux
pkg install tmux -y

# Criar sessão
tmux new -s magnus

# Rodar app
python magnus_proxy.py

# Desanexar: Ctrl+B depois D
# Reanexar: tmux attach -t magnus
```

---

## 🔗 PASSO 8: Conectar ao Servidor Manus

No servidor Manus, configure a URL do celular:

```bash
# Editar .env
nano /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend/.env
```

Adicionar:
```env
APP_URL=http://192.168.1.105:5000
```

(Substitua pelo IP do seu celular)

---

## 🧪 PASSO 9: Testar Integração

No servidor Manus:

```bash
cd /home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
python3 -c "
import requests
url = 'http://192.168.1.105:5000/health'
print(requests.get(url).json())
"
```

Se retornar `binance_connected: true`, está funcionando! ✅

---

## 🎯 PASSO 10: Ativar Automação

Agora o sistema está completo:

1. **Servidor Manus** roda análise às 21h
2. **Decide** comprar/vender
3. **Envia comando** para seu celular
4. **Termux executa** na Binance (seu IP)
5. **Retorna resultado** para Manus
6. **Manus notifica** no Telegram

**100% automático!** 🚀

---

## 📊 MONITORAMENTO

### Ver Logs

```bash
# No Termux
tail -f ~/magnus/magnus_proxy.log
```

### Ver Posições

No navegador:
```
http://192.168.1.105:5000/positions
```

### Status

```
http://192.168.1.105:5000/
```

---

## 🔋 DICAS IMPORTANTES

1. **Deixe celular carregando** sempre que possível
2. **Não feche o Termux** (minimize apenas)
3. **Mantenha Wi-Fi conectado** (não use dados móveis)
4. **Desative economia de bateria** para o Termux
5. **Cadastre IP do Wi-Fi** na Binance API

---

## ⚙️ CONFIGURAÇÕES ANDROID

### Desabilitar Economia de Bateria

1. Configurações → Apps → Termux
2. Bateria → Sem restrições

### Permitir Execução em Segundo Plano

1. Configurações → Apps → Termux
2. Permissões → Executar em segundo plano: Permitir

---

## 🐛 TROUBLESHOOTING

### Erro: "Address already in use"

```bash
# Matar processo na porta 5000
pkill -f magnus_proxy.py
```

### Erro: "Module not found"

```bash
# Reinstalar dependências
pip install --upgrade flask python-binance
```

### Termux fecha sozinho

1. Desabilitar economia de bateria
2. Usar tmux
3. Usar termux-wake-lock

### Não conecta à Binance

1. Verificar API Keys
2. Verificar IP cadastrado na Binance
3. Verificar conexão Wi-Fi

---

## 📞 COMANDOS ÚTEIS

```bash
# Ver IP do celular
ifconfig wlan0 | grep inet

# Testar servidor
curl http://localhost:5000/health

# Ver logs
tail -f magnus_proxy.log

# Parar servidor
Ctrl+C

# Reiniciar
python magnus_proxy.py
```

---

## ✅ CHECKLIST FINAL

- [ ] Termux instalado
- [ ] Python instalado
- [ ] Dependências instaladas
- [ ] Script baixado
- [ ] API Keys configuradas
- [ ] Binance conectada
- [ ] Wake lock ativado
- [ ] IP anotado
- [ ] Servidor Manus configurado
- [ ] Teste de integração OK

---

**Pronto! Sistema 100% automático funcionando!** 🎉

