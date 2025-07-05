#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo Notificador de WhatsApp (Versión Optimizada)
===================================================

Versión optimizada que solo verifica modales una vez al iniciar sesión
y luego se enfoca en las tareas de envío sin verificaciones adicionales.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

from utils import limpiar_texto_unicode
from config import CHROME_PROFILE_PATH, USER_AGENT

logger = logging.getLogger(__name__)

class WhatsAppNotifier:
    """
    Clase para automatizar el envío de mensajes de VTV por WhatsApp.
    Optimizada para verificar modales solo al iniciar sesión.
    """

    def __init__(self):
        """Inicializa el notificador."""
        self.driver = None
        self.modal_verificado = False  # Flag para controlar la verificación de modales

    def inicializar_driver(self):
        """
        Inicializa el driver de Chrome con configuración optimizada.
        """
        try:
            logger.info("Inicializando el driver de Chrome...")
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
            chrome_options.add_argument(f"--user-agent={USER_AGENT}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Script para ocultar que es un navegador automatizado
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Driver de Chrome inicializado correctamente.")
            return True
        except Exception as e:
            logger.error(f"Error al inicializar Chrome driver: {e}")
            logger.critical("Asegúrate de tener Google Chrome instalado y una conexión a internet.")
            return False

    def _cerrar_ventanas_modales(self):
        """
        Detecta y cierra ventanas modales que pueden aparecer en WhatsApp Web.
        SOLO se ejecuta una vez al iniciar sesión.
        """
        try:
            logger.info("Verificando si hay ventanas modales que cerrar...")

            # Esperar un poco para que el modal se cargue completamente
            time.sleep(3)

            # Verificar si hay un modal general usando role="dialog"
            modal_dialog_found = False
            try:
                modal_dialog = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
                )
                if modal_dialog.is_displayed():
                    logger.info("Modal detectado usando role='dialog'")
                    modal_dialog_found = True
            except TimeoutException:
                logger.debug("No se encontró modal con role='dialog'")

            if not modal_dialog_found:
                logger.info("No se encontraron ventanas modales para cerrar.")
                return

            # Lista de selectores específicos para el modal
            selectores_botones = [
                "//div[@role='dialog']//div[@role='button'][contains(text(), 'Continuar')]",
                "//div[@role='dialog']//button[contains(text(), 'Continuar')]",
                "//div[@role='dialog']//span[contains(text(), 'Continuar')]",
                "//div[@role='dialog']//div[contains(text(), 'Continuar')]",
                "//div[@role='dialog']//div[@role='button']",
                "//div[@role='dialog']//button",
                "//div[@role='dialog']//button[contains(@aria-label, 'Cerrar')]",
                "//div[@role='dialog']//div[contains(@aria-label, 'Close')]",
                "//div[@role='dialog']//button[contains(@aria-label, 'Close')]",
                "//div[@role='dialog']//*[@role='button']",
                "//div[@role='dialog']//button[@type='button']",
            ]

            modal_cerrado = False

            for i, selector in enumerate(selectores_botones):
                try:
                    logger.debug(f"Probando selector {i+1}: {selector}")
                    elementos = self.driver.find_elements(By.XPATH, selector)

                    if elementos:
                        logger.debug(f"Encontrados {len(elementos)} elementos con selector {i+1}")

                        for j, elemento in enumerate(elementos):
                            try:
                                if elemento.is_displayed() and elemento.is_enabled():
                                    # Hacer scroll al elemento
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                                    time.sleep(0.5)

                                    # Intentar diferentes métodos de clic
                                    try:
                                        elemento.click()
                                        logger.info(f"Modal cerrado con clic normal usando selector {i+1}")
                                        modal_cerrado = True
                                        break
                                    except Exception:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", elemento)
                                            logger.info(f"Modal cerrado con JavaScript usando selector {i+1}")
                                            modal_cerrado = True
                                            break
                                        except Exception:
                                            try:
                                                actions = ActionChains(self.driver)
                                                actions.move_to_element(elemento).click().perform()
                                                logger.info(f"Modal cerrado con ActionChains usando selector {i+1}")
                                                modal_cerrado = True
                                                break
                                            except Exception:
                                                continue
                            except Exception:
                                continue
                            
                        if modal_cerrado:
                            break

                except Exception:
                    continue
                
            # Si no se pudo cerrar con los selectores específicos, intentar presionar ESC
            if not modal_cerrado:
                logger.info("Intentando cerrar modal con tecla ESC...")
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(2)
                    modal_cerrado = True
                    logger.info("Modal cerrado con tecla ESC")
                except Exception:
                    pass

            if modal_cerrado:
                time.sleep(3)
                logger.info("Modal cerrado exitosamente")
            else:
                logger.warning("No se pudo cerrar el modal automáticamente")

        except Exception as e:
            logger.error(f"Error general al verificar ventanas modales: {str(e)}")

    def abrir_whatsapp(self):
        """
        Abre WhatsApp Web y espera la autenticación del usuario.
        Incluye verificación de modales SOLO una vez.
        """
        try:
            logger.info("Accediendo a WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")

            logger.info("Esperando autenticación. Escanea el código QR si es necesario.")
            
            # Intentar detectar si ya está logueado
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                logger.info("Sesión de WhatsApp ya activa.")
            except TimeoutException:
                # Si no está logueado, esperar el código QR
                logger.info("Esperando escaneo de código QR (máximo 60 segundos)...")
                WebDriverWait(self.driver, 60).until_not(
                    EC.presence_of_element_located((By.XPATH, "//canvas[@aria-label='Scan me!']"))
                )
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
                )
                logger.info("Autenticación por código QR exitosa.")
            
            # VERIFICACIÓN DE MODALES - SOLO UNA VEZ
            if not self.modal_verificado:
                logger.info("Realizando verificación única de modales...")
                self._cerrar_ventanas_modales()
                self.modal_verificado = True
                logger.info("Verificación de modales completada. No se realizarán más verificaciones.")
            
            return True
            
        except TimeoutException:
            logger.error("Tiempo de espera agotado para la autenticación en WhatsApp Web.")
            return False
        except Exception as e:
            logger.error(f"Error al inicializar WhatsApp: {e}")
            return False

    def _limpiar_campo_busqueda(self):
        """
        Limpia el campo de búsqueda de forma robusta.
        SIN verificación de modales.
        """
        try:
            # Buscar el campo de búsqueda con múltiples selectores
            selectores_busqueda = [
                "//div[@contenteditable='true'][@data-tab='3']",
                "//div[@role='textbox'][@data-tab='3']",
                "//div[contains(@aria-label, 'Buscar')][@contenteditable='true']",
                "//div[@aria-label='Cuadro de texto para ingresar la búsqueda']",
            ]

            search_box = None
            for selector in selectores_busqueda:
                try:
                    search_box = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if search_box:
                        logger.debug(f"Campo de búsqueda encontrado con selector: {selector}")
                        break
                except TimeoutException:
                    continue
                
            if not search_box:
                logger.error("No se pudo encontrar el campo de búsqueda")
                return False

            # Hacer scroll al campo de búsqueda
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
            time.sleep(1)

            # Intentar diferentes métodos para hacer clic
            click_successful = False

            try:
                search_box.click()
                click_successful = True
                logger.debug("Clic normal en campo de búsqueda exitoso")
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].click();", search_box)
                    click_successful = True
                    logger.debug("Clic con JavaScript en campo de búsqueda exitoso")
                except Exception:
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(search_box).click().perform()
                        click_successful = True
                        logger.debug("Clic con ActionChains en campo de búsqueda exitoso")
                    except Exception:
                        pass

            if not click_successful:
                logger.warning("No se pudo hacer clic en el campo de búsqueda")
                return False

            time.sleep(0.5)

            # Limpiar el campo usando múltiples métodos
            try:
                search_box.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                search_box.send_keys(Keys.DELETE)
                time.sleep(0.2)
                search_box.send_keys(Keys.BACKSPACE)
                time.sleep(0.2)
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(0.5)

                logger.debug("Campo de búsqueda limpiado exitosamente")
                return True

            except Exception as e:
                logger.warning(f"Error al limpiar el campo de búsqueda: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error general al limpiar campo de búsqueda: {str(e)}")
            return False

    def _buscar_contacto(self, numero):
        """
        Busca un contacto por número de teléfono.
        SIN verificación de modales.
        """
        try:
            logger.info(f"Buscando contacto: {numero}")
            
            # Paso 1: Limpiar completamente el campo de búsqueda
            if not self._limpiar_campo_busqueda():
                return False
            
            # Paso 2: Encontrar y hacer clic en el campo de búsqueda
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            
            # Paso 3: Escribir el número de teléfono
            search_box.click()
            time.sleep(0.5)
            search_box.send_keys(numero)
            time.sleep(2)  # Esperar a que aparezcan los resultados
            
            # Paso 4: Buscar el contacto en los resultados
            selectores_resultado = [
                "//div[@data-testid='cell-frame-container']",
                "//div[contains(@class, 'zoWT4')]",
                "//div[contains(@class, '_21S-L')]",
                "//div[contains(@class, 'zoWT4')]//span[contains(@class, 'ggj6brxn')]",
                "//div[contains(@class, 'cell-frame-container')]",
                "//div[@role='listitem']",
                "//div[contains(@class, 'chat-title')]",
                "//div[contains(@class, 'chat')]//span[contains(@title, '{}')]".format(numero)
            ]
            
            contacto_encontrado = False
            
            for i, selector in enumerate(selectores_resultado):
                try:
                    logger.debug(f"Intentando selector {i+1}: {selector}")
                    
                    resultados = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                    
                    # Buscar en todos los resultados
                    for resultado in resultados:
                        try:
                            texto_resultado = resultado.get_attribute('innerText') or ''
                            if numero in texto_resultado or any(digit in texto_resultado for digit in numero[-4:]):
                                
                                # Hacer scroll al elemento si es necesario
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
                                time.sleep(0.5)
                                
                                # Hacer clic en el resultado
                                resultado.click()
                                contacto_encontrado = True
                                logger.debug(f"Contacto encontrado y seleccionado con selector {i+1}")
                                break
                        except Exception:
                            continue
                    
                    if contacto_encontrado:
                        break
                        
                except TimeoutException:
                    continue
                except Exception:
                    continue
            
            if not contacto_encontrado:
                logger.warning(f"No se encontró contacto para: {numero}")
                return False
            
            # Paso 5: Verificar que se abrió el chat
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
                )
                logger.info(f"Chat abierto correctamente para: {numero}")
                return True
                
            except TimeoutException:
                logger.error(f"No se pudo abrir el chat para: {numero}")
                return False
                
        except Exception as e:
            logger.error(f"Error al buscar contacto {numero}: {str(e)}")
            return False

    def _enviar_mensaje(self, mensaje: str) -> bool:
        """
        Envía un mensaje al chat actualmente abierto.
        
        Args:
            mensaje (str): Mensaje a enviar.
            
        Returns:
            bool: True si el mensaje se envió correctamente, False en caso contrario.
        """
        try:
            # Limpiar el mensaje de caracteres problemáticos
            mensaje_limpio = limpiar_texto_unicode(mensaje)
            
            # Buscar el campo de texto del mensaje
            message_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            
            # Hacer clic en el campo de mensaje
            message_box.click()
            time.sleep(0.5)
            
            # Escribir el mensaje
            message_box.send_keys(mensaje_limpio)
            time.sleep(1)
            
            # Enviar el mensaje presionando Enter
            message_box.send_keys(Keys.ENTER)
            time.sleep(1)
            
            logger.info("Mensaje enviado correctamente.")
            return True
            
        except TimeoutException:
            logger.error("No se pudo encontrar el campo de mensaje.")
            return False
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            return False

    def _verificar_contacto_correcto(self, numero_esperado: str) -> bool:
        """
        Verifica que el chat abierto corresponde al número esperado.
        Versión mejorada con más selectores y métodos de verificación.
        
        Args:
            numero_esperado (str): Número que se espera que esté abierto.
            
        Returns:
            bool: True si el contacto es correcto, False en caso contrario.
        """
        try:
            logger.info(f"Verificando que el chat abierto corresponde a: {numero_esperado}")
            
            # Limpiar el número esperado (quitar espacios, guiones, etc.)
            numero_limpio = ''.join(filter(str.isdigit, numero_esperado))
            
            # Esperar a que el chat se cargue completamente
            time.sleep(2)
            
            # Método 1: Verificar el header del chat
            contacto_verificado = self._verificar_header_chat(numero_limpio)
            
            if contacto_verificado:
                return True
                
            # Método 2: Verificar información del contacto mediante clic en el header
            contacto_verificado = self._verificar_info_contacto(numero_limpio)
            
            if contacto_verificado:
                return True
                
            # Método 3: Verificar URL del chat
            contacto_verificado = self._verificar_url_chat(numero_limpio)
            
            if contacto_verificado:
                return True
                
            # Método 4: Verificar mediante atributos data-* y aria-*
            contacto_verificado = self._verificar_atributos_chat(numero_limpio)
            
            if contacto_verificado:
                return True
                
            logger.warning(f"⚠️ No se pudo verificar que el chat corresponde a: {numero_esperado}")
            
            # Log adicional para debug
            self._log_debug_info()
            
            return False
            
        except Exception as e:
            logger.error(f"Error al verificar contacto: {str(e)}")
            return False

    def _verificar_header_chat(self, numero_limpio: str) -> bool:
        """Verifica el contacto usando el header del chat."""
        try:
            # Selectores actualizados para el header del chat
            selectores_header = [
                # Selectores más específicos primero
                "//header[@data-testid='conversation-header']//span",
                "//div[@data-testid='conversation-header']//span",
                "//header//div[contains(@class, 'chat-title')]//span",
                "//div[@data-testid='conversation-panel-header']//span",
                
                # Selectores más generales
                "//header//span[@title]",
                "//header//span[contains(@class, 'ggj6brxn')]",
                "//div[contains(@class, 'zoWT4')]//span[contains(@class, 'ggj6brxn')]",
                "//div[contains(@class, 'chat-title')]//span",
                "//header//span[contains(@dir, 'auto')]",
                "//header//span[text()]",
                
                # Selectores alternativos
                "//div[@role='button']//span[contains(@class, 'ggj6brxn')]",
                "//div[@data-testid='cell-frame-title']//span",
                "//div[contains(@class, 'chat-header')]//span",
            ]
            
            for i, selector in enumerate(selectores_header):
                try:
                    logger.debug(f"Verificando header con selector {i+1}: {selector}")
                    
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    
                    for elemento in elementos:
                        try:
                            if not elemento.is_displayed():
                                continue
                                
                            # Obtener texto del elemento
                            texto = elemento.get_attribute('innerText') or ''
                            titulo = elemento.get_attribute('title') or ''
                            aria_label = elemento.get_attribute('aria-label') or ''
                            
                            # Buscar números en el texto
                            texto_completo = f"{texto} {titulo} {aria_label}".strip()
                            numeros_encontrados = ''.join(filter(str.isdigit, texto_completo))
                            
                            logger.debug(f"Texto encontrado: '{texto_completo}'")
                            logger.debug(f"Números extraídos: '{numeros_encontrados}'")
                            
                            # Verificar coincidencia
                            if self._verificar_coincidencia_numeros(numero_limpio, numeros_encontrados):
                                logger.info(f"✓ Contacto verificado por header: {texto_completo}")
                                return True
                                
                        except Exception as e:
                            logger.debug(f"Error al procesar elemento del header: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error con selector header {i+1}: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error en verificación de header: {e}")
            return False

    def _verificar_info_contacto(self, numero_limpio: str) -> bool:
        """Verifica el contacto haciendo clic en la información del contacto."""
        try:
            logger.debug("Intentando verificar mediante información del contacto")
            
            # Selectores para hacer clic en el header y abrir info del contacto
            selectores_header_click = [
                "//header[@data-testid='conversation-header']",
                "//div[@data-testid='conversation-header']",
                "//header//div[contains(@class, 'chat-title')]",
                "//div[@data-testid='conversation-panel-header']",
                "//header//span[contains(@class, 'ggj6brxn')]",
            ]
            
            for selector in selectores_header_click:
                try:
                    header_element = self.driver.find_element(By.XPATH, selector)
                    if header_element.is_displayed():
                        # Hacer clic en el header
                        header_element.click()
                        time.sleep(1)
                        
                        # Buscar información del contacto en el panel que se abre
                        selectores_info = [
                            "//div[contains(@class, 'contact-info')]//span",
                            "//div[@data-testid='drawer-right']//span",
                            "//div[contains(@class, 'drawer')]//span",
                            "//div[contains(@class, 'panel-right')]//span",
                            "//*[contains(text(), '+')]",
                        ]
                        
                        for info_selector in selectores_info:
                            try:
                                info_elements = self.driver.find_elements(By.XPATH, info_selector)
                                for info_element in info_elements:
                                    texto = info_element.get_attribute('innerText') or ''
                                    numeros = ''.join(filter(str.isdigit, texto))
                                    
                                    if self._verificar_coincidencia_numeros(numero_limpio, numeros):
                                        logger.info(f"✓ Contacto verificado por info del contacto: {texto}")
                                        
                                        # Cerrar el panel de información
                                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                                        time.sleep(0.5)
                                        
                                        return True
                                        
                            except Exception:
                                continue
                        
                        # Cerrar el panel de información si se abrió
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        time.sleep(0.5)
                        break
                        
                except Exception:
                    continue
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error en verificación de info del contacto: {e}")
            return False

    def _verificar_url_chat(self, numero_limpio: str) -> bool:
        """Verifica el contacto usando la URL del chat."""
        try:
            logger.debug("Verificando mediante URL del chat")
            
            url_actual = self.driver.current_url
            logger.debug(f"URL actual: {url_actual}")
            
            # Extraer números de la URL
            numeros_url = ''.join(filter(str.isdigit, url_actual))
            
            if self._verificar_coincidencia_numeros(numero_limpio, numeros_url):
                logger.info(f"✓ Contacto verificado por URL: {url_actual}")
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error en verificación de URL: {e}")
            return False

    def _verificar_atributos_chat(self, numero_limpio: str) -> bool:
        """Verifica el contacto usando atributos data-* y aria-*."""
        try:
            logger.debug("Verificando mediante atributos del chat")
            
            # Buscar elementos con atributos que puedan contener el número
            selectores_atributos = [
                "//*[@data-id]",
                "//*[@aria-label]",
                "//*[@data-testid]",
                "//*[@data-phone]",
                "//*[@data-number]",
            ]
            
            for selector in selectores_atributos:
                try:
                    elementos = self.driver.find_elements(By.XPATH, selector)
                    
                    for elemento in elementos:
                        try:
                            # Revisar diferentes atributos
                            atributos = ['data-id', 'aria-label', 'data-testid', 'data-phone', 'data-number']
                            
                            for atributo in atributos:
                                valor = elemento.get_attribute(atributo) or ''
                                numeros = ''.join(filter(str.isdigit, valor))
                                
                                if numeros and self._verificar_coincidencia_numeros(numero_limpio, numeros):
                                    logger.info(f"✓ Contacto verificado por atributo {atributo}: {valor}")
                                    return True
                                    
                        except Exception:
                            continue
                            
                except Exception:
                    continue
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error en verificación de atributos: {e}")
            return False

    def _verificar_coincidencia_numeros(self, numero_esperado: str, numero_encontrado: str) -> bool:
        """Verifica si dos números coinciden usando diferentes criterios."""
        try:
            if not numero_esperado or not numero_encontrado:
                return False
                
            # Criterio 1: Coincidencia exacta
            if numero_esperado == numero_encontrado:
                return True
                
            # Criterio 2: Uno contiene al otro
            if numero_esperado in numero_encontrado or numero_encontrado in numero_esperado:
                return True
                
            # Criterio 3: Coincidencia de los últimos 8 dígitos
            if len(numero_esperado) >= 8 and len(numero_encontrado) >= 8:
                if numero_esperado[-8:] == numero_encontrado[-8:]:
                    return True
                    
            # Criterio 4: Coincidencia de los últimos 10 dígitos (sin código país)
            if len(numero_esperado) >= 10 and len(numero_encontrado) >= 10:
                if numero_esperado[-10:] == numero_encontrado[-10:]:
                    return True
                    
            # Criterio 5: Verificar si el número esperado está al final del encontrado
            if numero_encontrado.endswith(numero_esperado):
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error en verificación de coincidencia: {e}")
            return False

    def _log_debug_info(self):
        """Log información adicional para debug."""
        try:
            logger.debug("=== DEBUG INFO ===")
            
            # Log URL actual
            url_actual = self.driver.current_url
            logger.debug(f"URL actual: {url_actual}")
            
            # Log título de la página
            titulo = self.driver.title
            logger.debug(f"Título: {titulo}")
            
            # Log algunos elementos del header
            try:
                header_elements = self.driver.find_elements(By.TAG_NAME, "header")
                for i, header in enumerate(header_elements):
                    text = header.get_attribute('innerText') or ''
                    if text.strip():
                        logger.debug(f"Header {i+1}: {text[:100]}...")
            except Exception:
                pass
                
            # Log algunos spans visibles
            try:
                spans = self.driver.find_elements(By.TAG_NAME, "span")
                span_count = 0
                for span in spans:
                    if span.is_displayed():
                        text = span.get_attribute('innerText') or ''
                        if text.strip() and any(c.isdigit() for c in text):
                            logger.debug(f"Span con números: {text}")
                            span_count += 1
                            if span_count >= 5:  # Limitar cantidad de logs
                                break
            except Exception:
                pass
                
            logger.debug("=== END DEBUG INFO ===")
            
        except Exception as e:
            logger.debug(f"Error en debug info: {e}")
    def enviar_notificacion(self, numero: str, mensaje: str) -> tuple[bool, str]:
        """
        Orquesta el proceso completo: buscar contacto, verificar y enviar mensaje.

        Args:
            numero (str): Número de teléfono del destinatario.
            mensaje (str): Mensaje a enviar.

        Returns:
            tuple[bool, str]: (True/False si fue exitoso, Razón del fallo).
        """
        if not self._buscar_contacto(numero):
            return False, f"No se pudo encontrar o seleccionar el contacto {numero}."
        
        time.sleep(1)  # Pequeña pausa entre la selección y la verificación

        # NUEVA VERIFICACIÓN: Confirmar que el chat correcto está abierto
        if not self._verificar_contacto_correcto(numero):
            logger.error(f"El chat abierto NO corresponde al número esperado: {numero}")
            self._limpiar_campo_busqueda()  # Limpiar búsqueda
            return False, f"El chat abierto no corresponde al número {numero}. Envío cancelado por seguridad."

        time.sleep(0.5)  # Pequeña pausa entre la verificación y el envío

        if not self._enviar_mensaje(mensaje):
            return False, f"Fallo al enviar el mensaje a {numero}."
        
        # Limpiar búsqueda para el siguiente contacto
        self._limpiar_campo_busqueda()
        
        return True, "Enviado"

    def cerrar(self):
        """Cierra el navegador y finaliza la sesión."""
        if self.driver:
            logger.info("Cerrando el navegador...")
            time.sleep(3)
            self.driver.quit()