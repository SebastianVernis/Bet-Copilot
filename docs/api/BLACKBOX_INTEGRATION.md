# 🔌 Integración con Blackbox AI

## 📋 Información Verificada con MCP de Blackbox Docs

### API Endpoint Oficial
```
https://api.blackbox.ai/chat/completions
```

### Formato
**OpenAI-compatible** - Usa el mismo schema que OpenAI Chat API

---

## 🔑 Configuración

### 1. Obtener API Key

**Pasos**:
1. Visita [Blackbox Dashboard](https://app.blackbox.ai/dashboard)
2. Inicia sesión con Google o GitHub
3. Ve a "Manage API Keys"
4. Genera nueva API key
5. Copia la key (formato: `sk-...`)

### 2. Configurar en Proyecto

**`.env`**:
```bash
BLACKBOX_API_KEY=sk-...tu_key_aqui
```

**Verificar**:
```bash
# Ver si está configurada
python -c "from bet_copilot.config import BLACKBOX_API_KEY; print('Key:', 'Configurada' if BLACKBOX_API_KEY else 'No configurada')"
```

---

## 🔧 Implementación Técnica

### Payload del Request (OpenAI-compatible)

```json
{
  "model": "blackboxai-pro",
  "messages": [
    {
      "role": "user",
      "content": "Tu prompt aquí"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": false
}
```

### Headers Requeridos

```http
Content-Type: application/json
Authorization: Bearer sk-...tu_api_key
```

### Response Format

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "blackboxai-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Respuesta del modelo"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "total_tokens": 150
  }
}
```

---

## 🎯 Implementación en Bet-Copilot

### BlackboxClient.py

**Ubicación**: `bet_copilot/ai/blackbox_client.py`

**Características implementadas**:
```python
class BlackboxClient:
    API_URL = "https://api.blackbox.ai/chat/completions"
    
    async def _generate_response(self, prompt: str) -> str:
        payload = {
            "model": self.model,           # blackboxai-pro
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # POST request
        response = await session.post(API_URL, json=payload, headers=headers)
        
        # Parse OpenAI format
        data = await response.json()
        content = data['choices'][0]['message']['content']
        return content
```

**Manejo de errores**:
- `200`: Éxito, extrae `choices[0].message.content`
- `401`: API key inválida
- `404`: Endpoint no encontrado (no debería pasar)
- `429`: Rate limit excedido
- Timeout: 30 segundos

---

## 📊 Modelos Disponibles

Según docs de Blackbox, puedes usar:

### Modelos Blackbox Propios
```python
model = "blackboxai-pro"      # Recomendado (rápido y bueno)
model = "blackboxai"           # Estándar
```

### Modelos de Otros Proveedores (vía Blackbox)
```python
model = "blackboxai/openai/gpt-4"       # GPT-4 via Blackbox
model = "blackboxai/openai/gpt-4o"      # GPT-4 Optimized
model = "blackboxai/anthropic/claude-4" # Claude
model = "blackboxai/google/gemini-2.0"  # Gemini via Blackbox
```

**Uso en Bet-Copilot**:
```python
# Default (ya configurado)
client = BlackboxClient()  # Usa blackboxai-pro

# Cambiar modelo
client = BlackboxClient(model="blackboxai/openai/gpt-4")
```

---

## 🧪 Testing

### Test Unitario
```bash
pytest bet_copilot/tests/test_blackbox_client.py -v
```

**15 tests**:
- ✅ Initialization con/sin key
- ✅ Prompt building
- ✅ JSON parsing (válido, con texto extra, inválido)
- ✅ OpenAI response format
- ✅ Error handling
- ✅ Session management

### Test Interactivo
```bash
python test_ai_fallback.py
```

**Verifica**:
- Conexión a API
- Formato de request correcto
- Parsing de response
- Fallback a SimpleAnalyzer si falla

---

## 🔍 Verificación de Integración

### Checklist

- [x] **Endpoint correcto**: `https://api.blackbox.ai/chat/completions`
- [x] **Formato OpenAI**: Compatible con schema estándar
- [x] **Headers**: `Authorization: Bearer {key}`
- [x] **Payload**: Estructura correcta con `model`, `messages`
- [x] **Response parsing**: Extrae `choices[0].message.content`
- [x] **Error handling**: 401, 404, 429, timeout
- [x] **Modelo por defecto**: `blackboxai-pro`
- [x] **Timeout**: 30 segundos
- [x] **Session management**: `aiohttp.ClientSession`
- [x] **Logging**: Detallado en todos los pasos

### Comparación con Docs

| Aspecto | Docs Blackbox | Implementación | Status |
|---------|---------------|----------------|--------|
| Endpoint | `/chat/completions` | ✅ Correcto | ✅ |
| Base URL | `api.blackbox.ai` | ✅ Correcto | ✅ |
| Auth header | `Bearer {key}` | ✅ Correcto | ✅ |
| Payload format | OpenAI schema | ✅ Correcto | ✅ |
| Model param | String | ✅ Correcto | ✅ |
| Messages array | Required | ✅ Implementado | ✅ |
| Response format | `choices[0].message` | ✅ Parseado | ✅ |

---

## 💡 Ejemplo de Uso Real

### Request Real
```python
import aiohttp
import asyncio

async def test_blackbox():
    url = "https://api.blackbox.ai/chat/completions"
    
    payload = {
        "model": "blackboxai-pro",
        "messages": [
            {
                "role": "user",
                "content": "Analyze: Arsenal (WWWWW) vs Chelsea (LLLLL)"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    headers = {
        "Authorization": "Bearer sk-your_key",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            print(data['choices'][0]['message']['content'])

asyncio.run(test_blackbox())
```

### Response Esperada
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1704380000,
  "model": "blackboxai-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"home_adjustment\": 1.1, ...}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 80,
    "total_tokens": 180
  }
}
```

---

## 🐛 Troubleshooting

### Error 401: Unauthorized
```
Blackbox authentication failed. API key may be invalid.
```

**Solución**:
1. Verificar que API key está en `.env`
2. Verificar formato: debe empezar con `sk-`
3. Regenerar key en dashboard si es necesaria
4. Verificar que no hay espacios extra

### Error 404: Not Found
```
Blackbox API error 404: {"detail":"Not Found"}
```

**Causas posibles**:
- Endpoint incorrecto (verificar URL)
- Modelo no disponible
- API key sin permisos

**Solución aplicada**:
- Endpoint corregido a: `https://api.blackbox.ai/chat/completions`
- Modelo: `blackboxai-pro`
- Fallback a SimpleAnalyzer si persiste

### Error 429: Rate Limit
```
API returned status 429
```

**Solución**:
- Sistema usa SimpleAnalyzer automáticamente
- Implementar rate limiting si es recurrente
- Considerar upgrade de plan

### Timeout (30s)
```
Blackbox API timeout (30s)
```

**Solución**:
- Normal para requests complejos
- Sistema reintenta con SimpleAnalyzer
- Considerar aumentar timeout si es frecuente

---

## 📈 Métricas de Performance

### Benchmarks Esperados

Con API key configurada:
```
Latencia promedio:    1-2s
Success rate:         95%+
Calidad de análisis:  Alta (AI real)
Confianza promedio:   65-85%
```

Sin API key (limitado):
```
Latencia promedio:    Variable
Success rate:         <50%
Calidad:              Puede fallar
Recomendación:        Usar SimpleAnalyzer
```

---

## 🔗 Referencias

### Documentación Oficial
- **API Reference**: https://docs.blackbox.ai/api-reference/chat
- **Dashboard**: https://app.blackbox.ai/dashboard
- **Introduction**: https://docs.blackbox.ai/api-reference/introduction
- **Response Format**: https://docs.blackbox.ai/api-reference/responses

### Implementación en Bet-Copilot
- **BlackboxClient**: `bet_copilot/ai/blackbox_client.py`
- **Tests**: `bet_copilot/tests/test_blackbox_client.py`
- **Config**: `bet_copilot/config.py`
- **Ejemplo**: `test_ai_fallback.py`

---

## ✅ Checklist de Verificación

Basado en docs de Blackbox:

- [x] Endpoint: `https://api.blackbox.ai/chat/completions`
- [x] Método: POST
- [x] Header `Content-Type: application/json`
- [x] Header `Authorization: Bearer {key}`
- [x] Payload con `model`, `messages`, `temperature`, `max_tokens`
- [x] Response parsing de `choices[0].message.content`
- [x] Manejo de errores 401, 404, 429
- [x] Timeout configurado (30s)
- [x] Logging detallado
- [x] Session cleanup
- [x] Tests unitarios (15)
- [x] Fallback a SimpleAnalyzer si falla
- [x] Documentación completa

---

## 🎯 Resumen de Cambios

### Correcciones Aplicadas

1. **Endpoint**: ✅ Corregido a `/chat/completions`
2. **Formato payload**: ✅ OpenAI-compatible
3. **Response parsing**: ✅ Extrae `choices[0].message.content`
4. **Modelo por defecto**: ✅ `blackboxai-pro`
5. **Error handling**: ✅ Manejo completo de códigos HTTP
6. **Logging**: ✅ Detallado con contexto

### Estado Actual

✅ **Implementación verificada contra docs oficiales**
✅ **Compatible con formato OpenAI**
✅ **Fallback robusto a SimpleAnalyzer**
✅ **15 tests unitarios**
✅ **Documentación completa**

---

**Versión**: 0.5.1  
**Fecha**: 2026-01-04  
**Verificado con**: Blackbox AI Docs (MCP)  
**Status**: ✅ Production Ready
