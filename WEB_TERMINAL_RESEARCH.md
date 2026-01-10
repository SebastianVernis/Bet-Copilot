# 🔍 Research: Web Terminal Solutions

**Fecha**: 2026-01-06  
**Branch**: laptop/feature/web-terminal-shellinabox  
**Objetivo**: Elegir mejor solución para acceso web terminal

---

## 📊 Comparativa: ttyd vs shellinabox vs wetty

### 1. ttyd
**GitHub**: https://github.com/tsl0922/ttyd

**Ventajas**:
- ✅ Moderno (C, WebSocket)
- ✅ Muy rápido y ligero (~100KB binario)
- ✅ SSL/TLS nativo
- ✅ Autenticación HTTP basic auth
- ✅ Soporte multi-client
- ✅ Activamente mantenido (2024)
- ✅ Excelente para Docker
- ✅ Reconexión automática

**Desventajas**:
- ⚠️ Auth básica (no PAM)
- ⚠️ Configuración manual

**Instalación**:
```bash
# Ubuntu/Debian
apt install ttyd

# Docker
docker run -p 7681:7681 tsl0922/ttyd bash
```

**Configuración Básica**:
```bash
ttyd -p 7681 \
     -c username:password \
     --ssl \
     --ssl-cert /path/to/cert.pem \
     --ssl-key /path/to/key.pem \
     bash
```

**Recursos**: ~10-20MB RAM, <1% CPU idle

---

### 2. shellinabox
**GitHub**: https://github.com/shellinabox/shellinabox

**Ventajas**:
- ✅ Estable y probado (desde 2008)
- ✅ SSL/TLS nativo
- ✅ PAM authentication (integración sistema)
- ✅ Simple configuración
- ✅ Funciona out-of-the-box

**Desventajas**:
- ⚠️ Menos mantenimiento (último release 2018)
- ⚠️ Tecnología más antigua
- ⚠️ Menos features modernas
- ⚠️ Performance inferior a ttyd

**Instalación**:
```bash
# Ubuntu/Debian
apt install shellinabox

# Servicio systemd
systemctl enable shellinabox
systemctl start shellinabox
```

**Configuración**:
```bash
# /etc/default/shellinabox
SHELLINABOX_ARGS="--no-beep --disable-ssl --localhost-only"
# Luego Nginx maneja SSL
```

**Recursos**: ~30-50MB RAM, 2-3% CPU

---

### 3. wetty
**GitHub**: https://github.com/butlerx/wetty

**Ventajas**:
- ✅ Moderno (Node.js, WebSocket)
- ✅ Activamente mantenido
- ✅ UI customizable
- ✅ SSH support nativo
- ✅ Múltiples opciones de auth

**Desventajas**:
- ⚠️ Dependencia Node.js pesada (~200MB)
- ⚠️ Mayor consumo de recursos
- ⚠️ Complejidad de setup
- ⚠️ Overhead de npm

**Instalación**:
```bash
npm install -g wetty

# O Docker
docker run -p 3000:3000 wettyoss/wetty
```

**Configuración**:
```bash
wetty --port 3000 \
      --sslkey /path/to/key.pem \
      --sslcert /path/to/cert.pem \
      --base /terminal/
```

**Recursos**: ~100-150MB RAM, 5-10% CPU

---

## 🎯 Decisión Recomendada: **ttyd**

### Justificación

**Para Bet-Copilot**:
1. ✅ **Performance**: Crítico para CLI interactiva
2. ✅ **Ligereza**: Ideal para deployment alpha
3. ✅ **Docker-friendly**: Fácil containerización
4. ✅ **Moderno**: WebSocket, reconexión automática
5. ✅ **Mantenimiento activo**: Updates regulares

**Trade-offs Aceptables**:
- Auth básica HTTP suficiente para alpha
- Configuración manual no es problema (scripting)

### Arquitectura Propuesta

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS (443)
       ▼
┌─────────────┐
│    Nginx    │  ← Reverse Proxy + SSL/TLS
└──────┬──────┘
       │ HTTP (7681)
       ▼
┌─────────────┐
│    ttyd     │  ← Web Terminal Server
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ bet-copilot │  ← CLI Python app
└─────────────┘
```

---

## 📋 Stack Final Elegido

### Componentes

1. **ttyd** (v1.7+)
   - Web terminal server
   - Puerto interno: 7681

2. **Nginx** (latest)
   - Reverse proxy
   - SSL/TLS termination
   - Rate limiting
   - Puerto externo: 443 (HTTPS)

3. **Docker + docker-compose**
   - Containerización
   - Orquestación multi-container

4. **Let's Encrypt** (opcional)
   - SSL/TLS automático (certbot)

---

## 🔧 Plan de Implementación

### Fase 1: POC Básico (Día 1)
```bash
# Setup ttyd local
apt install ttyd
ttyd -p 7681 bash

# Probar en navegador
http://localhost:7681
```

### Fase 2: Dockerización (Día 2)
```dockerfile
FROM alpine:latest
RUN apk add --no-cache ttyd bash python3 py3-pip
COPY bet_copilot /app/bet_copilot
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
EXPOSE 7681
CMD ["ttyd", "-p", "7681", "python", "/app/main.py"]
```

### Fase 3: Nginx + Auth (Día 3-4)
```nginx
server {
    listen 443 ssl http2;
    server_name alpha.bet-copilot.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location /terminal {
        proxy_pass http://ttyd:7681;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Fase 4: docker-compose (Día 5)
```yaml
version: '3.8'
services:
  ttyd:
    build: ./docker/ttyd
    ports:
      - "7681:7681"
    volumes:
      - ./bet_copilot.db:/data/bet_copilot.db
  
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ttyd
```

### Fase 5: Deploy Scripts (Día 6-7)
```bash
#!/bin/bash
# scripts/deploy_alpha.sh
docker-compose up -d
echo "✅ Alpha deployment running on https://alpha.bet-copilot.com/terminal"
```

---

## 🔐 Seguridad

### Consideraciones

1. **Autenticación**:
   - HTTP Basic Auth (ttyd `-c user:pass`)
   - Nginx también puede añadir capa extra

2. **SSL/TLS**:
   - Nginx termina SSL
   - Certificados Let's Encrypt

3. **Rate Limiting**:
   - Nginx: `limit_req` por IP

4. **Aislamiento**:
   - Docker network privada
   - ttyd no expuesto públicamente

5. **Logs**:
   - Nginx access logs
   - ttyd command logs

### Configuración Segura

```bash
# ttyd con auth
ttyd -p 7681 \
     -c alpha_user:$(openssl rand -base64 32) \
     --max-clients 10 \
     --once \  # Una sesión por conexión
     python /app/main.py
```

---

## 📊 Testing Plan

### Tests Locales
```bash
# 1. ttyd solo
ttyd -p 7681 bash
curl http://localhost:7681

# 2. Con Python CLI
ttyd -p 7681 python main.py

# 3. Con Docker
docker run -p 7681:7681 bet-copilot-ttyd

# 4. Latency test
time curl http://localhost:7681
# Target: <100ms
```

### Tests Alpha
- [ ] 5 usuarios concurrentes
- [ ] Latencia < 2s
- [ ] Reconexión automática
- [ ] Mobile browser compatible
- [ ] 24h uptime test

---

## 📚 Referencias

- **ttyd**: https://github.com/tsl0922/ttyd
- **Docker ttyd**: https://hub.docker.com/r/tsl0922/ttyd
- **Nginx WebSocket**: https://nginx.org/en/docs/http/websocket.html
- **Let's Encrypt**: https://letsencrypt.org/

---

## ✅ Conclusión

**Elegido: ttyd + Nginx + Docker**

**Ventajas para este proyecto**:
- Ligereza (crítico para alpha)
- Performance (CLI interactiva)
- Fácil deployment
- Moderno y mantenido

**Siguiente paso**: Implementar POC básico

---

**Investigación por**: Crush AI  
**Fecha**: 2026-01-06  
**Decision**: ttyd como web terminal server
