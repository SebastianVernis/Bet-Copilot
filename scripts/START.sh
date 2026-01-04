#!/bin/bash
# Script de inicio rápido para Bet-Copilot

echo "🎯 Iniciando Bet-Copilot..."
echo ""

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "   Copiando .env.example a .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  Por favor edita .env con tus claves API antes de continuar"
    echo "   Luego ejecuta: ./START.sh"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    echo "   Instala Python 3.10 o superior"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"
echo ""

# Verificar dependencias
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "⚠️  Dependencias no instaladas"
    echo "   Instalando dependencias..."
    pip install -r requirements.txt
    echo ""
fi

echo "✓ Dependencias instaladas"
echo ""

# Ejecutar aplicación
echo "🚀 Iniciando Bet-Copilot..."
echo ""
python3 main.py
