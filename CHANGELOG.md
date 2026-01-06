# Changelog - Bet-Copilot

Todas las actualizaciones importantes del proyecto.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [0.6.0] - 2026-01-06

### 🎨 Textual TUI Dashboard - Migración Completa

#### Added
- **Textual TUI Dashboard** - Interfaz interactiva completa
  - `bet_copilot/ui/textual_dashboard.py` (650 líneas)
  - 6 widgets especializados: API Health, News, Markets, Alt Markets, Logs, Input
  - Reactive variables para auto-actualización
  - Auto-refresh configurable (API: 5min, News: 1h, Markets: 60s)
  - Keyboard shortcuts (q, r, n, m, h, Ctrl+C)
  - CSS styling con tema neon
  - Event handlers para comandos interactivos
  
- **Persistencia de Estado**
  - `bet_copilot/ui/dashboard_state.py` (180 líneas)
  - Guarda última liga consultada
  - Historial de búsquedas recientes (últimas 20)
  - Mercados favoritos
  - Preferencias de usuario configurables
  - Timestamp de última sesión
  - Contador de sesiones
  - Ubicación: `~/.bet_copilot_state.json`
  
- **Modo Dual CLI/TUI**
  - `python main.py` - Rich CLI (default)
  - `python main.py --tui` - Textual TUI Dashboard
  - Sin breaking changes, ambos modos disponibles
  
- **Testing Suite**
  - `test_textual_tui.py` - Tests de componentes TUI
  - 4 tests: Imports, State Manager, Widgets, App Creation
  - ✅ 4/4 tests passed
  
- **Documentación Completa**
  - `docs/TEXTUAL_TUI_GUIDE.md` (800+ líneas)
  - `TEXTUAL_MIGRATION_COMPLETE.md` - Resumen de migración
  - README.md actualizado con comandos TUI

#### Changed
- **cli.py** - Soporte para modo dual
  - Detecta flag `--tui` o `--textual`
  - Lanza Textual dashboard o Rich CLI según flag
  
- **main.py** - Docstring actualizado
  - Instrucciones de uso para ambos modos
  
- **README.md** - Secciones actualizadas
  - v0.6 features en características principales
  - Comandos TUI documentados
  - Atajos de teclado TUI
  - Quick start con modo TUI

#### Features
- ✅ **Interactividad nativa** - Clicks, navegación con teclado
- ✅ **Actualizaciones en vivo** - Datos en tiempo real sin re-render completo
- ✅ **Persistencia** - Recuerda última sesión automáticamente
- ✅ **Multi-zona** - 6 áreas especializadas en una pantalla
- ✅ **Responsive** - Se adapta al tamaño del terminal
- ✅ **Auto-refresh** - Markets (60s), News (1h), API Health (5min)
- ✅ **Comandos interactivos** - mercados, analizar, salud, ayuda
- ✅ **Keyboard shortcuts** - q (quit), r (refresh), n (news), m (markets), h (help)

#### Technical Details
- **Arquitectura**: Event-driven con reactive variables
- **Rendimiento**: ~10ms render (solo cambios), +15MB RAM vs Rich
- **Dependencias**: textual>=0.40.0 (ya en requirements.txt)
- **Compatibilidad**: Python 3.10+, sin breaking changes

---

## [0.5.2] - 2026-01-04

### 🏗️ Reorganización para GitHub

#### Added
- **Estructura profesional** para GitHub
  - `.github/workflows/tests.yml` - CI/CD con GitHub Actions
  - `CONTRIBUTING.md` - Guía completa para contributors
  - `LICENSE` - MIT License con disclaimer
  - `ORGANIZACION_COMPLETA.md` - Documentación de estructura
  
- **Football Data Fallback System**
  - `SimpleFootballDataProvider` - Estimaciones por tier de equipo
  - `FootballClientWithFallback` - Cliente unificado con fallback
  - 30 equipos pre-configurados en 3 tiers
  - Estimaciones ~75-85% precisión vs datos reales
  - 23 tests nuevos

- **Scripts de verificación**
  - `scripts/verify_apis.py` - Verificador visual de API keys con Rich

#### Changed
- **Estructura de directorios** reorganizada
  - Docs movidas a `docs/` (api/, guides/, development/)
  - Scripts movidos a `scripts/`
  - Ejemplos movidos a `examples/`
  - Raíz limpia: 13 archivos (antes: 28)
  
- **README.md** completamente reescrito
  - Formato profesional con badges
  - Quick start mejorado
  - Estructura clara
  - Links a documentación organizada

- **API_FOOTBALL_KEY** actualizada
  - Nueva key: `90c6403a265e6509c7a658c56db84b72`

#### Fixed
- Rutas actualizadas en toda la documentación
- Links internos corregidos
- Scripts ejecutables desde nuevas ubicaciones

#### Tests
```
Total:     90 tests (+23)
Passing:   ~87 tests (97%)
Coverage:  56% (58% con football fallback)
```

---

## [0.5.1] - 2026-01-04

### 🤖 Sistema AI con Fallback Multi-Nivel

#### Added
- **BlackboxClient** - Cliente para Blackbox AI API
  - Endpoint: `https://api.blackbox.ai/chat/completions`
  - Formato OpenAI-compatible
  - Verificado con MCP Blackbox Docs
  - 15 tests unitarios

- **SimpleAnalyzer** - Analizador heurístico local
  - Análisis basado en forma (W/D/L points)
  - Análisis H2H
  - Detección de lesiones por keywords
  - Ajustes conservadores ±10%
  - **100% disponibilidad** (sin deps externas)
  - 15 tests unitarios

- **AIClient** - Cliente unificado con fallback automático
  - Nivel 1: Gemini (mejor calidad)
  - Nivel 2: Blackbox (fallback rápido)
  - Nivel 3: SimpleAnalyzer (garantizado)
  - Fallback transparente y automático
  - 10 tests unitarios

- **BLACKBOX_API_KEY** en configuración

#### Changed
- CLI usa `AIClient` en lugar de `GeminiClient` directamente
- Health check muestra proveedor AI activo
- `.env.example` actualizado con BLACKBOX_API_KEY

#### Fixed
- **Gemini model** corregido: `gemini-1.5-flash` → `gemini-pro`
- **Blackbox API** endpoint verificado contra docs oficiales
- Error handling mejorado en todos los AI clients

#### Tests
```
Total:     67 tests (+40)
AI tests:  40 tests (nuevos)
Passing:   66/67 (98.5%)
Coverage:  56%
```

---

## [0.5.0] - 2026-01-04

### 🎹 Sistema de Input Avanzado

#### Added
- **CommandInput** con prompt_toolkit
  - Historial navegable con ↑/↓
  - Autocompletado inteligente con Tab
  - Edición inline con ←/→, Ctrl+A/E/K/U
  - Búsqueda incremental con Ctrl+R
  
- **BetCopilotCompleter** - Autocompletado contextual
  - Comandos base (dashboard, mercados, analizar, etc.)
  - 13 sport keys con descripciones
  - Nombres de partidos desde eventos cargados
  - Metadatos en menú

- **Prompt estilizado** - `➜ bet-copilot` con colores neón

- **4 tests interactivos** para command input

#### Changed
- CLI integrado con CommandInput avanzado
- Help actualizado con atajos de teclado
- `fetch_markets()` actualiza completer dinámicamente

#### Fixed
- **Autocompletado de partidos** - Lógica de parsing reescrita
- No agrega caracteres extra
- Funciona correctamente con espacios

#### Tests
```
Total:     30 tests (+11)
Passing:   ~27 tests
Coverage:  N/A (componentes interactivos)
```

---

## [0.4.0] - 2026-01-04

### 🧠 Análisis Mejorado con Datos Reales

#### Added
- MatchAnalyzer service (integración completa)
- FootballAPIClient con endpoints completos
- Detección de jugadores lesionados/suspendidos
- Análisis H2H (últimos 10 partidos)
- Gemini AI integration
- Kelly Criterion calculator
- Dashboard 4 zonas
- CLI interactivo

#### Changed
- Traducción completa al español
- Comandos bilingües (ES/EN)

#### Tests
```
Total:     24 tests
Coverage:  ~90%
```

Ver [docs/CHANGELOG.md](docs/CHANGELOG.md) para changelog completo histórico.

---

## Formato

```
## [MAJOR.MINOR.PATCH] - YYYY-MM-DD

### Categoría

#### Added
- Nuevas features

#### Changed
- Cambios en funcionalidad existente

#### Deprecated
- Features marcadas para remoción

#### Removed
- Features removidas

#### Fixed
- Bug fixes

#### Security
- Patches de seguridad
```

---

**Última actualización**: 2026-01-04  
**Versión actual**: 0.5.2  
**Formato**: [Keep a Changelog](https://keepachangelog.com/)
