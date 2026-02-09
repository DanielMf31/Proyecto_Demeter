#!/bin/bash

echo "🍌 Nano Banana: Buscando procesos perdidos..."

# Buscar procesos que usen el puerto 8888
echo "🔍 Comprobando puerto 8888..."
lsof -i :8888

# Matar procesos por nombre
echo "🔪 Matando procesos de Python relacionados (async_service.py, simple_server.py)..."
pkill -f "async_service.py"
pkill -f "simple_server.py"
pkill -f "main_async.py"

echo "✅ Limpieza completada. Ya puedes iniciar servidores nuevos sin conflictos."
