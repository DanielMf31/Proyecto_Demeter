# Análisis de Parámetros Agronómicos

Este documento sirve como referencia para interpretar los resultados generados por el script `calculos_agronomicos.py` y `Resultados_Simulacion.xlsx`.

## 1. Estadística Descriptiva
| Parámetro | Definición | Interpretación |
|---|---|---|
| **Media (μ)** | Promedio aritmético de los datos. | Valor central de referencia. |
| **Desviación Estándar (σ)** | Medida de dispersión de los datos. | Alta σ indica clima inestable. Baja σ clima constante. |
| **Coef. Variación (CV)** | Variabilidad relativa (σ/μ). | CV < 10%: Muy estable. CV > 30%: Muy variable. |
| **SEM** | Error Estándar de la Media. | Precisión de la estimación del promedio con los datos actuales. |

## 2. Termodinámica (Agua y Aire)
| Parámetro | Unidad | Rango Óptimo (General) | Peligro / Alerta |
|---|---|---|---|
| **VPD** | kPa | **0.4 - 1.2 kPa** | < 0.2: Riesgo fúngico. > 1.5: Estrés hídrico. |
| **Punto de Rocío (Tdp)** | °C | N/A | Si T_hoja < Tdp, hay condensación. |
| **Entalpía (h)** | kJ/kg | **40 - 70 kJ/kg** | > 80: Exceso de energía, difícil de enfriar. |
| **Humedad Absoluta** | g/m³ | **10 - 22 g/m³** | Cantidad real de agua en el aire. |
| **Humedad Específica (q)** | kg/kg | - | Masa de vapor por unidad de masa de aire húmedo. |
| **Relación de Mezcla (r)** | kg/kg | - | Masa de vapor por unidad de masa de aire seco. |
| **Presión Vapor Sat/Act** | kPa | - | Bases para cálculo de VPD. |

## 3. Fenología
| Parámetro | Descripción | Uso |
|---|---|---|
| **GDD** | Grados Día. | Predecir etapas (Maíz ~1400-1600 GDD). |
| **DLI** | Integral de Luz. | 12-20 mol/m² (Hojas), 20-30 (Frutos). |
| **DTR** | Amplitud Térmica. | Tmax - Tmin. Afecta dulzura y estiramiento. |
| **Horas Frío** | Horas < 7.2°C. | Para frutales dormantes. |
| **CHU** | Unidades Calor Maíz. | Índice específico para maíz (Heat Units). |

## 4. Índices de Estrés y Salud
- **Heat Index (HI)**: Sensación térmica. Riesgo si > 30°C.
- **ETo**: Evapotranspiración Referencia. Guía para riego.
- **LSD (Leaf Sat. Deficit)**: Déficit Saturación Hoja. kPa entre el interior de la hoja y el aire.
- **Punto de Escarcha**: Tdp cuando es < 0°C. Riesgo de daño por congelación directa.
- **Riesgo Wallin**: Modelo de predicción de enfermedades fúngicas basado en horas de alta humedad. (0-4 escala de severidad).

## 5. Anomalías
- **Z-Score**: Desviaciones estándar desde la media. |Z| > 3 es un evento extremo.
- **Delta T**: Cambio de temperatura respecto a la hora anterior. Cambios bruscos (>3-5°C/h) estresan la planta.
