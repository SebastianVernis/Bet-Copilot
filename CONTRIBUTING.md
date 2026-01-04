# 🤝 Contributing to Bet-Copilot

¡Gracias por tu interés en contribuir a Bet-Copilot!

---

## 📋 Guías Rápidas

### Para Empezar

1. **Fork** el repositorio
2. **Clone** tu fork
3. **Crea** un branch para tu feature
4. **Haz** tus cambios
5. **Testea** tus cambios
6. **Commit** con mensajes claros
7. **Push** a tu fork
8. **Crea** un Pull Request

---

## 🔧 Setup de Desarrollo

```bash
# 1. Clonar
git clone <tu-fork>
cd Bet-Copilot

# 2. Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Instalar deps de desarrollo
pip install -r requirements-dev.txt

# 4. Verificar
python scripts/check_deps.py

# 5. Ejecutar tests
./scripts/run_tests.sh
```

---

## 📝 Convenciones de Código

Ver [**AGENTS.md**](AGENTS.md) para convenciones detalladas.

### Estilo General

```python
# Type hints obligatorios
def calculate_ev(model_prob: float, odds: float) -> float:
    return (model_prob * odds) - 1

# Docstrings en funciones públicas
def predict_match(home_xg: float, away_xg: float) -> Dict[str, float]:
    """
    Predict match outcome using Poisson distribution.
    
    Args:
        home_xg: Expected goals for home team
        away_xg: Expected goals for away team
        
    Returns:
        Dictionary with probabilities
    """
    pass

# Usar dataclasses
@dataclass
class MatchPrediction:
    home_team: str
    away_team: str
    home_win_prob: float
```

### Naming

```python
# Variables: snake_case
home_lambda = 1.8

# Clases: PascalCase
class CircuitBreaker: pass

# Constantes: UPPER_SNAKE_CASE
CIRCUIT_BREAKER_TIMEOUT = 60

# Privados: prefijo _
def _internal_helper(): pass
```

---

## 🧪 Testing

### Requisitos

- **Todos los nuevos features** deben tener tests
- **Mínimo 3 test cases** por función pública
- **Coverage >80%** para nuevos módulos

### Ejecutar Tests

```bash
# Todos los tests
./scripts/run_tests.sh

# Solo tus nuevos tests
pytest bet_copilot/tests/test_mi_modulo.py -v

# Con coverage
pytest --cov=bet_copilot/mi_modulo bet_copilot/tests/test_mi_modulo.py -v
```

### Escribir Tests

```python
import pytest

class TestMiFeature:
    """Test suite for mi feature."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return MiClase()
    
    def test_basic_functionality(self, instance):
        """Test basic use case."""
        result = instance.do_something()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_async_function(self, instance):
        """Test async functionality."""
        result = await instance.async_method()
        assert result == expected
```

---

## 📚 Documentación

### Requisitos

- **README actualizado** si cambias features principales
- **Docstrings** en todas las funciones públicas
- **Type hints** en todos los parámetros
- **Ejemplos** de uso si es feature compleja

### Estructura de Docs

```
docs/
├── guides/         # Guías de usuario
├── api/            # Documentación de APIs
├── development/    # Docs para desarrolladores
└── ...
```

### Actualizar Docs

Si tu feature es grande:
1. Crear `docs/MI_FEATURE.md`
2. Actualizar `INDICE_DOCUMENTACION.md`
3. Agregar entrada en `CHANGELOG.md`

---

## 🔀 Git Workflow

### Branches

```bash
# Feature
git checkout -b feature/nombre-descriptivo

# Bug fix
git checkout -b fix/descripcion-del-bug

# Docs
git checkout -b docs/que-documenta
```

### Commits

**Formato**:
```
tipo: descripción breve

Descripción detallada (opcional)
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `test`: Agregar/modificar tests
- `refactor`: Refactoring de código
- `style`: Cambios de formato (no afectan lógica)
- `chore`: Tareas de mantenimiento

**Ejemplos**:
```bash
git commit -m "feat: add simple analyzer for AI fallback"
git commit -m "fix: correct gemini model name to gemini-pro"
git commit -m "docs: add coverage report analysis"
git commit -m "test: add 23 tests for football fallback"
```

### Pull Requests

**Template**:
```markdown
## Descripción
Breve descripción de los cambios

## Tipo de Cambio
- [ ] Nueva feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentación

## Checklist
- [ ] Tests agregados/actualizados
- [ ] Docs actualizadas
- [ ] Coverage >80% en nuevos módulos
- [ ] Lint passing
- [ ] Tests passing (./scripts/run_tests.sh)

## Screenshots (si aplica)
```

---

## 🎯 Áreas de Contribución

### 🟢 Buenas para Empezar

- Agregar más equipos a tier detection
- Mejorar documentación
- Agregar ejemplos de uso
- Traducir docs a inglés
- Arreglar typos

### 🟡 Nivel Intermedio

- Implementar nuevos proveedores AI
- Agregar más sport keys
- Mejorar heurísticas de SimpleAnalyzer
- Agregar más tests
- Mejorar coverage

### 🔴 Nivel Avanzado

- Implementar web scraping de stats
- Machine learning para tier detection
- Circuit breaker avanzado
- Optimización de performance
- Docker containerization
- CI/CD setup

---

## 🐛 Reportar Bugs

### Template de Issue

```markdown
**Descripción del Bug**
Descripción clara del problema

**Pasos para Reproducir**
1. Ejecutar comando X
2. Hacer Y
3. Ver error Z

**Comportamiento Esperado**
Qué debería pasar

**Comportamiento Actual**
Qué pasa realmente

**Ambiente**
- OS: [Ubuntu 22.04 / macOS 13 / Windows 11]
- Python: [3.10.5]
- Versión: [0.5.2]

**Logs**
```
Incluir logs relevantes
```

**Screenshots** (si aplica)
```

---

## 💡 Sugerir Features

### Template de Feature Request

```markdown
**Descripción de la Feature**
¿Qué quieres que se implemente?

**Problema que Resuelve**
¿Qué problema soluciona?

**Solución Propuesta**
¿Cómo lo implementarías?

**Alternativas Consideradas**
¿Hay otras formas de resolverlo?

**Contexto Adicional**
Cualquier info extra
```

---

## 🔍 Code Review

### Criterios

Tu PR será revisado considerando:

- ✅ **Funcionalidad**: ¿Funciona correctamente?
- ✅ **Tests**: ¿Tiene tests adecuados?
- ✅ **Docs**: ¿Está documentado?
- ✅ **Estilo**: ¿Sigue las convenciones?
- ✅ **Performance**: ¿Es eficiente?
- ✅ **Seguridad**: ¿No introduce vulnerabilidades?

### Proceso

1. Automated checks (cuando CI/CD esté configurado)
2. Code review por maintainer
3. Sugerencias de cambios (si necesario)
4. Aprobación
5. Merge a main

---

## 📊 Métricas de Calidad

### Requisitos Mínimos

```
Tests passing:     >95%
Coverage (nuevo):  >80%
Lint errors:       0
Type hints:        100%
Docstrings:        100% (funciones públicas)
```

### Herramientas

```bash
# Linter
flake8 bet_copilot/

# Type checker
mypy bet_copilot/

# Formatter
black bet_copilot/

# Tests
pytest bet_copilot/tests/ -v
```

---

## 🙏 Reconocimientos

Los contribuidores serán reconocidos en:
- `CONTRIBUTORS.md`
- Release notes
- Changelog

---

## 📞 Contacto

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions (futuro)
- **Docs**: Ver INDICE_DOCUMENTACION.md

---

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo MIT License.

---

**¡Gracias por contribuir a Bet-Copilot!** 🎉
