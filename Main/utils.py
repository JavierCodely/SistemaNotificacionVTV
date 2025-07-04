#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Utilidades
====================

Contiene funciones de soporte reutilizables como la configuración del logging,
la validación de datos y la limpieza de texto.
"""

import logging
import sys
import unicodedata
import re
import pandas as pd
from config import LOG_FILE

def configurar_logging():
    """Configura el sistema de logging para registrar actividades."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def limpiar_texto_unicode(texto: str) -> str:
    """
    Limpia el texto de caracteres que pueden causar problemas con ChromeDriver.

    Args:
        texto (str): Texto a limpiar.

    Returns:
        str: Texto limpio, sin emojis y normalizado.
    """
    if not texto:
        return ""
    
    # Normalizar para descomponer caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    
    # Filtrar caracteres que no están en el Basic Multilingual Plane (BMP)
    texto_limpio = "".join(
        char for char in texto_normalizado if ord(char) <= 0xFFFF
    )
    
    return texto_limpio

def validar_numero_telefono(numero) -> str | None:
    """
    Valida y formatea un número de teléfono argentino.

    Args:
        numero: El número de teléfono (puede ser str, int, float).

    Returns:
        str | None: El número formateado con "+54" o None si es inválido.
    """
    if pd.isna(numero):
        return None
        
    numero_str = str(numero).split('.')[0] # Convertir a str y quitar decimales
    numero_limpio = re.sub(r'[\s\-()+]', '', numero_str)
    
    # Quitar prefijo de país si existe
    if numero_limpio.startswith('54'):
        numero_limpio = numero_limpio[2:]
        
    # Verificar que tenga el formato de 10 dígitos (sin el 9 de móvil)
    # WhatsApp requiere el formato +549... para móviles, pero lo gestiona internamente
    if re.match(r'^(11|\d{2,4})?\d{6,8}$', numero_limpio) and len(numero_limpio) >= 10:
         # Si no incluye el '9' entre el código de país y el de área, WhatsApp puede no encontrarlo.
         # El formato estándar es +54 9 CódArea Número.
         if len(numero_limpio) == 10: # CódArea + Número
            return f"549{numero_limpio}"
         elif len(numero_limpio) == 11 and numero_limpio.startswith('9'): # Ya tiene el 9
            return f"54{numero_limpio}"
         else: # Otros casos
            return f"54{numero_limpio}"

    return None