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
ARCHIVO_EXCEL = os.getenv('ARCHIVO_EXCEL', 'resultado_vencimientos.xlsx')
REPORTE_FALLIDOS_EXCEL = os.getenv('REPORTE_FALLIDOS_EXCEL', 'reporte_fallidos.xlsx')
LOG_FILE = os.getenv('LOG_FILE', 'vtv_notificaciones.log')
CHROME_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile")

# --- Parámetros de Notificación ---
INTERVALO_MENSAJES = int(os.getenv('INTERVALO_MENSAJES', '5'))
DIAS_ANTICIPACION = int(os.getenv('DIAS_ANTICIPACION', '15'))

# --- Plantillas de Mensajes ---
# Mensaje para VTV próxima a vencer
MENSAJE_TEMPLATE = os.getenv(
    'MENSAJE_TEMPLATE',
    "Hola !Somos de de la Verificación Técnica Vehicular Alto Verde. Te recordamos que la VTV de tu vehiculo con patente {patente} "
    "Por Disposición de la nueva ley vigente (reg. de la Subsecretaria de Seguridad y Justicia) se fijo un recargo trimestral del 35% para aquellos usuarios que circulen con su VTV vencidas"
    "vence el {fecha_vencimiento}. Te sugerimos renovarla pronto para evitar inconvenientes. "
    "Saludos del equipo de Alto Verde!"
)

# Mensaje para VTV ya vencida
MENSAJE_VENCIDO_TEMPLATE = os.getenv(
    'MENSAJE_VENCIDO_TEMPLATE',
    "Hola! Somos de la Verificación Técnica Vehicular Alto Verde. Te informamos que la VTV de tu vehiculo {nombre} con  patente {patente} "
    "ESTÁ VENCIDA desde el {fecha_vencimiento} (hace {dias_vencidos} días). "
    "Por Disposición de la nueva ley vigente (reg. de la Subsecretaria de Seguridad y Justicia) se fijo un recargo trimestral del 35% para aquellos usuarios que circulen con su VTV vencidas"
    "Es urgente que la renueves para evitar inconvenientes."
    "Saludos del equipo de Alto Verde!"
)

# --- Configuración de Selenium ---
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)