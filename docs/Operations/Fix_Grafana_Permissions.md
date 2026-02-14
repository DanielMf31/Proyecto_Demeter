# 🚑 Solución de Permisos Grafana - SQLite (Método de Grupos Linux)

Si las ACLs (`setfacl`) fallan, este método utiliza los permisos estándar de Linux y es infalible si se siguen los pasos.

**Concepto**: Añadimos al usuario `grafana` (que ejecuta el servicio) al grupo principal del usuario `montero`, y permitimos que ese grupo "pase" por las carpetas.

### Pasos a ejecutar en la terminal de la Raspberry Pi:

#### 1. Añadir usuario `grafana` al grupo `montero`
```bash
sudo usermod -aG montero grafana
```

#### 2. Dar permiso de "Paso" (Ejecución +x) al grupo en toda la ruta
Esto **NO** da permiso de lectura ni escritura, solo permite "travesar" la carpeta para llegar a una subcarpeta. Es seguro.

```bash
sudo chmod g+x /home/montero
sudo chmod g+x /home/montero/Documentos
sudo chmod g+x /home/montero/Documentos/Proyectos_Personales
sudo chmod g+x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter
sudo chmod g+x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python
sudo chmod g+x /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data
```

#### 3. Dar permiso de LECTURA (+r) al archivo de base de datos
Esto permite al grupo leer el contenido.

```bash
sudo chmod g+r /home/montero/Documentos/Proyectos_Personales/Proyecto_Demeter/Python/data/demeter_data.db
```

#### 4. Reiniciar Grafana (CRÍTICO)
Para que el sistema reconozca que el usuario ha cambiado de grupos, hay que reiniciar el proceso.

```bash
sudo systemctl restart grafana-server
```

---
### Verificación
Después de esto, vuelve a Grafana:
1. **Configuration** > **Data Sources** > **Demeter SQLite**.
2. Dale a **Save & Test**.
3. Debería aparecer: *"Data source is working"*.
