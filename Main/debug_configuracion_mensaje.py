#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug para verificar la configuración de mensajes
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def debug_configuracion():
    """Debug de la configuración de mensajes"""
    print("="*60)
    print("DEBUG DE CONFIGURACIÓN DE MENSAJES")
    print("="*60)
    
    # Verificar si existe el archivo .env
    env_exists = os.path.exists('.env')
    print(f"¿Existe archivo .env? {env_exists}")
    
    if env_exists:
        print("\nContenido del archivo .env:")
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    print(content)
                else:
                    print("El archivo .env está vacío")
        except Exception as e:
            print(f"Error al leer .env: {e}")
    
    # Verificar variables de entorno
    print("\n" + "="*40)
    print("VARIABLES DE ENTORNO")
    print("="*40)
    
    mensaje_template = os.getenv('MENSAJE_TEMPLATE')
    mensaje_vencido_template = os.getenv('MENSAJE_VENCIDO_TEMPLATE')
    
    print(f"MENSAJE_TEMPLATE existe: {mensaje_template is not None}")
    print(f"MENSAJE_VENCIDO_TEMPLATE existe: {mensaje_vencido_template is not None}")
    
    if mensaje_template:
        print(f"MENSAJE_TEMPLATE (primeros 100 chars): {mensaje_template[:100]}...")
    
    if mensaje_vencido_template:
        print(f"MENSAJE_VENCIDO_TEMPLATE (primeros 100 chars): {mensaje_vencido_template[:100]}...")
    
    # Mostrar las plantillas que se están usando actualmente
    print("\n" + "="*40)
    print("PLANTILLAS ACTUALES EN CONFIG.PY")
    print("="*40)
    
    # Importar desde config para ver qué se está usando
    try:
        from config import MENSAJE_TEMPLATE, MENSAJE_VENCIDO_TEMPLATE
        
        print("MENSAJE_TEMPLATE:")
        print(f"Tipo: {type(MENSAJE_TEMPLATE)}")
        print(f"Contenido: {MENSAJE_TEMPLATE}")
        
        print("\nMENSAJE_VENCIDO_TEMPLATE:")
        print(f"Tipo: {type(MENSAJE_VENCIDO_TEMPLATE)}")
        print(f"Contenido: {MENSAJE_VENCIDO_TEMPLATE}")
        
        # Probar el formateo
        print("\n" + "="*40)
        print("PRUEBA DE FORMATEO")
        print("="*40)
        
        datos_prueba = {
            'patente': 'ABC123',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'fecha_revision': '15/06/2024',
            'fecha_vencimiento': '15/06/2025',
            'esta_vencida': False,
            'dias_vencidos': 0
        }
        
        # Probar mensaje normal
        try:
            mensaje_normal = MENSAJE_TEMPLATE.format(**datos_prueba)
            print("✅ Mensaje normal formateado correctamente:")
            print(mensaje_normal[:200] + "...")
        except Exception as e:
            print(f"❌ Error al formatear mensaje normal: {e}")
        
        # Probar mensaje vencido
        datos_prueba_vencido = datos_prueba.copy()
        datos_prueba_vencido['esta_vencida'] = True
        datos_prueba_vencido['dias_vencidos'] = 5
        
        try:
            mensaje_vencido = MENSAJE_VENCIDO_TEMPLATE.format(**datos_prueba_vencido)
            print("\n✅ Mensaje vencido formateado correctamente:")
            print(mensaje_vencido[:200] + "...")
        except Exception as e:
            print(f"❌ Error al formatear mensaje vencido: {e}")
            
    except Exception as e:
        print(f"❌ Error al importar desde config: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_configuracion()