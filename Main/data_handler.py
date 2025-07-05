#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección del módulo DataHandler - Formato de fechas corregido
"""

import pandas as pd
from datetime import datetime, timedelta
import logging
from utils import validar_numero_telefono
from config import DIAS_ANTICIPACION

logger = logging.getLogger(__name__)

class DataHandler:
    """Gestiona la carga y el procesamiento de datos del archivo Excel."""
    
    # ========================================
    # CONFIGURACIÓN DE COLUMNAS DEL EXCEL
    # ========================================
    COLUMNAS_REQUERIDAS = {
        'patente': 'Patente',
        'telefono': 'Telefono',
        'fecha_revision': 'FechaDeRevision',
        'fecha_vencimiento': 'FechaDeVencimiento',
        'marca': 'MARCA',
        'modelo': 'MODELO'
    }
    
    COLUMNAS_ALTERNATIVAS = {
        'patente': ['Dominio', 'Matricula', 'Placa'],
        'telefono': ['NumeroDeWhatsapp', 'WhatsApp', 'Celular', 'Numero'],
        'fecha_revision': ['FechaRevision', 'FechaDeRevision', 'FechaRealizacion'],
        'fecha_vencimiento': ['FechaVencimiento', 'FechaDeVencimiento', 'Vencimiento', 'FechaVTV', 'VencimientoVTV'],
        'marca': ['Marca', 'MARCA', 'Brand'],
        'modelo': ['Modelo', 'MODELO', 'Model']
    }
    
    def __init__(self, archivo_excel: str):
        self.archivo_excel = archivo_excel
        self.df = None
        self.columnas_mapeadas = {}

    def _detectar_columnas(self, df: pd.DataFrame) -> dict:
        """Detecta automáticamente las columnas del Excel."""
        columnas_df = df.columns.tolist()
        columnas_encontradas = {}
        
        logger.info("Detectando columnas del Excel...")
        logger.info(f"Columnas disponibles: {columnas_df}")
        
        for campo, nombre_esperado in self.COLUMNAS_REQUERIDAS.items():
            columna_encontrada = None
            
            if nombre_esperado in columnas_df:
                columna_encontrada = nombre_esperado
                logger.info(f"✓ {campo.upper()}: '{nombre_esperado}' (nombre exacto)")
            else:
                for nombre_alternativo in self.COLUMNAS_ALTERNATIVAS.get(campo, []):
                    if nombre_alternativo in columnas_df:
                        columna_encontrada = nombre_alternativo
                        logger.info(f"✓ {campo.upper()}: '{nombre_alternativo}' (nombre alternativo)")
                        break
                
                if not columna_encontrada:
                    for col in columnas_df:
                        if any(alt.lower() in col.lower() for alt in self.COLUMNAS_ALTERNATIVAS.get(campo, [])):
                            columna_encontrada = col
                            logger.info(f"✓ {campo.upper()}: '{col}' (por similitud)")
                            break
            
            if columna_encontrada:
                columnas_encontradas[campo] = columna_encontrada
            else:
                logger.error(f"✗ {campo.upper()}: No se encontró una columna válida")
        
        return columnas_encontradas

    def _validar_columnas_requeridas(self, columnas_encontradas: dict):
        """Valida que se hayan encontrado todas las columnas requeridas."""
        faltantes = []
        
        for campo in self.COLUMNAS_REQUERIDAS.keys():
            if campo not in columnas_encontradas:
                nombres_posibles = [self.COLUMNAS_REQUERIDAS[campo]] + self.COLUMNAS_ALTERNATIVAS.get(campo, [])
                faltantes.append(f"  - {campo.upper()}: {', '.join(nombres_posibles)}")
        
        if faltantes:
            mensaje_error = (
                "❌ COLUMNAS FALTANTES EN EL EXCEL:\n"
                + "\n".join(faltantes) + 
                "\n\n💡 SOLUCIÓN: Asegúrate de que tu Excel tenga columnas con estos nombres."
            )
            raise ValueError(mensaje_error)

    def _procesar_fechas_mejorado(self, df: pd.DataFrame, columna: str) -> pd.Series:

        logger.info(f"🔍 Procesando fechas de la columna: {columna}")

        # Obtener muestra de datos para debugging
        muestra_datos = df[columna].dropna().head(10).tolist()
        logger.info(f"📋 Muestra de datos de fecha: {muestra_datos}")

        # Limpiar datos: remover espacios y convertir a string
        serie_limpia = df[columna].astype(str).str.strip()

        # FORMATOS CORREGIDOS - Procesamiento inteligente
        formatos_fecha = [
            '%d/%m/%y',    # 28/03/25 -> 2025-03-28 (FORMATO ARGENTINO)
            '%m/%d/%y',    # 03/28/25 -> 2025-03-28 (FORMATO US)
            '%d/%m/%Y',    # 28/03/2025 -> 2025-03-28 
            '%m/%d/%Y',    # 03/28/2025 -> 2025-03-28
            '%d-%m-%y',    # 28-03-25 -> 2025-03-28
            '%d-%m-%Y',    # 28-03-2025 -> 2025-03-28
            '%Y-%m-%d',    # 2025-03-28 -> 2025-03-28
            '%Y/%m/%d'     # 2025/03/28 -> 2025-03-28
        ]

        fechas_procesadas = None
        formato_exitoso = None
        mejor_resultado = 0

        # Estrategia mejorada: probar ambos formatos y elegir el mejor
        for formato in formatos_fecha:
            try:
                # Probar conversión
                fechas_temp = pd.to_datetime(serie_limpia, format=formato, errors='coerce')

                # Contar fechas válidas
                fechas_validas = fechas_temp.notna().sum()

                if fechas_validas > 0:
                    logger.info(f"✓ Formato '{formato}': {fechas_validas} fechas válidas de {len(serie_limpia)}")

                    # Usar el formato que procese MÁS fechas
                    if fechas_validas > mejor_resultado:
                        fechas_procesadas = fechas_temp
                        formato_exitoso = formato
                        mejor_resultado = fechas_validas

                        # Si procesamos todas las fechas, usar este formato
                        if fechas_validas == len(serie_limpia.replace('nan', pd.NA).dropna()):
                            logger.info(f"🎯 Formato perfecto encontrado: {formato}")
                            break
                else:
                    logger.debug(f"✗ Formato '{formato}': 0 fechas válidas")

            except Exception as e:
                logger.debug(f"✗ Error con formato '{formato}': {e}")
                continue
            
        # Si ningún formato específico funciona, usar inferencia automática
        if fechas_procesadas is None or mejor_resultado == 0:
            logger.info("🔄 Intentando inferencia automática...")
            try:
                # Probar interpretación automática con día primero
                fechas_procesadas = pd.to_datetime(serie_limpia, errors='coerce', dayfirst=True)
                fechas_validas = fechas_procesadas.notna().sum()

                if fechas_validas > mejor_resultado:
                    logger.info(f"✓ Inferencia automática (dayfirst=True): {fechas_validas} fechas válidas")
                    formato_exitoso = "inferencia automática (día primero)"
                    mejor_resultado = fechas_validas
                else:
                    # Probar con month first
                    fechas_procesadas = pd.to_datetime(serie_limpia, errors='coerce', dayfirst=False)
                    fechas_validas = fechas_procesadas.notna().sum()
                    if fechas_validas > mejor_resultado:
                        logger.info(f"✓ Inferencia automática (month first): {fechas_validas} fechas válidas")
                        formato_exitoso = "inferencia automática (mes primero)"
                        mejor_resultado = fechas_validas

            except Exception as e:
                logger.error(f"❌ Error en inferencia automática: {e}")
                fechas_procesadas = pd.Series([pd.NaT] * len(serie_limpia))

        # Logging de resultados detallado
        if fechas_procesadas is not None:
            fechas_validas = fechas_procesadas.notna().sum()
            fechas_invalidas = fechas_procesadas.isna().sum()

            logger.info(f"📊 Resultado final para {columna}:")
            logger.info(f"  - Formato exitoso: {formato_exitoso}")
            logger.info(f"  - Fechas válidas: {fechas_validas}")
            logger.info(f"  - Fechas inválidas: {fechas_invalidas}")

            # Mostrar rango de fechas válidas
            if fechas_validas > 0:
                fecha_min = fechas_procesadas.min()
                fecha_max = fechas_procesadas.max()
                logger.info(f"  - Rango de fechas: {fecha_min.strftime('%d/%m/%Y')} a {fecha_max.strftime('%d/%m/%Y')}")

                # Mostrar TODAS las fechas procesadas con sus valores originales
                logger.info("  - Mapeo completo:")
                for i, (orig, proc) in enumerate(zip(serie_limpia, fechas_procesadas)):
                    if pd.notna(proc):
                        logger.info(f"    {orig} -> {proc.strftime('%d/%m/%Y')}")
                    else:
                        logger.info(f"    {orig} -> NO PROCESADA")

            # Advertencia si hay fechas no procesadas
            if fechas_invalidas > 0:
                logger.warning(f"⚠️  {fechas_invalidas} fechas no pudieron ser procesadas")
                fechas_no_procesadas = serie_limpia[fechas_procesadas.isna()]
                logger.warning(f"   Fechas problemáticas: {fechas_no_procesadas.tolist()}")

        return fechas_procesadas

    def cargar_y_procesar_datos(self):
        """Carga, valida y procesa los datos del archivo Excel."""
        try:
            logger.info(f"📊 Cargando datos desde '{self.archivo_excel}'...")
            df = pd.read_excel(self.archivo_excel)
            
            # Detectar columnas automáticamente
            columnas_encontradas = self._detectar_columnas(df)
            self._validar_columnas_requeridas(columnas_encontradas)
            
            # Guardar el mapeo
            self.columnas_mapeadas = columnas_encontradas
            
            logger.info("🔄 Procesando datos...")
            
            # Procesar fechas con el método mejorado
            fecha_revision_col = columnas_encontradas['fecha_revision']
            fecha_vencimiento_col = columnas_encontradas['fecha_vencimiento']
            
            df['_fecha_revision'] = self._procesar_fechas_mejorado(df, fecha_revision_col)
            df['_fecha_vencimiento'] = self._procesar_fechas_mejorado(df, fecha_vencimiento_col)
            
            # Validar números de teléfono
            telefono_col = columnas_encontradas['telefono']
            df['NumeroValidado'] = df[telefono_col].apply(validar_numero_telefono)
            
            # Crear columnas estandarizadas
            df['_patente'] = df[columnas_encontradas['patente']]
            df['_telefono'] = df[columnas_encontradas['telefono']]
            df['_marca'] = df[columnas_encontradas['marca']]
            df['_modelo'] = df[columnas_encontradas['modelo']]
            
            self.df = df
            logger.info(f"✅ Datos cargados y procesados exitosamente: {len(self.df)} registros.")
            
            # Estadísticas finales
            fechas_revision_validas = df['_fecha_revision'].notna().sum()
            fechas_vencimiento_validas = df['_fecha_vencimiento'].notna().sum()
            telefonos_validos = df['NumeroValidado'].notna().sum()
            
            logger.info(f"📊 Resumen de datos procesados:")
            logger.info(f"  - Fechas de revisión válidas: {fechas_revision_validas}/{len(df)}")
            logger.info(f"  - Fechas de vencimiento válidas: {fechas_vencimiento_validas}/{len(df)}")
            logger.info(f"  - Teléfonos válidos: {telefonos_validos}/{len(df)}")
            
            return self.df
        
        except FileNotFoundError:
            logger.error(f"❌ Error: El archivo '{self.archivo_excel}' no fue encontrado.")
            raise
        except Exception as e:
            logger.error(f"❌ Error crítico al cargar los datos: {e}")
            raise

    def filtrar_vencimientos_proximos(self) -> pd.DataFrame:
        """Filtra los registros cuya VTV está por vencer O ya está vencida."""
        if self.df is None:
            logger.error("❌ Los datos no han sido cargados. Ejecute 'cargar_y_procesar_datos' primero.")
            return pd.DataFrame()
    
        fecha_actual = datetime.now().date()
        fecha_limite_futura = fecha_actual + timedelta(days=DIAS_ANTICIPACION)
        
        # ===== CAMBIO AQUÍ =====
        # ANTES (solo 60 días):
        # fecha_limite_pasada = fecha_actual - timedelta(days=60)
        
        # DESPUÉS (TODOS los vencidos):
        fecha_limite_pasada = datetime(2020, 1, 1).date()  # Fecha muy antigua para capturar todos
        
        # ===== FIN DEL CAMBIO =====
        logger.info(f"🔍 Filtrando vencimientos:")
        logger.info(f"  - VTV vencidas desde: {fecha_limite_pasada}")
        logger.info(f"  - Fecha actual: {fecha_actual}")
        logger.info(f"  - VTV por vencer hasta: {fecha_limite_futura} ({DIAS_ANTICIPACION} días)")
        
        # Filtrar registros válidos
        columnas_criticas = ['_fecha_vencimiento', '_fecha_revision', 'NumeroValidado', '_marca', '_modelo']
        df_valido = self.df.dropna(subset=columnas_criticas).copy()
        
        logger.info(f"📋 Registros con datos completos: {len(df_valido)}/{len(self.df)}")
        
        if len(df_valido) == 0:
            logger.warning("⚠️ No hay registros con datos completos para procesar.")
            return pd.DataFrame()
        
        # Convertir fechas a date objects
        df_valido['FechaVencimiento_Date'] = df_valido['_fecha_vencimiento'].dt.date
        df_valido['FechaRevision_Date'] = df_valido['_fecha_revision'].dt.date
        
        # DEBUG: Mostrar todas las fechas procesadas
        logger.info("🔍 DEBUG - Fechas procesadas:")
        for idx, row in df_valido.iterrows():
            logger.info(f"  - {row['_patente']}: Vencimiento {row['FechaVencimiento_Date']} - Revisión {row['FechaRevision_Date']}")
        
        # Filtrar por rango de fechas
        vencimientos = df_valido[
            (df_valido['FechaVencimiento_Date'] >= fecha_limite_pasada) & 
            (df_valido['FechaVencimiento_Date'] <= fecha_limite_futura)
        ].copy()
        
        # Agregar información de estado
        vencimientos['esta_vencida'] = vencimientos['FechaVencimiento_Date'] < fecha_actual
        vencimientos['dias_vencidos'] = (fecha_actual - vencimientos['FechaVencimiento_Date']).apply(
            lambda x: x.days if hasattr(x, 'days') else 0
        )
        
        # DEBUG: Mostrar detalles de cada vencimiento
        logger.info("🔍 DEBUG - Análisis de vencimientos:")
        for idx, row in vencimientos.iterrows():
            estado = "VENCIDA" if row['esta_vencida'] else "PRÓXIMA"
            dias = row['dias_vencidos'] if row['esta_vencida'] else (row['FechaVencimiento_Date'] - fecha_actual).days
            logger.info(f"  - {row['_patente']}: {estado} - {row['FechaVencimiento_Date']} ({dias} días)")
        
        # Separar para logging
        vencidas = vencimientos[vencimientos['esta_vencida']]
        proximas = vencimientos[~vencimientos['esta_vencida']]
        
        logger.info(f"📋 Resultados encontrados:")
        logger.info(f"  - VTV vencidas: {len(vencidas)}")
        logger.info(f"  - VTV próximas a vencer: {len(proximas)}")
        logger.info(f"  - Total a notificar: {len(vencimientos)}")
        
        # Mostrar ejemplos
        if len(vencidas) > 0:
            logger.info("📄 VTV VENCIDAS (ejemplos):")
            for _, row in vencidas.head(5).iterrows():
                dias_venc = row['dias_vencidos']
                logger.info(f"  - {row['_marca']} {row['_modelo']}: {row['_patente']} (vencida hace {dias_venc} días)")
        
        if len(proximas) > 0:
            logger.info("📄 VTV PRÓXIMAS A VENCER (ejemplos):")
            for _, row in proximas.head(5).iterrows():
                dias_restantes = (row['FechaVencimiento_Date'] - fecha_actual).days
                logger.info(f"  - {row['_marca']} {row['_modelo']}: {row['_patente']} (vence en {dias_restantes} días)")
        
        return vencimientos

    def crear_reporte_fallidos(self, fallidos: list, archivo_salida: str):
        """Crea un archivo Excel con los detalles de los mensajes fallidos."""
        if not fallidos:
            logger.info("✅ No hubo mensajes fallidos, no se generará reporte.")
            return

        try:
            logger.info(f"📊 Generando reporte de envíos fallidos en '{archivo_salida}'...")
            df_fallidos = pd.DataFrame(fallidos)
            df_fallidos.to_excel(archivo_salida, index=False, engine='openpyxl')
            logger.info("✅ Reporte de fallidos generado exitosamente.")
        except Exception as e:
            logger.error(f"❌ No se pudo generar el reporte de fallidos: {e}")

    def obtener_datos_para_envio(self, vencimientos_df: pd.DataFrame) -> list:
        """Convierte el DataFrame de vencimientos a lista de diccionarios para envío."""
        datos_envio = []
        
        for _, row in vencimientos_df.iterrows():
            if pd.isna(row['_fecha_vencimiento']) or pd.isna(row['_fecha_revision']):
                continue
                
            fecha_vencimiento_str = row['_fecha_vencimiento'].strftime('%d/%m/%Y')
            fecha_revision_str = row['_fecha_revision'].strftime('%d/%m/%Y')
            
            dato = {
                'patente': row['_patente'],
                'marca': row['_marca'],
                'modelo': row['_modelo'],
                'numero': row['NumeroValidado'],
                'numero_original': row['_telefono'],
                'fecha_revision': fecha_revision_str,
                'fecha_vencimiento': fecha_vencimiento_str,
                'esta_vencida': row['esta_vencida'],
                'dias_vencidos': row['dias_vencidos'] if row['esta_vencida'] else 0
            }
            datos_envio.append(dato)
        
        return datos_envio

    def obtener_info_columnas(self) -> dict:
        """Devuelve información sobre las columnas detectadas."""
        if not self.columnas_mapeadas:
            return {"error": "No se han cargado datos aún"}
        
        info = {
            "columnas_detectadas": self.columnas_mapeadas,
            "columnas_disponibles": list(self.df.columns) if self.df is not None else [],
            "total_registros": len(self.df) if self.df is not None else 0
        }
        
        return info

    def mostrar_configuracion_columnas(self):
        """Muestra la configuración actual de columnas."""
        print("\n" + "="*60)
        print("           CONFIGURACIÓN DE COLUMNAS")
        print("="*60)
        print("Si tu Excel tiene nombres diferentes, modifica estas líneas:")
        print()
        
        for campo, nombre in self.COLUMNAS_REQUERIDAS.items():
            alternativas = ", ".join(self.COLUMNAS_ALTERNATIVAS.get(campo, []))
            print(f"📋 {campo.upper():<15}: '{nombre}'")
            print(f"   Alternativas: {alternativas}")
            print()
        
        print("📍 Ubicación: data_handler.py, líneas 25-40")
        print("="*60)

    def debug_fechas(self):
        """Función de debugging para analizar problemas con fechas."""
        if self.df is None:
            print("❌ No hay datos cargados para debuggear.")
            return
        
        print("\n" + "="*60)
        print("           DEBUG DE FECHAS")
        print("="*60)
        
        for campo in ['fecha_revision', 'fecha_vencimiento']:
            if campo in self.columnas_mapeadas:
                columna = self.columnas_mapeadas[campo]
                print(f"\n🔍 Analizando columna: {columna}")
                
                # Mostrar datos originales
                datos_originales = self.df[columna].dropna().head(10)
                print(f"📋 Datos originales: {datos_originales.tolist()}")
                
                # Mostrar datos procesados
                columna_procesada = f"_{campo}"
                if columna_procesada in self.df.columns:
                    datos_procesados = self.df[columna_procesada].dropna().head(10)
                    print(f"📋 Datos procesados: {[d.strftime('%d/%m/%Y') if pd.notna(d) else 'NaT' for d in datos_procesados]}")
                    
                    # Estadísticas
                    total = len(self.df)
                    validos = self.df[columna_procesada].notna().sum()
                    invalidos = total - validos
                    print(f"📊 Estadísticas: {validos} válidas, {invalidos} inválidas de {total} total")
        
        print("="*60)