import { steps } from "../state.js";
import { postCommand } from "../api.js";
import { showToast } from "../ui/toast.js";
import { makeExecSequence } from "../types/demeter_types.js";

let btnCta: HTMLButtonElement | null = null;
let ctaHint: HTMLElement | null = null;
let ctaLoading: HTMLElement | null = null;
let ctaInner: HTMLElement | null = null;

interface CtaElements {
    btnCta: HTMLButtonElement;
    ctaHint: HTMLElement;
    ctaLoading: HTMLElement;
    ctaInner: HTMLElement;
}

export function initCta(els: CtaElements): void {
    btnCta = els.btnCta;
    ctaHint = els.ctaHint;
    ctaLoading = els.ctaLoading;
    ctaInner = els.ctaInner;
}

export function updateCta(): void {
    if (!btnCta || !ctaHint) return;
    const has = steps.length > 0;
    btnCta.disabled = !has;
    ctaHint.textContent = has
        ? `${steps.length} paso${steps.length !== 1 ? "s" : ""} listos para enviar.`
        : "Añade al menos un paso para enviar la configuración.";
}

export async function sendConfiguration(): Promise<void> {
    if (!btnCta || !ctaLoading || !ctaInner) return;
    if (steps.length === 0) return;

    const cmd = makeExecSequence(steps);

    // Show loading state
    ctaInner.style.display = "none";
    ctaLoading.style.display = "";
    btnCta.disabled = true;

    const res = await postCommand(cmd);

    // Give a small delay for the animation
    setTimeout(() => {
        if (ctaInner) ctaInner.style.display = "";
        if (ctaLoading) ctaLoading.style.display = "none";
        if (btnCta) btnCta.disabled = false;

        if (res) {
            showToast("Configuración enviada correctamente.", "success");
        }
    }, 600);
}
