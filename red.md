Aquí tienes la lista paso a paso, limpia y directa para que la copies en tu papel.

Guía Rápida WiFi Raspberry Pi (nmcli)
1. Actualizar la lista de redes

Bash
sudo nmcli dev wifi rescan
2. Listar todas las redes disponibles

Bash
nmcli dev wifi list
(Fíjate bien en la columna SSID para copiar el nombre exacto con sus mayúsculas).

3. Conectar a una red (Método Estándar)

Bash
sudo nmcli dev wifi connect "NOMBRE_RED" password "CONTRASEÑA"
4. Conectar a un Hotspot/Móvil (Método Forzado)
Usa este si el paso anterior te da error de seguridad.

Bash
sudo nmcli dev wifi connect "NOMBRE_RED" password "CONTRASEÑA" key-mgmt wpa-psk
5. Verificar la conexión

Bash
hostname -I
(Si aparece una serie de números como 192.168.1.15, tienes internet).

Notas importantes para tu papel:

Mayúsculas: Linux es estricto. "WiFi_Casa" no es lo mismo que "wifi_casa".

Comillas: Usa siempre las comillas " si el nombre de la red o la contraseña tienen espacios.

Olvidar una red: Si quieres borrar una red guardada para volver a intentar desde cero:
sudo nmcli con delete "NOMBRE_RED"