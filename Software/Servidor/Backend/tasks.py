import time
import os
import io
import zipfile
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

def generar_analisis_cientifico(experimento_id: int):
    """
    Simula una tarea pesada de análisis científico procesando datos de múltiples
    nodos, calculando el VPD, generando gráficas con matplotlib y comprimiendo
    todo (junto con un reporte Excel) en un archivo ZIP.
    """
    # 1. Simular carga pesada (10 segundos)
    time.sleep(10)

    # 2. Generar datos simulados para múltiples nodos de las últimas 24 hrs
    ahora = datetime.now()
    rango_tiempos = [ahora - timedelta(hours=i) for i in range(24)]
    rango_tiempos.reverse()
    
    nodos = ['Planta_A', 'Planta_B']
    datos_nodos = {}
    
    for nodo in nodos:
        temp = [random.uniform(15.0, 30.0) for _ in range(24)]
        hum = [random.uniform(40.0, 80.0) for _ in range(24)]
        
        # Calcular VPD simulado
        # Presión de Vapor de Saturación (SVP) = 0.611 * exp( (17.27 * T) / (T + 237.3) )
        # Temperatura en °C, resultado en kPa
        svp = [0.611 * pow(2.71828, (17.27 * t) / (t + 237.3)) for t in temp]
        
        # Presión de Vapor Actual (AVP) = SVP * (Humedad / 100)
        avp = [s * (h / 100.0) for s, h in zip(svp, hum)]
        
        # VPD = SVP - AVP
        vpd = [s - a for s, a in zip(svp, avp)]
        
        df = pd.DataFrame({
            'Timestamp': rango_tiempos,
            'Temperatura_C': temp,
            'Humedad_%': hum,
            'VPD_kPa': vpd
        })
        datos_nodos[nodo] = df

    # --- Generación de Reportes en Memoria ---
    archivos_memoria = {} # dict para guardar buffer -> filename

    # 3. Guardar DataFrames a un archivo Excel en memoria
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for nodo, df in datos_nodos.items():
            df.to_excel(writer, sheet_name=nodo, index=False)
            
            # Formatear columnas
            worksheet = writer.sheets[nodo]
            worksheet.column_dimensions['A'].width = 25
            for col in ['B', 'C', 'D']:
                worksheet.column_dimensions[col].width = 15
    
    archivos_memoria['Resultados_Simulacion.xlsx'] = excel_buffer.getvalue()

    # 4. Generar Gráficas (PNGs) en memoria
    # Grafica comparativa de Temperatura
    plt.figure(figsize=(10, 6))
    for nodo, df in datos_nodos.items():
        plt.plot(df['Timestamp'], df['Temperatura_C'], marker='o', label=nodo)
    
    plt.title('Comparativa de Temperatura (24 Horas)')
    plt.xlabel('Hora')
    plt.ylabel('Temperatura (°C)')
    plt.grid(True)
    plt.legend()
    plt.gcf().autofmt_xdate()
    
    img_buffer_temp = io.BytesIO()
    plt.savefig(img_buffer_temp, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    archivos_memoria['grafica_temperatura.png'] = img_buffer_temp.getvalue()

    # Grafica comparativa de VPD
    plt.figure(figsize=(10, 6))
    for nodo, df in datos_nodos.items():
        plt.plot(df['Timestamp'], df['VPD_kPa'], marker='s', linestyle='--', label=nodo)
    
    plt.title('Comparativa de Deficit de Presión de Vapor - VPD (24 Horas)')
    plt.xlabel('Hora')
    plt.ylabel('VPD (kPa)')
    plt.grid(True)
    plt.legend()
    plt.gcf().autofmt_xdate()
    
    img_buffer_vpd = io.BytesIO()
    plt.savefig(img_buffer_vpd, format='png', bbox_inches='tight', dpi=300)
    plt.close()
    archivos_memoria['grafica_vpd.png'] = img_buffer_vpd.getvalue()

    # 5. Crear el archivo ZIP
    shared_dir = "/app/shared"
    os.makedirs(shared_dir, exist_ok=True)
    
    zip_filename = f"reporte_multi_nodo_{experimento_id}_{int(time.time())}.zip"
    zip_path = os.path.join(shared_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Añadir el excel
        zipf.writestr('Resultados_Simulacion.xlsx', archivos_memoria['Resultados_Simulacion.xlsx'])
        # Añadir las imagenes
        zipf.writestr('grafica_temperatura.png', archivos_memoria['grafica_temperatura.png'])
        zipf.writestr('grafica_vpd.png', archivos_memoria['grafica_vpd.png'])
        
        # Añadir un archivo de texto de reporte resumen
        texto_reporte = f"Reporte Generado para Experimento: {experimento_id}\n"
        texto_reporte += f"Fecha de generación: {ahora.isoformat()}\n\n"
        for nodo, df in datos_nodos.items():
            texto_reporte += f"Nodo: {nodo}\n"
            texto_reporte += f"- Temp Media: {df['Temperatura_C'].mean():.2f} °C\n"
            texto_reporte += f"- VPD Promedio: {df['VPD_kPa'].mean():.2f} kPa\n\n"
        
        zipf.writestr('Resumen.txt', texto_reporte)

    # 6. Retornar el nombre del archivo generado para que la API sepa qué servir
    return {"filename": zip_filename}

