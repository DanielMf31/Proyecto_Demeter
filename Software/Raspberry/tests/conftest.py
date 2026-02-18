import sys
import os
import pytest

# Add 'src' to sys.path so tests can import 'proyecto_demeter'
# This assumes conftest.py is in Python/tests/
# and src is in Python/src/
core_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if core_path not in sys.path:
    sys.path.insert(0, core_path)
