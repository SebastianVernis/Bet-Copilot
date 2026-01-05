#!/bin/bash
# Quick Start Script para Bet-Copilot
# Verifica todo antes de ejecutar

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════╗"
echo "║   Bet-Copilot v0.5.2 - Quick Start            ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Check Python version
echo -e "${YELLOW}[1/5] Verificando Python...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Python 3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python OK${NC}"
echo ""

# Step 2: Check if dependencies are installed
echo -e "${YELLOW}[2/5] Verificando dependencias...${NC}"
if python3 -c "import rich" 2>/dev/null; then
    echo -e "${GREEN}✓ Dependencias básicas instaladas${NC}"
    DEPS_OK=true
else
    echo -e "${RED}⚠ Dependencias no instaladas${NC}"
    DEPS_OK=false
fi
echo ""

# Step 3: Install if needed
if [ "$DEPS_OK" = false ]; then
    echo -e "${YELLOW}[3/5] Instalando dependencias...${NC}"
    read -p "¿Instalar ahora? (s/n): " install
    if [ "$install" = "s" ] || [ "$install" = "y" ]; then
        ./scripts/INSTALL_DEPS.sh
    else
        echo -e "${RED}Instalación cancelada. Ejecuta: ./scripts/INSTALL_DEPS.sh${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}[3/5] Dependencias ya instaladas${NC}"
    echo -e "${GREEN}✓ OK${NC}"
fi
echo ""

# Step 4: Check .env
echo -e "${YELLOW}[4/5] Verificando configuración...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ Archivo .env no encontrado${NC}"
    read -p "¿Crear desde .env.example? (s/n): " create
    if [ "$create" = "s" ] || [ "$create" = "y" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env creado${NC}"
        echo -e "${YELLOW}Edita .env para agregar tus API keys${NC}"
    fi
else
    echo -e "${GREEN}✓ .env existe${NC}"
fi
echo ""

# Step 5: Verify APIs (optional)
echo -e "${YELLOW}[5/5] Verificando API keys...${NC}"
if python3 scripts/verify_apis.py 2>/dev/null; then
    echo -e "${GREEN}✓ Verificación exitosa${NC}"
else
    echo -e "${YELLOW}⚠ No se pudo verificar (python-dotenv puede no estar instalado)${NC}"
    echo -e "${YELLOW}Las API keys se verificarán al ejecutar el sistema${NC}"
fi
echo ""

# Ready to run
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✓ Sistema listo para ejecutar               ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Ejecutar ahora:"
echo -e "  ${GREEN}python main.py${NC}"
echo ""
echo "O ver demo primero:"
echo -e "  ${GREEN}python examples/DEMO.py${NC}"
echo ""
echo "Tests:"
echo -e "  ${GREEN}./scripts/run_tests.sh${NC}"
echo ""
