#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Configuración
=======================

Centraliza la carga de variables de entorno y constantes del proyecto para
un fácil acceso y modificación.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Archivos y Rutas ---
ARCHIVO_EXCEL = os.getenv('ARCHIVO_EXCEL', 'resultado_vencimientos_telefonos_corregidos_20250704_234031.xlsx')
REPORTE_FALLIDOS_EXCEL = os.getenv('REPORTE_FALLIDOS_EXCEL', 'reporte_fallidos.xlsx')
LOG_FILE = os.getenv('LOG_FILE', 'vtv_notificaciones.log')
CHROME_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")

# --- Parámetros de Notificación ---
INTERVALO_MENSAJES = int(os.getenv('INTERVALO_MENSAJES', '5'))
DIAS_ANTICIPACION = int(os.getenv('DIAS_ANTICIPACION', '15'))

# --- Plantillas de Mensajes ---
# Plantilla por defecto para VTV próxima a vencer
MENSAJE_TEMPLATE_DEFAULT = """Hola! Somos de la Verificación Técnica Vehicular Alto Verde. Te recordamos que la VTV de tu vehículo {marca} {modelo} con patente {patente} que fue revisado el {fecha_revision} vence el {fecha_vencimiento}. Por Disposición de la nueva ley vigente (reg. de la Subsecretaria de Seguridad y Justicia) se fijó un recargo trimestral del 35% para aquellos usuarios que circulen con su VTV vencida. Te sugerimos renovarla pronto para evitar inconvenientes. Saludos del equipo de Alto Verde!"""

# Plantilla por defecto para VTV ya vencida
MENSAJE_VENCIDO_TEMPLATE_DEFAULT = """Hola! Somos de la Verificación Técnica Vehicular Alto Verde. Te informamos que la VTV de tu vehículo {marca} {modelo} con patente {patente} que fue revisado el {fecha_revision} ESTÁ VENCIDA desde el {fecha_vencimiento} (hace {dias_vencidos} días). Por Disposición de la nueva ley vigente (reg. de la Subsecretaria de Seguridad y Justicia) se fijó un recargo trimestral del 35% para aquellos usuarios que circulen con su VTV vencida. Es urgente que la renueves para evitar inconvenientes. Saludos del equipo de Alto Verde!"""

# Cargar desde variables de entorno o usar valores por defecto
MENSAJE_TEMPLATE = os.getenv('MENSAJE_TEMPLATE', MENSAJE_TEMPLATE_DEFAULT)
MENSAJE_VENCIDO_TEMPLATE = os.getenv('MENSAJE_VENCIDO_TEMPLATE', MENSAJE_VENCIDO_TEMPLATE_DEFAULT)

# --- Configuración de Selenium ---
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# --- Función para validar configuración ---
def validar_configuracion():
    """
    Valida que las plantillas de mensajes estén correctamente configuradas.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar que las plantillas contengan los campos requeridos
    campos_requeridos = ['patente', 'marca', 'modelo', 'fecha_revision', 'fecha_vencimiento']
    campos_vencido = campos_requeridos + ['dias_vencidos']
    
    # Validar MENSAJE_TEMPLATE
    for campo in campos_requeridos:
        if f'{{{campo}}}' not in MENSAJE_TEMPLATE:
            logger.warning(f"Campo '{campo}' no encontrado en MENSAJE_TEMPLATE")
    
    # Validar MENSAJE_VENCIDO_TEMPLATE
    for campo in campos_vencido:
        if f'{{{campo}}}' not in MENSAJE_VENCIDO_TEMPLATE:
            logger.warning(f"Campo '{campo}' no encontrado en MENSAJE_VENCIDO_TEMPLATE")
    
    logger.info("Configuración de mensajes validada.")

# --- Función para mostrar configuración actual ---
def mostrar_configuracion():
    """
    Muestra la configuración actual de mensajes.
    """
    print("="*60)
    print("CONFIGURACIÓN ACTUAL DE MENSAJES")
    print("="*60)
    
    print("📧 MENSAJE PARA VTV PRÓXIMA A VENCER:")
    print(f"'{MENSAJE_TEMPLATE}'")
    print()
    
    print("📧 MENSAJE PARA VTV VENCIDA:")
    print(f"'{MENSAJE_VENCIDO_TEMPLATE}'")
    print()
    
    print("⚙️  OTROS PARÁMETROS:")
    print(f"- Intervalo entre mensajes: {INTERVALO_MENSAJES} segundos")
    print(f"- Días de anticipación: {DIAS_ANTICIPACION}")
    print(f"- Archivo Excel: {ARCHIVO_EXCEL}")
    print(f"- Reporte de fallidos: {REPORTE_FALLIDOS_EXCEL}")
    print("="*60)

# Ejecutar validación al importar el módulo
if __name__ == "__main__":
    mostrar_configuracion()
else:
    validar_configuracion()