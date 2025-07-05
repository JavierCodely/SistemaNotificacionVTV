import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys

def procesar_excel(archivo_entrada, archivo_salida):
    """
    Procesa un archivo Excel según las especificaciones:
    - Calcula fechas de vencimiento según la serie (B: 6 meses, C: 1 año, EF: 1 mes)
    - Maneja duplicados de patentes actualizando con la fecha más reciente
    - Completa números de teléfono faltantes
    """
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_entrada)
        
        # Definir los nombres de columnas según tu estructura
        columnas_esperadas = ['NRO', 'FechaDeRevision', 'DOMINIO', 'MARCA', 'MODELO', 'SERIE', 'NRO_INTERNO', 'OBLEA', 'TEL', 'EMAIL', 'BORRAR']
        
        # Si las columnas no tienen nombre, asignar nombres
        if df.columns.tolist() == list(range(len(df.columns))):
            df.columns = columnas_esperadas[:len(df.columns)]
        
        # Renombrar las columnas para que coincidan con el procesamiento
        df = df.rename(columns={
            'FechaDeRevision': 'Fecha',
            'DOMINIO': 'Patente',
            'TEL': 'Telefono'
        })
        
        # Convertir la columna Fecha a datetime (ahora es 'Fecha' después del renombrado)
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%m/%d/%y', errors='coerce')
        
        # Función para calcular fecha de vencimiento
        def calcular_vencimiento(fecha_revision, serie):
            if pd.isna(fecha_revision) or pd.isna(serie):
                return None
            
            fecha_revision = pd.to_datetime(fecha_revision)
            serie = str(serie).upper().strip()
            
            if serie == 'B':
                # 6 meses después: si es 7/1/24, será 1/1/25
                return fecha_revision + relativedelta(months=6)
            elif serie == 'C':
                # 1 año después: si es 7/1/24, será 7/1/25
                return fecha_revision + relativedelta(years=1)
            elif serie == 'EF':
                # 1 mes después: si es 7/1/24, será 8/1/24
                return fecha_revision + relativedelta(months=1)
            else:
                return None
        
        # Crear una copia del DataFrame para trabajar
        df_procesado = df.copy()
        
        # Calcular fechas de vencimiento iniciales (usando la columna 'SERIE' original)
        df_procesado['FechaDeVencimiento'] = df_procesado.apply(
            lambda row: calcular_vencimiento(row['Fecha'], row['SERIE']), axis=1
        )
        
        # Procesar duplicados de patentes (ahora usando la columna 'Patente' que viene de 'DOMINIO')
        patentes_unicas = df_procesado['Patente'].dropna().unique()
        
        resultado_final = []
        
        for patente in patentes_unicas:
            # Filtrar solo patentes que no estén vacías
            if pd.isna(patente) or str(patente).strip() == '':
                continue
                
            # Obtener todas las filas para esta patente
            filas_patente = df_procesado[df_procesado['Patente'] == patente].copy()
            
            if len(filas_patente) > 1:
                # Hay duplicados, necesitamos procesarlos
                
                # Encontrar la fecha más reciente
                fecha_mas_reciente = filas_patente['Fecha'].max()
                fila_mas_reciente = filas_patente[filas_patente['Fecha'] == fecha_mas_reciente].iloc[0]
                
                # Recopilar todos los teléfonos no nulos
                telefonos = filas_patente['Telefono'].dropna().unique()
                telefono_final = telefonos[0] if len(telefonos) > 0 else None
                
                # Recopilar información adicional (marca, modelo, email)
                marcas = filas_patente['MARCA'].dropna().unique()
                marca_final = marcas[0] if len(marcas) > 0 else None
                
                modelos = filas_patente['MODELO'].dropna().unique()
                modelo_final = modelos[0] if len(modelos) > 0 else None
                
                emails = filas_patente['EMAIL'].dropna().unique()
                email_final = emails[0] if len(emails) > 0 else None
                
                # Crear la fila final con la información más actualizada
                fila_final = fila_mas_reciente.copy()
                fila_final['Telefono'] = telefono_final
                fila_final['MARCA'] = marca_final
                fila_final['MODELO'] = modelo_final
                fila_final['EMAIL'] = email_final
                fila_final['FechaDeVencimiento'] = calcular_vencimiento(
                    fila_final['Fecha'], fila_final['SERIE']
                )
                
                resultado_final.append(fila_final)
            else:
                # No hay duplicados, agregar la fila tal como está
                resultado_final.append(filas_patente.iloc[0])
        
        # Crear el DataFrame final
        df_final = pd.DataFrame(resultado_final)
        
        # Seleccionar y reordenar las columnas según lo solicitado
        columnas_salida = ['Patente', 'Telefono', 'Fecha', 'FechaDeVencimiento', 'SERIE', 'MARCA', 'MODELO', 'EMAIL']
        
        # Renombrar la columna Fecha a FechaDeRevision
        df_final = df_final.rename(columns={'Fecha': 'FechaDeRevision'})
        
        # Seleccionar solo las columnas necesarias
        df_salida = df_final[['Patente', 'Telefono', 'FechaDeRevision', 'FechaDeVencimiento', 'SERIE', 'MARCA', 'MODELO', 'EMAIL']].copy()
        
        # Formatear las fechas como MM/DD/YY sin hora
        df_salida['FechaDeRevision'] = df_salida['FechaDeRevision'].dt.strftime('%m/%d/%y')
        df_salida['FechaDeVencimiento'] = df_salida['FechaDeVencimiento'].dt.strftime('%m/%d/%y')
        
        # Ordenar por patente
        df_salida = df_salida.sort_values('Patente')
        
        # Guardar el archivo Excel de salida
        df_salida.to_excel(archivo_salida, index=False)
        
        print(f"Archivo procesado exitosamente. Resultado guardado en: {archivo_salida}")
        print(f"Registros procesados: {len(df_salida)}")
        
        # Mostrar resumen
        print("\nResumen del procesamiento:")
        print(f"- Total de patentes únicas: {len(df_salida)}")
        print(f"- Registros con teléfono: {df_salida['Telefono'].notna().sum()}")
        print(f"- Registros con fecha de vencimiento: {df_salida['FechaDeVencimiento'].notna().sum()}")
        print(f"- Registros con serie: {df_salida['SERIE'].notna().sum()}")
        print(f"- Registros con marca: {df_salida['MARCA'].notna().sum()}")
        print(f"- Registros con modelo: {df_salida['MODELO'].notna().sum()}")
        print(f"- Registros con email: {df_salida['EMAIL'].notna().sum()}")
        
        return df_salida
        
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return None

def main():
    """
    Función principal para ejecutar el script
    """
    # Configurar los nombres de archivos
    archivo_entrada = "verificaciones enero 2024 a julio 2025.xlsx"  # Cambia por el nombre de tu archivo Excel
    archivo_salida = "resultado_vencimientos.xlsx"
    
    # Procesar el archivo
    resultado = procesar_excel(archivo_entrada, archivo_salida)
    
    if resultado is not None:
        print("\n" + "="*50)
        print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*50)
        print(f"Archivo de salida: {archivo_salida}")
        print("\nPrimeras 5 filas del resultado:")
        print(resultado.head().to_string(index=False))
    else:
        print("El procesamiento falló. Revisa los errores anteriores.")

if __name__ == "__main__":
    # Instalar las dependencias necesarias si no están instaladas
    try:
        import pandas as pd
        from dateutil.relativedelta import relativedelta
    except ImportError:
        print("Instalando dependencias necesarias...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl", "python-dateutil"])
        import pandas as pd
        from dateutil.relativedelta import relativedelta
    
    main()