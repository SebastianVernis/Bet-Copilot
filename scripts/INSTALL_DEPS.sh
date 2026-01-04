#!/bin/bash
# Script para instalar dependencias de Bet-Copilot

echo "╔═══════════════════════════════════════╗"
echo "║   Instalando Dependencias             ║"
echo "║   Bet-Copilot v0.5.0                  ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Detectar si estamos en un venv
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment detectado: $VIRTUAL_ENV"
    pip install -r requirements.txt
else
    echo "⚠ No se detectó virtual environment"
    echo ""
    echo "Opciones:"
    echo "  1. Instalar con --user (recomendado)"
    echo "  2. Crear virtual environment"
    echo "  3. Instalar system-wide (requiere permisos)"
    echo ""
    read -p "Selecciona opción (1-3): " option
    
    case $option in
        1)
            echo "Instalando con --user..."
            pip install --user -r requirements.txt
            ;;
        2)
            echo "Creando virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
            echo ""
            echo "✓ Virtual environment creado en ./venv"
            echo "  Actívalo con: source venv/bin/activate"
            ;;
        3)
            echo "Instalando system-wide..."
            sudo pip install -r requirements.txt
            ;;
        *)
            echo "Opción inválida"
            exit 1
            ;;
    esac
fi

echo ""
echo "✓ Dependencias instaladas"
echo ""
echo "Dependencias clave:"
echo "  • prompt_toolkit - Input avanzado con historial y completado"
echo "  • google-generativeai - Cliente Gemini AI"
echo "  • rich - UI terminal"
echo "  • aiohttp - HTTP async"
echo "  • aiosqlite - Database async"
echo "  • pytest + pytest-cov - Testing"
echo ""
echo "Para dependencias de desarrollo (black, mypy, etc.):"
echo "  pip install -r requirements-dev.txt"
echo ""
