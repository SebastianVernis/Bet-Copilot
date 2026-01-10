# 🔐 Web Terminal Security Guide

**Fecha**: 2026-01-06  
**Stack**: ttyd + Nginx + Docker

---

## ⚠️ Security Considerations

### Threat Model

**Riesgos**:
1. Acceso no autorizado a terminal
2. Command injection
3. Data leakage (API keys)
4. Man-in-the-middle attacks
5. DoS/resource exhaustion

**Mitigaciones Implementadas**:
- ✅ HTTP Basic Auth (ttyd)
- ✅ SSL/TLS encryption (Nginx)
- ✅ Rate limiting (Nginx)
- ✅ Container isolation (Docker)
- ✅ Health checks
- ✅ Command logging

---

## 🔑 Authentication

### ttyd Basic Auth
```bash
# Configurado en Dockerfile
--credential ${TTYD_USER}:${TTYD_PASS}
```

**Best Practices**:
- ✅ Usar contraseñas fuertes (16+ caracteres)
- ✅ Rotar credenciales cada 90 días
- ✅ No hardcodear en código
- ✅ Usar variables de entorno

**Generar Password Fuerte**:
```bash
openssl rand -base64 32
```

### Nginx Additional Auth (Opcional)
```nginx
location /terminal {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # ... resto config
}
```

Crear `.htpasswd`:
```bash
htpasswd -c docker/.htpasswd alpha_user
```

---

## 🔒 SSL/TLS

### Development (Self-Signed)
```bash
./scripts/generate_ssl.sh localhost
```

**Pros**: Rápido setup  
**Cons**: Navegador mostrará warning

### Production (Let's Encrypt)
```bash
# Auto-renovación con certbot
certbot renew --deploy-hook "docker-compose restart nginx"
```

**Configuración Nginx** (ya incluida):
- TLS 1.2, 1.3 only
- Strong ciphers
- HSTS header
- Perfect forward secrecy

---

## 🚧 Network Isolation

### Docker Network
```yaml
networks:
  bet-network:
    driver: bridge
```

**Aislamiento**:
- ttyd no expuesto directamente a internet
- Solo Nginx en puertos públicos (80, 443)
- Comunicación interna vía Docker network

### Firewall Rules (Producción)
```bash
# UFW (Ubuntu)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 443/tcp   # HTTPS
ufw deny 7681/tcp   # Block direct ttyd access
ufw enable
```

---

## 🛡️ Rate Limiting

### Nginx Configuration
```nginx
limit_req_zone $binary_remote_addr zone=terminal_limit:10m rate=10r/s;

location /terminal {
    limit_req zone=terminal_limit burst=20 nodelay;
    # ...
}
```

**Límites**:
- 10 requests/segundo por IP
- Burst de 20 requests
- Zone de 10MB (~160k IPs)

**Customizar**:
```nginx
# Más restrictivo
rate=5r/s burst=10

# Más permisivo
rate=20r/s burst=50
```

---

## 📝 Logging & Auditing

### ttyd Command Logging
```bash
# En Dockerfile CMD, añadir:
--client-option enableTrzsz=true \
--client-option enableSixel=false \
2>&1 | tee -a /data/ttyd.log
```

### Nginx Access Logs
```nginx
access_log /var/log/nginx/terminal_access.log combined;
error_log /var/log/nginx/terminal_error.log warn;
```

**Ver logs**:
```bash
docker-compose logs nginx | grep terminal
docker-compose exec nginx tail -f /var/log/nginx/terminal_access.log
```

### Análisis de Logs
```bash
# IPs únicas conectadas
docker-compose logs nginx | grep "GET /terminal" | awk '{print $1}' | sort -u

# Request rate por minuto
docker-compose logs nginx | grep "GET /terminal" | awk '{print $4}' | cut -d: -f1-2 | uniq -c
```

---

## 🔐 Secrets Management

### Environment Variables
```bash
# docker/.env
TTYD_USER=alpha_user
TTYD_PASS=$(openssl rand -base64 32)
ODDS_API_KEY=sk_live_...
```

**No commitear**:
```gitignore
# .gitignore
docker/.env
docker/ssl/*.pem
```

### Docker Secrets (Producción)
```yaml
# docker-compose.yml
services:
  ttyd:
    secrets:
      - ttyd_password
      - api_keys

secrets:
  ttyd_password:
    file: ./secrets/ttyd_password.txt
  api_keys:
    file: ./secrets/api_keys.txt
```

---

## 🚨 Container Security

### Run as Non-Root
```dockerfile
# Añadir a Dockerfile.ttyd
RUN adduser -D -u 1000 betuser
USER betuser
```

### Read-Only Filesystem
```yaml
# docker-compose.yml
services:
  ttyd:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
```

### Resource Limits
```yaml
services:
  ttyd:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## 🔍 Vulnerability Scanning

### Docker Image Scan
```bash
# Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image bet-copilot-ttyd

# Docker Scout
docker scout cves bet-copilot-ttyd
```

### Dependency Audit
```bash
# Python dependencies
pip-audit -r requirements.txt

# Alpine packages
docker-compose exec ttyd apk audit
```

---

## 🛠️ Hardening Checklist

### Pre-Deployment
- [ ] Cambiar credenciales default (TTYD_USER/TTYD_PASS)
- [ ] Configurar SSL/TLS válido
- [ ] Actualizar todas las dependencias
- [ ] Scan de vulnerabilidades
- [ ] Test rate limiting
- [ ] Verificar logs funcionando

### Production
- [ ] Firewall configurado (UFW/iptables)
- [ ] Fail2ban para brute force protection
- [ ] Monitoreo de logs activo
- [ ] Backups automáticos
- [ ] Proceso de rotación de credenciales
- [ ] Plan de incident response

### Monitoring
- [ ] Alertas para logins fallidos
- [ ] Monitoreo de uso de recursos
- [ ] Health checks automáticos
- [ ] Log aggregation (ELK, Splunk, etc.)

---

## 🚨 Incident Response

### Acceso Sospechoso Detectado

1. **Revisar logs**:
```bash
docker-compose logs nginx | grep "401\|403"
```

2. **Bloquear IP** (temporal):
```bash
# Nginx
echo "deny 1.2.3.4;" >> docker/nginx_block.conf
docker-compose exec nginx nginx -s reload
```

3. **Rotar credenciales**:
```bash
nano docker/.env
docker-compose up -d --force-recreate ttyd
```

4. **Auditoría**:
```bash
# Verificar comandos ejecutados
docker-compose logs ttyd | grep "python"
```

### Container Comprometido

1. **Detener inmediatamente**:
```bash
docker-compose stop ttyd
```

2. **Inspeccionar**:
```bash
docker-compose exec ttyd sh
# Buscar archivos modificados, procesos sospechosos
```

3. **Recrear desde cero**:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

4. **Revisar código**:
```bash
git status
git diff
```

---

## 📚 Security Resources

- **OWASP Docker Security**: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- **CIS Docker Benchmark**: https://www.cisecurity.org/benchmark/docker
- **ttyd Security**: https://github.com/tsl0922/ttyd#security
- **Nginx Security**: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

---

## 📧 Report Security Issues

**Email**: security@bet-copilot.com  
**PGP Key**: [Publicar en repo]

**Disclosure Policy**: 90 días responsible disclosure

---

**Última actualización**: 2026-01-06  
**Review**: Cada 3 meses
