/**
 * main.ts — Entry point for esbuild bundle.
 * Initializes all modules, wires DOM references and event listeners.
 */

// Core
import { steps, setSteps, setNextId, undo, redo, canUndo, canRedo } from "./state.js";
import { initStorage, loadFromStorage, persistToStorage } from "./storage.js";
import { connectWebSocket, setMessageHandler } from "./websocket.js";
import { fetchDevices, postCommand } from "./api.js"; // Added fetchDevices and postCommand

// UI
import { showToast } from "./ui/toast.js";
import { initClock } from "./ui/clock.js";
import { initTheme, toggleTheme } from "./ui/theme.js";
import { initNavigation, switchView } from "./ui/navigation.js";

// Planner
import { initForm, addStep, onPinChange } from "./planner/form.js";
import {
    initTable, rebuildTable, updateView,
    toggleSelectAll, bulkDelete, handleTableAction,
} from "./planner/table.js";
import { initCta, updateCta, sendConfiguration } from "./planner/cta.js";
import { renderTimeline, initTimeline } from "./planner/timeline.js";
import { initSimulation, toggleSimulation } from "./planner/simulation.js";

// Manual
import { toggleCard, emergencyStop, renderDeviceCards, updatePlannerOptions } from "./manual/cards.js";

// Types
import type { WsIncomingMessage } from "./types/demeter_types.js";

// ── DOM References ───────────────────────────────────────────────────────────

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

const clockEl = $("clock");
const btnTheme = $("btn-theme");
const navPlanner = $("nav-planner");
const navManual = $("nav-manual");
const viewPlanner = $("view-planner");
const viewManual = $("view-manual");
const historyControls = document.querySelector<HTMLElement>(".history-controls")!;
const autosaveBadge = $("autosave-badge");
const btnUndo = $<HTMLButtonElement>("btn-undo");
const btnRedo = $<HTMLButtonElement>("btn-redo");

const selPin = $<HTMLSelectElement>("sel-pin");
const selEstado = $<HTMLSelectElement>("sel-estado");
const inpTiempo = $<HTMLInputElement>("inp-tiempo");
const groupEstado = $("group-estado");
const btnAdd = $<HTMLButtonElement>("btn-add");

const tableBody = $("table-body");
const tableScroll = $("table-scroll");
const emptyState = $("empty-state");
const rowCount = $("row-count");
const bulkBar = $<HTMLElement>("bulk-bar");
const bulkInfo = $("bulk-info");
const chkAll = $<HTMLInputElement>("chk-all");
const btnBulkDelete = $<HTMLButtonElement>("btn-bulk-delete");

const timelineTrack = $("timeline-track");
const timelineEmpty = $("timeline-empty");
const totalTimeBadge = $("total-time-badge");
const btnPlay = $<HTMLButtonElement>("btn-play");
const simProgressWrap = $("sim-progress-wrap");
const simProgressBar = $("sim-progress-bar");
const simLabel = btnPlay.querySelector<HTMLElement>(".sim-label")!;
const iconPlayEl = btnPlay.querySelector<SVGElement>(".icon-play")!;
const iconStopEl = btnPlay.querySelector<SVGElement>(".icon-stop")!;

const btnCta = $<HTMLButtonElement>("btn-cta");
const ctaHint = $("cta-hint");
const ctaLoading = btnCta.querySelector<HTMLElement>(".btn-cta-loading")!;
const ctaInner = btnCta.querySelector<HTMLElement>(".btn-cta-inner")!;

const btnEmergency = $<HTMLButtonElement>("btn-emergency");

// ── Initialize Modules ───────────────────────────────────────────────────────

initTheme();

initClock(clockEl);

initNavigation({ viewPlanner, viewManual, navPlanner, navManual, historyControls, autosaveBadge });

initStorage(autosaveBadge);

initForm({ selPin, selEstado, inpTiempo, groupEstado, onStepAdded: () => { rebuildTable(); syncHistoryButtons(); } });

initTable({ tableBody, tableScroll, emptyState, rowCount, bulkBar, bulkInfo, chkAll, onAfterRender: renderTimeline });

initTimeline({ track: timelineTrack, empty: timelineEmpty, totalTimeBadge, btnPlay });

initSimulation({
    btnPlay, btnPlayLabel: simLabel, iconPlay: iconPlayEl, iconStop: iconStopEl,
    simProgressWrap, simProgressBar,
});

initCta({ btnCta, ctaHint, ctaLoading, ctaInner });

// ── Load persisted state ─────────────────────────────────────────────────────
const stored = loadFromStorage();
if (stored) {
    setSteps(stored.steps);
    setNextId(stored.nextId);
    rebuildTable();
}
updateView();
updateCta();

// ── Sync undo/redo button states ─────────────────────────────────────────────
function syncHistoryButtons(): void {
    btnUndo.disabled = !canUndo();
    btnRedo.disabled = !canRedo();
    updateCta();
}
syncHistoryButtons();

// ── Event Listeners ──────────────────────────────────────────────────────────

// Theme
btnTheme.addEventListener("click", toggleTheme);

// Navigation tabs
navPlanner.addEventListener("click", () => switchView("planner"));
navManual.addEventListener("click", () => switchView("manual"));

// Planner form
selPin.addEventListener("change", onPinChange);
btnAdd.addEventListener("click", () => { addStep(); syncHistoryButtons(); });

// Undo / Redo
btnUndo.addEventListener("click", () => {
    const newSteps = undo();
    if (newSteps) { rebuildTable(); persistToStorage(); }
    syncHistoryButtons();
    showToast("Acción deshecha.", "info");
});
btnRedo.addEventListener("click", () => {
    const newSteps = redo();
    if (newSteps) { rebuildTable(); persistToStorage(); }
    syncHistoryButtons();
    showToast("Acción rehecha.", "info");
});

// Keyboard shortcuts
document.addEventListener("keydown", (e: KeyboardEvent) => {
    if (e.ctrlKey && e.key === "z" && !e.shiftKey) {
        e.preventDefault();
        btnUndo.click();
    } else if ((e.ctrlKey && e.key === "y") || (e.ctrlKey && e.shiftKey && e.key === "z")) {
        e.preventDefault();
        btnRedo.click();
    }
});

// Table: action delegation (delete / duplicate)
tableBody.addEventListener("click", (e) => {
    handleTableAction(e.target as HTMLElement);
    syncHistoryButtons();
});

// Bulk actions
chkAll.addEventListener("change", () => toggleSelectAll(chkAll.checked));
btnBulkDelete.addEventListener("click", () => { bulkDelete(); syncHistoryButtons(); });

// Simulation
btnPlay.addEventListener("click", toggleSimulation);

// CTA
btnCta.addEventListener("click", sendConfiguration);

// ── Auto-Discovery ───────────────────────────────────────────────────────────
async function performDiscovery() {
    console.log("Starting hardware discovery...");
    const res = await fetchDevices();
    if (res && res.status === "online") {
        console.log("Devices discovered:", res.devices);
        renderDeviceCards(res.devices);
        updatePlannerOptions(res.devices);
    } else {
        console.log("Discovery pending: Raspberry not reported yet.");
        // We will wait for the system_config message via WS
    }
}

performDiscovery();

// ── WebSocket ────────────────────────────────────────────────────────────────
setMessageHandler((msg: WsIncomingMessage) => {
    switch (msg.type) {
        case "ack":
        case "nack":
            if (msg.type === "ack") showToast("Comando confirmado por el servidor.", "success");
            else showToast(`Error del servidor (código ${msg.error_code}).`, "error");
            break;
        case "system_config":
            console.log("Real-time discovery update:", msg.devices);
            renderDeviceCards(msg.devices);
            updatePlannerOptions(msg.devices);
            showToast("Hardware configurado (Auto-Discovery).", "success");
            break;
        case "info":
            showToast(msg.message, "info");
            break;
        default:
            console.log("WS message:", msg);
    }
});

connectWebSocket();
