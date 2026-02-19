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
export type ViewType = 'DATAVIZ' | 'MANUAL' | 'PLANNER';

// ─────────────────────────────────────────────────────────────────────────────
// Comandos de Control (Frontend → API → Raspberry)
// ─────────────────────────────────────────────────────────────────────────────

interface DemeterCommandBase {
    target_id: number;
    source_id?: number | null;
}

export interface SetGpio extends DemeterCommandBase {
    type: "set_gpio";
    pin: number;
    value: 0 | 1;
}

export interface SequenceStep {
    target_id?: number;
    pin: number;
    value: 0 | 1;
    delay_ms: number;
}

export interface ExecSequence extends DemeterCommandBase {
    type: "exec_sequence";
    steps: SequenceStep[];
}

export interface PlannerStep {
    id: number;
    pin: string;
    estado: "ON" | "OFF" | "WAIT";
    tiempo: number;
}

export type CommandPayload = SetGpio | ExecSequence | { type: "ping"; target_id: number };

export interface CommandResponse {
    status: "queued" | "error" | "gateway_offline";
    message: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Discovery
// ─────────────────────────────────────────────────────────────────────────────

export interface DeviceConfig {
    target_id: number;
    physical_pin: number;
    label: string;
}

export interface DiscoveryConfig {
    pump?: Record<string, DeviceConfig>;
    valve?: Record<string, DeviceConfig>;
    [key: string]: Record<string, DeviceConfig> | undefined;
}

export interface DiscoveryResponse {
    status: "online" | "pending";
    devices: DiscoveryConfig;
    message?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

export function makeSetGpio(pin: number, value: 0 | 1, target_id = 1): SetGpio {
    return { type: "set_gpio", target_id, pin, value };
}

export function makeExecSequence(steps: PlannerStep[], target_id = 1): ExecSequence {
    const sequenceSteps: SequenceStep[] = steps.map((s) => ({
        target_id,
        pin: s.pin === "WAIT" ? 0 : parseInt(s.pin, 10),
        value: s.estado === "ON" ? 1 : 0,
        delay_ms: s.tiempo,
    }));
    return { type: "exec_sequence", target_id, steps: sequenceSteps };
}

export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
}
