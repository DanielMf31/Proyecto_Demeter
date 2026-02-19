import type { WsIncomingMessage } from "./types/demeter_types.js";
import { showToast } from "./ui/toast.js";

/**
 * websocket.ts — Canal de telemetría y estado.
 * 
 * En el nuevo refactor, este socket es de SOLO LECTURA para el frontend.
 * Se utiliza para recibir:
 *  - Telemetría en tiempo real (temp, humedad, estados de pines).
 *  - Confirmaciones (ACK/NACK) de comandos enviados por HTTP.
 *  - Estado de conexión del Gateway (Raspberry).
 */

let socket: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/frontend`;

type MessageHandler = (msg: WsIncomingMessage) => void;
let onMessageHandler: MessageHandler | null = null;

export function setMessageHandler(handler: MessageHandler): void {
    onMessageHandler = handler;
}

export function connectWebSocket(): void {
    if (socket && socket.readyState === WebSocket.OPEN) return;

    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        showToast("Conectado al servidor (Monitor de Telemetría).", "success");
        if (reconnectTimer !== null) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
    };

    socket.onclose = () => {
        showToast("Conexión de telemetría perdida. Reconectando…", "info");
        reconnectTimer = setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error("WebSocket telemetry error:", err);
    };

    socket.onmessage = (event: MessageEvent<string>) => {
        try {
            const msg = JSON.parse(event.data) as WsIncomingMessage;
            onMessageHandler?.(msg);
        } catch (e) {
            console.warn("Invalid WS telemetry message:", event.data);
        }
    };
}

export function isConnected(): boolean {
    return socket !== null && socket.readyState === WebSocket.OPEN;
}
