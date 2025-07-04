# Notificador de Vencimientos de VTV por WhatsApp

Este proyecto es una herramienta automatizada escrita en Python que lee datos de clientes desde un archivo Excel, identifica aquellos cuyas Verificaciones Técnicas Vehiculares (VTV) están próximas a vencer, y les envía un recordatorio personalizado a través de WhatsApp Web.

El script utiliza **Selenium** para automatizar la interacción con el navegador y **Pandas** para la manipulación de datos.

## ✨ Características Principales

- **Lectura desde Excel**: Carga la información de clientes, patentes y fechas de vencimiento desde un archivo `datos_vtv.xlsx`.
- **Filtro Inteligente**: Identifica automáticamente los vencimientos que ocurrirán dentro de un período configurable (por defecto, 15 días).
- **Mensajes Personalizados**: Envía un mensaje único a cada cliente con su nombre, patente y fecha de vencimiento.
- **Automatización de WhatsApp**: Abre WhatsApp Web, busca a cada contacto y envía el mensaje de forma automática.
- **Reporte de Errores**: Genera un archivo Excel (`reporte_fallidos.xlsx`) con una lista de todos los contactos a los que no se pudo enviar un mensaje y el motivo del fallo.
- **Registro de Actividades**: Crea un archivo de log (`vtv_notificaciones.log`) que detalla cada paso del proceso, facilitando la depuración.
- **Configuración Flexible**: Permite ajustar parámetros clave (como días de anticipación, intervalo entre mensajes y plantilla de mensaje) a través de un archivo `.env`.

---

## 🚀 Cómo Empezar

Sigue estos pasos para poner en funcionamiento el notificador en tu máquina local.

### Prerrequisitos

- **Python 3.8** o superior.
- Navegador **Google Chrome** instalado.
- Un archivo `datos_vtv.xlsx` con los datos de los clientes.

### 1. Configuración del Entorno

Primero, clona o descarga este proyecto en tu computadora.

Se recomienda encarecidamente crear un entorno virtual para aislar las dependencias del proyecto.

```bash
# Navega al directorio del proyecto
cd ruta/a/notificador_vtv

# Crea un entorno virtual
python -m venv venv

# Activa el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```
