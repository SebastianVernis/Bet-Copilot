# 🆓 Opciones de Hosting GRATUITAS - Bet-Copilot Web Terminal

**Fecha**: 2026-01-10  
**Objetivo**: Desplegar sin costo mensual

---

## 🎯 Opciones 100% Gratuitas

### 1. ⭐ **Oracle Cloud Free Tier** (MEJOR OPCIÓN GRATIS)

**Recursos Always Free (PERMANENTES)**:
- ✅ **VM ARM Ampere**: 4 vCPU + 24GB RAM (compartido entre VMs)
- ✅ **VM x86**: 2 instancias con 1GB RAM cada una (AMD)
- ✅ 200GB Block Storage total
- ✅ 10TB outbound transfer/mes
- ✅ Load Balancer (10 Mbps)
- ✅ IPv4 pública gratuita

**Limitaciones**:
- ❌ Requiere tarjeta crédito (solo verificación, NO cobran)
- ❌ Si no usas recursos por 3+ meses, pueden reclamarlos
- ❌ Performance variable (shared infrastructure)
- ❌ UI confusa (típico Oracle)

**Setup**:
```bash
# 1. Registrarse en cloud.oracle.com
#    - Elegir "Free Tier" (no "Pay As You Go")
#    - Verificar con tarjeta (no cobran nada)

# 2. Crear Compute Instance
#    - Shape: VM.Standard.A1.Flex (ARM)
#    - OCPUs: 2
#    - Memory: 12GB
#    - OS: Ubuntu 22.04
#    - Boot volume: 50GB

# 3. Configurar Security List (Firewall)
#    - Ingress rule: TCP 443 from 0.0.0.0/0
#    - Ingress rule: TCP 80 from 0.0.0.0/0
#    - Ingress rule: TCP 22 from tu-ip/32

# 4. SSH y deploy
ssh ubuntu@instance-ip
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot
./scripts/deploy_alpha.sh
```

**Ventajas**:
- 🏆 Mejores specs gratuitas del mercado (24GB RAM!)
- 🏆 Sin límite de tiempo (Always Free)
- 🏆 ARM Ampere es muy eficiente

**Desventajas**:
- Proceso registro complejo (30-45 min)
- Puede tardar días en aprobar cuenta (anti-fraude)
- UI confusa

**Veredicto**: ⭐⭐⭐⭐⭐ - Mejor opción si tienes paciencia

---

### 2. 🔥 **GitHub Codespaces** (60 horas/mes)

**Recursos Gratuitos**:
- ✅ 60 horas/mes de 2-core VM
- ✅ 15GB storage por codespace
- ✅ Docker soportado
- ✅ Port forwarding automático
- ✅ SSL gratis (*.github.dev)

**Limitaciones**:
- ❌ Solo 60 horas/mes (2 horas/día)
- ❌ Máximo 2 cores
- ❌ Inactividad 30 min = auto-stop
- ❌ URL cambia (no dominio fijo)

**Setup**:
```bash
# 1. Fork del repositorio en GitHub
# 2. Abrir Codespace desde repo
#    Code → Codespaces → Create codespace on main

# 3. Dentro del codespace
./scripts/deploy_alpha.sh

# 4. Port forwarding automático
#    Ports tab → Forward port 7681
#    Visibility: Public
#    URL: https://xxxx-7681.app.github.dev
```

**Pros**:
- Setup instantáneo (30 segundos)
- Docker preinstalado
- SSL automático
- No requiere tarjeta crédito

**Contras**:
- Solo para testing/desarrollo
- 60 horas = ~2 horas/día
- No para producción 24/7

**Veredicto**: ⭐⭐⭐⭐ - Excelente para demos/testing cortos

---

### 3. 🎓 **Google Cloud Platform (GCP) Free Tier**

**Recursos Always Free**:
- ✅ **e2-micro VM** (2 vCPU shared, 1GB RAM)
- ✅ Solo en regiones USA: us-west1, us-central1, us-east1
- ✅ 30GB HDD storage
- ✅ 1GB egress/mes (red saliente)
- ✅ IPv4 estática gratis (si usas VM continuamente)

**Limitaciones**:
- ❌ Solo e2-micro (1GB RAM = justo para nuestra app)
- ❌ Solo 1 VM
- ❌ Solo regiones USA
- ❌ 1GB egress/mes (poco para web terminal)
- ❌ Requiere tarjeta crédito

**Setup**:
```bash
# 1. Registrarse en console.cloud.google.com
#    - $300 créditos por 90 días (bonus trial)
#    - Después del trial, pasa a Always Free

# 2. Crear VM
#    Compute Engine → VM Instances → Create
#    - Machine type: e2-micro (0.25-2 vCPU, 1 GB RAM)
#    - Region: us-west1, us-central1, or us-east1
#    - Boot disk: Ubuntu 22.04 LTS, 30GB
#    - Firewall: Allow HTTP, HTTPS

# 3. Configurar firewall
#    VPC Network → Firewall → Create rule
#    - tcp:443, tcp:80 from 0.0.0.0/0

# 4. SSH y deploy
gcloud compute ssh instance-name
# ... deploy normal
```

**Pros**:
- Gratis permanente
- Google reliability
- $300 créditos trial (3 meses)

**Contras**:
- Solo 1GB RAM (ajustado)
- Solo USA (latencia LATAM)
- 1GB egress limitado (web terminal consume)

**Veredicto**: ⭐⭐⭐ - OK para testing, limitado para producción

---

### 4. 🔵 **Azure for Students** (Solo estudiantes - $100 créditos)

**Recursos con Azure for Students**:
- ✅ $100 créditos/año (sin tarjeta crédito)
- ✅ B1s VM: 1 vCPU, 1GB RAM (~$7.30/mes)
- ✅ 13 meses de créditos
- ✅ Múltiples VMs posibles

**Limitaciones**:
- ❌ SOLO para estudiantes con email .edu
- ❌ $100/año = ~12 meses de B1s
- ❌ Después del año, requiere pago

**Setup**:
```bash
# 1. Verificar elegibilidad
#    azure.microsoft.com/en-us/free/students
#    - Email estudiante (.edu, .ac, etc)
#    - NO requiere tarjeta crédito

# 2. Crear VM
#    Virtual Machines → Create
#    - Size: B1s (1 vCPU, 1 GB RAM)
#    - OS: Ubuntu 22.04
#    - Region: East US (más barato)

# 3. Deploy normal
ssh azureuser@vm-ip
# ... setup docker, deploy
```

**Pros**:
- No requiere tarjeta (estudiantes)
- $100 = 13 meses de hosting
- Azure ecosystem

**Contras**:
- Solo estudiantes
- Limitado a 1 año
- UI compleja

**Veredicto**: ⭐⭐⭐⭐ - Excelente si eres estudiante

---

### 5. 🌐 **Render.com Free Tier**

**Recursos Gratuitos**:
- ✅ Web Service (Docker)
- ✅ 512MB RAM
- ✅ 0.1 CPU (shared)
- ✅ SSL automático
- ✅ Deploy automático desde Git

**Limitaciones**:
- ❌ **Auto-sleep después de 15 minutos de inactividad**
- ❌ **Cold start: 30-60 segundos**
- ❌ 750 horas/mes gratis (después paga)
- ❌ 100GB bandwidth/mes

**Setup**:
```yaml
# 1. Conectar GitHub repo a Render
#    render.com → New Web Service → Connect repo

# 2. Configuración automática
#    - Environment: Docker
#    - Dockerfile path: docker/Dockerfile.ttyd
#    - Plan: Free

# 3. Variables de entorno
#    Environment → Add env vars
#    TTYD_USER, TTYD_PASS, ODDS_API_KEY, etc.

# 4. Deploy automático
#    Git push → auto-deploy
```

**Pros**:
- Setup más simple (5 minutos)
- SSL automático
- Deploy Git automático
- No requiere tarjeta

**Contras**:
- ⚠️ **Sleep después 15 min = NO para web terminal 24/7**
- Cold start lento
- 512MB RAM limitado

**Veredicto**: ⭐⭐ - NO recomendado para web terminal (sleep lo arruina)

---

### 6. 🚀 **Fly.io Free Tier**

**Recursos Gratuitos**:
- ✅ 3 VMs shared-cpu-1x (256MB RAM cada una)
- ✅ 3GB storage persistente
- ✅ 160GB outbound transfer
- ✅ SSL automático
- ✅ Deploy global

**Limitaciones**:
- ❌ Solo 256MB RAM por VM (muy poco para Python + ttyd)
- ❌ Shared CPU (performance variable)
- ❌ Requiere tarjeta crédito (verificación, no cobran si usas solo free tier)

**Setup**:
```bash
# 1. Instalar flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app
cd Bet-Copilot
flyctl launch
#   - Name: bet-copilot
#   - Region: closest to you
#   - PostgreSQL: No
#   - Redis: No

# 4. Configurar variables
flyctl secrets set TTYD_USER=admin TTYD_PASS=pass123

# 5. Ajustar fly.toml
nano fly.toml
```

```toml
# fly.toml
app = "bet-copilot"

[build]
  dockerfile = "docker/Dockerfile.ttyd"

[[services]]
  internal_port = 7681
  protocol = "tcp"

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
  
  [[services.ports]]
    port = 80
    handlers = ["http"]

[env]
  TTYD_USER = "admin"
```

```bash
# 6. Deploy
flyctl deploy

# 7. URL
flyctl open  # https://bet-copilot.fly.dev
```

**Pros**:
- Deploy muy rápido
- SSL automático
- Global edge locations

**Contras**:
- 256MB RAM insuficiente (Python + Rich + APIs)
- Requiere tarjeta
- Puede necesitar upgrade a paid ($1.94/mes)

**Veredicto**: ⭐⭐⭐ - Marginal para nuestra app (RAM limitado)

---

### 7. 🐙 **Gitpod** (50 horas/mes)

**Recursos Gratuitos**:
- ✅ 50 horas/mes
- ✅ 4 workspaces paralelos
- ✅ 30GB storage
- ✅ Docker soportado
- ✅ Port forwarding público

**Limitaciones**:
- ❌ 50 horas/mes = 1.6 horas/día
- ❌ Timeout 30 min inactividad
- ❌ URL aleatoria

**Setup**:
```bash
# 1. Fork repo en GitHub
# 2. Prefijo URL: gitpod.io/#https://github.com/tu-usuario/Bet-Copilot
# 3. Auto-inicia workspace
# 4. Deploy
./scripts/deploy_alpha.sh

# 5. Port 7681 forward público automático
```

**Pros**:
- Setup instantáneo
- Más horas que Codespaces (50 vs 60)
- Docker preinstalado

**Contras**:
- Solo para desarrollo
- No 24/7

**Veredicto**: ⭐⭐⭐ - Alternativa a Codespaces

---

### 8. 🏠 **Ngrok + Localhost** (GRATIS pero requiere PC encendida)

**Recursos**:
- ✅ Expone localhost a internet
- ✅ HTTPS automático
- ✅ Plan gratuito: 1 proceso, 40 conexiones/min
- ✅ Dominio aleatorio: xxxx.ngrok.io

**Limitaciones**:
- ❌ Requiere tu PC/server encendido 24/7
- ❌ URL cambia cada reinicio (gratis)
- ❌ 40 req/min limit
- ❌ No production-ready

**Setup**:
```bash
# 1. Instalar ngrok
# Linux
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | \
  sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | \
  sudo tee /etc/apt/sources.list.d/ngrok.list && \
  sudo apt update && sudo apt install ngrok

# 2. Auth (gratis en ngrok.com/signup)
ngrok authtoken TU_TOKEN

# 3. Deploy local
cd Bet-Copilot
./scripts/deploy_alpha.sh

# 4. Exponer puerto
ngrok http 7681

# Output: Forwarding https://xxxx-ngrok.io -> http://localhost:7681
```

**Pros**:
- 100% gratis
- Setup 5 minutos
- No requiere VPS

**Contras**:
- Requiere PC encendido
- URL cambia
- Rate limited
- No para producción

**Veredicto**: ⭐⭐ - Solo para demos rápidas

---

### 9. 🌍 **Cloudflare Tunnel** (GRATIS permanente)

**Recursos**:
- ✅ 100% gratis sin límites
- ✅ Expone localhost a internet
- ✅ Dominio personalizado (si tienes uno)
- ✅ SSL automático
- ✅ Sin rate limits

**Limitaciones**:
- ❌ Requiere PC/server encendido 24/7
- ❌ Requiere dominio propio (opcional, pueden usar *.trycloudflare.com)

**Setup**:
```bash
# 1. Instalar cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# 2. Deploy local
cd Bet-Copilot
./scripts/deploy_alpha.sh

# 3. Crear tunnel TEMPORAL (sin dominio)
cloudflared tunnel --url http://localhost:7681

# Output: https://xxxx.trycloudflare.com

# ---- O tunnel PERMANENTE (con dominio) ----

# 4. Login Cloudflare
cloudflared tunnel login

# 5. Crear tunnel
cloudflared tunnel create bet-copilot
# Output: Tunnel credentials saved to ~/.cloudflared/UUID.json

# 6. Configurar DNS
cloudflared tunnel route dns bet-copilot terminal.tudominio.com

# 7. Crear config
nano ~/.cloudflared/config.yml
```

```yaml
# config.yml
tunnel: <UUID-del-tunnel>
credentials-file: /home/user/.cloudflared/<UUID>.json

ingress:
  - hostname: terminal.tudominio.com
    service: http://localhost:7681
  - service: http_status:404
```

```bash
# 8. Iniciar tunnel
cloudflared tunnel run bet-copilot

# 9. (Opcional) Systemd service para auto-start
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

**Pros**:
- Totalmente gratis
- Sin rate limits
- SSL automático
- Cloudflare DDoS protection

**Contras**:
- Requiere máquina local 24/7
- Requiere dominio para tunnel permanente

**Veredicto**: ⭐⭐⭐⭐ - Mejor opción si tienes PC/Raspberry Pi

---

### 10. 🍓 **Raspberry Pi + DuckDNS** (Costo hardware único)

**Recursos**:
- ✅ Costo único: ~$100 (Raspberry Pi 4 - 4GB)
- ✅ Consumo eléctrico: ~$2-3/mes
- ✅ Control total
- ✅ Sin límites de tiempo

**Limitaciones**:
- ❌ Requiere IP pública o DDNS
- ❌ Uptime depende de tu internet
- ❌ Configuración router/firewall
- ❌ Sin backups automáticos

**Setup**:
```bash
# 1. Hardware necesario
#    - Raspberry Pi 4 (4GB RAM): $55
#    - Tarjeta SD 32GB: $10
#    - Case + fuente: $20
#    - Total: ~$85-100

# 2. Instalar Ubuntu Server 22.04 ARM
#    Raspberry Pi Imager → Ubuntu Server 22.04 LTS (64-bit)

# 3. SSH al Pi
ssh ubuntu@raspberrypi.local

# 4. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker ubuntu

# 5. Clonar y deploy
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot
./scripts/deploy_alpha.sh

# 6. Configurar DuckDNS (dominio dinámico gratis)
#    - Registrarse en duckdns.org
#    - Crear subdomain: betcopilot.duckdns.org
#    - Script actualización IP:

mkdir ~/duckdns
cd ~/duckdns
nano duck.sh
```

```bash
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=betcopilot&token=TU_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

```bash
chmod +x duck.sh
crontab -e
# Agregar: */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1

# 7. Port forwarding en router
#    - Abrir 443 → Pi IP:443
#    - Abrir 80 → Pi IP:80
#    (Varía por router, ver manual)

# 8. (Opcional) Cloudflare Tunnel en lugar de port forwarding
#    Ver opción #9 arriba
```

**Pros**:
- Costo único ~$100
- Sin costos mensuales (solo electricidad)
- Control total
- Specs suficientes (4GB RAM)

**Contras**:
- Setup más complejo
- Depende de tu internet
- No backups automáticos
- Mantenimiento manual

**Veredicto**: ⭐⭐⭐⭐ - Excelente si sabes administrar

---

## 📊 Comparativa Final: Opciones 100% Gratis

| Plataforma | RAM | Horas/mes | Mejor para | Dificultad |
|------------|-----|-----------|------------|------------|
| **Oracle Free** | 24GB | ∞ | Producción 24/7 | ⭐⭐⭐⭐ |
| **GCP Free** | 1GB | ∞ | Testing ligero | ⭐⭐⭐ |
| **GitHub Codespaces** | 4GB | 60h | Demos/dev | ⭐ |
| **Gitpod** | 8GB | 50h | Desarrollo | ⭐ |
| **Render** | 512MB | ∞ * | NO (sleep) | ⭐ |
| **Fly.io** | 256MB | ∞ | NO (muy poco RAM) | ⭐⭐ |
| **Ngrok + Local** | Ilimitado | ∞ | Demos rápidas | ⭐ |
| **Cloudflare Tunnel** | Ilimitado | ∞ | Producción local | ⭐⭐⭐ |
| **Raspberry Pi** | 4GB | ∞ | Self-hosted | ⭐⭐⭐⭐ |

\* Render duerme después 15 min, no viable para terminal web

---

## 🏆 Ranking por Caso de Uso

### 🥇 Mejor para Producción 24/7 (Gratis)
1. **Oracle Cloud Always Free** - 24GB RAM, sin límites
2. **GCP e2-micro** - 1GB RAM, solo USA, 1GB egress limitado
3. **Raspberry Pi + Cloudflare Tunnel** - Requiere hardware (~$100)

### 🥇 Mejor para Testing/Demos
1. **GitHub Codespaces** - 60h/mes, setup instantáneo
2. **Gitpod** - 50h/mes
3. **Ngrok + Local** - Ilimitado pero requiere PC

### 🥇 Mejor para Estudiantes
1. **Azure for Students** - $100 créditos/año
2. **GitHub Education Pack** - Incluye DO $200, Heroku, etc.

### 🥇 Sin Tarjeta de Crédito
1. **GitHub Codespaces** - No requiere tarjeta
2. **Gitpod** - No requiere tarjeta
3. **Render** - No requiere tarjeta (pero duerme)

---

## 🎯 Mi Recomendación Final

### Opción A: Máxima Calidad (Gratis permanente)
```
1. Registrarse en Oracle Cloud (30-45 min)
2. Esperar aprobación cuenta (1-3 días)
3. Crear VM ARM Ampere (2 vCPU, 12GB RAM)
4. Deploy y listo → 24/7 gratis PARA SIEMPRE
```
**Tiempo**: 3-5 días (aprobación)  
**Costo**: $0/mes  
**Specs**: ⭐⭐⭐⭐⭐

---

### Opción B: Máxima Rapidez (Testing)
```
1. GitHub → Fork Bet-Copilot
2. Code → Codespaces → Create
3. ./scripts/deploy_alpha.sh
4. Forward port 7681 → Listo en 2 minutos
```
**Tiempo**: 2 minutos  
**Costo**: $0 (60h/mes)  
**Specs**: ⭐⭐⭐⭐

---

### Opción C: Self-Hosted (Control total)
```
1. Comprar Raspberry Pi 4 (4GB) - $100
2. Instalar Ubuntu Server 22.04
3. Deploy + Cloudflare Tunnel
4. Gratis para siempre (solo luz ~$2/mes)
```
**Tiempo**: 1 día setup  
**Costo**: $100 una vez + $2/mes luz  
**Specs**: ⭐⭐⭐⭐

---

## 🚀 Quick Start: Oracle Cloud (Paso a Paso)

### 1. Registro (15-20 min)
```
1. Ir a cloud.oracle.com
2. Click "Start for free"
3. Llenar formulario:
   - Email
   - Nombre/Dirección
   - Tarjeta crédito (solo verificación, NO cobran)
4. Verificar email
5. Esperar aprobación (1-3 días hábiles)
```

### 2. Crear Instancia (10 min)
```
1. Login → Compute → Instances → Create Instance
2. Name: bet-copilot-alpha
3. Image: Ubuntu 22.04 (Canonical)
4. Shape: 
   - Type: Virtual Machine
   - Shape series: Ampere
   - Shape: VM.Standard.A1.Flex
   - OCPUs: 2
   - Memory: 12 GB
5. Networking:
   - VCN: Default (auto-create)
   - Public IP: Assign
6. SSH Keys: 
   - Paste SSH public key (o generar)
7. Boot Volume: 50GB
8. Create
```

### 3. Configurar Firewall (5 min)
```
1. Instance details → Primary VNIC → Subnet
2. Security Lists → Default Security List
3. Add Ingress Rules:
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 443
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 80
   - Source: TU_IP/32, Protocol: TCP, Port: 22
```

### 4. Deploy (10 min)
```bash
# SSH
ssh ubuntu@<instance-public-ip>

# Actualizar
sudo apt update && sudo apt upgrade -y

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

# Clonar
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot

# Configurar
cp docker/.env.example docker/.env
nano docker/.env  # Editar credenciales

# Deploy
./scripts/deploy_alpha.sh

# Firewall interno (Oracle usa iptables)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save

# Verificar
curl http://localhost:7681
```

### 5. SSL (Opcional - Let's Encrypt)
```bash
# Si tienes dominio
sudo apt install certbot
sudo certbot certonly --standalone -d betcopilot.tudominio.com
sudo cp /etc/letsencrypt/live/betcopilot.tudominio.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/betcopilot.tudominio.com/privkey.pem docker/ssl/key.pem

# Actualizar nginx.conf
nano docker/nginx.conf  # server_name betcopilot.tudominio.com;

# Deploy con Nginx
cd docker
docker-compose --profile production up -d
```

---

## 📋 Troubleshooting Común (Oracle)

### Cuenta no aprobada después de 3 días
```
- Verificar email (spam)
- Contactar soporte Oracle (chat 24/7)
- Probar con otra tarjeta/dirección
```

### "Out of host capacity" al crear VM
```
- Cambiar a otra availability domain (AD-1, AD-2, AD-3)
- O cambiar región (Phoenix, Ashburn, San Jose)
- Oracle tiene capacidad limitada ARM (muy demandado)
```

### No puedo acceder al puerto 443
```
# Firewall interno Oracle (iptables)
sudo iptables -L INPUT --line-numbers
sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save

# Security List (panel web)
# Verificar ingress rules estén bien
```

---

## 💡 Tips Finales

### Para Maximizar Plan Gratuito Oracle
- Usa ARM Ampere (más RAM gratis que x86)
- Crea 1 VM con 4 vCPU + 24GB (o 2 VMs con 2+12GB cada una)
- Usa los 200GB storage totales (distribuidos entre VMs)
- Configura backups manuales (los automáticos cuestan)

### Para Evitar Perder Cuenta Oracle
- Usa la VM al menos 1 vez/mes
- Configura monitoring/alertas
- Backup tu .env y configuración regularmente

### Combinar Opciones
```
Testing:    GitHub Codespaces (60h/mes)
Staging:    Oracle Free Tier (24/7)
Producción: DigitalOcean $6 (cuando escales)
```

---

**Última actualización**: 2026-01-10  
**Autor**: SebastianVernisMora
