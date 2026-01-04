# 🤖 Sistema de Fallback AI - Bet-Copilot

## 📋 Descripción

Sistema inteligente de fallback que usa **Gemini** como proveedor primario y **Blackbox AI** como respaldo automático cuando Gemini no está disponible o falla.

---

## ✨ Características

### 1. **Fallback Multi-Nivel**
- **Nivel 1**: Gemini (AI avanzada, requiere API key)
- **Nivel 2**: Blackbox (AI alternativa, funciona sin key)
- **Nivel 3**: SimpleAnalyzer (heurísticas, siempre disponible)
- Automático y transparente
- Sin intervención manual requerida
- **Garantía**: Siempre retorna un análisis válido

### 2. **Configuración Flexible**
```python
# Preferir Gemini (default)
ai_client = create_ai_client(prefer_gemini=True)

# Preferir Blackbox
ai_client = create_ai_client(prefer_gemini=False)

# Con API keys específicas
ai_client = create_ai_client(
    gemini_api_key="tu_key",
    blackbox_api_key="tu_key"
)
```

### 3. **Interfaz Unificada**
Misma interfaz para ambos proveedores:
```python
analysis = await ai_client.analyze_match_context(
    home_team="Arsenal",
    away_team="Chelsea",
    home_form="WWDLW",
    away_form="DWLWW",
    h2h_results=["H", "A", "D"],
    additional_context="Arsenal sin Saka"
)
```

---

## 🏗️ Arquitectura

```
AIClient (Unified)
├── Primary: Gemini (si API key configurada)
│   └── Ventajas: Mejor comprensión contextual, modelo grande
├── Fallback 1: Blackbox (si falla Gemini)
│   └── Ventajas: No requiere API key, rápido
└── Fallback 2: SimpleAnalyzer (siempre disponible)
    └── Ventajas: Sin dependencias externas, reglas estadísticas
```

### Flujo de Ejecución
```
1. Intentar con Primary (Gemini)
   ├─ ✓ Éxito → Retornar resultado
   └─ ✗ Fallo → Continuar
   
2. Intentar con Blackbox
   ├─ ✓ Éxito → Retornar resultado
   └─ ✗ Fallo → Continuar

3. Usar SimpleAnalyzer (garantizado)
   └─ ✓ Siempre retorna resultado válido

4. Log completo de toda la cadena
```

---

## 📦 Componentes

### 1. SimpleAnalyzer (Ultimate Fallback)
**Archivo**: `bet_copilot/ai/simple_analyzer.py`

**Características**:
- **Siempre disponible** (sin dependencias externas)
- Análisis basado en reglas heurísticas
- Usa forma reciente, H2H y contexto
- Ajustes conservadores (±10% max)
- Confianza máxima 80%

**Heurísticas**:
```python
# Form score: W=3pts, D=1pt, L=0pts
form_score = total_points / max_points

# Adjustments:
- Form > 0.3 diferencia → ±10% lambda
- H2H dominante → ±5% lambda
- Lesiones detectadas → -5% lambda por equipo
```

**Uso directo**:
```python
from bet_copilot.ai.simple_analyzer import SimpleAnalyzer

analyzer = SimpleAnalyzer()
analysis = await analyzer.analyze_match_context(...)
# Siempre retorna resultado válido
```

### 2. BlackboxClient (Secondary Fallback)
**Archivo**: `bet_copilot/ai/blackbox_client.py`

**Características**:
- Cliente HTTP async con `aiohttp`
- Endpoint: `https://www.blackbox.ai/api/chat`
- Funciona sin API key (con limitaciones)
- Misma interfaz que GeminiClient

**Nota**: API puede requerir autenticación o cambiar endpoints. SimpleAnalyzer actúa como respaldo.

**Uso directo**:
```python
from bet_copilot.ai.blackbox_client import BlackboxClient

client = BlackboxClient(api_key="optional")
analysis = await client.analyze_match_context(...)
```

### 3. GeminiClient (Primary)
**Archivo**: `bet_copilot/ai/gemini_client.py`

**Características**:
- Cliente oficial de Google Generative AI
- Modelo: `gemini-pro` (estable)
- Requiere API key
- Mejor calidad de análisis

**Fix aplicado**: Cambiado de `gemini-1.5-flash` a `gemini-pro`

### 4. AIClient (Unified)
**Archivo**: `bet_copilot/ai/ai_client.py`

**Características**:
- Maneja cadena de fallback automáticamente
- Detecta proveedores disponibles
- Logging detallado de todos los intentos
- Limpieza automática de sesiones
- **Garantiza resultado válido** (SimpleAnalyzer siempre funciona)

**Métodos**:
```python
ai_client.is_available()           # Siempre True (SimpleAnalyzer)
ai_client.get_active_provider()    # Nombre del primario
ai_client.analyze_match_context()  # Análisis con fallback multi-nivel
ai_client.close()                  # Cerrar todas las sesiones
```

### 3. Integración en CLI
**Archivo**: `bet_copilot/cli.py`

**Cambios**:
```python
# Antes
from bet_copilot.ai.gemini_client import GeminiClient
self.gemini_client = GeminiClient()

# Ahora
from bet_copilot.ai.ai_client import create_ai_client
self.ai_client = create_ai_client()  # Con fallback automático
```

---

## 🔧 Configuración

### Variables de Entorno

**`.env`**:
```bash
# Gemini (primario)
GEMINI_API_KEY=tu_key_aqui

# Blackbox (fallback, opcional)
BLACKBOX_API_KEY=tu_key_aqui
```

**Opciones**:
1. **Solo Gemini**: Blackbox como fallback sin key
2. **Solo Blackbox**: Usar como primario
3. **Ambos**: Fallback completo con keys

### Actualizar `.env`
```bash
cp .env.example .env
nano .env  # Agregar keys
```

---

## 🧪 Testing

### Test de Fallback
```bash
python test_ai_fallback.py
```

**Verifica**:
1. Proveedor primario activo
2. Fallback disponible
3. Análisis de partido de prueba
4. Comparación entre proveedores (opcional)

**Output esperado**:
```
═══════════════════════════════════════════════
  Test: AI Client con Fallback                
═══════════════════════════════════════════════

Inicializando AI client...

┌─────────────── Estado de Proveedores ───────────────┐
│ Proveedor │      Estado      │ Rol      │
├───────────┼──────────────────┼──────────┤
│ Gemini    │ ✓ Activo         │ Primario │
│ Blackbox  │ ✓ Disponible     │ Fallback │
└───────────┴──────────────────┴──────────┘

Probando análisis de partido...

╭─────── Análisis con Gemini ───────╮
│ ✓ Análisis completado exitosamente│
│                                    │
│ Partido: Arsenal vs Chelsea        │
│                                    │
│ Ajustes Lambda:                    │
│   • Local: 0.95                    │
│   • Visitante: 1.05                │
│                                    │
│ Confianza: 75%                     │
│ Sentimiento: NEGATIVE              │
...
╰────────────────────────────────────╯
```

### Test en CLI
```bash
python main.py

# Verificar proveedor activo
➜ bet-copilot salud

✓ AI (Gemini)  # o ✓ AI (Blackbox)
```

---

## 📊 Comparativa de Proveedores

| Aspecto | Gemini | Blackbox | SimpleAnalyzer |
|---------|--------|----------|----------------|
| **API Key** | Requerida | Opcional | No requiere |
| **Dependencias** | google-generativeai | aiohttp | Ninguna |
| **Límite requests** | Generoso | Desconocido | Ilimitado |
| **Latencia** | ~2-3s | ~1-2s | <0.1s |
| **Calidad** | Alta (AI) | Media-Alta (AI) | Media (heurísticas) |
| **Contexto** | Excelente | Buena | Básica |
| **Disponibilidad** | 99%+ | Variable | 100% |
| **Costo** | Gratis (límites) | Gratis | Gratis |
| **Confianza** | 70-95% | 60-85% | 60-80% |

### Cuándo Se Usa Cada Uno

**Gemini (Nivel 1 - Recomendado)**:
- API key configurada
- Análisis complejos con mucho contexto
- Requiere comprensión profunda de lesiones/noticias
- Mejor calidad de predicción

**Blackbox (Nivel 2 - Fallback)**:
- Gemini no disponible o sin API key
- Análisis rápidos
- Backup cuando Gemini falla
- Requiere conexión a internet

**SimpleAnalyzer (Nivel 3 - Garantizado)**:
- Todos los AI fallan
- Sin API keys configuradas
- Sin conexión a internet
- Garantiza funcionamiento del sistema
- Análisis basado en datos objetivos (forma, H2H)

---

## 🔍 Logs y Debugging

### Logging Activado
```python
import logging
logging.basicConfig(level=logging.INFO)
```

**Logs típicos**:
```
INFO - AI client initialized. Primary: Gemini, Fallback: Blackbox
INFO - Attempting analysis with Gemini
INFO - ✓ Analysis successful with Gemini
```

**Logs de fallback**:
```
INFO - Attempting analysis with Gemini
WARNING - Primary (Gemini) failed: API key not configured
INFO - Falling back to Blackbox
INFO - ✓ Fallback successful with Blackbox
```

**Logs con fallback completo**:
```
INFO - Attempting analysis with Gemini
WARNING - Primary (Gemini) failed: 404 model not found
INFO - Falling back to Blackbox
WARNING - Fallback (Blackbox) failed: 404 Not Found
INFO - Falling back to SimpleAnalyzer
INFO - ✓ Fallback successful with SimpleAnalyzer
```

**Logs de SimpleAnalyzer**:
```
INFO - Simple analyzer initialized (rule-based fallback)
INFO - Attempting analysis with SimpleAnalyzer
INFO - ✓ Analysis successful with SimpleAnalyzer
```

---

## 💡 Ejemplos de Uso

### 1. Uso Básico (Auto-fallback)
```python
from bet_copilot.ai.ai_client import create_ai_client

ai_client = create_ai_client()

analysis = await ai_client.analyze_match_context(
    home_team="Barcelona",
    away_team="Real Madrid",
    home_form="WWWDW",
    away_form="WWLWW",
)

print(f"Provider: {ai_client.get_active_provider()}")
print(f"Confidence: {analysis.confidence*100:.0f}%")
print(f"Adjustments: {analysis.lambda_adjustment_home:.2f} - {analysis.lambda_adjustment_away:.2f}")
```

### 2. Forzar Blackbox
```python
ai_client = create_ai_client(prefer_gemini=False)
# Siempre usa Blackbox primero
```

### 3. Solo Gemini (Sin Fallback)
```python
from bet_copilot.ai.gemini_client import GeminiClient

gemini = GeminiClient()
# Sin fallback, falla si Gemini no disponible
```

### 4. Análisis Múltiple
```python
matches = [
    {"home_team": "Arsenal", "away_team": "Chelsea", ...},
    {"home_team": "Liverpool", "away_team": "Man City", ...},
]

analyses = await ai_client.analyze_multiple_matches(matches)
# Usa fallback independientemente para cada partido
```

---

## 🚨 Troubleshooting

### "Primary (Gemini) failed: API key not configured"
**Solución**: Agregar `GEMINI_API_KEY` en `.env`

### "Fallback (Blackbox) also failed: Connection refused"
**Causa**: Problema de red o API de Blackbox caída

**Solución**: 
- Verificar conexión a internet
- Reintentar más tarde
- Sistema retorna análisis neutral automáticamente

### "All AI providers failed"
**Sistema funciona**: Retorna análisis neutral (lambda=1.0)

**No afecta**: Resto del sistema funciona normal

---

## 📝 Checklist de Implementación

- [x] `BlackboxClient` implementado
- [x] `AIClient` con fallback automático
- [x] Integración en `CLI`
- [x] `BLACKBOX_API_KEY` en config
- [x] `.env.example` actualizado
- [x] Test script creado
- [x] Documentación completa
- [x] Logging detallado
- [x] Limpieza de sesiones

---

## 🔮 Mejoras Futuras

1. **Cache de respuestas**: Evitar requests duplicadas
2. **Retry con exponential backoff**: Reintentos inteligentes
3. **Circuit breaker**: Para proveedores caídos
4. **Métricas**: Tracking de tasa de éxito por proveedor
5. **A/B Testing**: Comparar calidad de análisis
6. **Más proveedores**: Añadir Claude, GPT-4, etc.

---

**Versión**: 0.5.1  
**Fecha**: 2026-01-04  
**Status**: ✅ Completado y probado
