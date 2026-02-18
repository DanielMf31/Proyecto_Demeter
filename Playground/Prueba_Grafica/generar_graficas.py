import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def configurar_estilo():
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10

def cargar_datos(excel_path):
    try:
        xls = pd.ExcelFile(excel_path)
        # Filtramos hojas que sean de datos (no resumen)
        hojas_datos = [h for h in xls.sheet_names if not h.endswith("_Res")]
        
        datos_nodos = {}
        for hoja in hojas_datos:
            df = pd.read_excel(xls, sheet_name=hoja)
            df["Nodo"] = hoja # Etiquetar con nombre de hoja
            datos_nodos[hoja] = df
            
        return datos_nodos
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return None

def graficar_comparativa(datos_nodos, output_dir):
    """Grafica comparativa temporal de T, VPD y Radiación."""
    if not datos_nodos: return
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    df_total = pd.concat(datos_nodos.values())
    
    # 1. Temperatura
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_total, x="Hora", y="T_Bulbo_Seco_C", hue="Nodo", marker="o")
    plt.title("Evolución Temporal: Temperatura")
    plt.ylabel("Temperatura (°C)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_Tiempo_Temperatura.png"))
    plt.close()
    
    # 2. VPD
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_total, x="Hora", y="VPD_kPa", hue="Nodo", marker="o")
    plt.axhspan(0.4, 1.2, color='green', alpha=0.1, label='Zona Óptima')
    plt.axhspan(1.5, 3.0, color='red', alpha=0.1, label='Alto Déficit')
    plt.title("Evolución Temporal: VPD")
    plt.ylabel("VPD (kPa)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_Tiempo_VPD.png"))
    plt.close()

def graficar_comparativa_avanzada(datos_nodos, output_dir):
    """Genera gráficas comparativas estadísticas (Boxplots, Barplots)."""
    if not datos_nodos: return
    comp_dir = output_dir # Ya es la carpeta Comparativas
    
    df_total = pd.concat(datos_nodos.values())

    # 1. Boxplots (Distribución de Temperatura y VPD)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    sns.boxplot(ax=axes[0], data=df_total, x="Nodo", y="T_Bulbo_Seco_C", hue="Nodo", palette="hot", legend=False)
    axes[0].set_title("Distribución de Temperatura")
    axes[0].tick_params(axis='x', rotation=15)
    
    sns.boxplot(ax=axes[1], data=df_total, x="Nodo", y="VPD_kPa", hue="Nodo", palette="viridis", legend=False)
    axes[1].set_title("Distribución de VPD")
    axes[1].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, "03_Boxplot_Temp_VPD.png"))
    plt.close()
    
    # 2. Violin Plot (Densidad)
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=df_total, x="Nodo", y="VPD_kPa", hue="Nodo", inner="quart", palette="muted", legend=False)
    plt.title("Densidad Probabilística de VPD")
    plt.axhspan(0.4, 1.2, color='green', alpha=0.1, label='Optimo')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, "04_Violin_VPD.png"))
    plt.close()
    
    # 3. Bar Chart (Resumen Métricas)
    resumen = df_total.groupby("Nodo").agg({
        "T_Bulbo_Seco_C": "max",
        "VPD_kPa": "mean",
        "Radiacion_W_m2": "sum" # Suma simple como proxy
    }).reset_index()
    resumen.columns = ["Nodo", "T_Max", "VPD_Medio", "Rad_Total"]
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    sns.barplot(ax=axes[0], data=resumen, x="Nodo", y="T_Max", hue="Nodo", palette="Reds", legend=False)
    axes[0].set_title("Temperatura Máxima (°C)")
    axes[0].tick_params(axis='x', rotation=15)
    
    sns.barplot(ax=axes[1], data=resumen, x="Nodo", y="VPD_Medio", hue="Nodo", palette="Greens", legend=False)
    axes[1].set_title("VPD Promedio (kPa)")
    axes[1].tick_params(axis='x', rotation=15)

    sns.barplot(ax=axes[2], data=resumen, x="Nodo", y="Rad_Total", hue="Nodo", palette="Oranges", legend=False)
    axes[2].set_title("Radiación Total Acumulada")
    axes[2].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig(os.path.join(comp_dir, "05_Resumen_Barras.png"))
    plt.close()
    
    print("   ✅ Comparativas estadísticas generadas.")


def graficar_nodo_individual(df, nombre_nodo, base_output_dir):
    """Genera set completo de gráficas para un solo nodo en su propia carpeta."""
    output_dir = os.path.join(base_output_dir, nombre_nodo)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 1. Series Temporales Panel
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=True)
    sns.lineplot(ax=axes[0, 0], data=df, x="Hora", y="T_Bulbo_Seco_C", color="tab:red", marker="o")
    axes[0, 0].set_title(f"Temperatura (°C)")
    axes[0, 0].grid(True, alpha=0.3)
    
    sns.lineplot(ax=axes[0, 1], data=df, x="Hora", y="Humedad_Rel_Percent", color="tab:blue", marker="o")
    axes[0, 1].set_title(f"Humedad Relativa (%)")
    axes[0, 1].grid(True, alpha=0.3)
    
    sns.lineplot(ax=axes[1, 0], data=df, x="Hora", y="VPD_kPa", color="tab:green", marker="o")
    axes[1, 0].axhspan(0.4, 1.2, color='green', alpha=0.1)
    axes[1, 0].axhspan(1.5, 3.0, color='red', alpha=0.1)
    axes[1, 0].set_title(f"VPD (kPa)")
    axes[1, 0].grid(True, alpha=0.3)
    
    sns.lineplot(ax=axes[1, 1], data=df, x="Hora", y="Radiacion_W_m2", color="tab:orange", marker="o")
    axes[1, 1].set_title(f"Radiación Solar (W/m²)")
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle(f"Análisis Horario: {nombre_nodo}", fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "01_Panel_Temporal.png"))
    plt.close()

    # 2. Distribuciones
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    vars = ["T_Bulbo_Seco_C", "VPD_kPa", "Delta_T_C_h"]
    colores = ["red", "green", "purple"]
    
    for i, var in enumerate(vars):
        if var in df.columns:
            sns.histplot(data=df, x=var, kde=True, ax=axes[i], color=colores[i], element="step")
            axes[i].set_title(f"Distribución {var}")
            axes[i].grid(True, alpha=0.3)
            
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "02_Distribuciones.png"))
    plt.close()
    
    print(f"   ✅ Reporte individual generado: {nombre_nodo}")

def main():
    base_dir = os.path.dirname(__file__)
    excel_path = os.path.join(base_dir, "Resultados_Simulacion.xlsx")
    output_dir = os.path.join(base_dir, "Resultados_Graficos")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"📂 Leyendo datos multi-nodo de: {excel_path}")
    datos_nodos = cargar_datos(excel_path)
    
    if datos_nodos:
        configurar_estilo()
        
        # 1. Gráficas Comparativas Globales
        print("📊 Generando comparativas globales...")
        graficar_comparativa(datos_nodos, os.path.join(output_dir, "Comparativas"))
        graficar_comparativa_avanzada(datos_nodos, os.path.join(output_dir, "Comparativas"))
        
        # 2. Gráficas Individuales por Nodo
        print("📊 Generando reportes individuales...")
        for nodo, df in datos_nodos.items():
            graficar_nodo_individual(df, nodo, output_dir)
            
        print(f"🎉 Reporte gráfico completo generado en: {output_dir}")

if __name__ == "__main__":
    main()
