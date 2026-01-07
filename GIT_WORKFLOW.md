# Git Workflow - Completar Push y PR

## Estado Actual

✅ **Commit realizado localmente**:
- Branch: `feature/ai-spanish-fix-v0.6.1`
- Commit: `4a9e411` - "feat: Fix AI analysis + Spanish i18n + API alternatives research (v0.6.1)"
- Archivos modificados: 7
  * 3 nuevos documentos (CHANGELOG, RESEARCH, SUMMARY)
  * 4 archivos modificados (AI clients + CLI)

⚠️ **Pendiente**: Push a GitHub y creación de PR

---

## Pasos para Completar

### 1. Push de la rama feature

```bash
cd /home/sebastianvernis/Proyectos/Bet-Copilot

# Opción A: Si tienes SSH configurado
git remote set-url origin git@github.com:SebastianVernis/Bet-Copilot.git
git push -u origin feature/ai-spanish-fix-v0.6.1

# Opción B: Si usas HTTPS con token
# Primero configura el token como credential helper
git push -u origin feature/ai-spanish-fix-v0.6.1
# Te pedirá usuario y password (usa token como password)

# Opción C: Usar gh CLI
gh auth login
git push -u origin feature/ai-spanish-fix-v0.6.1
```

### 2. Crear rama develop (si no existe)

```bash
# Checkout a master
git checkout master
git pull origin master

# Crear develop desde master
git checkout -b develop
git push -u origin develop

# Volver a feature branch
git checkout feature/ai-spanish-fix-v0.6.1
```

### 3. Crear Pull Request a develop

#### Opción A: Usando gh CLI (Recomendado)
```bash
gh pr create \
  --base develop \
  --title "feat: Fix AI analysis + Spanish i18n + API alternatives research (v0.6.1)" \
  --body "$(cat <<'PRBODY'
## 🎯 Resumen

Esta PR corrige el análisis de IA, añade internacionalización completa al español e incluye investigación de alternativas a API-Football.

## ✅ Cambios Principales

### 1. Corrección del Análisis de IA
- **Problema**: Análisis no generaba pronósticos completos cuando Gemini fallaba
- **Solución**: 
  * Detector de análisis neutral por error usando keywords
  * Fallback limpio a Blackbox
  * No contamina consensus con mensajes de error

### 2. Corrección de CLI
- **Problema**: Error `'SoccerPredictor' object has no attribute 'is_available'`
- **Solución**: Uso de argumentos con nombre en `MatchAnalyzer` constructor

### 3. Internacionalización Español
- Prompts de Gemini completamente en español
- Prompts de Blackbox completamente en español
- Detección de errores bilingüe (EN + ES)
- Mensajes de error en español

### 4. Investigación API-Football
- Documento completo evaluando 6 alternativas
- Estrategia híbrida recomendada (Football-Data.org + FBref + SimpleProvider)
- Roadmap de implementación (9-13h estimadas)

## 📊 Tests

- ✅ 96/96 tests passing (100%)
- ✅ Validación completa del sistema
- ✅ Prompts verificados en español

## 📁 Archivos Modificados

### Nuevos
- `CHANGELOG_Spanish_AI.md` - Detalles de i18n
- `RESEARCH_Football_APIs.md` - Investigación alternativas API
- `SUMMARY_2026-01-07.md` - Resumen de sesión

### Modificados
- `bet_copilot/ai/gemini_client.py` - Prompts en español
- `bet_copilot/ai/blackbox_client.py` - Prompts en español
- `bet_copilot/ai/collaborative_analyzer.py` - Detección bilingüe
- `bet_copilot/cli.py` - Corrección inicialización

## 🎯 Estado

- Sistema completamente operativo
- Blackbox funcional (IA principal)
- Gemini rate limited (esperado, fallback activo)
- Todas las predicciones en español

## 📋 Checklist

- [x] Código implementado
- [x] Tests pasando (96/96)
- [x] Documentación actualizada
- [x] Sin breaking changes
- [x] Validación completa del sistema
- [x] Prompts verificados

## 🔗 Documentos de Referencia

Ver archivos adjuntos para detalles completos:
- CHANGELOG_Spanish_AI.md
- RESEARCH_Football_APIs.md
- SUMMARY_2026-01-07.md

---

💖 Generated with Crush
PRBODY
)"
```

#### Opción B: Crear PR manualmente en GitHub
1. Ve a https://github.com/SebastianVernis/Bet-Copilot
2. Click en "Pull requests" → "New pull request"
3. Base: `develop` ← Compare: `feature/ai-spanish-fix-v0.6.1`
4. Copia el título y descripción de arriba
5. Click "Create pull request"

### 4. Merge a develop (después de review)

```bash
# Opción A: En GitHub UI
# Click en "Merge pull request" → "Squash and merge" o "Create merge commit"

# Opción B: Desde CLI
gh pr merge feature/ai-spanish-fix-v0.6.1 --squash --delete-branch
```

### 5. Actualizar local

```bash
git checkout develop
git pull origin develop

# Limpiar branches locales
git branch -d feature/ai-spanish-fix-v0.6.1
```

---

## Estructura de Branches Recomendada

```
master (release - protegida)
  └── develop (integración - default branch)
       ├── feature/ai-spanish-fix-v0.6.1 (esta PR)
       ├── feature/football-data-client (próxima)
       └── feature/fbref-scraper (próxima)
```

### Configurar develop como default branch

1. Ve a GitHub repo settings
2. Branches → Default branch
3. Cambia de `master` a `develop`
4. Save changes

---

## Workflow Futuro

### Para nuevas features:
```bash
# Desde develop
git checkout develop
git pull origin develop

# Crear feature branch
git checkout -b feature/nombre-descriptivo

# Hacer cambios y commits
git add .
git commit -m "feat: descripción"

# Push y PR
git push -u origin feature/nombre-descriptivo
gh pr create --base develop
```

### Para releases:
```bash
# Desde develop
git checkout develop
git pull origin develop

# Crear release branch
git checkout -b release/v0.7.0

# Hacer ajustes finales, actualizar VERSION
git commit -m "chore: prepare release v0.7.0"

# PR a master
gh pr create --base master --title "Release v0.7.0"

# Después de merge, tag
git checkout master
git pull origin master
git tag -a v0.7.0 -m "Release v0.7.0"
git push origin v0.7.0

# Merge back a develop
git checkout develop
git merge master
git push origin develop
```

---

## Troubleshooting

### Push falla con "Authentication failed"

**HTTPS + Token**:
```bash
# Generar token en GitHub: Settings → Developer settings → Personal access tokens
# Usar token como password al hacer push
git push -u origin feature/ai-spanish-fix-v0.6.1
Username: SebastianVernis
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**SSH**:
```bash
# Configurar SSH key
ssh-keygen -t ed25519 -C "pelongemelo@gmail.com"
cat ~/.ssh/id_ed25519.pub
# Copiar y agregar en GitHub: Settings → SSH keys

# Cambiar remote a SSH
git remote set-url origin git@github.com:SebastianVernis/Bet-Copilot.git
git push -u origin feature/ai-spanish-fix-v0.6.1
```

### Conflictos en PR

```bash
# Actualizar con develop
git checkout feature/ai-spanish-fix-v0.6.1
git fetch origin
git rebase origin/develop

# Resolver conflictos manualmente
# Luego:
git add .
git rebase --continue
git push -f origin feature/ai-spanish-fix-v0.6.1
```

---

## Resumen de lo Pendiente

1. ✅ Commit local realizado
2. ⏳ Push a GitHub (ejecutar: `git push -u origin feature/ai-spanish-fix-v0.6.1`)
3. ⏳ Crear rama develop (ejecutar: pasos en sección 2)
4. ⏳ Crear PR a develop (ejecutar: pasos en sección 3)
5. ⏳ Review y merge
6. ⏳ Actualizar local

**Tiempo estimado**: 5-10 minutos

---

**Creado**: 2026-01-07  
**Branch**: feature/ai-spanish-fix-v0.6.1  
**Commit**: 4a9e411
