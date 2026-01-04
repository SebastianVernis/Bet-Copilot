# 🔑 Configuración de Proveedores AI

## 📋 Opciones Disponibles

Bet-Copilot soporta 3 proveedores de IA con fallback automático:

1. **Gemini** (Google) - Recomendado
2. **Blackbox** (Blackbox.ai) - Alternativa
3. **SimpleAnalyzer** - Fallback garantizado (sin API)

---

## 🔐 Obtener API Keys

### 1. Gemini (Google)

**Cómo obtener**:
1. Ir a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Iniciar sesión con cuenta Google
3. Crear nueva API key
4. Copiar la key

**Configurar**:
```bash
# En .env
GEMINI_API_KEY=AIzaSy...tu_key_aqui
```

**Modelos disponibles**:
- `gemini-pro` (default, recomendado) ✅
- `gemini-1.0-pro` (versión específica)
- `gemini-1.5-pro` (si disponible en tu región)

**Límites gratuitos**:
- 60 requests por minuto
- Generoso para uso personal
- Modelo usado: `gemini-pro` (estable)

**Ventajas**:
- ✅ Mejor comprensión contextual
- ✅ Análisis más profundo
- ✅ Mejor manejo de lenguaje natural
- ✅ Modelo grande y actualizado

---

### 2. Blackbox AI (Opcional)

**Cómo obtener**:
1. Ir a [Blackbox Dashboard](https://app.blackbox.ai/dashboard)
2. Crear cuenta (Google/GitHub)
3. Navegar a API Keys
4. Generar nueva API key
5. Copiar la key

**Configurar**:
```bash
# En .env
BLACKBOX_API_KEY=sk-...tu_key_aqui
```

**API Details**:
- **Endpoint**: `https://api.blackbox.ai/chat/completions`
- **Formato**: Compatible con OpenAI
- **Autenticación**: `Authorization: Bearer {API_KEY}`
- **Modelos disponibles**: 
  - `blackboxai-pro` (recomendado)
  - `blackboxai` (estándar)
  - `blackboxai/openai/gpt-4` (si tienes acceso)

**Límites**:
- Depende del plan
- Requiere API key para uso oficial
- Ver [docs.blackbox.ai](https://docs.blackbox.ai/)

**Ventajas**:
- ✅ Formato OpenAI (estándar)
- ✅ Múltiples modelos disponibles
- ✅ Rápido (~1-2s)
- ✅ Buen análisis general

**Nota**: Si falla o no está configurado, SimpleAnalyzer toma el control automáticamente.

---

### 3. SimpleAnalyzer (Sin Configuración)

**No requiere**:
- ❌ API key
- ❌ Conexión a internet
- ❌ Dependencias externas

**Cómo funciona**:
- Calcula puntuación de forma (W=3, D=1, L=0)
- Analiza historial H2H
- Detecta lesiones por palabras clave
- Aplica ajustes conservadores

**Ventajas**:
- ✅ **Siempre disponible**
- ✅ Instantáneo (<0.1s)
- ✅ Sin costos
- ✅ Offline-capable
- ✅ Transparente (reglas conocidas)

**Desventajas**:
- ⚠️ Análisis más simple
- ⚠️ Sin comprensión de contexto profundo
- ⚠️ Confianza máxima 80%

---

## ⚙️ Configuración del Sistema

### Escenario 1: Solo Gemini (Recomendado)

**`.env`**:
```bash
GEMINI_API_KEY=AIzaSy...
BLACKBOX_API_KEY=  # Dejar vacío
```

**Comportamiento**:
```
Primario: Gemini
Fallback: SimpleAnalyzer
```

### Escenario 2: Gemini + Blackbox (Máxima Redundancia)

**`.env`**:
```bash
GEMINI_API_KEY=AIzaSy...
BLACKBOX_API_KEY=tu_key...
```

**Comportamiento**:
```
Primario: Gemini
Fallback 1: Blackbox
Fallback 2: SimpleAnalyzer
```

### Escenario 3: Solo Blackbox

**`.env`**:
```bash
GEMINI_API_KEY=  # Dejar vacío
BLACKBOX_API_KEY=tu_key...
```

**Comportamiento**:
```
Primario: Blackbox
Fallback: SimpleAnalyzer
```

### Escenario 4: Sin API Keys (Offline)

**`.env`**:
```bash
GEMINI_API_KEY=
BLACKBOX_API_KEY=
```

**Comportamiento**:
```
Primario: SimpleAnalyzer
Fallback: Ninguno (no necesario)
```

**Ideal para**:
- Desarrollo sin keys
- Testing sin consumir cuota
- Uso offline
- Demo/prueba del sistema

---

## 🧪 Verificar Configuración

### Script de Verificación
```bash
python test_ai_fallback.py
```

**Output esperado**:
```
Estado de Proveedores
┌────────────────┬────────────┬────────────┐
│ Proveedor      │ Estado     │ Rol        │
├────────────────┼────────────┼────────────┤
│ Gemini         │ ✓ Activo   │ Primario   │
│ Blackbox       │ ⚠ Caído    │ Fallback 1 │
│ SimpleAnalyzer │ ✓ Activo   │ Fallback 2 │
└────────────────┴────────────┴────────────┘
```

### En CLI
```bash
python main.py

➜ bet-copilot salud

✓ The Odds API
✓ API-Football
✓ AI (Gemini)        ← Muestra proveedor activo
# o
✓ AI (SimpleAnalyzer) ← Si no hay keys
```

---

## 🔍 Debugging

### Ver qué proveedor se está usando

```bash
# Activar logs detallados
export LOG_LEVEL=DEBUG
python main.py
```

**Logs**:
```
INFO - AI client initialized. Primary: Gemini, Fallbacks: [Blackbox, SimpleAnalyzer]
INFO - Attempting analysis with Gemini
INFO - ✓ Analysis successful with Gemini
```

### Si Gemini falla

**Error típico**:
```
Gemini API error: 404 models/gemini-1.5-flash is not found
```

**Solución aplicada**:
```python
# Cambiado modelo a versión estable
model: str = "gemini-pro"  # Antes: "gemini-1.5-flash"
```

**Modelos disponibles**:
- `gemini-pro` - Recomendado (estable)
- `gemini-1.0-pro` - Versión específica
- `gemini-1.5-pro` - Si disponible en tu región

### Si Blackbox falla

**Error típico**:
```
Blackbox API error 404: {"detail":"Not Found"}
```

**Comportamiento**:
- Sistema usa SimpleAnalyzer automáticamente
- No requiere acción del usuario
- Análisis continúa con heurísticas

**Endpoint actual**: `https://www.blackbox.ai/api/chat`

**Si cambia**: Actualizar en `bet_copilot/ai/blackbox_client.py:42`

---

## 📈 Métricas de Calidad por Proveedor

### Gemini
```
Confianza promedio:     75-85%
Ajustes típicos:        0.9-1.15 (±5-15%)
Factores detectados:    3-6
Precisión estimada:     Alta
Casos de uso:           Producción
```

### Blackbox
```
Confianza promedio:     65-75%
Ajustes típicos:        0.95-1.1 (±5-10%)
Factores detectados:    2-4
Precisión estimada:     Media-Alta
Casos de uso:           Backup
```

### SimpleAnalyzer
```
Confianza promedio:     60-70%
Ajustes típicos:        0.9-1.1 (±0-10%)
Factores detectados:    1-3
Precisión estimada:     Media
Casos de uso:           Fallback/Offline
```

---

## 🚀 Mejores Prácticas

### 1. Configurar Gemini
```bash
# Siempre que sea posible
GEMINI_API_KEY=AIzaSy...
```

### 2. Monitorear Uso
```bash
# Ver logs de qué proveedor se usa
grep "Analysis successful" logs/*.log
```

### 3. Testing
```bash
# Probar cada proveedor
pytest bet_copilot/tests/test_ai_client.py -v
pytest bet_copilot/tests/test_simple_analyzer.py -v
```

### 4. Ambiente de Desarrollo
```bash
# Sin keys para no consumir cuota
GEMINI_API_KEY=
BLACKBOX_API_KEY=

# Usa SimpleAnalyzer automáticamente
```

---

## 📝 Checklist de Setup

- [ ] Copiar `.env.example` a `.env`
- [ ] Obtener Gemini API key (recomendado)
- [ ] Agregar key a `.env`
- [ ] Verificar con `python test_ai_fallback.py`
- [ ] Verificar con `salud` en CLI
- [ ] (Opcional) Configurar Blackbox para redundancia

---

## 🔗 Enlaces Útiles

- **Gemini API**: https://makersuite.google.com/app/apikey
- **Gemini Docs**: https://ai.google.dev/docs
- **Blackbox.ai**: https://www.blackbox.ai/
- **Código SimpleAnalyzer**: `bet_copilot/ai/simple_analyzer.py`

---

**Versión**: 0.5.1  
**Fecha**: 2026-01-04  
**Prioridad**: Gemini > Blackbox > SimpleAnalyzer
