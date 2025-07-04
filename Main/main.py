#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de Entrada Principal - Notificador de Vencimientos VTV
============================================================

Este script orquesta el proceso completo de notificación:
1. Configura el entorno.
2. Carga y procesa los datos de los clientes desde un archivo Excel.
3. Filtra los clientes cuyas VTV están próximas a vencer O ya vencidas.
4. Inicializa WhatsApp Web a través de Selenium.
5. Itera sobre los clientes a notificar y envía un mensaje personalizado.
6. Genera un reporte con los envíos que no pudieron completarse.
"""

import time
import os
import logging

from whatsapp_notifier import WhatsAppNotifier
from data_handler import DataHandler
from utils import configurar_logging
from config import (
    ARCHIVO_EXCEL,
    REPORTE_FALLIDOS_EXCEL,
    INTERVALO_MENSAJES,
    MENSAJE_TEMPLATE,
    MENSAJE_VENCIDO_TEMPLATE
)

# Configurar logging al inicio
logger = configurar_logging()

def crear_mensaje_personalizado(dato):
    """
    Crea un mensaje personalizado basado en si la VTV está vencida o próxima a vencer.
    
    Args:
        dato (dict): Diccionario con los datos del cliente
        
    Returns:
        str: Mensaje personalizado
    """
    if dato['esta_vencida']:
        # VTV ya vencida - usar plantilla de vencido
        mensaje = MENSAJE_VENCIDO_TEMPLATE.format(
            nombre=dato['nombre'],
            patente=dato['patente'],
            fecha_vencimiento=dato['fecha_vencimiento'],
            dias_vencidos=dato['dias_vencidos']
        )
    else:
        # VTV próxima a vencer - usar plantilla normal
        mensaje = MENSAJE_TEMPLATE.format(
            nombre=dato['nombre'],
            patente=dato['patente'],
            fecha_vencimiento=dato['fecha_vencimiento']
        )
    
    return mensaje

def ejecutar_proceso():
    """Función principal que ejecuta todo el flujo de notificaciones."""
    logger.info("==================================================")
    logger.info("=== INICIANDO PROCESO DE NOTIFICACIONES DE VTV ===")
    logger.info("==================================================")

    # --- 1. Carga y Procesamiento de Datos ---
    if not os.path.exists(ARCHIVO_EXCEL):
        logger.critical(f"❌ Error: No se encontró el archivo de datos '{ARCHIVO_EXCEL}'.")
        logger.critical("Por favor, asegúrate de que el archivo exista en el directorio correcto.")
        return

    data_handler = DataHandler(ARCHIVO_EXCEL)
    
    # Mostrar configuración de columnas para debug
    data_handler.mostrar_configuracion_columnas()
    
    try:
        data_handler.cargar_y_procesar_datos()
        vencimientos_df = data_handler.filtrar_vencimientos_proximos()
    except ValueError as e:
        logger.critical(f"❌ Error en la estructura del Excel:")
        logger.critical(str(e))
        return
    except Exception as e:
        logger.critical(f"❌ Error crítico al procesar datos: {e}")
        return

    if vencimientos_df.empty:
        logger.info("✅ No hay vencimientos próximos ni vencidos para notificar. Proceso finalizado.")
        return

    # --- 2. Preparar datos para envío ---
    datos_envio = data_handler.obtener_datos_para_envio(vencimientos_df)

    # --- 3. Interacción con el Usuario ---
    print("\n" + "="*60)
    print("           NOTIFICADOR DE VENCIMIENTOS VTV")
    print("="*60)
    print(f"📊 Se encontraron {len(datos_envio)} vencimientos para notificar.")
    
    # Separar vencidas de próximas para mostrar estadísticas
    vencidas = [d for d in datos_envio if d['esta_vencida']]
    proximas = [d for d in datos_envio if not d['esta_vencida']]
    
    if len(vencidas) > 0:
        print(f"🔴 VTV VENCIDAS: {len(vencidas)}")
    if len(proximas) > 0:
        print(f"🟡 VTV PRÓXIMAS A VENCER: {len(proximas)}")
    
    print("🌐 A continuación se abrirá Google Chrome para conectar con WhatsApp Web.")
    print()
    print("📋 INSTRUCCIONES:")
    print("  1. Escanea el código QR con tu teléfono si es la primera vez.")
    print("  2. Una vez iniciada la sesión, el proceso comenzará automáticamente.")
    print("  3. NO CIERRES el navegador hasta que el proceso finalice.")
    print("="*60)

    # Mostrar preview de los primeros contactos
    print("\n📋 PREVIEW DE CONTACTOS A NOTIFICAR:")
    for i, dato in enumerate(datos_envio[:5]):
        estado = "VENCIDA" if dato['esta_vencida'] else "Por vencer"
        if dato['esta_vencida']:
            print(f"  {i+1}. {dato['nombre']} - {dato['patente']} ({estado} hace {dato['dias_vencidos']} días)")
        else:
            print(f"  {i+1}. {dato['nombre']} - {dato['patente']} ({estado} {dato['fecha_vencimiento']})")
    if len(datos_envio) > 5:
        print(f"  ... y {len(datos_envio) - 5} más")

    respuesta = input("\n¿Deseas continuar con el envío de notificaciones? (s/n): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        logger.info("❌ Proceso cancelado por el usuario.")
        return

    # --- 4. Inicialización de WhatsApp ---
    logger.info("🚀 Iniciando WhatsApp Web...")
    notificador = WhatsAppNotifier()
    if not notificador.inicializar_driver():
        return
    if not notificador.abrir_whatsapp():
        notificador.cerrar()
        return

    # --- 5. Proceso de Envío ---
    enviados_count = 0
    fallidos_list = []
    total_a_enviar = len(datos_envio)

    logger.info(f"📤 Comenzando envío de {total_a_enviar} mensajes...")

    for i, dato in enumerate(datos_envio):
        estado_log = "VENCIDA" if dato['esta_vencida'] else "Por vencer"
        logger.info(f"📨 Procesando {i+1}/{total_a_enviar}: {dato['nombre']} ({dato['numero']}) - {estado_log} ---")

        # Crear mensaje personalizado según el estado
        mensaje = crear_mensaje_personalizado(dato)
        
        # Log del tipo de mensaje que se enviará
        tipo_mensaje = "VENCIDA" if dato['esta_vencida'] else "PRÓXIMA A VENCER"
        logger.info(f"📝 Enviando mensaje de VTV {tipo_mensaje}")

        # Enviar notificación
        exito, razon_fallo = notificador.enviar_notificacion(dato['numero'], mensaje)

        if exito:
            enviados_count += 1
            logger.info(f"✅ Mensaje enviado exitosamente a {dato['nombre']}")
        else:
            logger.error(f"❌ Fallo al enviar a {dato['nombre']}: {razon_fallo}")
            fallidos_list.append({
                'NombreDelCliente': dato['nombre'],
                'NumeroDeWhatsapp': dato['numero_original'],
                'NumeroValidado': dato['numero'],
                'Patente': dato['patente'],
                'FechaVencimientoVTV': dato['fecha_vencimiento'],
                'EstadoVTV': 'VENCIDA' if dato['esta_vencida'] else 'PRÓXIMA A VENCER',
                'DiasVencidos': dato['dias_vencidos'] if dato['esta_vencida'] else 0,
                'MotivoDelFallo': razon_fallo
            })

        # Esperar antes del próximo envío (excepto en el último)
        if i < total_a_enviar - 1:
            logger.info(f"⏱️ Esperando {INTERVALO_MENSAJES} segundos para el próximo envío...")
            time.sleep(INTERVALO_MENSAJES)

    # --- 6. Finalización y Reporte ---
    logger.info("\n" + "="*60)
    logger.info("=== PROCESO DE NOTIFICACIONES COMPLETADO ===")
    logger.info(f"📊 Total de vencimientos a notificar: {total_a_enviar}")
    logger.info(f"✅ Mensajes enviados exitosamente: {enviados_count}")
    logger.info(f"❌ Mensajes fallidos: {len(fallidos_list)}")
    
    if len(fallidos_list) > 0:
        logger.info("📋 Contactos con fallo:")
        for fallido in fallidos_list:
            logger.info(f"  - {fallido['NombreDelCliente']}: {fallido['MotivoDelFallo']}")
    
    logger.info("="*60)

    # Generar reporte de fallidos
    data_handler.crear_reporte_fallidos(fallidos_list, REPORTE_FALLIDOS_EXCEL)

    # Cerrar navegador
    notificador.cerrar()
    logger.info("🎉 El script ha finalizado. Revisa el log y el reporte de fallidos si es necesario.")

    # Mostrar resumen final
    print("\n" + "="*60)
    print("           RESUMEN FINAL")
    print("="*60)
    print(f"✅ Enviados exitosamente: {enviados_count}/{total_a_enviar}")
    print(f"❌ Fallidos: {len(fallidos_list)}/{total_a_enviar}")
    
    # Mostrar desglose por tipo
    if len(vencidas) > 0 or len(proximas) > 0:
        print("\n📊 DESGLOSE POR TIPO:")
        if len(vencidas) > 0:
            print(f"🔴 VTV Vencidas notificadas: {len(vencidas)}")
        if len(proximas) > 0:
            print(f"🟡 VTV Próximas notificadas: {len(proximas)}")
    
    if len(fallidos_list) > 0:
        print(f"📄 Reporte de fallidos: {REPORTE_FALLIDOS_EXCEL}")
    print("="*60)


if __name__ == "__main__":
    try:
        ejecutar_proceso()
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Proceso interrumpido por el usuario.")
    except Exception as e:
        logger.critical(f"💥 Ha ocurrido un error crítico no controlado: {e}", exc_info=True)
    finally:
        input("\n🔚 Presiona Enter para salir...")  # Evitar que se cierre inmediatamente