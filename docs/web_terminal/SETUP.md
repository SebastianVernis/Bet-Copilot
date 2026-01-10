# 🚀 Web Terminal Setup Guide

**Fecha**: 2026-01-06  
**Versión**: v0.7.0-alpha  
**Stack**: ttyd + Docker + Nginx

---

## 📋 Requisitos

### Software
- Docker 20.10+
- docker-compose 1.29+
- (Opcional) OpenSSL para certificados SSL

### Hardware Mínimo
- CPU: 2 cores
- RAM: 2GB
- Disco: 1GB

---

## 🔧 Instalación

### 1. Clonar Repositorio
```bash
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot
git checkout laptop/feature/web-terminal-shellinabox
```

### 2. Configurar Variables de Entorno
```bash
# Copiar ejemplo
cp docker/.env.example docker/.env

# Editar con tus credenciales
nano docker/.env
```

**Configuración mínima**:
```bash
# Autenticación web terminal
TTYD_USER=tu_usuario
TTYD_PASS=tu_password_seguro

# API Keys (obtener de proveedores)
ODDS_API_KEY=tu_api_key_odds
API_FOOTBALL_KEY=tu_api_key_football  
GEMINI_API_KEY=tu_api_key_gemini
```

### 3. Deploy Básico (Solo ttyd)
```bash
./scripts/deploy_alpha.sh
```

Esto iniciará el servidor web terminal en `http://localhost:7681`

---

## 🔐 SSL/TLS Setup (Producción)

### Opción A: Certificados Self-Signed (Testing)
```bash
# Generar certificados
./scripts/generate_ssl.sh localhost

# Deploy con Nginx
cd docker
docker-compose --profile production up -d
```

Acceso: `https://localhost/terminal`

### Opción B: Let's Encrypt (Producción)
```bash
# Instalar certbot
apt install certbot

# Obtener certificado (requiere dominio público)
certbot certonly --standalone -d tu-dominio.com

# Copiar certificados
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem docker/ssl/key.pem

# Deploy con SSL
cd docker
docker-compose --profile production up -d
```

---

## 📊 Verificación

### Check Containers
```bash
cd docker
docker-compose ps
```

**Salida esperada**:
```
NAME                  STATUS        PORTS
bet-copilot-ttyd      Up (healthy)  0.0.0.0:7681->7681/tcp
bet-copilot-nginx     Up            0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### Check Logs
```bash
# ttyd logs
docker-compose logs -f ttyd

# Nginx logs
docker-compose logs -f nginx
```

### Test Conectividad
```bash
# Test HTTP
curl http://localhost:7681

# Test HTTPS (con Nginx)
curl -k https://localhost/terminal
```

---

## 🎮 Uso

### Acceso Browser

**Deploy básico**:
1. Abrir navegador
2. Ir a `http://localhost:7681`
3. Ingresar credenciales (TTYD_USER/TTYD_PASS)
4. CLI de Bet-Copilot lista

**Deploy con Nginx**:
1. Abrir navegador
2. Ir a `https://tu-dominio.com/terminal`
3. Aceptar certificado (si es self-signed)
4. Ingresar credenciales
5. CLI disponible

### Comandos CLI
Una vez conectado, usar comandos normales:
```bash
# Ver cuotas disponibles
list sports

# Analizar partido
analyze "Manchester United" "Liverpool"

# Ver historial
history

# Ayuda
help
```

---

## 🛑 Administración

### Detener Servicios
```bash
cd docker
docker-compose down
```

### Reiniciar
```bash
docker-compose restart
```

### Ver Estado
```bash
docker-compose ps
docker-compose top
```

### Actualizar Imagen
```bash
# Rebuild
docker-compose build --no-cache

# Restart
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Puerto 7681 en Uso
```bash
# Ver qué usa el puerto
lsof -i :7681

# Cambiar puerto en docker-compose.yml
ports:
  - "8080:7681"  # Usar 8080 externamente
```

### Conexión WebSocket Falla
```bash
# Check Nginx config
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

### Autenticación No Funciona
```bash
# Verificar variables
docker-compose exec ttyd env | grep TTYD

# Recrear con nuevas credenciales
docker-compose up -d --force-recreate
```

### Performance Bajo
```bash
# Ver recursos
docker stats

# Limitar conexiones en docker-compose.yml
# Aumentar --max-clients en Dockerfile
```

---

## 📈 Monitoreo

### Health Checks
```bash
# ttyd health
curl http://localhost:7681/

# Nginx health
curl http://localhost/health
```

### Logs en Tiempo Real
```bash
# Todos los servicios
docker-compose logs -f

# Solo ttyd
docker-compose logs -f ttyd

# Últimas 100 líneas
docker-compose logs --tail=100
```

### Métricas
```bash
# Uso de recursos
docker stats bet-copilot-ttyd

# Conexiones activas
docker-compose exec ttyd netstat -an | grep 7681
```

---

## 🔐 Seguridad

### Cambiar Credenciales
```bash
# Editar .env
nano docker/.env

# Recrear contenedor
cd docker
docker-compose up -d --force-recreate ttyd
```

### Rate Limiting
Configurado en `nginx.conf`:
- 10 requests/segundo por IP
- Burst de 20 requests

### Firewall (Producción)
```bash
# Permitir solo HTTPS
ufw allow 443/tcp

# Bloquear acceso directo a ttyd
ufw deny 7681/tcp
```

---

## 📚 Referencias

- **ttyd GitHub**: https://github.com/tsl0922/ttyd
- **Docker Docs**: https://docs.docker.com/
- **Nginx WebSocket**: https://nginx.org/en/docs/http/websocket.html
- **Let's Encrypt**: https://letsencrypt.org/

---

## 🆘 Soporte

**Problemas?**
1. Check logs: `docker-compose logs`
2. Verificar .env: API keys correctas
3. Test básico: `docker run -it --rm alpine sh`
4. Issue en GitHub

---

**Última actualización**: 2026-01-06  
**Documentado para**: Alpha v0.7.0
