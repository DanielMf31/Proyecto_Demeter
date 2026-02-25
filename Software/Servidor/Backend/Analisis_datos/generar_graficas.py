import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib

# Set non-interactive backend immediately
matplotlib.use('Agg')

def configurar_estilo():
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10

def graficar_comparativa(datos_nodos: dict, output_dir: str):
    """Grafica comparativa temporal de T y VPD."""
    if not datos_nodos: return
    
    comparativa_dir = os.path.join(output_dir, "Comparacion_Global")
    os.makedirs(comparativa_dir, exist_ok=True)
    
    # Asegurar que cada df tiene su nodo
    dfs_con_nodo = []
    for nodo_id, df in datos_nodos.items():
        df_copy = df.copy()
        df_copy["Nodo"] = f"Planta {nodo_id}"
        dfs_con_nodo.append(df_copy)
        
    df_total = pd.concat(dfs_con_nodo)
    
    # 1. Temperatura
    plt.figure(figsize=(12, 6))
    if 'Hora_Medicion' in df_total.columns:
        sns.lineplot(data=df_total, x="Hora_Medicion", y="T_Bulbo_Seco_C", hue="Nodo", marker="o", palette="tab10")
    else:
        sns.lineplot(data=df_total, x="Timestamp", y="T_Bulbo_Seco_C", hue="Nodo", marker="o", palette="tab10")
        
    plt.title("Evolución Temporal: Temperatura")
    plt.ylabel("Temperatura (°C)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(comparativa_dir, "grafica_temperatura_global.png"))
    plt.close()
    
    # 2. VPD
    plt.figure(figsize=(12, 6))
    if 'Hora_Medicion' in df_total.columns:
        sns.lineplot(data=df_total, x="Hora_Medicion", y="VPD_kPa", hue="Nodo", marker="o", palette="viridis")
    else:
        sns.lineplot(data=df_total, x="Timestamp", y="VPD_kPa", hue="Nodo", marker="o", palette="viridis")

    plt.axhspan(0.4, 1.2, color='green', alpha=0.1, label='Zona Óptima')
    plt.axhspan(1.5, 3.0, color='red', alpha=0.1, label='Alto Déficit')
    plt.title("Evolución Temporal: VPD")
    plt.ylabel("VPD (kPa)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(comparativa_dir, "grafica_vpd_global.png"))
    plt.close()

def graficar_comparativa_avanzada(datos_nodos: dict, output_dir: str):
    """Genera gráficas comparativas estadísticas (Boxplots)."""
    if not datos_nodos: return
    comparativa_dir = os.path.join(output_dir, "Comparacion_Global")
    
    dfs_con_nodo = []
    for nodo_id, df in datos_nodos.items():
        df_copy = df.copy()
        df_copy["Nodo"] = f"Planta {nodo_id}"
        dfs_con_nodo.append(df_copy)
        
    df_total = pd.concat(dfs_con_nodo)

    # 1. Boxplots (Distribución de Temperatura y VPD)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    sns.boxplot(ax=axes[0], data=df_total, x="Nodo", y="T_Bulbo_Seco_C", hue="Nodo", palette="hot", legend=False)
    axes[0].set_title("Distribución de Temperatura")
    axes[0].tick_params(axis='x', rotation=15)
    
    sns.boxplot(ax=axes[1], data=df_total, x="Nodo", y="VPD_kPa", hue="Nodo", palette="viridis", legend=False)
    axes[1].set_title("Distribución de VPD")
    axes[1].tick_params(axis='x', rotation=15)
    
    plt.tight_layout()
    plt.savefig(os.path.join(comparativa_dir, "boxplot_estadistico.png"))
    plt.close()
    
    # 2. Bar Chart (Resumen Métricas)
    resumen = df_total.groupby("Nodo").agg({
        "T_Bulbo_Seco_C": "max",
        "VPD_kPa": "mean"
    }).reset_index()
    resumen.columns = ["Nodo", "T_Max", "VPD_Medio"]
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.barplot(ax=axes[0], data=resumen, x="Nodo", y="T_Max", hue="Nodo", palette="Reds", legend=False)
    axes[0].set_title("Temperatura Máxima (°C)")
    axes[0].tick_params(axis='x', rotation=15)
    
    sns.barplot(ax=axes[1], data=resumen, x="Nodo", y="VPD_Medio", hue="Nodo", palette="Greens", legend=False)
    axes[1].set_title("VPD Promedio (kPa)")
    axes[1].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(os.path.join(comparativa_dir, "resumen_barras.png"))
    plt.close()

def graficar_nodo_individual(df: pd.DataFrame, nodo_id: str, base_output_dir: str):
    """Genera set completo de gráficas para un solo nodo en su propia carpeta."""
    output_dir = os.path.join(base_output_dir, f"Planta_{nodo_id}")
    os.makedirs(output_dir, exist_ok=True)
        
    # 1. Series Temporales Panel
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    x_col = "Hora_Medicion" if "Hora_Medicion" in df.columns else "Timestamp"

    sns.lineplot(ax=axes[0], data=df, x=x_col, y="T_Bulbo_Seco_C", color="tab:red", marker="o", label="Bulbo Seco")
    if "T_Bulbo_Humedo_C" in df.columns:
        sns.lineplot(ax=axes[0], data=df, x=x_col, y="T_Bulbo_Humedo_C", color="tab:blue", marker="s", label="Bulbo Húmedo")
    axes[0].set_title("Temperatura (°C)")
    axes[0].grid(True, alpha=0.3)
    
    sns.lineplot(ax=axes[1], data=df, x=x_col, y="Humedad_Rel_Percent", color="tab:blue", marker="o")
    axes[1].set_title("Humedad Relativa (%)")
    axes[1].grid(True, alpha=0.3)
    
    sns.lineplot(ax=axes[2], data=df, x=x_col, y="VPD_kPa", color="tab:green", marker="o")
    axes[2].axhspan(0.4, 1.2, color='green', alpha=0.1)
    axes[2].axhspan(1.5, 3.0, color='red', alpha=0.1)
    axes[2].set_title("VPD (kPa)")
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle(f"Análisis Horario: Planta {nodo_id}", fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"grafica_planta_{nodo_id}_panel.png"))
    plt.close()

def procesar_graficas_generales(datos_nodos: dict, output_dir: str):
    """Main workflow to trigger from the worker."""
    configurar_estilo()
    graficar_comparativa(datos_nodos, output_dir)
    graficar_comparativa_avanzada(datos_nodos, output_dir)
    
    for nodo_id, df in datos_nodos.items():
        graficar_nodo_individual(df, nodo_id, output_dir)
