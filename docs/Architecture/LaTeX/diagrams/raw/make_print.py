#!/usr/bin/env python3
"""
make_print.py — Genera versiones _print.d2 con colores claros para impresión académica.

Transforma contextualmente SOLO fill: y font-color:, dejando stroke: intactos
para preservar la legibilidad de bordes y flechas.

Uso:
    python3 make_print.py                  # procesa todos los .d2 del directorio actual
    python3 make_print.py 01_serial.d2    # procesa uno solo
"""

import re
import sys
import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# MAPA DE COLORES: fill oscuros → claros (misma familia de hue)
# ─────────────────────────────────────────────────────────────────────────────
FILL_MAP = {
    # Negros / grises muy oscuros → blanco / casi blanco
    '"#0d1117"': '"#ffffff"',
    '"#161b22"': '"#f6f8fa"',
    '"#21262d"': '"#ffffff"',
    '"#1a1a1a"': '"#f8f8f8"',
    '"#0f1117"': '"#f8f9fa"',

    # Verdes oscuros → verdes muy claros
    '"#0f2d24"': '"#dff7eb"',
    '"#1f2d1f"': '"#dff7eb"',
    '"#1f2414"': '"#f0f9ec"',
    '"#0f1a0f"': '"#f0fff4"',
    '"#1a1f0f"': '"#f2f9e6"',

    # Azules oscuros → azules muy claros
    '"#0f1a28"': '"#e6f0ff"',
    '"#0f1e2d"': '"#e8f2ff"',
    '"#1a1f2b"': '"#eef4ff"',

    # Morados oscuros → morados muy claros
    '"#2d1f3d"': '"#f3e8ff"',
    '"#1a1520"': '"#f5f0ff"',

    # Rojos oscuros → rojos muy claros
    '"#2d0f0f"': '"#fff0f0"',
    '"#2d0a0a"': '"#ffe9e9"',

    # Ámbar / amarillo oscuro → amarillo muy claro
    '"#2d1f0f"': '"#fff8ec"',
    '"#2d2a14"': '"#fffce0"',
    '"#1a1f0f"': '"#f9ffe6"',
}

# ─────────────────────────────────────────────────────────────────────────────
# MAPA DE COLORES: font-color brillantes para fondo oscuro → oscuros para fondo claro
# ─────────────────────────────────────────────────────────────────────────────
FONT_MAP = {
    # Texto claro genérico
    '"#e6edf3"': '"#1a1a2e"',   # texto blanco-azulado → casi negro
    '"#8b949e"': '"#4a4a5a"',   # gris claro → gris oscuro legible
    '"#6e7681"': '"#4a4a5a"',   # gris → gris oscuro

    # Colores de acento como texto: versiones oscuras para fondo blanco
    '"#58a6ff"': '"#0550ae"',   # azul brillante → azul oscuro
    '"#3fb950"': '"#1a7f37"',   # verde brillante → verde oscuro
    '"#e3b341"': '"#9a6700"',   # ámbar brillante → ámbar oscuro
    '"#d2a8ff"': '"#6639ba"',   # morado brillante → morado oscuro
    '"#f85149"': '"#cf222e"',   # rojo brillante → rojo oscuro
    '"#388bfd"': '"#0969da"',   # azul → azul oscuro (más legible en blanco)
}

# Colores a NO tocar en font-color (texto blanco sobre fondo coloreado = OK)
KEEP_WHITE_FONT = {'"#ffffff"'}


def transform(content: str) -> str:
    """Aplica el mapa de colores contextualmente (fill:, font-color:, style.fill:, etc.)"""

    # fill: "COLOR"   o   style.fill: "COLOR"
    for old, new in FILL_MAP.items():
        pattern = r'((?:style\.)?fill:\s*)' + re.escape(old)
        content = re.sub(pattern, r'\g<1>' + new, content)

    # font-color: "COLOR"   o   style.font-color: "COLOR"
    for old, new in FONT_MAP.items():
        if old in KEEP_WHITE_FONT:
            continue
        pattern = r'((?:style\.)?font-color:\s*)' + re.escape(old)
        content = re.sub(pattern, r'\g<1>' + new, content)

    return content


def process_file(src: Path) -> Path:
    name = src.stem
    if name.endswith('_dark'):
        return None  # ya es una versión print, saltar
    dst = src.parent / f"{name}_dark.d2"
    original = src.read_text(encoding='utf-8')
    transformed = transform(original)
    # Añadir comentario de cabecera
    header = (
        "# AUTO-GENERADO por make_print.py — VERSIÓN PARA IMPRESIÓN\n"
        "# Colores adaptados para fondo blanco / documento académico\n"
        "# No editar directamente; editar el archivo fuente y regenerar.\n\n"
    )
    dst.write_text(header + transformed, encoding='utf-8')
    return dst


def main():
    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:] if f.endswith('.d2')]
    else:
        files = sorted(Path('.').glob('*.d2'))
        files = [f for f in files if not f.stem.endswith('_dark')]

    ok, skip = 0, 0
    for f in files:
        result = process_file(f)
        if result:
            print(f"  ✓ {f.name}  →  {result.name}")
            ok += 1
        else:
            skip += 1

    print(f"\n{ok} archivo(s) transformados, {skip} saltados.")


if __name__ == '__main__':
    main()
