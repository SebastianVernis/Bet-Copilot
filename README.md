# ⚽ Bet-Copilot

**Sistema de Análisis Especulativo Deportivo con CLI/TUI**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-90%20passing-brightgreen.svg)](./docs/development/README_TESTS.md)
[![Coverage](https://img.shields.io/badge/coverage-56%25-yellow.svg)](./docs/development/COVERAGE_REPORT.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

> 🎯 **"Copiloto, no bot"** - El sistema informa con matemáticas transparentes, **tú decides**.

---

## 🚀 Quick Start

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Bet-Copilot

# 2. Instalar dependencias
./scripts/INSTALL_DEPS.sh

# 3. Configurar API keys (opcional)
cp .env.example .env
nano .env  # Agregar tus API keys

# 4. Verificar instalación
python scripts/verify_apis.py

# 5. ¡Ejecutar!
python main.py
```

**Demo sin instalación**:
```bash
python examples/DEMO.py
```

---

## ✨ Características Principales

### 🎹 **Input Avanzado**
- **Historial navegable** con ↑/↓
- **Autocompletado inteligente** con Tab (comandos + argumentos)
- **Búsqueda incremental** con Ctrl+R
- **Edición inline** completa (←/→, Ctrl+A/E/K/U)

### 🤖 **AI Multi-Nivel con Fallback**
```
Nivel 1: Gemini (Google)          → Alta calidad ⭐⭐⭐⭐⭐
Nivel 2: Blackbox (Blackbox.ai)   → Buena calidad ⭐⭐⭐⭐
Nivel 3: SimpleAnalyzer (Local)   → Garantizado ⭐⭐⭐
```

**Garantía**: El sistema **NUNCA falla** - SimpleAnalyzer asegura análisis siempre.

### ⚽ **Football Data con Fallback**
```
Primary: API-Football     → Datos oficiales ⭐⭐⭐⭐⭐
Fallback: SimpleProvider  → Estimaciones ⭐⭐⭐
```

**30 equipos pre-configurados** en 3 tiers para estimaciones precisas.

### 🎲 **Motor Matemático**
- **Distribución de Poisson** para probabilidades de goles
- **Kelly Criterion** para sizing óptimo de apuestas
- **Expected Value (EV)** calculation
- **Home advantage** factor

### 📊 **Análisis Completo**
- Stats de equipos (forma, goles, defensa)
- Historial H2H (últimos 10 partidos)
- Detección de lesiones/suspensiones
- Predicción Poisson con xG real
- Análisis contextual con AI
- Recomendaciones Kelly

---

## 📋 Comandos Disponibles

```bash
➜ bet-copilot dashboard          # Dashboard 4 zonas en vivo
➜ bet-copilot mercados           # Obtener mercados de apuestas
➜ bet-copilot analizar [partido] # Analizar partido específico
➜ bet-copilot salud              # Verificar estado de APIs
➜ bet-copilot ayuda              # Mostrar ayuda
```

### Atajos de Teclado

```
↑/↓         Navegar historial de comandos
Tab         Autocompletar comandos y argumentos
Ctrl+R      Búsqueda incremental en historial
←/→         Mover cursor en la línea
Ctrl+A/E    Ir a inicio/fin de línea
```

---

## 🛠️ Stack Tecnológico

```
Lenguaje:     Python 3.10+
UI:           Rich, Textual, prompt_toolkit
Database:     SQLite (aiosqlite)
Async:        asyncio, aiohttp
APIs:         The Odds API, API-Football, Gemini, Blackbox
Testing:      pytest, pytest-asyncio, pytest-cov
```

---

## 📦 Instalación

### Opción 1: Script Automático (Recomendado)
```bash
./scripts/INSTALL_DEPS.sh
```

### Opción 2: Manual
```bash
# Con virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Opción 3: Desarrollo
```bash
pip install -r requirements-dev.txt
```

### Verificar Instalación
```bash
python scripts/check_deps.py
```

---

## ⚙️ Configuración

### API Keys

**Copiar template**:
```bash
cp .env.example .env
```

**Editar `.env`**:
```bash
# CRÍTICA (requerida para odds)
ODDS_API_KEY="tu_key_aqui"

# IMPORTANTE (recomendada para stats reales)
API_FOOTBALL_KEY="tu_key_aqui"

# OPCIONAL (mejora análisis AI)
GEMINI_API_KEY="tu_key_aqui"
BLACKBOX_API_KEY="tu_key_aqui"
```

### Obtener API Keys

| API | URL | Prioridad |
|-----|-----|-----------|
| **The Odds API** | https://the-odds-api.com/ | 🔴 Crítica |
| **API-Football** | https://www.api-football.com/ | 🟡 Importante |
| **Gemini** | https://makersuite.google.com/app/apikey | 🟢 Opcional |
| **Blackbox** | https://app.blackbox.ai/dashboard | 🟢 Opcional |

**Verificar configuración**:
```bash
python scripts/verify_apis.py
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Script con menú interactivo
./scripts/run_tests.sh

# O directamente con pytest
pytest bet_copilot/tests/ -v

# Con coverage
pytest --cov=bet_copilot --cov-report=html bet_copilot/tests/
```

### Stats
- **90 tests** totales
- **~87 passing** (97%)
- **56% coverage** (75% sin UI)
- **6.5s** ejecución completa

Ver [README_TESTS.md](docs/development/README_TESTS.md) para más detalles.

---

## 📚 Documentación

### Guías de Usuario
- [**Configuración AI**](docs/guides/CONFIGURACION_AI.md) - Setup de AI providers
- [**Dependencias**](docs/guides/DEPENDENCIAS.md) - Gestión de dependencias
- [**Guía Rápida (ES)**](docs/GUIA_RAPIDA.md) - Quick start en español
- [**Quick Start (EN)**](docs/QUICK_START.md) - Quick start en inglés

### Documentación Técnica
- [**AGENTS.md**](AGENTS.md) - Guía para agentes IA (Cursor, Copilot)
- [**AI Fallback**](docs/api/AI_FALLBACK.md) - Sistema de fallback AI
- [**Football Fallback**](docs/api/FOOTBALL_FALLBACK.md) - Sistema de fallback Football
- [**Blackbox Integration**](docs/api/BLACKBOX_INTEGRATION.md) - Integración Blackbox API

### Para Desarrolladores
- [**Testing**](docs/development/README_TESTS.md) - Guía de testing
- [**Coverage**](docs/development/COVERAGE_REPORT.md) - Análisis de coverage
- [**Command Input**](docs/README_COMMAND_INPUT.md) - Sistema de input avanzado

Ver [**Índice Completo**](INDICE_DOCUMENTACION.md)

---

## 🎯 Modos de Operación

### Modo 1: Full API (Producción)
✅ Todas las API keys configuradas
- Odds reales
- Stats reales de equipos  
- AI avanzada (Gemini)
- Máxima calidad

### Modo 2: Essentials
✅ ODDS_API_KEY + API_FOOTBALL_KEY
- Odds reales
- Stats reales
- AI básica (SimpleAnalyzer)
- Buena calidad

### Modo 3: Desarrollo/Demo
✅ Solo ODDS_API_KEY (o ninguna)
- Odds reales (si key)
- Stats estimadas (SimpleProvider)
- AI heurística (SimpleAnalyzer)
- Funcional para desarrollo

---

## 💡 Ejemplos

```bash
➜ bet-copilot mercados soccer_epl
✓ 15 eventos cargados

➜ bet-copilot analizar Arsenal vs Chelsea

📊 Estadísticas: 3.40 - 2.85 goles promedio
🎲 Predicción: 38.5% - 28.2% - 33.3%
💰 Mejor Apuesta: Victoria Visitante @ 2.85 (EV: +8.5%)
```

Ver más en [examples/](examples/)

---

## ⚠️ Disclaimer

**Este software es una herramienta de soporte a decisiones, NO asesoría financiera.**

- Responsabilidad 100% del usuario
- Predicciones probabilísticas, no garantías
- Riesgo de pérdida siempre presente
- Usar solo capital disponible

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## 🔗 Links

- [Documentación Completa](INDICE_DOCUMENTACION.md)
- [Changelog](CHANGELOG.md)
- [Testing](docs/development/README_TESTS.md)
- [Contributing](CONTRIBUTING.md)

---

**Versión**: 0.5.2  
**Status**: ✅ Production Ready  
**Actualizado**: 2026-01-04
