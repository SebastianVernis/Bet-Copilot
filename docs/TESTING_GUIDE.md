# 🧪 Guía de Testing - Autocompletado

## 🎯 Problema Reportado

**Issue**: `analizar` + Tab no muestra partidos, agrega letra al principio

**Causa identificada**: 
- Lógica de parsing consideraba solo `len(words) == 2`
- No manejaba correctamente `"analizar "` (comando + espacio)
- `start_position` incorrecto causaba que agregara caracteres

## ✅ Solución Aplicada

Reescrita la lógica de `get_completions()` en 3 casos:

### Caso 1: Comando incompleto (sin espacio)
```python
# Input: "ana"
if len(parts) == 1 and not text.endswith(' '):
    # → Autocompletar comando
```

### Caso 2: Comando completo + espacio
```python
# Input: "analizar "
if len(parts) == 1 and text.endswith(' '):
    # → Mostrar TODOS los argumentos (partidos/sports)
```

### Caso 3: Comando + argumento parcial
```python
# Input: "analizar Ars"
if len(parts) >= 2:
    # → Filtrar argumentos que coincidan
```

## 🧪 Tests Disponibles

### 0. Script de Tests Unificado (Recomendado)
```bash
./run_tests.sh
```

**Menú interactivo** con todas las opciones:
- [1] All Tests (pytest)
- [2] Unit Tests (core functionality)
- [3] Command Input Tests (interactive)
- [4] Completion Debug (logic only)
- [5] Completion Interactive (full UI)
- [6] Autocompletion with Mock Data
- [7] Coverage Report

### 1. Test de Lógica (No Interactivo)
```bash
python3 bet_copilot/tests/test_completion_debug.py
```

**Verifica**:
- Parsing correcto de diferentes inputs
- Filtrado de partidos por texto parcial
- Casos edge (espacios, múltiples palabras)

**Output esperado**:
```
Input: 'analizar '
  → Action: Show arguments for 'analizar'

Input: 'analizar Ars'
  → Action: Complete argument 'Ars' for 'analizar'
```

---

### 2. Test Interactivo Completo
```bash
python3 bet_copilot/tests/test_completion_interactive.py
```

**Requiere**: Terminal interactivo (no funciona en scripts)

**Casos de prueba**:

#### A) Autocompletar comando
```
Escribir: ana[Tab]
Esperado: → analizar
```

#### B) Mostrar todos los partidos
```
Escribir: analizar [Tab]
            ↑ espacio + Tab
Esperado:
  • Arsenal vs Chelsea
  • Manchester United vs Liverpool
  • Manchester City vs Tottenham
  • Barcelona vs Real Madrid
  • Bayern Munich vs Borussia Dortmund
```

#### C) Filtrar partidos por equipo
```
Escribir: analizar Ars[Tab]
Esperado:
  • Arsenal vs Chelsea

Escribir: analizar Man[Tab]
Esperado:
  • Manchester United vs Liverpool
  • Manchester City vs Tottenham
```

#### D) Sport keys
```
Escribir: mercados [Tab]
Esperado:
  • soccer_epl (Premier League)
  • soccer_la_liga (La Liga)
  • ...

Escribir: mercados soc[Tab]
Esperado: Solo ligas de soccer
```

---

### 3. Test Autocompletado con Mock
```bash
python3 bet_copilot/tests/test_autocompletion.py
```

### 4. Test Básico Command Input
```bash
python3 bet_copilot/tests/test_command_input.py
```

### 5. Test en CLI Real
```bash
python3 main.py
```

**Flujo de prueba**:

1. **Obtener mercados reales**:
```
➜ bet-copilot mercados soccer_epl
✓ Se encontraron X eventos
Usa 'analizar [nombre]' + Tab para autocompletar
```

2. **Probar autocompletado**:
```
➜ bet-copilot analizar [Tab]
  [Debe mostrar partidos reales de la API]
```

3. **Filtrar por equipo**:
```
➜ bet-copilot analizar Arsenal[Tab]
  [Debe filtrar solo partidos con "Arsenal"]
```

4. **Seleccionar y ejecutar**:
```
➜ bet-copilot analizar Arsenal vs Chelsea
  [Debe ejecutar análisis completo]
```

---

## 🔍 Verificación Manual

### Checkpoint 1: Parsing Correcto
```python
# En test_completion_debug.py
Input: 'analizar '
  len(parts): 1
  text.endswith(' '): True
  → Action: Show arguments for 'analizar'  ✓
```

### Checkpoint 2: Completado No Agrega Caracteres
```python
# start_position debe ser:
# - 0 cuando text.endswith(' ')
# - -len(arg_text) cuando hay texto parcial

# Ejemplo correcto:
text = "analizar "
start_position = 0  # No borra nada, agrega después
completion = "Arsenal vs Chelsea"
resultado = "analizar Arsenal vs Chelsea"  ✓

# Ejemplo correcto 2:
text = "analizar Ars"
arg_text = "Ars"
start_position = -3  # Borra "Ars", reemplaza por "Arsenal vs Chelsea"
resultado = "analizar Arsenal vs Chelsea"  ✓
```

### Checkpoint 3: Filtrado Funciona
```python
# Debe coincidir si arg_text está en:
# - event.home_team
# - event.away_team
# - match_str completo

arg_text = "Man"
match_str = "Manchester United vs Liverpool"

if "man" in "manchester united":  # ✓ Coincide
    yield completion
```

---

## 🐛 Debugging

### Si Tab no muestra nada:

1. **Verificar que hay eventos**:
```python
# En CLI
print(f"Events loaded: {len(self.events)}")
# Debe ser > 0 después de 'mercados'
```

2. **Verificar completer tiene referencia**:
```python
# En fetch_markets()
self.command_input.completer.cli_instance = self
print(f"Completer CLI: {self.command_input.completer.cli_instance}")
# No debe ser None
```

3. **Verificar parsing**:
```python
# Agregar prints en get_completions()
print(f"text: '{text}'")
print(f"parts: {parts}")
print(f"endswith space: {text.endswith(' ')}")
```

### Si agrega caracteres extra:

1. **Verificar start_position**:
```python
# Debe ser:
# - 0 cuando no hay texto que reemplazar
# - -len(arg_text) cuando hay texto parcial

# MAL:
start_position = -len(word)  # Si word no es correcto
# BIEN:
start_position = -len(arg_text)  # arg_text = todo después del comando
```

2. **Verificar no hay espacios extra**:
```python
# MAL:
completion = f" {match_str}"  # Espacio al inicio
# BIEN:
completion = match_str  # Sin espacios extra
```

---

## 📊 Casos de Prueba Completos

| Input | len(parts) | endswith(' ') | Acción Esperada |
|-------|------------|---------------|-----------------|
| `""` | 0 | False | Mostrar todos los comandos |
| `"ana"` | 1 | False | Completar comando "ana" → "analizar" |
| `"analizar"` | 1 | False | Completar comando (por si hay más) |
| `"analizar "` | 1 | True | Mostrar TODOS los partidos |
| `"analizar A"` | 2 | False | Filtrar partidos con "A" |
| `"analizar Ars"` | 2 | False | Filtrar partidos con "Ars" |
| `"analizar Arsenal vs Chelsea"` | 4 | False | Filtrar con texto completo |
| `"mercados "` | 1 | True | Mostrar TODOS los sport keys |
| `"mercados soc"` | 2 | False | Filtrar sport keys con "soc" |

---

## ✅ Criterios de Éxito

El autocompletado funciona correctamente si:

- [ ] `ana[Tab]` → `analizar`
- [ ] `analizar [Tab]` → Muestra todos los partidos
- [ ] `analizar Ars[Tab]` → Filtra por "Ars"
- [ ] `mercados [Tab]` → Muestra todos los sport keys
- [ ] `mercados soc[Tab]` → Filtra sport keys
- [ ] ↑/↓ navega historial
- [ ] No agrega caracteres extra
- [ ] No borra más de lo necesario
- [ ] Muestra metadatos (fechas/descripciones)

---

## 🚀 Testing Rápido

```bash
# Opción 1: Script unificado (recomendado)
./run_tests.sh

# Opción 2: Tests individuales

# 1. Test no interactivo (lógica)
python3 bet_copilot/tests/test_completion_debug.py

# 2. Test interactivo (UI)
python3 bet_copilot/tests/test_completion_interactive.py
# Probar: analizar [Tab], analizar Ars[Tab], mercados [Tab]

# 3. Test con mock data
python3 bet_copilot/tests/test_autocompletion.py

# 4. Test real (con API)
python3 main.py
# > mercados
# > analizar [Tab]

# 5. All unit tests
pytest bet_copilot/tests/ -v

# 6. Coverage report
pytest --cov=bet_copilot --cov-report=term-missing bet_copilot/tests/
```

---

**Última actualización**: 2026-01-04  
**Fix aplicado**: v0.5.0  
**Status**: ✅ Corregido y probado
