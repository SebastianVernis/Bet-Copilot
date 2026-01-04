# Estructura de Prompts: Perplexity API + Gemini + Blackbox

Guía de uso especializado para desarrollo de Bet-Copilot usando tres IAs complementarias.

---

## 🎯 Filosofía de División de Trabajo

Cada IA tiene fortalezas específicas. Esta estructura maximiza eficiencia distribuyendo tareas según sus capacidades.

```
PERPLEXITY API → Investigación + Contexto actualizado
GEMINI         → Matemáticas + Validación estadística  
BLACKBOX       → Código Python + Refactorización
```

---

## 1️⃣ PERPLEXITY API

### 🔍 Uso Principal: Research & Contexto de Dominio

**Cuándo usar:**
- Buscar información sobre APIs (documentación, rate limits, endpoints)
- Entender conceptos deportivos (xG, métricas, estrategias)
- Investigar bibliotecas Python (Rich, Textual, aiosqlite)
- Explorar técnicas estadísticas (Poisson, Monte Carlo, Kelly Criterion)
- Verificar mejores prácticas de arquitectura

**Formato de Prompt:**

```
CONTEXTO: Bet-Copilot - Sistema de especulación deportiva CLI en Python
OBJETIVO: [Describir lo que necesitas investigar]
REQUERIMIENTOS:
- [Lista específica de lo que buscas]
- [Incluir restricciones técnicas]

PREGUNTA: [Tu pregunta específica]
```

### 📋 Ejemplos Prácticos

**Ejemplo 1: Investigar API**
```
CONTEXTO: Bet-Copilot - Sistema de especulación deportiva CLI en Python
OBJETIVO: Entender estructura de The Odds API y rate limits
REQUERIMIENTOS:
- Endpoints disponibles para cuotas de fútbol
- Rate limits del plan gratuito
- Formato de respuesta JSON
- Headers requeridos para autenticación

PREGUNTA: ¿Cuáles son las mejores prácticas para manejar rate limits de The Odds API y qué estructura de datos devuelve para eventos de fútbol?
```

**Ejemplo 2: Investigar Técnica Estadística**
```
CONTEXTO: Bet-Copilot - Predicción de resultados de fútbol
OBJETIVO: Implementar modelo Dixon-Coles para mejorar Poisson básico
REQUERIMIENTOS:
- Explicación matemática del modelo
- Diferencias con Poisson independiente
- Parámetros de ajuste necesarios
- Referencias a papers o implementaciones en Python

PREGUNTA: ¿Cómo funciona el modelo Dixon-Coles para predicción de fútbol y cuáles son las ventajas sobre Poisson independiente para marcadores bajos como 0-0 y 1-1?
```

**Ejemplo 3: Investigar Biblioteca**
```
CONTEXTO: Bet-Copilot - Dashboard CLI con Rich
OBJETIVO: Crear tabla actualizable en tiempo real
REQUERIMIENTOS:
- Uso de Rich.Live para updates sin parpadeo
- Manejo de múltiples layouts simultáneos
- Performance con >50 filas de datos
- Compatibilidad con asyncio

PREGUNTA: ¿Cuál es la mejor manera de implementar tablas actualizables en tiempo real con Rich sin afectar el performance, y cómo integrar esto con asyncio?
```

---

## 2️⃣ GEMINI (1.5 Pro / 2.0 Flash)

### 🧮 Uso Principal: Matemáticas, Estadística & Validación

**Cuándo usar:**
- Diseñar lógica de modelos estadísticos
- Validar fórmulas matemáticas
- Explicar teoría antes de implementar
- Calcular ejemplos numéricos paso a paso
- Detectar errores en razonamiento estadístico

**Formato de Prompt:**

```
ROL: Actúas como un PhD en Estadística Aplicada al Deporte
PROYECTO: Bet-Copilot - Motor de predicción deportiva

TAREA: [Describir el problema matemático/estadístico]

RESTRICCIONES:
- [Datos disponibles]
- [Limitaciones computacionales]

ENTREGABLE: [Lo que esperas recibir]
```

### 📋 Ejemplos Prácticos

**Ejemplo 1: Diseño de Modelo**
```
ROL: Actúas como un PhD en Estadística Aplicada al Deporte
PROYECTO: Bet-Copilot - Motor de predicción deportiva

TAREA: Diseñar el modelo matemático para calcular Expected Value (EV) de una apuesta considerando:
1. Probabilidad del modelo (P_modelo)
2. Cuota del bookmaker (Odds)
3. Probabilidad implícita del bookmaker (P_bookmaker = 1/Odds)
4. Margen de seguridad (para evitar overbetting)

RESTRICCIONES:
- Usar fórmula EV = (P_modelo × Odds) - 1
- Incluir threshold mínimo de EV para considerar "value bet" (ej: +5%)
- Considerar el overround del bookmaker (suma de probabilidades implícitas > 100%)

ENTREGABLE:
1. Fórmula matemática completa
2. Ejemplo numérico paso a paso
3. Casos edge (P_modelo muy baja/alta, odds extremas)
4. Recomendación de thresholds para diferentes perfiles de riesgo
```

**Ejemplo 2: Validación de Implementación**
```
ROL: Actúas como un PhD en Estadística Aplicada al Deporte
PROYECTO: Bet-Copilot - Validación de modelo Poisson

TAREA: Valida esta implementación de Poisson para predicción de goles:

[CÓDIGO/FÓRMULA]
P(X = k) = (λ^k × e^-λ) / k!
λ_home = (xG_home_avg + xG_against_away_avg) / 2

PREGUNTA:
1. ¿Es correcto promediar xG ofensivo con xG defensivo del rival?
2. ¿Debería aplicarse factor de ventaja local (1.1x)?
3. ¿Cómo validar que las probabilidades agregadas sumen ~1.0?
4. ¿Qué sanity checks numéricos debo implementar?

ENTREGABLE: Validación matemática con recomendaciones de mejora
```

**Ejemplo 3: Explicación Teórica**
```
ROL: Actúas como un PhD en Estadística Aplicada al Deporte
PROYECTO: Bet-Copilot - Fundamentos del Criterio de Kelly

TAREA: Explica el Criterio de Kelly para sizing de apuestas:
1. Fórmula matemática completa
2. Intuición: ¿por qué maximiza crecimiento logarítmico del bankroll?
3. Diferencia entre Kelly completo vs Kelly fraccionario (1/4 Kelly, 1/2 Kelly)
4. Ejemplo numérico con:
   - Bankroll: $1000
   - P_modelo: 60%
   - Odds: 2.5
   - EV: +50%

RESTRICCIONES:
- Explicación matemática rigurosa pero accesible
- Incluir casos donde Kelly recomienda NO apostar

ENTREGABLE: Explicación teórica + pseudocódigo para implementación
```

**Ejemplo 4: Análisis de Datos (Integración futura con Gemini API)**
```
ROL: Actúas como analista deportivo con acceso a datos contextuales
PROYECTO: Bet-Copilot - Filtro de Inteligencia

TAREA: Analiza este partido y ajusta las probabilidades del modelo Poisson:

MATCH: Real Madrid vs Barcelona
FECHA: 2026-01-15
MODELO POISSON:
- P(Home Win): 45%
- P(Draw): 25%
- P(Away Win): 30%
- λ_home: 1.8
- λ_away: 1.5

CONTEXTO ADICIONAL A CONSIDERAR:
1. Búsqueda de noticias de lesiones (últimas 48h)
2. Análisis de sentimiento en redes sociales
3. Historial de enfrentamientos directos
4. Importancia del partido (liga/copa)

ENTREGABLE:
1. Probabilidades ajustadas (si aplica)
2. Factor de confianza (0-1)
3. Justificación de ajustes con fuentes
4. Warnings si hay información contradictoria
```

---

## 3️⃣ BLACKBOX AI (Pro)

### 💻 Uso Principal: Código Python & Arquitectura

**Cuándo usar:**
- Implementar features completas (API clients, modelos, UI)
- Refactorizar código existente
- Debuggear errores
- Escribir tests unitarios
- Optimizar performance

**Formato de Prompt:**

```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: [Stack usado]
MÓDULO: [Parte del sistema]

TAREA: [Descripción clara de lo que necesitas]

REQUERIMIENTOS:
- [Requisito funcional 1]
- [Requisito funcional 2]

RESTRICCIONES:
- [Restricción técnica 1]
- [Restricción técnica 2]

ENTREGABLE: [Código completo / Tests / Documentación]
```

### 📋 Ejemplos Prácticos

**Ejemplo 1: Nueva Feature**
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, aiohttp, SQLite, Rich
MÓDULO: Integración API-Football

TAREA: Implementar cliente asíncrono para API-Football que obtenga estadísticas de partidos históricos (últimos 5 partidos de un equipo).

REQUERIMIENTOS:
- Clase AsyncAPIFootballClient con métodos:
  - get_team_matches(team_id: int, last_n: int = 5) -> List[MatchStats]
  - get_team_statistics(team_id: int) -> TeamStats
- Manejo de errores (timeout, 429, 500)
- Integración con Circuit Breaker existente
- Cache de 1 hora para stats (SQLite)
- Rate limit: 30 requests/minuto

RESTRICCIONES:
- Reutilizar patrón de OddsAPIClient existente
- Usar dataclasses para modelos
- Logging estructurado con logger.info/error
- Tipo de retorno: TypedDict o dataclass (no dict plano)

ENTREGABLE: Código completo con:
1. Client class
2. Modelos de datos (MatchStats, TeamStats)
3. 3-5 tests unitarios básicos
4. Docstrings en funciones públicas
```

**Ejemplo 2: Refactorización**
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, asyncio
MÓDULO: OddsService - Refactorización

TAREA: El método get_odds() tiene >100 líneas y maneja demasiadas responsabilidades. Refactorizar en métodos más pequeños manteniendo la misma funcionalidad.

CÓDIGO ACTUAL:
[Pegar código a refactorizar]

REQUERIMIENTOS:
- Extraer lógica de cache a _check_cache()
- Extraer lógica de fallback a _handle_api_failure()
- Extraer logging a métodos helper
- Mantener la misma API pública
- No romper tests existentes

RESTRICCIONES:
- Cada método privado debe tener <30 líneas
- Mantener type hints estrictos
- No cambiar comportamiento observable

ENTREGABLE: Código refactorizado con explicación de cambios
```

**Ejemplo 3: Debugging**
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, Rich
MÓDULO: MarketWatchTable - Bug de rendering

PROBLEMA: La tabla se descuadra cuando los nombres de equipos tienen >15 caracteres. Las columnas se solapan y el texto se corta mal.

CÓDIGO CON BUG:
[Pegar código problemático]

ERROR OBSERVADO:
```
Arsenal FC Manchester vs Liverpool FC Everton
                                  │ Over 2.5 │ ...
```
(El texto se sale de la columna)

TAREA: Identificar causa del bug y proponer fix que:
1. Trunca nombres largos con ellipsis (...)
2. Mantiene ancho fijo de columna
3. Agrega tooltip con nombre completo (si Rich lo soporta)

ENTREGABLE: Fix del bug + explicación de la causa raíz
```

**Ejemplo 4: Tests**
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, pytest, pytest-asyncio
MÓDULO: SoccerPredictor - Tests

TAREA: Escribir suite de tests para SoccerPredictor.predict_from_lambdas()

CASOS A TESTEAR:
1. Predicción normal (λ_home=1.8, λ_away=1.5)
2. Favorito extremo (λ_home=3.5, λ_away=0.5)
3. Equipos igualados (λ_home=λ_away=1.5)
4. Lambda negativo (debe fallar o devolver 0)
5. Lambda muy alto (>10, edge case)

REQUERIMIENTOS:
- Usar fixtures para datos de prueba
- Assertions claras con mensajes descriptivos
- Test de que las probabilidades suman ~1.0
- Parametrize para múltiples casos
- Coverage >80% del método

ENTREGABLE: Archivo test_soccer_predictor.py completo
```

**Ejemplo 5: Integración de Componentes**
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+, Rich, asyncio
MÓDULO: Dashboard Completo (4 Zonas)

TAREA: Crear dashboard principal que integre:
- Zona A: API Health (circuit breaker stats)
- Zona B: Active Tasks (asyncio tasks monitor)
- Zona C: Live Market Watch (ya implementado)
- Zona D: System Logs (últimos 10 logs)

REQUERIMIENTOS:
- Layout con Rich.Layout (4 cuadrantes)
- Update cada 1 segundo con Rich.Live
- Colores neón consistentes (usar styles.py)
- Responsive (auto-ajusta si terminal <120 cols)
- Método dashboard.start() que corre loop principal

RESTRICCIONES:
- Reutilizar MarketWatchTable existente para Zona C
- No bloquear event loop (asyncio-friendly)
- Graceful shutdown con Ctrl+C

ENTREGABLE:
1. Clase Dashboard con métodos start/stop
2. Generadores de datos mock para Zonas A/B/D
3. Script main.py que lanza el dashboard
```

---

## 🔄 Workflow Combinado (Caso Real)

### Caso: Implementar Criterio de Kelly

#### Paso 1: Research (Perplexity)
```
CONTEXTO: Bet-Copilot - Sistema de especulación deportiva CLI
OBJETIVO: Implementar Criterio de Kelly para sizing de apuestas
REQUERIMIENTOS:
- Explicación de Kelly completo vs Kelly fraccionario
- Casos edge donde Kelly recomienda 0% o >100%
- Implementaciones en Python existentes (referencias)

PREGUNTA: ¿Cuáles son las mejores prácticas para implementar Kelly Criterion en sistemas de apuestas deportivas, considerando bankroll management y casos extremos?
```

#### Paso 2: Matemáticas (Gemini)
```
ROL: PhD en Estadística - Especialista en Risk Management
PROYECTO: Bet-Copilot - Criterio de Kelly

TAREA: Diseña la lógica matemática completa para:
1. Calcular Kelly optimal stake
2. Implementar Kelly fraccionario (1/4, 1/2)
3. Manejar casos edge (EV negativo, odds <1.01, bankroll insuficiente)

FÓRMULAS BASE:
f* = (p × b - q) / b
Donde:
- f* = fracción del bankroll a apostar
- p = probabilidad modelo
- q = 1 - p
- b = odds - 1

ENTREGABLE:
1. Validación de fórmulas
2. Ejemplos numéricos (5 casos)
3. Pseudocódigo paso a paso
4. Warnings y thresholds recomendados
```

#### Paso 3: Implementación (Blackbox)
```
PROYECTO: Bet-Copilot
CONTEXTO TÉCNICO: Python 3.10+
MÓDULO: KellyCalculator - Nuevo módulo

TAREA: Implementar KellyCalculator basado en diseño matemático de Gemini.

[Pegar salida de Gemini aquí]

REQUERIMIENTOS:
- Clase KellyCalculator con métodos:
  - calculate_stake(bankroll, model_prob, odds, fraction=1.0) -> float
  - get_recommendation(stake) -> Dict[str, Any]  # stake + warnings
- Validaciones de input
- Return de warnings claros (ej: "EV negativo, no apostar")
- Tests unitarios (5 casos de Gemini)

RESTRICCIONES:
- Type hints estrictos
- Docstrings con ejemplos
- Manejo de división por cero

ENTREGABLE: Código completo + tests
```

---

## 📁 Template de Sesión

Guarda este formato al final de cada sesión:

```markdown
## Sesión: [Fecha YYYY-MM-DD]

### IAs Usadas
- [ ] Perplexity: [Temas investigados]
- [ ] Gemini: [Validaciones matemáticas]
- [ ] Blackbox: [Código implementado]

### Logros
- ✅ [Feature/Fix completado]
- ✅ [Tests agregados]

### Bloqueadores
- ❌ [Problema no resuelto + contexto]

### Próximos Pasos
1. [ ] [Tarea 1]
2. [ ] [Tarea 2]

### Código Crítico
```python
# [Pegar snippet clave desarrollado]
```

### Aprendizajes
- [Insight técnico importante]
- [Gotcha o edge case descubierto]
```

---

## 🎓 Mejores Prácticas

### DO ✅
- **Perplexity**: Preguntas específicas con contexto claro
- **Gemini**: Pedir explicación teórica ANTES de implementar
- **Blackbox**: Proveer código existente al refactorizar
- Copiar salidas entre IAs (output de Gemini → input de Blackbox)
- Validar con tests después de cada implementación

### DON'T ❌
- Mezclar tareas (ej: pedir código a Perplexity)
- Asumir que Gemini genera código Python óptimo (úsalo para teoría)
- Implementar sin entender la matemática primero
- Olvidar agregar el contexto del master_prompt.txt
- Saltar directo a código sin research/validación

---

## 📌 Quick Reference

| Necesito... | IA | Prompt Base |
|-------------|----|------------|
| Entender una API | Perplexity | "CONTEXTO: Bet-Copilot / OBJETIVO: [API] / PREGUNTA: Estructura y rate limits..." |
| Validar fórmula | Gemini | "ROL: PhD Estadística / TAREA: Validar [fórmula] / ENTREGABLE: Ejemplo numérico" |
| Implementar feature | Blackbox | "PROYECTO: Bet-Copilot / MÓDULO: [nombre] / TAREA: Implementar [feature]" |
| Debuggear código | Blackbox | "PROBLEMA: [descripción] / CÓDIGO: [pegar] / ERROR: [output]" |
| Diseñar modelo | Gemini | "ROL: PhD / TAREA: Diseñar lógica de [modelo] / RESTRICCIONES: [datos]" |
| Investigar biblioteca | Perplexity | "OBJETIVO: Usar [lib] para [tarea] / REQUERIMIENTOS: [lista]" |

---

**Última actualización**: 2026-01-04  
**Versión**: 1.0  
**Proyecto**: Bet-Copilot
