"""
Validador de datos para entradas del sistema
"""
import json
import yaml
from typing import Dict, Any, List
from datetime import datetime
import re

class DataValidator:
    """Valida y sanitiza datos de entrada"""
    
    @staticmethod
    def validate_json(data: str) -> Dict:
        """Valida y parsea JSON"""
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")
    
    @staticmethod
    def validate_yaml(data: str) -> Dict:
        """Valida y parsea YAML"""
        try:
            return yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML inválido: {e}")
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Valida coordenadas GPS"""
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    
    @staticmethod
    def validate_timestamp(timestamp: str) -> bool:
        """Valida formato de timestamp ISO"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 500) -> str:
        """Sanitiza strings para prevenir inyecciones"""
        if not input_str:
            return ""
        
        # Limitar longitud
        sanitized = input_str[:max_length]
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[<>"\'&;]', '', sanitized)
        
        # Normalizar espacios
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    @staticmethod
    def validate_imei(imei: str) -> bool:
        """Valida formato de IMEI (simplificado)"""
        if not imei:
            return False
        
        # Formato básico: 15 dígitos
        pattern = r'^\d{15}$'
        return bool(re.match(pattern, imei))
    
    @staticmethod
    def validate_incident_data(data: Dict) -> List[str]:
        """Valida estructura de datos de incidente"""
        errors = []
        
        required_fields = ['id', 'timestamp', 'coordinates', 'incident_type']
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Campo requerido faltante: {field}")
        
        if 'coordinates' in data:
            coords = data['coordinates']
            if isinstance(coords, dict):
                if not all(k in coords for k in ['lat', 'lon']):
                    errors.append("Coordenadas deben tener lat y lon")
                else:
                    try:
                        lat = float(coords['lat'])
                        lon = float(coords['lon'])
                        if not DataValidator.validate_coordinates(lat, lon):
                            errors.append("Coordenadas fuera de rango válido")
                    except (ValueError, TypeError):
                        errors.append("Coordenadas deben ser números")
        
        if 'timestamp' in data:
            if not DataValidator.validate_timestamp(data['timestamp']):
                errors.append("Timestamp en formato inválido")
        
        # Validar tipos de incidente permitidos
        allowed_types = [
            'accident', 'breakdown', 'medical', 
            'hazard', 'roadblock', 'other'
        ]
        
        if 'incident_type' in data:
            if data['incident_type'] not in allowed_types:
                errors.append(f"Tipo de incidente inválido. Permitidos: {allowed_types}")
        
        return errors
