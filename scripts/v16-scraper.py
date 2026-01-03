#!/usr/bin/env python3
"""
Scraper automático del mapa V16 - Extrae datos en tiempo real
"""
import requests
import json
import time
from datetime import datetime

class V16Scraper:
    def __init__(self):
        self.base_url = "https://mapabalizasv16.es"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def find_api_endpoint(self):
        """Busca el endpoint real de la API"""
        # Intentar diferentes patrones de API
        patterns = [
            '/api/v1/incidents',
            '/api/incidents',
            '/data/incidents',
            '/incidents/json',
            '/getMarkers'
        ]
        
        for pattern in patterns:
            url = f"{self.base_url}{pattern}"
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Posible endpoint: {url}")
                    # Intentar parsear como JSON
                    try:
                        data = response.json()
                        print(f"   📊 Datos JSON válidos: {len(data)} elementos")
                        return url, data
                    except:
                        print(f"   ℹ️  Respuesta no JSON: {response.text[:100]}...")
            except:
                continue
        
        return None, None
    
    def monitor_changes(self, interval_seconds=60):
        """Monitorea cambios en tiempo real"""
        print(f"🔍 Iniciando monitorización cada {interval_seconds} segundos...")
        
        last_data = None
        incident_count = 0
        
        while True:
            try:
                endpoint, data = self.find_api_endpoint()
                if data and data != last_data:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{timestamp}] 📡 Datos actualizados")
                    
                    # Guardar snapshot
                    filename = f"data/snapshots/snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    print(f"💾 Guardado: {filename}")
                    incident_count += 1
                    last_data = data
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitorización detenida")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(interval_seconds)

if __name__ == "__main__":
    scraper = V16Scraper()
    scraper.monitor_changes(300)  # 5 minutos
