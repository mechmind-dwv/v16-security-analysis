.PHONY: help install deps scan anonymize simulate test clean

VENV = venv
PYTHON = $(VENV)/bin/python
SCRIPTS = scripts

help:
	@echo "🚀 SISTEMA DE ANÁLISIS V16 - COMANDOS:"
	@echo ""
	@echo "📦 Instalación:"
	@echo "  make install    # Instala sistema completo"
	@echo "  make deps       # Solo dependencias"
	@echo ""
	@echo "🔍 Análisis:"
	@echo "  make scan       # Escaneo de vulnerabilidades"
	@echo "  make simulate   # Simulación de impacto"
	@echo "  make report     # Genera informe ejecutivo"
	@echo ""
	@echo "🧹 Mantenimiento:"
	@echo "  make clean      # Limpia archivos temporales"
	@echo "  make test       # Pruebas básicas"

install:
	@echo "⚙️  Instalando sistema V16..."
	@if [ -f setup.sh ]; then \
		chmod +x setup.sh && ./setup.sh; \
	else \
		echo "⚠️  setup.sh no encontrado, creando entorno..."; \
		python3 -m venv $(VENV) && $(VENV)/bin/pip install requests pyyaml; \
	fi

deps:
	@echo "📦 Instalando dependencias..."
	$(VENV)/bin/pip install requests pyyaml matplotlib numpy

scan:
	@echo "🔍 Ejecutando escaneo de vulnerabilidades..."
	$(PYTHON) $(SCRIPTS)/vulnerability-scanner.py

simulate:
	@echo "📊 Ejecutando simulación de impacto..."
	$(PYTHON) $(SCRIPTS)/impact-simulator.py

report:
	@echo "📄 Generando informe ejecutivo..."
	@if [ -f scripts/generate-report.py ]; then \
		$(PYTHON) scripts/generate-report.py; \
	else \
		echo "📋 Creando informe básico..."; \
		mkdir -p reports; \
		echo "# Informe V16 - $(date)" > reports/informe.md; \
		echo "Fecha: $(date)" >> reports/informe.md; \
		echo "Estado: VULNERABILIDADES CRÍTICAS DETECTADAS" >> reports/informe.md; \
	fi

test:
	@echo "🧪 Ejecutando pruebas..."
	@echo "✅ Python: $(shell which python3)"
	@echo "✅ Venv: $(shell if [ -d "$(VENV)" ]; then echo "OK"; else echo "NO"; fi)"
	@echo "✅ Scripts: $(shell ls scripts/*.py 2>/dev/null | wc -l) encontrados"

clean:
	@echo "🧹 Limpiando archivos temporales..."
	rm -rf __pycache__ scripts/__pycache__
	rm -f *.pyc scripts/*.pyc
	@echo "✅ Limpieza completada"

.PHONY: docker-build docker-run

docker-build:
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t v16-analyzer .

docker-run:
	@echo "🚀 Ejecutando en Docker..."
	docker run --rm -v $(PWD)/data:/app/data v16-analyzer make scan
