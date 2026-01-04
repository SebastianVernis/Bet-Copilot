# Guía Rápida - Bet-Copilot 🎯

**Para usuarios que quieren empezar YA.**

---

## ⚡ Inicio en 3 Pasos

### 1. Instalar

```bash
git clone <repo-url>
cd Bet-Copilot
pip install -r requirements.txt
```

### 2. Configurar

```bash
cp .env.example .env
nano .env  # o tu editor favorito
```

Pegar tus claves API:
```bash
ODDS_API_KEY=tu_clave_de_theoddsapi
API_FOOTBALL_KEY=tu_clave_aqui
GEMINI_API_KEY=tu_clave_aqui
```

### 3. Ejecutar

```bash
./START.sh
# o
python main.py
```

---

## 🎮 Comandos Esenciales

```bash
# Ver ayuda
bet-copilot> ayuda

# Verificar que todo funciona
bet-copilot> salud

# Ver partidos disponibles
bet-copilot> mercados

# Analizar un partido
bet-copilot> analizar <nombre del partido>

# Ver dashboard completo
bet-copilot> dashboard

# Salir
bet-copilot> salir
```

---

## 💡 Flujo de Trabajo Típico

### Caso 1: Análisis Rápido (2 minutos)

```bash
# 1. Iniciar
$ python main.py

# 2. Ver qué hay
bet-copilot> mercados
Se encontraron 26 eventos
  • Leeds United vs Manchester United
  • Arsenal vs Chelsea
  ...

# 3. Analizar el que te interese
bet-copilot> analizar Leeds United vs Manchester United

Partido: Leeds United vs Manchester United
Probabilidad del Modelo: 48.5%
Cuota del Bookmaker: 2.15
Valor Esperado: +4.3%

Recomendación Kelly:
  Apuesta: 1.08% del bankroll
  Nivel de Riesgo: BAJO

# 4. Salir
bet-copilot> salir
```

### Caso 2: Vigilancia Continua

```bash
# 1. Ver mercados
bet-copilot> mercados

# 2. Abrir dashboard
bet-copilot> dashboard

# 3. Monitorear en tiempo real
# (El dashboard se actualiza automáticamente)

# 4. Ctrl+C para salir del dashboard
# 5. Continuar con otros comandos o salir
```

### Caso 3: Multi-Liga

```bash
# Premier League
bet-copilot> mercados
bet-copilot> analizar <partido>

# La Liga
bet-copilot> mercados soccer_la_liga
bet-copilot> analizar <partido español>

# Serie A
bet-copilot> mercados soccer_serie_a
bet-copilot> analizar <partido italiano>
```

---

## 🔑 Obtener API Keys (Gratis)

### The Odds API (Requerida)

1. Ir a: https://the-odds-api.com/
2. Crear cuenta (email + password)
3. Verificar email
4. Copiar API key del dashboard
5. Pegar en `.env`

**Límite gratuito**: 500 requests/mes

### API-Football (Opcional)

1. Ir a: https://www.api-football.com/
2. Crear cuenta
3. Suscribirse al plan gratuito
4. Copiar API key
5. Pegar en `.env`

**Límite gratuito**: 100 requests/día

### Gemini AI (Opcional)

1. Ir a: https://makersuite.google.com/app/apikey
2. Crear API key con cuenta de Google
3. Copiar la clave
4. Pegar en `.env`

**Límite gratuito**: Generoso (varía)

---

## 🎨 Interpretando Resultados

### Expected Value (EV)

```
EV > +5%   →  Apuesta de ALTO valor  (verde)
EV 0-5%    →  Apuesta de valor leve   (amarillo)
EV < 0%    →  NO apostar              (rojo)
```

### Recomendación Kelly

```
Apuesta: X% del bankroll
```

**Ejemplo**: Si tienes $1,000 y Kelly recomienda 2.5%, apuesta $25.

**Importante**: El sistema usa 1/4 Kelly (conservador). Si quieres ser más agresivo, multiplica por 4.

### Nivel de Riesgo

```
BAJO    →  < 1% del bankroll
MEDIO   →  1-3% del bankroll
ALTO    →  > 3% del bankroll
```

---

## ⚠️ Limitaciones

### Modelo Actual

El sistema usa un **modelo simplificado**:
- Probabilidad implícita + 5% de ajuste
- No usa estadísticas reales (xG, forma, H2H)
- Suficiente para demostración, **mejorable para producción**

### Para Mejorar

1. Integrar stats de API-Football
2. Usar predictor Poisson con xG real
3. Activar análisis de Gemini
4. Agregar backtesting

---

## 🐛 Problemas Comunes

### "Circuit breaker is open"

**Causa**: Llegaste al rate limit del API  
**Solución**: Espera 60 segundos

```bash
# Ver estado
bet-copilot> salud

# Esperar y reintentar
```

### "Partido no encontrado"

**Causa**: No has cargado mercados o el nombre está mal  
**Solución**:

```bash
# 1. Cargar mercados primero
bet-copilot> mercados

# 2. Usar nombre exacto del listado
bet-copilot> analizar Leeds United vs Manchester United
```

### "API key not configured"

**Causa**: `.env` no existe o está vacío  
**Solución**:

```bash
# Verificar que .env existe
cat .env

# Si no existe
cp .env.example .env
nano .env  # Agregar claves
```

---

## 📊 Ejemplo Real

### Sesión Completa (5 minutos)

```bash
$ ./START.sh

╔═══════════════════════════════════════╗
║           BET-COPILOT            ║
║   Sistema de Análisis Especulativo   ║
╚═══════════════════════════════════════╝

⚠️  Herramienta de soporte a decisiones, NO asesoría financiera.

bet-copilot> salud

Verificando salud de las APIs...

✓ The Odds API
✓ API-Football
⚠ Gemini AI: No disponible


bet-copilot> mercados

Obteniendo mercados para soccer_epl...

Se encontraron 26 eventos

  • Leeds United vs Manchester United
    2026-01-04 12:30
  • Everton vs Brentford
    2026-01-04 15:00
  • Newcastle United vs Crystal Palace
    2026-01-04 15:00


bet-copilot> analizar Leeds United vs Manchester United

Analizando: Leeds United vs Manchester United

Partido: Leeds United vs Manchester United
Mercado: Home Win
Probabilidad del Modelo: 48.5%
Cuota del Bookmaker: 2.15
Valor Esperado: +4.3%
Bookmaker: Bet365

Recomendación Kelly:
  Apuesta: 1.08% del bankroll
  Nivel de Riesgo: BAJO
  ⚠ Por debajo del umbral de valor


bet-copilot> dashboard

Iniciando dashboard...
Presiona Ctrl+C para salir

[Dashboard con 4 zonas mostrando datos en tiempo real]

^C

bet-copilot> salir

¡Gracias por usar Bet-Copilot!
```

---

## 💰 Interpretación de Value Bets

### ¿Qué es una Value Bet?

Cuando tu modelo estima una probabilidad **mayor** que la implícita en las cuotas del bookmaker.

**Ejemplo**:
```
Tu modelo: 55% de probabilidad de ganar
Cuota bookmaker: 2.10 (implica ~47.6%)
Edge: 55% - 47.6% = +7.4%
EV: (0.55 × 2.10) - 1 = +15.5%

→ HAY VALOR (apostar según Kelly)
```

### ¿Cuánto Apostar?

Usa la **Recomendación Kelly**:

```
Bankroll: $1,000
Kelly recomienda: 2.5%
Apuesta: $25
```

**Regla de oro**: Nunca apuestes más del 5% de tu bankroll en una sola apuesta.

---

## 🎓 Tips Avanzados

### 1. Usar con Múltiples Ligas

```bash
# Crea un script para escanear todas
bet-copilot> mercados soccer_epl
bet-copilot> mercados soccer_la_liga
bet-copilot> mercados soccer_serie_a
bet-copilot> mercados soccer_bundesliga
```

### 2. Filtrar por EV Alto

En el dashboard, los mercados se ordenan por EV. Los primeros son los de mayor valor.

### 3. Verificar Antes de Apostar

```bash
# 1. Ver análisis
bet-copilot> analizar <partido>

# 2. Verificar dashboard para contexto
bet-copilot> dashboard

# 3. Verificar salud de APIs
bet-copilot> salud

# 4. Decidir manualmente
```

### 4. Conservar Quota de API

```bash
# El sistema cachea por 30 minutos
# Si recargas mercados muy seguido, gastas quota
# Espera al menos 5-10 min entre recargas
```

---

## 🔒 Seguridad

### API Keys

- ✅ Nunca commitees `.env` a git (ya está en `.gitignore`)
- ✅ No compartas tus claves con nadie
- ✅ Rota claves si crees que están comprometidas

### Datos

- ✅ Todo se guarda localmente (SQLite)
- ✅ No se envía información a terceros
- ✅ No tracking ni analytics

---

## 📞 Ayuda

### Documentación

- **Esta guía**: Inicio rápido
- **INSTALLATION.md**: Instalación detallada
- **README.md**: Overview completo
- **TRADUCCION.md**: Detalles de traducción

### Soporte

- GitHub Issues para bugs
- Documentación técnica en `AGENTS.md`

---

## 🎉 ¡Listo!

Ya estás preparado para usar Bet-Copilot. Recuerda:

1. ⚠️ **No es asesoría financiera**
2. 🧮 **Usa matemáticas, no emociones**
3. 💰 **Nunca apuestes más del 5% de tu bankroll**
4. 📊 **Verifica siempre antes de ejecutar**
5. 🎯 **El sistema informa, tú decides**

---

**¡Buena suerte y apuesta responsablemente!** 🍀

---

**Versión**: 0.3.2  
**Fecha**: 2026-01-04  
**Idioma**: Español
