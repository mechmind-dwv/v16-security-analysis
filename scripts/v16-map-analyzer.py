#!/usr/bin/env python3
"""
Analizador específico del mapa V16 - Basado en datos reales capturados
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class V16MapAnalyzer:
    """Analiza datos expuestos en el mapa V16"""
    
    @staticmethod
    def parse_incident_from_text(text: str) -> Optional[Dict]:
        """Parsea un incidente desde texto copiado del mapa"""
        incident = {}
        
        # Patrones para extraer información
        patterns = {
            'carretera': r'Carretera:\s*(.+)',
            'pk': r'PK:\s*([\d.]+)',
            'sentido': r'Sentido:\s*(.+)',
            'orientacion': r'Orientación:\s*(.+)',
            'desde': r'Desde:\s*(.+)',
            'comunidad': r'Comunidad:\s*(.+)',
            'provincia': r'Provincia:\s*(.+)',
            'municipio': r'Municipio:\s*(.+)',
            'ultima_señal': r'Última señal hace\s*(.+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                incident[key] = match.group(1).strip()
        
        # Convertir fecha
        if 'desde' in incident:
            try:
                # Formato: "3/1/2026, 14:27:04"
                date_str = incident['desde']
                dt = datetime.strptime(date_str, "%d/%m/%Y, %H:%M:%S")
                incident['timestamp_iso'] = dt.isoformat()
                incident['timestamp_unix'] = int(dt.timestamp())
            except ValueError:
                incident['timestamp_iso'] = incident['desde']
        
        # Calcular coordenadas aproximadas desde PK
        if 'carretera' in incident and 'pk' in incident:
            incident['coordenadas_aproximadas'] = V16MapAnalyzer.estimate_coordinates(
                incident['carretera'], 
                float(incident['pk'])
            )
        
        return incident if incident else None
    
    @staticmethod
    def estimate_coordinates(highway: str, pk: float) -> Dict[str, float]:
        """Estima coordenadas aproximadas basadas en carretera y PK"""
        # Datos de referencia aproximados (ejemplos)
        highway_reference_points = {
            'AP-4': {'lat': 36.5, 'lon': -6.2, 'direction': 'north-south'},
            'AP-7': {'lat': 41.4, 'lon': 2.2, 'direction': 'north-south'},
            'A-2': {'lat': 40.4, 'lon': -3.7, 'direction': 'east-west'},
            'A-6': {'lat': 40.4, 'lon': -3.7, 'direction': 'northwest'},
            'M-30': {'lat': 40.4, 'lon': -3.7, 'direction': 'circular'},
        }
        
        ref = highway_reference_points.get(highway, {'lat': 40.4, 'lon': -3.7})
        
        # Aproximación muy básica
        lat = ref['lat'] + (pk * 0.001 if 'north' in ref['direction'] else 0)
        lon = ref['lon'] + (pk * 0.001 if 'east' in ref['direction'] else 0)
        
        return {
            'lat': round(lat, 6),
            'lon': round(lon, 6),
            'precision': 'low',
            'source': 'estimated_from_pk'
        }
    
    @staticmethod
    def analyze_vulnerabilities(incident: Dict) -> List[str]:
        """Analiza vulnerabilidades en los datos expuestos"""
        vulnerabilities = []
        
        # Verificar exposición de datos
        if 'municipio' in incident:
            vulnerabilities.append("📍 Ubicación municipal expuesta")
        
        if 'timestamp_iso' in incident:
            vulnerabilities.append("⏰ Timestamp exacto expuesto")
        
        if 'carretera' in incident and 'pk' in incident:
            vulnerabilities.append("🛣️ Localización exacta en carretera (PK específico)")
        
        if 'sentido' in incident:
            vulnerabilities.append("🧭 Dirección de viaje expuesta")
        
        # Evaluar riesgo
        risk_factors = []
        if 'ultima_señal' in incident and 'minutos' in incident['ultima_señal']:
            minutes = int(re.search(r'(\d+)', incident['ultima_señal']).group(1))
            if minutes < 30:
                risk_factors.append(f"Incidente reciente ({minutes} minutos)")
        
        if risk_factors:
            vulnerabilities.append(f"⚠️ RIESGO ALTO: {', '.join(risk_factors)}")
        
        return vulnerabilities
    
    @staticmethod
    def generate_report(incidents: List[Dict]) -> Dict:
        """Genera reporte de análisis"""
        report = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_incidents": len(incidents),
                "analyzer_version": "1.0.0"
            },
            "incidents": incidents,
            "statistics": {
                "by_provincia": {},
                "by_carretera": {},
                "time_distribution": {}
            },
            "vulnerability_analysis": {
                "total_vulnerabilities": 0,
                "vulnerabilities_by_type": {},
                "risk_assessment": "unknown"
            },
            "recommendations": [
                "🔒 Implementar autenticación para acceso a datos en tiempo real",
                "📍 Anonimizar ubicaciones (usar área en lugar de punto exacto)",
                "⏰ Retrasar publicación de incidentes (15-30 minutos)",
                "🚫 Limitar información expuesta (ocultar PK exacto, sentido)",
                "👤 Requerir autenticación para ver datos detallados"
            ]
        }
        
        # Estadísticas
        for incident in incidents:
            # Por provincia
            prov = incident.get('provincia', 'Desconocida')
            report["statistics"]["by_provincia"][prov] = \
                report["statistics"]["by_provincia"].get(prov, 0) + 1
            
            # Por carretera
            carr = incident.get('carretera', 'Desconocida')
            report["statistics"]["by_carretera"][carr] = \
                report["statistics"]["by_carretera"].get(carr, 0) + 1
        
        # Análisis de vulnerabilidades
        vuln_count = 0
        vuln_types = {}
        
        for incident in incidents:
            vulns = V16MapAnalyzer.analyze_vulnerabilities(incident)
            vuln_count += len(vulns)
            
            for vuln in vulns:
                vuln_types[vuln] = vuln_types.get(vuln, 0) + 1
        
        report["vulnerability_analysis"]["total_vulnerabilities"] = vuln_count
        report["vulnerability_analysis"]["vulnerabilities_by_type"] = vuln_types
        
        # Evaluación de riesgo
        if vuln_count > 10:
            report["vulnerability_analysis"]["risk_assessment"] = "CRITICAL"
        elif vuln_count > 5:
            report["vulnerability_analysis"]["risk_assessment"] = "HIGH"
        elif vuln_count > 0:
            report["vulnerability_analysis"]["risk_assessment"] = "MEDIUM"
        else:
            report["vulnerability_analysis"]["risk_assessment"] = "LOW"
        
        return report

def main():
    """Función principal"""
    print("="*60)
    print("ANALIZADOR DE DATOS MAPA V16 - BASADO EN DATOS REALES")
    print("="*60)
    
    # Ejemplo de dato real capturado
    sample_text = """Baliza reciente
Carretera: AP-4
PK: 102.8
Sentido: Decreciente
Orientación: Este
Desde: 3/1/2026, 14:27:04
Comunidad: Andalucía
Provincia: Cádiz
Municipio: Puerto Real

Última señal hace 25 minutos"""
    
    print("\n📋 DATO DE EJEMPLO (capturado de https://mapabalizasv16.es/#mapa):")
    print("-"*60)
    print(sample_text)
    print("-"*60)
    
    # Analizar el incidente
    analyzer = V16MapAnalyzer()
    incident = analyzer.parse_incident_from_text(sample_text)
    
    if incident:
        print("\n✅ INCIDENTE ANALIZADO:")
        for key, value in incident.items():
            print(f"   • {key}: {value}")
        
        # Analizar vulnerabilidades
        vulnerabilities = analyzer.analyze_vulnerabilities(incident)
        
        print("\n🚨 VULNERABILIDADES IDENTIFICADAS:")
        for vuln in vulnerabilities:
            print(f"   • {vuln}")
        
        # Generar reporte
        report = analyzer.generate_report([incident])
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/reports", exist_ok=True)
        
        report_file = f"data/reports/map_analysis_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN EJECUTIVO:")
        print("="*60)
        print(f"📊 Total vulnerabilidades: {report['vulnerability_analysis']['total_vulnerabilities']}")
        print(f"⚠️  Nivel de riesgo: {report['vulnerability_analysis']['risk_assessment']}")
        print(f"📍 Ubicación: {incident.get('municipio', 'N/A')}, {incident.get('provincia', 'N/A')}")
        print(f"⏰ Tiempo desde activación: {incident.get('ultima_señal', 'N/A')}")
        
        print("\n🎯 RECOMENDACIONES INMEDIATAS:")
        for i, rec in enumerate(report['recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    
    else:
        print("\n❌ No se pudo analizar el incidente")
    
    print("\n" + "="*60)
    print("INSTRUCCIONES PARA CAPTURAR MÁS DATOS:")
    print("="*60)
    print("1. 🌐 Visitar https://mapabalizasv16.es/#mapa")
    print("2. 🖱️  Hacer clic en cualquier baliza (punto naranja/rojo)")
    print("3. 📋 Copiar toda la información que aparece")
    print("4. 💾 Guardar en un archivo .txt")
    print("5. 🔄 Ejecutar este script con los datos capturados")
    print("="*60)

if __name__ == "__main__":
    main()
