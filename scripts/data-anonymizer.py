#!/usr/bin/env python3
"""
V16 Data Anonymizer v1.0.0
Sistema de anonimización para investigación ética
"""

import json
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import argparse

logger = logging.getLogger(__name__)

class AnonymizationLevel(Enum):
    LOW = "low"       # Solo nombres/directos
    MEDIUM = "medium" # Coordenadas aproximadas
    HIGH = "high"     # Datos agregados
    MAX = "max"       # Solo estadísticas

@dataclass
class AnonymizationConfig:
    level: AnonymizationLevel
    gps_precision: int = 2
    time_variance: int = 15  # minutos
    salt: Optional[str] = None
    
    def __post_init__(self):
        if self.salt is None:
            self.salt = hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()[:16]

class V16DataAnonymizer:
    """Sistema de anonimización para datos V16"""
    
    def __init__(self, config: AnonymizationConfig):
        self.config = config
        self.stats = {
            "records_processed": 0,
            "fields_anonymized": 0,
            "start_time": datetime.now()
        }
    
    def anonymize_coordinates(self, lat: float, lon: float) -> tuple:
        """Anonimiza coordenadas GPS con variación controlada"""
        if self.config.level == AnonymizationLevel.MAX:
            return None, None
        
        # Reducir precisión
        precision_factor = 10 ** self.config.gps_precision
        lat = round(lat, self.config.gps_precision)
        lon = round(lon, self.config.gps_precision)
        
        # Agregar pequeña variación aleatoria
        if self.config.level in [AnonymizationLevel.MEDIUM, AnonymizationLevel.HIGH]:
            variation = random.uniform(-0.01, 0.01)
            lat += variation
            lon += variation
        
        return lat, lon
    
    def anonymize_timestamp(self, timestamp: str) -> str:
        """Anonimiza timestamp agregando variación temporal"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if self.config.level == AnonymizationLevel.MAX:
                # Solo mantener hora del día
                return dt.strftime("%H:%M")
            
            # Agregar variación
            variance = random.randint(-self.config.time_variance, self.config.time_variance)
            dt = dt + timedelta(minutes=variance)
            
            if self.config.level == AnonymizationLevel.HIGH:
                # Redondear a intervalo de 15 minutos
                minutes = (dt.minute // 15) * 15
                dt = dt.replace(minute=minutes, second=0, microsecond=0)
            
            return dt.isoformat()
            
        except (ValueError, TypeError):
            return timestamp
    
    def hash_identifier(self, identifier: str, prefix: str = "ID") -> str:
        """Genera hash irreversible de identificadores"""
        if not identifier:
            return f"{prefix}_NULL"
        
        salted = f"{self.config.salt}:{identifier}"
        hash_digest = hashlib.sha256(salted.encode()).hexdigest()
        
        # Formato: prefijo + primeros 12 chars del hash
        return f"{prefix}_{hash_digest[:12]}"
    
    def anonymize_incident(self, incident: Dict) -> Dict:
        """Anonimiza un incidente completo"""
        anonymized = incident.copy()
        self.stats["records_processed"] += 1
        
        # Lista de campos a procesar
        fields_to_process = [
            ('coordinates', self._anonymize_coordinates_field),
            ('timestamp', self.anonymize_timestamp),
            ('imei', lambda x: self.hash_identifier(x, 'IMEI')),
            ('imsi', lambda x: self.hash_identifier(x, 'IMSI')),
            ('device_id', lambda x: self.hash_identifier(x, 'DEV')),
            ('vehicle_plate', lambda x: self.hash_identifier(x, 'PLATE')),
            ('phone', lambda x: self.hash_identifier(x, 'PHONE')),
            ('personal_data', self._anonymize_personal_data)
        ]
        
        for field_name, processor in fields_to_process:
            if field_name in anonymized and anonymized[field_name]:
                try:
                    original = anonymized[field_name]
                    anonymized[field_name] = processor(original)
                    self.stats["fields_anonymized"] += 1
                except Exception as e:
                    logger.warning(f"Error anonimizando campo {field_name}: {e}")
        
        # Para nivel MAX, solo mantener datos agregados
        if self.config.level == AnonymizationLevel.MAX:
            anonymized = {
                'incident_type': anonymized.get('incident_type'),
                'severity': anonymized.get('severity'),
                'anonymized_id': self.hash_identifier(
                    str(incident.get('id', 'unknown')),
                    'INC'
                )
            }
        
        return anonymized
    
    def _anonymize_coordinates_field(self, coords: Any) -> Optional[Dict]:
        """Maneja diferentes formatos de coordenadas"""
        if isinstance(coords, dict):
            if 'lat' in coords and 'lon' in coords:
                lat, lon = self.anonymize_coordinates(
                    coords['lat'],
                    coords['lon']
                )
                if lat is not None and lon is not None:
                    return {'lat': lat, 'lon': lon}
        elif isinstance(coords, list) and len(coords) >= 2:
            lat, lon = self.anonymize_coordinates(coords[0], coords[1])
            if lat is not None and lon is not None:
                return [lat, lon]
        
        return coords
    
    def _anonymize_personal_data(self, data: Any) -> str:
        """Anonimiza cualquier dato personal"""
        if isinstance(data, dict):
            # Para objetos complejos, hash el contenido serializado
            serialized = json.dumps(data, sort_keys=True)
            return self.hash_identifier(serialized, 'PERSONAL')
        else:
            return self.hash_identifier(str(data), 'PERSONAL')
    
    def anonymize_dataset(self, dataset: List[Dict]) -> List[Dict]:
        """Anonimiza un conjunto completo de datos"""
        logger.info(f"Anonimizando {len(dataset)} registros...")
        
        anonymized_data = []
        for i, record in enumerate(dataset):
            try:
                anonymized = self.anonimyze_incident(record)
                anonymized_data.append(anonymized)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Procesados {i + 1} registros...")
                    
            except Exception as e:
                logger.error(f"Error procesando registro {i}: {e}")
                continue
        
        logger.info(f"Anonimización completada. Procesados: {len(anonymized_data)} registros")
        return anonymized_data
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del proceso"""
        self.stats["processing_time"] = str(datetime.now() - self.stats["start_time"])
        return self.stats

def load_data(input_file: str) -> List[Dict]:
    """Carga datos desde archivo"""
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            # Si es un objeto con array de incidents
            if 'incidents' in data:
                return data['incidents']
            else:
                return [data]
        elif isinstance(data, list):
            return data
        else:
            logger.error(f"Formato de datos no reconocido en {input_file}")
            return []
            
    except Exception as e:
        logger.error(f"Error cargando {input_file}: {e}")
        return []

def save_data(data: List[Dict], output_file: str):
    """Guarda datos anonimizados"""
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Datos guardados en {output_file}")
    except Exception as e:
        logger.error(f"Error guardando datos: {e}")

def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description='Anonimizador de datos V16')
    parser.add_argument('input', help='Archivo de entrada (JSON)')
    parser.add_argument('output', help='Archivo de salida (JSON)')
    parser.add_argument('--level', choices=['low', 'medium', 'high', 'max'],
                       default='medium', help='Nivel de anonimización')
    parser.add_argument('--gps-precision', type=int, default=2,
                       help='Precisión decimal para coordenadas')
    parser.add_argument('--salt', help='Salt para hashing (opcional)')
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Crear configuración
    config = AnonymizationConfig(
        level=AnonymizationLevel(args.level),
        gps_precision=args.gps_precision,
        salt=args.salt
    )
    
    # Cargar datos
    logger.info(f"Cargando datos desde {args.input}...")
    original_data = load_data(args.input)
    
    if not original_data:
        logger.error("No se pudieron cargar datos. Saliendo.")
        return
    
    logger.info(f"{len(original_data)} registros cargados")
    
    # Crear anonimizador
    anonymizer = V16DataAnonymizer(config)
    
    # Anonimizar datos
    anonymized_data = anonymizer.anonymize_dataset(original_data)
    
    # Guardar resultados
    save_data(anonymized_data, args.output)
    
    # Mostrar estadísticas
    stats = anonymizer.get_stats()
    print("\n" + "="*50)
    print("ESTADÍSTICAS DE ANONIMIZACIÓN")
    print("="*50)
    print(f"Registros procesados: {stats['records_processed']}")
    print(f"Campos anonimizados: {stats['fields_anonymized']}")
    print(f"Tiempo de procesamiento: {stats['processing_time']}")
    print(f"Nivel de anonimización: {config.level.value}")
    print("="*50)

if __name__ == "__main__":
    main()
