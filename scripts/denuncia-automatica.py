#!/usr/bin/env python3
"""
Script para preparar denuncia automática de vulnerabilidades V16
"""

import json
from datetime import datetime
import os

def preparar_denuncia_aepd():
    """Prepara denuncia para la Agencia Española de Protección de Datos"""
    
    denuncia = {
        "destinatario": "Agencia Española de Protección de Datos (AEPD)",
        "asunto": "Denuncia por violación del RGPD - Sistema de balizas V16 DGT",
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        
        "datos_denunciante": {
            "nombre": "[NOMBRE]",
            "dni": "[DNI]",
            "email": "[EMAIL]",
            "telefono": "[TELÉFONO]"
        },
        
        "hechos": [
            "El sistema de balizas V16 de la Dirección General de Tráfico expone en tiempo real y sin controles de acceso:",
            "1. Ubicación exacta de conductores en situación de emergencia",
            "2. Información del vehículo y tiempo exacto de la incidencia",
            "3. Datos de municipio, provincia y carretera específica",
            "4. Dirección de viaje y punto kilométrico exacto"
        ],
        
        "violaciones_rgpd": [
            "Artículo 5: Principios relativos al tratamiento - Falta de licitud, lealtad y transparencia",
            "Artículo 25: Protección de datos desde el diseño y por defecto - No se implementaron medidas técnicas adecuadas",
            "Artículo 32: Seguridad del tratamiento - No se garantiza confidencialidad e integridad",
            "Artículo 35: Evaluación de impacto - No se realizó evaluación de impacto en la protección de datos"
        ],
        
        "evidencias_adjuntas": [
            "Informe técnico de vulnerabilidades",
            "Capturas de pantalla del sistema",
            "Análisis de endpoints públicos",
            "Ejemplos de datos expuestos"
        ],
        
        "peticiones": [
            "Que se inicie procedimiento sancionador contra la DGT",
            "Que se ordene el cese inmediato de la exposición de datos",
            "Que se realice auditoría de seguridad del sistema",
            "Que se notifique a los afectados la violación de sus datos"
        ],
        
        "anexos": [
            "Informe técnico completo",
            "Logs de acceso sin autenticación",
            "Análisis de impacto en seguridad física"
        ]
    }
    
    # Guardar denuncia
    os.makedirs("denuncias", exist_ok=True)
    archivo = f"denuncias/denuncia_aepd_v16_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(denuncia, f, indent=2, ensure_ascii=False)
    
    # Versión en texto plano para enviar
    txt_archivo = f"denuncias/denuncia_aepd_v16_{datetime.now().strftime('%Y%m%d')}.txt"
    
    with open(txt_archivo, 'w', encoding='utf-8') as f:
        f.write(f"DENUNCIA - VIOLACIÓN RGPD - SISTEMA V16 DGT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Fecha: {denuncia['fecha']}\n")
        f.write(f"Destinatario: {denuncia['destinatario']}\n\n")
        
        f.write("DATOS DEL DENUNCIANTE:\n")
        for key, value in denuncia['datos_denunciante'].items():
            f.write(f"- {key}: {value}\n")
        
        f.write("\nHECHOS:\n")
        for hecho in denuncia['hechos']:
            f.write(f"• {hecho}\n")
        
        f.write("\nVIOLACIONES DEL RGPD:\n")
        for violacion in denuncia['violaciones_rgpd']:
            f.write(f"• {violacion}\n")
        
        f.write("\nPETICIONES:\n")
        for i, peticion in enumerate(denuncia['peticiones'], 1):
            f.write(f"{i}. {peticion}\n")
    
    print(f"✅ Denuncia preparada:")
    print(f"   JSON: {archivo}")
    print(f"   Texto: {txt_archivo}")
    print(f"\n📧 Enviar a: denuncias@aepd.es")
    print(f"📎 Adjuntar: reports/informe_ejecutivo_v16_*.md")

def preparar_comunicado_prensa():
    """Prepara comunicado de prensa"""
    
    comunicado = f"""PARA DIFUSIÓN INMEDIATA

🚨 ALERTA DE SEGURIDAD: EL SISTEMA DE BALIZAS V16 DE LA DGT EXPONE DATOS DE CONDUCTORES EN PELIGRO

{FECHA}

Investigadores de seguridad han descubierto graves vulnerabilidades en el sistema de balizas V16 de la Dirección General de Tráfico (DGT) que exponen en tiempo real y sin protección la ubicación exacta de conductores en situación de emergencia.

HALLAZGOS PRINCIPALES:
1. 📍 UBICACIÓN EXPUESTA: Cualquier persona puede ver la localización exacta (carretera + punto kilométrico) de conductores que han activado su baliza V16
2. 🔓 SIN AUTENTICACIÓN: Acceso público total sin necesidad de credenciales
3. ⏰ TIEMPO REAL: Los datos se actualizan en tiempo real, mostrando "última señal hace X minutos"
4. 🏙️ DATOS PERSONALES: Municipio, provincia, dirección de viaje y hora exacta son visibles

EJEMPLO CONCRETO:
- Carretera: AP-4, PK 102.8
- Municipio: Puerto Real, Provincia: Cádiz
- Hora de activación: 14:27:04
- Última señal: hace 25 minutos

RIESGOS IDENTIFICADOS:
• Robo vehicular dirigido a vehículos inmovilizados
• Acoso y hostigamiento
• Secuestro oportunista
• Violación masiva del derecho a la privacidad

VIOLACIONES LEGALES:
- Reglamento General de Protección de Datos (RGPD)
- Ley Orgánica de Protección de Datos
- Deber de protección de personas en situación de vulnerabilidad

EXIGIMOS:
1. Cese inmediato de la exposición pública de datos
2. Auditoría de seguridad independiente
3. Explicaciones públicas de la DGT
4. Medidas de protección para los afectados

PARA MÁS INFORMACIÓN:
- Hashtag: #BalizaV16Insegura
- Repositorio técnico: https://github.com/mechmind-dwv/v16-security-analysis
- Contacto para medios: [CONTACTO]

###

ACERCA DE LA INVESTIGACIÓN:
Esta investigación se realizó de forma ética y legal, con el único objetivo de proteger a los ciudadanos. Todos los datos fueron obtenidos de fuentes públicas accesibles sin autenticación.
"""
    
    archivo = f"comunicados/comunicado_prensa_v16_{datetime.now().strftime('%Y%m%d')}.txt"
    os.makedirs("comunicados", exist_ok=True)
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(comunicado.replace("{FECHA}", datetime.now().strftime("%d de enero de 2026")))
    
    print(f"\n📰 Comunicado de prensa preparado: {archivo}")
    print("📤 Enviar a: sociedad@elpais.com, tecnologia@eldiario.es, redaccion@lavanguardia.es")

if __name__ == "__main__":
    print("="*60)
    print("PREPARADOR DE DENUNCIA Y COMUNICACIÓN - VULNERABILIDAD V16")
    print("="*60)
    
    preparar_denuncia_aepd()
    print("\n" + "-"*60)
    preparar_comunicado_prensa()
    
    print("\n" + "="*60)
    print("🎯 ACCIONES RECOMENDADAS:")
    print("="*60)
    print("1. 📝 Completar datos personales en denuncia_aepd_*.json")
    print("2. 📧 Enviar denuncia a: denuncias@aepd.es")
    print("3. 🐦 Publicar en Twitter con: #BalizaV16Insegura #RGPD")
    print("4. 📱 Compartir en grupos de WhatsApp de conductores")
    print("5. 📞 Contactar programas de TV: Salvados, Al Rojo Vivo")
    print("="*60)
