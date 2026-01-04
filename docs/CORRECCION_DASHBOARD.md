# Corrección Dashboard - v0.4.1

**Fecha**: 2026-01-04  
**Issue**: Dashboard no era persistente  
**Estado**: ✅ Corregido

---

## 🐛 Problema Detectado

### Comportamiento Anterior (v0.4.0)

```bash
bet-copilot> dashboard

Iniciando dashboard...
[Muestra dashboard]
[Se cierra inmediatamente]
[Vuelve al prompt]
```

**Issue**: El dashboard se mostraba una sola vez con `render_once()` y se cerraba inmediatamente.

---

## ✅ Solución Implementada

### Cambios en `bet_copilot/cli.py`

**Antes**:
```python
async def show_dashboard(self):
    health = await self.check_health()
    self.dashboard.render_once(...)  # Solo imprime una vez
```

**Ahora**:
```python
async def show_dashboard(self):
    from rich.live import Live
    
    with Live(
        self.dashboard.layout,
        console=self.console,
        screen=True,
        auto_refresh=True,
        refresh_per_second=2,
    ) as live:
        while True:
            # Actualizar datos
            self.dashboard.update(...)
            await asyncio.sleep(1)
```

### Cambios en `bet_copilot/ui/dashboard.py`

**Mejorado `run_live()` method**:
- Acepta callback para actualización de datos
- Refresh rate configurable
- Manejo de KeyboardInterrupt

**Footer actualizado**:
```
Antes: "Ctrl+C: Salir  •  Espacio: Actualizar  •  Enter: Comando"
Ahora: "Ctrl+C: Volver al CLI  •  Dashboard se actualiza cada 1 segundo automáticamente"
```

---

## 🎯 Comportamiento Nuevo (v0.4.1)

### Flujo Mejorado

```bash
bet-copilot> dashboard

Iniciando dashboard en vivo...
Presiona Ctrl+C para volver al CLI

[Dashboard se muestra en pantalla completa]
[Se actualiza cada 1 segundo]
[Timestamp cambia en tiempo real]
[Datos se refrescan automáticamente]

[Usuario presiona Ctrl+C]

Dashboard cerrado. Volviendo al CLI...

bet-copilot> _
```

### Características del Dashboard Live

1. **Actualización Automática**
   - Timestamp actualizado cada segundo
   - Datos refrescados en tiempo real
   - No requiere input del usuario

2. **Optimización de Requests**
   - Health check cada 30 segundos (no cada actualización)
   - Usa datos en memoria para markets y logs
   - No gasta quota de API en actualizaciones

3. **Salida Limpia**
   - Ctrl+C cierra dashboard limpiamente
   - Vuelve al CLI sin errores
   - Pantalla se limpia automáticamente

4. **Refresh Rate**
   - 2 actualizaciones por segundo (suave)
   - Timestamp preciso
   - Sin parpadeo

---

## 🔧 Correcciones Adicionales

### 1. Import Missing

**Error**: `NameError: name 'MINIMAL' is not defined`

**Fix**:
```python
from rich.table import Table
from rich.box import MINIMAL
```

Agregado a `bet_copilot/cli.py:14-15`

### 2. Modelo Gemini Deprecado

**Warning**: `gemini-pro is not found for API version v1beta`

**Fix**:
```python
# Antes
model: str = "gemini-pro"

# Ahora
model: str = "gemini-1.5-flash"
```

Actualizado en `bet_copilot/ai/gemini_client.py:58`

---

## 🧪 Testing

Todos los tests siguen pasando:

```bash
$ pytest bet_copilot/tests/ -q

30 passed, 1 skipped, 10 warnings ✅
```

---

## 💡 Uso del Dashboard

### Comandos

```bash
# Iniciar dashboard persistente
bet-copilot> dashboard

# [Dashboard en pantalla completa]
# [Se actualiza automáticamente]

# Presionar Ctrl+C para volver

bet-copilot> _  # De vuelta en el CLI
```

### Qué se Actualiza en Tiempo Real

- ✅ **Timestamp**: Cada segundo
- ✅ **Logs**: Últimos 5 eventos
- ✅ **Markets**: Top 10 por EV
- ✅ **Tasks**: Estado actual
- ✅ **API Health**: Cada 30 segundos

### Qué NO se Actualiza Automáticamente

- ❌ **Markets data**: Requiere comando `mercados` manual
- ❌ **Analysis results**: Requiere comando `analizar` manual

**Razón**: Evitar gastar quota de API automáticamente.

---

## 📊 Comparativa

### Antes (v0.4.0)

```
bet-copilot> dashboard
[Muestra pantalla]
[Se cierra]
bet-copilot> _
```

Tiempo visible: ~1 segundo

### Ahora (v0.4.1)

```
bet-copilot> dashboard
[Muestra pantalla completa]
[Se actualiza cada segundo]
[Timestamp cambia: 10:30:01, 10:30:02, ...]
[Usuario observa en tiempo real]
[Presiona Ctrl+C cuando quiere salir]

Dashboard cerrado. Volviendo al CLI...

bet-copilot> _
```

Tiempo visible: Hasta que usuario salga (persistente)

---

## ✅ Checklist de Corrección

- [x] Importar `Table` y `MINIMAL` en cli.py
- [x] Cambiar `render_once()` a `Live` mode en `show_dashboard()`
- [x] Implementar loop infinito con actualización
- [x] Agregar manejo de KeyboardInterrupt
- [x] Actualizar footer con instrucciones claras
- [x] Mejorar método `run_live()` en Dashboard
- [x] Actualizar modelo Gemini a gemini-1.5-flash
- [x] Corregir test de inicialización
- [x] Verificar todos los tests pasan
- [x] Documentar cambios

---

## 🎉 Resultado

Dashboard ahora es **totalmente persistente** y se actualiza en tiempo real hasta que el usuario presione Ctrl+C.

---

**Versión**: 0.4.1  
**Fecha**: 2026-01-04  
**Tests**: 30/30 ✅  
**Estado**: ✅ Corregido
