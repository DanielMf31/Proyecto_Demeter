#!/bin/bash

# Script inteligente para sincronizar y cambiar de ramas en Raspberry Pi
# Uso: bash deploy_branch.sh

echo "🍌 Demeter Deploy Manager"
echo "========================="

# 1. Fetch de todo el remoto
echo "[1/3] Descargando información del repositorio remoto..."
git fetch --all --prune

# 2. Mostrar ramas
echo ""
echo "Ramas Remotas Disponibles:"
git branch -r | grep -v '\->' | sed 's/origin\///'
echo ""

# 3. Preguntar al usuario
read -p "👉 Escribe el nombre de la rama a desplegar (ej. feature/gui-sequencer): " TARGET_BRANCH

if [ -z "$TARGET_BRANCH" ]; then
    echo "❌ Operación cancelada."
    exit 1
fi

# 4. Logic de Checkout
if git show-ref --verify --quiet refs/heads/$TARGET_BRANCH; then
    echo "✅ La rama local '$TARGET_BRANCH' ya existe. Actualizando..."
    git checkout $TARGET_BRANCH
    git pull origin $TARGET_BRANCH
else
    echo "✨ La rama es nueva en este dispositivo. Creando..."
    # Intenta hacer checkout directo (Git moderno lo detecta) o explícito
    git checkout -t origin/$TARGET_BRANCH || git checkout -b $TARGET_BRANCH origin/$TARGET_BRANCH
fi

# 5. Ejecutar Setup si existe
if [ -f "Python/setup_deployment.sh" ]; then
    echo "🔧 Ejecutando script de configuración del entorno..."
    bash Python/setup_deployment.sh
else
    echo "⚠️  No se encontró setup_deployment.sh en esta rama."
fi

echo "🚀 ¡Listo! Estás en la rama: $TARGET_BRANCH"
