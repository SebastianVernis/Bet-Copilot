# 🐙 Guía Completa de Despliegue en Gitpod - Bet-Copilot

**Fecha**: 2026-01-10  
**Versión**: v0.7.0-alpha  
**Plataforma**: Gitpod.io

---

## 📊 Por qué Gitpod

### ✅ Ventajas
- **50 horas/mes gratuitas** (1.6 horas/día)
- **8GB RAM** (suficiente para Python + ttyd + APIs)
- **4 workspaces simultáneos** (desarrollo paralelo)
- **Docker preinstalado** (listo para usar)
- **Port forwarding público automático** (SSL incluido)
- **No requiere tarjeta de crédito**
- **Setup instantáneo** (30 segundos)
- **Integración Git** (commit/push desde workspace)

### ⚠️ Limitaciones
- **50 horas/mes** = ~1.6 horas/día (suficiente para demos/testing)
- **Timeout 30 min inactividad** (se duerme automáticamente)
- **URL aleatoria** (cambia cada workspace, pero puedes hacer fija con config)
- **No para producción 24/7** (solo desarrollo/demos)

---

## 🚀 Quick Start (5 minutos)

### Opción A: Desde URL (Más Rápido)

```bash
# 1. Abrir en Gitpod (prefija URL GitHub con gitpod.io/#)
https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot

# 2. Espera 30 segundos (auto-provisiona workspace)

# 3. En la terminal del workspace:
git checkout laptop/feature/web-terminal-shellinabox
./scripts/deploy_alpha.sh

# 4. Gitpod detecta puerto 7681 automáticamente
# Click "Open Preview" o "Open Browser" en la notificación
# URL pública: https://7681-yourworkspace.gitpod.io
```

### Opción B: Desde Dashboard (Más Control)

```bash
# 1. Ir a gitpod.io/workspaces
# 2. Login con GitHub
# 3. New Workspace → Repository URL:
#    https://github.com/SebastianVernis/Bet-Copilot
# 4. Branch: laptop/feature/web-terminal-shellinabox
# 5. Create
```

---

## 📁 Configuración Óptima con `.gitpod.yml`

Para optimizar el workspace y pre-configurar todo, crea este archivo:

### `.gitpod.yml` (Recomendado)

```yaml
# Gitpod workspace configuration
image: gitpod/workspace-full

# Puertos a exponer
ports:
  - port: 7681
    name: "Web Terminal"
    description: "Bet-Copilot ttyd web terminal"
    visibility: public
    onOpen: notify
  
  - port: 443
    name: "HTTPS (nginx)"
    visibility: public
    onOpen: ignore
  
  - port: 80
    name: "HTTP (nginx)"
    visibility: public
    onOpen: ignore

# Comandos al iniciar workspace
tasks:
  - name: Setup & Deploy
    init: |
      # Checkout branch correcto
      git checkout laptop/feature/web-terminal-shellinabox || true
      
      # Crear .env si no existe
      if [ ! -f docker/.env ]; then
        cp docker/.env.example docker/.env
        echo "⚠️  Configura docker/.env con tus API keys"
      fi
      
      # Instalar dependencias Python (para testing local)
      pip install -r requirements.txt
      
      echo "✅ Workspace inicializado"
      echo "📝 Edita docker/.env con tus credenciales"
      echo "🚀 Luego ejecuta: ./scripts/deploy_alpha.sh"
    
    command: |
      echo ""
      echo "╔═══════════════════════════════════════╗"
      echo "║     BET-COPILOT GITPOD WORKSPACE      ║"
      echo "╚═══════════════════════════════════════╝"
      echo ""
      echo "📝 PASOS:"
      echo "  1. Editar docker/.env con tus API keys"
      echo "  2. Ejecutar: ./scripts/deploy_alpha.sh"
      echo "  3. Abrir puerto 7681 en panel Ports"
      echo ""
      echo "⏱️  Recuerda: 50 horas/mes, timeout 30 min"
      echo ""

# GitHub integration
github:
  prebuilds:
    master: true
    branches: true
    pullRequests: true
    pullRequestsFromForks: false
    addCheck: false
    addComment: false
    addBadge: false

# VS Code extensions (opcional)
vscode:
  extensions:
    - ms-python.python
    - ms-azuretools.vscode-docker
    - eamodio.gitlens
```

---

## 🔧 Setup Detallado

### 1. Primer Inicio (Automático)

```bash
# Cuando abres el workspace, Gitpod ejecuta automáticamente:
# - git clone del repo
# - Instala dependencias (si .gitpod.yml lo especifica)
# - Ejecuta tasks.init

# Verás en terminal:
✅ Workspace inicializado
📝 Edita docker/.env con tus credenciales
🚀 Luego ejecuta: ./scripts/deploy_alpha.sh
```

### 2. Configurar Credenciales

```bash
# Editar .env con tus API keys
cd docker
nano .env  # O usar VS Code editor
```

```bash
# docker/.env
TTYD_USER=admin
TTYD_PASS=gitpod_demo_2026

# API Keys (obtener de proveedores)
ODDS_API_KEY=tu_odds_api_key_aqui
API_FOOTBALL_KEY=tu_football_api_key
GEMINI_API_KEY=tu_gemini_api_key

# Opcional
BLACKBOX_API_KEY=tu_blackbox_key
```

### 3. Deploy de Contenedores

```bash
# Ejecutar script de deploy
./scripts/deploy_alpha.sh

# Output esperado:
🚀 Bet-Copilot Alpha Deployment
================================

📦 Building Docker image...
[+] Building 45.2s (12/12) FINISHED

🔄 Starting containers...
[+] Running 2/2
 ✔ Network docker_bet-network  Created
 ✔ Container bet-copilot-ttyd  Started

⏳ Waiting for services to be healthy...

✅ Deployment successful!

📡 Access Information:
   - Web Terminal: http://localhost:7681
   - Username: admin
   - Password: (check docker/.env)
```

### 4. Acceder al Terminal Web

#### Opción A: URL Pública (Recomendado)

```bash
# 1. Abrir panel "Ports" (lado derecho o View → Ports)
# 2. Buscar puerto 7681
# 3. Hacer clic en icono "Open Browser" (🌐)
# 4. URL será: https://7681-yourworkspace.gitpod.io

# 5. Login:
#    Username: admin
#    Password: (del .env)
```

#### Opción B: Preview Interno

```bash
# 1. En terminal: gp url 7681
# Output: https://7681-workspace-id.gitpod.io

# 2. Click en URL o:
#    View → Command Palette → "Ports: Open Preview"
```

---

## 🎛️ Gestión de Puertos

### Ver Puertos Activos

```bash
# En terminal Gitpod
gp ports list

# Output:
PORT    STATUS          URL
7681    open (public)   https://7681-workspace.gitpod.io
443     not exposed     -
80      not exposed     -
```

### Hacer Puerto Público Manualmente

```bash
# Si puerto no se expone automáticamente
gp ports expose 7681

# O desde UI:
# Panel Ports → Right-click puerto → Make Public
```

### Obtener URL Pública

```bash
# En scripts o terminal
export TERMINAL_URL=$(gp url 7681)
echo "Terminal disponible en: $TERMINAL_URL"
```

---

## 📊 Monitoreo y Debugging

### Ver Logs de Contenedores

```bash
# Logs ttyd en tiempo real
docker-compose -f docker/docker-compose.yml logs -f ttyd

# Logs nginx (si usas perfil production)
docker-compose -f docker/docker-compose.yml logs -f nginx

# Todos los logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Ver Estado de Contenedores

```bash
# Estado
docker-compose -f docker/docker-compose.yml ps

# Recursos (CPU, RAM)
docker stats

# Health checks
docker inspect bet-copilot-ttyd | grep -A5 Health
```

### Debugging CLI Python

```bash
# Probar CLI localmente (sin Docker)
python3 main.py

# Ver logs aplicación
# (Los logs van a stdout, visible en docker-compose logs)
```

---

## ⚙️ Comandos Útiles

### Gestión de Workspace

```bash
# Pausar workspace manualmente (ahorra horas)
gp stop

# Ver tiempo restante este mes
# (Solo desde dashboard: gitpod.io/usage)

# Compartir workspace con otro usuario
gp share

# Crear snapshot del workspace
gp snapshot

# Clonar workspace actual
# Dashboard → Three dots → Duplicate
```

### Gestión de Docker

```bash
# Reiniciar contenedores
docker-compose -f docker/docker-compose.yml restart

# Detener
docker-compose -f docker/docker-compose.yml stop

# Iniciar
docker-compose -f docker/docker-compose.yml start

# Recrear (si cambiaste Dockerfile)
docker-compose -f docker/docker-compose.yml up -d --build

# Limpiar todo
docker-compose -f docker/docker-compose.yml down -v
```

### Git desde Workspace

```bash
# Commit cambios
git add .
git commit -m "feat: configuración Gitpod"

# Push (Gitpod maneja auth automáticamente)
git push origin laptop/feature/web-terminal-shellinabox

# Pull
git pull origin master
```

---

## 🔒 Seguridad en Gitpod

### Variables de Entorno Seguras

**❌ NUNCA comitear `.env` con API keys**

Usar variables de entorno de Gitpod:

```bash
# Opción A: Gitpod Environment Variables (recomendado)
# 1. Dashboard → Account Settings → Variables
# 2. Agregar:
#    Name: ODDS_API_KEY
#    Value: tu_key_real
#    Scope: SebastianVernis/Bet-Copilot/*

# 3. En .gitpod.yml, usar variables:
```

```yaml
# .gitpod.yml
tasks:
  - name: Deploy
    command: |
      # Variables inyectadas automáticamente
      echo "TTYD_USER=admin" > docker/.env
      echo "TTYD_PASS=${GITPOD_WORKSPACE_ID}" >> docker/.env
      echo "ODDS_API_KEY=${ODDS_API_KEY}" >> docker/.env
      echo "API_FOOTBALL_KEY=${API_FOOTBALL_KEY}" >> docker/.env
      echo "GEMINI_API_KEY=${GEMINI_API_KEY}" >> docker/.env
      
      ./scripts/deploy_alpha.sh
```

**Opción B: Usar `.env` local (más simple pero menos seguro)**

```bash
# .gitignore debe incluir:
docker/.env
.env
*.env
```

### Credenciales ttyd

```bash
# Generar password seguro automático
export TTYD_PASS=$(openssl rand -base64 24)
echo "TTYD_PASS=${TTYD_PASS}" >> docker/.env

# O usar workspace ID como password
export TTYD_PASS="${GITPOD_WORKSPACE_ID}"
```

---

## 📈 Optimización de Uso (50 horas/mes)

### Estrategias para Maximizar Horas

#### 1. **Pausar Workspace Manualmente**
```bash
# Cuando termines, pausar manualmente (no esperar timeout)
gp stop

# Ahorra ~25 min promedio por sesión
```

#### 2. **Usar Prebuilds** (Workspaces Preconstruidos)

```yaml
# .gitpod.yml
github:
  prebuilds:
    master: true
    branches: true
```

- Gitpod construye imagen Docker en background
- Workspace inicia en 10s (vs 2-3 min)
- Ahorra ~2 min por inicio = más sesiones

#### 3. **Snapshots para Sesiones Largas**

```bash
# Crear snapshot del estado actual
gp snapshot

# Compartir URL snapshot con ti mismo
# Abrir snapshot cuando vuelvas (estado preservado)
```

#### 4. **Monitorear Uso**

```bash
# Dashboard → Usage (gitpod.io/usage)
# Ver:
# - Horas usadas este mes
# - Horas restantes
# - Workspaces activos
```

### Cálculo de Uso Típico

```
Sesión demo (15 min):
  - Inicio workspace: 2 min
  - Deploy containers: 3 min
  - Testing: 10 min
  Total: 15 min

50 horas/mes ÷ 15 min = ~200 demos/mes
O: 1.6 horas/día = 6 demos/día de 15 min
```

---

## 🎨 Personalización de Workspace

### Extensiones VS Code Recomendadas

```yaml
# .gitpod.yml
vscode:
  extensions:
    # Python
    - ms-python.python
    - ms-python.vscode-pylance
    
    # Docker
    - ms-azuretools.vscode-docker
    
    # Git
    - eamodio.gitlens
    
    # Markdown
    - yzhang.markdown-all-in-one
    
    # Themes (opcional)
    - GitHub.github-vscode-theme
```

### Dotfiles Personalizados

```bash
# Crear repo dotfiles con tus configs
# Ejemplo: github.com/tu-usuario/dotfiles

# Gitpod Settings → Dotfiles
# Repository: tu-usuario/dotfiles

# Gitpod clonará y ejecutará install.sh automáticamente
```

Ejemplo `install.sh`:
```bash
#!/bin/bash
# ~/dotfiles/install.sh

# Bash aliases
cat >> ~/.bashrc <<'EOF'
alias dc='docker-compose'
alias dps='docker ps'
alias dlogs='docker-compose logs -f'
EOF

# Git config
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

---

## 🔄 Workflows Recomendados

### Workflow 1: Demo Rápida (10 min)

```bash
# 1. Abrir workspace desde URL
https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot

# 2. Esperar inicio (30s)

# 3. Deploy
./scripts/deploy_alpha.sh

# 4. Abrir puerto 7681
gp url 7681

# 5. Demo en navegador

# 6. Pausar cuando termines
gp stop
```

### Workflow 2: Desarrollo Activo (1-2 horas)

```bash
# 1. Abrir workspace

# 2. Crear branch nueva
git checkout -b feature/mi-feature

# 3. Desarrollo:
#    - Editar código
#    - Probar localmente: python3 main.py
#    - Rebuild Docker: docker-compose up -d --build

# 4. Commit
git add .
git commit -m "feat: nueva funcionalidad"
git push origin feature/mi-feature

# 5. Crear PR desde GitHub

# 6. Pausar workspace
gp stop
```

### Workflow 3: Testing Multi-Usuario (20 min)

```bash
# 1. Deploy en workspace

# 2. Compartir workspace
gp share
# Output: https://gitpod.io/#/workspace-id

# 3. Otros usuarios abren esa URL (tienen acceso read-only)

# 4. O compartir solo URL terminal:
gp url 7681
# https://7681-workspace.gitpod.io

# 5. Multiple usuarios prueban simultáneamente
#    (máx 10 clientes en ttyd)
```

---

## 🐛 Troubleshooting Gitpod

### Problema: Workspace no inicia

```bash
# Causas comunes:
# 1. Cuota de 50 horas agotada
#    → Ver gitpod.io/usage
#    → Esperar próximo mes o upgrade a paid

# 2. Workspace corrupto
#    → Dashboard → Delete workspace → Crear nuevo

# 3. .gitpod.yml con errores
#    → Validar YAML: yamllint .gitpod.yml
```

### Problema: Puerto 7681 no accesible

```bash
# 1. Verificar contenedor corriendo
docker ps | grep ttyd

# 2. Verificar puerto expuesto
gp ports list

# 3. Hacer público manualmente
gp ports expose 7681

# 4. Verificar firewall contenedor
docker logs bet-copilot-ttyd

# 5. Test local primero
curl http://localhost:7681
```

### Problema: Docker out of space

```bash
# Limpiar imágenes/contenedores viejos
docker system prune -af

# Ver uso disco
df -h

# Gitpod workspace tiene 30GB
# Si lleno, crear workspace nuevo
```

### Problema: Timeout muy rápido

```bash
# Gitpod timeout por inactividad: 30 min (free tier)
# No hay forma de extenderlo en free

# Workarounds:
# 1. Keep-alive script (no recomendado, gasta horas)
# 2. Pausar/reanudar manualmente cuando no uses
# 3. Usar snapshot para sesiones largas

# Upgrade a paid ($9/mes) para:
# - Timeout 3 horas
# - 100 horas/mes
```

### Problema: Variables entorno no se cargan

```bash
# Verificar .env existe
ls -la docker/.env

# Verificar docker-compose lee .env
docker-compose -f docker/docker-compose.yml config

# Verificar variables dentro contenedor
docker exec bet-copilot-ttyd env | grep TTYD
```

---

## 📊 Comparación: Gitpod vs Alternativas

| Feature | Gitpod | Codespaces | Render | Oracle Free |
|---------|--------|------------|--------|-------------|
| **Horas/mes** | 50 | 60 | ∞* | ∞ |
| **RAM** | 8GB | 4GB | 512MB | 24GB |
| **Timeout** | 30 min | 30 min | 15 min | N/A |
| **Docker** | ✅ | ✅ | ✅ | ✅ |
| **SSL Auto** | ✅ | ✅ | ✅ | Manual |
| **Setup** | 30s | 30s | 5 min | 3 días |
| **24/7** | ❌ | ❌ | ❌** | ✅ |

\* Render duerme tras 15 min inactividad  
\** No viable para web terminal

**Veredicto**: Gitpod es mejor que Render para terminal web (no duerme mid-sesión)

---

## 💡 Tips Pro

### 1. URL Fija con Dominio Custom (Paid)
```bash
# Gitpod Paid ($9/mes) permite:
# - Custom domain: terminal.tudominio.com
# - 100 horas/mes
# - Timeout 3h
```

### 2. Prebuilds para Speed
```yaml
# .gitpod.yml optimizado
github:
  prebuilds:
    master: true
    branches: true
    pullRequests: true
    pullRequestsFromForks: false

# Gitpod construye Docker image en background
# Workspace inicia en 10s vs 2 min
```

### 3. Multi-Workspace para Diferentes Branches
```bash
# Dashboard → New Workspace
# Branch: feature/nueva-funcionalidad

# Permite desarrollar múltiples features en paralelo
# Sin afectar workspace principal
```

### 4. Integración CI/CD
```yaml
# .github/workflows/gitpod.yml
name: Open in Gitpod
on: [pull_request]

jobs:
  gitpod:
    runs-on: ubuntu-latest
    steps:
      - uses: gitpod-io/gitpod-action@v1
        with:
          prebuild: true
```

---

## 🎯 Checklist Final

### Pre-Deploy
- [ ] Fork/clonar repositorio
- [ ] Crear `.gitpod.yml` (copiar de arriba)
- [ ] Commit y push `.gitpod.yml`
- [ ] Obtener API keys (Odds API, Gemini, etc.)

### Deploy en Gitpod
- [ ] Abrir workspace: `gitpod.io/#https://github.com/...`
- [ ] Esperar inicialización (30s)
- [ ] Editar `docker/.env` con credenciales
- [ ] Ejecutar `./scripts/deploy_alpha.sh`
- [ ] Verificar contenedor: `docker ps`
- [ ] Abrir puerto 7681 en panel Ports

### Testing
- [ ] Acceder a URL pública: `https://7681-workspace.gitpod.io`
- [ ] Login con usuario/password del `.env`
- [ ] Probar comandos CLI: `mercados`, `estado`, `ayuda`
- [ ] Verificar APIs funcionan
- [ ] Compartir URL para testing multi-usuario

### Post-Demo
- [ ] Pausar workspace: `gp stop` (ahorra horas)
- [ ] Monitorear uso: `gitpod.io/usage`
- [ ] Commit cambios si desarrollaste: `git push`

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [Gitpod Docs](https://www.gitpod.io/docs)
- [.gitpod.yml Reference](https://www.gitpod.io/docs/references/gitpod-yml)
- [Port Forwarding](https://www.gitpod.io/docs/configure/workspaces/ports)

### Ejemplos `.gitpod.yml`
- [Python Projects](https://github.com/gitpod-io/template-python-django)
- [Docker Compose](https://github.com/gitpod-io/template-docker-compose)

### Comunidad
- [Gitpod Community Discord](https://www.gitpod.io/chat)
- [GitHub Discussions](https://github.com/gitpod-io/gitpod/discussions)

---

## 🏁 Siguiente Paso: Crear `.gitpod.yml`

**Archivo listo para commit**:

```bash
# En tu repo local
nano .gitpod.yml
# Copiar contenido de arriba

git add .gitpod.yml
git commit -m "feat: add Gitpod workspace configuration"
git push origin laptop/feature/web-terminal-shellinabox

# Ahora prueba:
# https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot
```

---

**Autor**: SebastianVernisMora  
**Email**: pelongemelo@gmail.com  
**Última actualización**: 2026-01-10
