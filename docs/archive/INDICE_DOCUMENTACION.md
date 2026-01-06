# 📚 Índice de Documentación - Bet-Copilot

Guía completa de toda la documentación disponible del proyecto.

---

## 🚀 Inicio Rápido

### Para Usuarios Nuevos
1. **[README.md](README.md)** - Inicio del proyecto
2. **[Dependencias](docs/guides/DEPENDENCIAS.md)** - Instalación
3. **[Configuración AI](docs/guides/CONFIGURACION_AI.md)** - Setup de API keys
4. **[Guía Rápida](docs/GUIA_RAPIDA.md)** - Quick start

### Para Desarrolladores
1. **[AGENTS.md](AGENTS.md)** - Guía para agentes IA
2. **[Testing](docs/development/README_TESTS.md)** - Sistema de testing
3. **[AI Fallback](docs/api/AI_FALLBACK.md)** - Arquitectura de IA
4. **[Contributing](CONTRIBUTING.md)** - Cómo contribuir

---

## 📖 Documentación por Categoría

### 🔧 Instalación y Setup

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| [**Dependencias**](docs/guides/DEPENDENCIAS.md) | Gestión de dependencias, troubleshooting | Usuarios/Devs |
| [**Configuración AI**](docs/guides/CONFIGURACION_AI.md) | Setup de Gemini/Blackbox/SimpleAnalyzer | Usuarios |
| [**scripts/INSTALL_DEPS.sh**](scripts/INSTALL_DEPS.sh) | Script automático de instalación | Usuarios |
| [**scripts/check_deps.py**](scripts/check_deps.py) | Verificador visual de dependencias | Usuarios/Devs |
| [**scripts/verify_apis.py**](scripts/verify_apis.py) | Verificador de API keys | Usuarios/Devs |

---

### 🤖 Sistema de IA

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| [**AI Fallback**](docs/api/AI_FALLBACK.md) | Arquitectura del sistema de fallback (3 niveles) | Devs |
| [**Blackbox Integration**](docs/api/BLACKBOX_INTEGRATION.md) | Integración verificada con Blackbox API | Devs |
| [**Football Fallback**](docs/api/FOOTBALL_FALLBACK.md) | Sistema de fallback para Football data | Devs |
| [**examples/test_ai_fallback.py**](examples/test_ai_fallback.py) | Test interactivo de fallback | Devs |

**Archivos de código**:
- `bet_copilot/ai/gemini_client.py`
- `bet_copilot/ai/blackbox_client.py`
- `bet_copilot/ai/simple_analyzer.py`
- `bet_copilot/ai/ai_client.py`

---

### 🧪 Testing

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| [**README_TESTS.md**](docs/development/README_TESTS.md) | Guía general de testing | Devs |
| [**COVERAGE_REPORT.md**](docs/development/COVERAGE_REPORT.md) | Análisis de coverage detallado | Devs |
| [**scripts/run_tests.sh**](scripts/run_tests.sh) | Script unificado con menú interactivo | Devs |
| [**MIGRACION_TESTS.md**](docs/development/MIGRACION_TESTS.md) | Documentación de migración de tests | Devs |

**Tests disponibles** (90):
- `bet_copilot/tests/` - Todos los tests unitarios
- 66+ passing, 56% coverage

---

### 🎹 Sistema de Input Avanzado

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| [**README_COMMAND_INPUT.md**](docs/README_COMMAND_INPUT.md) | Sistema de input con historial y autocompletado | Usuarios/Devs |
| [**TESTING_GUIDE.md**](docs/TESTING_GUIDE.md) | Testing del autocompletado | Devs |

**Tests interactivos**:
- `bet_copilot/tests/test_command_input.py`
- `bet_copilot/tests/test_autocompletion.py`
- `bet_copilot/tests/test_completion_debug.py`
- `bet_copilot/tests/test_completion_interactive.py`

---

### 📋 Changelogs y Resúmenes

| Archivo | Descripción | Versión |
|---------|-------------|---------|
| [**CHANGELOG.md**](CHANGELOG.md) | Changelog completo del proyecto | Todas |
| [**docs/CHANGELOG.md**](docs/CHANGELOG.md) | Changelog histórico detallado | v0.1-v0.5 |
| [**Resumen v0.5.0**](docs/RESUMEN_FINAL_v0.5.0.md) | Sistema de input | v0.5.0 |
| [**Resumen v0.5.1**](docs/RESUMEN_EJECUTIVO_v0.5.1.md) | Sistema AI fallback | v0.5.1 |
| [**Estado Final**](docs/ESTADO_FINAL.md) | Estado completo del proyecto | v0.5.2 |

---

### 🎓 Guías y Tutoriales

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| [**AGENTS.md**](AGENTS.md) | Guía para agentes IA (Cursor, Copilot, Claude) | IA Agents |
| [**Guía Rápida (ES)**](docs/GUIA_RAPIDA.md) | Quick start en español | Usuarios |
| [**Quick Start (EN)**](docs/QUICK_START.md) | Quick start en inglés | Usuarios |
| [**Deployment**](docs/DEPLOYMENT.md) | Deploy en producción | DevOps |
| [**Installation**](docs/INSTALLATION.md) | Instalación detallada | Usuarios |
| [**CONTRIBUTING.md**](CONTRIBUTING.md) | Guía de contribución | Contributors |

---

### 💻 Ejemplos de Código

| Archivo | Descripción | Tipo |
|---------|-------------|------|
| [**examples/DEMO.py**](examples/DEMO.py) | Demo principal del sistema | Showcase |
| [**examples/example_usage.py**](examples/example_usage.py) | Ejemplo básico de uso | Tutorial |
| [**examples/example_soccer_prediction.py**](examples/example_soccer_prediction.py) | Demo de Poisson | Math |
| [**examples/example_enhanced_analysis.py**](examples/example_enhanced_analysis.py) | Análisis completo | Advanced |
| [**examples/test_ai_fallback.py**](examples/test_ai_fallback.py) | Demo de fallback AI | Testing |

---

### 📊 Estado del Proyecto

| Archivo | Descripción | Actualización |
|---------|-------------|---------------|
| [**docs/PROJECT_STATUS.md**](docs/PROJECT_STATUS.md) | Estado general y roadmap | v0.4.0 |
| [**docs/PROJECT_SUMMARY.md**](docs/PROJECT_SUMMARY.md) | Resumen ejecutivo | v0.4.0 |
| [**docs/ESTADO_FINAL.md**](docs/ESTADO_FINAL.md) | Estado final v0.5.2 | v0.5.2 |

---

## 🗺️ Mapa de Navegación

### Quiero...

#### Instalar el proyecto
1. [Dependencias](docs/guides/DEPENDENCIAS.md)
2. [scripts/INSTALL_DEPS.sh](scripts/INSTALL_DEPS.sh)
3. [scripts/check_deps.py](scripts/check_deps.py)

#### Configurar APIs
1. [Configuración AI](docs/guides/CONFIGURACION_AI.md)
2. [.env.example](.env.example)
3. [scripts/verify_apis.py](scripts/verify_apis.py)

#### Ejecutar tests
1. [README Tests](docs/development/README_TESTS.md)
2. [scripts/run_tests.sh](scripts/run_tests.sh)
3. [Coverage Report](docs/development/COVERAGE_REPORT.md)

#### Entender IA/Fallback
1. [AI Fallback](docs/api/AI_FALLBACK.md)
2. [Blackbox Integration](docs/api/BLACKBOX_INTEGRATION.md)
3. [Football Fallback](docs/api/FOOTBALL_FALLBACK.md)

#### Ver ejemplos
1. [examples/DEMO.py](examples/DEMO.py)
2. [examples/](examples/)

#### Contribuir
1. [CONTRIBUTING.md](CONTRIBUTING.md)
2. [AGENTS.md](AGENTS.md)
3. [docs/development/](docs/development/)

#### Ver changelog
1. [CHANGELOG.md](CHANGELOG.md)
2. [docs/CHANGELOG.md](docs/CHANGELOG.md)
3. [docs/RESUMEN_EJECUTIVO_v0.5.1.md](docs/RESUMEN_EJECUTIVO_v0.5.1.md)

---

## 📂 Estructura Completa

```
/Bet-Copilot/
│
├── 📄 Archivos Esenciales (Raíz)
│   ├── README.md                       Principal
│   ├── CONTRIBUTING.md                 Contribuir
│   ├── LICENSE                         MIT License
│   ├── CHANGELOG.md                    Changelog
│   ├── AGENTS.md                       AI agents
│   └── INDICE_DOCUMENTACION.md         Este archivo
│
├── 📁 .github/                         GitHub configs
│   └── workflows/tests.yml             CI/CD
│
├── 📁 docs/                            Documentación
│   ├── api/                            APIs (3 archivos)
│   ├── guides/                         Guías (2 archivos)
│   ├── development/                    Devs (3 archivos)
│   └── *.md                            Otros (~10 archivos)
│
├── 📁 scripts/                         Scripts
│   ├── INSTALL_DEPS.sh
│   ├── run_tests.sh
│   ├── check_deps.py
│   ├── verify_apis.py
│   └── START.sh
│
├── 📁 examples/                        Ejemplos
│   ├── DEMO.py
│   ├── example_*.py
│   └── test_ai_fallback.py
│
└── 📁 bet_copilot/                     Código
    ├── ai/                             AI (4 archivos)
    ├── api/                            APIs (7 archivos)
    ├── tests/                          Tests (12 archivos)
    └── ...
```

---

## 🎯 Guía por Rol

### 👤 Usuario Final
```
1. README.md
2. docs/guides/DEPENDENCIAS.md
3. docs/guides/CONFIGURACION_AI.md
4. docs/GUIA_RAPIDA.md
5. examples/DEMO.py
```

### 👨‍💻 Desarrollador
```
1. AGENTS.md
2. docs/api/AI_FALLBACK.md
3. docs/development/README_TESTS.md
4. CONTRIBUTING.md
5. bet_copilot/tests/
```

### 🤖 Agente IA
```
1. AGENTS.md
2. INDICE_DOCUMENTACION.md
3. bet_copilot/
```

### 📊 Product Manager
```
1. docs/ESTADO_FINAL.md
2. docs/PROJECT_STATUS.md
3. CHANGELOG.md
```

---

## 📊 Estadísticas

```
Total archivos MD:        32
Líneas documentación:     ~15,000
Directorios docs:         3 (api, guides, development)
Scripts:                  5
Ejemplos:                 8+
Versiones documentadas:   0.1 - 0.5.2
Idiomas:                  ES + EN
Última actualización:     2026-01-04
```

---

## 🔗 Links Externos

### APIs
- [The Odds API](https://the-odds-api.com/)
- [API-Football](https://www.api-football.com/)
- [Google Gemini](https://makersuite.google.com/app/apikey)
- [Blackbox AI](https://app.blackbox.ai/dashboard)

### Librerías
- [Rich](https://rich.readthedocs.io/)
- [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/)
- [pytest](https://docs.pytest.org/)
- [aiohttp](https://docs.aiohttp.org/)

---

**Mantenido por**: Bet-Copilot Team  
**Última actualización**: 2026-01-04  
**Versión actual**: 0.5.2  
**Estructura**: ✅ Organizada para GitHub
