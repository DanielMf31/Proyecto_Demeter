# 🔐 Granting Grafana Access to Demeter Data

Grafana runs as a dedicated user (`grafana`), while the Demeter backend runs as your user (`danielmf31`). By default, Grafana cannot read the `demeter_data.db` file created by your user.

To fix this securely **without opening your files to everyone**, we will use a **Linux Group**.

## 📋 The Plan

1.  **Create a Group**: Create a new group called `demeter_readers`.
2.  **Add Users**: Add both `grafana` and your user (`danielmf31`) to this group.
3.  **Set Permissions**: Change the group ownership of the `Python/data` directory and grant "Read" access to the group.
4.  **Future-Proofing**: Set the `setgid` bit so new files created in that folder automatically inherit the group.

## 🚀 Execution Steps

Run the following commands in your terminal:

```bash
# 1. Create the shared group
sudo groupadd demeter_readers

# 2. Add the 'grafana' service user to the group
sudo usermod -a -G demeter_readers grafana

# 3. Add YOURSELF to the group (so you can still write to it!)
sudo usermod -a -G demeter_readers $USER

# 4. Change group ownership of the data directory
# Replace with the absolute path to your project's data folder
PROJECT_DATA_DIR="/home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/Python/data"

chgrp -R demeter_readers "$PROJECT_DATA_DIR"

# 5. Grant Group Read/Execute permissions (g+rX)
# r = Read files
# X = Enter directories (needed to reach the file)
chmod -R g+rX "$PROJECT_DATA_DIR"

# 6. (Critical) Ensure future files (like db-wal) are also readable
# The 's' (setgid) ensures files created inside inherit 'demeter_readers' group
chmod g+s "$PROJECT_DATA_DIR"
```

## 🔄 Finalize

After running the commands, you **must restart Grafana** for it to pick up the new group membership:

```bash
sudo systemctl restart grafana-server
```

## ⚠️ Security Note

*   **Least Privilege**: This method only grants access to this specific folder.
*   **Safety**: Using a specific group (`demeter_readers`) is safer than giving access to `www-data` or using `chmod 777` (which allows anyone to delete your data).
