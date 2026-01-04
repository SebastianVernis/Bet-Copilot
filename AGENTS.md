# AGENTS.md - Guía para Agentes IA

Documentación técnica para que cualquier agente IA (Cursor, GitHub Copilot, Claude, etc.) trabaje efectivamente en este repositorio.

---

## 📋 Información Esencial del Proyecto

### Nombre
**Bet-Copilot** - Sistema de especulación deportiva con CLI/TUI

### Stack Tecnológico
```
Lenguaje:     Python 3.10+
UI:           Rich, Textual (terminal)
Persistencia: SQLite (aiosqlite)
Concurrency:  asyncio
APIs:         The Odds API, API-Football, Gemini
Testing:      pytest, pytest-asyncio
```

### Filosofía
- **"Copiloto", no bot**: El sistema informa, el usuario decide
- **Transparencia total**: Todas las predicciones son explicables matemáticamente
- **Rate limit conscious**: Circuit breakers en todas las APIs
- **No garantías**: Vocabulario cuidadoso (especulación, valor esperado, no "ganancias")

---

## 🏗️ Arquitectura del Sistema

### Flujo Principal
```
User Input → Odds API → Math Engine → AI Filter → Dashboard → Manual Execution
```

**Detalle**:
1. **Extracción de datos**: APIs (cuotas + estadísticas)
2. **Motor matemático**: Poisson + Monte Carlo para probabilidades
3. **Filtro IA**: Gemini analiza contexto (lesiones, sentimiento)
4. **Estrategia**: Criterio de Kelly para sizing
5. **Dashboard**: Rich TUI muestra información
6. **Usuario**: Ejecuta apuesta manualmente

### Módulos Implementados (95%)

```
bet_copilot/
├── api/                    ✅ Clientes de APIs
│   ├── circuit_breaker.py      - Pattern de protección
│   ├── odds_client.py          - Cliente The Odds API
│   └── football_client.py      - Cliente API-Football (NUEVO v0.4)
├── ai/                     ✅ Inteligencia Artificial
│   └── gemini_client.py        - Cliente Gemini AI (NUEVO v0.3)
├── db/                     ✅ Persistencia
│   ├── schema.sql              - DDL SQLite
│   └── odds_repository.py      - CRUD + cache
├── math_engine/            ✅ Motor estadístico
│   ├── poisson.py              - Distribución de Poisson
│   ├── soccer_predictor.py     - Predictor de fútbol
│   └── kelly.py                - Kelly Criterion (NUEVO v0.3)
├── models/                 ✅ Modelos de datos
│   ├── odds.py                 - Cuotas y eventos
│   └── soccer.py               - Stats de fútbol (xG, form)
├── services/               ✅ Orquestadores
│   ├── odds_service.py         - Integra API + breaker + repo
│   └── match_analyzer.py       - Análisis completo (NUEVO v0.4)
├── ui/                     ✅ Interfaz terminal
│   ├── dashboard.py            - Dashboard 4 zonas (NUEVO v0.3)
│   └── styles.py               - Paleta neón
├── tests/                  ✅ 30 tests (100% passing)
├── cli.py                  ✅ CLI interactivo (NUEVO v0.3)
└── config.py               ✅ Configuración
```

---

## 🔧 Comandos Esenciales

### Instalación
```bash
# Desde raíz del proyecto
pip install -r requirements.txt
cp .env.example .env
# Editar .env con API keys
```

### Ejecución
```bash
# CLI principal (RECOMENDADO)
python main.py

# O con script de inicio
./START.sh

# Demos específicos:
python example_enhanced_analysis.py  # Demo análisis v0.4 (NUEVO)
python example_soccer_prediction.py  # Demo predictor Poisson
python demo_market_watch_simple.py   # Demo UI Rich
python example_usage.py              # Demo cliente APIs
```

### Testing
```bash
# Todos los tests
pytest bet_copilot/tests/ -v

# Solo un módulo
pytest bet_copilot/tests/test_poisson.py -v

# Con coverage
pytest --cov=bet_copilot bet_copilot/tests/
```

### Base de Datos
```bash
# Inspeccionar SQLite
sqlite3 bet_copilot.db

# Ver últimas peticiones
sqlite3 bet_copilot.db "SELECT * FROM api_requests ORDER BY timestamp DESC LIMIT 10;"

# Ver estado del circuit breaker
sqlite3 bet_copilot.db "SELECT * FROM circuit_breaker_events ORDER BY timestamp DESC LIMIT 10;"
```

---

## 📝 Convenciones de Código

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
        Dictionary with probabilities: {home_win, draw, away_win}
    """
    pass

# Usar dataclasses para modelos
@dataclass
class MatchPrediction:
    home_team: str
    away_team: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
```

### Naming Conventions
```python
# Variables y funciones: snake_case
home_lambda = 1.8
def calculate_poisson_probability(): pass

# Clases: PascalCase
class CircuitBreaker: pass
class OddsAPIClient: pass

# Constantes: UPPER_SNAKE_CASE
CIRCUIT_BREAKER_TIMEOUT = 60
NEON_GREEN = "#39FF14"

# Privados: prefijo _
def _internal_helper(): pass
self._state = CircuitState.CLOSED
```

### Async/Await
```python
# Siempre usar async para I/O
async def fetch_odds(sport_key: str) -> List[OddsEvent]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Repository siempre async
async def save_odds(self, event: OddsEvent) -> int:
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute(query, params)
        await db.commit()
```

### Error Handling
```python
# Excepciones específicas
class RateLimitError(OddsAPIError):
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.status = 429
        self.retry_after = retry_after

# Logging estructurado
logger.info(f"Fetched {len(events)} odds for {sport_key}")
logger.error(f"Rate limit exceeded. Retry after {retry_after}s")

# Try-except específico
try:
    result = await api_call()
except RateLimitError as e:
    # Circuit breaker se encarga
    await self.circuit_breaker.manual_open()
    raise
except asyncio.TimeoutError:
    # Retry con backoff
    await asyncio.sleep(BACKOFF_FACTOR ** retry_count)
```

---

## 🎨 Estilo UI (Rich)

### Paleta de Colores
```python
# Colores neón (hex)
NEON_GREEN  = "#39FF14"  # Éxito, EV positivo alto
NEON_YELLOW = "#FFFF00"  # Warning, EV positivo bajo
NEON_CYAN   = "#00FFFF"  # Info, equipo local
NEON_PINK   = "#FF10F0"  # Equipo visitante
NEON_PURPLE = "#9D00FF"  # Títulos
NEON_RED    = "#FF073A"  # Error, EV negativo
LIGHT_GRAY  = "#CCCCCC"  # Texto secundario

# Uso en Rich
from rich.text import Text
text = Text("Valor positivo", style=f"bold {NEON_GREEN}")
```

### Tablas
```python
# Usar MINIMAL para bordes limpios
table = Table(
    box=MINIMAL,
    border_style=LIGHT_GRAY,
    header_style=f"bold {NEON_CYAN}",
)

# Columnas con ancho fijo para responsive
table.add_column("Match", width=25, justify="left")
table.add_column("EV", width=8, justify="right")
```

---

## 🧮 Motor Matemático

### Distribución de Poisson
```python
# Fórmula base
P(X = k) = (λ^k × e^-λ) / k!

# Implementación
@staticmethod
def probability(k: int, lambda_: float) -> float:
    if lambda_ <= 0:
        return 1.0 if k == 0 else 0.0
    
    numerator = (lambda_ ** k) * math.exp(-lambda_)
    denominator = factorial(k)
    return numerator / denominator
```

### Cálculo de Lambda (Expected Goals)
```python
# Para equipo local
lambda_home = (
    home_team.avg_xg_for(home_only=True) +
    away_team.avg_xg_against(away_only=True)
) / 2 * home_advantage_factor

# Para equipo visitante
lambda_away = (
    away_team.avg_xg_for(away_only=True) +
    home_team.avg_xg_against(home_only=True)
) / 2
```

### Expected Value (EV)
```python
# Fórmula
EV = (P_modelo × Odds) - 1

# Ejemplo
model_prob = 0.55  # 55%
odds = 2.10        # Bookmaker
ev = (0.55 * 2.10) - 1 = 0.155  # +15.5% EV

# Threshold para "value bet"
if ev >= 0.05:  # ≥5%
    return "HIGH_VALUE"
```

---

## 🔐 Secrets & Config

### Variables de Entorno
```bash
# .env (nunca commitear)
ODDS_API_KEY=your_key_here
API_FOOTBALL_KEY=your_key_here
GEMINI_API_KEY=your_key_here
LOG_LEVEL=INFO
```

### Config Centralizado
```python
# bet_copilot/config.py
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
CIRCUIT_BREAKER_TIMEOUT = 60
MAX_CONCURRENT_REQUESTS = 3
CACHE_TTL_LIVE = 300  # 5 minutos
```

---

## 🚨 Gotchas & Edge Cases

### 1. Circuit Breaker
```python
# ❌ NO hacer
while circuit_breaker.is_open:
    await asyncio.sleep(1)  # Bloquea todo

# ✅ Hacer
try:
    result = await circuit_breaker.call(api_call)
except CircuitBreakerError:
    # Retornar cache o informar al usuario
    return cached_data
```

### 2. SQLite + Asyncio
```python
# ❌ NO usar sqlite3 directamente (bloqueante)
import sqlite3
conn = sqlite3.connect("db.db")  # Bloquea event loop

# ✅ Usar aiosqlite
import aiosqlite
async with aiosqlite.connect("db.db") as db:
    await db.execute(query)
```

### 3. Probabilidades que no suman 1.0
```python
# Siempre validar
total = home_win + draw + away_win
assert 0.99 <= total <= 1.01, f"Probabilities sum to {total}"

# En Poisson, suma puede ser <1.0 si max_goals es bajo
# Usar max_goals=8 mínimo para >99% coverage
```

### 4. Odds Extremas
```python
# Odds <1.01 → Kelly puede recomendar >100% bankroll
# Limitar siempre
if odds < 1.01:
    logger.warning(f"Odds too low: {odds}")
    return 0.0  # No apostar

# Odds >100 → Probabilidad implícita <1%
# Validar que modelo esté confiado
if odds > 100 and model_prob < 0.05:
    logger.warning("High odds but low model probability")
```

### 5. Rate Limits de APIs
```python
# The Odds API: 500 requests/mes (plan gratuito)
# ≈ 16 requests/día
# Usar cache agresivamente
CACHE_TTL_UPCOMING = 1800  # 30 min para eventos futuros

# API-Football: 30 requests/min, 100/día
# Implementar queue con rate limiter
```

---

## 📊 Estructura de Datos Clave

### OddsEvent
```python
@dataclass
class OddsEvent:
    id: str
    sport_key: str
    home_team: str
    away_team: str
    commence_time: datetime
    bookmakers: List[Bookmaker]  # Múltiples casas
```

### MatchPrediction
```python
@dataclass
class MatchPrediction:
    home_team: str
    away_team: str
    home_lambda: float       # Expected goals
    away_lambda: float
    home_win_prob: float     # Probabilidades
    draw_prob: float
    away_win_prob: float
    most_likely_score: tuple[int, int]
    expected_total_goals: float
    # Opcionales
    over_under_2_5: Dict[str, float]
    btts: Dict[str, float]
```

### MockMarket (para UI)
```python
@dataclass
class MockMarket:
    home_team: str
    away_team: str
    market_type: str        # "Home Win", "Over 2.5", etc.
    model_prob: float       # De nuestro modelo
    odds: float             # Del bookmaker
    ev: float               # Expected Value calculado
    bookmaker: str
    home_lambda: float
    away_lambda: float
```

---

## 🔍 Debugging Tips

### Activar logs detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("bet_copilot")
```

### Inspeccionar SQLite
```bash
# Ver esquema
sqlite3 bet_copilot.db ".schema"

# Últimas odds cacheadas
sqlite3 bet_copilot.db "SELECT event_id, home_team, away_team, fetched_at FROM odds_data ORDER BY fetched_at DESC LIMIT 5;"

# Rate limit hits
sqlite3 bet_copilot.db "SELECT COUNT(*) FROM api_requests WHERE status_code = 429;"
```

### Probar componentes en aislamiento
```python
# Circuit Breaker
from bet_copilot.api.circuit_breaker import CircuitBreaker

async def test_func():
    return "success"

breaker = CircuitBreaker(timeout=5)
result = await breaker.call(test_func)

# Poisson
from bet_copilot.math_engine.poisson import PoissonCalculator

calc = PoissonCalculator()
prob = calc.probability(k=2, lambda_=1.5)
print(f"P(2 goals | λ=1.5) = {prob:.3f}")  # ~0.251
```

---

## 📚 Referencias Importantes

### Papers
- **Dixon-Coles (1997)**: "Modelling Association Football Scores and Inefficiencies in the Football Betting Market"
- **Kelly (1956)**: "A New Interpretation of Information Rate"

### Documentación Externa
- **The Odds API**: https://the-odds-api.com/
- **Rich (UI)**: https://rich.readthedocs.io/
- **aiosqlite**: https://aiosqlite.omnilib.dev/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/

### Métricas de Fútbol
- **xG (Expected Goals)**: Probabilidad de que un tiro resulte en gol
- **xGA (Expected Goals Against)**: xG concedidos por la defensa
- **Form**: Últimos 5 resultados (W/D/L)

---

## ✅ Checklist para Nuevas Features

Antes de considerar una feature completa:

- [ ] Código implementado con type hints
- [ ] Docstrings en funciones públicas
- [ ] Error handling apropiado (try-except específico)
- [ ] Logging en puntos clave
- [ ] Tests unitarios (≥3 casos)
- [ ] Integración con componentes existentes verificada
- [ ] Documentación actualizada (README o este archivo)
- [ ] Sin hardcoded values (usar config.py)
- [ ] Manejo de rate limits (si aplica)
- [ ] Validaciones de input

---

## 🎯 Próximas Prioridades

Según roadmap del proyecto:

1. **API-Football Client** (pendiente)
   - Patrón similar a OddsAPIClient
   - Endpoints: fixtures, h2h, team stats

2. **Kelly Calculator** (pendiente)
   - Fórmula: f* = (p × b - q) / b
   - Modos: full Kelly, 1/2 Kelly, 1/4 Kelly

3. **Gemini Integration** (pendiente)
   - Análisis de noticias (lesiones, suspensiones)
   - Ajuste de lambdas según contexto

4. **Dashboard 4 Zonas** (pendiente)
   - Zona A: API Health
   - Zona B: Active Tasks
   - Zona C: Market Watch (implementada)
   - Zona D: System Logs

---

**Última actualización**: 2026-01-04  
**Proyecto**: Bet-Copilot v0.2.0  
**Autor**: Documentación generada para agentes IA
