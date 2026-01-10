# 🚀 Inicio Rápido en Gitpod (2 minutos)

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot)

---

## 📋 Requisitos Previos

- ✅ Cuenta GitHub (gratis)
- ✅ API keys de:
  - [The Odds API](https://the-odds-api.com/) (REQUERIDA)
  - [Google Gemini](https://ai.google.dev/) (opcional)
  - [API-Football](https://www.api-football.com/) (opcional)

---

## ⚡ 3 Pasos Rápidos

### 1. Abrir Workspace (30 segundos)

Click en el botón:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot)

O copia esta URL en tu navegador:
```
https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot
```

Gitpod abrirá VS Code en el navegador y inicializará el proyecto automáticamente.

---

### 2. Configurar API Keys (30 segundos)

En la terminal de Gitpod:

```bash
# Editar archivo de configuración
nano docker/.env
```

**Edita estas líneas**:
```bash
ODDS_API_KEY=tu_odds_api_key_aqui      # ← REEMPLAZAR
GEMINI_API_KEY=tu_gemini_api_key_aqui  # ← OPCIONAL
```

Guardar: `Ctrl+O` → `Enter` → Salir: `Ctrl+X`

---

### 3. Desplegar (1 minuto)

```bash
./scripts/deploy_alpha.sh
```

**Output esperado**:
```
🚀 Bet-Copilot Alpha Deployment
================================

📦 Building Docker image...
✅ Deployment successful!

📡 Access Information:
   - Web Terminal: http://localhost:7681
```

---

## 🌐 Acceder al Terminal Web

### Opción A: Desde Panel Ports (Recomendado)

1. Abrir panel **"Ports"** (lado derecho o `View → Ports`)
2. Buscar puerto **7681**
3. Click en icono **"Open Browser"** (🌐)
4. **Login**:
   - Usuario: `admin`
   - Password: ver en `docker/.env` (línea `TTYD_PASS`)

### Opción B: Desde Terminal

```bash
# Obtener URL pública
gp url 7681

# Output: https://7681-yourworkspace.gitpod.io
# Abrir esa URL en navegador
```

---

## 🎮 Probar la Aplicación

Una vez dentro del terminal web:

```bash
# Ver estado de APIs
estado

# Listar mercados disponibles
mercados

# Analizar un partido (con autocompletado)
analizar Arsenal vs Chelsea

# Ver comandos disponibles
ayuda

# Salir
salir
```

---

## 📊 Monitoreo

### Ver Logs
```bash
docker-compose -f docker/docker-compose.yml logs -f ttyd
```

### Ver Estado Contenedor
```bash
docker ps
```

### Reiniciar si Necesario
```bash
docker-compose -f docker/docker-compose.yml restart
```

---

## ⏸️ Pausar Workspace (Ahorra Horas)

Cuando termines:

```bash
gp stop
```

O cierra la pestaña del navegador (auto-pausa después de 30 min).

**Plan Free**: 50 horas/mes → Pausar manualmente ahorra ~25 min/sesión

---

## 🔧 Troubleshooting

### Puerto 7681 no se expone automáticamente

```bash
# Hacer público manualmente
gp ports expose 7681

# Verificar
gp ports list
```

### Contenedor no inicia

```bash
# Ver logs de error
docker-compose -f docker/docker-compose.yml logs ttyd

# Recrear contenedor
docker-compose -f docker/docker-compose.yml up -d --force-recreate
```

### Error "ODDS_API_KEY not configured"

```bash
# Verificar .env
cat docker/.env | grep ODDS_API_KEY

# Si dice "your_odds_api_key_here", editarlo:
nano docker/.env
```

---

## 💡 Tips Pro

### Variables de Entorno Persistentes

Para no editar `.env` cada vez:

1. Ir a [gitpod.io/user/variables](https://gitpod.io/user/variables)
2. Agregar variables:
   - `ODDS_API_KEY` = tu_key
   - `GEMINI_API_KEY` = tu_key
3. Scope: `SebastianVernis/Bet-Copilot/*`

Gitpod las inyectará automáticamente.

### Probar CLI sin Docker

```bash
# Más rápido para testing de código
python3 main.py
```

### Compartir Workspace

```bash
# Generar URL compartible
gp share

# Otros usuarios pueden ver tu workspace (read-only)
```

---

## 📚 Más Información

- **Setup Completo**: [GITPOD_SETUP_GUIDE.md](GITPOD_SETUP_GUIDE.md)
- **Opciones Hosting**: [FREE_HOSTING_OPTIONS.md](FREE_HOSTING_OPTIONS.md)
- **Documentación Técnica**: [docs/web_terminal/](docs/web_terminal/)

---

## 🆘 Ayuda

### Uso de Gitpod
- Ver horas restantes: [gitpod.io/usage](https://gitpod.io/usage)
- Documentación: [gitpod.io/docs](https://www.gitpod.io/docs)
- Discord: [gitpod.io/chat](https://www.gitpod.io/chat)

### Proyecto Bet-Copilot
- Issues: [GitHub Issues](https://github.com/SebastianVernis/Bet-Copilot/issues)
- Email: pelongemelo@gmail.com

---

**¡Listo! 🎉 Ahora tienes Bet-Copilot corriendo en Gitpod.**

⏱️ Tiempo total: ~2 minutos  
💰 Costo: $0 (50 horas/mes gratis)
