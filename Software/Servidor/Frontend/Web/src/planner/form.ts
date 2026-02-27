import { steps, nextId, saveSnapshot, pushStep, setNextId } from "../state.js";
import { persistToStorage } from "../storage.js";
import { showToast } from "../ui/toast.js";
import type { PlannerStep } from "../types/demeter_types.js";

interface FormElements {
    selPin: HTMLSelectElement;
    selEstado: HTMLSelectElement;
    inpTiempo: HTMLInputElement;
    groupEstado: HTMLElement;
    onStepAdded: () => void; // callback → main.ts calls rebuildTable + syncHistory
}

let formEls: FormElements | null = null;

export function initForm(elements: FormElements): void {
    formEls = elements;
}

export function onPinChange(): void {
    if (!formEls) return;
    const isWait = formEls.selPin.value === "WAIT";
    formEls.groupEstado.style.display = isWait ? "none" : "";
    if (isWait) formEls.selEstado.value = "";
}

export function addStep(): void {
    if (!formEls) return;

    const pin = formEls.selPin.value;
    const estado = formEls.selEstado.value;
    const tiempo = Number(formEls.inpTiempo.value);

    if (!pin) { showToast("Selecciona un pin o pausa.", "error"); return; }

    const isWait = pin === "WAIT";
    if (!isWait && !estado) { showToast("Selecciona el estado (ON/OFF).", "error"); return; }
    if (!tiempo || tiempo < 1) { showToast("Introduce un tiempo válido (≥ 1 ms).", "error"); return; }

    saveSnapshot();

    const step: PlannerStep = {
        id: nextId,
        pin,
        estado: isWait ? "WAIT" : (estado as "ON" | "OFF"),
        tiempo,
    };
    setNextId(nextId + 1);
    pushStep(step);

    formEls.onStepAdded();
    persistToStorage();

    // Reset form
    formEls.selPin.value = "";
    formEls.selEstado.value = "";
    formEls.inpTiempo.value = "";
    onPinChange();

    showToast(
        `Paso ${steps.length} añadido — ${isWait ? "Pausa" : `Pin ${pin} ${estado}`} ${tiempo} ms`,
        "success"
    );
}
