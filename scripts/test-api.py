#!/usr/bin/env python3
"""
Script de prueba para verificar endpoints DGT
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, description):
    """Prueba un endpoint específico"""
    print(f"\n🔍 Probando: {description}")
    print(f"   URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            # Intentar parsear como JSON
            try:
                data = response.json()
                print(f"   Tipo de respuesta: JSON")
                print(f"   Tamaño: {len(response.text)} caracteres")
                print(f"   Muestra (primeros 200 chars):")
                print(f"   {response.text[:200]}...")
                
                # Buscar datos sensibles
                if isinstance(data, dict):
                    sensitive_keys = [k for k in data.keys() if any(
                        term in k.lower() for term in ['coord', 'lat', 'lon', 'gps', 'location']
                    )]
                    if sensitive_keys:
                        print(f"   ⚠️  Campos sensibles encontrados: {sensitive_keys}")
                
            except json.JSONDecodeError:
                print(f"   Tipo de respuesta: HTML/Texto")
                print(f"   Tamaño: {len(response.text)} caracteres")
                
                # Buscar patrones de coordenadas
                import re
                coord_patterns = [
                    r'"lat":\s*([-+]?\d*\.\d+|\d+)',
                    r'"lon":\s*([-+]?\d*\.\d+|\d+)',
                    r'"latitude":\s*([-+]?\d*\.\d+|\d+)',
                    r'"longitude":\s*([-+]?\d*\.\d+|\d+)'
                ]
                
                for pattern in coord_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        print(f"   ⚠️  Coordenadas encontradas: {matches[:3]}...")
                
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    """Función principal"""
    print("="*60)
    print("PRUEBA DE ENDPOINTS DGT - BALIZAS V16")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    endpoints = [
        ("https://mapabalizasv16.es", "Mapa principal V16"),
        ("https://etraffic.dgt.es/etrafficWEB", "API eTraffic DGT"),
        ("https://www.dgt.es", "Web principal DGT"),
    ]
    
    results = []
    for url, desc in endpoints:
        status = test_endpoint(url, desc)
        results.append((desc, status))
    
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS:")
    print("="*60)
    
    for desc, status in results:
        if status == 200:
            print(f"✅ {desc}: ACCESIBLE")
        elif status is None:
            print(f"❌ {desc}: ERROR")
        else:
            print(f"⚠️  {desc}: Status {status}")
    
    print("\n🎯 Recomendaciones:")
    print("1. Verificar manualmente https://mapabalizasv16.es/#mapa")
    print("2. Usar herramientas como Burp Suite o OWASP ZAP para análisis profundo")
    print("3. Monitorizar el tráfico de red para descubrir endpoints API")
    print("="*60)

if __name__ == "__main__":
    main()
