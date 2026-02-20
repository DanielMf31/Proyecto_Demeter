import { useEffect, useState, useRef } from 'react';
import { SensorData } from '../types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export const useTelemetry = (maxRecords: number = 100) => {
    const [data, setData] = useState<SensorData[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // We generate a random client ID for the monitoring dashboard
        const clientId = `web-dashboard-${Math.random().toString(36).substring(7)}`;
        const ws = new WebSocket(`${WS_URL}/${clientId}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WebSocket Connected");
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);

                // Assuming telemetry message format has type: "telemetry" or it's a direct dictionary
                // Adjust based on the actual WS payload from Backend dispatcher.
                // Demeter Protocol usually sends { type: "telemetry", node_id: ..., timestamp: ..., temperature: ..., humidity: ..., valve_state: ... }

                // The backend dispatcher handles formatting. If it's direct DemeterProtocol format:
                if (message.type === "telemetry" || message.temperature !== undefined || message.temperatura !== undefined) {

                    const newRecord: SensorData = {
                        timestamp: message.timestamp || new Date().toISOString(),
                        temperatura: message.temperature ?? message.temperatura ?? 0,
                        humedad: message.humidity ?? message.humedad ?? 0,
                        estado_riego: message.valve_state === 'OPEN' || message.valve_state === true || message.estado_riego
                    };

                    setData(prev => {
                        const updated = [newRecord, ...prev];
                        if (updated.length > maxRecords) {
                            updated.length = maxRecords; // Keep buffer fixed size
                        }
                        return updated;
                    });
                }
            } catch (error) {
                console.error("Error parsing WS telemetry:", error);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket Disconnected");
            setIsConnected(false);
            // Optional: Implement reconnection logic here
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
            setIsConnected(false);
        };

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [maxRecords]);

    return { data, isConnected };
};
