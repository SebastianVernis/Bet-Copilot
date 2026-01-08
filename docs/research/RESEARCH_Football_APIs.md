# Investigación: Alternativas a API-Football

## Problema Actual
API-Football tiene límites muy restrictivos en el plan gratuito:
- 10 requests/minuto
- 100 requests/día
- No acceso a parámetro "Last" (partidos recientes con stats)
- Rate limit frecuente

## Alternativas Investigadas

### 1. **Football-Data.org** (MUY RECOMENDADA)
🌐 https://www.football-data.org/

**Plan Gratuito:**
- 10 llamadas/minuto
- Sin límite diario explícito
- Tier gratuito permanente
- No requiere tarjeta de crédito

**Datos Disponibles:**
- ✅ Ligas principales (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- ✅ Partidos en vivo y programados
- ✅ Resultados históricos
- ✅ Clasificaciones
- ✅ Goleadores
- ✅ Equipos y plantillas básicas
- ❌ Stats detalladas por partido (solo en plan de pago)

**Endpoint Ejemplo:**
```bash
curl -X GET https://api.football-data.org/v4/competitions/PL/matches \
  -H "X-Auth-Token: YOUR_API_KEY"
```

**Ventajas:**
- API muy estable y confiable
- Documentación excelente
- Rate limit razonable
- Cobertura de ligas top

**Desventajas:**
- Stats detalladas (xG, shots, corners) solo en plan de pago (€18/mes)

---

### 2. **SportsData.io** (Alternativa con Trial)
🌐 https://sportsdata.io/

**Plan Trial:**
- 30 días gratis
- 1000 requests/día
- Después $0 por 500 requests/mes

**Datos Disponibles:**
- ✅ Resultados y fixtures
- ✅ Stats básicas
- ✅ Lesiones
- ✅ Lineups
- ❌ xG y stats avanzadas limitadas

**Ventajas:**
- Trial generoso
- API rápida

**Desventajas:**
- Después del trial, muy restrictivo en plan gratuito

---

### 3. **TheSportsDB** (Gratuita con Patreon)
🌐 https://www.thesportsdb.com/api.php

**Plan Gratuito:**
- Sin límite oficial documentado
- 100% gratuito para uso personal
- Opción Patreon para soporte prioritario ($2-3/mes)

**Datos Disponibles:**
- ✅ Ligas, equipos, jugadores
- ✅ Resultados de partidos
- ✅ Próximos partidos
- ✅ Clasificaciones
- ❌ Stats en vivo (solo Patreon)
- ❌ No xG ni stats avanzadas

**Endpoint Ejemplo:**
```bash
curl https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t=Arsenal
```

**Ventajas:**
- Totalmente gratuito
- Sin rate limit estricto
- Muy fácil de usar

**Desventajas:**
- No tiene stats avanzadas (xG, corners, shots)
- Datos a veces desactualizados

---

### 4. **API-Sports (Similar a API-Football pero más flexible)**
🌐 https://api-sports.io/

**Plan Gratuito:**
- 100 requests/día
- Acceso a múltiples deportes
- Mismo proveedor que API-Football

**Desventajas:**
- Mismos límites que API-Football
- No resuelve el problema

---

### 5. **OpenLigaDB** (Solo Bundesliga - Gratuita)
🌐 https://www.openligadb.de/

**Plan:**
- 100% gratuito
- Sin rate limit
- Solo Bundesliga alemana

**Ventajas:**
- Completamente gratis
- Stats detalladas de Bundesliga

**Desventajas:**
- Solo Bundesliga

---

### 6. **Web Scraping de Fuentes Públicas** ⭐ RECOMENDADA
Sitios con datos públicos que podemos scrapear:

#### **FBref.com** (Stats avanzadas)
- ✅ xG, xGA por equipo
- ✅ Corners, shots, tarjetas
- ✅ Stats detalladas por partido
- ✅ Datos históricos completos
- ⚠️ Requiere web scraping (BeautifulSoup)

#### **Transfermarkt**
- ✅ Lesiones actualizadas
- ✅ Valores de jugadores
- ✅ Transferencias
- ⚠️ Requiere web scraping

#### **SofaScore** (Datos en vivo)
- ✅ Stats en tiempo real
- ✅ Clasificaciones
- ✅ Próximos partidos
- ⚠️ Tiene API no oficial pero puede cambiar

---

## Estrategia Recomendada (Híbrida)

### Opción 1: Football-Data.org + Web Scraping
```python
# Football-Data.org para:
- Fixtures y resultados básicos
- Clasificaciones
- Equipos y jugadores

# Web Scraping (FBref) para:
- xG, xGA, shots, corners
- Stats detalladas por partido
- Datos históricos avanzados
```

**Ventajas:**
- ✅ Datos completos
- ✅ Sin límites estrictos
- ✅ 100% gratuito

**Implementación:**
```python
# 1. Usar Football-Data.org como fuente principal
# 2. Scrapear FBref.com para stats avanzadas (con cache)
# 3. Cachear agresivamente (24h para stats históricas)
# 4. Rate limiting manual (1 request cada 2 segundos)
```

---

### Opción 2: Solo Web Scraping (Sin APIs)
```python
# Scrapear directamente de:
- FBref.com (stats avanzadas)
- ESPN.com (fixtures y resultados)
- Transfermarkt (lesiones)
```

**Ventajas:**
- ✅ Completamente gratuito
- ✅ Sin límites de API
- ✅ Datos muy completos

**Desventajas:**
- ⚠️ Requiere mantenimiento si cambian layouts
- ⚠️ Más lento que API
- ⚠️ Posible bloqueo si no se usa rate limiting

---

### Opción 3: TheSportsDB + Stats Estimadas
```python
# TheSportsDB para fixtures/resultados
# Estimar xG basado en:
- Goles históricos promedio
- Forma reciente
- Algoritmos propios (ya implementado en SimpleProvider)
```

**Ventajas:**
- ✅ Muy simple
- ✅ API gratuita y estable
- ✅ Ya tenemos lógica de estimación

**Desventajas:**
- ⚠️ Stats menos precisas

---

## Decisión Final Recomendada

**Implementar sistema híbrido con fallback en cascada:**

```
1. Football-Data.org (fixtures, resultados, equipos)
   ↓ (si falla o necesita stats avanzadas)
2. Web Scraping FBref (xG, corners, shots, cards)
   ↓ (si falla)
3. SimpleProvider (estimaciones basadas en histórico)
```

**Prioridades:**
1. ✅ Implementar cliente para Football-Data.org
2. ✅ Implementar scraper de FBref con cache agresivo
3. ✅ Mantener SimpleProvider como último fallback

---

## Próximos Pasos

### 1. Registrarse en Football-Data.org
```bash
# Obtener API key gratuita en:
https://www.football-data.org/client/register
```

### 2. Implementar cliente
```python
# bet_copilot/api/football_data_client.py
class FootballDataClient:
    BASE_URL = "https://api.football-data.org/v4"
    
    async def get_matches(self, competition: str):
        # Implementation
        pass
```

### 3. Implementar scraper FBref
```python
# bet_copilot/scrapers/fbref_scraper.py
class FBrefScraper:
    async def get_team_stats(self, team_name: str):
        # BeautifulSoup + cache
        pass
```

### 4. Actualizar FootballClientWithFallback
```python
# Añadir Football-Data.org como provider principal
# Fallback: FBref → SimpleProvider
```

---

**Fecha**: 2026-01-07  
**Investigado por**: Sistema de IA  
**Estado**: Recomendación lista para implementación

---

## Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                    FootballClientWithFallback                   │
│                      (Orchestrator Layer)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │       Provider Selection Logic          │
        │  (Try providers in order until success) │
        └─────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ FootballData   │  │  FBref Scraper   │  │ SimpleProvider  │
│   Client       │  │   (Web Scraping) │  │  (Estimations)  │
│                │  │                  │  │                 │
│ - Fixtures     │  │ - xG/xGA         │  │ - Estimated xG  │
│ - Results      │  │ - Corners        │  │ - Form-based    │
│ - Teams        │  │ - Shots          │  │ - No API needed │
│ - Players      │  │ - Cards          │  │                 │
│ - Standings    │  │ - Detailed stats │  │                 │
│                │  │                  │  │                 │
│ Rate: 10/min   │  │ Rate: 1/2s       │  │ Rate: Unlimited │
│ Free: Yes      │  │ Free: Yes        │  │ Free: Yes       │
└────────────────┘  └──────────────────┘  └─────────────────┘
```

### Data Flow Example

**Scenario 1: Get team stats (success path)**
```
User Request
    ↓
FootballClientWithFallback.get_team_stats()
    ↓
Try FootballDataClient
    ↓ (Success)
Return basic stats (form, goals avg)
    ↓
Try FBrefScraper for advanced stats (xG, corners, shots)
    ↓ (Success)
Merge data and return complete stats
```

**Scenario 2: API failure (fallback path)**
```
User Request
    ↓
FootballClientWithFallback.get_team_stats()
    ↓
Try FootballDataClient
    ↓ (Rate limit exceeded)
Try FBrefScraper
    ↓ (Success)
Return scraped data
    ↓ (If scraping fails)
Try SimpleProvider
    ↓
Return estimated stats
```

### Cache Strategy

```python
# Layer 1: Memory cache (fast, short-lived)
memory_cache = {
    "ttl": 300,  # 5 minutes
    "use_for": ["live_matches", "current_odds"]
}

# Layer 2: Disk cache (persistent, medium-lived)
disk_cache = {
    "ttl": 86400,  # 24 hours
    "use_for": ["team_stats", "historical_results", "standings"]
}

# Layer 3: Database cache (long-term)
db_cache = {
    "ttl": 604800,  # 7 days
    "use_for": ["player_info", "team_info", "league_structure"]
}
```

### Rate Limiting Strategy

```python
# Per-provider rate limiters
rate_limiters = {
    "football_data": {
        "calls_per_minute": 10,
        "strategy": "token_bucket"
    },
    "fbref_scraper": {
        "calls_per_second": 0.5,  # 1 call every 2 seconds
        "strategy": "fixed_window",
        "user_agent_rotation": True
    },
    "simple_provider": {
        "unlimited": True
    }
}
```

---

## Comparativa Final

| Feature                | API-Football | Football-Data.org | FBref Scraper | SimpleProvider |
|------------------------|--------------|-------------------|---------------|----------------|
| **Fixtures**           | ✅ Excelente | ✅ Excelente      | ✅ Bueno      | ✅ Estimado    |
| **Resultados**         | ✅ Excelente | ✅ Excelente      | ✅ Excelente  | ✅ Estimado    |
| **xG/xGA**             | ✅ Premium   | ❌ Solo pago      | ✅ Gratis     | ✅ Estimado    |
| **Corners/Shots**      | ✅ Premium   | ❌ Solo pago      | ✅ Gratis     | ✅ Estimado    |
| **Lesiones**           | ✅ Premium   | ❌ No disponible  | ⚠️ Manual     | ❌ No          |
| **Rate Limit**         | ⚠️ 10/min    | ✅ 10/min         | ✅ Flexible   | ✅ Ilimitado   |
| **Daily Limit**        | ⚠️ 100       | ✅ Sin límite     | ✅ Sin límite | ✅ Sin límite  |
| **Costo**              | Gratuito     | Gratuito          | Gratuito      | Gratuito       |
| **Mantenimiento**      | ✅ Bajo      | ✅ Bajo           | ⚠️ Medio      | ✅ Bajo        |
| **Confiabilidad**      | ✅ Alta      | ✅ Alta           | ⚠️ Media      | ✅ Alta        |
| **Ligas Soportadas**   | ✅ Muchas    | ✅ Top 5          | ✅ Top 5      | ✅ Cualquiera  |

**Recomendación**: Implementar las 3 opciones (Football-Data.org, FBref, SimpleProvider) con sistema de fallback inteligente.

---

## Roadmap de Implementación

### Fase 1: Cliente Football-Data.org (2-3 horas)
- [ ] Crear `bet_copilot/api/football_data_client.py`
- [ ] Implementar endpoints básicos (fixtures, teams, standings)
- [ ] Añadir rate limiting y error handling
- [ ] Tests unitarios

### Fase 2: Scraper FBref (4-5 horas)
- [ ] Crear `bet_copilot/scrapers/fbref_scraper.py`
- [ ] Implementar scraping de team stats (xG, corners, shots)
- [ ] Cache agresivo (disk + memory)
- [ ] Rate limiting manual (1 request cada 2s)
- [ ] User agent rotation
- [ ] Tests con HTML fixtures

### Fase 3: Integración con Fallback (1-2 horas)
- [ ] Actualizar `FootballClientWithFallback`
- [ ] Añadir Football-Data.org como provider principal
- [ ] Añadir FBref como provider secundario
- [ ] Mantener SimpleProvider como último fallback
- [ ] Tests de integración

### Fase 4: Mejoras Opcionales (2-3 horas)
- [ ] Scraper de Transfermarkt para lesiones
- [ ] Dashboard de health de providers
- [ ] Métricas de uso por provider
- [ ] Auto-switch de providers basado en performance

**Tiempo estimado total**: 9-13 horas de desarrollo

---

## Consideraciones Éticas y Legales

### Web Scraping
- ✅ **Respetar robots.txt** de cada sitio
- ✅ **Rate limiting agresivo** (1 request cada 2-3 segundos)
- ✅ **User-Agent honesto** identificando el proyecto
- ✅ **Cache extensivo** para minimizar requests
- ✅ **Uso personal/educativo** (no comercial sin permiso)

### Ejemplo robots.txt check
```python
from urllib.robotparser import RobotFileParser

def can_scrape(url: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)
```

---

**Estado**: ✅ Investigación completa  
**Próximo paso**: Implementar Fase 1 (Football-Data.org client)
