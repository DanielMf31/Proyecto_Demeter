import type { CommandPayload, CommandResponse, DiscoveryResponse } from "./types/demeter_types.js";
import { showToast } from "./ui/toast.js";

const API_BASE = `${location.protocol}//${location.host}/api`;

/**
 * Centralized API service for sending commands to the Demeter system.
 */
export async function postCommand(cmd: CommandPayload): Promise<CommandResponse | null> {
    try {
        const response = await fetch(`${API_BASE}/command`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(cmd),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMsg = errorData.detail || `Error del servidor (${response.status})`;
            showToast(`Error: ${errorMsg}`, "error");
            return null;
        }

        const data = await response.json() as CommandResponse;

        if (data.status === "gateway_offline") {
            showToast(data.message, "info");
        } else if (data.status === "error") {
            showToast(data.message, "error");
        }

        return data;
    } catch (error) {
        console.error("API Error:", error);
        showToast("No se pudo contactar con el servidor. Revisa tu conexión.", "error");
        return null;
    }
}

/**
 * Recupera la lista de dispositivos configurados en la Raspberry.
 */
export async function fetchDevices(): Promise<DiscoveryResponse | null> {
    try {
        const response = await fetch(`${API_BASE}/devices`);
        if (!response.ok) {
            console.error("Error fetching devices:", response.status);
            return null;
        }
        return await response.json() as DiscoveryResponse;
    } catch (error) {
        console.error("Discovery API Error:", error);
        return null;
    }
}
