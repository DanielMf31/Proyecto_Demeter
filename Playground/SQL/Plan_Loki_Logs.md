# PRD: Integración de Logs con GLP (Grafana-Loki-Promtail)

## 1. 🎯 Objetivo
Visualizar los logs de la aplicación Python (`Proyecto_Demeter/Python/logs/*.log`) directamente en Grafana, permitiendo filtrado, búsqueda y correlación temporal con las métricas de sensores.

## 2. 🏗️ Arquitectura GLP (The "L" Stack)

El flujo de datos es:
1.  **Tu App**: Escribe texto en `app.log` (como siempre).
2.  **Promtail** (El Agente): Lee ese archivo en tiempo real, añade etiquetas (`job=demeter`, `host=raspberry`) y lo envía.
3.  **Loki** (El Almacén): Recibe los logs comprimidos y los guarda eficientemente.
4.  **Grafana** (El Visor): Consulta a Loki y muestra los logs.

## 3. 🚀 Pasos de Implementación

### Paso A: Instalación (Vía APT)
Loki y Promtail son de la misma gente que Grafana, así que están en el mismo repositorio.

1.  **Instalar Loki y Promtail**:
    ```bash
    sudo apt-get update
    sudo apt-get install loki promtail
    ```

2.  **Verificar servicios**:
    ```bash
    sudo systemctl enable loki promtail
    sudo systemctl start loki promtail
    ```

### Paso B: Configurar Promtail (El "Ojo" que mira los logs)
Necesitamos decirle a Promtail **dónde** están tus archivos.

1.  Edita la config: `sudo nano /etc/promtail/config.yml`
2.  Añade este bloque `scrape_configs` al final (o sustituye el ejemplo):

```yaml
scrape_configs:
- job_name: demeter_logs
  static_configs:
  - targets:
      - localhost
    labels:
      job: demeter_python
      __path__: /home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/Python/logs/*.log
```

3.  **IMPORTANTE**: Permisos de lectura.
    Promtail corre como usuario `promtail`. Necesita leer tus logs.
    *   *Opción Rápida (Dev)*: Añadir tu usuario al grupo `systemd-journal` o dar permisos de lectura global a la carpeta logs.
    *   `chmod -R o+r /home/danielmf31/Documentos/.../Python/logs/`

4.  Reinicia Promtail:
    ```bash
    sudo systemctl restart promtail
    ```

### Paso C: Conectar Grafana a Loki
1.  Ve a **Administration** -> **Data Sources**.
2.  **Add new data source** -> Busca **Loki**.
3.  URL: `http://localhost:3100` (Puerto por defecto de Loki).
4.  **Save & Test**. Debería salir verde.

### Paso D: Visualizar en Dashboard
1.  Añade un nuevo panel -> **Logs**.
2.  Selecciona data source **Loki**.
3.  En el navegador de etiquetas (Log Browser), selecciona:
    *   `job` = `demeter_python`
4.  ¡Verás tus logs en vivo!

## 4. 🧪 Verificación
1.  Ejecuta tu script Python para generar logs.
2.  Mira Grafana y confirma que aparecen las líneas nuevas casi al instante.
