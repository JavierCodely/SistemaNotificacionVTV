
# Sistema de Notificaciones VTV

Un sistema automatizado para enviar notificaciones de vencimientos de VTV (Verificación Técnica Vehicular) a través de WhatsApp Web utilizando Python, Selenium y procesamiento de datos con pandas.

## 📋 Características Principales

* **Automatización completa** : Envío masivo de mensajes personalizados por WhatsApp
* **Detección inteligente** : Identifica automáticamente VTV vencidas y próximas a vencer
* **Configuración flexible** : Personaliza mensajes, intervalos y días de anticipación
* **Mapeo automático de columnas** : Detecta automáticamente las columnas de tu Excel
* **Reportes detallados** : Genera reportes de envíos exitosos y fallidos
* **Logging completo** : Registra todas las operaciones para seguimiento
* **Validación de datos** : Verifica y formatea números de teléfono argentinos

## 🎯 Casos de Uso

### VTV Próximas a Vencer

* Envía recordatorios cuando faltan X días para el vencimiento
* Mensaje personalizado con nombre, patente y fecha de vencimiento

### VTV Vencidas

* Notifica urgentemente sobre VTV que ya han vencido
* Incluye cantidad de días vencidos y advertencia sobre multas

## 🛠️ Instalación

### Requisitos Previos

1. **Python 3.8 o superior**
2. **Google Chrome** (versión actualizada)
3. **Microsoft Excel** o compatible para crear el archivo de datos

### Instalación Paso a Paso

1. **Clona o descarga el proyecto**

```bash
git clone https://github.com/JavierCodely/SistemaNotificacionVTV
cd SistemaNotificacionVTV
```

2. **Instala las dependencias**

```bash
pip install -r requirements.txt
```

3. **Configura tu archivo Excel**
   * Crea un archivo Excel llamado `datos_vtv.xlsx` con las siguientes columnas:
     * `NombreDelCliente`: Nombre del cliente
     * `NumeroDeWhatsapp`: Número de teléfono (formato argentino)
     * `Patente`: Patente del vehículo
     * `FechaVencimientoVTV`: Fecha de vencimiento (formato DD/MM/YYYY)
4. **Ejecuta el sistema**

```bash
python main.py
```

## 📊 Estructura del Archivo Excel

### Columnas Requeridas

| Columna             | Nombres Aceptados                                               | Ejemplo     |
| ------------------- | --------------------------------------------------------------- | ----------- |
| Nombre del Cliente  | `NombreDelCliente`,`Nombre`,`Cliente`,`Titular`         | Juan Pérez |
| Número de WhatsApp | `NumeroDeWhatsapp`,`Telefono`,`WhatsApp`,`Celular`      | 1123456789  |
| Patente             | `Patente`,`Dominio`,`Matricula`,`Placa`                 | ABC123      |
| Fecha Vencimiento   | `FechaVencimientoVTV`,`FechaVencimiento`,`VencimientoVTV` | 15/12/2024  |

### Ejemplo de Datos

```
| NombreDelCliente | NumeroDeWhatsapp | Patente | FechaVencimientoVTV |
|------------------|------------------|---------|---------------------|
| Juan Pérez       | 1123456789       | ABC123  | 15/12/2024         |
| María García     | 1187654321       | DEF456  | 20/11/2024         |
| Carlos López     | 1145678901       | GHI789  | 05/01/2025         |
```

## ⚙️ Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en el directorio raíz para personalizar la configuración:

```env
# Archivos
ARCHIVO_EXCEL=datos_vtv.xlsx
REPORTE_FALLIDOS_EXCEL=reporte_fallidos.xlsx
LOG_FILE=vtv_notificaciones.log

# Parámetros de notificación
INTERVALO_MENSAJES=5
DIAS_ANTICIPACION=15

# Mensajes personalizados
MENSAJE_TEMPLATE=Hola {nombre}! Te recordamos que la VTV de tu vehiculo patente {patente} vence el {fecha_vencimiento}. Te sugerimos renovarla pronto para evitar inconvenientes. Saludos del equipo!

MENSAJE_VENCIDO_TEMPLATE=Hola {nombre}! Te informamos que la VTV de tu vehiculo patente {patente} ESTÁ VENCIDA desde el {fecha_vencimiento} (hace {dias_vencidos} días). Es urgente que la renueves para evitar multas y problemas legales. Saludos del equipo!
```

### Configuración de Columnas

Si el Excel tiene nombres de columnas diferentes, puedes configurarlos en `data_handler.py`:

```python
COLUMNAS_REQUERIDAS = {
    'nombre': 'NombreDelCliente',
    'telefono': 'NumeroDeWhatsapp',
    'patente': 'Patente',
    'fecha_vencimiento': 'FechaVencimientoVTV'
}
```

## 🚀 Uso del Sistema

### Ejecución Normal

1. **Ejecuta el script principal**

```bash
python main.py
```

2. **Sigue las instrucciones en pantalla**
   * Se abrirá Google Chrome con WhatsApp Web
   * Escanea el código QR si es la primera vez
   * Confirma el envío de notificaciones
3. **Monitorea el progreso**
   * El sistema mostrará el progreso en tiempo real
   * Revisa el archivo de log para detalles completos

### Ejemplo de Ejecución

```
==================================================
=== INICIANDO PROCESO DE NOTIFICACIONES DE VTV ===
==================================================

📊 Se encontraron 25 vencimientos para notificar.
🔴 VTV VENCIDAS: 8
🟡 VTV PRÓXIMAS A VENCER: 17

📋 PREVIEW DE CONTACTOS A NOTIFICAR:
  1. Juan Pérez - ABC123 (VENCIDA hace 5 días)
  2. María García - DEF456 (Por vencer 20/12/2024)
  3. Carlos López - GHI789 (Por vencer 15/01/2025)
  ... y 22 más

¿Deseas continuar con el envío de notificaciones? (s/n): s
```

## 📱 Funcionamiento con WhatsApp

### Primera Vez

1. Se abre Chrome con WhatsApp Web
2. Escanea el código QR con tu teléfono
3. El sistema detecta automáticamente cuando estás conectado
4. Comienza el envío de mensajes

### Ejecuciones Posteriores

* Chrome recuerda tu sesión
* Se conecta automáticamente sin necesidad de escanear
* Proceso más rápido y fluido

## 📊 Reportes y Logging

### Archivo de Log

* **Ubicación** : `vtv_notificaciones.log`
* **Contenido** : Registro completo de todas las operaciones
* **Formato** : Timestamp, nivel, mensaje detallado

### Reporte de Fallidos

* **Archivo** : `reporte_fallidos.xlsx`
* **Contenido** : Contactos que no pudieron ser notificados
* **Incluye** : Motivo del fallo, datos del contacto, estado de VTV

### Estadísticas Finales

```
===============================================
           RESUMEN FINAL
===============================================
✅ Enviados exitosamente: 23/25
❌ Fallidos: 2/25

📊 DESGLOSE POR TIPO:
🔴 VTV Vencidas notificadas: 8
🟡 VTV Próximas notificadas: 15

📄 Reporte de fallidos: reporte_fallidos.xlsx
===============================================
```

## 🔧 Personalización

### Modificar Mensajes

Puedes personalizar los mensajes en el archivo `.env`:

```env
MENSAJE_TEMPLATE=¡Hola {nombre}! 🚗 Tu VTV de la patente {patente} vence el {fecha_vencimiento}. ¡No olvides renovarla! 📅

MENSAJE_VENCIDO_TEMPLATE=🚨 ¡URGENTE! {nombre}, tu VTV de la patente {patente} está VENCIDA desde el {fecha_vencimiento} (hace {dias_vencidos} días). ¡Renuévala YA! ⚠️
```

### Variables Disponibles

* `{nombre}`: Nombre del cliente
* `{patente}`: Patente del vehículo
* `{fecha_vencimiento}`: Fecha de vencimiento formateada
* `{dias_vencidos}`: Días transcurridos desde el vencimiento (solo para VTV vencidas)

### Ajustar Intervalos

* **INTERVALO_MENSAJES** : Segundos entre envíos (default: 5)
* **DIAS_ANTICIPACION** : Días antes del vencimiento para notificar (default: 15)

## 🛡️ Validaciones y Seguridad

### Validación de Números de Teléfono

* Formatea automáticamente números argentinos
* Añade prefijo +54 cuando es necesario
* Detecta y corrige formatos incorrectos

### Manejo de Errores

* Reintenta operaciones automáticamente
* Registra errores detallados en el log
* Continúa con el siguiente contacto si uno falla

### Protección contra Spam

* Intervalos configurables entre mensajes
* Evita envíos duplicados
* Respeta los límites de WhatsApp

## 🔄 Mantenimiento

### Actualización de Datos

1. Actualiza tu archivo Excel con nuevos datos
2. Vuelve a ejecutar el script
3. Solo se notificarán los vencimientos vigentes

### Limpieza de Archivos

* Los logs se acumulan, revisa y limpia periódicamente
* Los reportes de fallidos se sobrescriben en cada ejecución

## ❓ Troubleshooting

### Problemas Comunes

#### Error: "No se encontró el archivo Excel"

```
Solución: Asegúrate de que el archivo 'datos_vtv.xlsx' esté en el directorio correcto
```

#### Error: "Columnas faltantes en el Excel"

```
Solución: Verifica que tu Excel tenga las columnas requeridas o configura nombres alternativos
```

#### Error: "No se pudo encontrar el contacto"

```
Solución: Verifica que el número de teléfono sea correcto y que el contacto tenga WhatsApp
```

#### Chrome se cierra inesperadamente

```
Solución: Actualiza Chrome a la última versión y verifica que no haya otros procesos de Chrome ejecutándose
```

### Logs de Debug

Para más información detallada, revisa el archivo `vtv_notificaciones.log`:

```
2024-12-10 14:30:15 - INFO - 📊 Cargando datos desde 'datos_vtv.xlsx'...
2024-12-10 14:30:15 - INFO - ✓ NOMBRE: 'NombreDelCliente' (nombre exacto)
2024-12-10 14:30:15 - INFO - ✓ TELEFONO: 'NumeroDeWhatsapp' (nombre exacto)
2024-12-10 14:30:15 - INFO - ✅ Datos cargados y procesados exitosamente: 150 registros.
```

## 📄 Estructura del Proyecto

```
vtv-notifier/
├── main.py                 # Punto de entrada principal
├── config.py              # Configuración y variables de entorno
├── data_handler.py        # Procesamiento de datos Excel
├── whatsapp_notifier.py   # Automatización de WhatsApp
├── utils.py               # Funciones de utilidad
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno (crear)
├── datos_vtv.xlsx         # Archivo de datos (crear)
├── chrome_profile/        # Perfil de Chrome (generado automáticamente)
├── vtv_notificaciones.log # Log de operaciones (generado automáticamente)
└── reporte_fallidos.xlsx  # Reporte de envíos fallidos (generado automáticamente)
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Troubleshooting](https://claude.ai/chat/3d4a7e1a-315a-4734-865e-09956ee15f50#-troubleshooting)
2. Consulta los logs en `vtv_notificaciones.log`
3. Abre un issue en el repositorio
4. Consultame

---

 **⚠️ Aviso Legal** : Este sistema está diseñado para uso legítimo de notificaciones. Asegúrate de cumplir con las políticas de WhatsApp y las regulaciones locales sobre comunicaciones automatizadas.

 **📱 Compatibilidad** : Probado con WhatsApp Web en Chrome. Otros navegadores pueden requerir ajustes adicionales.
