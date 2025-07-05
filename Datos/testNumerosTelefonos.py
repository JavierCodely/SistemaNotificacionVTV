#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la validación de números de teléfono con tu archivo Excel
===========================================================================

Este script te permite probar la nueva función de validación con tus datos reales
y ver exactamente qué números son problemáticos.
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


def crear_directorio_reportes():
    """
    Crea el directorio de reportes si no existe
    """
    # Obtener el directorio del script actual
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Crear la ruta del directorio reportes
    directorio_reportes = os.path.join(directorio_actual, 'reportes')
    
    # Crear el directorio si no existe
    if not os.path.exists(directorio_reportes):
        os.makedirs(directorio_reportes)
        print(f"📁 Directorio creado: {directorio_reportes}")
    else:
        print(f"📁 Directorio ya existe: {directorio_reportes}")
    
    return directorio_reportes


def analizar_telefonos_excel(archivo_excel):
    """
    Analiza los números de teléfono en el archivo Excel y muestra estadísticas detalladas.
    """
    try:
        # Cargar el Excel sin convertir automáticamente las columnas
        print(f"📊 Cargando archivo: {archivo_excel}")
        
        # Leer el Excel manteniendo los números como texto para evitar conversiones automáticas
        df = pd.read_excel(archivo_excel, dtype=str)
        
        # Detectar columna de teléfono
        columnas_telefono = ['TEL', 'Telefono', 'NumeroDeWhatsapp', 'WhatsApp', 'Celular', 'Numero']
        columna_telefono = None
        
        # Detectar columna de patente
        columnas_patente = ['Patente', 'PATENTE', 'Placa', 'PLACA', 'Dominio', 'DOMINIO']
        columna_patente = None
        
        print(f"Columnas disponibles: {list(df.columns)}")
        
        for col in columnas_telefono:
            if col in df.columns:
                columna_telefono = col
                break
        
        for col in columnas_patente:
            if col in df.columns:
                columna_patente = col
                break
        
        if not columna_telefono:
            print("❌ No se encontró columna de teléfono en el Excel")
            print(f"Columnas disponibles: {list(df.columns)}")
            return
        
        print(f"✅ Columna de teléfono encontrada: {columna_telefono}")
        
        if columna_patente:
            print(f"✅ Columna de patente encontrada: {columna_patente}")
        else:
            print("⚠️  No se encontró columna de patente - se omitirá en el reporte")
        
        # Análisis inicial
        total_registros = len(df)
        telefonos_no_nulos = df[columna_telefono].notna().sum()
        telefonos_nulos = df[columna_telefono].isna().sum()
        
        print(f"\n📈 ANÁLISIS INICIAL:")
        print(f"  Total de registros: {total_registros}")
        print(f"  Teléfonos no nulos: {telefonos_no_nulos}")
        print(f"  Teléfonos nulos: {telefonos_nulos}")
        
        # Mostrar ejemplos de números originales
        print(f"\n📋 EJEMPLOS DE NÚMEROS ORIGINALES:")
        ejemplos = df[columna_telefono].dropna().head(10)
        for i, numero in enumerate(ejemplos, 1):
            print(f"  {i:2d}. '{numero}' (tipo: {type(numero)})")
        
        # Mostrar algunos valores únicos para verificar
        print(f"\n🔍 VALORES ÚNICOS (primeros 10):")
        valores_unicos = df[columna_telefono].dropna().unique()[:10]
        for i, valor in enumerate(valores_unicos, 1):
            print(f"  {i:2d}. '{valor}'")
        
        # Aplicar validación mejorada
        print(f"\n🔄 Aplicando validación mejorada...")
        df['NumeroValidado'] = df[columna_telefono].apply(validar_numero_telefono_mejorado)
        
        # Estadísticas después de validación
        numeros_validos = df['NumeroValidado'].notna().sum()
        numeros_invalidos = df['NumeroValidado'].isna().sum()
        
        print(f"\n📊 RESULTADOS DE VALIDACIÓN:")
        print(f"  ✅ Números válidos: {numeros_validos}")
        print(f"  ❌ Números inválidos: {numeros_invalidos}")
        print(f"  📈 Porcentaje válido: {(numeros_validos/total_registros)*100:.1f}%")
        
        # Mostrar ejemplos de números validados (con patente si existe)
        print(f"\n📋 EJEMPLOS DE NÚMEROS VALIDADOS:")
        validos = df[df['NumeroValidado'].notna()].head(10)
        for i, (_, row) in enumerate(validos.iterrows(), 1):
            original = row[columna_telefono]
            validado = row['NumeroValidado']
            if columna_patente:
                patente = row[columna_patente]
                print(f"  {i:2d}. Patente: '{patente}' | Tel: '{original}' -> '{validado}'")
            else:
                print(f"  {i:2d}. '{original}' -> '{validado}'")
        
        # Mostrar números problemáticos (con patente si existe)
        print(f"\n❌ NÚMEROS PROBLEMÁTICOS:")
        problematicos_df = df[df['NumeroValidado'].isna()]
        problematicos_sample = problematicos_df[problematicos_df[columna_telefono].notna()].head(10)
        for i, (_, row) in enumerate(problematicos_sample.iterrows(), 1):
            numero = row[columna_telefono]
            if columna_patente:
                patente = row[columna_patente]
                print(f"  {i:2d}. Patente: '{patente}' | Tel: '{numero}'")
            else:
                print(f"  {i:2d}. '{numero}'")
        
        # Análisis por tipo de problema
        print(f"\n🔍 ANÁLISIS DETALLADO DE PROBLEMAS:")
        
        # Números que empiezan con 0
        empiezan_0 = df[df[columna_telefono].astype(str).str.startswith('0', na=False)][columna_telefono].count()
        print(f"  Números que empiezan con 0: {empiezan_0}")
        
        # Números muy cortos
        df_temp = df[df[columna_telefono].notna()].copy()
        df_temp['longitud'] = df_temp[columna_telefono].astype(str).str.len()
        muy_cortos = df_temp[df_temp['longitud'] < 8]['longitud'].count()
        muy_largos = df_temp[df_temp['longitud'] > 15]['longitud'].count()
        print(f"  Números muy cortos (<8 dígitos): {muy_cortos}")
        print(f"  Números muy largos (>15 caracteres): {muy_largos}")
        
        # Números con espacios
        con_espacios = df[df[columna_telefono].astype(str).str.contains(' ', na=False)][columna_telefono].count()
        print(f"  Números con espacios: {con_espacios}")
        
        # Números que parecen fechas
        parecen_fechas = df[df[columna_telefono].astype(str).str.contains('/', na=False)][columna_telefono].count()
        print(f"  Números que parecen fechas (contienen '/'): {parecen_fechas}")
        
        # Crear directorio de reportes
        directorio_reportes = crear_directorio_reportes()
        
        # Crear nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_validacion_telefonos_{timestamp}.xlsx"
        ruta_completa = os.path.join(directorio_reportes, nombre_archivo)
        
        # Guardar reporte detallado
        columnas_reporte = [columna_telefono, 'NumeroValidado']
        if columna_patente:
            columnas_reporte.insert(0, columna_patente)  # Agregar patente al inicio
        
        df_reporte = df[columnas_reporte].copy()
        df_reporte['Estado'] = df_reporte['NumeroValidado'].apply(lambda x: 'VÁLIDO' if pd.notna(x) else 'INVÁLIDO')
        
        # Agregar columna con tipo de problema para números inválidos
        def clasificar_problema(row):
            if pd.notna(row['NumeroValidado']):
                return 'OK'
            
            numero = str(row[columna_telefono])
            if pd.isna(row[columna_telefono]):
                return 'NULO'
            elif numero.lower() in ['nan', 'none', 'null', '']:
                return 'VACÍO'
            elif '/' in numero:
                return 'PARECE_FECHA'
            elif len(numero) < 8:
                return 'MUY_CORTO'
            elif len(numero) > 15:
                return 'MUY_LARGO'
            elif not any(c.isdigit() for c in numero):
                return 'SIN_DÍGITOS'
            else:
                return 'FORMATO_INVÁLIDO'
        
        df_reporte['TipoProblema'] = df_reporte.apply(clasificar_problema, axis=1)
        
        # Crear un archivo Excel con múltiples hojas
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            # Hoja 1: Datos detallados
            df_reporte.to_excel(writer, sheet_name='Datos_Detallados', index=False)
            
            # Hoja 2: Resumen ejecutivo
            resumen_data = {
                'Métrica': [
                    'Total de registros',
                    'Teléfonos no nulos',
                    'Teléfonos nulos',
                    'Números válidos',
                    'Números inválidos',
                    'Porcentaje válido',
                    'Números que empiezan con 0',
                    'Números muy cortos',
                    'Números muy largos',
                    'Números con espacios',
                    'Números que parecen fechas'
                ],
                'Valor': [
                    total_registros,
                    telefonos_no_nulos,
                    telefonos_nulos,
                    numeros_validos,
                    numeros_invalidos,
                    f"{(numeros_validos/total_registros)*100:.1f}%",
                    empiezan_0,
                    muy_cortos,
                    muy_largos,
                    con_espacios,
                    parecen_fechas
                ]
            }
            
            # Agregar información de patentes si existe la columna
            if columna_patente:
                patentes_no_nulas = df[columna_patente].notna().sum()
                patentes_nulas = df[columna_patente].isna().sum()
                patentes_unicas = df[columna_patente].nunique()
                
                resumen_data['Métrica'].extend([
                    '--- INFORMACIÓN DE PATENTES ---',
                    'Patentes no nulas',
                    'Patentes nulas',
                    'Patentes únicas'
                ])
                resumen_data['Valor'].extend([
                    '---',
                    patentes_no_nulas,
                    patentes_nulas,
                    patentes_unicas
                ])
            
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen_Ejecutivo', index=False)
            
            # Hoja 3: Análisis por tipo de problema
            df_problemas = df_reporte[df_reporte['Estado'] == 'INVÁLIDO']['TipoProblema'].value_counts().reset_index()
            df_problemas.columns = ['Tipo_Problema', 'Cantidad']
            df_problemas.to_excel(writer, sheet_name='Análisis_Problemas', index=False)
            
            # Hoja 4: Solo números válidos (para uso posterior)
            df_validos = df_reporte[df_reporte['Estado'] == 'VÁLIDO'].copy()
            if not df_validos.empty:
                df_validos.to_excel(writer, sheet_name='Números_Válidos', index=False)
        
        print(f"\n💾 Reporte completo guardado en: {ruta_completa}")
        print(f"📊 El archivo contiene 4 hojas:")
        print(f"    - Datos_Detallados: Todos los registros con validación")
        print(f"    - Resumen_Ejecutivo: Estadísticas generales")
        print(f"    - Análisis_Problemas: Conteo por tipo de problema")
        print(f"    - Números_Válidos: Solo registros con números válidos")
        
        return df
        
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
    Función principal para ejecutar el análisis.
    """
    print("="*70)
    print("ANÁLISIS DE NÚMEROS DE TELÉFONO - ARCHIVO EXCEL")
    print("="*70)
    
    # Verificar si existe el archivo
    if not os.path.exists(ARCHIVO_EXCEL):
        print(f"❌ No se encontró el archivo: {ARCHIVO_EXCEL}")
        print("Por favor, asegúrate de que el archivo esté en el directorio correcto.")
        return
    
    # Ejecutar análisis
    resultado = analizar_telefonos_excel(ARCHIVO_EXCEL)
    
    if resultado is not None:
        print(f"\n✅ Análisis completado exitosamente")
        print(f"📄 Revisa el archivo en el directorio 'reportes/' para ver todos los detalles")
    else:
        print(f"\n❌ El análisis no pudo completarse")
    
    print("="*70)


if __name__ == "__main__":
    main()