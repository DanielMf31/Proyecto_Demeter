import { postCommand } from "../api.js";
import { showToast } from "../ui/toast.js";
import { makeSetGpio } from "../types/demeter_types.js";

import type { DiscoveryConfig, DeviceConfig } from "../types/demeter_types.js";

// Ya no necesitamos PIN_MAP local, la Raspberry traduce los IDs lógicos (1-8).
// Bombas: 1, 2, 3, 4
// Válvulas: 5, 6, 7, 8 (offset de 4)

type DeviceType = "pump" | "valve";

function isPumpOrValve(s: string): s is DeviceType {
    return s === "pump" || s === "valve";
}

export async function toggleCard(card: HTMLElement): Promise<void> {
    const deviceStr = card.dataset["device"] ?? "";
    const idStr = card.dataset["id"] ?? "";
    if (!isPumpOrValve(deviceStr)) return;

    const isActive = card.getAttribute("aria-pressed") === "true";
    const nextState = !isActive;

    // El ID lógico para la Raspberry es: Pump (1-4), Valve (5-8)
    const idInt = parseInt(idStr, 10);
    const logicalPin = deviceStr === "pump" ? idInt : idInt + 4;

    const cmd = makeSetGpio(logicalPin, nextState ? 1 : 0);
    const res = await postCommand(cmd);
    if (!res) return;  // El toast de error ya lo maneja postCommand

    // Update UI
    card.setAttribute("aria-pressed", String(nextState));
    card.classList.toggle("card-active", nextState);

    const dot = card.querySelector<HTMLElement>(".status-dot-card");
    const label = card.querySelector<HTMLElement>(".card-state-label");
    if (dot) dot.classList.toggle("dot-on", nextState);
    if (label) label.textContent = nextState ? "ON" : "OFF";

    // Update device-row counter
    updateRowCount(card.closest<HTMLElement>(".device-row"));

    // Update global active count
    updateGlobalCount();
}

export function emergencyStop(): void {
    const cards = document.querySelectorAll<HTMLElement>(".control-card[aria-pressed='true']");
    if (cards.length === 0) {
        showToast("Todos los dispositivos ya están apagados.", "info");
        return;
    }

    cards.forEach(card => {
        const deviceStr = card.dataset["device"] ?? "";
        const idStr = card.dataset["id"] ?? "";
        if (!isPumpOrValve(deviceStr)) return;

        const idInt = parseInt(idStr, 10);
        const logicalPin = deviceStr === "pump" ? idInt : idInt + 4;

        const cmd = makeSetGpio(logicalPin, 0);
        postCommand(cmd);


        card.setAttribute("aria-pressed", "false");
        card.classList.remove("card-active");
        const dot = card.querySelector<HTMLElement>(".status-dot-card");
        const label = card.querySelector<HTMLElement>(".card-state-label");
        if (dot) dot.classList.remove("dot-on");
        if (label) label.textContent = "OFF";
    });

    document.querySelectorAll<HTMLElement>(".device-row").forEach(row => updateRowCount(row));
    updateGlobalCount();
    showToast("¡Paro de emergencia activado! Todos los dispositivos apagados.", "error");
}

function updateRowCount(row: HTMLElement | null): void {
    if (!row) return;
    const device = row.dataset["device"] ?? "";
    const total = row.querySelectorAll(".control-card").length;
    const active = row.querySelectorAll(".control-card[aria-pressed='true']").length;
    const counter = row.querySelector<HTMLElement>(".device-row-count");
    if (!counter) return;

    const label = device === "pump" ? "activa" : "abierta";
    counter.textContent = `${active} / ${total} ${label}${active !== 1 ? "s" : ""}`;
}

/**
 * Renderiza dinámicamente las tarjetas de control basándose en la configuración.
 */
export function renderDeviceCards(config: DiscoveryConfig): void {
    const types: DeviceType[] = ["pump", "valve"];

    types.forEach(type => {
        const row = document.querySelector<HTMLElement>(`.device-row[data-device="${type}"]`);
        if (!row) return;

        const grid = row.querySelector(".cards-grid");
        if (!grid) return;

        const devices = config[type];
        if (!devices) {
            grid.innerHTML = '<p class="empty-discovery">No se encontraron dispositivos de este tipo.</p>';
            return;
        }

        grid.innerHTML = ""; // Limpiar hardcoded

        Object.entries(devices).forEach(([id, dev]) => {
            const button = document.createElement("button");
            button.className = "control-card";
            button.dataset["device"] = type;
            button.dataset["id"] = id;
            button.setAttribute("aria-pressed", "false");
            button.setAttribute("aria-label", `${dev.label}, estado OFF`);

            button.innerHTML = `
                <div class="card-icon ${type}" aria-hidden="true">
                    ${getIcon(type)}
                </div>
                <div class="card-body">
                    <span class="card-name">${dev.label}</span>
                    <span class="card-id">ID: ${type === "pump" ? "P" : "V"}-0${id}</span>
                </div>
                <div class="card-status-wrap">
                    <span class="status-dot-card" aria-hidden="true"></span>
                    <span class="card-state-label">OFF</span>
                </div>
            `;

            button.addEventListener("click", () => toggleCard(button));
            grid.appendChild(button);
        });

        updateRowCount(row);
    });

    updateGlobalCount();
}

/**
 * Actualiza el resumen global de dispositivos activos.
 */
function updateGlobalCount(): void {
    const totalActive = document.querySelectorAll(".control-card[aria-pressed='true']").length;
    const label = document.getElementById("manual-summary-label");
    if (!label) return;
    label.textContent = totalActive === 0
        ? "Todo apagado"
        : `${totalActive} dispositivo${totalActive !== 1 ? "s" : ""} activo${totalActive !== 1 ? "s" : ""}`;
}

/**
 * Actualiza el dropdown del planificador con los pines descubiertos.
 */
export function updatePlannerOptions(config: DiscoveryConfig): void {
    const select = document.getElementById("sel-pin") as HTMLSelectElement | null;
    if (!select) return;

    // Guardar opción WAIT
    const waitOption = Array.from(select.options).find(opt => opt.value === "WAIT");
    select.innerHTML = '<option value="">— Pin —</option>';
    if (waitOption) {
        const newWait = document.createElement("option");
        newWait.value = waitOption.value;
        newWait.textContent = waitOption.textContent;
        select.appendChild(newWait);
    }

    const types: DeviceType[] = ["pump", "valve"];
    types.forEach(type => {
        const devices = config[type];
        if (!devices) return;

        Object.entries(devices).forEach(([id, dev]) => {
            const idInt = parseInt(id, 10);
            const logicalPin = type === "pump" ? idInt : idInt + 4;
            const opt = document.createElement("option");
            opt.value = logicalPin.toString();
            opt.textContent = dev.label;
            select.appendChild(opt);
        });
    });
}

function getIcon(type: DeviceType): string {
    if (type === "pump") {
        return `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22a10 10 0 100-20 10 10 0 000 20z" />
                <path d="M12 8v4l3 3" />
            </svg>
        `;
    }
    return `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2v20M2 12h20" />
            <circle cx="12" cy="12" r="4" />
        </svg>
    `;
}

