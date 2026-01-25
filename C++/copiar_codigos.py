#!/usr/bin/env python3
"""
Script para copiar automáticamente todos los archivos .h y .cpp
de un proyecto PlatformIO y guardarlos en un archivo Codigos.txt
para compartir fácilmente en chats de IA.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def obtener_estructura_proyecto(base_path):
    """Obtiene la estructura de archivos del proyecto"""
    
    estructura = {
        'include': [],
        'src': [],
        'src_compartidos': [],
        'otros': []
    }
    
    # Buscar archivos .h en include/
    include_path = base_path / 'include'
    if include_path.exists():
        for archivo in include_path.glob('*.h'):
            estructura['include'].append(archivo)
    
    # Buscar main.cpp en src/
    src_path = base_path / 'src'
    if src_path.exists():
        # main.cpp en src/
        main_path = src_path / 'main.cpp'
        if main_path.exists():
            estructura['src'].append(main_path)
        
        # main_transmisor.cpp y main_receptor.cpp
        for pattern in ['main_*.cpp', 'Main*.cpp', 'MAIN*.cpp']:
            for archivo in src_path.glob(pattern):
                if archivo not in estructura['src']:
                    estructura['src'].append(archivo)
        
        # Archivos en src/Compartidos/
        compartidos_path = src_path / 'Compartidos'
        if compartidos_path.exists():
            for archivo in compartidos_path.glob('*.cpp'):
                estructura['src_compartidos'].append(archivo)
    
    # Buscar otros archivos .cpp en src/
    if src_path.exists():
        for archivo in src_path.rglob('*.cpp'):
            if archivo not in estructura['src'] and archivo not in estructura['src_compartidos']:
                estructura['otros'].append(archivo)
    
    return estructura

def leer_contenido_archivo(ruta_archivo):
    """Lee el contenido de un archivo con manejo de errores"""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"ERROR al leer archivo {ruta_archivo.name}: {str(e)}"

def generar_codigos_txt(base_path, estructura):
    """Genera el archivo Codigos.txt con todos los códigos"""
    
    output_path = base_path / 'Codigos.txt'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Cabecera
        f.write("=" * 80 + "\n")
        f.write("CÓDIGOS DEL PROYECTO INVERNADERO AUTOMÁTICO - PLATFORMIO\n")
        f.write(f"Generado automáticamente: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # 1. Archivos .h en include/
        if estructura['include']:
            f.write("=" * 80 + "\n")
            f.write("ARCHIVOS DE CABECERA (.h) - Carpeta 'include/'\n")
            f.write("=" * 80 + "\n\n")
            
            for archivo in sorted(estructura['include'], key=lambda x: x.name):
                f.write(f"// {'='*40}\n")
                f.write(f"// ARCHIVO: {archivo.name}\n")
                f.write(f"// RUTA: {archivo.relative_to(base_path)}\n")
                f.write(f"// {'='*40}\n\n")
                f.write(leer_contenido_archivo(archivo))
                f.write("\n\n")
        
        # 2. Archivos .cpp en src/Compartidos/
        if estructura['src_compartidos']:
            f.write("=" * 80 + "\n")
            f.write("ARCHIVOS DE IMPLEMENTACIÓN (.cpp) - Carpeta 'src/Compartidos/'\n")
            f.write("=" * 80 + "\n\n")
            
            for archivo in sorted(estructura['src_compartidos'], key=lambda x: x.name):
                f.write(f"// {'='*40}\n")
                f.write(f"// ARCHIVO: {archivo.name}\n")
                f.write(f"// RUTA: {archivo.relative_to(base_path)}\n")
                f.write(f"// {'='*40}\n\n")
                f.write(leer_contenido_archivo(archivo))
                f.write("\n\n")
        
        # 3. main.cpp y variantes
        if estructura['src']:
            f.write("=" * 80 + "\n")
            f.write("ARCHIVOS PRINCIPALES (.cpp) - Carpeta 'src/'\n")
            f.write("=" * 80 + "\n\n")
            
            for archivo in sorted(estructura['src'], key=lambda x: x.name):
                f.write(f"// {'='*40}\n")
                f.write(f"// ARCHIVO: {archivo.name}\n")
                f.write(f"// RUTA: {archivo.relative_to(base_path)}\n")
                f.write(f"// {'='*40}\n\n")
                f.write(leer_contenido_archivo(archivo))
                f.write("\n\n")
        
        # 4. Otros archivos .cpp
        if estructura['otros']:
            f.write("=" * 80 + "\n")
            f.write("OTROS ARCHIVOS (.cpp)\n")
            f.write("=" * 80 + "\n\n")
            
            for archivo in sorted(estructura['otros'], key=lambda x: x.name):
                f.write(f"// {'='*40}\n")
                f.write(f"// ARCHIVO: {archivo.name}\n")
                f.write(f"// RUTA: {archivo.relative_to(base_path)}\n")
                f.write(f"// {'='*40}\n\n")
                f.write(leer_contenido_archivo(archivo))
                f.write("\n\n")
        
        # Resumen
        f.write("=" * 80 + "\n")
        f.write("RESUMEN DE ARCHIVOS COPIADOS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Archivos .h en include/: {len(estructura['include'])}\n")
        f.write(f"Archivos .cpp en src/Compartidos/: {len(estructura['src_compartidos'])}\n")
        f.write(f"Archivos main.cpp en src/: {len(estructura['src'])}\n")
        f.write(f"Otros archivos .cpp: {len(estructura['otros'])}\n")
        f.write(f"TOTAL: {len(estructura['include']) + len(estructura['src_compartidos']) + len(estructura['src']) + len(estructura['otros'])}\n")
        f.write("=" * 80 + "\n")
    
    return output_path

def main():
    """Función principal"""
    
    # Obtener ruta actual del script
    script_dir = Path(__file__).parent.absolute()
    
    print("=" * 60)
    print("COPIADOR DE CÓDIGOS PARA PROYECTOS PLATFORMIO")
    print("=" * 60)
    
    print(f"\nBuscando proyecto en: {script_dir}")
    
    # Obtener estructura del proyecto
    estructura = obtener_estructura_proyecto(script_dir)
    
    # Mostrar resumen
    print("\nENCONTRADOS:")
    print(f"  • Archivos .h en include/: {len(estructura['include'])}")
    for archivo in estructura['include']:
        print(f"    - {archivo.name}")
    
    print(f"\n  • Archivos .cpp en src/Compartidos/: {len(estructura['src_compartidos'])}")
    for archivo in estructura['src_compartidos']:
        print(f"    - {archivo.name}")
    
    print(f"\n  • Archivos main en src/: {len(estructura['src'])}")
    for archivo in estructura['src']:
        print(f"    - {archivo.name}")
    
    total_archivos = (len(estructura['include']) + 
                     len(estructura['src_compartidos']) + 
                     len(estructura['src']) + 
                     len(estructura['otros']))
    
    if total_archivos == 0:
        print("\n⚠️  No se encontraron archivos .h o .cpp")
        print("   Asegúrate de que la estructura del proyecto sea:")
        print("   /include/       (archivos .h)")
        print("   /src/           (main.cpp)")
        print("   /src/Compartidos/ (archivos .cpp)")
        return
    
    # Generar archivo
    print(f"\nGenerando Codigos.txt...")
    output_path = generar_codigos_txt(script_dir, estructura)
    
    print(f"✅ Archivo generado: {output_path}")
    print(f"📊 Total de archivos incluidos: {total_archivos}")
    
    # Mostrar instrucciones
    print("\n" + "=" * 60)
    print("INSTRUCCIONES PARA USAR:")
    print("=" * 60)
    print("1. Copia el contenido de Codigos.txt")
    print("2. Pégalo en el chat de la IA")
    print("3. Añade tu pregunta o descripción del problema")
    print("\nPara ejecutar automáticamente en el futuro:")
    print(f"   $ python {Path(__file__).name}")
    print("=" * 60)

if __name__ == "__main__":
    main()