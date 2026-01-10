# ⚽ Bet-Copilot v0.6.1

**AI-Powered Sports Betting Analysis Platform**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot)

---

## 🎯 Descripción

Bet-Copilot es una plataforma avanzada de análisis de apuestas deportivas que combina:
- 📊 **Análisis Matemático**: Predicciones Poisson, Kelly Criterion
- 🤖 **Multi-AI Analysis**: Blackbox AI, Gemini, análisis colaborativo
- 📰 **Live News Feed**: Noticias en tiempo real de múltiples fuentes
- 📈 **Alternative Markets**: Corners, cards, shots predictions
- 🎨 **Dual Interface**: CLI (Rich) y TUI (Textual)

---

## ✨ Características Principales

### 🔥 Nuevas en v0.6.1
- ✅ **Navegación con Scroll**: CLI y TUI con paginación completa
- ✅ **No más información cortada**: Acceso a todo el contenido
- ✅ **Controles intuitivos**: Flechas, Page Up/Down, mouse wheel

### Core Features
- 🎯 **Match Analysis**: Análisis completo de partidos con múltiples fuentes
- 📊 **Poisson Predictions**: Predicciones matemáticas basadas en estadísticas
- 💰 **Kelly Criterion**: Gestión de bankroll y stakes recomendados
- 🤖 **Multi-AI Consensus**: Análisis colaborativo de múltiples IAs
- 📰 **Real-time News**: Feed de noticias de lesiones, transferencias, etc.
- 📐 **Alternative Markets**: Corners, cards, shots, offsides
- 🎨 **Dual Interface**: CLI interactivo y TUI dashboard

### Data Sources
- 🏆 **The Odds API**: Cuotas en tiempo real
- ⚽ **API-Football**: Estadísticas, alineaciones, H2H
- 🤖 **Blackbox AI / Gemini**: Análisis contextual avanzado
- 📰 **Multiple News Sources**: BBC Sport, ESPN, Sky Sports, etc.

---

## 📜 Navegación con Scroll

### CLI (Rich-based)

Cuando hay contenido largo, se activa automáticamente el paginador:

```bash
> mercados soccer_epl
Se encontraron 38 eventos
Presiona 'q' para salir del scroll

  • Arsenal vs Chelsea
  • Manchester City vs Liverpool
  ... [navegación completa]

# Controles:
# ↑/↓ : Navegar línea por línea
# Space/b : Página siguiente/anterior
# q : Salir del paginador
```

### TUI (Textual-based)

Todos los widgets tienen scroll independiente:

```bash
python textual_main.py

# Controles:
# ↑/↓ : Scroll vertical
# Page Up/Down : Página completa
# Mouse Wheel : Scroll con mouse
```

Ver documentación completa: [docs/SCROLL_NAVIGATION.md](docs/SCROLL_NAVIGATION.md)

---

## 🚀 Instalación

### ⚡ Opción 1: Gitpod (Más Rápido - 2 minutos)

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/SebastianVernis/Bet-Copilot)

- ✅ **50 horas/mes gratis**
- ✅ **Docker preinstalado**
- ✅ **Web terminal con SSL automático**
- ✅ **No requiere instalación local**

Ver guía: [GITPOD_QUICKSTART.md](GITPOD_QUICKSTART.md)

---

### 🖥️ Opción 2: Instalación Local

#### Requisitos
- Python 3.8 o superior
- pip (gestor de paquetes)
- API Keys (opcionales para funcionalidad completa)

#### Pasos

```bash
# Clonar repositorio
git clone https://github.com/SebastianVernis/Bet-Copilot.git
cd Bet-Copilot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

---

### 🐳 Opción 3: Web Terminal (Docker)

Despliegue contenedorizado con ttyd:

```bash
# 1. Configurar credenciales
cp docker/.env.example docker/.env
nano docker/.env  # Editar con tus API keys

# 2. Desplegar
./scripts/deploy_alpha.sh

# 3. Acceder
# http://localhost:7681
```

Ver guía completa: [docs/web_terminal/SETUP.md](docs/web_terminal/SETUP.md)

### Configuración de API Keys

Edita el archivo `.env`:

```bash
# The Odds API (requerido para cuotas)
ODDS_API_KEY=tu_odds_api_key

# API-Football (requerido para estadísticas completas)
API_FOOTBALL_KEY=tu_api_football_key

# AI Services (al menos uno requerido)
BLACKBOX_API_KEY=tu_blackbox_key
GEMINI_API_KEY=tu_gemini_key
```

Obtén tus API keys:
- The Odds API: https://the-odds-api.com/
- API-Football: https://www.api-football.com/
- Blackbox AI: https://www.blackbox.ai/
- Google Gemini: https://ai.google.dev/

---

## 💻 Uso

### CLI Interactivo

```bash
python main.py

# Comandos disponibles:
> mercados                    # Ver mercados disponibles
> mercados soccer_la_liga     # Mercados de una liga específica
> analizar Arsenal vs Chelsea # Analizar un partido
> salud                       # Estado de las APIs
> ayuda                       # Ver ayuda completa
> salir                       # Salir de la aplicación
```

### TUI Dashboard

```bash
python textual_main.py

# Interface interactiva con:
# - API Health Monitor
# - Live News Feed
# - Match Predictions
# - Market Watch
# - Alternative Markets Summary
```

### Atajos de Teclado (TUI)

```
q              Salir
r              Refresh all
n              Toggle news
m              Toggle alternative markets
Ctrl+C         Salir
↑/↓            Scroll en widgets
Page Up/Down   Scroll de página
```

---

## 📊 Ejemplo de Análisis

```bash
> analizar Manchester City vs Liverpool

╔═══ Manchester City vs Liverpool ═══╗
Liga: Premier League
Fecha: 2026-01-15 20:00

📊 Estadísticas de Equipos

Métrica              Man City    Liverpool
──────────────────────────────────────────
Partidos Jugados     20          20
Forma (últimos 5)    WWWWD       WWDWW
Goles Promedio       2.45        2.30
Goles Recibidos      0.85        1.05

🎲 Predicción Matemática (Poisson)

Expected Goals: 2.12 - 1.67
Probabilidades:
  Victoria Local: 48.5%
  Empate: 25.2%
  Victoria Visitante: 26.3%
Score más probable: 2-1 (15.3%)

🤖 Análisis Contextual (Multi-AI)

Confianza: 78%
Sentimiento: positive_home
Razonamiento: Man City domina en casa con alta posesión...

💰 Mejor Apuesta de Valor

Resultado: Home Win
Equipo: Manchester City
Cuota: 2.10
Valor Esperado: +8.5%
Apuesta Recomendada: 4.2% del bankroll
Nivel de Riesgo: MEDIO

# Presiona 'q' para volver al CLI
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest bet_copilot/tests/test_cli.py -v
pytest bet_copilot/tests/test_ai_client.py -v

# Con coverage
pytest --cov=bet_copilot --cov-report=html

# Test de scroll
python test_scroll_cli.py
```

---

## 📁 Estructura del Proyecto

```
Bet-Copilot/
├── bet_copilot/
│   ├── ai/                 # AI clients (Blackbox, Gemini, Multi-AI)
│   ├── api/                # API clients (Odds API, API-Football)
│   ├── math_engine/        # Poisson, Kelly, Alternative Markets
│   ├── services/           # Match Analyzer, Data Aggregator
│   ├── ui/                 # CLI y TUI interfaces
│   ├── news/               # News scraping y aggregation
│   └── tests/              # Unit tests
├── docs/
│   ├── SCROLL_NAVIGATION.md      # Guía de navegación
│   └── changelogs/
│       └── CHANGELOG_v0.6.1.md   # Changelog actual
├── main.py                 # Entry point CLI
├── textual_main.py        # Entry point TUI
├── requirements.txt       # Dependencias
└── .env.example          # Template de configuración
```

---

## 🔧 Configuración Avanzada

### Cambiar Pager del Sistema (CLI)

```bash
# Linux/Mac
export PAGER="less -R"    # Con colores
export PAGER="most"       # Alternativa avanzada

# En .bashrc o .zshrc para permanencia
echo 'export PAGER="less -R"' >> ~/.bashrc
```

### Ajustar Altura de Widgets (TUI)

Edita `bet_copilot/ui/textual_app.py`:

```python
CSS = """
    #prediction {
        height: 25;  # Ajusta altura
    }
"""
```

---

## 🐛 Solución de Problemas

### Error: "No se encontraron eventos"
- Verifica tu API key de The Odds API
- Confirma que tienes créditos disponibles
- Revisa la key en `.env`

### Error: "AI Analysis failed"
- Confirma que tienes al menos una AI key configurada
- El sistema fallback a SimpleAnalyzer si no hay IAs disponibles

### Scroll no funciona
- En CLI: Verifica que tu terminal soporte pagers (`less`/`more`)
- En TUI: Usa flechas ↑/↓ o Page Up/Down

### API Rate Limits
- The Odds API: 500 requests/mes (free tier)
- API-Football: 100 requests/día (free tier)
- Considera upgrade si necesitas más requests

---

## 📚 Documentación

- [Navegación con Scroll](docs/SCROLL_NAVIGATION.md)
- [Changelog v0.6.1](docs/changelogs/CHANGELOG_v0.6.1.md)
- [Branch Plan](BRANCH_PLAN.md)
- [Status Branches](STATUS_BRANCHES.md)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 🌟 Roadmap

### v0.6.2 (Próxima)
- [ ] Indicadores de posición en scroll
- [ ] Búsqueda dentro del pager
- [ ] Bookmarks en contenido largo
- [ ] Export de análisis a archivo

### v0.7.0 (Futuro)
- [ ] Machine Learning predictions
- [ ] Historical data analysis
- [ ] Backtesting framework
- [ ] Web dashboard

---

## 📞 Contacto

**Sebastian Vernis**  
GitHub: [@SebastianVernis](https://github.com/SebastianVernis)  
Email: sebastian.vernis@example.com

---

## 🙏 Agradecimientos

- The Odds API por las cuotas en tiempo real
- API-Football por estadísticas completas
- Blackbox AI y Google Gemini por análisis inteligente
- Rich y Textual por interfaces increíbles

---

## ⚠️ Disclaimer

Este software es solo para fines educativos e informativos. Las apuestas conllevan riesgos financieros. Apuesta responsablemente y solo lo que puedas permitirte perder. El análisis proporcionado no garantiza ganancias.

---

**Versión:** 0.6.1  
**Fecha:** 2026-01-09  
**Estado:** ✅ Activo y en desarrollo

**🎉 ¡Disfruta del análisis con navegación completa!**
