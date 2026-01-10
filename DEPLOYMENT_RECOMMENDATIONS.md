# 🚀 Recomendaciones de Despliegue - Bet-Copilot Web Terminal

**Fecha**: 2026-01-10  
**Versión**: v0.7.0-alpha  
**Stack**: ttyd + Docker + Nginx

---

## 📊 Comparativa de Plataformas

### 1. ⭐ **DigitalOcean Droplets** (RECOMENDADO)

**Pros**:
- ✅ $6/mes plan básico suficiente (1GB RAM, 1 vCPU)
- ✅ 1-Click Docker pre-instalado
- ✅ Panel web intuitivo
- ✅ Backups automáticos (+$1.20/mes)
- ✅ Firewall managed gratuito
- ✅ IPv4 estática incluida
- ✅ DNS gratuito
- ✅ Documentación excelente
- ✅ Escalabilidad vertical fácil

**Cons**:
- ❌ Más caro que VPS básicos
- ❌ No hay tier gratuito permanente

**Specs Recomendadas**:
```
Droplet: Basic - $6/mes
- 1 vCPU
- 1 GB RAM
- 25 GB SSD
- 1 TB transfer
- Ubuntu 22.04 LTS
```

**Setup Rápido**:
```bash
# 1. Crear Droplet con Docker pre-instalado (1-Click App)
# 2. SSH al servidor
ssh root@your-droplet-ip

# 3. Clonar repo
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot

# 4. Configurar
cp docker/.env.example docker/.env
nano docker/.env  # Editar credenciales

# 5. Deploy
./scripts/deploy_alpha.sh

# 6. Configurar firewall
ufw allow 443/tcp
ufw allow 80/tcp
ufw deny 7681/tcp  # Bloquear acceso directo a ttyd
ufw enable
```

**Precio Total**:
- Droplet: $6/mes
- Backups: $1.20/mes
- **Total: ~$7.20/mes**

---

### 2. 🥈 **AWS Lightsail**

**Pros**:
- ✅ $5/mes plan básico (1GB RAM, 1 vCPU)
- ✅ 3 meses gratis primer año
- ✅ Integración con AWS ecosystem
- ✅ Static IP gratuita
- ✅ Firewall managed
- ✅ Snapshots ($1/GB)

**Cons**:
- ❌ UI menos intuitiva que DO
- ❌ Límite de transfer (1TB)
- ❌ Requiere cuenta AWS (tarjeta crédito)

**Setup**:
```bash
# Similar a DigitalOcean
# Dashboard: lightsail.aws.amazon.com
```

**Precio**: $5-7/mes

---

### 3. 🥉 **Hetzner Cloud**

**Pros**:
- ✅ €4.15/mes (~$4.50) plan básico (2GB RAM!)
- ✅ Mejor relación precio/rendimiento
- ✅ Datacenter en Europa (buena latencia)
- ✅ IPv4 + IPv6 incluidas
- ✅ Backups automáticos

**Cons**:
- ❌ No popular en LATAM (soporte en alemán/inglés)
- ❌ Menos integraciones que AWS/DO

**Setup**:
```bash
# Igual proceso que DigitalOcean
# Panel: console.hetzner.cloud
```

**Precio**: €4-5/mes (~$4.50-5.50)

---

### 4. 🏠 **Oracle Cloud Free Tier** (GRATIS PERMANENTE)

**Pros**:
- ✅ **GRATIS para siempre** (no solo trial)
- ✅ ARM: 4 vCPU + 24GB RAM (compartido)
- ✅ x86: 2 VMs con 1GB RAM cada una
- ✅ 200GB storage total
- ✅ 10TB transfer/mes

**Cons**:
- ❌ Requiere tarjeta crédito (verificación)
- ❌ Proceso de alta más complejo
- ❌ Performance variable (shared)
- ❌ UI confusa (típico Oracle)
- ❌ Pueden reclamar recursos si no usas

**Setup**:
```bash
# 1. Crear Always Free VM (ARM Ampere)
# 2. Configurar Security List (puerto 443)
# 3. Deploy igual que otros
```

**Precio**: **$0/mes** (con límites)

---

### 5. 📦 **Render.com** (Platform as a Service)

**Pros**:
- ✅ Deploy automático desde GitHub
- ✅ SSL gratuito automático
- ✅ Plan gratuito (con sleep)
- ✅ No requiere administración de servidor
- ✅ Build automático

**Cons**:
- ❌ Plan gratuito: sleep después 15 min inactividad
- ❌ Plan pago: $7/mes (básico)
- ❌ Menos control que VPS tradicional
- ❌ Terminal web podría no funcionar bien

**Configuración**:
```yaml
# render.yaml
services:
  - type: web
    name: bet-copilot-ttyd
    env: docker
    dockerfilePath: ./docker/Dockerfile.ttyd
    envVars:
      - key: TTYD_USER
        sync: false
      - key: TTYD_PASS
        sync: false
```

**Precio**: 
- Gratis (con sleep)
- $7/mes (siempre activo)

---

### 6. 🐳 **Fly.io** (Docker-Native)

**Pros**:
- ✅ Especializado en Docker
- ✅ $1.94/mes plan básico (shared CPU)
- ✅ SSL automático
- ✅ Deploy global (edge locations)
- ✅ CLI excelente

**Cons**:
- ❌ Facturación por uso puede variar
- ❌ Menos documentación que AWS/DO

**Setup**:
```bash
# Instalar flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly secrets set TTYD_USER=user TTYD_PASS=pass
fly deploy
```

**Precio**: $2-5/mes

---

### 7. 🏡 **Home Server / Raspberry Pi** (Self-Hosted)

**Pros**:
- ✅ Costo hardware único (~$100 RPi)
- ✅ Control total
- ✅ Sin costos mensuales
- ✅ Privacidad máxima

**Cons**:
- ❌ Requiere IP pública/DDNS
- ❌ Configurar router/firewall
- ❌ Uptime depende de tu conexión
- ❌ Costos eléctricos (~$2-3/mes)
- ❌ Sin backups automáticos

**Setup**:
```bash
# Raspberry Pi 4 (4GB RAM)
# Ubuntu Server 22.04 ARM
# Docker + docker-compose
# DuckDNS para dominio dinámico
# Cloudflare Tunnel o Ngrok para exposición
```

**Precio**: 
- Hardware: $100 una vez
- Electricidad: ~$2/mes

---

## 🏆 Recomendación Final

### Para Desarrollo/Testing (1-3 meses)
**🥇 Oracle Cloud Free Tier**
- Gratis permanente
- Recursos suficientes (ARM)
- Bueno para proof of concept

### Para Producción Alpha (usuarios limitados)
**🥇 DigitalOcean $6 Droplet**
- Setup más simple
- Documentación excelente
- Firewall managed
- Backups automáticos
- Mejor soporte

**🥈 Hetzner Cloud €4.15**
- Si quieres ahorrar $2/mes
- Mejor specs por precio
- Datacenter Europa

### Para Producción Beta/Estable
**🥇 AWS Lightsail $10-20**
- Escalabilidad
- Integración AWS (RDS, S3, etc.)
- Load balancing
- Monitoreo avanzado

---

## 📋 Checklist de Selección

| Criterio | Oracle Free | DigitalOcean | Hetzner | AWS Lightsail |
|----------|-------------|--------------|---------|---------------|
| **Precio/mes** | $0 | $6 | $4.50 | $5 |
| **Setup fácil** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Docs/Soporte** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Escalabilidad** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Backups** | Manual | +$1.20 | +€1 | +$1 |
| **Free Tier** | Permanente | $200/60d | €20 | 3 meses |

---

## 🛠️ Setup Paso a Paso (DigitalOcean)

### 1. Crear Cuenta y Droplet
```bash
# 1. Registrarse en digitalocean.com
# 2. Crear Droplet:
#    - Ubuntu 22.04 LTS
#    - Basic plan ($6/mes)
#    - 1 vCPU, 1GB RAM, 25GB SSD
#    - Datacenter: más cercano a ti
#    - Authentication: SSH Key (recomendado)
#    - Hostname: bet-copilot-alpha
```

### 2. Configurar Dominio (Opcional pero Recomendado)
```bash
# Opción A: Dominio gratuito (DuckDNS, FreeDNS)
curl "https://www.duckdns.org/update?domains=betcopilot&token=YOUR_TOKEN&ip="

# Opción B: DigitalOcean DNS (si tienes dominio)
# Panel DO → Networking → Domains → Add Domain
# A record: @ → Droplet IP
# A record: www → Droplet IP
```

### 3. Conectar y Configurar
```bash
# SSH al servidor
ssh root@your-droplet-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker (si no usaste 1-Click)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar docker-compose
apt install docker-compose -y

# Clonar repositorio
cd /opt
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot
git checkout laptop/feature/web-terminal-shellinabox
```

### 4. Configurar Aplicación
```bash
# Copiar y editar configuración
cp docker/.env.example docker/.env
nano docker/.env

# Configurar:
# TTYD_USER=admin_user
# TTYD_PASS=$(openssl rand -base64 32)  # Password fuerte
# ODDS_API_KEY=tu_key
# API_FOOTBALL_KEY=tu_key
# GEMINI_API_KEY=tu_key
```

### 5. Generar SSL (Producción)
```bash
# Opción A: Let's Encrypt (dominio real)
apt install certbot -y
certbot certonly --standalone -d betcopilot.tudominio.com
cp /etc/letsencrypt/live/betcopilot.tudominio.com/fullchain.pem docker/ssl/cert.pem
cp /etc/letsencrypt/live/betcopilot.tudominio.com/privkey.pem docker/ssl/key.pem

# Opción B: Self-Signed (testing)
./scripts/generate_ssl.sh betcopilot.tudominio.com

# Editar nginx.conf con tu dominio
nano docker/nginx.conf
# Cambiar: server_name betcopilot.tudominio.com;
```

### 6. Deploy
```bash
# Deploy solo ttyd (sin SSL)
./scripts/deploy_alpha.sh

# O deploy completo con Nginx (SSL)
cd docker
docker-compose --profile production up -d

# Verificar
docker-compose ps
docker-compose logs -f ttyd
```

### 7. Configurar Firewall
```bash
# Configurar UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh  # IMPORTANTE: permitir SSH primero
ufw allow 443/tcp  # HTTPS
ufw allow 80/tcp   # HTTP (redirect a HTTPS)
ufw deny 7681/tcp  # Bloquear acceso directo a ttyd
ufw enable

# Verificar
ufw status verbose
```

### 8. Verificar Funcionamiento
```bash
# Desde tu máquina local
curl https://betcopilot.tudominio.com/health

# O abrir en navegador
# https://betcopilot.tudominio.com/terminal
# Usuario: admin_user
# Password: (ver docker/.env)
```

### 9. Configurar Backups (Opcional)
```bash
# DigitalOcean Backups automáticos (+$1.20/mes)
# Panel DO → Droplet → Backups → Enable

# O backup manual con script
nano /root/backup.sh
```

```bash
#!/bin/bash
# backup.sh - Backup manual
docker-compose -f /opt/Bet-Copilot/docker/docker-compose.yml stop
tar -czf /root/backups/bet-copilot-$(date +%Y%m%d).tar.gz /opt/Bet-Copilot
docker-compose -f /opt/Bet-Copilot/docker/docker-compose.yml start
```

```bash
chmod +x /root/backup.sh
crontab -e
# Agregar: 0 3 * * * /root/backup.sh  # Backup diario 3am
```

### 10. Monitoreo
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver métricas contenedor
docker stats

# Health check
curl http://localhost:7681/  # Interno
curl https://betcopilot.tudominio.com/health  # Externo
```

---

## 💰 Estimación de Costos

### Escenario Mínimo (Alpha Testing)
```
Oracle Cloud Free Tier: $0/mes
o
Hetzner CX11: €4.15/mes (~$4.50)
Dominio .com: $12/año (~$1/mes)
--------------------------------------
Total: $0-5.50/mes
```

### Escenario Recomendado (Producción Pequeña)
```
DigitalOcean Droplet $6: $6/mes
Backups automáticos: $1.20/mes
Dominio .com: $12/año (~$1/mes)
--------------------------------------
Total: ~$8.20/mes
```

### Escenario Escalado (100+ usuarios)
```
DigitalOcean/AWS $20-40: $30/mes
Cloudflare CDN: $0 (plan gratis)
Dominio: $1/mes
Monitoreo (Datadog/New Relic): $0-15/mes
--------------------------------------
Total: ~$31-46/mes
```

---

## 🔒 Consideraciones de Seguridad

### Esenciales
1. ✅ Cambiar password root SSH inmediatamente
2. ✅ Usar SSH keys, deshabilitar password auth
3. ✅ Configurar firewall (UFW/iptables)
4. ✅ Mantener sistema actualizado (unattended-upgrades)
5. ✅ Usar passwords fuertes para ttyd (32+ caracteres)
6. ✅ SSL/TLS obligatorio en producción
7. ✅ Rate limiting en Nginx
8. ✅ Logs de acceso habilitados

### Avanzadas
- 🔐 Fail2ban para bloquear IPs sospechosas
- 🔐 2FA en panel del hosting
- 🔐 VPN para acceso administrativo
- 🔐 Rotación de credenciales cada 90 días
- 🔐 Monitoreo de intrusiones (OSSEC, Wazuh)

---

## 📊 Métricas de Rendimiento Esperadas

### Recursos (1 usuario activo)
- CPU: 5-10%
- RAM: 200-300 MB
- Disco: <100 MB
- Bandwidth: ~1 MB/min

### Capacidad Estimada
**Droplet $6 (1GB RAM)**:
- Usuarios concurrentes: 5-8
- Sesiones CLI simultáneas: 10 (límite ttyd)

**Droplet $12 (2GB RAM)**:
- Usuarios concurrentes: 15-20
- Sesiones CLI simultáneas: 20

---

## 🆘 Troubleshooting Común

### Contenedor no inicia
```bash
docker-compose logs ttyd
# Verificar variables de entorno en .env
```

### No puedo acceder desde navegador
```bash
# Verificar firewall
ufw status
netstat -tlnp | grep 7681  # ttyd
netstat -tlnp | grep 443   # nginx

# Verificar DNS
nslookup betcopilot.tudominio.com
```

### SSL certificate invalid
```bash
# Renovar Let's Encrypt
certbot renew
docker-compose restart nginx

# Verificar fechas
openssl x509 -in docker/ssl/cert.pem -noout -dates
```

### Performance lento
```bash
# Verificar recursos
htop
docker stats

# Escalar verticalmente (resize droplet)
# Panel DO → Droplet → Resize
```

---

## 📚 Recursos Adicionales

### Documentación Proyecto
- `docs/web_terminal/SETUP.md` - Setup detallado
- `docs/web_terminal/SECURITY.md` - Hardening completo
- `docs/web_terminal/ARCHITECTURE.md` - Arquitectura técnica

### Tutoriales Hosting
- [DigitalOcean Docker Tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04)
- [Let's Encrypt con Nginx](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
- [UFW Firewall Guide](https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands)

---

## 🎯 Decisión Rápida

**¿Qué plataforma elegir?**

| Si quieres... | Elige |
|---------------|-------|
| **Gratis permanente** | Oracle Cloud Free Tier |
| **Setup más fácil** | DigitalOcean $6 |
| **Mejor precio/specs** | Hetzner €4.15 |
| **Integración AWS** | AWS Lightsail $5 |
| **Deploy automático Git** | Render/Fly.io |
| **Máximo control** | Home Server |

**Mi recomendación personal**: 

1. **Testing (1-3 meses)**: Oracle Cloud Free Tier
2. **Alpha/Beta (usuarios limitados)**: DigitalOcean $6
3. **Producción (escalable)**: DigitalOcean $12+ o AWS Lightsail

---

**Autor**: SebastianVernisMora  
**Contacto**: pelongemelo@gmail.com  
**Última actualización**: 2026-01-10
