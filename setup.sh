#!/bin/bash

# ============================================
# INSTALADOR - SISTEMA DE ANÁLISIS V16
# ============================================

set -e  # Salir en error

echo "🔧 Instalando sistema de análisis V16..."
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}[✓]${NC} $1"; }
info() { echo -e "${BLUE}[i]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

# Verificar Python
info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    error "Python3 no encontrado. Instálalo primero."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
success "Python $PYTHON_VERSION detectado"

# Verificar pip
info "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    warn "pip3 no encontrado. Instalando..."
    sudo apt-get update && sudo apt-get install -y python3-pip
fi

success "pip3 disponible"

# Crear entorno virtual (opcional pero recomendado)
info "Creando entorno virtual Python..."
python3 -m venv venv --prompt="v16-analysis"

success "Entorno virtual creado"

# Activar entorno virtual
info "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
info "Instalando dependencias Python..."

cat > requirements.txt << 'REQUIREMENTS'
# Análisis de datos
requests>=2.28.0
PyYAML>=6.0
pandas>=1.5.0
numpy>=1.24.0

# Seguridad y hashing
cryptography>=40.0.0

# Visualización (opcional)
matplotlib>=3.7.0
seaborn>=0.12.0

# Testing y desarrollo
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0

# Utilidades
python-dateutil>=2.8.0
tqdm>=4.65.0
REQUIREMENTS

pip install --upgrade pip
pip install -r requirements.txt

success "Dependencias instaladas"

# Hacer scripts ejecutables
info "Configurando scripts..."
chmod +x scripts/*.py
chmod +x scripts/utils/*.py 2>/dev/null || true

# Crear directorios necesarios
info "Creando estructura de directorios..."
mkdir -p {data/{raw,processed,reports},logs,exports,backups}

# Configurar permisos
info "Configurando permisos..."
find . -type f -name "*.py" -exec chmod 755 {} \; 2>/dev/null || true
chmod 644 config/*.yaml config/*.json 2>/dev/null || true

# Crear archivo de entorno de ejemplo
info "Creando configuración de entorno..."
cat > .env.example << 'ENVEXAMPLE'
# Configuración del sistema de análisis V16
# Copiar a .env y modificar valores

# API Endpoints (oficiales)
DGT_API_URL="https://etraffic.dgt.es/etrafficWEB/"
DGT_MAP_URL="https://mapabalizasv16.es/#mapa"

# Configuración de seguridad
API_KEY=""  # Si la API requiere autenticación
RATE_LIMIT=10  # requests por minuto

# Configuración de anonimización
ANONYMIZATION_LEVEL="medium"
GPS_PRECISION=2

# Configuración de logging
LOG_LEVEL="INFO"
LOG_FILE="logs/v16_analysis.log"

# Notificaciones (opcional)
ALERT_WEBHOOK=""
ALERT_EMAIL=""
ENVEXAMPLE

# Verificación final
info "Verificando instalación..."
echo ""

# Pruebas básicas
if python3 -c "import requests, yaml, pandas" &> /dev/null; then
    success "Módulos Python cargados correctamente"
else
    error "Error cargando módulos Python"
    exit 1
fi

if [ -f "scripts/vulnerability-scanner.py" ] && [ -x "scripts/vulnerability-scanner.py" ]; then
    success "Scripts configurados correctamente"
else
    error "Error configurando scripts"
    exit 1
fi

echo ""
echo "======================================"
success "INSTALACIÓN COMPLETADA"
echo "======================================"
echo ""
echo "📁 Estructura creada:"
echo "   scripts/     - Herramientas de análisis"
echo "   config/      - Configuraciones"
echo "   data/        - Datos y reportes"
echo "   logs/        - Logs del sistema"
echo ""
echo "🚀 Para empezar:"
echo "   1. source venv/bin/activate"
echo "   2. cp .env.example .env"
echo "   3. Edita .env con tu configuración"
echo "   4. python scripts/vulnerability-scanner.py"
echo ""
echo "📚 Documentación en docs/"
echo "🐛 Reportar issues en GitHub"
echo ""
echo "======================================"

# Crear alias útiles
cat >> ~/.bashrc << 'ALIASES'

# Aliases para sistema V16 Analysis
alias v16-activate="source $(pwd)/venv/bin/activate"
alias v16-scan="cd $(pwd) && python scripts/vulnerability-scanner.py"
alias v16-anonymize="cd $(pwd) && python scripts/data-anonymizer.py"
alias v16-simulate="cd $(pwd) && python scripts/impact-simulator.py"
ALIASES

warn "Se han añadido aliases a ~/.bashrc. Ejecuta 'source ~/.bashrc' para usarlos."
