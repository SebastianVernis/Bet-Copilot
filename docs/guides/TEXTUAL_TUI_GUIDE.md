# 🎮 Guía Completa del Textual TUI

**Dashboard Interactivo en Terminal** - Análisis en tiempo real con widgets reactivos.

---

## 🚀 Inicio Rápido

```bash
# Iniciar TUI
python textual_main.py

# Demo con instrucciones
python examples/demo_textual_tui.py
```

---

## 📊 Layout del Dashboard

```
┌────────────────────────────────────────────────────────────┐
│ ⚽ BET-COPILOT v0.6 - Multi-AI Analysis Dashboard         │
├────────────────────────────────────────────────────────────┤
│ ┌─── API Health ───┐ ┌─── Live News Feed ──────────────┐ │
│ │ 🟢 Odds API       │ │ 📰 Loading news...              │ │
│ │ 🟢 Football API   │ │ 2h ⚽ Arsenal injury update      │ │
│ │ ⚪ Gemini AI      │ │ 5h 🔄 Chelsea transfer news     │ │
│ │ ⚪ Blackbox AI    │ │ 1d ⚽ Liverpool match preview    │ │
│ └──────────────────┘ └─────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│ ┌─── Match Prediction ──┐ ┌─── Market Watch ───────────┐ │
│ │ Arsenal vs Chelsea    │ │ Match          Market   EV  │ │
│ │                       │ │ ────────────────────────────│ │
│ │ Expected Goals:       │ │ Arsenal vs     Home Win +8% │ │
│ │   Home: 1.85          │ │ Chelsea                     │ │
│ │   Away: 1.42          │ │                             │ │
│ │                       │ │ Liverpool vs   Away Win +12%│ │
│ │ Win Probabilities:    │ │ Man City                    │ │
│ │   Home: 38.5%         │ │                             │ │
│ │   Draw: 29.3%         │ │ Last update: 14:32:45       │ │
│ │   Away: 32.2%         │ └────────────────────────────┘ │
│ │                       │                                │
│ │ Most Likely: 2-1      │                                │
│ │ AI Confidence: ⭐⭐⭐⭐  │                                │
│ └───────────────────────┘                                │
├────────────────────────────────────────────────────────────┤
│ ┌─── Alternative Markets ──────────────────────────────┐  │
│ │ 🏁 Corners: 11.2  🟨 Cards: 4.6  🎯 Shots: 24.8     │  │
│ └──────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│ Arsenal vs Chelsea ▌                    [Analyze] [Refresh]│
└────────────────────────────────────────────────────────────┘
```

---

## 🎮 Controles

### Teclado (Shortcuts)

| Tecla | Acción | Descripción |
|-------|--------|-------------|
| **r** | Refresh All | Actualiza APIs + News + Markets |
| **a** | Analyze | Procesa el input actual |
| **n** | Toggle News | Muestra/oculta feed de noticias |
| **m** | Toggle Markets | Muestra/oculta mercados alternativos |
| **q** | Quit | Salir (con cleanup) |
| **Ctrl+C** | Force Quit | Salida forzada |

### Input de Texto

```bash
# Analizar partido
Arsenal vs Chelsea
Man City vs Liverpool
Real Madrid vs Barcelona

# El análisis se ejecuta al presionar Enter
```

### Botones

- **[Analyze]** - Mismo que presionar Enter en input
- **[Refresh]** - Mismo que presionar 'r'

---

## 📊 Widgets Explicados

### 1. API Health Monitor 🏥

**Ubicación**: Top-left  
**Color**: Verde

Muestra el estado de cada API:
- 🟢 **Healthy**: API disponible y funcionando
- 🟡 **Degraded**: API con problemas
- 🔴 **Down**: API no disponible
- ⚪ **Unknown**: No configurada

**Request counters**:
```
🟢 Odds API       123/500 daily
🟢 Football API    45/100 daily
```

### 2. Live News Feed 📰

**Ubicación**: Top-right  
**Color**: Cyan

Feed en vivo de noticias de fútbol:
- **Fuentes**: BBC Sport, ESPN
- **Auto-refresh**: Cada 30 minutos
- **Categorías**:
  - 🏥 Injuries (lesiones)
  - 🔄 Transfers (fichajes)
  - ⚽ Match previews
  - 📋 General

**Formato**:
```
2h ⚽ Arsenal squad news ahead of Chelsea clash
    BBC Sport
```

### 3. Match Prediction ⚽

**Ubicación**: Middle-left  
**Color**: Cyan

Predicción Poisson del partido analizado:
- **Expected Goals**: Lambda de cada equipo
- **Win Probabilities**: Home/Draw/Away %
- **Most Likely Score**: Resultado más probable
- **AI Confidence**: Confianza del análisis IA (⭐⭐⭐⭐⭐)

**Ejemplo**:
```
Arsenal vs Chelsea

Expected Goals:
  Home: 1.85  |  Away: 1.42

Win Probabilities:
  Home: 38.5%
  Draw: 29.3%
  Away: 32.2%

Most Likely: 2-1
AI Confidence: ⭐⭐⭐⭐ (80%)
```

### 4. Market Watch 📊

**Ubicación**: Middle-right  
**Color**: Amarillo

**Tabla de mercados** con value bets:

| Columna | Descripción |
|---------|-------------|
| **Match** | Equipos del partido |
| **Market** | Tipo de mercado (Home Win, Draw, Away Win) |
| **EV** | Expected Value (%) |
| **Odds** | Cuota decimal |
| **Conf** | Confianza IA (⭐⭐⭐⭐⭐) |

**Colores**:
- **Verde (bold)**: ✅ Value bet confirmado (✓ en nombre)
- **Amarillo**: EV positivo pero < threshold
- **Dim**: EV negativo (no apostar)

**Auto-refresh**: Cada 5 minutos escanea top matches

### 5. Alternative Markets 📐

**Ubicación**: Bottom  
**Color**: Magenta

Resumen rápido de mercados alternativos:

```
🏁 Corners: 11.2  🟨 Cards: 4.6  🎯 Shots: 24.8
```

- **Corners** (🏁): Esquinas esperadas
- **Cards** (🟨): Tarjetas esperadas
- **Shots** (🎯): Tiros totales esperados

**Actualización**: Cada análisis de partido

---

## 🔄 Auto-Refresh

| Widget | Intervalo | Acción |
|--------|-----------|--------|
| News Feed | 30 min | Fetch RSS feeds |
| Market Watch | 5 min | Scan top matches |
| API Health | On-demand | Press 'r' |

---

## 💡 Workflow Típico

### Sesión de Análisis

1. **Iniciar TUI**
   ```bash
   python textual_main.py
   ```

2. **Revisar News** (panel top-right)
   - Últimas noticias auto-cargadas
   - Ver lesiones, fichajes, previews

3. **Analizar Partido Específico**
   ```
   Input: Arsenal vs Chelsea
   Press: Enter
   ```

4. **Ver Resultados**:
   - **Prediction**: Goles esperados, probabilidades
   - **Market Watch**: 3 mercados (Home/Draw/Away) con EV
   - **Alt Markets**: Corners, cards, shots

5. **Evaluar Value Bets**:
   - Verde bold con ✓ = Apuesta de valor
   - EV > +5% típicamente
   - Revisar confianza IA

6. **Analizar Otro Partido**:
   - Escribir nuevo match
   - Repeat

7. **Refresh Periódico**:
   - Presionar 'r' para actualizar todo
   - O esperar auto-refresh

8. **Salir**:
   - Presionar 'q'
   - Cleanup automático

---

## 🎯 Casos de Uso

### Monitoring Continuo

**Objetivo**: Vigilar mercados buscando value bets

1. Iniciar TUI
2. Presionar 'r' para escanear
3. Market Watch se puebla con top 5 matches
4. Value bets aparecen en verde
5. Refresh cada 5 min automático

### Análisis Individual

**Objetivo**: Analizar un partido específico en detalle

1. Escribir match en input
2. Ver predicción completa
3. Evaluar 3 mercados principales
4. Revisar mercados alternativos
5. Comparar con cuotas del bookmaker

### Research Mode

**Objetivo**: Investigar múltiples partidos

1. Analizar partido 1
2. Tomar nota de value bets
3. Analizar partido 2
4. Comparar predicciones
5. Identificar mejores oportunidades

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env
ODDS_API_KEY=your_key           # Para cuotas reales
API_FOOTBALL_KEY=your_key       # Para stats detalladas
GEMINI_API_KEY=your_key         # Para análisis IA
BLACKBOX_API_KEY=your_key       # Fallback IA
```

### Sin API Keys

El TUI funciona **sin API keys** usando:
- SimpleAnalyzer (análisis local)
- Datos estimados por tier de equipo
- News feed RSS (gratis)

**Limitaciones sin APIs**:
- No cuotas en tiempo real
- No stats detalladas de jugadores
- No análisis IA contextual
- Predicciones solo con Poisson básico

---

## 🐛 Troubleshooting

### News Feed Vacío

**Síntoma**: "🔄 Loading news..." permanente

**Solución**:
```bash
# Check network
ping bbc.com

# Test news scraper
python -c "from bet_copilot.news import NewsScraper; import asyncio; scraper = NewsScraper(); asyncio.run(scraper.fetch_all_news())"
```

### Market Watch Vacío

**Síntoma**: No aparecen mercados al presionar 'r'

**Causas**:
1. Sin ODDS_API_KEY configurada
2. Rate limit alcanzado
3. No hay partidos próximos

**Solución**:
- Configurar ODDS_API_KEY en .env
- Analizar partido específico (input manual)
- Ver API Health para diagnóstico

### Prediction Widget Vacío

**Síntoma**: "No prediction available"

**Causas**:
1. Partido no encontrado en Odds API
2. Nombres de equipos incorrectos
3. No hay datos disponibles

**Solución**:
- Usar nombres exactos (e.g., "Arsenal" no "The Arsenal")
- Ver log: `tail -f bet_copilot.log`
- Probar con partido conocido: "Man City vs Liverpool"

### Crash al Iniciar

**Síntoma**: Error AttributeError o ImportError

**Solución**:
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# Verificar Textual
python -c "import textual; print(textual.__version__)"

# Debe ser >= 0.40.0 (recomendado 7.0.0+)
```

---

## 🔥 Tips & Tricks

### 1. Scan Rápido de Mercados

```bash
# En lugar de esperar 5 min, forzar:
Press: r (Refresh All)
```

### 2. Ver Solo Value Bets

Markets en **verde bold con ✓** son value bets confirmados.  
Resto son informativos pero no cumplen threshold (EV < 5%).

### 3. Comparar con Bookmaker

1. Analizar partido en TUI
2. Ver EV y cuotas predichas
3. Comparar con tu bookmaker
4. Si cuotas mejores → value aumenta
5. Si cuotas peores → value disminuye

### 4. Usar Alt Markets

```bash
# Después de analizar:
1. Ver "Alternative Markets" panel
2. Si Corners: 11.2 → Buscar Over 10.5 en bookmaker
3. Si Cards: 4.6 → Buscar Over 4.5
4. Comparar cuotas
```

### 5. Historial de Sesión

TUI muestra **último análisis** en Prediction widget.  
Para múltiples análisis:
- Tomar screenshots (terminal)
- Copiar datos manualmente
- O usar CLI mode: `python main.py` (guarda logs)

---

## 📈 Interpretación de Datos

### Expected Value (EV)

| EV | Interpretación | Acción |
|----|----------------|--------|
| **> +10%** | 🔥 Excelente value | Apostar (si confianza alta) |
| **+5% a +10%** | ✅ Buen value | Considerar |
| **0% a +5%** | ⚠️ Value marginal | Evaluar confianza |
| **< 0%** | ❌ No value | No apostar |

### Confianza IA

```
⭐⭐⭐⭐⭐ (5 estrellas) = 100% confianza
⭐⭐⭐⭐ (4 estrellas)   = 80% confianza
⭐⭐⭐ (3 estrellas)     = 60% confianza
⭐⭐ (2 estrellas)       = 40% confianza
⭐ (1 estrella)         = 20% confianza
```

**Nota**: Confianza ≥ 60% + EV ≥ +5% = Señal fuerte

### Probabilidades

```
Home: 38.5%  }
Draw: 29.3%  } → Deben sumar ~100%
Away: 32.2%  }

Si suman > 105% → Overround del modelo (normal)
Si suman < 95%  → Error (reportar)
```

---

## 🎨 Personalización

### Colores del Dashboard

Editar `bet_copilot/ui/textual_app.py`:

```python
# Cambiar colores de widgets
#api-health {
    border: solid green;    # Cambiar a blue, red, etc.
}

#market-watch {
    border: solid yellow;   # Cambiar color
}
```

### Refresh Intervals

```python
# NewsWidget - línea ~102
self.set_interval(1800, self.refresh_news)  # 30 min → Cambiar

# MarketWatchWidget - línea ~201
self.set_interval(300, self.refresh_markets)  # 5 min → Cambiar
```

### Tamaño de Layout

```python
# CSS - línea ~410
#prediction {
    width: 2fr;  # Cambiar proporción
}

#market-watch {
    width: 3fr;  # Cambiar proporción
}
```

---

## 🔍 Logs y Debug

### Ver Logs en Tiempo Real

```bash
# Terminal 1: TUI
python textual_main.py

# Terminal 2: Logs
tail -f bet_copilot.log
```

### Log Levels

```python
# bet_copilot/config.py
import logging
logging.basicConfig(level=logging.DEBUG)  # Más verbose
```

### Debug Mode

```python
# textual_main.py
from bet_copilot.ui.textual_app import BetCopilotApp

app = BetCopilotApp()
app.run(log="textual_debug.log")  # Debug de Textual
```

---

## 🚀 Performance

### Optimizaciones Aplicadas

1. **Async I/O**: Todas las llamadas API son async
2. **Reactive Widgets**: Solo re-render lo que cambia
3. **Lazy Loading**: News/Markets se cargan bajo demanda
4. **Cleanup**: Recursos liberados al salir

### Consumo de Recursos

```
CPU: ~5-10% idle, ~20-30% durante análisis
RAM: ~50-100 MB
Network: ~1-5 MB por análisis completo
```

### Rate Limits

**Con auto-refresh cada 5 min**:
- Odds API: ~288 requests/día (de 500 disponibles)
- Football API: ~60 requests/día (de 100 disponibles)

**Recomendación**: 
- Desactivar auto-refresh si límites apretados
- Usar refresh manual ('r') solo cuando necesites

---

## 📚 Recursos Adicionales

### Documentación
- [Textual Docs](https://textual.textualize.io/)
- [TEXTUAL_INTEGRATION.md](../TEXTUAL_INTEGRATION.md) - Detalles técnicos
- [AGENTS.md](../AGENTS.md) - Arquitectura del sistema

### Ejemplos
- `examples/demo_textual_tui.py` - Demo con instrucciones
- `examples/example_enhanced_analysis.py` - Análisis programático
- `test_textual_quick.py` - Tests de integración

---

## ✅ Checklist de Uso

### Primera Vez
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Configurar API keys en `.env` (opcional)
- [ ] Ejecutar test: `python test_textual_quick.py`
- [ ] Iniciar demo: `python examples/demo_textual_tui.py`

### Sesión Típica
- [ ] Iniciar TUI: `python textual_main.py`
- [ ] Revisar news feed
- [ ] Presionar 'r' para escanear mercados
- [ ] Analizar partidos específicos
- [ ] Evaluar value bets (verde bold)
- [ ] Salir con 'q'

---

## 🎉 Ventajas del TUI vs CLI

| Característica | CLI (Rich) | TUI (Textual) |
|----------------|------------|---------------|
| **Live Updates** | ❌ | ✅ Auto-refresh |
| **Multi-Panel** | ❌ | ✅ 5 widgets simultáneos |
| **News Feed** | Manual | ✅ Automático |
| **Market Scan** | No | ✅ Cada 5 min |
| **Shortcuts** | No | ✅ r/a/n/m/q |
| **Persistencia** | Scroll up | ✅ Widgets fijos |
| **Ideal para** | Análisis único | Monitoring continuo |

---

**¿Dudas?** Revisa [TROUBLESHOOTING](../TROUBLESHOOTING.md) o abre un issue.

**Happy analyzing!** ⚽📊✨
