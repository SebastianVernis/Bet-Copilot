# 🌳 Git Branch Strategy - Bet-Copilot

## 📋 Convención de Ramas

### Formato
```
{entorno}/{tipo}/{descripcion-breve}
```

### Entornos
- `laptop/` - Desarrollo en máquina local
- `server/` - Cambios específicos para servidor
- `cloud/` - Despliegue en cloud (futuro)

### Tipos
- `feature/` - Nueva funcionalidad
- `update/` - Mejora de funcionalidad existente
- `fix/` - Corrección de bugs
- `hotfix/` - Corrección crítica urgente
- `refactor/` - Refactorización sin cambio de funcionalidad
- `docs/` - Solo documentación
- `test/` - Solo tests

### Ejemplos
```bash
laptop/feature/collaborative-ai-alternative-markets
laptop/update/improve-kelly-criterion
laptop/fix/poisson-calculation-edge-case
server/feature/api-rate-limiter
server/hotfix/circuit-breaker-timeout
```

---

## 🔄 Flujo de Trabajo

### 1. Desarrollo Local
```bash
# Crear rama de feature desde master
git checkout master
git pull origin master
git checkout -b laptop/feature/mi-nueva-feature

# Desarrollar y commitear
git add .
git commit -m "Descripción clara del cambio"

# Push a origin
git push -u origin laptop/feature/mi-nueva-feature
```

### 2. Pull Request a Development
```bash
# Crear PR desde laptop/feature/* hacia development
gh pr create --base development --title "Feature: Mi Nueva Feature" --body "..."

# O via GitHub UI
```

### 3. Testing en Development
```bash
# Checkout development en servidor
git checkout development
git pull origin development

# Deploy en servidor de staging
./deploy_staging.sh

# Ejecutar pruebas alpha
pytest bet_copilot/tests/
python scripts/integration_test.py
```

### 4. PR a Release/Main
```bash
# Una vez aprobado en development
gh pr create --base main --title "Release: v0.X.X" --body "..."

# Merge a main = despliegue a producción
```

---

## 🌿 Estructura de Ramas

```
main (production)
  │
  └─── development (staging/alpha)
         │
         ├─── laptop/feature/collaborative-ai
         ├─── laptop/update/api-optimization
         ├─── laptop/fix/bug-in-kelly
         ├─── server/feature/monitoring
         └─── server/update/performance-tuning
```

---

## 📊 Ramas Principales

### `main` (Protected)
- **Propósito**: Código en producción
- **Despliegue**: Servidor principal
- **Protección**: 
  - Requiere PR review
  - Tests deben pasar
  - No push directo

### `development` (Protected)
- **Propósito**: Integración y testing alpha
- **Despliegue**: Servidor de staging
- **Protección**:
  - Requiere PR
  - Tests deben pasar
  - Permite push directo para hotfixes

### Feature Branches (Temporal)
- **Propósito**: Desarrollo de features
- **Lifetime**: Hasta merge en development
- **Limpieza**: Borrar después de merge

---

## 🔐 Protección de Ramas

### Configurar en GitHub

```bash
# Settings → Branches → Add rule

# Para 'main':
- Require pull request before merging
- Require status checks to pass (CI/CD)
- Require conversation resolution
- Do not allow bypassing

# Para 'development':
- Require pull request before merging
- Require status checks to pass
- Allow administrators to bypass
```

---

## 📝 Commit Message Convention

### Formato
```
<tipo>: <descripción breve>

<descripción detallada opcional>
<referencia a issue si aplica>
```

### Tipos
- `feat:` - Nueva funcionalidad
- `update:` - Mejora de feature existente
- `fix:` - Bug fix
- `refactor:` - Refactorización
- `test:` - Agregar/mejorar tests
- `docs:` - Documentación
- `style:` - Formateo, typos
- `perf:` - Mejora de performance
- `chore:` - Tareas de mantenimiento

### Ejemplos
```bash
feat: Add collaborative AI analysis with Gemini + Blackbox

- Implement CollaborativeAnalyzer for multi-AI consensus
- Add agreement scoring and divergence detection
- Integrate with MatchAnalyzer
- Add 12 new tests

Closes #42

---

update: Migrate from google-generativeai to google-genai SDK

- Uninstall deprecated package
- Install modern google-genai v1.56+
- Update GeminiClient to use new API
- Fix all tests

---

fix: Correct cumulative_probability in PoissonCalculator

Alternative markets predictor was failing due to missing method.
Added cumulative_probability for Over/Under calculations.
```

---

## 🚀 Workflow Completo - Ejemplo

### Escenario: Nueva Feature

```bash
# 1. Crear rama
git checkout master
git pull origin master
git checkout -b laptop/feature/backtesting-engine

# 2. Desarrollar
# ... código ...

# 3. Commit
git add bet_copilot/backtest/
git add bet_copilot/tests/test_backtest.py
git commit -m "feat: Add backtesting engine for historical validation

- Implement BacktestEngine with historical data replay
- Calculate ROI, Sharpe ratio, max drawdown
- Add 15 new tests
- Update documentation"

# 4. Push
git push -u origin laptop/feature/backtesting-engine

# 5. PR a development
gh pr create --base development \
  --title "Feature: Backtesting Engine" \
  --body "## Summary
  
Adds backtesting engine to validate predictions against historical data.

## Changes
- New module: bet_copilot/backtest/
- 15 new tests
- Documentation updated

## Testing
- [x] All tests pass (111/111)
- [x] Manual testing with 100 historical matches
- [x] ROI calculation verified

## Deployment
Ready for alpha testing in development server."

# 6. Review y merge
# ... esperar aprobación ...

# 7. Testing en development
ssh servidor
cd /opt/bet-copilot
git checkout development
git pull origin development
pytest bet_copilot/tests/
./run_integration_tests.sh

# 8. Si tests pasan, PR a main
gh pr create --base main \
  --title "Release: v0.6.0 - Backtesting Engine" \
  --body "..."

# 9. Merge a main = producción
# 10. Cleanup
git branch -d laptop/feature/backtesting-engine
git push origin --delete laptop/feature/backtesting-engine
```

---

## 🎯 Estado Actual del Proyecto

### Ramas Existentes
```
✅ main                                    (production - estable)
🆕 laptop/feature/collaborative-ai-alternative-markets  (← ESTÁS AQUÍ)
```

### Próximos Pasos

1. **Crear rama development** (si no existe en origin):
```bash
git checkout -b development
git push -u origin development
```

2. **Commitear trabajo actual**:
```bash
git add .
git commit -m "feat: Add collaborative AI, alternative markets, and news feed

Major v0.5 release with:
- Multi-AI collaborative analysis (Gemini + Blackbox)
- Free news aggregation (BBC + ESPN RSS)
- Alternative markets predictor (Corners, Cards, Shots, Offsides)
- Migration to google-genai SDK
- Enhanced tactical AI prompts
- 96 tests passing
- ~60% API cost reduction"
```

3. **Push y crear PR**:
```bash
git push -u origin laptop/feature/collaborative-ai-alternative-markets

gh pr create --base development \
  --title "Feature: Collaborative AI + Alternative Markets (v0.5)" \
  --body "See CHANGELOG_v0.5.md for full details"
```

---

## 📚 Recursos

### GitHub CLI
```bash
# Install gh (si no está instalado)
# Ubuntu/Debian:
sudo apt install gh

# Autenticar
gh auth login

# Crear PR
gh pr create --base development --title "..." --body "..."

# Ver PRs
gh pr list

# Merge PR
gh pr merge <number> --squash
```

### Git Aliases Útiles
```bash
# Agregar a ~/.gitconfig
[alias]
  co = checkout
  br = branch
  ci = commit
  st = status --short
  lg = log --oneline --graph --decorate --all
  
  # Feature workflow
  feat = "!f() { git checkout -b laptop/feature/$1; }; f"
  update = "!f() { git checkout -b laptop/update/$1; }; f"
  fix = "!f() { git checkout -b laptop/fix/$1; }; f"
```

**Uso**:
```bash
git feat collaborative-ai
# = git checkout -b laptop/feature/collaborative-ai
```

---

## ✅ Checklist para PR

Antes de crear PR a development:

- [ ] Todos los tests pasan (`pytest bet_copilot/tests/`)
- [ ] No hay TODOs o código comentado innecesario
- [ ] Documentación actualizada (AGENTS.md, README.md)
- [ ] CHANGELOG creado/actualizado
- [ ] Commits tienen mensajes descriptivos
- [ ] No hay secrets o API keys en código
- [ ] Código sigue convenciones del proyecto
- [ ] Features nuevas tienen tests

---

**Última actualización**: 2026-01-04  
**Versión**: v0.5.0  
**Estrategia**: Trunk-based development con feature branches
