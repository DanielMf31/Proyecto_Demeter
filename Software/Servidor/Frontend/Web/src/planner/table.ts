import { steps, nextId, saveSnapshot, setSteps, setNextId } from "../state.js";
import { persistToStorage } from "../storage.js";
import { showToast } from "../ui/toast.js";
import type { PlannerStep } from "../types/demeter_types.js";

// DOM references (set from main.ts via initTable)
let tableBody: HTMLElement | null = null;
let tableScroll: HTMLElement | null = null;
let emptyState: HTMLElement | null = null;
let rowCountEl: HTMLElement | null = null;
let bulkBar: HTMLElement | null = null;
let bulkInfo: HTMLElement | null = null;
let chkAll: HTMLInputElement | null = null;

// Callback injected from main.ts so timeline can be updated without circular import
let afterRender: (() => void) | null = null;

interface TableElements {
    tableBody: HTMLElement;
    tableScroll: HTMLElement;
    emptyState: HTMLElement;
    rowCount: HTMLElement;
    bulkBar: HTMLElement;
    bulkInfo: HTMLElement;
    chkAll: HTMLInputElement;
    onAfterRender: () => void; // called after every rebuild → main.ts calls renderTimeline()
}

export function initTable(els: TableElements): void {
    tableBody = els.tableBody;
    tableScroll = els.tableScroll;
    emptyState = els.emptyState;
    rowCountEl = els.rowCount;
    bulkBar = els.bulkBar;
    bulkInfo = els.bulkInfo;
    chkAll = els.chkAll;
    afterRender = els.onAfterRender;
}

// ── Row builder ──────────────────────────────────────────────────────────────
export function buildRow(step: PlannerStep, index: number): HTMLTableRowElement {
    const isWait = step.pin === "WAIT";
    const tr = document.createElement("tr");
    tr.dataset["id"] = String(step.id);
    tr.draggable = true;

    const badgeClass = isWait ? "badge-wait" : step.estado === "ON" ? "badge-on" : "badge-off";
    const badgeText = isWait ? "WAIT" : step.estado;
    const pinText = isWait ? "⏸ Pausa" : `Pin ${step.pin}`;

    tr.innerHTML = `
    <td class="col-drag" aria-label="Arrastrar para reordenar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
    </td>
    <td class="col-check">
      <label class="checkbox-wrap" aria-label="Seleccionar paso ${index + 1}">
        <input type="checkbox" class="row-chk" aria-label="Seleccionar paso ${index + 1}"/>
        <span class="checkmark" aria-hidden="true"></span>
      </label>
    </td>
    <td class="col-num">${index + 1}</td>
    <td>${pinText}</td>
    <td><span class="badge ${badgeClass}">${badgeText}</span></td>
    <td>${step.tiempo} ms</td>
    <td class="col-actions">
      <button class="btn-icon btn-delete" data-action="delete" aria-label="Eliminar paso ${index + 1}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6M9 6V4h6v2"/></svg>
      </button>
      <button class="btn-icon btn-duplicate" data-action="duplicate" aria-label="Duplicar paso ${index + 1}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      </button>
    </td>`;

    // Drag & drop
    let dragSrcIndex: number | null = null;
    tr.addEventListener("dragstart", () => { dragSrcIndex = getRowIndex(tr); tr.classList.add("dragging"); });
    tr.addEventListener("dragend", () => tr.classList.remove("dragging"));
    tr.addEventListener("dragover", (e) => { e.preventDefault(); tr.classList.add("drag-over"); });
    tr.addEventListener("dragleave", () => tr.classList.remove("drag-over"));
    tr.addEventListener("drop", (e) => {
        e.preventDefault();
        tr.classList.remove("drag-over");
        const targetIndex = getRowIndex(tr);
        if (dragSrcIndex === null || dragSrcIndex === targetIndex) return;
        saveSnapshot();
        const [moved] = steps.splice(dragSrcIndex, 1);
        if (moved) steps.splice(targetIndex, 0, moved);
        rebuildTable();
        persistToStorage();
        showToast("Orden actualizado.", "success");
    });

    tr.querySelector<HTMLInputElement>(".row-chk")?.addEventListener("change", () => {
        syncSelectAll();
        updateBulkBar();
    });

    return tr;
}

function getRowIndex(tr: HTMLTableRowElement): number {
    return Array.from(tableBody?.querySelectorAll("tr") ?? []).indexOf(tr);
}

// ── Rebuild table ────────────────────────────────────────────────────────────
export function rebuildTable(): void {
    if (!tableBody) return;
    tableBody.innerHTML = "";
    steps.forEach((s, i) => tableBody!.appendChild(buildRow(s, i)));
    updateView();
}

// ── View state ───────────────────────────────────────────────────────────────
export function updateView(): void {
    const hasItems = steps.length > 0;
    if (emptyState) emptyState.style.display = hasItems ? "none" : "";
    if (tableScroll) tableScroll.style.display = hasItems ? "" : "none";
    if (rowCountEl) rowCountEl.textContent = `${steps.length} paso${steps.length !== 1 ? "s" : ""}`;
    afterRender?.();
}

// ── Bulk selection ───────────────────────────────────────────────────────────
function getSelectedIds(): number[] {
    return Array.from(tableBody?.querySelectorAll<HTMLInputElement>(".row-chk:checked") ?? [])
        .map(cb => Number(cb.closest("tr")?.dataset["id"]));
}

function syncSelectAll(): void {
    if (!chkAll || !tableBody) return;
    const all = tableBody.querySelectorAll<HTMLInputElement>(".row-chk");
    const checked = tableBody.querySelectorAll<HTMLInputElement>(".row-chk:checked");
    chkAll.checked = all.length > 0 && all.length === checked.length;
    chkAll.indeterminate = checked.length > 0 && checked.length < all.length;
}

function updateBulkBar(): void {
    if (!bulkBar || !bulkInfo) return;
    const ids = getSelectedIds();
    bulkBar.hidden = ids.length === 0;
    bulkInfo.textContent = `${ids.length} seleccionado${ids.length !== 1 ? "s" : ""}`;
}

export function toggleSelectAll(checked: boolean): void {
    tableBody?.querySelectorAll<HTMLInputElement>(".row-chk").forEach(cb => (cb.checked = checked));
    updateBulkBar();
}

export function bulkDelete(): void {
    const ids = getSelectedIds();
    if (ids.length === 0) return;
    saveSnapshot();
    setSteps(steps.filter(s => !ids.includes(s.id)));
    if (chkAll) chkAll.checked = false;
    rebuildTable();
    persistToStorage();
    showToast(`${ids.length} paso${ids.length > 1 ? "s" : ""} eliminado${ids.length > 1 ? "s" : ""}.`, "success");
}

// ── Table action handler ─────────────────────────────────────────────────────
export function handleTableAction(target: HTMLElement): void {
    const btn = target.closest<HTMLButtonElement>("[data-action]");
    if (!btn) return;
    const tr = btn.closest<HTMLTableRowElement>("tr");
    if (!tr) return;
    const id = Number(tr.dataset["id"]);
    const idx = steps.findIndex(s => s.id === id);
    if (idx === -1) return;

    if (btn.dataset["action"] === "delete") {
        saveSnapshot();
        steps.splice(idx, 1);
        rebuildTable();
        persistToStorage();
        showToast("Paso eliminado.", "success");
    } else if (btn.dataset["action"] === "duplicate") {
        saveSnapshot();
        const orig = steps[idx]!;
        const copy: PlannerStep = { ...orig, id: nextId };
        setNextId(nextId + 1);
        steps.splice(idx + 1, 0, copy);
        rebuildTable();
        persistToStorage();
        showToast("Paso duplicado.", "success");
    }
}
