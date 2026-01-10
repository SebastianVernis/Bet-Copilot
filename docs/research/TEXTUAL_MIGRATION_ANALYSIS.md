# 🔄 Análisis de Migración: Rich → Textual

**Fecha**: 2026-01-04  
**Estado actual**: Rich (display estático) + prompt_toolkit (input)  
**Objetivo**: Textual TUI completo (display + input interactivo)

---

## 📊 Complejidad Estimada

### ⭐⭐⭐ BAJA-MEDIA (2-3 días de trabajo)

**Razón**: 
- ✅ Textual ya está en dependencies
- ✅ La mayoría del código es lógica de negocio (independiente de UI)
- ✅ Rich y Textual comparten muchos conceptos (Panel, Table, Layout)
- ✅ Solo 17 archivos usan Rich directamente

---

## 📁 Análisis de Código Actual

### Uso de Rich (21 imports en proyecto)

**Archivos principales**:
```
bet_copilot/ui/dashboard.py           - 315 líneas (core UI)
bet_copilot/cli.py                    - Usa Console + Tables
bet_copilot/ui/command_input.py       - Usa prompt_toolkit (no Rich)
scripts/check_deps.py                 - Solo para display
examples/                             - Demos (no core)
```

**Componentes Rich usados**:
- `Console` - Para print/display
- `Panel` - Contenedores con bordes
- `Table` - Tablas de datos
- `Layout` - Grid system estático
- `Live` - Updates en tiempo real (2 usos)
- `Text` - Texto con estilos
- `box` - Estilos de bordes

---

## 🔄 Equivalencias Rich → Textual

### Mapeo Directo (Fácil)

| Rich | Textual | Complejidad |
|------|---------|-------------|
| `Console.print()` | `app.log()` o `Static` widget | ⭐ Trivial |
| `Panel()` | `Container` con border | ⭐ Trivial |
| `Table()` | `DataTable` widget | ⭐⭐ Fácil |
| `Layout()` | `Horizontal`/`Vertical` containers | ⭐⭐ Fácil |
| `Text()` | `Text` o `Label` widget | ⭐ Trivial |

### Requiere Adaptación (Media)

| Rich | Textual | Complejidad |
|------|---------|-------------|
| `Live()` updates | Reactive attributes | ⭐⭐⭐ Media |
| `Prompt()` (prompt_toolkit) | `Input` widget | ⭐⭐ Fácil |
| Estilos inline | CSS-like styling | ⭐⭐⭐ Media |

---

## 🏗️ Arquitectura Propuesta

### Estructura Textual

```python
from textual.app import App
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Input, Button

class BetCopilotApp(App):
    """Main Textual application."""
    
    CSS = """
    #api-health {
        height: 10;
        border: solid green;
    }
    
    #market-watch {
        height: 1fr;  # Fill remaining space
    }
    
    #news-feed {
        width: 1fr;
        border: solid cyan;
    }
    """
    
    def compose(self):
        yield Header()
        
        # Top row: API Health + News
        with Horizontal():
            yield Container(id="api-health")
            yield Container(id="news-feed")
        
        # Middle: Market Watch (main area)
        yield Container(id="market-watch")
        
        # Bottom: Input + Commands
        with Horizontal():
            yield Input(placeholder="Enter command...")
            yield Button("Analyze", id="btn-analyze")
        
        yield Footer()
```

---

## 📋 Plan de Migración

### Fase 1: Prototipo (1 día) ⭐
**Objetivo**: Dashboard básico funcionando

- [ ] Crear `bet_copilot/ui/textual_app.py`
- [ ] Implementar layout de 4 zonas
- [ ] Widgets básicos (Static, DataTable)
- [ ] Sin funcionalidad (solo estructura)

**Archivos afectados**: 1 nuevo
**Complejidad**: ⭐ Baja

---

### Fase 2: Componentes Core (1-2 días) ⭐⭐
**Objetivo**: Migrar dashboard.py funciones

- [ ] `APIHealthWidget` (reemplaza `render_api_health`)
- [ ] `MarketWatchWidget` (reemplaza `render_market_watch`)
- [ ] `NewsWidget` (nuevo, usa NewsScraper)
- [ ] `LogsWidget` (para system logs)

**Archivos afectados**: 4 nuevos widgets
**Complejidad**: ⭐⭐ Media

---

### Fase 3: Interactividad (1 día) ⭐⭐
**Objetivo**: Input commands + acciones

- [ ] `CommandInput` widget (reemplaza prompt_toolkit)
- [ ] Autocompletado con Textual (sugerencias)
- [ ] Handlers para comandos (on_input_submitted)
- [ ] Navegación con teclado

**Archivos afectados**: cli.py refactor
**Complejidad**: ⭐⭐ Media

---

### Fase 4: Reactive Updates (1 día) ⭐⭐⭐
**Objetivo**: Live data updates

- [ ] Reactive variables para API status
- [ ] Auto-refresh de market watch (cada 30s)
- [ ] News feed updates (cada 1h)
- [ ] Progress indicators

**Archivos afectados**: Todos los widgets
**Complejidad**: ⭐⭐⭐ Media-Alta

---

### Fase 5: Polish & Testing (1 día) ⭐⭐
**Objetivo**: Estabilidad y UX

- [ ] CSS styling (colores neón)
- [ ] Keyboard shortcuts
- [ ] Error handling en UI
- [ ] Tests de widgets
- [ ] Documentación

**Archivos afectados**: CSS, tests
**Complejidad**: ⭐⭐ Media

---

## 🎯 Esfuerzo Total

### Timeline Estimado

| Fase | Esfuerzo | Resultado |
|------|----------|-----------|
| Fase 1 | 4-6 horas | Estructura básica |
| Fase 2 | 8-12 horas | Widgets funcionales |
| Fase 3 | 6-8 horas | Input interactivo |
| Fase 4 | 6-8 horas | Updates en vivo |
| Fase 5 | 4-6 horas | Production-ready |
| **TOTAL** | **28-40 horas** | **~3-5 días** |

**Complejidad final**: ⭐⭐⭐ **MEDIA**

---

## ✅ Ventajas de Migrar a Textual

### 1. **Interactividad Nativa**
**Rich**:
```python
# Estático - requiere re-render completo
with Live(layout, refresh_per_second=1):
    while True:
        layout.update()  # Re-render todo
        await asyncio.sleep(1)
```

**Textual**:
```python
# Reactivo - solo actualiza lo que cambió
self.market_table.reactive_var = new_data  # Auto-update
```

### 2. **Input Built-in**
**Rich** (actual):
- Requiere `prompt_toolkit` separado
- Dos librerías diferentes (Rich + prompt_toolkit)
- Coordinación manual

**Textual**:
- Input, Button, Select integrados
- Todo en una librería
- Eventos nativos

### 3. **Event System**
**Rich**:
- No tiene event loop propio
- Manual polling

**Textual**:
```python
def on_button_pressed(self, event):
    """Handler automático"""
    
async def on_input_submitted(self, event):
    """Input events nativos"""
```

### 4. **Keyboard Shortcuts**
**Textual**:
```python
BINDINGS = [
    ("q", "quit", "Quit"),
    ("r", "refresh", "Refresh"),
    ("n", "news", "Show News"),
]

def action_refresh(self):
    """Ctrl+R = refresh"""
```

### 5. **Responsive Layout**
**Rich**:
- Layout estático
- Requiere cálculos manuales

**Textual**:
- CSS con `width: 1fr`
- Auto-resize responsive
- Media queries posibles

---

## ⚠️ Desventajas / Consideraciones

### 1. **Curva de Aprendizaje**
- Textual tiene conceptos nuevos (App, Screen, Workers)
- CSS-like styling diferente a Rich inline styles
- Event handling asíncrono

### 2. **Debugging**
- Rich errors son simples (render fails)
- Textual errors pueden ser más complejos (event loop, widgets)

### 3. **Breaking Changes**
- Todos los scripts de ejemplo usan Rich
- Documentación actual muestra Rich
- Usuarios familiarizados con output actual

---

## 🎨 Prototipo Textual

### Estructura Básica

```python
# bet_copilot/ui/textual_app.py

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Input, Label
from textual.reactive import reactive

class APIHealthWidget(Static):
    """API health status display."""
    
    odds_status = reactive("unknown")
    football_status = reactive("unknown")
    
    def render(self):
        return Panel(
            f"Odds API: {self.odds_status}\n"
            f"Football API: {self.football_status}",
            title="API Health"
        )

class MarketWatchWidget(Static):
    """Market watch with live updates."""
    
    markets = reactive([])
    
    def compose(self):
        yield DataTable()
    
    def watch_markets(self, markets):
        """Auto-update when markets change."""
        table = self.query_one(DataTable)
        table.clear()
        for market in markets:
            table.add_row(market.home_team, market.ev, ...)

class NewsWidget(Static):
    """Live news feed."""
    
    articles = reactive([])
    
    def compose(self):
        yield Label("📰 Latest News")
        yield Container(id="news-list")
    
    async def on_mount(self):
        """Fetch news on startup."""
        from bet_copilot.news import NewsScraper
        scraper = NewsScraper()
        self.articles = await scraper.fetch_all_news()

class BetCopilotApp(App):
    """Main Textual application."""
    
    CSS_PATH = "app.tcss"  # External CSS file
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_markets", "Refresh"),
        ("n", "toggle_news", "News"),
        ("a", "analyze_match", "Analyze"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        # Top row
        with Horizontal(id="top-row"):
            yield APIHealthWidget(id="api-health")
            yield NewsWidget(id="news-feed")
        
        # Main area
        yield MarketWatchWidget(id="market-watch")
        
        # Input area
        with Horizontal(id="input-row"):
            yield Input(placeholder="Enter command or team names...")
            yield Button("Analyze", variant="success")
        
        yield Footer()
    
    async def on_input_submitted(self, event):
        """Handle command input."""
        command = event.value
        # Process command
        await self.process_command(command)
    
    async def action_refresh_markets(self):
        """Refresh market data."""
        market_widget = self.query_one(MarketWatchWidget)
        # Fetch new data
        market_widget.markets = await self.fetch_markets()
    
    async def action_toggle_news(self):
        """Toggle news panel visibility."""
        news_widget = self.query_one(NewsWidget)
        news_widget.display = not news_widget.display
```

### CSS Styling

```css
/* app.tcss */

#api-health {
    width: 1fr;
    height: 10;
    border: solid green;
}

#news-feed {
    width: 1fr;
    height: 10;
    border: solid cyan;
}

#market-watch {
    height: 1fr;
    border: solid yellow;
}

#input-row {
    height: 3;
    dock: bottom;
}

DataTable {
    background: #1a1a1a;
    color: #39ff14;
}
```

---

## 📊 Comparación Detallada

### Rich (Actual)

**Pros**:
- ✅ Simple para output estático
- ✅ Excelente para demos/scripts
- ✅ Menor complejidad inicial
- ✅ Familiar para el equipo

**Cons**:
- ❌ No es interactivo nativamente
- ❌ Requiere prompt_toolkit separado
- ❌ Live() es "hack" para updates
- ❌ No tiene event system
- ❌ Layout estático

### Textual (Propuesto)

**Pros**:
- ✅ Interactividad nativa (clicks, keyboard)
- ✅ Event system robusto
- ✅ Reactive updates eficientes
- ✅ CSS styling potente
- ✅ Widgets reutilizables
- ✅ Mejor para dashboards complejos
- ✅ Mouse support opcional
- ✅ Screens (múltiples vistas)

**Cons**:
- ❌ Más complejo conceptualmente
- ❌ Requiere refactor de UI completa
- ❌ Curva de aprendizaje mayor
- ❌ Debugging más difícil inicialmente

---

## 🎯 Recomendación

### Opción 1: **Migración Completa** ⭐⭐⭐
**Esfuerzo**: 3-5 días  
**Beneficio**: Dashboard profesional e interactivo  
**Riesgo**: Medio (requiere testing exhaustivo)

**Ideal si**:
- Quieres dashboard permanente (no CLI one-off)
- Usuarios interactúan frecuentemente
- Planeas features UI-heavy (gráficos, multi-screens)

### Opción 2: **Híbrido (Recomendado)** ⭐⭐
**Esfuerzo**: 1-2 días  
**Beneficio**: Lo mejor de ambos  
**Riesgo**: Bajo

**Arquitectura**:
```
- CLI commands → Mantener Rich (simple, funciona)
- Dashboard live → Migrar a Textual (mejor para TUI)
- Examples/demos → Mantener Rich (más fácil de leer)
```

**Archivos a migrar**:
- `bet_copilot/ui/dashboard.py` → `bet_copilot/ui/textual_dashboard.py`
- Crear `BetCopilotApp` en Textual
- CLI puede elegir modo: `--mode=cli` (Rich) o `--mode=tui` (Textual)

### Opción 3: **No Migrar** ⭐
**Esfuerzo**: 0 días  
**Beneficio**: Estabilidad  
**Riesgo**: Ninguno

**Mantener si**:
- Sistema funciona bien actualmente
- Usuarios prefieren CLI simple
- No necesitas interactividad avanzada

---

## 🚀 Plan de Migración Híbrida (Recomendado)

### Paso 1: Crear Textual Dashboard (Paralelo)
**No rompe nada existente**

```bash
bet_copilot/ui/
├── dashboard.py          # Mantener (Rich, para CLI)
├── textual_dashboard.py  # NUEVO (Textual, para TUI)
├── textual_app.py        # NUEVO (App principal)
├── widgets/              # NUEVO (widgets reutilizables)
│   ├── api_health.py
│   ├── market_watch.py
│   ├── news_feed.py
│   └── alternative_markets.py
└── styles.tcss           # NUEVO (CSS)
```

### Paso 2: Punto de Entrada Dual

```python
# main.py (actualizado)

import sys

if "--tui" in sys.argv:
    # Textual mode (dashboard interactivo)
    from bet_copilot.ui.textual_app import BetCopilotApp
    app = BetCopilotApp()
    app.run()
else:
    # CLI mode (Rich, actual)
    from bet_copilot.cli import BetCopilotCLI
    cli = BetCopilotCLI()
    asyncio.run(cli.run())
```

### Paso 3: Deprecación Gradual (Opcional)

- v0.6: Ambos modos disponibles
- v0.7: TUI como default, CLI con flag `--cli`
- v0.8: Solo TUI (CLI deprecated)

---

## 💡 Ejemplo de Widget Textual

### Market Watch Widget (Completo)

```python
# bet_copilot/ui/widgets/market_watch.py

from textual.widgets import Static, DataTable
from textual.reactive import reactive

class MarketWatchWidget(Static):
    """Live market watch with auto-refresh."""
    
    markets = reactive([])
    auto_refresh = reactive(True)
    
    def compose(self):
        yield DataTable()
    
    def on_mount(self):
        """Initialize table on mount."""
        table = self.query_one(DataTable)
        
        # Add columns
        table.add_column("Match", width=25)
        table.add_column("Market", width=15)
        table.add_column("EV", width=8)
        table.add_column("Odds", width=8)
        table.add_column("Stake", width=10)
        
        # Start auto-refresh
        if self.auto_refresh:
            self.set_interval(30, self.refresh_data)
    
    async def refresh_data(self):
        """Fetch new market data."""
        # Call your service
        from bet_copilot.services.match_analyzer import MatchAnalyzer
        analyzer = MatchAnalyzer()
        
        # Update reactive var (triggers auto-update)
        self.markets = await analyzer.get_value_bets()
    
    def watch_markets(self, markets):
        """Called automatically when markets changes."""
        table = self.query_one(DataTable)
        table.clear()
        
        for market in markets:
            # Color coding
            if market.ev > 0.10:
                style = "bold green"
            elif market.ev > 0.05:
                style = "yellow"
            else:
                style = "dim"
            
            table.add_row(
                f"{market.home_team} vs {market.away_team}",
                market.market_type,
                f"{market.ev:+.1%}",
                f"{market.odds:.2f}",
                f"{market.recommended_stake:.1%}",
                style=style
            )
```

**Beneficios vs Rich**:
- ✅ Auto-refresh cada 30s (sin Live() hack)
- ✅ Reactive updates (solo redibuja lo que cambió)
- ✅ Built-in interval timers
- ✅ Efficient rendering

---

## 📈 Comparación de Complejidad

### Rich (Actual): ⭐⭐
```python
# Simple pero limitado
console = Console()
table = Table()
table.add_row(...)
console.print(table)
```

**Pros**: Inmediato, fácil  
**Cons**: Estático, no interactivo

### Textual: ⭐⭐⭐
```python
# Más setup pero más potente
class MyWidget(Static):
    data = reactive([])
    
    def compose(self):
        yield DataTable()
    
    def watch_data(self, data):
        # Auto-update
```

**Pros**: Interactivo, profesional  
**Cons**: Curva aprendizaje

### Diferencia: +50% complejidad, +300% capacidades

---

## 🔍 Análisis de Riesgo

### Riesgos de Migración

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Bugs en UI | Media | Bajo | Mantener Rich en paralelo |
| User confusion | Baja | Bajo | Docs + tutorial |
| Performance issues | Baja | Medio | Profiling + optimización |
| Incomplete migration | Media | Alto | Migración por fases |

### Riesgos de NO Migrar

| Riesgo | Probabilidad | Impacto |
|--------|--------------|---------|
| UI limitada | Alta | Medio |
| User experience inferior | Media | Medio |
| Features difíciles de agregar | Alta | Alto |

---

## 💰 ROI Estimado

### Inversión
- **Tiempo**: 3-5 días desarrollo
- **Riesgo**: Medio (testeado en paralelo)

### Retorno
- **UX mejorada**: Interactividad nativa
- **Mantenibilidad**: Un framework vs dos (Rich + prompt_toolkit)
- **Features futuras**: Más fácil agregar gráficos, multi-screens
- **Profesionalismo**: Dashboard de "producto real"

### ROI = **POSITIVO** si el proyecto es long-term

---

## 🎬 Demo Visual Propuesto

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ BET-COPILOT v0.6 - Multi-AI Analysis Dashboard                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────── API Health ────────────────┬──────────── News Feed ──────────┐
│ ● Odds API      Healthy   (12/500)        │ 📰 2h ago - City injuries       │
│ ● Football API  Healthy   (45/100)        │ 📰 4h ago - Liverpool signs     │
│ ● Gemini AI     Available ✓               │ 📰 6h ago - Arsenal preview     │
│ ● Blackbox AI   Available ✓               │ [Scroll for more ↓]            │
│ 🤝 Collaborative: ACTIVE (85% agreement)  │                                 │
└───────────────────────────────────────────┴─────────────────────────────────┘

┌─────────────────────── Market Watch (Live) ───────────────────────────────┐
│ Match                    Market      EV      Odds   Stake   Confidence    │
├───────────────────────────────────────────────────────────────────────────┤
│ Man City vs Liverpool    Home Win   +12.5%  2.10   8.2%    ⭐⭐⭐⭐⭐      │
│ Arsenal vs Chelsea       Over 2.5   +8.3%   2.05   5.1%    ⭐⭐⭐⭐        │
│ → Corners Over 10.5      +15.2%     1.95   10.8%   ⭐⭐⭐⭐⭐   ← NEW      │
│ → Cards Over 4.5         +6.1%      2.20   3.2%    ⭐⭐⭐              │
│ Tottenham vs Newcastle   Draw       +5.8%   3.40   2.1%    ⭐⭐⭐          │
│                                                                           │
│ [Auto-refresh: 28s] [Last update: 14:32:15]                             │
└───────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────── Alternative Markets ───────────────────────────┐
│ 📐 Corners  🟨 Cards  🎯 Shots  🚩 Offsides                   [View All] │
│                                                                           │
│ Man City vs Liverpool - Expected Corners: 11.8                           │
│ ████████████████░░░░ Over 10.5 (78%) ✅ HIGH VALUE                       │
└───────────────────────────────────────────────────────────────────────────┘

 > analyze man city liverpool _
 
 [Tab] autocomplete | [↑↓] history | [Ctrl+R] search | [q] quit | [n] news
```

**Interactividad**:
- Click en partido → Análisis detallado
- Click en "View All" → Pantalla de alternative markets
- Navegación con teclas
- Auto-refresh en background

---

## 🎓 Recursos de Aprendizaje

### Documentación Textual
- Tutorial oficial: https://textual.textualize.io/tutorial/
- Widget gallery: https://textual.textualize.io/widget_gallery/
- CSS guide: https://textual.textualize.io/guide/CSS/

### Ejemplos Similares
- Textual demo apps: https://github.com/Textualize/textual/tree/main/examples
- Rich to Textual migration: https://textual.textualize.io/blog/

### Tiempo de Aprendizaje
- Básico: 2-4 horas (tutorial + ejemplos)
- Intermedio: 1 día (crear widgets propios)
- Avanzado: 2-3 días (reactive, workers, screens)

---

## ✅ Decisión Recomendada

### 🎯 **MIGRACIÓN HÍBRIDA** (Opción 2)

**Plan**:
1. **Fase 1** (ahora): Crear prototipo Textual en paralelo
2. **Fase 2** (v0.6): Ofrecer ambos modos (`--cli` y `--tui`)
3. **Fase 3** (v0.7): Evaluar feedback, deprecar uno

**Ventajas**:
- ✅ Sin breaking changes
- ✅ Usuarios eligen su preferencia
- ✅ Aprendemos Textual sin riesgo
- ✅ Mejor para long-term

**Inversión**: 1-2 días para prototipo funcional

---

## 📝 Conclusión

**Complejidad de migración**: ⭐⭐⭐ MEDIA (3-5 días)

**¿Vale la pena?**
- **Corto plazo (1-3 meses)**: No urgente
- **Mediano plazo (6-12 meses)**: Recomendado
- **Largo plazo (1+ años)**: Esencial para profesionalismo

**Próximo paso inmediato**: Crear prototipo Textual (4-6 horas) para evaluar fit real con tu workflow.

---

**Autor**: Análisis técnico para decisión de arquitectura  
**Versión**: Bet-Copilot v0.5.0  
**Última actualización**: 2026-01-04
