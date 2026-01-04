#!/bin/bash
# Script para ejecutar tests de Bet-Copilot

echo "╔═══════════════════════════════════════════════════╗"
echo "║   Bet-Copilot Test Suite                         ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Función para mostrar menú
show_menu() {
    echo -e "${CYAN}Tests Disponibles:${NC}"
    echo ""
    echo "  [1] All Tests (pytest)"
    echo "  [2] Unit Tests (core functionality)"
    echo "  [3] Command Input Tests (interactive)"
    echo "  [4] Completion Debug (logic only)"
    echo "  [5] Completion Interactive (full UI)"
    echo "  [6] Autocompletion with Mock Data"
    echo "  [7] Coverage Report"
    echo ""
    echo "  [0] Exit"
    echo ""
}

# Función para ejecutar pytest
run_pytest() {
    local pattern=$1
    local description=$2
    
    echo -e "${CYAN}Running: $description${NC}"
    echo "─────────────────────────────────────────────────"
    
    if [ -z "$pattern" ]; then
        pytest bet_copilot/tests/ -v
    else
        pytest bet_copilot/tests/$pattern -v
    fi
    
    local exit_code=$?
    echo ""
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Tests passed${NC}"
    else
        echo -e "${RED}✗ Tests failed${NC}"
    fi
    
    return $exit_code
}

# Función para ejecutar script interactivo
run_interactive() {
    local script=$1
    local description=$2
    
    echo -e "${CYAN}Running: $description${NC}"
    echo -e "${YELLOW}(Press Ctrl+C to exit)${NC}"
    echo "─────────────────────────────────────────────────"
    echo ""
    
    python3 bet_copilot/tests/$script
    
    echo ""
    echo -e "${GREEN}✓ Interactive test completed${NC}"
}

# Main loop
while true; do
    show_menu
    read -p "Select option (0-7): " choice
    echo ""
    
    case $choice in
        1)
            run_pytest "" "All Unit Tests"
            ;;
        2)
            run_pytest "test_poisson.py test_kelly.py test_soccer_predictor.py" "Core Math Tests"
            ;;
        3)
            run_interactive "test_command_input.py" "Command Input Basic Test"
            ;;
        4)
            echo -e "${CYAN}Running: Completion Logic Debug${NC}"
            echo "─────────────────────────────────────────────────"
            python3 bet_copilot/tests/test_completion_debug.py
            echo ""
            echo -e "${GREEN}✓ Debug test completed${NC}"
            ;;
        5)
            run_interactive "test_completion_interactive.py" "Completion Interactive Test"
            ;;
        6)
            run_interactive "test_autocompletion.py" "Autocompletion with Mock Data"
            ;;
        7)
            echo -e "${CYAN}Running: Coverage Report${NC}"
            echo "─────────────────────────────────────────────────"
            
            # Check if pytest-cov is installed
            if pytest --version 2>&1 | grep -q "pytest"; then
                if python3 -c "import pytest_cov" 2>/dev/null; then
                    pytest --cov=bet_copilot --cov-report=term-missing bet_copilot/tests/
                else
                    echo -e "${YELLOW}⚠ pytest-cov not installed${NC}"
                    echo ""
                    echo "Install with:"
                    echo "  pip install pytest-cov"
                    echo "  # or"
                    echo "  pip install -r requirements.txt"
                    echo ""
                    echo "Running tests without coverage..."
                    pytest bet_copilot/tests/ -v
                fi
            else
                echo -e "${RED}✗ pytest not found${NC}"
            fi
            echo ""
            ;;
        0)
            echo -e "${GREEN}Goodbye!${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            echo ""
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done
