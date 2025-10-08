import pandas as pd

# Crear DataFrame desde un array
datos = [
    ["Ana", 28, "Madrid", 35000],
    ["Carlos", 35, "Barcelona", 42000],
    ["María", 31, "Valencia", 38000],
    ["Pedro", 29, "Sevilla", 32000]
]

columnas = ["Nombre", "Edad", "Ciudad", "Salario"]
df = pd.DataFrame(datos, columns=columnas)

# Guardar en Excel
with pd.ExcelWriter("datos_pandas.xlsx", engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Datos', index=False)
    
    # Acceder al workbook para formato adicional
    workbook = writer.book
    worksheet = writer.sheets['Datos']
    
    # Formato de cabecera
    for col_num, value in enumerate(df.columns.values):
        worksheet.cell(1, col_num + 1).font = openpyxl.styles.Font(bold=True)

print("Archivo guardado con Pandas!")