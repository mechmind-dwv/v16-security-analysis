#!/usr/bin/env python3
"""
V16 Impact Simulator v1.0.0
Simula consecuencias de vulnerabilidades en sistema V16
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import argparse
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class AttackType(Enum):
    DATA_EXPOSURE = "data_exposure"
    LOCATION_TRACKING = "location_tracking"
    FALSE_ALARMS = "false_alarms"
    DOS_ATTACK = "dos_attack"
    IDENTITY_THEFT = "identity_theft"

@dataclass
class SimulationConfig:
    duration_days: int = 30
    incidents_per_day: int = 1000
    attack_probability: float = 0.01  # 1% de incidentes son atacados
    city_population: int = 1000000
    urban_density: float = 0.7  # 70% de incidentes en zonas urbanas
    police_response_time: int = 15  # minutos
    attacker_resources: int = 3  # escala 1-10

@dataclass
class Incident:
    id: str
    timestamp: datetime
    location: Tuple[float, float]  # (lat, lon)
    incident_type: str
    severity: str
    urban_area: bool
    anonymized: bool = True
    attacked: bool = False
    attack_type: Optional[AttackType] = None
    consequences: List[str] = None
    
    def __post_init__(self):
        if self.consequences is None:
            self.consequences = []

class V16ImpactSimulator:
    """Simulador de impacto de vulnerabilidades V16"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.incidents = []
        self.stats = defaultdict(int)
        self.consequence_log = []
        
        # Modelos probabilísticos
        self.attack_models = {
            AttackType.DATA_EXPOSURE: {
                'probability': 0.4,
                'consequences': ['privacy_violation', 'data_leak', 'personal_info_exposure']
            },
            AttackType.LOCATION_TRACKING: {
                'probability': 0.3,
                'consequences': ['stalking', 'targeted_theft', 'harassment']
            },
            AttackType.FALSE_ALARMS: {
                'probability': 0.2,
                'consequences': ['police_resource_waste', 'system_distrust', 'delayed_response']
            },
            AttackType.DOS_ATTACK: {
                'probability': 0.08,
                'consequences': ['system_outage', 'delayed_emergency', 'infrastructure_failure']
            },
            AttackType.IDENTITY_THEFT: {
                'probability': 0.02,
                'consequences': ['financial_loss', 'reputation_damage', 'legal_complications']
            }
        }
    
    def generate_incident(self, day: int, sequence: int) -> Incident:
        """Genera un incidente simulado"""
        # Distribución temporal (más incidentes en tarde/noche)
        hour = self._weighted_hour()
        
        timestamp = datetime.now().replace(
            hour=hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ) + timedelta(days=day)
        
        # Generar ubicación (España)
        if random.random() < self.config.urban_density:
            # Zonas urbanas principales
            city_centers = [
                (40.4168, -3.7038),   # Madrid
                (41.3851, 2.1734),    # Barcelona
                (39.4699, -0.3763),   # Valencia
                (37.3891, -5.9845),   # Sevilla
                (43.2630, -2.9350)    # Bilbao
            ]
            center = random.choice(city_centers)
            location = (
                center[0] + random.uniform(-0.1, 0.1),
                center[1] + random.uniform(-0.1, 0.1)
            )
            urban_area = True
        else:
            # Zonas rurales/carreteras
            location = (
                40.0 + random.uniform(-4, 4),
                -3.5 + random.uniform(-3, 3)
            )
            urban_area = False
        
        # Tipo de incidente
        incident_types = [
            'accident', 'breakdown', 'medical_emergency',
            'roadblock', 'hazard', 'assistance_needed'
        ]
        weights = [0.3, 0.25, 0.15, 0.1, 0.1, 0.1]
        incident_type = random.choices(incident_types, weights=weights)[0]
        
        # Severidad
        severity = random.choices(
            ['low', 'medium', 'high', 'critical'],
            weights=[0.4, 0.3, 0.2, 0.1]
        )[0]
        
        incident = Incident(
            id=f"INC_{day:03d}_{sequence:04d}",
            timestamp=timestamp,
            location=location,
            incident_type=incident_type,
            severity=severity,
            urban_area=urban_area
        )
        
        return incident
    
    def _weighted_hour(self) -> int:
        """Genera hora con distribución realista"""
        # Distribución aproximada de incidentes por hora
        hour_weights = [
            0.02, 0.01, 0.01, 0.01,  # 0-3
            0.02, 0.03, 0.05, 0.07,   # 4-7
            0.08, 0.07, 0.06, 0.05,   # 8-11
            0.06, 0.07, 0.08, 0.07,   # 12-15
            0.08, 0.09, 0.10, 0.08,   # 16-19
            0.06, 0.05, 0.03, 0.02    # 20-23
        ]
        
        hours = list(range(24))
        return random.choices(hours, weights=hour_weights)[0]
    
    def simulate_attack(self, incident: Incident) -> Optional[AttackType]:
        """Determina si un incidente es atacado y cómo"""
        if random.random() > self.config.attack_probability:
            return None
        
        # Seleccionar tipo de ataque basado en probabilidades
        attack_types = list(self.attack_models.keys())
        probabilities = [model['probability'] for model in self.attack_models.values()]
        
        selected_attack = random.choices(attack_types, weights=probabilities)[0]
        
        # Ajustar probabilidad según características del incidente
        if incident.urban_area:
            # Más probabilidad de location_tracking en zonas urbanas
            if selected_attack == AttackType.LOCATION_TRACKING:
                if random.random() < 0.7:  # 70% más probable
                    return selected_attack
        
        if incident.severity == 'critical':
            # Ataques DoS más probables en incidentes críticos
            if selected_attack == AttackType.DOS_ATTACK:
                if random.random() < 0.8:
                    return selected_attack
        
        return selected_attack
    
    def calculate_consequences(self, incident: Incident, attack_type: AttackType):
        """Calcula consecuencias del ataque"""
        model = self.attack_models[attack_type]
        consequences = []
        
        # Consecuencias base del modelo
        base_consequences = random.sample(
            model['consequences'],
            k=min(2, len(model['consequences']))
        )
        consequences.extend(base_consequences)
        
        # Consecuencias adicionales basadas en contexto
        if incident.urban_area:
            if attack_type == AttackType.LOCATION_TRACKING:
                if random.random() < 0.3:
                    consequences.append('physical_theft')
        
        if incident.severity in ['high', 'critical']:
            if attack_type == AttackType.DOS_ATTACK:
                consequences.append('emergency_delay')
                if random.random() < 0.2:
                    consequences.append('life_threatening')
        
        # Impacto económico estimado
        economic_impact = self._estimate_economic_impact(attack_type, incident)
        if economic_impact > 0:
            consequences.append(f'economic_loss_{economic_impact}')
        
        incident.consequences = consequences
        incident.attacked = True
        incident.attack_type = attack_type
        
        # Registrar para estadísticas
        self.stats[f'attack_{attack_type.value}'] += 1
        for consequence in consequences:
            self.stats[f'consequence_{consequence}'] += 1
        
        # Log detallado
        self.consequence_log.append({
            'incident_id': incident.id,
            'timestamp': incident.timestamp.isoformat(),
            'attack_type': attack_type.value,
            'consequences': consequences,
            'location': incident.location,
            'severity': incident.severity
        })
    
    def _estimate_economic_impact(self, attack_type: AttackType, incident: Incident) -> int:
        """Estima impacto económico en euros"""
        base_costs = {
            AttackType.DATA_EXPOSURE: 1000,
            AttackType.LOCATION_TRACKING: 5000,
            AttackType.FALSE_ALARMS: 2000,
            AttackType.DOS_ATTACK: 10000,
            AttackType.IDENTITY_THEFT: 15000
        }
        
        base_cost = base_costs.get(attack_type, 1000)
        
        # Multiplicadores
        multipliers = 1.0
        
        if incident.severity == 'critical':
            multipliers *= 3.0
        elif incident.severity == 'high':
            multipliers *= 2.0
        
        if incident.urban_area:
            multipliers *= 1.5
        
        # Variación aleatoria
        multipliers *= random.uniform(0.8, 1.2)
        
        return int(base_cost * multipliers)
    
    def run_simulation(self):
        """Ejecuta la simulación completa"""
        logger.info(f"Iniciando simulación de {self.config.duration_days} días...")
        
        total_incidents = self.config.duration_days * self.config.incidents_per_day
        incident_counter = 0
        
        for day in range(self.config.duration_days):
            logger.info(f"Simulando día {day + 1}/{self.config.duration_days}...")
            
            for seq in range(self.config.incidents_per_day):
                # Generar incidente
                incident = self.generate_incident(day, seq)
                self.incidents.append(incident)
                
                # Simular posible ataque
                attack_type = self.simulate_attack(incident)
                if attack_type:
                    self.calculate_consequences(incident, attack_type)
                    self.stats['total_attacks'] += 1
                
                self.stats['total_incidents'] += 1
                incident_counter += 1
                
                if incident_counter % 1000 == 0:
                    logger.info(f"Procesados {incident_counter}/{total_incidents} incidentes")
        
        logger.info("Simulación completada")
    
    def generate_report(self) -> Dict:
        """Genera reporte completo de la simulación"""
        total_attacks = self.stats.get('total_attacks', 0)
        total_incidents = self.stats.get('total_incidents', 0)
        
        attack_rate = (total_attacks / total_incidents * 100) if total_incidents > 0 else 0
        
        # Calcular coste total estimado
        total_cost = 0
        for entry in self.consequence_log:
            for consequence in entry['consequences']:
                if consequence.startswith('economic_loss_'):
                    try:
                        cost = int(consequence.split('_')[-1])
                        total_cost += cost
                    except (ValueError, IndexError):
                        pass
        
        report = {
            "simulation_metadata": {
                "config": {
                    "duration_days": self.config.duration_days,
                    "incidents_per_day": self.config.incidents_per_day,
                    "attack_probability": self.config.attack_probability,
                    "city_population": self.config.city_population
                },
                "timestamp": datetime.now().isoformat(),
                "total_incidents_simulated": total_incidents
            },
            "attack_statistics": {
                "total_attacks": total_attacks,
                "attack_rate_percentage": round(attack_rate, 2),
                "attacks_by_type": {
                    atk_type.value: self.stats.get(f'attack_{atk_type.value}', 0)
                    for atk_type in AttackType
                }
            },
            "consequence_analysis": {
                "most_common_consequences": sorted(
                    [(k.replace('consequence_', ''), v) 
                     for k, v in self.stats.items() if k.startswith('consequence_')],
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "economic_impact_estimated": {
                    "total_euros": total_cost,
                    "per_capita": total_cost / self.config.city_population if self.config.city_population > 0 else 0,
                    "daily_average": total_cost / self.config.duration_days if self.config.duration_days > 0 else 0
                }
            },
            "risk_assessment": {
                "urban_vs_rural": {
                    "urban_attacks": sum(1 for i in self.incidents if i.urban_area and i.attacked),
                    "rural_attacks": sum(1 for i in self.incidents if not i.urban_area and i.attacked)
                },
                "severity_distribution": {
                    severity: sum(1 for i in self.incidents if i.severity == severity and i.attacked)
                    for severity in ['low', 'medium', 'high', 'critical']
                }
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en resultados de simulación"""
        recommendations = []
        
        total_attacks = self.stats.get('total_attacks', 0)
        
        if total_attacks > 0:
            recommendations.append(
                "🚨 IMPLEMENTAR ANONIMIZACIÓN DE DATOS: "
                "Ocultar coordenadas exactas y usar áreas aproximadas (radio 500m)"
            )
            
            if self.stats.get('attack_location_tracking', 0) > 0:
                recommendations.append(
                    "📍 CONTROL DE ACCESO A GEOLOCALIZACIÓN: "
                    "Solo personal autorizado debe ver ubicaciones en tiempo real"
                )
            
            if self.stats.get('attack_dos_attack', 0) > 0:
                recommendations.append(
                    "🛡️ FORTALECER INFRAESTRUCTURA: "
                    "Implementar rate limiting y sistemas anti-DDoS"
                )
            
            recommendations.append(
                "🔐 ENCRIPTACIÓN END-TO-END: "
                "Cifrar todas las comunicaciones baliza-servidor"
            )
            
            recommendations.append(
                "📊 AUDITORÍAS REGULARES: "
                "Revisiones de seguridad trimestrales por terceros independientes"
            )
        
        return recommendations
    
    def visualize_results(self, report: Dict, output_prefix: str = "simulation"):
        """Genera visualizaciones de los resultados"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 1. Distribución de tipos de ataque
            plt.figure(figsize=(10, 6))
            attack_data = report['attack_statistics']['attacks_by_type']
            
            attacks = list(attack_data.keys())
            counts = list(attack_data.values())
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(attacks)))
            
            plt.bar(attacks, counts, color=colors)
            plt.title('Distribución de Tipos de Ataque Simulados')
            plt.xlabel('Tipo de Ataque')
            plt.ylabel('Número de Incidentes')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f'{output_prefix}_attack_distribution.png', dpi=150)
            plt.close()
            
            # 2. Impacto económico acumulado
            plt.figure(figsize=(10, 6))
            
            # Simular acumulación diaria
            days = list(range(self.config.duration_days))
            daily_costs = []
            
            for day in days:
                day_cost = 0
                for entry in self.consequence_log:
                    entry_day = datetime.fromisoformat(entry['timestamp']).date()
                    sim_day = (datetime.now() + timedelta(days=day)).date()
                    
                    if entry_day == sim_day:
                        for consequence in entry['consequences']:
                            if consequence.startswith('economic_loss_'):
                                try:
                                    cost = int(consequence.split('_')[-1])
                                    day_cost += cost
                                except (ValueError, IndexError):
                                    pass
                
                daily_costs.append(day_cost)
            
            cumulative = np.cumsum(daily_costs)
            
            plt.plot(days, cumulative, 'b-', linewidth=2)
            plt.fill_between(days, cumulative, alpha=0.3)
            plt.title('Impacto Económico Acumulado de Vulnerabilidades V16')
            plt.xlabel('Días de Simulación')
            plt.ylabel('Coste Acumulado (€)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f'{output_prefix}_economic_impact.png', dpi=150)
            plt.close()
            
            # 3. Mapa de calor de incidentes atacados
            plt.figure(figsize=(12, 8))
            
            attacked_lats = []
            attacked_lons = []
            
            for incident in self.incidents:
                if incident.attacked:
                    attacked_lats.append(incident.location[0])
                    attacked_lons.append(incident.location[1])
            
            if attacked_lats and attacked_lons:
                plt.hexbin(attacked_lons, attacked_lats, gridsize=30, cmap='Reds', alpha=0.7)
                plt.colorbar(label='Número de Incidentes Atacados')
                plt.title('Mapa de Calor: Incidentes V16 Atacados por Ubicación')
                plt.xlabel('Longitud')
                plt.ylabel('Latitud')
                
                # Añadir puntos de ciudades principales
                cities = {
                    'Madrid': (40.4168, -3.7038),
                    'Barcelona': (41.3851, 2.1734),
                    'Valencia': (39.4699, -0.3763),
                    'Sevilla': (37.3891, -5.9845)
                }
                
                for city, (lat, lon) in cities.items():
                    plt.plot(lon, lat, 'ko', markersize=8)
                    plt.annotate(city, (lon, lat), xytext=(5, 5), 
                                textcoords='offset points', fontweight='bold')
                
                plt.tight_layout()
                plt.savefig(f'{output_prefix}_attack_heatmap.png', dpi=150)
                plt.close()
            
            logger.info(f"Visualizaciones guardadas con prefijo: {output_prefix}_*.png")
            
        except ImportError:
            logger.warning("Matplotlib no disponible. Saltando visualizaciones.")
        except Exception as e:
            logger.error(f"Error generando visualizaciones: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Simulador de impacto de vulnerabilidades V16')
    parser.add_argument('--days', type=int, default=30, help='Días a simular')
    parser.add_argument('--incidents-per-day', type=int, default=1000, help='Incidentes diarios')
    parser.add_argument('--attack-prob', type=float, default=0.01, help='Probabilidad de ataque')
    parser.add_argument('--population', type=int, default=1000000, help='Población de la ciudad')
    parser.add_argument('--output', default='simulation_report.json', help='Archivo de salida')
    parser.add_argument('--visualize', action='store_true', help='Generar visualizaciones')
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Crear configuración
    config = SimulationConfig(
        duration_days=args.days,
        incidents_per_day=args.incidents_per_day,
        attack_probability=args.attack_prob,
        city_population=args.population
    )
    
    logger.info("="*60)
    logger.info("SIMULADOR DE IMPACTO - VULNERABILIDADES V16")
    logger.info("="*60)
    logger.info(f"Configuración: {args.days} días, {args.incidents_per_day} incidentes/día")
    logger.info(f"Probabilidad de ataque: {args.attack_prob*100}%")
    logger.info(f"Población simulada: {args.population:,}")
    logger.info("="*60)
    
    # Ejecutar simulación
    simulator = V16ImpactSimulator(config)
    simulator.run_simulation()
    
    # Generar reporte
    report = simulator.generate_report()
    
    # Guardar reporte
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Reporte guardado en {args.output}")
    
    # Mostrar resumen ejecutivo
    print("\n" + "="*60)
    print("RESUMEN EJECUTIVO DE SIMULACIÓN")
    print("="*60)
    print(f"Incidentes totales simulados: {report['simulation_metadata']['total_incidents_simulated']:,}")
    print(f"Ataques simulados: {report['attack_statistics']['total_attacks']:,}")
    print(f"Tasa de ataque: {report['attack_statistics']['attack_rate_percentage']}%")
    print(f"Impacto económico estimado: €{report['consequence_analysis']['economic_impact_estimated']['total_euros']:,}")
    print(f"Coste per cápita: €{report['consequence_analysis']['economic_impact_estimated']['per_capita']:.2f}")
    print("\nRECOMENDACIONES PRINCIPALES:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    print("="*60)
    
    # Generar visualizaciones si se solicita
    if args.visualize:
        simulator.visualize_results(report, output_prefix=args.output.replace('.json', ''))

if __name__ == "__main__":
    main()
