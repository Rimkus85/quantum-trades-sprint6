# 🚀 Magnus Wealth - Deploy Permanente

## Serviço Systemd Configurado

O Proxy Binance está configurado para rodar **permanentemente** como serviço do sistema.

### Status do Serviço

```bash
sudo systemctl status magnus-proxy
```

### Comandos Úteis

```bash
# Iniciar
sudo systemctl start magnus-proxy

# Parar
sudo systemctl stop magnus-proxy

# Reiniciar
sudo systemctl restart magnus-proxy

# Ver logs
sudo journalctl -u magnus-proxy -f
```

### URL Permanente

**Acesso Web:** https://5000-ib34pqn2vi38fss1puv5n-a559137e.manusvm.computer

### Características

✅ **Inicia automaticamente** ao ligar o servidor
✅ **Reinicia automaticamente** se cair
✅ **Roda em segundo plano** sempre
✅ **Logs centralizados** no systemd

### Arquivo de Serviço

Localização: `/etc/systemd/system/magnus-proxy.service`

```ini
[Unit]
Description=Magnus Wealth - Proxy Binance
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/quantum-trades-sprint6/backend/quantum-trades-backend
ExecStart=/usr/bin/python3 api_proxy_binance.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

**Status:** ✅ ATIVO E PERMANENTE
