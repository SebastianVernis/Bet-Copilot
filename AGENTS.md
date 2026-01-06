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
User Input → News Feed → Odds API → Math Engine → Multi-AI Analysis → Dashboard → Manual Execution
```

**Detalle**:
1. **News Aggregation**: RSS feeds gratuitos (BBC, ESPN) - NO API CALLS
2. **Extracción de datos**: APIs (cuotas + estadísticas detalladas)
3. **Motor matemático**: Poisson para mercados tradicionales + alternativos
4. **Análisis colaborativo**: Gemini + Blackbox trabajan juntos (si ambos disponibles)
5. **Estrategia**: Criterio de Kelly para sizing
6. **Dashboard**: Rich TUI muestra información multi-dimensional
7. **Usuario**: Ejecuta apuesta manualmente

### Módulos Implementados (100%)

```
bet_copilot/
├── api/                    ✅ Clientes de APIs
│   ├── circuit_breaker.py      - Pattern de protección
│   ├── odds_client.py          - Cliente The Odds API
│   └── football_client.py      - Cliente API-Football + stats detalladas (v0.5)
├── ai/                     ✅ Inteligencia Artificial
│   ├── types.py                - ContextualAnalysis (shared type)
│   ├── gemini_client.py        - Gemini AI con google-genai SDK (v0.5)
│   ├── blackbox_client.py      - Blackbox AI fallback
│   ├── collaborative_analyzer.py - Multi-AI consensus (NUEVO v0.5)
│   ├── ai_client.py            - Unified client con fallback
│   └── simple_analyzer.py      - Rule-based fallback
├── news/                   ✅ News Aggregation (NUEVO v0.5)
│   ├── news_scraper.py         - BBC + ESPN RSS (sin API calls)
│   └── __init__.py
├── db/                     ✅ Persistencia
│   ├── schema.sql              - DDL SQLite
│   └── odds_repository.py      - CRUD + cache
├── math_engine/            ✅ Motor estadístico
│   ├── poisson.py              - Distribución de Poisson + cumulative
│   ├── soccer_predictor.py     - Predictor de fútbol
│   ├── kelly.py                - Kelly Criterion
│   └── alternative_markets.py  - Corners, Cards, Shots (NUEVO v0.5)
├── models/                 ✅ Modelos de datos
│   ├── odds.py                 - Cuotas y eventos
│   └── soccer.py               - Stats extendidas (corners, cards, shots) (v0.5)
├── services/               ✅ Orquestadores
│   ├── odds_service.py         - Integra API + breaker + repo
│   └── match_analyzer.py       - Análisis multi-dimensional (v0.5)
├── ui/                     ✅ Interfaz terminal
│   ├── dashboard.py            - Dashboard 4 zonas
│   └── styles.py               - Paleta neón
├── tests/                  ✅ 96 tests (100% passing)
├── cli.py                  ✅ CLI interactivo
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
python example_collaborative_analysis.py  # Demo análisis colaborativo + news (NUEVO v0.5)
python example_alternative_markets.py     # Demo mercados alternativos (NUEVO v0.5)
python example_enhanced_analysis.py       # Demo análisis completo
python example_soccer_prediction.py       # Demo predictor Poisson
python demo_market_watch_simple.py        # Demo UI Rich
python example_usage.py                   # Demo cliente APIs
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

### AlternativeMarketPrediction (NUEVO v0.5)
```python
@dataclass
class AlternativeMarketPrediction:
    market_type: str              # "corners", "cards", "shots", etc.
    home_team: str
    away_team: str
    total_expected: float         # Valor esperado total
    over_under_predictions: Dict  # Probabilidades Over/Under múltiples thresholds
    home_expected: float          # Esperado para equipo local
    away_expected: float          # Esperado para equipo visitante
    distribution: Dict[int, float]  # Distribución completa de probabilidades
    confidence: float             # 0-1
    data_quality: str             # "high", "medium", "low"
    reasoning: str
```

### CollaborativeAnalysis (NUEVO v0.5)
```python
@dataclass
class CollaborativeAnalysis:
    consensus: ContextualAnalysis      # Análisis consensuado
    gemini_analysis: ContextualAnalysis  # Perspectiva Gemini
    blackbox_analysis: ContextualAnalysis  # Perspectiva Blackbox
    agreement_score: float             # 0-1, nivel de acuerdo
    confidence_boost: float            # Boost de confianza por acuerdo
    divergence_points: List[str]       # Puntos de desacuerdo
```

### NewsArticle (NUEVO v0.5)
```python
@dataclass
class NewsArticle:
    title: str
    url: str
    published: datetime
    source: str                    # "BBC Sport", "ESPN"
    summary: str
    teams_mentioned: List[str]     # Equipos detectados
    category: str                  # "injury", "transfer", "match_preview"
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

## 🎯 Nuevas Funcionalidades v0.5 (2026-01-04)

### 🤝 Análisis Colaborativo Multi-AI

Cuando **ambas IAs están disponibles** (Gemini + Blackbox), el sistema ejecuta:

1. **Análisis paralelo**: Ambas IAs analizan independientemente
2. **Merge inteligente**: Combina resultados ponderando por confianza
3. **Detección de divergencias**: Identifica puntos de desacuerdo
4. **Boost de confianza**: +20% máximo cuando acuerdo >80%

```python
from bet_copilot.ai.collaborative_analyzer import CollaborativeAnalyzer

analyzer = CollaborativeAnalyzer()

if analyzer.is_collaborative_available():
    result = await analyzer.analyze_match_comprehensive(
        home_team, away_team, home_form, away_form, h2h, context
    )
    
    print(f"Agreement: {result.agreement_score:.0%}")
    print(f"Confidence: {result.consensus.confidence:.0%}")
    print(f"Boost: +{result.confidence_boost:.0%}")
```

### 📰 News Feed Sin API Calls

**Fuentes gratuitas**:
- BBC Sport RSS (feeds.bbci.co.uk/sport/football/rss.xml)
- ESPN Soccer RSS (espn.com/espn/rss/soccer/news)

**Features**:
- ✅ Zero API calls / Zero cost
- ✅ Cache de 1 hora (configurable)
- ✅ Detección automática de equipos mencionados
- ✅ Categorización (injury, transfer, match_preview, general)
- ✅ Filtros por equipos y categorías

```python
from bet_copilot.news import NewsScraper

scraper = NewsScraper(cache_ttl=3600)

# Obtener últimas noticias
news = await scraper.fetch_all_news(max_per_source=15)

# Filtrar por equipos
relevant = scraper.filter_by_teams(news, ["Arsenal", "Chelsea"])

# Solo lesiones/suspensiones
injuries = scraper.filter_by_category(news, ["injury"])
```

### 📐 Mercados Alternativos

**Predicciones implementadas**:
- **Corners** (tiros de esquina)
- **Cards** (tarjetas amarillas/rojas) con ajuste por árbitro
- **Shots** (tiros totales)
- **Shots on target** (tiros a puerta)
- **Offsides** (fueras de juego)

**Modelo matemático**:
- Usa distribución de Poisson
- Calcula Over/Under para múltiples thresholds
- Distribución completa de probabilidades
- Assessment de calidad de datos

```python
from bet_copilot.math_engine.alternative_markets import AlternativeMarketsPredictor

predictor = AlternativeMarketsPredictor()

# Predicción de corners
corners = predictor.predict_corners(home_team_form, away_team_form)
print(f"Expected corners: {corners.total_expected:.1f}")
print(f"Over 10.5 prob: {corners.over_under_predictions[10.5]['over']:.1%}")

# Tarjetas con árbitro estricto
cards = predictor.predict_cards(
    home_team_form, away_team_form,
    referee_factor=1.2  # +20% por árbitro conocido por ser estricto
)
```

### 🔄 Flujo Integrado Completo

```python
from bet_copilot.services.match_analyzer import MatchAnalyzer

analyzer = MatchAnalyzer(
    use_collaborative_analysis=True  # Habilita modo colaborativo
)

# Análisis completo
analysis = await analyzer.analyze_match(
    "Manchester City", "Liverpool",
    league_id=39, season=2024,
    include_players=True,
    include_ai_analysis=True
)

# Resultados disponibles:
analysis.relevant_news            # Noticias del día (sin API)
analysis.collaborative_analysis   # Consenso Gemini+Blackbox
analysis.corners_prediction       # Predicción de esquinas
analysis.cards_prediction         # Predicción de tarjetas
analysis.shots_prediction         # Predicción de tiros
analysis.prediction               # Predicción tradicional ajustada por IA
analysis.kelly_home              # Recomendación Kelly para victoria local
```

---

## 🎯 Roadmap Completado

### ✅ Completado v0.5

1. ✅ **API-Football Client extendido**
   - get_fixture_statistics() - 12+ métricas por partido
   - get_team_recent_matches_with_stats() - Historial detallado
   - Parsing de corners, shots, cards, fouls, possession

2. ✅ **Kelly Calculator**
   - Implementado en v0.3
   - Modos: full Kelly, fractional Kelly

3. ✅ **Gemini Integration avanzada**
   - Migrado a google-genai SDK
   - Prompts extendidos con análisis táctico
   - Insights de mercados alternativos

4. ✅ **Análisis colaborativo**
   - Sistema de consenso multi-AI
   - Detección de divergencias
   - Confidence boosting

5. ✅ **News Aggregation**
   - RSS feeds gratuitos
   - Cache inteligente
   - Categorización automática

6. ✅ **Alternative Markets**
   - Predictor completo para 5 mercados
   - Distribuciones de Poisson
   - Over/Under múltiples thresholds

### 🔮 Próximas Mejoras

1. **Dashboard 4 Zonas mejorado**
   - Zona News Feed en tiempo real
   - Zona Multi-AI Agreement Score
   - Zona Alternative Markets

2. **Más fuentes de datos**
   - Integrar APIs gratuitas adicionales
   - Web scraping con rate limiting

3. **Backtesting Engine**
   - Validar predicciones históricas
   - Calcular ROI real

---

**Última actualización**: 2026-01-04  
**Proyecto**: Bet-Copilot v0.5.0  
**Código**: ~7,600 líneas Python  
**Tests**: 96 passing (100% coverage core features)  
**Autor**: Documentación generada para agentes IA
