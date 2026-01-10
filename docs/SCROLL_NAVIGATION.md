# 📜 Navegación con Scroll en Bet-Copilot

## 🎯 Descripción

Se ha implementado navegación con scroll en ambas interfaces (CLI y TUI) para evitar que la información se corte cuando hay contenido extenso.

## 📋 Características Implementadas

### 1. CLI (Rich-based)

El CLI ahora utiliza `rich.pager` para mostrar contenido largo con navegación interactiva:

#### **Comandos con Paginación:**
- ✅ `mercados` - Lista de eventos (cuando hay más de 10)
- ✅ `analizar [partido]` - Análisis completo de partidos
- ✅ Contenido que supere el tamaño de la terminal

#### **Controles de Navegación:**
```
↑ / ↓ o j / k    Navegar línea por línea
Space / b        Página siguiente/anterior
g / G            Ir al inicio/final
q                Salir del paginador
/                Buscar (en algunos pagers)
```

### 2. TUI (Textual-based)

El TUI utiliza `ScrollableContainer` para widgets con contenido extenso:

#### **Widgets con Scroll:**
- ✅ `PredictionWidget` - Análisis de predicción de partidos
- ✅ `NewsWidget` - Feed de noticias en tiempo real
- ✅ `MarketWatchWidget` - Tabla de mercados

#### **Controles de Navegación:**
```
↑ / ↓            Scroll vertical línea por línea
Page Up/Down     Scroll de página
Home / End       Ir al inicio/final
Mouse Wheel      Scroll con rueda del mouse
```

## 🚀 Uso

### Ejemplo CLI - Análisis de Partido

```bash
python main.py
> mercados
Se encontraron 25 eventos
Presiona 'q' para salir del scroll si hay muchos eventos

# Navega con flechas ↑/↓ o Space/b
# Presiona 'q' para volver al CLI

> analizar Arsenal vs Chelsea
# El análisis completo se muestra en paginador
# Navega libremente, presiona 'q' cuando termines
```

### Ejemplo TUI - Dashboard Interactivo

```bash
python textual_main.py

# Todos los paneles tienen scroll automático
# Usa flechas ↑/↓ para navegar
# Click en widget y scroll con mouse
```

## 🔧 Implementación Técnica

### CLI Implementation

```python
from rich.pager import Pager
from io import StringIO

# Construir output en buffer
output = StringIO()
temp_console = Console(file=output, force_terminal=True, width=self.console.width)

# Agregar contenido al buffer
temp_console.print("[bold]Título[/bold]")
temp_console.print("Contenido...")

# Mostrar con pager
with self.console.pager(styles=True):
    self.console.print(output.getvalue())
```

### TUI Implementation

```python
from textual.widgets import RichLog

class MyWidget(Static):
    def compose(self) -> ComposeResult:
        yield Label("Título")
        log = RichLog(id="content", highlight=True, markup=True)
        log.write("[bold]Contenido con markup[/bold]")
        log.write("Línea 2 con [cyan]colores[/cyan]")
        yield log
    
    def update_content(self, new_data):
        log = self.query_one("#content", RichLog)
        log.clear()  # Limpiar contenido anterior
        log.write(f"[green]{new_data}[/green]")
```

## 📊 Casos de Uso

### 1. Lista Larga de Mercados
Cuando obtienes mercados de una liga con muchos partidos:
```
> mercados soccer_epl
Se encontraron 38 eventos
[Paginador activado automáticamente]
```

### 2. Análisis Detallado
Cuando el análisis incluye:
- Estadísticas de equipos
- Jugadores lesionados/suspendidos
- Historial H2H
- Predicción Poisson
- Análisis de IA
- Insights y recomendaciones

```
> analizar Manchester City vs Liverpool
[Contenido completo con navegación]
```

### 3. Dashboard con Múltiples Secciones
En TUI, cada panel tiene scroll independiente:
- Panel de predicción (arriba)
- Panel de mercados (medio)
- Panel de noticias (izquierda)

## 🎨 Ventajas

### CLI
✅ No se pierde información al final de la pantalla  
✅ Control total sobre navegación  
✅ Búsqueda de texto (con pagers avanzados)  
✅ Preserva colores y estilos Rich  

### TUI
✅ Scroll independiente por widget  
✅ Soporte de mouse  
✅ Visual más intuitivo  
✅ Múltiples áreas scrollables simultáneamente  

## 🐛 Notas y Limitaciones

### CLI
- El pager usa el pager del sistema (`less` en Linux/Mac, `more` en Windows)
- Algunos comandos de búsqueda dependen del pager instalado
- En ambientes sin TTY, el contenido se imprime directamente

### TUI
- El scroll se activa automáticamente cuando el contenido excede el tamaño del widget
- Usa `RichLog` que soporta markup completo de Rich
- Los eventos de teclado pueden ser capturados por el widget con foco
- Mouse wheel requiere soporte del terminal
- Método `clear()` permite limpiar contenido antes de actualizar

## 📝 Configuración

### Cambiar Pager en CLI (Linux/Mac)
```bash
export PAGER="less -R"  # Con colores
export PAGER="most"     # Alternativa avanzada
```

### Ajustar Altura de Widgets en TUI
Edita `textual_app.py`:
```python
#prediction {
    height: 20;  # Ajusta altura del panel
}
```

## 🔍 Testing

Prueba la funcionalidad con:
```bash
# Test de pager CLI
python test_scroll_cli.py

# Test de TUI completo
python textual_main.py
```

## 📚 Recursos

- [Rich Pager Documentation](https://rich.readthedocs.io/en/stable/console.html#paging)
- [Textual Scrolling](https://textual.textualize.io/guide/layout/#scrolling)
- [Less Command Tutorial](https://man7.org/linux/man-pages/man1/less.1.html)

## ✨ Futuras Mejoras

- [ ] Agregar indicadores visuales de posición de scroll (ej: "Línea 50/200")
- [ ] Implementar búsqueda en TUI widgets
- [ ] Agregar atajos de teclado personalizados
- [ ] Soporte para export de contenido paginado
- [ ] Bookmarks dentro del contenido largo

---

**Versión:** 0.6.1  
**Fecha:** 2026-01-09  
**Autor:** Bet-Copilot Team
