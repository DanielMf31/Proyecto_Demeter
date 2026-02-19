#!/usr/bin/env python3
"""
generate_types.py
Genera demeter_types.ts desde schemas.py usando Pydantic v2 model_json_schema().
Uso: python3 scripts/generate_types.py
"""

import sys
import json
from pathlib import Path

# Añadir Common al path para poder importar schemas
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "Software" / "Common"))

from schemas import (
    CmdId, DemeterCommand, Ping, Ack, Nack, Syn, SynAck,
    SetGpio, SetPwm, GetSensors, RouteAdd,
    SequenceStep, ExecSequence,
    TempHumReport, PinReport, SystemReport,
)

OUTPUT_PATH = REPO_ROOT / "Software" / "Servidor" / "Frontend" / "Web" / "src" / "types" / "demeter_types.ts"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pydantic_type_to_ts(py_type: str) -> str:
    mapping = {
        "integer": "number",
        "number": "number",
        "string": "string",
        "boolean": "boolean",
        "array": "unknown[]",
        "object": "Record<string, unknown>",
        "null": "null",
    }
    return mapping.get(py_type, "unknown")


def model_to_interface(model_cls, extra_fields: dict[str, str] | None = None) -> str:
    """Convert a Pydantic model class to a TypeScript interface string."""
    schema = model_cls.model_json_schema()
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    lines = [f"export interface {model_cls.__name__} {{"]

    for field_name, field_info in props.items():
        optional = "" if field_name in required else "?"
        # Resolve $ref if present
        if "$ref" in field_info:
            ref_name = field_info["$ref"].split("/")[-1]
            ts_type = ref_name
        elif "anyOf" in field_info:
            # Usually Optional[X] → [X, null]
            inner = [
                pydantic_type_to_ts(t.get("type", "unknown"))
                for t in field_info["anyOf"]
                if t.get("type") != "null"
            ]
            ts_type = " | ".join(inner) + " | null"
            optional = "?"
        elif field_info.get("type") == "array":
            items = field_info.get("items", {})
            if "$ref" in items:
                item_type = items["$ref"].split("/")[-1]
            else:
                item_type = pydantic_type_to_ts(items.get("type", "unknown"))
            ts_type = f"{item_type}[]"
        elif field_info.get("type") == "string" and "format" in field_info:
            # bytes fields → string (base64 in JSON)
            ts_type = "string"
        else:
            ts_type = pydantic_type_to_ts(field_info.get("type", "unknown"))

        lines.append(f"  {field_name}{optional}: {ts_type};")

    # Extra manually-specified fields
    if extra_fields:
        for fname, ftype in extra_fields.items():
            lines.append(f"  {fname}: {ftype};")

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main generation
# ---------------------------------------------------------------------------

def generate() -> str:
    sections: list[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    sections.append("""\
/**
 * demeter_types.ts — AUTO-GENERATED
 * Source: Software/Common/schemas.py (Pydantic v2 models)
 * Script:  scripts/generate_types.py
 *
 * DO NOT EDIT MANUALLY. Run `npm run gen:types` to regenerate.
 */
""")

    # ── CmdId enum ──────────────────────────────────────────────────────────
    cmd_id_lines = ["export const CmdId = {"]
    for member in CmdId:
        cmd_id_lines.append(f"  {member.name}: {member.value:#04x},  // {member.value}")
    cmd_id_lines.append("} as const;")
    cmd_id_lines.append("export type CmdId = typeof CmdId[keyof typeof CmdId];")
    sections.append("\n".join(cmd_id_lines))

    # ── Pydantic models → TS interfaces ─────────────────────────────────────
    models = [
        DemeterCommand,
        Ping, Ack, Nack, Syn, SynAck,
        SetGpio, SetPwm, GetSensors,
        SequenceStep, ExecSequence,
        TempHumReport, PinReport, SystemReport,
    ]

    for model in models:
        sections.append(model_to_interface(model))

    # ── WebSocket message discriminated unions ───────────────────────────────
    ws_outgoing = """\
// ── WebSocket outgoing messages (Frontend → Backend) ──────────────────────

export interface WsGpioCmd {
  type: "GPIO_CMD";
  target_id: number;
  pin: number;
  action: "ON" | "OFF";
}

export interface WsSequenceConfig {
  type: "sequence_config";
  sequence: Array<{
    pin: string | "WAIT";
    estado: "ON" | "OFF" | "WAIT";
    tiempo: number;
  }>;
}

export interface WsPing {
  type: "command";
  command: "PING";
  params: { target_id: number };
}

export type WsOutgoingMessage = WsGpioCmd | WsSequenceConfig | WsPing;"""

    ws_incoming = """\
// ── WebSocket incoming messages (Backend → Frontend) ──────────────────────

export interface WsAck {
  type: "ack";
  original_cmd_id: number;
  target_id: number;
}

export interface WsNack {
  type: "nack";
  original_cmd_id: number;
  error_code: number;
  target_id: number;
}

export interface WsTempHumReport {
  type: "temp_hum_report";
  node_id: number;
  temperature: number;
  humidity: number;
  timestamp: number;
}

export interface WsPinReport {
  type: "pin_report";
  node_id: number;
  pin: number;
  state: 0 | 1;
}

export interface WsSystemReport {
  type: "system_report";
  node_id: number;
  mode: number;
  battery_mv: number;
}

export interface WsPong {
  type: "pong";
}

export type WsIncomingMessage =
  | WsAck
  | WsNack
  | WsTempHumReport
  | WsPinReport
  | WsSystemReport
  | WsPong;"""

    sections.append(ws_outgoing)
    sections.append(ws_incoming)

    # ── Planner step type (used by frontend state) ───────────────────────────
    planner_step = """\
// ── Frontend-specific types ────────────────────────────────────────────────

/** A step in the sequence planner (before serialization to ExecSequence) */
export interface PlannerStep {
  id: number;
  pin: string; // "1" | "2" | "3" | "4" | "WAIT"
  estado: "ON" | "OFF" | "WAIT";
  tiempo: number; // milliseconds
}"""
    sections.append(planner_step)

    return "\n\n".join(sections) + "\n"


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"✅  Generated: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"    Lines: {len(content.splitlines())}")
