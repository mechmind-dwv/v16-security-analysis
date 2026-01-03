#!/bin/bash
# Script para desplegar proyecto V16 Security Analysis a GitHub

set -e  # Salir en error

echo "🚀 DESPLIEGUE A GITHUB - V16 SECURITY ANALYSIS"
echo "=============================================="

# Configuración
REPO_NAME="v16-security-analysis"
USER_NAME="$1"
GITHUB_TOKEN="$2"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
info() { echo -e "${BLUE}[i]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# Verificar parámetros
if [ -z "$USER_NAME" ]; then
    echo "Uso: $0 <tu_usuario_github> [token]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 tuusuario"
    echo "  $0 tuusuario ghp_tu_token_aqui"
    exit 1
fi

# Paso 1: Verificar estructura
info "1. Verificando estructura del proyecto..."
if [ ! -f "README.md" ]; then
    error "README.md no encontrado"
fi

if [ ! -d "scripts" ]; then
    error "Directorio scripts/ no encontrado"
fi

success "Estructura OK"

# Paso 2: Inicializar git si no existe
info "2. Configurando repositorio git..."
if [ ! -d ".git" ]; then
    git init
    git config user.name "$USER_NAME"
    git config user.email "$USER_NAME@users.noreply.github.com"
    success "Repositorio inicializado"
else
    success "Repositorio ya existe"
fi

# Paso 3: Crear .gitignore si no existe
info "3. Configurando .gitignore..."
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.env

# Data
data/raw/
*.csv
*.pkl

# Logs
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporal
tmp/
temp/

# Reportes (excepto muestras)
reports/*.pdf
reports/*.docx

# Configuraciones sensibles
*.key
*.pem
secrets.yaml
GITIGNORE
    success ".gitignore creado"
else
    success ".gitignore ya existe"
fi

# Paso 4: Añadir archivos
info "4. Añadiendo archivos al repositorio..."
git add .

# Paso 5: Crear commit
info "5. Creando commit..."
COMMIT_MSG="🚀 Initial commit: V16 Security Analysis System

- Vulnerability scanner for DGT V16 system
- Impact simulator and data anonymizer
- Professional documentation and reports
- Ethical security research tools
- CVE-2025-65855 analysis included

Endpoints analyzed:
• https://mapabalizasv16.es/#mapa
• https://etraffic.dgt.es/etrafficWEB/

CVE Reference: https://www.cve.org/CVERecord?id=CVE-2025-65855"

git commit -m "$COMMIT_MSG" || {
    warn "No hay cambios para commit (puede ser normal si ya existe)"
}

# Paso 6: Crear repositorio remoto
info "6. Configurando repositorio remoto en GitHub..."

# Verificar si ya existe el remoto
if git remote | grep -q origin; then
    warn "Remote 'origin' ya existe, actualizando..."
    git remote remove origin
fi

# URL del repositorio
REPO_URL="https://github.com/$USER_NAME/$REPO_NAME"

# Si tenemos token, usar URL con token
if [ -n "$GITHUB_TOKEN" ]; then
    REPO_URL="https://$GITHUB_TOKEN@github.com/$USER_NAME/$REPO_NAME"
fi

# Intentar crear repositorio via API si no existe
info "Intentando crear repositorio en GitHub..."
if ! curl -s -H "Authorization: token $GITHUB_TOKEN" \
          -d '{"name":"'"$REPO_NAME"'","description":"Security analysis of DGT V16 emergency beacons system","private":false,"has_issues":true,"has_wiki":false,"has_projects":false}' \
          https://api.github.com/user/repos 2>/dev/null | grep -q '"name"'; then
    warn "No se pudo crear repositorio via API (puede que ya exista o falte token)"
    warn "Crea manualmente: https://github.com/new"
    warn "Nombre: $REPO_NAME"
    warn "Descripción: Security analysis of DGT V16 emergency beacons system"
    warn "Público, con README e issues"
    read -p "Presiona Enter después de crear el repositorio..." _
fi

# Configurar remote
git remote add origin "https://github.com/$USER_NAME/$REPO_NAME.git"
success "Remote configurado: $REPO_URL"

# Paso 7: Subir código
info "7. Subiendo código a GitHub..."
git branch -M main

if git push -u origin main; then
    success "¡Código subido exitosamente!"
else
    warn "Error en push, intentando con fuerza..."
    git push -u origin main --force
fi

# Paso 8: Crear tag de versión
info "8. Creando versión 1.0.0..."
git tag -a v1.0.0 -m "Version 1.0.0: Complete security analysis system" 2>/dev/null || true
git push origin v1.0.0 2>/dev/null || true

# Paso 9: Mostrar resumen
echo ""
echo "=============================================="
success "🎉 DESPLIEGUE COMPLETADO"
echo "=============================================="
echo ""
echo "📊 RESUMEN:"
echo "  • Repositorio: https://github.com/$USER_NAME/$REPO_NAME"
echo "  • Versión: 1.0.0"
echo "  • Branch: main"
echo ""
echo "🚀 ACCESO RÁPIDO:"
echo "  • git clone https://github.com/$USER_NAME/$REPO_NAME.git"
echo "  • cd $REPO_NAME"
echo "  • make install"
echo ""
echo "📢 PRÓXIMOS PASOS:"
echo "  1. Verificar el repositorio en GitHub"
echo "  2. Configurar GitHub Pages (opcional)"
echo "  3. Compartir en redes sociales"
echo "  4. Actualizar README con badges"
echo ""
echo "🐛 REPORTAR PROBLEMAS:"
echo "  • Issues: $REPO_URL/issues"
echo ""
echo "⭐ ¡No olvides darle una estrella al proyecto!"
echo "=============================================="

# Paso 10: Crear archivo de estado
cat > DEPLOYMENT_INFO.md << 'DEPLOYINFO'
# Deployment Information

- **Repository**: $REPO_NAME
- **User**: $USER_NAME
- **URL**: https://github.com/$USER_NAME/$REPO_NAME
- **Version**: 1.0.0
- **Deployed**: $(date)
- **Status**: ACTIVE

## Quick Start
```bash
git clone https://github.com/$USER_NAME/$REPO_NAME.git
cd $REPO_NAME
make install
make scan
Features Deployed

    ✅ Vulnerability Scanner

    ✅ Impact Simulator

    ✅ Data Anonymizer

    ✅ Professional Reports

    ✅ CVE-2025-65855 Analysis

    ✅ DGT API Integration

Security Notes

This repository is for ethical security research only.
Do not use for illegal activities.
DEPLOYINFO

success "Información de despliegue guardada en DEPLOYMENT_INFO.md"
