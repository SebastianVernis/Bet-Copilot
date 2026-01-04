# 🎹 Advanced Command Input - Bet-Copilot

Sistema avanzado de entrada de comandos con historial, autocompletado y navegación con teclado.

## ✨ Características

### 1. **Historial de Comandos**
- **↑/↓**: Navega por comandos anteriores
- **Ctrl+R**: Búsqueda incremental en historial
- Persistencia en memoria durante la sesión

### 2. **Autocompletado Inteligente**
- **Tab**: Autocompleta comandos y argumentos
- **Sugerencias contextuales**: 
  - Comandos base cuando no hay input
  - Sport keys después de `mercados`/`markets`
  - Nombres de partidos después de `analizar`/`analyze`
- **Metadatos**: Muestra descripción de cada opción

### 3. **Edición Inline**
- **←/→**: Mueve el cursor en la línea
- **Ctrl+A**: Ir al inicio de la línea
- **Ctrl+E**: Ir al final de la línea
- **Ctrl+K**: Borrar desde cursor hasta el final
- **Ctrl+U**: Borrar toda la línea

### 4. **Interfaz Visual**
- Prompt con flecha estilizada: `➜ bet-copilot`
- Menú de completado con colores neón
- Selección actual destacada

## 🚀 Uso

### En el CLI principal:
```bash
python main.py
```

El input avanzado se activa automáticamente. Todos los comandos existentes funcionan igual:

```
➜ bet-copilot dashboard
➜ bet-copilot mercados soccer_la_liga
➜ bet-copilot analizar "Arsenal vs Chelsea"
```

### Probar funcionalidades:
```bash
# Script unificado (recomendado)
./run_tests.sh

# O tests individuales
python bet_copilot/tests/test_command_input.py
python bet_copilot/tests/test_autocompletion.py
python bet_copilot/tests/test_completion_interactive.py
```

## 📋 Comandos Disponibles

| Comando | Descripción | Autocompletado |
|---------|-------------|----------------|
| `dashboard` | Mostrar dashboard en vivo | ✅ |
| `mercados [sport]` | Obtener mercados | ✅ + sport keys |
| `analizar [match]` | Analizar partido | ✅ + nombres de partidos |
| `salud` | Verificar APIs | ✅ |
| `ayuda` | Mostrar ayuda | ✅ |
| `salir` | Salir | ✅ |

## 🎯 Ejemplos de Uso

### Autocompletado de comandos:
```
➜ bet-copilot mer[Tab]
→ mercados
```

### Autocompletado de sport keys:
```
➜ bet-copilot mercados soc[Tab]
→ Muestra: soccer_epl, soccer_la_liga, soccer_serie_a, ...
```

### Autocompletado de partidos:
```
➜ bet-copilot analizar Ars[Tab]
→ Muestra partidos disponibles: "Arsenal vs Chelsea", etc.
```

### Navegación de historial:
```
➜ bet-copilot mercados
➜ bet-copilot dashboard
[Presiona ↑]
→ dashboard
[Presiona ↑ nuevamente]
→ mercados
```

### Búsqueda en historial (Ctrl+R):
```
(reverse-i-search)`merc': mercados soccer_la_liga
```

## 🔧 Implementación Técnica

### Arquitectura:
```
CommandInput (bet_copilot/ui/command_input.py)
├── PromptSession (prompt_toolkit)
│   ├── InMemoryHistory
│   ├── BetCopilotCompleter
│   └── Style personalizado
└── Métodos públicos:
    ├── get_command() → str
    ├── add_to_history()
    ├── get_history() → List[str]
    └── clear_history()
```

### BetCopilotCompleter:
```python
class BetCopilotCompleter(Completer):
    def get_completions(document, complete_event):
        # Lógica contextual:
        # 1. Primera palabra → comandos base
        # 2. Segunda palabra → argumentos específicos
        #    - mercados → sport keys
        #    - analizar → nombres de partidos (de cli.events)
```

### Integración con CLI:
```python
class BetCopilotCLI:
    def __init__(self):
        # ...
        self.command_input = create_command_input(self)
    
    async def run(self):
        # Bucle principal
        command = await self.command_input.get_command()
        await self.run_command(command)
```

## 🎨 Estilo Visual

### Colores:
- **Prompt**: `#00FFFF` (cyan neón)
- **Flecha**: `#00FFFF` (cyan neón, bold)
- **Menú de completado**: Fondo `#222222`, texto `#CCCCCC`
- **Item seleccionado**: Fondo `#00FFFF`, texto `#000000` (invertido)

### Tipografía:
- Monoespaciada (heredada del terminal)
- Uso de caracteres Unicode: `➜`, `↑`, `↓`, `←`, `→`

## 📦 Dependencias

```
prompt_toolkit>=3.0.0
```

Agregado a `requirements.txt`.

## 🧪 Testing

### Test manual:
```bash
# Script unificado
./run_tests.sh

# O tests individuales
python bet_copilot/tests/test_command_input.py
python bet_copilot/tests/test_autocompletion.py
python bet_copilot/tests/test_completion_interactive.py
```

Comandos especiales en el test:
- `history`: Ver historial de comandos
- `clear`: Limpiar historial
- `quit`: Salir del test

### Verificar características:
1. ✅ Tab completion funciona
2. ✅ ↑/↓ navega historial
3. ✅ Ctrl+R busca en historial
4. ✅ ←/→ mueve cursor
5. ✅ Metadatos se muestran en menú

## 🔍 Troubleshooting

### "prompt_toolkit not found"
```bash
# Agregar a requirements.txt (ya hecho)
pip install prompt_toolkit
```

### Historial no persiste entre sesiones
**Comportamiento esperado**. Usa `InMemoryHistory` por diseño. Para persistir, cambiar a `FileHistory`:
```python
from prompt_toolkit.history import FileHistory
self.history = FileHistory('.bet_copilot_history')
```

### Autocompletado no muestra partidos
Primero ejecutar `mercados` para llenar `cli.events`.

## 🚀 Roadmap

- [ ] Persistir historial en archivo
- [ ] Syntax highlighting en tiempo real
- [ ] Comandos con alias (ej: `m` → `mercados`)
- [ ] Validación de argumentos en tiempo real
- [ ] Sugerencias basadas en frecuencia de uso
- [ ] Atajos personalizables

## 📚 Referencias

- **prompt_toolkit**: https://python-prompt-toolkit.readthedocs.io/
- **Completion API**: https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#autocompletion
- **Key Bindings**: https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html

---

**Autor**: Bet-Copilot Team  
**Versión**: 0.5.0  
**Fecha**: 2026-01-04
