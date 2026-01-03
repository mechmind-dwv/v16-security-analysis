# ============================================
# MAKEFILE - SISTEMA DE ANÁLISIS V16
# ============================================

.PHONY: help install deps scan anonymize simulate map-analyze test-api clean clean-all sample

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
SCRIPTS_DIR = scripts

help:
	@echo "Sistema de Análisis V16 - Comandos disponibles:"
	@echo ""
	@echo "Instalación:"
	@echo "  make install       Instala el sistema completo"
	@echo "  make deps          Instala solo dependencias"
	@echo ""
	@echo "Análisis:"
	@echo "  make scan          Ejecuta escaneo de vulnerabilidades"
	@echo "  make anonymize     Anonimiza datos de muestra"
	@echo "  make simulate      Ejecuta simulación de impacto"
	@echo "  make map-analyze   Analiza datos del mapa V16"
	@echo "  make test-api      Prueba endpoints DGT"
	@echo ""
	@echo "Utilidades:"
	@echo "  make sample        Crea datos de muestra"
	@echo "  make report        Genera informe ejecutivo"
	@echo "  make clean         Limpia archivos temporales"
	@echo "  make clean-all     Limpia todo (incluye venv)"

install:
	@echo "Instalando sistema..."
	chmod +x setup.sh
	./setup.sh

deps:
	@echo "Instalando dependencias..."
	$(PIP) install -r requirements.txt

scan:
	@echo "Ejecutando escaneo de vulnerabilidades..."
	$(PYTHON) $(SCRIPTS_DIR)/vulnerability-scanner.py

anonymize:
	@echo "Anonimizando datos..."
	@if [ -f "data/sample.json" ]; then \
		$(PYTHON) $(SCRIPTS_DIR)/data-anonymizer.py data/sample.json data/anonymized.json; \
	else \
		echo "Error: data/sample.json no encontrado"; \
		echo "Crea un archivo de muestra primero: make sample"; \
	fi

simulate:
	@echo "Ejecutando simulación de impacto..."
	$(PYTHON) $(SCRIPTS_DIR)/impact-simulator.py --visualize

map-analyze:
	@echo "Analizando datos del mapa V16..."
	$(PYTHON) $(SCRIPTS_DIR)/v16-map-analyzer.py

test-api:
	@echo "Probando endpoints DGT..."
	$(PYTHON) $(SCRIPTS_DIR)/test-api.py

report:
	@echo "Generando informe ejecutivo..."
	$(PYTHON) scripts/generate-report.py

sample:
	@echo "Creando datos de muestra..."
	@mkdir -p data
	@cat > data/sample.json << "SAMPLE_EOF"
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
SAMPLE_EOF
	@echo "Archivo de muestra creado: data/sample.json"

clean:
	@echo "Limpieza de archivos temporales..."
	rm -rf data/processed/*
	rm -rf data/reports/*.json
	rm -rf logs/*.log
	rm -rf __pycache__ scripts/__pycache__ scripts/utils/__pycache__
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".coverage" -delete

clean-all: clean
	@echo "Limpieza completa..."
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov

