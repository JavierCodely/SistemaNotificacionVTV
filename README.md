**Sistema de Notificación de Vencimientos VTV por WhatsApp**

Este proyecto brinda una solución automatizada, robusta y segura para enviar notificaciones personalizadas sobre vencimientos de la Verificación Técnica Vehicular (VTV) a través de WhatsApp Web. Está desarrollado en Python, utilizando Selenium para la automatización del navegador y Pandas para el procesamiento flexible de datos.

---

## 🚀 Novedades Destacadas

* 🛡️ Verificación de Contacto: Doble chequeo para asegurar que el chat activo en WhatsApp corresponde al contacto correcto antes de enviar el mensaje.
* 🧠 Procesamiento Inteligente de Fechas: Detección automática de formatos de fecha (DD/MM/AAAA, MM-DD-YY, etc.) en los archivos Excel.
* 🤖 Automatización Resistente a Errores: Manejador inteligente de ventanas emergentes y pop-ups en WhatsApp Web.
* 🐞 Herramientas de Depuración: Scripts dedicados para probar mensajes y validar tu Excel de forma independiente.
* ⚙️ Configuración Lista para Usar: Plantillas predefinidas y configuraciones por defecto para un funcionamiento inmediato.

---

## 🌟 Características Principales

* 📲 Automatización de WhatsApp: Envía mensajes masivos y personalizados a través de WhatsApp Web.
* 📊 Gestión Dinámica de Datos: Lee archivos Excel sin necesidad de modificar nombres de columnas; el sistema las detecta automáticamente.
* ⏰ Filtrado de Vencimientos: Notifica tanto VTV próximas a vencer como aquellas ya vencidas.
* 🧩 Alta Personalización: Controla días de antelación, intervalos entre mensajes y plantillas desde un archivo .env.
* 🔧 Utilidades de Datos: Scripts para calcular vencimientos y validar números telefónicos.
* 📁 Reportes Detallados: Generación automática de logs y reportes en Excel con fallos o envíos pendientes.
* 🖥️ Interfaz Interactiva por Consola: Resumen previo, vista previa de mensajes y confirmación manual antes de iniciar la campaña.

---

## 🛠️ Instalación y Configuración

### ✅ Requisitos

* Python 3.8 o superior
* Google Chrome actualizado
* Paquetes: pandas, selenium, python-dotenv, webdriver-manager, openpyxl

### 🚧 Pasos de Instalación

# 1. Clonar el repositorio

git clone https://github.com/JavierCodely/SistemaNotificacionVTV.git

cd SistemaNotificacionVTV

# 2. (Opcional) Crear entorno virtual

python -m venv venv

source venv/bin/activate  # Linux/Mac

venv\Scripts\activate     # Windows

# 3. Instalar dependencias

pip install -r requirements.txt

### ⚙️ Configuración

Podés personalizar el sistema creando un archivo .env en la raíz del proyecto. Si no lo hacés, se usarán valores por defecto definidos en config.py.

#### Ejemplo de .env

# Archivos y Parámetros

ARCHIVO_EXCEL="resultado_vencimientos.xlsx"

INTERVALO_MENSAJES=8

DIAS_ANTICIPACION=30

# Plantillas de mensajes (opcional)

# MENSAJE_TEMPLATE="Hola! Recordatorio VTV para tu patente. Vence el. Saludos!"

# MENSAJE_VENCIDO_TEMPLATE="URGENTE! La VTV de tu patente ESTÁ VENCIDA desde el ( días)."

---

## 📊 Preparación del Archivo Excel

No es necesario modificar los nombres de columnas. El sistema reconoce múltiples variantes automáticamente.

### ✅ Columnas esperadas (nombres alternativos reconocidos):

| Información         | Nombres de columna aceptados              |
| -------------------- | ----------------------------------------- |
| Patente              | Patente,DOMINIO,Placa,Matricula           |
| Teléfono            | Telefono,TEL,NumeroDeWhatsapp,Celular     |
| Fecha de Revisión   | FechaDeRevision,FechaRevision,Fecha, etc. |
| Fecha de Vencimiento | Vencimiento,FechaVTV,FechaDeVencimiento   |
| Marca                | Marca,MARCA,Brand                         |
| Modelo               | Modelo,MODELO,Model                       |

🎯 Compatibilidad de Fechas: Acepta formatos como 25/07/2025, 2025-07-25, 07-25-25, entre otros.

---

## ▶️ Uso del Sistema

### 🔍 Paso 1: Probar Configuración

#### Verificar plantillas de mensajes:

python debug_configuracion_mensaje.py

#### Verificar archivo Excel:

python debug_dates_script.py

---

### 🚀 Paso 2: Ejecutar Notificador Principal

1. Asegurate de que ARCHIVO_EXCEL esté bien definido en .env o config.py.
2. Ejecutá el script principal:

python main.py

3. Seguí las instrucciones de la terminal:

   * Vista previa de mensajes y resumen de vencimientos.
   * Se abrirá Chrome con WhatsApp Web (guardará la sesión).
   * Confirmá el inicio de la campaña de envíos.

---

## 🧩 Personalización de Plantillas

Las siguientes variables pueden usarse en los mensajes:

* {patente} – Patente del vehículo
* {marca} – Marca del vehículo
* {modelo} – Modelo del vehículo
* {fecha_revision} – Fecha de la última revisión
* {fecha_vencimiento} – Fecha de vencimiento de la VTV
* {dias_vencidos} – Días transcurridos desde el vencimiento (solo para VTV vencidas)

---

## ⚠️ Aviso Legal

Este proyecto es una herramienta de automatización que debe utilizarse con responsabilidad. El envío masivo de mensajes puede violar los Términos de Servicio de WhatsApp. Los desarrolladores no se responsabilizan por el mal uso del sistema. Asegurate de contar con el consentimiento de los destinatarios y evitá prácticas abusivas.

**
