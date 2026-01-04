# Deployment Guide - Bet-Copilot

Guía completa para desplegar y configurar Bet-Copilot desde cero.

---

## 🚀 Quick Start (3 minutos)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Bet-Copilot

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configuración interactiva
python scripts/setup.py

# 4. Verificar APIs
python scripts/check_apis.py

# 5. Lanzar aplicación
python scripts/start.py
```

---

## 📋 Requisitos

### Sistema
- **Python**: 3.10 o superior
- **Sistema operativo**: Linux, macOS, Windows
- **Memoria**: 512 MB RAM mínimo
- **Disco**: 100 MB libres

### Dependencias
```bash
pip install -r requirements.txt
```

Principales:
- `aiohttp` - HTTP async
- `aiosqlite` - SQLite async
- `rich` - UI terminal
- `python-dotenv` - Env vars

---

## 🔧 Scripts de Deployment

### 1. `scripts/setup.py` - Configuración Inicial

**Propósito**: Configuración interactiva guiada de API keys.

**Uso**:
```bash
python scripts/setup.py
```

**Funcionalidad**:
- ✅ Guía paso a paso para cada API
- ✅ Muestra instrucciones de obtención de keys
- ✅ Valida formato de keys
- ✅ Crea archivo `.env` automáticamente
- ✅ Hace backup de configuración anterior
- ✅ Permite skip de APIs opcionales

**Salida**:
```
Bet-Copilot/
└── .env           # Archivo creado con configuración
└── .env.backup    # Backup si ya existía .env
```

**Ejemplo de sesión**:
```
⚡ Bet-Copilot Setup ⚡

━━━ The Odds API ━━━
Required for fetching betting odds
Status: REQUIRED

Enter your The Odds API key: **********************
✓ Key accepted

━━━ API-Football ━━━
Optional - for historical statistics
Configure API-Football? [y/N]: n

━━━ General Settings ━━━
Log Level (DEBUG/INFO/WARNING/ERROR): INFO

✓ Configuration saved to .env
```

---

### 2. `scripts/check_apis.py` - Validación de APIs

**Propósito**: Verifica que todas las API keys son válidas y funcionales.

**Uso**:
```bash
python scripts/check_apis.py
```

**Funcionalidad**:
- ✅ Prueba conectividad real a cada API
- ✅ Verifica rate limits disponibles
- ✅ Detecta keys inválidas
- ✅ Muestra cuota restante
- ✅ Exit code 0 si todo OK, 1 si hay errores

**Salida**:
```
API Status
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ API                ┃ Required ┃ Status                         ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ The Odds API       │ YES      │ ✓ Connected (487 req remaining)│
│ API-Football       │ no       │ ✗ Not configured               │
│ Google Gemini      │ no       │ ✗ Not configured               │
└────────────────────┴──────────┴────────────────────────────────┘

✓ All required APIs are configured and working!
```

**Integración con CI/CD**:
```bash
# En pipeline de CI
if ! python scripts/check_apis.py; then
    echo "API validation failed"
    exit 1
fi
```

---

### 3. `scripts/health_check.py` - Diagnóstico del Sistema

**Propósito**: Revisa salud completa del sistema (DB, cache, circuit breaker).

**Uso**:
```bash
python scripts/health_check.py
```

**Funcionalidad**:
- ✅ Estado de base de datos SQLite
- ✅ Estadísticas de cache (hit rate, entries)
- ✅ Estado del circuit breaker
- ✅ Requests en últimas 24h
- ✅ Rate limits alcanzados
- ✅ API keys configuradas

**Salida**:
```
Database
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric           ┃ Value                   ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Status           │ ✓ Healthy               │
│ Size             │ 2.3 MB                  │
│ Requests (24h)   │ 127                     │
│ Successful (24h) │ 124                     │
│ Rate Limited     │ 3                       │
└──────────────────┴─────────────────────────┘

Circuit Breaker
┏━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric     ┃ Value   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━┩
│ Status     │ ✓ CLOSED│
│ Failures   │ 0       │
└────────────┴─────────┘

✓ All systems healthy!
```

---

### 4. `scripts/start.py` - Launcher Principal

**Propósito**: Punto de entrada único con pre-flight checks y menú.

**Uso**:
```bash
python scripts/start.py
```

**Funcionalidad**:
- ✅ Pre-flight checks automáticos
- ✅ Menú interactivo con opciones
- ✅ Lanza demos y utilidades
- ✅ Manejo de errores graceful

**Flujo**:
```
1. Pre-flight checks
   ├─ Verifica .env existe
   ├─ Verifica API keys
   ├─ Inicializa DB
   └─ Prueba conectividad

2. Si checks OK → Muestra menú
3. Usuario elige opción
4. Ejecuta script correspondiente
```

**Menú**:
```
Bet-Copilot Menu
┌──────────────────────────────────────┐
│ Select an option:                    │
│                                      │
│  1 - Run Market Watch Demo           │
│  2 - Run Soccer Prediction Demo      │
│  3 - Run API Usage Demo              │
│  4 - Health Check                    │
│  5 - Test API Connectivity           │
│  q - Quit                            │
└──────────────────────────────────────┘
```

---

## 🔑 Configuración de API Keys

### The Odds API (REQUERIDA)

**Obtener key**:
1. Visitar https://the-odds-api.com/
2. Crear cuenta gratuita
3. Copiar API key del dashboard

**Plan gratuito**:
- 500 requests/mes
- Actualización cada 5 minutos
- Suficiente para testing

**Configurar**:
```bash
python scripts/setup.py
# O manualmente:
echo "ODDS_API_KEY=your-key-here" >> .env
```

**Verificar**:
```bash
python scripts/check_apis.py
```

---

### API-Football (OPCIONAL)

**Obtener key**:
1. Visitar https://www.api-football.com/
2. Registrarse
3. Obtener key del dashboard

**Plan gratuito**:
- 100 requests/día
- Acceso a stats históricas

**Configurar**:
```bash
python scripts/setup.py
# O manualmente:
echo "API_FOOTBALL_KEY=your-key-here" >> .env
```

---

### Google Gemini (OPCIONAL)

**Obtener key**:
1. Visitar https://ai.google.dev/
2. Crear proyecto en Google Cloud
3. Habilitar Gemini API
4. Generar API key

**Plan gratuito**:
- 60 requests/minuto
- Perfecto para análisis contextual

**Configurar**:
```bash
python scripts/setup.py
# O manualmente:
echo "GEMINI_API_KEY=your-key-here" >> .env
```

---

## 📁 Estructura de Archivos

```
Bet-Copilot/
├── scripts/              # Scripts de deployment
│   ├── setup.py          # Configuración interactiva ⚡
│   ├── check_apis.py     # Validación de APIs ✓
│   ├── health_check.py   # Diagnóstico del sistema 🏥
│   └── start.py          # Launcher principal 🚀
├── .env                  # Configuración (generado)
├── .env.example          # Template de configuración
├── bet_copilot.db        # Base de datos (generado)
└── requirements.txt      # Dependencias Python
```

---

## 🐳 Deployment con Docker (Futuro)

```dockerfile
# Dockerfile (pendiente de crear)
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Pre-flight checks on startup
CMD ["python", "scripts/start.py"]
```

```yaml
# docker-compose.yml (pendiente de crear)
version: '3.8'
services:
  bet-copilot:
    build: .
    environment:
      - ODDS_API_KEY=${ODDS_API_KEY}
      - API_FOOTBALL_KEY=${API_FOOTBALL_KEY}
    volumes:
      - ./bet_copilot.db:/app/bet_copilot.db
```

---

## 🔄 Workflow de Deployment

### Desarrollo Local
```bash
# 1. Setup inicial
python scripts/setup.py

# 2. Verificar todo OK
python scripts/check_apis.py
python scripts/health_check.py

# 3. Desarrollo
python example_usage.py

# 4. Antes de commit
pytest bet_copilot/tests/ -v
```

### Servidor/Producción
```bash
# 1. Clonar repo
git clone <repo-url>
cd Bet-Copilot

# 2. Variables de entorno
export ODDS_API_KEY="..."
export API_FOOTBALL_KEY="..."

# 3. Instalar
pip install -r requirements.txt

# 4. Verificar
python scripts/check_apis.py

# 5. Ejecutar
python scripts/start.py
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml (ejemplo)
name: Deploy
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest bet_copilot/tests/
      
      # Pre-deployment checks
      - run: python scripts/check_apis.py
        env:
          ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}
```

---

## 🚨 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Verificar instalación
pip list | grep aiohttp

# Reinstalar
pip install -r requirements.txt --force-reinstall
```

### Error: "ODDS_API_KEY not configured"
```bash
# Opción 1: Usar setup
python scripts/setup.py

# Opción 2: Manual
cp .env.example .env
# Editar .env y agregar keys
```

### Error: "Circuit breaker is open"
```bash
# Verificar estado
python scripts/health_check.py

# Ver logs de rate limits
sqlite3 bet_copilot.db "SELECT * FROM api_requests WHERE status_code = 429;"

# Esperar 60 segundos o resetear manualmente
```

### Error: "Database locked"
```bash
# Cerrar todas las conexiones
pkill -f "python.*bet_copilot"

# Eliminar DB y reiniciar
rm bet_copilot.db
python scripts/start.py
```

---

## 📊 Monitoreo

### Logs de Sistema
```bash
# Ver últimos requests
sqlite3 bet_copilot.db "SELECT * FROM api_requests ORDER BY timestamp DESC LIMIT 10;"

# Ver rate limits
sqlite3 bet_copilot.db "SELECT COUNT(*) as hits FROM api_requests WHERE status_code = 429;"

# Ver estado del circuit breaker
sqlite3 bet_copilot.db "SELECT * FROM circuit_breaker_events ORDER BY timestamp DESC LIMIT 5;"
```

### Métricas
```bash
# Health check completo
python scripts/health_check.py

# Solo APIs
python scripts/check_apis.py
```

---

## 🔐 Seguridad

### API Keys
```bash
# NUNCA commitear .env
echo ".env" >> .gitignore

# Usar variables de entorno en producción
export ODDS_API_KEY="..."

# Rotar keys periódicamente
# (Cada 3 meses recomendado)
```

### Permisos
```bash
# Restringir acceso a .env
chmod 600 .env

# Restringir scripts
chmod 700 scripts/*.py
```

---

## 📝 Checklist de Deployment

### Primera Instalación
- [ ] Python 3.10+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] API keys obtenidas (mínimo The Odds API)
- [ ] Configuración completada (`python scripts/setup.py`)
- [ ] APIs verificadas (`python scripts/check_apis.py`)
- [ ] Health check OK (`python scripts/health_check.py`)
- [ ] Demo ejecutado exitosamente

### Pre-Producción
- [ ] Tests passing (`pytest bet_copilot/tests/ -v`)
- [ ] API keys de producción configuradas
- [ ] Base de datos inicializada
- [ ] Logs configurados
- [ ] Backup strategy definida
- [ ] Monitoreo configurado

### Post-Deployment
- [ ] Health check en producción
- [ ] Verificar rate limits disponibles
- [ ] Test de conectividad
- [ ] Revisar logs de errores
- [ ] Documentar issues encontrados

---

## 🆘 Soporte

### Documentación
- **Setup rápido**: [QUICK_START.md](QUICK_START.md)
- **Guía técnica**: [AGENTS.md](AGENTS.md)
- **Estado del proyecto**: [PROJECT_STATUS.md](PROJECT_STATUS.md)

### Scripts de Ayuda
```bash
# Diagnóstico completo
python scripts/health_check.py

# Reconfigurar
python scripts/setup.py

# Verificar APIs
python scripts/check_apis.py
```

---

**Última actualización**: 2026-01-04  
**Versión**: 1.0  
**Proyecto**: Bet-Copilot
