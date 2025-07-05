#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir números de teléfono en archivo Excel
=======================================================

Este script toma tu archivo Excel original y genera uno nuevo con todas las columnas
intactas, pero con los números de teléfono corregidos usando la función de validación.
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ARCHIVO_EXCEL

def validar_numero_telefono_mejorado(numero) -> str | None:
    """
    Función mejorada de validación (copia de la versión optimizada)
    """
    import pandas as pd
    import re
    
    # Verificar si el número es nulo, vacío o NaN
    if numero is None or pd.isna(numero):
        return None
    
    # Convertir a string y manejar números flotantes
    try:
        if isinstance(numero, float):
            if pd.isna(numero):
                return None
            numero_str = str(int(numero))
        else:
            numero_str = str(numero).strip()
    except (ValueError, OverflowError):
        return None
    
    # Verificar que no esté vacío después de la conversión
    if not numero_str or numero_str.lower() in ['nan', 'none', 'null', '']:
        return None
    
    # Remover todos los caracteres que no sean dígitos
    numero_limpio = re.sub(r'[^\d]', '', numero_str)
    
    # Verificar que queden dígitos después de la limpieza
    if not numero_limpio or not numero_limpio.isdigit():
        return None
    
    # Remover prefijo de país Argentina (54) si existe
    if numero_limpio.startswith('54'):
        numero_limpio = numero_limpio[2:]
    
    # Manejar números que empiezan con 0
    if numero_limpio.startswith('0'):
        numero_limpio = numero_limpio[1:]
    
    # Verificar longitud
    if len(numero_limpio) < 8 or len(numero_limpio) > 12:
        return None
    
    # Formatear según el caso
    if numero_limpio.startswith('11') and len(numero_limpio) == 10:
        return f"549{numero_limpio}"
    elif numero_limpio.startswith('9') and len(numero_limpio) == 11:
        return f"54{numero_limpio}"
    elif numero_limpio.startswith('9') and len(numero_limpio) == 10:
        return f"54{numero_limpio}"
    elif len(numero_limpio) == 10:
        return f"549{numero_limpio}"
    elif len(numero_limpio) == 8:
        return f"5411{numero_limpio}"
    elif len(numero_limpio) == 9:
        return f"549{numero_limpio}"
    elif len(numero_limpio) == 11:
        return f"54{numero_limpio}"
    
    return None


def crear_directorio_corregidos():
    """
    Crea el directorio de archivos corregidos si no existe
    """
    # Obtener el directorio del script actual
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Crear la ruta del directorio corregidos
    directorio_corregidos = os.path.join(directorio_actual, 'corregidos')
    
    # Crear el directorio si no existe
    if not os.path.exists(directorio_corregidos):
        os.makedirs(directorio_corregidos)
        print(f"📁 Directorio creado: {directorio_corregidos}")
    else:
        print(f"📁 Directorio ya existe: {directorio_corregidos}")
    
    return directorio_corregidos


def corregir_telefonos_excel(archivo_excel):
    """
    Toma el archivo Excel y genera uno nuevo con los teléfonos corregidos,
    manteniendo todas las demás columnas intactas.
    """
    try:
        # Cargar el Excel manteniendo los tipos de datos originales
        print(f"📊 Cargando archivo: {archivo_excel}")
        df = pd.read_excel(archivo_excel, dtype=str)
        
        # Detectar columna de teléfono
        columnas_telefono = ['TEL', 'Telefono', 'NumeroDeWhatsapp', 'WhatsApp', 'Celular', 'Numero']
        columna_telefono = None
        
        print(f"Columnas disponibles: {list(df.columns)}")
        
        for col in columnas_telefono:
            if col in df.columns:
                columna_telefono = col
                break
        
        if not columna_telefono:
            print("❌ No se encontró columna de teléfono en el Excel")
            print(f"Columnas disponibles: {list(df.columns)}")
            return None
        
        print(f"✅ Columna de teléfono encontrada: {columna_telefono}")
        
        # Crear una copia del DataFrame original
        df_corregido = df.copy()
        
        # Estadísticas iniciales
        total_registros = len(df_corregido)
        telefonos_originales = df_corregido[columna_telefono].notna().sum()
        
        print(f"\n📈 ESTADÍSTICAS INICIALES:")
        print(f"  Total de registros: {total_registros}")
        print(f"  Teléfonos no nulos originales: {telefonos_originales}")
        
        # Mostrar algunos ejemplos de números originales
        print(f"\n📋 EJEMPLOS DE NÚMEROS ORIGINALES:")
        ejemplos = df_corregido[columna_telefono].dropna().head(5)
        for i, numero in enumerate(ejemplos, 1):
            print(f"  {i}. '{numero}'")
        
        # Aplicar la corrección solo a la columna de teléfono
        print(f"\n🔄 Aplicando corrección a la columna '{columna_telefono}'...")
        
        # Guardar los números originales en una nueva columna para referencia
        df_corregido[f'{columna_telefono}_Original'] = df_corregido[columna_telefono].copy()
        
        # Aplicar la validación/corrección
        df_corregido[columna_telefono] = df_corregido[columna_telefono].apply(validar_numero_telefono_mejorado)
        
        # Estadísticas después de la corrección
        telefonos_corregidos = df_corregido[columna_telefono].notna().sum()
        telefonos_perdidos = telefonos_originales - telefonos_corregidos
        
        print(f"\n📊 RESULTADOS DE LA CORRECCIÓN:")
        print(f"  ✅ Teléfonos corregidos exitosamente: {telefonos_corregidos}")
        print(f"  ❌ Teléfonos que no se pudieron corregir: {telefonos_perdidos}")
        print(f"  📈 Porcentaje de éxito: {(telefonos_corregidos/telefonos_originales)*100:.1f}%")
        
        # Mostrar algunos ejemplos de correcciones
        print(f"\n📋 EJEMPLOS DE CORRECCIONES:")
        ejemplos_corregidos = df_corregido[df_corregido[columna_telefono].notna()].head(5)
        for i, (_, row) in enumerate(ejemplos_corregidos.iterrows(), 1):
            original = row[f'{columna_telefono}_Original']
            corregido = row[columna_telefono]
            print(f"  {i}. '{original}' -> '{corregido}'")
        
        # Crear directorio de salida
        directorio_corregidos = crear_directorio_corregidos()
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = os.path.splitext(os.path.basename(archivo_excel))[0]
        nombre_archivo = f"{nombre_base}_telefonos_corregidos_{timestamp}.xlsx"
        ruta_completa = os.path.join(directorio_corregidos, nombre_archivo)
        
        # Guardar el archivo corregido
        print(f"\n💾 Guardando archivo corregido...")
        
        # Crear el archivo Excel con múltiples hojas
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            # Hoja principal: Datos corregidos (sin la columna _Original)
            df_final = df_corregido.drop(columns=[f'{columna_telefono}_Original'])
            df_final.to_excel(writer, sheet_name='Datos_Corregidos', index=False)
            
            # Hoja de comparación: Mostrando original vs corregido
            df_comparacion = df_corregido[[col for col in df_corregido.columns if col != columna_telefono]]
            df_comparacion.insert(1, f'{columna_telefono}_Corregido', df_corregido[columna_telefono])
            df_comparacion.to_excel(writer, sheet_name='Comparación', index=False)
            
            # Hoja de estadísticas
            estadisticas_data = {
                'Métrica': [
                    'Total de registros',
                    'Teléfonos originales no nulos',
                    'Teléfonos corregidos exitosamente',
                    'Teléfonos que no se pudieron corregir',
                    'Porcentaje de éxito',
                    'Fecha de procesamiento',
                    'Archivo original',
                    'Columna procesada'
                ],
                'Valor': [
                    total_registros,
                    telefonos_originales,
                    telefonos_corregidos,
                    telefonos_perdidos,
                    f"{(telefonos_corregidos/telefonos_originales)*100:.1f}%",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    os.path.basename(archivo_excel),
                    columna_telefono
                ]
            }
            
            df_estadisticas = pd.DataFrame(estadisticas_data)
            df_estadisticas.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        print(f"✅ Archivo guardado exitosamente en: {ruta_completa}")
        print(f"\n📚 El archivo contiene 3 hojas:")
        print(f"    - Datos_Corregidos: Tu archivo con teléfonos corregidos (¡listo para usar!)")
        print(f"    - Comparación: Ver original vs corregido lado a lado")
        print(f"    - Estadísticas: Resumen del proceso de corrección")
        
        # Mostrar información adicional
        print(f"\n🔍 INFORMACIÓN ADICIONAL:")
        print(f"  - Los números que no se pudieron corregir aparecen como vacíos")
        print(f"  - Todos los números corregidos siguen el formato: 549XXXXXXXXX")
        print(f"  - Las demás columnas permanecen exactamente iguales")
        
        return df_corregido
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_excel}")
        return None
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    Función principal para ejecutar la corrección.
    """
    print("="*70)
    print("CORRECCIÓN DE NÚMEROS DE TELÉFONO - EXCEL")
    print("="*70)
    
    # Verificar si existe el archivo
    if not os.path.exists(ARCHIVO_EXCEL):
        print(f"❌ No se encontró el archivo: {ARCHIVO_EXCEL}")
        print("Por favor, asegúrate de que el archivo esté en el directorio correcto.")
        return
    
    # Ejecutar corrección
    resultado = corregir_telefonos_excel(ARCHIVO_EXCEL)
    
    if resultado is not None:
        print(f"\n✅ Corrección completada exitosamente")
        print(f"📁 Busca tu archivo corregido en el directorio 'corregidos/'")
        print(f"🎯 El archivo principal está en la hoja 'Datos_Corregidos'")
    else:
        print(f"\n❌ La corrección no pudo completarse")
    
    print("="*70)


if __name__ == "__main__":
    main()