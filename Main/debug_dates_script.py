#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Debug para Fechas
============================

Usa este script para debuggear problemas con fechas antes de ejecutar el proceso completo.
"""

import pandas as pd
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_handler import DataHandler
from utils import configurar_logging

def main():
    """Función principal para debuggear fechas."""
    
    # Configurar logging
    logger = configurar_logging()
    
    # Nombre del archivo Excel
    archivo_excel = "resultado_vencimientos_telefonos_corregidos_20250704_234031.xlsx"
    
    if not os.path.exists(archivo_excel):
        print(f"❌ No se encontró el archivo: {archivo_excel}")
        print("📍 Asegúrate de que el archivo esté en el mismo directorio que este script.")
        input("Presiona Enter para salir...")
        return
    
    print("="*80)
    print("               SCRIPT DE DEBUG PARA FECHAS")
    print("="*80)
    print(f"📊 Analizando archivo: {archivo_excel}")
    print()
    
    try:
        # Crear instancia del data handler
        data_handler = DataHandler(archivo_excel)
        
        # Cargar y procesar datos
        print("🔄 Cargando y procesando datos...")
        data_handler.cargar_y_procesar_datos()
        
        # Ejecutar debug de fechas
        data_handler.debug_fechas()
        
        # Mostrar información general
        print("\n" + "="*60)
        print("           INFORMACIÓN GENERAL")
        print("="*60)
        
        info = data_handler.obtener_info_columnas()
        print(f"📊 Total de registros: {info['total_registros']}")
        print(f"📋 Columnas detectadas: {list(info['columnas_detectadas'].keys())}")
        
        # Intentar filtrar vencimientos
        print("\n🔍 Probando filtro de vencimientos...")
        vencimientos = data_handler.filtrar_vencimientos_proximos()
        
        if len(vencimientos) > 0:
            print(f"✅ Se encontraron {len(vencimientos)} vencimientos para procesar.")
            
            # Mostrar algunos ejemplos
            print("\n📋 Ejemplos de vencimientos encontrados:")
            for i, (_, row) in enumerate(vencimientos.head(5).iterrows()):
                estado = "VENCIDA" if row['esta_vencida'] else "Por vencer"
                print(f"  {i+1}. {row['_marca']} {row['_modelo']} - {row['_patente']} ({estado})")
        else:
            print("⚠️ No se encontraron vencimientos en el rango de fechas.")
        
        print("\n" + "="*80)
        print("               ANÁLISIS COMPLETO")
        print("="*80)
        
        # Análisis detallado del DataFrame
        df = data_handler.df
        
        print(f"📊 Estadísticas del DataFrame:")
        print(f"  - Filas totales: {len(df)}")
        print(f"  - Columnas totales: {len(df.columns)}")
        
        # Verificar fechas específicamente
        if '_fecha_revision' in df.columns and '_fecha_vencimiento' in df.columns:
            fechas_rev_validas = df['_fecha_revision'].notna().sum()
            fechas_venc_validas = df['_fecha_vencimiento'].notna().sum()
            
            print(f"\n📅 Análisis de fechas:")
            print(f"  - Fechas de revisión válidas: {fechas_rev_validas} ({fechas_rev_validas/len(df)*100:.1f}%)")
            print(f"  - Fechas de vencimiento válidas: {fechas_venc_validas} ({fechas_venc_validas/len(df)*100:.1f}%)")
            
            # Mostrar rango de fechas
            if fechas_venc_validas > 0:
                fecha_min = df['_fecha_vencimiento'].min()
                fecha_max = df['_fecha_vencimiento'].max()
                print(f"  - Rango de vencimientos: {fecha_min.strftime('%d/%m/%Y')} a {fecha_max.strftime('%d/%m/%Y')}")
        
        # Verificar teléfonos
        if 'NumeroValidado' in df.columns:
            telefonos_validos = df['NumeroValidado'].notna().sum()
            print(f"\n📱 Análisis de teléfonos:")
            print(f"  - Teléfonos válidos: {telefonos_validos} ({telefonos_validos/len(df)*100:.1f}%)")
            
            # Mostrar algunos ejemplos de números validados
            ejemplos_telefonos = df['NumeroValidado'].dropna().head(5).tolist()
            print(f"  - Ejemplos: {ejemplos_telefonos}")
        
        print("\n✅ Análisis completado exitosamente.")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        input("\n🔚 Presiona Enter para salir...")

if __name__ == "__main__":
    main()