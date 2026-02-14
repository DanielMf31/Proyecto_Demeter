# 🐧 Guía Rápida de Permisos y Grupos en Linux

Esta guía explica cómo ver, entender y modificar permisos de archivos y usuarios en Linux (Raspberry Pi OS / Ubuntu).

---

## 1. Ver Permisos (`ls -l`)
Para ver los permisos de un archivo o carpeta usa `ls -l`.

```bash
ls -l nombre_archivo
```

**Ejemplo de salida:**
```text
-rwxr-xr--  1 montero montero  1024 Feb 15 12:00 archivo.py
```

**Explicación:**
*   **`-`**: Tipo de archivo (`-` = archivo, `d` = directorio).
*   **`rwx` (Dueño)**: Permisos del usuario dueño (`montero`). (Lee, Escribe, Ejecuta).
*   **`r-x` (Grupo)**: Permisos del grupo dueño (`montero`). (Lee, Ejecuta, NO escribe).
*   **`r--` (Otros)**: Permisos para el resto del mundo. (Solo Lee).
*   **`montero` (Dueño)**: Nombre del usuario propietario.
*   **`montero` (Grupo)**: Nombre del grupo propietario.

---

## 2. Modificar Permisos (`chmod`)
Cambia **QUÉ** puede hacer cada quién.

### Modo Simbólico (Letras)
*   **u**: Usuario (Owner)
*   **g**: Grupo
*   **o**: Otros
*   **a**: Todos (All)
*   **+**: Añadir / **-**: Quitar / **=**: Asignar

**Ejemplos:**
```bash
chmod +x archivo.sh       # Hace ejecutable para todos
chmod u+w archivo.txt     # Da permiso de escritura solo al dueño
chmod g+r base_datos.db   # Da permiso de lectura al grupo
chmod o-r secreto.txt     # Quita permiso de lectura a "otros"
```

### Modo Numérico (Octal)
*   **4**: Lectura (r)
*   **2**: Escritura (w)
*   **1**: Ejecución (x)
*   Se suman: 7=rwx, 6=rw, 5=rx, 4=r

**Ejemplos:**
```bash
chmod 777 archivo # Todos hacen todo (PELIGROSO)
chmod 755 script  # Dueño(7)=rwx, Grupo(5)=rx, Otros(5)=rx (Típico para scripts/carpetas)
chmod 644 archivo # Dueño(6)=rw, Grupo(4)=r, Otros(4)=r (Típico para archivos normales)
chmod 600 clave   # Dueño(6)=rw, Nadie más tiene acceso (Para claves privadas)
```

---

## 3. Modificar Propietarios (`chown`)
Cambia **QUIÉN** es el dueño del archivo.

```bash
# Cambiar solo usuario dueño
sudo chown nuevo_dueno archivo

# Cambiar usuario y grupo
sudo chown usuario:grupo archivo

# Cambiar recursivamente (toda la carpeta y subcarpetas)
sudo chown -R usuario:grupo carpeta/
```

---

## 4. Gestión de Grupos (`usermod` / `groups`)

### Ver mis grupos
```bash
groups
# O para ver los de otro usuario
groups grafana
```

### Ver ID numéricos (Usuario y Grupos)
```bash
id
# O
id grafana
```

### Añadir usuario a un grupo
**IMPORTANTE**: Siempre usa `-aG` (Append + Group). Si olvidas la `-a` (Append), ¡borrarás al usuario de todos sus otros grupos!

```bash
# Añade al usuario 'grafana' al grupo 'montero'
sudo usermod -aG montero grafana
```

Luego de añadir un usuario a un grupo, **el usuario debe cerrar sesión o reiniciarse** (o reiniciar su servicio) para que los cambios surtan efecto.

---

## 5. ACLs (Listas de Control de Acceso) - `setfacl`
Permite dar permisos a un usuario específico sin cambiar el dueño ni el grupo principal.

```bash
# Dar permiso de lectura (r) al usuario 'grafana' sobre un archivo
setfacl -m u:grafana:r archivo.db

# Ver las ACLs de un archivo
getfacl archivo.db

# Quitar todas las ACLs
setfacl -b archivo.db
```
*(Requiere instalar el paquete `acl`)*.
