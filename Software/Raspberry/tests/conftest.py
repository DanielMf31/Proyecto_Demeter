import sys
import os
from unittest.mock import MagicMock

# Inyectar src/ y Common/ en sys.path para que pytest encuentre los paquetes
_tests_dir = os.path.dirname(__file__)
_raspberry_root = os.path.abspath(os.path.join(_tests_dir, '..'))
_src = os.path.join(_raspberry_root, 'src')
_common = os.path.abspath(os.path.join(_raspberry_root, '../../Common'))

for _path in (_src, _common):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Mockear módulos de hardware que no están disponibles fuera de la Raspberry Pi
# para que el código pueda importarse correctamente en el entorno de test.
_hw_mocks = ['serial_asyncio', 'serial', 'RPi', 'RPi.GPIO']
for _mod in _hw_mocks:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()
