# ============================================
# MAKEFILE - SISTEMA DE ANÁLISIS V16
# ============================================

.PHONY: help install test scan anonymize simulate clean

# Variables
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
SCRIPTS_DIR = scripts

# Colores
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m

help:
	@echo "$(YELLOW)Sistema de Análisis V16 - Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)Instalación:$(NC)"
	@echo "  make install       Instala el sistema completo"
	@echo "  make deps          Instala solo dependencias"
	@echo ""
	@echo "$(GREEN)Análisis:$(NC)"
	@echo "  make scan          Ejecuta escaneo de vulnerabilidades"
	@echo "  make anonymize     Anonimiza datos de muestra"
	@echo "  make simulate      Ejecuta simulación de impacto"
	@echo ""
	@echo "$(GREEN)Desarrollo:$(NC)"
	@echo "  make test          Ejecuta pruebas"
	@echo "  make lint          Verifica estilo de código"
	@echo "  make format        Formatea código automáticamente"
	@echo ""
	@echo "$(GREEN)Limpieza:$(NC)"
	@echo "  make clean         Limpia archivos temporales"
	@echo "  make clean-all     Limpia todo (incluye venv)"

install:
	@echo "$(YELLOW)Instalando sistema...$(NC)"
	chmod +x setup.sh
	./setup.sh

deps:
	@echo "$(YELLOW)Instalando dependencias...$(NC)"
	$(PIP) install -r requirements.txt

scan:
	@echo "$(YELLOW)Ejecutando escaneo de vulnerabilidades...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/vulnerability-scanner.py

anonymize:
	@echo "$(YELLOW)Anonimizando datos...$(NC)"
	@if [ -f "data/sample.json" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/data-anonymizer.py data/sample.json data/anonymized.json; \
	else \
		echo "$(RED)Error: data/sample.json no encontrado$(NC)"; \
		echo "Crea un archivo de muestra primero o especifica uno diferente"; \
	fi

simulate:
	@echo "$(YELLOW)Ejecutando simulación de impacto...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/impact-simulator.py --visualize

test:
	@echo "$(YELLOW)Ejecutando pruebas...$(NC)"
	$(PYTHON) -m pytest tests/ -v

lint:
	@echo "$(YELLOW)Verificando estilo de código...$(NC)"
	$(PYTHON) -m flake8 scripts/ --max-line-length=100 --ignore=E402,W503

format:
	@echo "$(YELLOW)Formateando código...$(NC)"
	$(PYTHON) -m black scripts/ --line-length=100

clean:
	@echo "$(YELLOW)Limpieza de archivos temporales...$(NC)"
	rm -rf data/processed/*
	rm -rf data/reports/*.json
	rm -rf logs/*.log
	rm -rf __pycache__ scripts/__pycache__ scripts/utils/__pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".coverage" -delete

clean-all: clean
	@echo "$(YELLOW)Limpieza completa...$(NC)"
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov

# Crear archivo de muestra para pruebas
sample:
	@echo "$(YELLOW)Creando datos de muestra...$(NC)"
	@cat > data/sample.json << 'SAMPLE'
[
  {
    "id": "INC_001",
    "timestamp": "2026-01-15T10:30:00Z",
    "coordinates": {"lat": 40.4168, "lon": -3.7038},
    "incident_type": "accident",
    "severity": "medium",
    "imei": "350123456789012",
    "device_id": "V16-12345"
  },
  {
    "id": "INC_002",
    "timestamp": "2026-01-15T14:45:00Z",
    "coordinates": {"lat": 41.3851, "lon": 2.1734},
    "incident_type": "breakdown",
    "severity": "low",
    "imei": "350987654321098",
    "device_id": "V16-67890"
  }
]
SAMPLE
	@echo "$(GREEN)Archivo de muestra creado: data/sample.json$(NC)"
