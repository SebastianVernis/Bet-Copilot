# 🌳 Plan de Branches de Desarrollo - Bet-Copilot v0.7

**Fecha**: 2026-01-06  
**Base**: master (v0.6.0)  
**Objetivo**: Despliegue alpha con web terminal

---

## 🎯 Nuevas Branches a Crear

### 1. laptop/feature/web-terminal-shellinabox
**Propósito**: Implementar web terminal para acceso remoto a la CLI

**Stack Técnico**:
- **Shellinabox** / **ttyd** / **wetty** (alternativas)
- **Docker** para containerización
- **Nginx** como reverse proxy
- **SSL/TLS** para seguridad

**Funcionalidades**:
```
✅ Servidor web terminal
✅ Acceso por navegador (HTTP/HTTPS)
✅ Autenticación básica
✅ Sesiones aisladas por usuario
✅ Logs de acceso
✅ Rate limiting
```

**Archivos a Crear**:
```
bet_copilot/
├── web/
│   ├── __init__.py
│   ├── terminal_server.py       # Servidor web terminal
│   ├── auth.py                  # Autenticación
│   └── config.py                # Configuración web

docker/
├── Dockerfile.shellinabox        # Imagen con shellinabox
├── Dockerfile.ttyd               # Alternativa con ttyd
├── docker-compose.yml            # Orquestación
└── nginx.conf                    # Reverse proxy config

scripts/
├── start_web_terminal.sh         # Launcher
└── deploy_alpha.sh               # Deploy script

docs/
└── web_terminal/
    ├── SETUP.md                  # Guía de instalación
    ├── SECURITY.md               # Consideraciones de seguridad
    └── ARCHITECTURE.md           # Arquitectura del sistema
```

**Deliverables**:
- [ ] Shellinabox/ttyd funcionando
- [ ] Docker container configurado
- [ ] Nginx reverse proxy
- [ ] Autenticación implementada
- [ ] SSL/TLS configurado
- [ ] Documentación completa
- [ ] Scripts de deploy

---

### 2. laptop/feature/textual-migration-complete
**Propósito**: Migración completa de Rich UI a Textual TUI

**Contexto**: Ya existe `textual_app.py` (502 líneas), pero no está integrado

**Trabajo a Realizar**:
```
✅ Refactorizar dashboard existente
✅ Migrar todas las vistas a Textual
✅ Implementar navegación por teclado
✅ Añadir widgets interactivos
✅ Testing de UI
✅ Integración con CLI principal
```

**Archivos a Modificar/Crear**:
```
bet_copilot/ui/
├── textual_app.py               # Existente - mejorar
├── widgets/
│   ├── __init__.py
│   ├── odds_table.py            # Widget tabla de cuotas
│   ├── match_card.py            # Widget tarjeta partido
│   ├── market_watch.py          # Widget mercados
│   ├── api_status.py            # Widget estado APIs
│   └── logs_panel.py            # Widget logs
├── screens/
│   ├── __init__.py
│   ├── dashboard.py             # Dashboard principal
│   ├── match_analysis.py        # Análisis de partido
│   ├── markets.py               # Mercados alternativos
│   └── settings.py              # Configuración
└── styles/
    ├── __init__.py
    └── theme.tcss                # Textual CSS

bet_copilot/cli.py                # Integrar Textual mode
main.py                           # Añadir flag --tui

tests/
└── ui/
    ├── test_textual_widgets.py
    └── test_textual_navigation.py

docs/ui/
├── TEXTUAL_GUIDE.md             # Guía de uso
└── WIDGET_API.md                # API de widgets
```

**Deliverables**:
- [ ] Textual TUI completo
- [ ] Todos los widgets implementados
- [ ] Navegación por teclado funcional
- [ ] Tests de UI
- [ ] Integración con CLI
- [ ] Documentación de uso
- [ ] Screenshots/GIFs

---

## 📋 Workflow de Desarrollo

### Fase 1: Crear Branches
```bash
# Branch 1: Web Terminal
git checkout master
git pull origin master
git checkout -b laptop/feature/web-terminal-shellinabox

# Branch 2: Textual Migration
git checkout master
git checkout -b laptop/feature/textual-migration-complete
```

### Fase 2: Desarrollo Paralelo
```bash
# En branch web-terminal
- Investigar shellinabox vs ttyd vs wetty
- Implementar servidor básico
- Añadir autenticación
- Dockerizar
- Configurar Nginx
- Testing de despliegue

# En branch textual-migration
- Refactorizar textual_app.py
- Crear widgets modulares
- Implementar navegación
- Integrar con CLI
- Tests UI
- Documentar
```

### Fase 3: Integration Branch
```bash
# Una vez ambas branches estén listas
git checkout -b laptop/feature/alpha-deployment

# Merge ambas features
git merge laptop/feature/web-terminal-shellinabox
git merge laptop/feature/textual-migration-complete

# Resolver conflictos (si existen)
# Testing de integración completo
```

### Fase 4: Deploy Alpha
```bash
# Push a development (staging)
git checkout development
git merge laptop/feature/alpha-deployment

# Deploy en servidor alpha
./scripts/deploy_alpha.sh

# Pruebas alpha con usuarios
# Recoger feedback
```

---

## 🔧 Consideraciones Técnicas

### Web Terminal (Shellinabox)

**Ventajas Shellinabox**:
- Simple de configurar
- Soporte HTTPS nativo
- Autenticación PAM
- Ligero (< 10MB)

**Alternativas**:
| Tool | Pros | Cons |
|------|------|------|
| **ttyd** | Moderno, WebSocket, rápido | Requiere más config |
| **wetty** | Node.js, fácil integrar | Dependencia pesada |
| **gotty** | Go, super ligero | Menos features |

**Recomendación**: Empezar con **ttyd** (moderno) o **shellinabox** (estable)

### Textual Migration

**Estructura Recomendada**:
```python
# Main TUI App
class BetCopilotTUI(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("m", "switch_markets", "Markets"),
        ("a", "switch_analysis", "Analysis"),
    ]
    
    def compose(self):
        yield Header()
        yield Container(
            APIStatusWidget(),
            MarketWatchWidget(),
            MatchAnalysisWidget(),
        )
        yield Footer()
```

**Testing UI**:
```python
from textual.pilot import Pilot

async def test_navigation():
    app = BetCopilotTUI()
    async with app.run_test() as pilot:
        await pilot.press("m")  # Switch to markets
        assert app.current_screen == "markets"
```

---

## 📊 Timeline Estimado

### Branch 1: Web Terminal (5-7 días)
- Día 1-2: Investigación y setup básico
- Día 3-4: Implementación servidor + auth
- Día 5: Dockerización
- Día 6: Nginx + SSL
- Día 7: Testing y docs

### Branch 2: Textual Migration (7-10 días)
- Día 1-2: Diseño de widgets y arquitectura
- Día 3-5: Implementación de widgets
- Día 6-7: Navegación e integración
- Día 8-9: Tests UI
- Día 10: Documentación y polish

### Integration + Deploy (3-5 días)
- Día 1-2: Merge e integración
- Día 3: Testing completo
- Día 4-5: Deploy alpha y pruebas

**Total**: ~20 días (3 semanas)

---

## 🚀 Comandos de Inicio

```bash
# Crear ambas branches
git checkout master
git checkout -b laptop/feature/web-terminal-shellinabox
git push -u origin laptop/feature/web-terminal-shellinabox

git checkout master
git checkout -b laptop/feature/textual-migration-complete
git push -u origin laptop/feature/textual-migration-complete

# Iniciar desarrollo
# Terminal 1: Web terminal branch
git checkout laptop/feature/web-terminal-shellinabox

# Terminal 2: Textual migration branch
git checkout laptop/feature/textual-migration-complete
```

---

## 📝 Checklist de Features

### Web Terminal Branch
- [ ] Investigar shellinabox/ttyd/wetty
- [ ] Setup servidor básico
- [ ] Implementar autenticación
- [ ] Crear Dockerfile
- [ ] Configurar docker-compose
- [ ] Setup Nginx reverse proxy
- [ ] Configurar SSL/TLS
- [ ] Rate limiting
- [ ] Logging de accesos
- [ ] Testing de seguridad
- [ ] Documentación completa
- [ ] Script de deploy

### Textual Migration Branch
- [ ] Refactorizar textual_app.py
- [ ] Crear widget: OddsTable
- [ ] Crear widget: MatchCard
- [ ] Crear widget: MarketWatch
- [ ] Crear widget: APIStatus
- [ ] Crear widget: LogsPanel
- [ ] Implementar screens: Dashboard
- [ ] Implementar screens: MatchAnalysis
- [ ] Implementar screens: Markets
- [ ] Implementar screens: Settings
- [ ] Navegación por teclado
- [ ] Integración con cli.py
- [ ] Tests UI (5+ tests)
- [ ] Documentación de uso
- [ ] Screenshots/GIFs

---

## 🎯 Objetivos del Alpha

**User Stories**:
1. Como usuario alpha, quiero acceder a la CLI desde mi navegador
2. Como usuario alpha, quiero una UI visual con widgets interactivos
3. Como usuario alpha, quiero navegar por teclado eficientemente
4. Como desarrollador, quiero desplegar fácilmente con Docker

**Métricas de Éxito**:
- [ ] 5+ usuarios alpha testeando
- [ ] < 2 segundos latency en web terminal
- [ ] 100% navegación funcional en TUI
- [ ] Deploy en 1 comando
- [ ] Cero errores críticos en 1 semana

---

**Siguiente acción**: Crear ambas branches y comenzar desarrollo paralelo
