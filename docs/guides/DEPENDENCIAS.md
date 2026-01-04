# 📦 Gestión de Dependencias - Bet-Copilot

## 📋 Archivos de Dependencias

### 1. requirements.txt (Producción)
**Ubicación**: `/Bet-Copilot/requirements.txt`

**Contenido**: Dependencias mínimas para ejecutar la aplicación.

```bash
# Instalar
pip install -r requirements.txt

# O con el script
./INSTALL_DEPS.sh
```

**Incluye**:
- `aiohttp` - HTTP async
- `aiosqlite` - Database async
- `pytest` + `pytest-asyncio` + `pytest-cov` - Testing
- `rich` - UI terminal
- `textual` - Dashboard
- `prompt_toolkit` - Input avanzado
- `google-generativeai` - Gemini AI
- `python-dotenv` - Variables de entorno

---

### 2. requirements-dev.txt (Desarrollo)
**Ubicación**: `/Bet-Copilot/requirements-dev.txt`

**Contenido**: Dependencias adicionales para desarrollo.

```bash
# Instalar (incluye requirements.txt)
pip install -r requirements-dev.txt
```

**Incluye**:
- `black` - Formatter
- `flake8` - Linter
- `mypy` - Type checker
- `isort` - Import sorter
- `pytest-mock` - Mocking
- `pytest-xdist` - Parallel testing
- `ipython` - REPL mejorado
- `sphinx` - Documentación

---

## 🚀 Instalación

### Opción 1: Script Automático
```bash
./INSTALL_DEPS.sh
```

Detecta automáticamente:
- Virtual environment
- Permisos
- Sistema operativo

### Opción 2: Manual (Producción)
```bash
# Con virtual environment (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Opción 3: Manual (Desarrollo)
```bash
# Activar venv primero
source venv/bin/activate

# Instalar todo
pip install -r requirements-dev.txt
```

### Opción 4: Usuario Local
```bash
# Sin permisos de admin
pip install --user -r requirements.txt
```

---

## 🔍 Verificar Instalación

### Check Básico
```bash
python3 -c "import aiohttp, rich, pytest; print('✓ OK')"
```

### Check Completo
```bash
# Crear script de verificación
cat > check_deps.py << 'EOF'
import sys

deps = [
    'aiohttp',
    'aiosqlite',
    'rich',
    'textual',
    'prompt_toolkit',
    'google.generativeai',
    'pytest',
    'pytest_asyncio',
    'pytest_cov',
    'dotenv',
]

missing = []
for dep in deps:
    try:
        __import__(dep.replace('.', '_'))
        print(f"✓ {dep}")
    except ImportError:
        print(f"✗ {dep}")
        missing.append(dep)

if missing:
    print(f"\n❌ Faltan {len(missing)} dependencias")
    print("Instalar con: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✅ Todas las dependencias instaladas")
EOF

python3 check_deps.py
```

---

## ❌ Error: pytest-cov no encontrado

### Síntomas
```
pytest: error: unrecognized arguments: --cov=bet_copilot
```

### Solución 1: Instalar pytest-cov
```bash
pip install pytest-cov

# O reinstalar todo
pip install -r requirements.txt
```

### Solución 2: Usar run_tests.sh
```bash
./run_tests.sh
# Opción 7: Coverage Report
# → Detecta automáticamente si está instalado
```

El script ahora maneja automáticamente la ausencia de `pytest-cov`:
- Si está instalado: genera reporte de coverage
- Si no está instalado: ejecuta tests sin coverage

---

## 🔧 Dependencias Opcionales

### pytest-cov (Coverage)
```bash
pip install pytest-cov

# Uso
pytest --cov=bet_copilot --cov-report=html bet_copilot/tests/
# Abre htmlcov/index.html
```

### black (Formatter)
```bash
pip install black

# Uso
black bet_copilot/
```

### mypy (Type Checker)
```bash
pip install mypy

# Uso
mypy bet_copilot/
```

---

## 📊 Gestión de Versiones

### Ver versiones instaladas
```bash
pip list | grep -E "(aiohttp|rich|pytest|prompt_toolkit)"
```

### Actualizar dependencias
```bash
# Actualizar todas
pip install -r requirements.txt --upgrade

# Actualizar una específica
pip install --upgrade pytest-cov
```

### Congelar versiones (lockfile)
```bash
pip freeze > requirements.lock

# Instalar desde lockfile
pip install -r requirements.lock
```

---

## 🐳 Docker (Futuro)

### Dockerfile (ejemplo)
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

---

## 📝 Notas por Sistema Operativo

### Linux (Ubuntu/Debian)
```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-venv python3-pip

# Luego instalar Python packages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### macOS
```bash
# Con Homebrew
brew install python3

# Luego igual que Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
```powershell
# Con Python installer desde python.org
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔗 Links Útiles

- [pip documentation](https://pip.pypa.io/)
- [venv documentation](https://docs.python.org/3/library/venv.html)
- [requirements.txt format](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

---

## 📋 Checklist de Setup

- [ ] Python 3.10+ instalado
- [ ] pip actualizado (`pip install --upgrade pip`)
- [ ] Virtual environment creado
- [ ] Virtual environment activado
- [ ] `requirements.txt` instalado
- [ ] Dependencias verificadas (`check_deps.py`)
- [ ] `.env` configurado (copiar desde `.env.example`)
- [ ] Tests ejecutables (`pytest bet_copilot/tests/ -v`)

---

**Última actualización**: 2026-01-04  
**Versión**: 0.5.0
