# 🧪 Tests - Bet-Copilot

Guía rápida de testing para el proyecto.

## 📁 Estructura

```
bet_copilot/tests/
├── __init__.py
├── test_poisson.py                    # Distribución de Poisson
├── test_kelly.py                      # Kelly Criterion
├── test_soccer_predictor.py           # Predictor de fútbol
├── test_circuit_breaker.py            # Circuit breaker
├── test_gemini_client.py              # Cliente Gemini AI
├── test_football_client.py            # Cliente API-Football
├── test_match_analyzer.py             # Análisis de partidos
├── test_command_input.py              # Input básico (interactivo)
├── test_autocompletion.py             # Autocompletado con mock (interactivo)
├── test_completion_debug.py           # Lógica de completado (no interactivo)
└── test_completion_interactive.py     # Test completo de UI (interactivo)
```

**Total**: 11 tests (7 unit tests + 4 interactive tests)

---

## 🚀 Ejecutar Tests

### Opción 1: Script Unificado (Recomendado)

```bash
./run_tests.sh
```

**Menú interactivo**:
```
Tests Disponibles:
  [1] All Tests (pytest)
  [2] Unit Tests (core functionality)
  [3] Command Input Tests (interactive)
  [4] Completion Debug (logic only)
  [5] Completion Interactive (full UI)
  [6] Autocompletion with Mock Data
  [7] Coverage Report
  [0] Exit
```

### Opción 2: Pytest Directamente

```bash
# Todos los tests
pytest bet_copilot/tests/ -v

# Test específico
pytest bet_copilot/tests/test_poisson.py -v

# Con coverage
pytest --cov=bet_copilot --cov-report=term-missing bet_copilot/tests/

# Solo core tests (matemáticos)
pytest bet_copilot/tests/test_poisson.py \
       bet_copilot/tests/test_kelly.py \
       bet_copilot/tests/test_soccer_predictor.py -v
```

### Opción 3: Tests Individuales

```bash
# Tests no interactivos (pueden ejecutarse en CI/CD)
python bet_copilot/tests/test_completion_debug.py

# Tests interactivos (requieren terminal)
python bet_copilot/tests/test_command_input.py
python bet_copilot/tests/test_autocompletion.py
python bet_copilot/tests/test_completion_interactive.py
```

---

## 📊 Tipos de Tests

### 1. Unit Tests (Pytest)

**Archivo**: `test_poisson.py`, `test_kelly.py`, etc.

**Ejecución**:
```bash
pytest bet_copilot/tests/test_poisson.py -v
```

**Características**:
- No interactivos
- Ejecutables en CI/CD
- Assertions estándar
- Fixtures de pytest

**Ejemplo**:
```python
def test_poisson_probability():
    calc = PoissonCalculator()
    prob = calc.probability(k=2, lambda_=1.5)
    assert 0.20 < prob < 0.30
```

### 2. Interactive Tests

**Archivos**: `test_command_input.py`, `test_autocompletion.py`, `test_completion_interactive.py`

**Ejecución**:
```bash
python bet_copilot/tests/test_command_input.py
```

**Características**:
- Requieren terminal interactivo
- Usan `prompt_toolkit`
- Verificación manual por el usuario
- No ejecutables en CI/CD

**Ejemplo de uso**:
```
➜ bet-copilot mer[Tab]
→ mercados
➜ bet-copilot analizar [Tab]
  • Arsenal vs Chelsea
  • Manchester United vs Liverpool
```

### 3. Debug Tests

**Archivo**: `test_completion_debug.py`

**Ejecución**:
```bash
python bet_copilot/tests/test_completion_debug.py
```

**Características**:
- No interactivo
- Verifica lógica de parsing
- Output detallado para debugging
- Ejecutable en cualquier entorno

**Output esperado**:
```
Input: 'analizar '
  len(parts): 1
  text.endswith(' '): True
  → Action: Show arguments for 'analizar'  ✓
```

---

## 🎯 Tests por Funcionalidad

### Core Math Engine
```bash
pytest bet_copilot/tests/test_poisson.py \
       bet_copilot/tests/test_kelly.py \
       bet_copilot/tests/test_soccer_predictor.py -v
```

### API Clients
```bash
pytest bet_copilot/tests/test_circuit_breaker.py \
       bet_copilot/tests/test_football_client.py -v
```

### AI & Analysis
```bash
pytest bet_copilot/tests/test_gemini_client.py \
       bet_copilot/tests/test_match_analyzer.py -v
```

### Command Input & UI
```bash
# Non-interactive
python bet_copilot/tests/test_completion_debug.py

# Interactive
python bet_copilot/tests/test_command_input.py
python bet_copilot/tests/test_autocompletion.py
python bet_copilot/tests/test_completion_interactive.py
```

---

## 📈 Coverage

### Generar reporte de coverage
```bash
pytest --cov=bet_copilot --cov-report=html bet_copilot/tests/
```

Abre `htmlcov/index.html` en el navegador.

### Coverage actual
```
Module                        Coverage
──────────────────────────────────────
bet_copilot/math_engine/       ~95%
bet_copilot/api/               ~85%
bet_copilot/services/          ~90%
bet_copilot/ai/                ~70%
bet_copilot/ui/                ~60%
──────────────────────────────────────
Total                          ~85%
```

---

## ✅ Checklist de Testing

Antes de hacer commit/push:

- [ ] `pytest bet_copilot/tests/ -v` pasa
- [ ] Coverage >80%
- [ ] Tests interactivos verificados manualmente
- [ ] No hay prints/debugs olvidados
- [ ] Documentación actualizada

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'prompt_toolkit'"
```bash
pip install prompt_toolkit
# o
./INSTALL_DEPS.sh
```

### "ModuleNotFoundError: No module named 'bet_copilot'"
```bash
# Ejecutar desde raíz del proyecto
cd /path/to/Bet-Copilot
pytest bet_copilot/tests/ -v
```

### Tests interactivos no funcionan en SSH
Los tests interactivos requieren terminal real con soporte para:
- Colores ANSI
- Entrada interactiva (stdin)
- Prompt rendering

**Solución**: Ejecutar localmente o usar `tmux`/`screen`.

### Pytest no encuentra tests
```bash
# Verificar que __init__.py existe
ls bet_copilot/tests/__init__.py

# Verificar que pytest está instalado
pytest --version
```

---

## 📚 Documentación Adicional

- **TESTING_GUIDE.md**: Guía detallada de testing de autocompletado
- **README_COMMAND_INPUT.md**: Documentación del sistema de input
- **RESUMEN_CAMBIOS.md**: Changelog v0.5.0

---

## 🔗 Links Útiles

- [pytest docs](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/)

---

**Última actualización**: 2026-01-04  
**Versión**: 0.5.0  
**Tests totales**: 11 (7 unit + 4 interactive)
