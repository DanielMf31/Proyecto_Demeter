/**
 * demeter_types.ts — SINCRONIZADO manualmente con schemas.py
 * Source: Software/Common/schemas.py (Pydantic v2 models)
 *
 * El campo `type` es el discriminador canónico para todos los modelos.
 * Es el mismo valor que Pydantic usa en el backend para parsear sin if/elif.
 *
 * Flujo Frontend → Backend:
 *   fetch("POST /api/command", body: AnyDemeterCommand)
 *   → Backend valida con TypeAdapter(AnyDemeterCommand)
 *   → Publica en Redis → Listener reenvía a Raspberry WS
 */


// ─────────────────────────────────────────────────────────────────────────────
// Enum de Command IDs (constante de protocolo binario, solo para referencia)
// El Frontend NO necesita enviar cmd_id; solo el campo `type`.
// ─────────────────────────────────────────────────────────────────────────────
export const CmdId = {
  PING: 0x01,
  ACK: 0x02,
  NACK: 0x03,
  SYN: 0x04,
  SYN_ACK: 0x05,
  ROUTE_ADD: 0x0a,
  TEMP_HUM_REPORT: 0x0b,
  PIN_REPORT: 0x0c,
  SYSTEM_REPORT: 0x0d,
  SET_GPIO: 0x10,
  SET_PWM: 0x11,
  GET_SENSORS: 0x20,
  EXEC_SEQUENCE: 0x30,
} as const;
export type CmdId = typeof CmdId[keyof typeof CmdId];


// ─────────────────────────────────────────────────────────────────────────────
// Base — campos comunes a todos los comandos
// ─────────────────────────────────────────────────────────────────────────────
interface DemeterCommandBase {
  target_id: number;
  source_id?: number | null;
}


// ─────────────────────────────────────────────────────────────────────────────
// Comandos de Control (Frontend → API → Raspberry)
// Todos llevan el campo `type` como discriminador literal.
// ─────────────────────────────────────────────────────────────────────────────

export interface SetGpio extends DemeterCommandBase {
  type: "set_gpio";
  pin: number;    // 0–40
  value: 0 | 1;  // 0 = OFF, 1 = ON
  flags?: number; // opcional, default 0
}

export interface SetPwm extends DemeterCommandBase {
  type: "set_pwm";
  pin: number;   // 0–40
  value: number; // 0–65535
}

export interface ExecSequence extends DemeterCommandBase {
  type: "exec_sequence";
  steps: SequenceStep[];
}

export interface SequenceStep {
  target_id?: number;
  cmd_id?: number;
  pin: number;
  value: 0 | 1;
  delay_ms: number;
}

export interface Ping extends DemeterCommandBase {
  type: "ping";
}

export interface GetSensors extends DemeterCommandBase {
  type: "get_sensors";
}

// Comandos de protocolo interno (raramente enviados desde Frontend)
export interface Ack extends DemeterCommandBase {
  type: "ack";
  original_cmd_id: number;
}

export interface Nack extends DemeterCommandBase {
  type: "nack";
  original_cmd_id: number;
  error_code: number;
}


// ─────────────────────────────────────────────────────────────────────────────
// Union discriminada — el tipo que envías al endpoint POST /api/command
//
// Uso en el Frontend:
//   const cmd: CommandPayload = { type: "set_gpio", target_id: 1, pin: 4, value: 1 };
//   await fetch("/api/command", { method: "POST", body: JSON.stringify(cmd), ... });
// ─────────────────────────────────────────────────────────────────────────────
// --- Discovery & Planning ---

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

export type CommandPayload =
  | SetGpio
  | SetPwm
  | ExecSequence
  | Ping
  | GetSensors;


// ─────────────────────────────────────────────────────────────────────────────
// Respuesta del endpoint POST /api/command
// ─────────────────────────────────────────────────────────────────────────────
export interface CommandResponse {
  status: "queued" | "error" | "gateway_offline";
  message: string;
  /** Tipo del comando que se procesó, para logging en el frontend */
  command_type?: string;
}


// ─────────────────────────────────────────────────────────────────────────────
// Reports — mensajes que llegan DESDE la Raspberry (via WebSocket o SSE futura)
// ─────────────────────────────────────────────────────────────────────────────

export interface TempHumReport extends DemeterCommandBase {
  type: "temp_hum_report";
  node_id: number;
  temperature: number;
  humidity: number;
  timestamp?: number;
}

export interface PinReport extends DemeterCommandBase {
  type: "pin_report";
  node_id: number;
  pin: number;
  state: 0 | 1;
}

export interface SystemReport extends DemeterCommandBase {
  type: "system_report";
  node_id: number;
  mode: number;
  battery_mv: number;
  reserved?: string;
}

export type GatewayReport = TempHumReport | PinReport | SystemReport;


// ─────────────────────────────────────────────────────────────────────────────
// WebSocket — sigue activo SOLO para la Raspberry (backend↔gateway)
// El Frontend ya NO necesita WS para enviar comandos.
// Puede seguir usándolo en el futuro para recibir telemetría en tiempo real.
// ─────────────────────────────────────────────────────────────────────────────

/** Mensajes que el Backend puede empujar al Frontend via WS (telemetría futura) */
export interface WsTelemetry {
  type: "telemetry";
  sensor: "temp_hum" | "pin" | "system";
  data: TempHumReport | PinReport | SystemReport;
}

export interface WsDispatcherStatus {
  type: "dispatcher_status";
  status: "gateway_offline" | "gateway_online";
  message: string;
}

export interface WsSystemConfig {
  type: "system_config";
  devices: DiscoveryConfig;
}

export interface WsInfoMessage {
  type: "info";
  message: string;
}

export interface WsGatewayAck {
  type: "ack" | "nack";
  original_cmd_id?: number;
  error_code?: number;
}

export type WsIncomingMessage =
  | WsTelemetry
  | WsDispatcherStatus
  | WsSystemConfig
  | WsInfoMessage
  | WsGatewayAck;


// ─────────────────────────────────────────────────────────────────────────────
// Tipos de UI — específicos del Frontend, no relacionados con el protocolo
// ─────────────────────────────────────────────────────────────────────────────

/** Un paso en el planificador de secuencias (antes de serializar a ExecSequence) */
export interface PlannerStep {
  id: number;
  pin: string;      // "1" | "2" | "3" | "4" | "WAIT"
  estado: "ON" | "OFF" | "WAIT";
  tiempo: number;   // milisegundos
}

/** Helper: construye un SetGpio desde la UI de Control Manual */
export function makeSetGpio(pin: number, value: 0 | 1, target_id = 1): SetGpio {
  return { type: "set_gpio", target_id, pin, value };
}

/** Helper: construye un ExecSequence desde los pasos del planificador */
export function makeExecSequence(steps: PlannerStep[], target_id = 1): ExecSequence {
  const sequenceSteps: SequenceStep[] = steps.map((s) => ({
    target_id,
    pin: s.pin === "WAIT" ? 0 : parseInt(s.pin, 10),
    value: s.estado === "ON" ? 1 : 0,
    delay_ms: s.tiempo,
  }));
  return { type: "exec_sequence", target_id, steps: sequenceSteps };
}
