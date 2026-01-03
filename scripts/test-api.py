#!/usr/bin/env python3
"""
Script de prueba para verificar endpoints DGT - COMPLETO
"""

import requests
import json
import re
from datetime import datetime
from typing import Optional, Dict, List

def test_endpoint(url: str, description: str) -> Optional[int]:
    """Prueba un endpoint específico"""
    print(f"\n🔍 Probando: {description}")
    print(f"   URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Referer': 'https://mapabalizasv16.es/'
    }
    
    try:
        # Desactivar proxy para esta prueba
        session = requests.Session()
        session.trust_env = False  # No usar proxy del sistema
        
        response = session.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            # Intentar parsear como JSON
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                try:
                    data = response.json()
                    print(f"   ✅ Tipo: JSON")
                    print(f"   📊 Tamaño: {len(response.text)} caracteres")
                    
                    # Mostrar estructura si es pequeño
                    if len(response.text) < 1000:
                        print(f"   📋 Contenido:")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                    else:
                        print(f"   📋 Muestra (200 chars): {response.text[:200]}...")
                    
                    # Buscar datos sensibles
                    sensitive_data = find_sensitive_data(data)
                    if sensitive_data:
                        print(f"   ⚠️  DATOS SENSIBLES ENCONTRADOS:")
                        for key, value in sensitive_data.items():
                            print(f"      • {key}: {value}")
                    
                except json.JSONDecodeError:
                    print(f"   ℹ️  Tipo: Texto/HTML (JSON inválido)")
                    print(f"   📊 Tamaño: {len(response.text)} caracteres")
                    analyze_text_response(response.text)
            
            else:
                print(f"   ℹ️  Tipo: {content_type}")
                print(f"   📊 Tamaño: {len(response.text)} caracteres")
                analyze_text_response(response.text)
        
        elif response.status_code == 403:
            print(f"   🔒 Acceso denegado (403)")
        elif response.status_code == 404:
            print(f"   ❓ No encontrado (404)")
        elif response.status_code == 429:
            print(f"   ⚡ Rate limiting detectado (429)")
        
        return response.status_code
        
    except requests.exceptions.ProxyError:
        print(f"   🚫 Error de proxy. Intenta: unset HTTP_PROXY HTTPS_PROXY")
        return None
    except requests.exceptions.SSLError:
        print(f"   🔐 Error SSL")
        return None
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout")
        return None
    except requests.exceptions.ConnectionError:
        print(f"   🔌 Error de conexión")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def find_sensitive_data(data, path="") -> Dict:
    """Busca datos sensibles en estructuras anidadas"""
    sensitive_patterns = [
        ('coord', ['lat', 'lon', 'latitude', 'longitude', 'coord', 'gps']),
        ('time', ['timestamp', 'time', 'date', 'hora', 'fecha']),
        ('location', ['location', 'ubicacion', 'address', 'direccion']),
        ('vehicle', ['vehicle', 'vehiculo', 'plate', 'matricula', 'imei', 'imsi']),
        ('personal', ['name', 'nombre', 'phone', 'telefono', 'dni', 'email'])
    ]
    
    found = {}
    
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            # Verificar si la clave es sensible
            for category, patterns in sensitive_patterns:
                if any(pattern in str(key).lower() for pattern in patterns):
                    found[current_path] = f"{value}"[:100] if value else "null"
            
            # Buscar recursivamente
            found.update(find_sensitive_data(value, current_path))
    
    elif isinstance(data, list):
        for i, item in enumerate(data[:3]):  # Limitar profundidad
            found.update(find_sensitive_data(item, f"{path}[{i}]"))
    
    return found

def analyze_text_response(text: str):
    """Analiza respuestas de texto/HTML"""
    # Buscar coordenadas en texto
    coord_patterns = [
        r'"lat":\s*([-+]?\d*\.\d+|\d+)',
        r'"lon":\s*([-+]?\d*\.\d+|\d+)',
        r'"latitude":\s*([-+]?\d*\.\d+|\d+)',
        r'"longitude":\s*([-+]?\d*\.\d+|\d+)',
        r'lat=([-+]?\d*\.\d+|\d+)',
        r'lon=([-+]?\d*\.\d+|\d+)',
        r'POINT\(([-+]?\d*\.\d+)\s+([-+]?\d*\.\d+)\)'
    ]
    
    for pattern in coord_patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"   ⚠️  Coordenadas encontradas con patrón '{pattern}':")
            for match in matches[:3]:
                print(f"      • {match}")
    
    # Buscar URLs de API
    api_patterns = [
        r'https?://[^"\']+/api/[^"\']+',
        r'https?://[^"\']+/v[0-9]+/[^"\']+',
        r'fetch\(["\']([^"\']+)["\']\)',
        r'axios\.get\(["\']([^"\']+)["\']\)'
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"   🔗 URLs de API encontradas:")
            for match in matches[:3]:
                print(f"      • {match}")

def test_map_interaction():
    """Prueba interacción con el mapa V16"""
    print("\n" + "="*60)
    print("PRUEBA DE INTERACCIÓN CON MAPA V16")
    print("="*60)
    
    # Simular lo que ves en https://mapabalizasv16.es/#mapa
    sample_incident = {
        "carretera": "AP-4",
        "pk": "102.8",
        "sentido": "Decreciente",
        "orientacion": "Este",
        "desde": "3/1/2026, 14:27:04",
        "comunidad": "Andalucía",
        "provincia": "Cádiz",
        "municipio": "Puerto Real",
        "ultima_señal": "hace 25 minutos"
    }
    
    print("🎯 DATO DEL MAPA CAPTURADO MANUALMENTE:")
    for key, value in sample_incident.items():
        print(f"   • {key}: {value}")
    
    print("\n⚠️  ANÁLISIS DE VULNERABILIDAD:")
    print("   1. ✅ Ubicación exacta expuesta (AP-4, PK 102.8)")
    print("   2. ✅ Hora exacta de activación (14:27:04)")
    print("   3. ✅ Municipio y provincia identificados")
    print("   4. ✅ Tiempo transcurrido visible (25 minutos)")
    print("   5. ❌ Sin autenticación requerida")
    print("   6. ❌ Sin anonimización de datos")
    
    return sample_incident

def main():
    """Función principal"""
    print("="*60)
    print("PRUEBA COMPLETA DE ENDPOINTS DGT - BALIZAS V16")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Nota: Si hay error de proxy, ejecuta: unset HTTP_PROXY HTTPS_PROXY")
    print("="*60)
    
    # Desactivar proxy para esta sesión
    import os
    os.environ.pop('HTTP_PROXY', None)
    os.environ.pop('HTTPS_PROXY', None)
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    
    # Endpoints a probar
    endpoints = [
        ("https://mapabalizasv16.es", "Mapa principal V16"),
        ("https://www.dgt.es", "Web principal DGT"),
        ("https://mapa.dgt.es", "Mapa DGT general"),
    ]
    
    # Endpoints de API potenciales (basados en análisis)
    api_endpoints = [
        ("https://mapabalizasv16.es/api/incidents", "API Incidencias"),
        ("https://mapabalizasv16.es/data/incidents.json", "Datos JSON"),
        ("https://mapabalizasv16.es/incidents", "Incidencias directo"),
    ]
    
    results = []
    
    # Probar endpoints principales
    for url, desc in endpoints:
        status = test_endpoint(url, desc)
        results.append((desc, status))
    
    # Probar endpoints de API
    print("\n" + "="*60)
    print("PRUEBA DE ENDPOINTS DE API POTENCIALES")
    print("="*60)
    
    for url, desc in api_endpoints:
        status = test_endpoint(url, desc)
        results.append((desc, status))
    
    # Prueba de interacción con mapa
    test_map_interaction()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS:")
    print("="*60)
    
    accessible = 0
    for desc, status in results:
        if status == 200:
            print(f"✅ {desc}: ACCESIBLE (200)")
            accessible += 1
        elif status is None:
            print(f"❌ {desc}: ERROR DE CONEXIÓN")
        else:
            print(f"⚠️  {desc}: Status {status}")
    
    print(f"\n📊 Estadísticas: {accessible}/{len(results)} endpoints accesibles")
    
    print("\n🎯 RECOMENDACIONES PARA INVESTIGACIÓN:")
    print("1. 🔍 Usar Developer Tools en el navegador para ver peticiones de red")
    print("2. 🕵️  Analizar tráfico con Wireshark o Fiddler")
    print("3. 🧩 Buscar endpoints en el código JavaScript de la página")
    print("4. 📡 Monitorizar WebSocket connections si el mapa es en tiempo real")
    print("5. 🔧 Probar parámetros comunes: /api/v1/, /graphql, /ws, /socket.io")
    print("="*60)
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "test_date": datetime.now().isoformat(),
        "results": [{"endpoint": desc, "status": status} for desc, status in results],
        "map_sample": test_map_interaction(),
        "summary": {
            "total_tested": len(results),
            "accessible": accessible,
            "accessibility_rate": (accessible / len(results) * 100) if results else 0
        }
    }
    
    os.makedirs("data/reports", exist_ok=True)
    with open(f"data/reports/api_test_{timestamp}.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: data/reports/api_test_{timestamp}.json")

if __name__ == "__main__":
    main()
