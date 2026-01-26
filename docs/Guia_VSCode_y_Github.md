# Guía: VS Code y Autenticación GitHub en Raspberry Pi

Esta guía responde a tus dudas sobre el entorno de desarrollo y cómo conectar con GitHub de forma segura.

## 1. VS Code en Raspberry Pi

¿Puedes instalarlo? **Sí.**
¿Deberías instalarlo? **Depende.**

### Opción A: VS Code Remote - SSH (¡Muy Recomendada!)
En lugar de instalar VS Code *dentro* de la Raspberry Pi (que consume mucha RAM y CPU), usas el VS Code de tu potente ordenador (PC/Mac) para editar archivos **remotamente** en la Pi.

**Ventajas:**
*   Tu PC hace el trabajo pesado.
*   La interfaz es fluida.
*   Tienes todas tus extensiones y temas.
*   La Raspberry Pi se dedica solo a ejecutar el código.

**Cómo hacerlo:**
1.  En tu VS Code (PC), instala la extensión oficial **"Remote - SSH"** (de Microsoft).
2.  Pulsa `F1` y escribe `Remote-SSH: Connect to Host...`.
3.  Escribe: `usuario@IP_DE_LA_PI` (ej: `pi@192.168.1.50` o `pi@demeter-pi.local`).
4.  Te pedirá la contraseña (la de la Raspberry Pi).
5.  ¡Listo! Se abrirá una ventana nueva. La terminal que ves ahí **es la de la Raspberry Pi**.

### Opción B: Instalar VS Code en el Escritorio de la Pi
Si estás usando la Raspberry Pi con un monitor, teclado y ratón (modo escritorio), puedes instalarlo.
```bash
sudo apt update
sudo apt install code
```
*Nota: Tarda un poco en abrir y puede ir lento en modelos con menos de 4GB de RAM.*

---

## 2. Autenticación en GitHub (Git Pull / Push)

**IMPORTANTE**: GitHub **ya no permite** usar tu contraseña de la cuenta para hacer `git pull` o `push` por HTTPS. Si intentas poner tu contraseña, te dará error de autenticación.

Debes usar uno de estos dos métodos:

### Método 1: SSH Keys (El estándar profesional)
Consiste en crear una llave criptográfica en la RPi y dársela a GitHub. No tendrás que poner contraseñas nunca más.

**Pasos:**

1.  **En la Raspberry Pi**, genera las llaves:
    ```bash
    ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"
    ```
    *Presiona Enter a todo (déjalo vacío para no pedir frase de paso).*

2.  **Lee tu llave pública**:
    ```bash
    cat ~/.ssh/id_ed25519.pub
    ```
    *(Verás un texto largo que empieza por `ssh-ed25519...`). Cópialo.*

3.  **En GitHub.com**:
    *   Ve a **Settings** (arriba a la derecha, en tu foto).
    *   Menú izquierda: **SSH and GPG keys**.
    *   Botón **New SSH key**.
    *   **Title**: Ponle un nombre (ej: "Raspberry Pi Demeter").
    *   **Key**: Pega el texto que copiaste.
    *   Dale a **Add SSH key**.

4.  **Prueba la conexión**:
    En la RPi ejecuta:
    ```bash
    ssh -T git@github.com
    ```
    *Debe decir: "Hi DanielMf31! You've successfully authenticated..."*

5.  **Cambiar tu repo a modo SSH** (si lo clonaste con HTTPS):
    ```bash
    cd ~/Documentos/PlatformIO/Projects/Proyecto_Demeter
    git remote set-url origin git@github.com:DanielMf31/Proyecto_Demeter.git
    ```

### Método 2: GitHub CLI (El método fácil / interactivo)
Si no quieres lidiar con llaves, puedes usar la herramienta oficial `gh`.

1.  **Instalar `gh` en la RPi**:
    *(Esto requiere unos pasos extra de instalación la primera vez, ver documentación oficial de cli.github.com, o podemos añadirlo al script bootstrap).*

2.  **Login**:
    ```bash
    gh auth login
    ```
    *   Te preguntará: `What account do you want to log into?` -> **GitHub.com**
    *   `What is your preferred protocol?` -> **HTTPS**
    *   `Authenticate Git with your GitHub credentials?` -> **Yes**
    *   `How would you like to authenticate?` -> **Login with a web browser**
    *   Te dará un código (ej: 1234-5678).
    *   Abres en tu móvil/PC la web `https://github.com/login/device`.
    *   Metes el código y autorizas.
    
    ¡Listo! `git pull` y `git push` funcionarán automágicamente.

### Resumen
*   **VS Code**: Usa **Remote - SSH** desde tu PC. Es mucho mejor.
*   **GitHub**: No busques tu contraseña, no funcionará. Crea una **SSH Key** (Método 1) y añádela a tu cuenta. Es lo más robusto para cosas automáticas.
