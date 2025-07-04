#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gestión de Datos
===========================

Clase para manejar la carga, validación y procesamiento de datos desde
el archivo Excel, así como la generación de reportes.
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
    # Si cambias los nombres de las columnas en tu Excel, 
    # modifica únicamente estos valores aquí:
    
    COLUMNAS_REQUERIDAS = {
        'nombre': 'NombreDelCliente',        # Nombre del cliente
        'telefono': 'NumeroDeWhatsapp',      # Número de WhatsApp
        'patente': 'Patente',                # Patente del vehículo
        'fecha_vencimiento': 'FechaVencimientoVTV'  # Fecha de vencimiento VTV
    }
    
    # Mapeo de columnas alternativas (por si el Excel tiene otros nombres)
    COLUMNAS_ALTERNATIVAS = {
        'nombre': ['Nombre', 'Cliente', 'NombreCliente', 'Titular'],
        'telefono': ['Telefono', 'WhatsApp', 'Celular', 'Numero'],
        'patente': ['Dominio', 'Matricula', 'Placa'],
        'fecha_vencimiento': ['FechaVencimiento', 'Vencimiento', 'FechaVTV', 'VencimientoVTV']
    }
    
    def __init__(self, archivo_excel: str):
        """
        Inicializa el manejador de datos.

        Args:
            archivo_excel (str): Ruta al archivo Excel con los datos.
        """
        self.archivo_excel = archivo_excel
        self.df = None
        self.columnas_mapeadas = {}

    def _detectar_columnas(self, df: pd.DataFrame) -> dict:
        """
        Detecta automáticamente las columnas del Excel basándose en los nombres.
        
        Args:
            df (pd.DataFrame): DataFrame cargado desde Excel
            
        Returns:
            dict: Mapeo de columnas encontradas
        """
        columnas_df = df.columns.tolist()
        columnas_encontradas = {}
        
        logger.info("Detectando columnas del Excel...")
        logger.info(f"Columnas disponibles: {columnas_df}")
        
        for campo, nombre_esperado in self.COLUMNAS_REQUERIDAS.items():
            columna_encontrada = None
            
            # Primero buscar el nombre exacto
            if nombre_esperado in columnas_df:
                columna_encontrada = nombre_esperado
                logger.info(f"✓ {campo.upper()}: '{nombre_esperado}' (nombre exacto)")
            else:
                # Buscar en nombres alternativos
                for nombre_alternativo in self.COLUMNAS_ALTERNATIVAS.get(campo, []):
                    if nombre_alternativo in columnas_df:
                        columna_encontrada = nombre_alternativo
                        logger.info(f"✓ {campo.upper()}: '{nombre_alternativo}' (nombre alternativo)")
                        break
                
                # Si no se encuentra, buscar por similitud (contiene)
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
        """
        Valida que se hayan encontrado todas las columnas requeridas.
        
        Args:
            columnas_encontradas (dict): Columnas detectadas
            
        Raises:
            ValueError: Si falta alguna columna requerida
        """
        faltantes = []
        
        for campo in self.COLUMNAS_REQUERIDAS.keys():
            if campo not in columnas_encontradas:
                nombres_posibles = [self.COLUMNAS_REQUERIDAS[campo]] + self.COLUMNAS_ALTERNATIVAS.get(campo, [])
                faltantes.append(f"  - {campo.upper()}: {', '.join(nombres_posibles)}")
        
        if faltantes:
            mensaje_error = (
                "❌ COLUMNAS FALTANTES EN EL EXCEL:\n"
                + "\n".join(faltantes) + 
                "\n\n💡 SOLUCIÓN: Asegúrate de que tu Excel tenga columnas con estos nombres, "
                "o modifica la configuración en data_handler.py líneas 20-30."
            )
            raise ValueError(mensaje_error)

    def cargar_y_procesar_datos(self):
        """
        Carga, valida y procesa los datos del archivo Excel.

        Returns:
            pd.DataFrame: DataFrame con los datos procesados y listos.
        """
        try:
            logger.info(f"📊 Cargando datos desde '{self.archivo_excel}'...")
            df = pd.read_excel(self.archivo_excel)
            
            # Detectar columnas automáticamente
            columnas_encontradas = self._detectar_columnas(df)
            self._validar_columnas_requeridas(columnas_encontradas)
            
            # Guardar el mapeo para uso posterior
            self.columnas_mapeadas = columnas_encontradas
            
            # Procesar datos usando las columnas mapeadas
            logger.info("🔄 Procesando datos...")
            
            # Convertir fecha de vencimiento con múltiples formatos
            fecha_col = columnas_encontradas['fecha_vencimiento']
            
            # Intentar diferentes formatos de fecha
            formatos_fecha = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d']
            
            for formato in formatos_fecha:
                try:
                    df[fecha_col] = pd.to_datetime(df[fecha_col], format=formato, errors='coerce')
                    logger.info(f"✓ Fechas convertidas con formato: {formato}")
                    break
                except ValueError:
                    continue
            else:
                # Si ningún formato específico funcionó, usar inferencia automática
                df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
                logger.info("✓ Fechas convertidas con inferencia automática")
            
            # Verificar si hay fechas inválidas
            fechas_invalidas = df[fecha_col].isna().sum()
            if fechas_invalidas > 0:
                logger.warning(f"⚠️ Se encontraron {fechas_invalidas} fechas inválidas que serán ignoradas")
            
            # Validar números de teléfono
            telefono_col = columnas_encontradas['telefono']
            df['NumeroValidado'] = df[telefono_col].apply(validar_numero_telefono)
            
            # Crear columnas estandarizadas para facilitar el acceso
            df['_nombre'] = df[columnas_encontradas['nombre']]
            df['_telefono'] = df[columnas_encontradas['telefono']]
            df['_patente'] = df[columnas_encontradas['patente']]
            df['_fecha_vencimiento'] = df[fecha_col]
            
            self.df = df
            logger.info(f"✅ Datos cargados y procesados exitosamente: {len(self.df)} registros.")
            return self.df
        
        except FileNotFoundError:
            logger.error(f"❌ Error: El archivo '{self.archivo_excel}' no fue encontrado.")
            raise
        except Exception as e:
            logger.error(f"❌ Error crítico al cargar los datos: {e}")
            raise

    def filtrar_vencimientos_proximos(self) -> pd.DataFrame:
        """
        Filtra los registros cuya VTV está por vencer O ya está vencida.
        Incluye tanto vencimientos próximos como vencimientos pasados.

        Returns:
            pd.DataFrame: Un DataFrame que contiene vencimientos próximos y vencidos.
        """
        if self.df is None:
            logger.error("❌ Los datos no han sido cargados. Ejecute 'cargar_y_procesar_datos' primero.")
            return pd.DataFrame()

        fecha_actual = datetime.now().date()
        fecha_limite_futura = fecha_actual + timedelta(days=DIAS_ANTICIPACION)
        
        # Consideramos VTV vencidas hasta 60 días atrás para notificar
        fecha_limite_pasada = fecha_actual - timedelta(days=60)
        
        logger.info(f"🔍 Filtrando vencimientos:")
        logger.info(f"  - VTV vencidas desde: {fecha_limite_pasada}")
        logger.info(f"  - Fecha actual: {fecha_actual}")
        logger.info(f"  - VTV por vencer hasta: {fecha_limite_futura} ({DIAS_ANTICIPACION} días)")
        
        # Filtrar registros válidos (sin datos faltantes)
        df_valido = self.df.dropna(subset=['_fecha_vencimiento', 'NumeroValidado']).copy()
        
        # Convertir fechas a date objects de forma segura
        df_valido['FechaVencimiento_Date'] = df_valido['_fecha_vencimiento'].dt.date
        
        # Filtrar por rango de fechas (incluye vencidas y próximas)
        vencimientos = df_valido[
            (df_valido['FechaVencimiento_Date'] >= fecha_limite_pasada) & 
            (df_valido['FechaVencimiento_Date'] <= fecha_limite_futura)
        ].copy()  # Usar .copy() para evitar el warning
        
        # Agregar columna para determinar si está vencida
        vencimientos['esta_vencida'] = vencimientos['FechaVencimiento_Date'] < fecha_actual
        
        # Calcular días vencidos de forma segura
        vencimientos['dias_vencidos'] = (fecha_actual - vencimientos['FechaVencimiento_Date']).apply(
            lambda x: x.days if hasattr(x, 'days') else 0
        )
        
        # Separar vencidas de próximas para el log
        vencidas = vencimientos[vencimientos['esta_vencida']]
        proximas = vencimientos[~vencimientos['esta_vencida']]
        
        logger.info(f"📋 Resultados encontrados:")
        logger.info(f"  - VTV vencidas: {len(vencidas)}")
        logger.info(f"  - VTV próximas a vencer: {len(proximas)}")
        logger.info(f"  - Total a notificar: {len(vencimientos)}")
        
        if len(vencidas) > 0:
            logger.info("📄 VTV VENCIDAS:")
            for _, row in vencidas.head(5).iterrows():
                dias_venc = row['dias_vencidos']
                logger.info(f"  - {row['_nombre']}: {row['_patente']} (vencida hace {dias_venc} días)")
            if len(vencidas) > 5:
                logger.info(f"  ... y {len(vencidas) - 5} más")
        
        if len(proximas) > 0:
            logger.info("📄 VTV PRÓXIMAS A VENCER:")
            for _, row in proximas.head(5).iterrows():
                logger.info(f"  - {row['_nombre']}: {row['_patente']} (vence {row['FechaVencimiento_Date']})")
            if len(proximas) > 5:
                logger.info(f"  ... y {len(proximas) - 5} más")
        
        return vencimientos

    def crear_reporte_fallidos(self, fallidos: list, archivo_salida: str):
        """
        Crea un archivo Excel con los detalles de los mensajes que no se pudieron enviar.

        Args:
            fallidos (list): Una lista de diccionarios con los datos de los envíos fallidos.
            archivo_salida (str): La ruta del archivo Excel de salida.
        """
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

    def obtener_info_columnas(self) -> dict:
        """
        Devuelve información sobre las columnas detectadas.
        
        Returns:
            dict: Información sobre las columnas del Excel
        """
        if not self.columnas_mapeadas:
            return {"error": "No se han cargado datos aún"}
        
        info = {
            "columnas_detectadas": self.columnas_mapeadas,
            "columnas_disponibles": list(self.df.columns) if self.df is not None else [],
            "total_registros": len(self.df) if self.df is not None else 0
        }
        
        return info

    def mostrar_configuracion_columnas(self):
        """
        Muestra la configuración actual de columnas para facilitar el debug.
        """
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
        
        print("📍 Ubicación: data_handler.py, líneas 20-30")
        print("="*60)

    def obtener_datos_para_envio(self, vencimientos_df: pd.DataFrame) -> list:
        """
        Convierte el DataFrame de vencimientos a una lista de diccionarios 
        con los datos necesarios para el envío.
        
        Args:
            vencimientos_df (pd.DataFrame): DataFrame con vencimientos próximos y vencidos
            
        Returns:
            list: Lista de diccionarios con datos para envío
        """
        datos_envio = []
        
        for _, row in vencimientos_df.iterrows():
            # Manejo seguro de fechas
            if pd.isna(row['_fecha_vencimiento']):
                continue
                
            fecha_vencimiento_str = row['_fecha_vencimiento'].strftime('%d/%m/%Y')
            
            dato = {
                'nombre': row['_nombre'],
                'patente': row['_patente'], 
                'numero': row['NumeroValidado'],
                'numero_original': row['_telefono'],
                'fecha_vencimiento': fecha_vencimiento_str,
                'esta_vencida': row['esta_vencida'],
                'dias_vencidos': row['dias_vencidos'] if row['esta_vencida'] else 0
            }
            datos_envio.append(dato)
        
        return datos_envio