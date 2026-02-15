# 🚑 Solución de Permisos Grafana - SQLite (Método de Grupos Linux)

Si las ACLs (`setfacl`) fallan, este método utiliza los permisos estándar de Linux y es infalible si se siguen los pasos.

**Concepto**: Añadimos al usuario `grafana` (que ejecuta el servicio) al grupo principal del usuario `montero`, y permitimos que ese grupo "pase" por las carpetas.

### Pasos a ejecutar en la terminal de la Raspberry Pi:

#### 1. Añadir usuario `grafana` al grupo `montero`
```bash
sudo usermod -aG montero grafana
```

#### 2. Dar permiso de "Paso" y "Lectura" (Ejecución +x y Lectura +r)
Esto permite al grupo entrar en las carpetas Y LISTAR su contenido (necesario si Grafana intenta navegar por ellas).

```bash
sudo chmod g+rx /home/montero
sudo chmod g+rx /home/montero/Documentos
sudo chmod g+rx /home/montero/Documentos/Proyectos_Personales
sudo chmod g+rx /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter
sudo chmod g+rx /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python
sudo chmod g+rx /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data
```

#### 3. Dar permiso de LECTURA (+r) al archivo de base de datos
Esto permite al grupo leer el contenido.

```bash
sudo chmod g+r /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data/demeter_data.db
```

#### 4. Desactivar Sandboxing de Systemd (CRÍTICO)
Muchos servicios de Grafana modernos vienen bloqueados para no ver `/home` ni con permisos.

Vamos a crear el archivo de configuración manualmente para evitar el editor confuso:

```bash
# 1. Crear la carpeta de configuración del servicio
sudo mkdir -p /etc/systemd/system/grafana-server.service.d

# 2. Crear el archivo de override directamente
sudo bash -c 'cat <<EOF > /etc/systemd/system/grafana-server.service.d/override.conf
[Service]
ProtectHome=false
EOF'
```

#### 5. Reiniciar Grafana
Para aplicar permisos de grupo y configuración de systemd.

```bash
sudo systemctl daemon-reload
sudo systemctl restart grafana-server
```

---
### Verificación
Después de esto, vuelve a Grafana:
1. **Configuration** > **Data Sources** > **Demeter SQLite**.
2. Dale a **Save & Test**.
3. Debería aparecer: *"Data source is working"*.
