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

    def enviar_notificacion(self, numero: str, mensaje: str) -> tuple[bool, str]:
        """
        Orquesta el proceso completo: buscar contacto y enviar mensaje.

        Args:
            numero (str): Número de teléfono del destinatario.
            mensaje (str): Mensaje a enviar.

        Returns:
            tuple[bool, str]: (True/False si fue exitoso, Razón del fallo).
        """
        if not self._buscar_contacto(numero):
            return False, f"No se pudo encontrar o seleccionar el contacto {numero}."
        
        time.sleep(1)  # Pequeña pausa entre la selección y el envío

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