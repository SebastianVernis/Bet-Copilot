# Instalación y Uso de Bet-Copilot

## Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Claves API (opcionales para funcionalidad completa)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd Bet-Copilot
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar `.env` con tus API keys:

```bash
# API Keys (obtener en los respectivos sitios)
ODDS_API_KEY=tu_clave_aqui
API_FOOTBALL_KEY=tu_clave_aqui
GEMINI_API_KEY=tu_clave_aqui

# Configuración
LOG_LEVEL=INFO
```

## Obtener API Keys

### The Odds API (Requerido)
1. Ir a: https://the-odds-api.com/
2. Crear cuenta gratuita (500 requests/mes)
3. Copiar API key al `.env`

### API-Football (Opcional)
1. Ir a: https://www.api-football.com/
2. Crear cuenta gratuita (100 requests/día)
3. Copiar API key al `.env`

### Gemini AI (Opcional)
1. Ir a: https://makersuite.google.com/app/apikey
2. Crear API key gratuita
3. Copiar al `.env`

## Uso

### Ejecutar CLI Interactivo

```bash
python main.py
```

O directamente:

```bash
python -m bet_copilot.cli
```

### Comandos Disponibles

Una vez en el CLI:

```
bet-copilot> help          # Ver ayuda
bet-copilot> health        # Verificar APIs
bet-copilot> markets       # Ver mercados disponibles
bet-copilot> dashboard     # Mostrar dashboard completo
bet-copilot> quit          # Salir
```

### Ejemplos de Uso

#### Verificar Salud de APIs

```bash
bet-copilot> health
```

#### Ver Mercados de Premier League

```bash
bet-copilot> markets soccer_epl
```

#### Mostrar Dashboard

```bash
bet-copilot> dashboard
```

## Scripts de Demostración

El proyecto incluye varios scripts de demostración:

### Demo de Predicción (Poisson)

```bash
python example_soccer_prediction.py
```

### Demo de UI (Market Watch)

```bash
python demo_market_watch_simple.py
```

### Demo de Cliente de APIs

```bash
python example_usage.py
```

## Tests

### Ejecutar Todos los Tests

```bash
pytest bet_copilot/tests/ -v
```

### Tests Específicos

```bash
# Solo Kelly Criterion
pytest bet_copilot/tests/test_kelly.py -v

# Solo Gemini
pytest bet_copilot/tests/test_gemini_client.py -v

# Con coverage
pytest --cov=bet_copilot bet_copilot/tests/
```

## Estructura del Proyecto

```
Bet-Copilot/
├── bet_copilot/          # Código principal
│   ├── api/              # Clientes de APIs
│   ├── ai/               # Integración Gemini
│   ├── db/               # Persistencia SQLite
│   ├── math_engine/      # Poisson + Kelly
│   ├── models/           # Modelos de datos
│   ├── services/         # Lógica de negocio
│   ├── ui/               # Interfaz terminal
│   ├── cli.py            # CLI principal
│   └── config.py         # Configuración
├── scripts/              # Scripts auxiliares
├── tests/                # Tests unitarios
├── main.py               # Punto de entrada
└── requirements.txt      # Dependencias
```

## Solución de Problemas

### Error: "Module not found"

```bash
# Verificar que estás en el entorno virtual
which python
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "API key not configured"

```bash
# Verificar que .env existe y tiene las claves
cat .env
# Asegurarse que las variables están cargadas
export $(cat .env | xargs)  # Linux/Mac
```

### Error: "Circuit breaker is open"

Las APIs tienen límites de requests. Espera unos minutos o verifica tu quota:

```bash
# Ver estado del circuit breaker
bet-copilot> health
```

### Tests Fallan

```bash
# Verificar instalación completa
pip install -r requirements.txt
# Limpiar cache
rm -rf __pycache__ bet_copilot/__pycache__
# Re-ejecutar
pytest bet_copilot/tests/ -v
```

## Base de Datos

Bet-Copilot usa SQLite para caché. El archivo se crea automáticamente:

```bash
# Ubicación
./bet_copilot.db

# Inspeccionar (requiere sqlite3)
sqlite3 bet_copilot.db
> .tables
> SELECT * FROM odds_data LIMIT 5;
```

Para limpiar el caché:

```bash
rm bet_copilot.db
```

## Modo de Desarrollo

### Activar Logs Detallados

Editar `.env`:

```bash
LOG_LEVEL=DEBUG
```

### Ejecutar con Auto-reload (Requiere watchdog)

```bash
pip install watchdog
watchmedo auto-restart -d bet_copilot -p '*.py' -- python main.py
```

## Limitaciones Conocidas

### Plan Gratuito

- **The Odds API**: 500 requests/mes (~16/día)
- **API-Football**: 100 requests/día
- **Gemini**: Límites generosos pero variables

### Workarounds

El sistema usa **cache agresivo** para minimizar requests:
- Eventos futuros: 30 min TTL
- Datos históricos: 24 hrs TTL
- Circuit breaker protege contra rate limits

## Próximos Pasos

1. Explorar comandos en el CLI
2. Verificar salud de APIs (`health`)
3. Ver mercados disponibles (`markets`)
4. Experimentar con predicciones
5. Revisar documentación en `AGENTS.md` para desarrollo

## Soporte

- **Documentación**: Ver `README.md`, `AGENTS.md`
- **Issues**: Reportar en GitHub
- **Contribuir**: Ver `AGENTS.md` para convenciones

---

**Última actualización**: 2026-01-04  
**Versión**: 0.3.0
