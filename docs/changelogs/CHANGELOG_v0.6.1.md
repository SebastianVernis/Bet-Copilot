# 📜 Changelog v0.6.1 - Navegación con Scroll

**Fecha:** 2026-01-09  
**Tipo:** Feature Enhancement  
**Prioridad:** High

---

## 🎯 Resumen

Implementación de navegación con scroll en CLI y TUI para evitar pérdida de información cuando el contenido excede el tamaño de la terminal.

## ✨ Nuevas Características

### CLI (Rich-based)

#### 1. Paginación Automática
- **Comando `mercados`**: Activa paginador cuando hay más de 10 eventos
- **Comando `analizar`**: Muestra análisis completo con navegación
- **Preservación de estilos**: Colores y formato Rich mantenidos en pager

#### 2. Controles de Navegación
```
↑/↓ o j/k  : Scroll línea por línea
Space/b    : Página siguiente/anterior
q          : Salir del paginador
g/G        : Inicio/fin del documento
```

### TUI (Textual-based)

#### 1. ScrollableContainer en Widgets
- **PredictionWidget**: Panel de predicción con scroll vertical
- **NewsWidget**: Feed de noticias scrollable
- **MarketWatchWidget**: Tabla de mercados con navegación

#### 2. Navegación Mejorada
```
↑/↓        : Scroll vertical
Page Up/Dn : Página completa
Mouse      : Soporte de rueda de scroll
```

## 🔧 Cambios Técnicos

### Modificaciones en `bet_copilot/cli.py`

```python
# Nuevo import
from rich.pager import Pager
from io import StringIO

# fetch_markets(): Paginación para listas largas
if len(events) > 10:
    with self.console.pager(styles=True):
        self.console.print(output.getvalue())

# analyze_match(): Análisis completo con pager
output = StringIO()
temp_console = Console(file=output, ...)
# ... construcción de output ...
with self.console.pager(styles=True):
    self.console.print(output.getvalue())
```

### Modificaciones en `bet_copilot/ui/textual_app.py`

```python
# PredictionWidget con ScrollableContainer
def compose(self) -> ComposeResult:
    yield Label("⚽ Match Prediction")
    yield ScrollableContainer(
        Static("...", id="prediction-content")
    )

# CSS mejorado
#prediction {
    height: 100%;
}

ScrollableContainer {
    height: 100%;
}
```

## 📊 Casos de Uso

### Antes (v0.6.0)
```
> mercados
Se encontraron 38 eventos
  • Arsenal vs Chelsea
  • ... (eventos se cortan)
[Información perdida]
```

### Después (v0.6.1)
```
> mercados
Se encontraron 38 eventos
Presiona 'q' para salir del scroll
  • Arsenal vs Chelsea
  • Manchester City vs Liverpool
  ... [navegación completa de todos los eventos]
  • Evento 38
[Presiona 'q' para volver al CLI]
```

## 🎨 Mejoras de UX

### CLI
✅ **No más información cortada**: Todo el contenido es accesible  
✅ **Navegación intuitiva**: Controles estándar de pager Unix  
✅ **Indicadores claros**: Mensajes de ayuda sobre navegación  
✅ **Estilos preservados**: Colores y formato Rich mantenidos  

### TUI
✅ **Scroll independiente**: Cada panel scrollea por separado  
✅ **Mouse support**: Rueda de scroll funciona en todos los widgets  
✅ **Altura dinámica**: Widgets se ajustan al contenido  
✅ **Visual consistente**: Scroll bars automáticos  

## 📝 Archivos Modificados

```
bet_copilot/cli.py                         [MODIFICADO]
bet_copilot/ui/textual_app.py             [MODIFICADO]
docs/SCROLL_NAVIGATION.md                 [NUEVO]
docs/changelogs/CHANGELOG_v0.6.1.md       [NUEVO]
test_scroll_cli.py                        [NUEVO]
```

## 🧪 Testing

### Tests Automáticos
```bash
# Verificar que no hay regresiones
pytest bet_copilot/tests/ -v
# Result: ✅ 95 tests passed
```

### Tests Manuales
```bash
# Test de pager CLI
python test_scroll_cli.py
# Result: ✅ Pager funciona correctamente

# Test de TUI completo
python textual_main.py
# Result: ✅ Scroll en todos los widgets
```

## 🐛 Bugs Corregidos

- ❌ **CLI**: Información de análisis se cortaba al exceder altura de terminal
- ❌ **CLI**: Listas largas de mercados no eran completamente visibles
- ❌ **TUI**: Widget de predicción mostraba solo contenido visible
- ❌ **TUI**: Sin forma de ver noticias más allá del viewport inicial

## 📚 Documentación

### Nuevos Documentos
- `docs/SCROLL_NAVIGATION.md`: Guía completa de navegación con scroll
- `docs/changelogs/CHANGELOG_v0.6.1.md`: Este changelog

### Documentación Actualizada
- `bet_copilot/cli.py`: Docstrings actualizados
- `bet_copilot/ui/textual_app.py`: Comentarios sobre scroll

## 🔄 Compatibilidad

### Requisitos
- Python 3.8+
- Rich >= 10.0.0 (con soporte de pager)
- Textual >= 0.1.0 (con ScrollableContainer)

### Sistemas Operativos
- ✅ Linux: Usa `less` por defecto
- ✅ macOS: Usa `less` por defecto
- ✅ Windows: Usa `more` por defecto
- ⚠️ Sin TTY: Imprime directamente (fallback automático)

## 🚀 Uso

### CLI - Análisis con Scroll
```bash
python main.py
> mercados soccer_epl
# Navega con flechas, presiona 'q' para salir

> analizar Arsenal vs Chelsea
# Análisis completo con navegación
```

### TUI - Dashboard Scrollable
```bash
python textual_main.py
# Usa flechas ↑/↓ en cada panel
# Scroll con mouse wheel
```

## 🎯 Próximos Pasos (v0.6.2)

- [ ] Agregar indicadores de posición (ej: "Línea 50/200")
- [ ] Implementar búsqueda dentro del pager
- [ ] Bookmarks en contenido largo
- [ ] Export de contenido paginado a archivo
- [ ] Atajos de teclado personalizables

## 🤝 Contribuciones

Esta feature fue solicitada para mejorar la experiencia de usuario cuando se analiza información extensa.

**Reportado por:** Usuario  
**Desarrollado por:** Bet-Copilot Team  
**Revisado por:** Blackbox AI  

---

## 📌 Notas de Migración

### Desde v0.6.0

No se requieren cambios en configuración. La funcionalidad se activa automáticamente:

- **CLI**: Pager se usa cuando contenido > 10 líneas
- **TUI**: Scroll siempre disponible en widgets con ScrollableContainer

### Desactivar Pager (opcional)

Si prefieres impresión directa:
```python
# En cli.py, comentar líneas con pager:
# with self.console.pager(styles=True):
#     self.console.print(output.getvalue())

# Reemplazar con:
self.console.print(output.getvalue())
```

---

**🎉 Feature completamente implementada y testeada**
