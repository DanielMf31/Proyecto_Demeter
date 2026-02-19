import { steps, nextId, setSteps, setNextId } from "./state.js";
import type { PlannerStep } from "./types/demeter_types.js";

const LS_KEY = "demeter_sequence_v2";
let saveTimer: ReturnType<typeof setTimeout> | null = null;

// DOM badge reference (set from main.ts)
let autosaveBadge: HTMLElement | null = null;

export function initStorage(badge: HTMLElement): void {
    autosaveBadge = badge;
}

export function loadFromStorage(): { steps: PlannerStep[]; nextId: number } | null {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return null;
        const data = JSON.parse(raw) as { steps: PlannerStep[]; nextId: number };
        return data;
    } catch (e) {
        console.warn("Load from storage failed:", e);
        return null;
    }
}

export function persistToStorage(): void {
    if (autosaveBadge) {
        autosaveBadge.classList.remove("saved");
        autosaveBadge.classList.add("saving");
        const textNode = autosaveBadge.childNodes[autosaveBadge.childNodes.length - 1];
        if (textNode) textNode.textContent = " Guardando…";
    }

    if (saveTimer !== null) clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        try {
            localStorage.setItem(LS_KEY, JSON.stringify({ steps, nextId }));
        } catch (e) {
            console.warn("Auto-save failed:", e);
        }
        if (autosaveBadge) {
            autosaveBadge.classList.remove("saving");
            autosaveBadge.classList.add("saved");
            const tn = autosaveBadge.childNodes[autosaveBadge.childNodes.length - 1];
            if (tn) tn.textContent = " Guardado";
        }
    }, 600);
}
