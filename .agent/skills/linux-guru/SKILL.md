---
name: linux-guru
description: Advanced Linux system administration, bash scripting, and service management for embedded Linux environments (Raspberry Pi OS / Ubuntu).
---

# Linux Guru

This skill empowers you to manage the Linux operating system effectively, crucial for setting up headless IoT gateways.

## Core Capabilities

1.  **Systemd Services:** Creating, enabling, and debugging background services.
2.  **Permissions & Users:** Handling `dialout` (Serial) and `gpio` groups correctly.
3.  **Networking:** Static IPs, SSH config, firewall (UFW).
4.  **Bash Scripting:** Automating deployment and maintenance.

## Essential Commands

-   `journalctl -u service_name -f`: Follow logs for a specific service.
-   `systemctl status/start/stop/restart service_name`: Manage services.
-   `htop`, `iotop`: Monitor System Resources.
-   `ls -l /dev/serial/by-id/`: Robustly identify USB Serial devices.

## Creating a Systemd Service

Create `/etc/systemd/system/demeter.service`:

```ini
[Unit]
Description=Demeter Async Backend Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/project/main_async.py
WorkingDirectory=/path/to/project
User=pi
Group=pi
Restart=always
RestartSec=5
Environment=DEMETER_PORT=/dev/ttyUSB0

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable demeter.service
sudo systemctl start demeter.service
```

## udev Rules (Stable Device Names)

Create `/etc/udev/rules.d/99-demeter.rules`:
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="ttyDemeter"
```
Now use `/dev/ttyDemeter` instead of `/dev/ttyUSB0`.
