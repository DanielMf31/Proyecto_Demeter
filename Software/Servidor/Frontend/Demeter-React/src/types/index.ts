export interface SensorData {
    timestamp: string;
    temperatura: number;
    humedad: number;
    estado_riego: boolean;
}

export interface ExperimentSummary {
    id: string;
    nombre: string;
    fecha_inicio: string;
    alertas_activas: number;
}

export type MetricType = 'temperatura' | 'humedad';

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
}
