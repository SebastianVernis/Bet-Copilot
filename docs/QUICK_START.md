# Quick Start Guide - Bet-Copilot

Guía rápida para retomar el desarrollo después de pausas.

---

## 🚀 Estado Actual del Proyecto

### ✅ Componentes Implementados (70%)

#### 1. Backend (APIs & Data)
```
✅ OddsAPIClient          - Cliente async para The Odds API
✅ CircuitBreaker         - Protección contra rate limits (429)
✅ OddsRepository         - Persistencia en SQLite + cache
✅ OddsService            - Orquestador (client + breaker + repo)
```

#### 2. Motor Matemático
```
✅ PoissonCalculator      - Distribución de Poisson pura
✅ MatchSimulator         - Simulación de marcadores
✅ SoccerPredictor        - Predictor de partidos con xG
✅ TeamForm / MatchResult - Modelos de datos históricos
```

#### 3. UI (Terminal)
```
✅ MarketWatchTable       - Tabla Rich con colores neón
✅ MockDataGenerator      - Generador de datos de prueba
✅ Styles (Neon Theme)    - Paleta de colores + helpers
```

#### 4. Base de Datos
```sql
✅ odds_data              - Cuotas cacheadas
✅ api_requests           - Log de peticiones
✅ circuit_breaker_events - Log de eventos del breaker
```

### ⏳ Componentes Pendientes (30%)

```
❌ API-Football Client    - Stats históricas detalladas
❌ Gemini Integration     - Análisis narrativo (lesiones, sentimiento)
❌ Kelly Calculator       - Sizing óptimo de apuestas
❌ Dashboard Completo     - 4 zonas (solo Zona C implementada)
❌ CLI Interactivo        - Comandos para operar el sistema
❌ Filtro de Intención    - LLM conversacional para perfil de usuario
```

---

## 📂 Estructura de Archivos

```
Bet-Copilot/
├── bet_copilot/
│   ├── api/
│   │   ├── circuit_breaker.py    ✅ Circuit Breaker pattern
│   │   └── odds_client.py         ✅ Cliente The Odds API
│   ├── db/
│   │   ├── schema.sql             ✅ DDL de SQLite
│   │   └── odds_repository.py     ✅ Capa de persistencia
│   ├── math_engine/
│   │   ├── poisson.py             ✅ Calculadora Poisson
│   │   └── soccer_predictor.py    ✅ Predictor de fútbol
│   ├── models/
│   │   ├── odds.py                ✅ Modelos de cuotas
│   │   └── soccer.py              ✅ Modelos de fútbol (xG, form)
│   ├── services/
│   │   └── odds_service.py        ✅ Orquestador principal
│   ├── ui/
│   │   ├── market_watch.py        ✅ Tabla de mercados (Rich)
│   │   ├── mock_data.py           ✅ Generador mock data
│   │   └── styles.py              ✅ Paleta neón + helpers
│   ├── tests/
│   │   ├── test_circuit_breaker.py   ✅ 11 tests
│   │   ├── test_poisson.py           ✅ 15 tests
│   │   └── test_soccer_predictor.py  ✅ 10 tests
│   └── config.py                  ✅ Configuración centralizada
├── example_usage.py               ✅ Demo de OddsService
├── example_soccer_prediction.py   ✅ Demo de SoccerPredictor
├── demo_market_watch_simple.py    ✅ Demo de UI (standalone)
├── master_prompt.txt              ✅ Contexto del proyecto
├── PROMPTS_STRUCTURE.md           ✅ Guía de uso de IAs
├── QUICK_START.md                 📄 Este archivo
├── README.md                      ✅ Documentación principal
├── requirements.txt               ✅ Dependencias
└── .env.example                   ✅ Template de config
```

---

## 🎯 Cómo Retomar Desarrollo

### Opción 1: Continuar con Feature Pendiente

#### A. Implementar API-Football Client

**IA Recomendada**: Blackbox

**Prompt**:
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, aiohttp, SQLite
MÓDULO: API-Football Client (Nuevo)

TAREA: Implementar cliente asíncrono para API-Football similar a OddsAPIClient.

REFERENCIA: Ver bet_copilot/api/odds_client.py como patrón base

REQUERIMIENTOS:
- Clase APIFootballClient con métodos:
  - get_team_fixtures(team_id: int, last: int = 5) -> List[Fixture]
  - get_h2h(team1_id: int, team2_id: int) -> List[H2HMatch]
  - get_team_statistics(team_id: int, season: int) -> TeamStatistics
- Integración con CircuitBreaker existente
- Cache en SQLite (tabla fixtures_cache, TTL: 6 horas)
- Rate limit: 30 req/min (plan gratuito)

RESTRICCIONES:
- Reutilizar patrón de retry/backoff de OddsAPIClient
- Type hints estrictos (usar dataclasses para modelos)
- Logging consistente con resto del proyecto

ENTREGABLE: Código completo + 5 tests básicos
```

#### B. Implementar Kelly Criterion

**IA Recomendada**: Gemini (teoría) → Blackbox (código)

**Prompt para Gemini**:
```
ROL: PhD en Matemática Financiera - Risk Management
PROYECTO: Bet-Copilot - Criterio de Kelly

TAREA: Diseñar lógica completa para Kelly Criterion aplicado a apuestas deportivas.

FÓRMULA BASE:
f* = (p × b - q) / b

Donde:
- f* = fracción óptima del bankroll
- p = probabilidad modelo
- q = 1 - p
- b = odds - 1

CASOS A CONSIDERAR:
1. Kelly completo (agresivo)
2. Kelly fraccionario (1/4, 1/2, conservador)
3. EV negativo → f* negativo → NO apostar
4. Odds muy bajas (<1.1) → stake muy alto → limitar
5. Bankroll insuficiente para stake mínimo

ENTREGABLE:
1. Validación matemática de fórmulas
2. 5 ejemplos numéricos paso a paso
3. Thresholds recomendados por perfil de riesgo:
   - Conservador: 1/4 Kelly
   - Moderado: 1/2 Kelly
   - Agresivo: Full Kelly
4. Pseudocódigo con validaciones
```

**Luego usar Blackbox** con output de Gemini para implementar.

#### C. Integración con Gemini API

**IA Recomendada**: Perplexity (research) → Blackbox (código)

**Prompt para Perplexity**:
```
CONTEXTO: Bet-Copilot - Sistema de predicción deportiva
OBJETIVO: Integrar Gemini 1.5 Pro para análisis contextual
REQUERIMIENTOS:
- SDK oficial de Google (google-generativeai)
- Rate limits y costos del plan gratuito
- Mejores prácticas para prompting de análisis deportivo
- Formato JSON estructurado de respuestas

PREGUNTA: ¿Cómo integrar Gemini 1.5 Pro API en Python para análizar contexto de partidos (lesiones, sentimiento) y ajustar probabilidades de un modelo Poisson?
```

---

### Opción 2: Ejecutar Demos Existentes

```bash
# 1. Ver cliente de APIs en acción
python example_usage.py

# 2. Ver motor de predicción (Poisson)
python example_soccer_prediction.py

# 3. Ver UI de mercados (Rich)
python demo_market_watch_simple.py

# 4. Ejecutar tests
# pytest bet_copilot/tests/ -v  (requiere instalar pytest)
```

---

### Opción 3: Explorar Código Existente

**Componentes Clave para Entender**:

1. **Circuit Breaker** (`bet_copilot/api/circuit_breaker.py:60-85`)
   - Cómo detecta 429 y abre el circuito
   - Estados: CLOSED → OPEN → HALF_OPEN

2. **Poisson Predictor** (`bet_copilot/math_engine/poisson.py:45-70`)
   - Cálculo de P(X=k) = (λ^k × e^-λ) / k!
   - Cómo simula todos los marcadores posibles

3. **Market Watch UI** (`demo_market_watch_simple.py:85-150`)
   - Cómo formatea EV con colores neón
   - Layout responsive con Rich

---

## 🔧 Setup Rápido

### 1. Dependencias
```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
aiohttp>=3.9.0
aiosqlite>=0.19.0
rich>=13.0.0
textual>=0.40.0
python-dotenv>=1.0.0

# Opcionales para desarrollo
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 2. Configuración
```bash
cp .env.example .env
# Editar .env y agregar API keys:
# ODDS_API_KEY=tu_clave_aqui
```

### 3. Base de Datos
```python
# Se crea automáticamente al ejecutar cualquier ejemplo
# Ubicación: bet_copilot.db (en raíz del proyecto)
```

---

## 📊 Estado de Tests

```
Circuit Breaker:    11/11 ✅ (100%)
Poisson:            15/15 ✅ (100%)
Soccer Predictor:   10/10 ✅ (100%)
Total:              36 tests passing
```

**Ejecutar tests** (requiere pytest):
```bash
pytest bet_copilot/tests/ -v
```

---

## 🎨 Paleta de Colores (UI)

```python
NEON_GREEN  = "#39FF14"  # EV positivo alto (>5%)
NEON_YELLOW = "#FFFF00"  # EV positivo bajo (0-5%)
NEON_CYAN   = "#00FFFF"  # Equipo local
NEON_PINK   = "#FF10F0"  # Equipo visitante
NEON_PURPLE = "#9D00FF"  # Títulos
NEON_RED    = "#FF073A"  # Errores / EV negativo
```

---

## 💡 Comandos Útiles

```bash
# Ver estructura del proyecto
tree bet_copilot/ -I '__pycache__|*.pyc'

# Buscar TODOs en código
grep -r "TODO" bet_copilot/

# Ver logs de SQLite
sqlite3 bet_copilot.db "SELECT * FROM api_requests ORDER BY timestamp DESC LIMIT 10;"

# Contar líneas de código
find bet_copilot/ -name "*.py" | xargs wc -l

# Limpiar cache de Python
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## 🐛 Troubleshooting

### Error: "No module named 'bet_copilot'"
```bash
# Ejecutar desde la raíz del proyecto
cd /ruta/a/Bet-Copilot
python example_usage.py
```

### Error: "No API key provided"
```bash
# Verificar .env
cat .env | grep ODDS_API_KEY

# Si no existe, copiar template
cp .env.example .env
# Editar y agregar clave real
```

### Error: "Circuit breaker is open"
```python
# Normal después de un 429
# Esperar 60 segundos o resetear manualmente:
from bet_copilot.services.odds_service import OddsService
service = OddsService()
await service.circuit_breaker.manual_close()
```

---

## 📚 Referencias Rápidas

### Documentación de APIs
- **The Odds API**: https://the-odds-api.com/
- **API-Football**: https://www.api-football.com/documentation-v3
- **Gemini API**: https://ai.google.dev/docs

### Librerías
- **Rich**: https://rich.readthedocs.io/
- **aiosqlite**: https://aiosqlite.omnilib.dev/
- **aiohttp**: https://docs.aiohttp.org/

### Papers de Referencia
- Dixon-Coles (1997): "Modelling Association Football Scores"
- Kelly Criterion: "A New Interpretation of Information Rate"
- Expected Goals (xG): Metrics en analytics deportivo

---

## 🎯 Próximo Sprint Recomendado

Según prioridad técnica:

1. **API-Football Client** (3-4 horas)
   - Permite obtener xG reales en lugar de mock data
   - Base para mejorar precisión del predictor

2. **Kelly Calculator** (2-3 horas)
   - Completa el flujo de "predicción → sizing"
   - Componente crítico para risk management

3. **Dashboard 4 Zonas** (4-5 horas)
   - Integra todo en UI unificada
   - Mejora UX dramáticamente

4. **Gemini Integration** (3-4 horas)
   - Añade capa de inteligencia contextual
   - Diferenciador clave del proyecto

---

**Última actualización**: 2026-01-04  
**Versión del proyecto**: 0.2.0 (MVP Core completo)
