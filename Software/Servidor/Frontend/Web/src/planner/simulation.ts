import { steps } from "../state.js";
import { showToast } from "../ui/toast.js";

let simTimer: ReturnType<typeof setTimeout> | null = null;
let isSimulationRunning = false;

// DOM references
let btnPlay: HTMLButtonElement | null = null;
let btnPlayLabel: HTMLElement | null = null;
let iconPlay: SVGElement | null = null;
let iconStop: SVGElement | null = null;
let simProgressWrap: HTMLElement | null = null;
let simProgressBar: HTMLElement | null = null;

interface SimElements {
    btnPlay: HTMLButtonElement;
    btnPlayLabel: HTMLElement;
    iconPlay: SVGElement;
    iconStop: SVGElement;
    simProgressWrap: HTMLElement;
    simProgressBar: HTMLElement;
}

export function initSimulation(els: SimElements): void {
    btnPlay = els.btnPlay;
    btnPlayLabel = els.btnPlayLabel;
    iconPlay = els.iconPlay;
    iconStop = els.iconStop;
    simProgressWrap = els.simProgressWrap;
    simProgressBar = els.simProgressBar;
}

export function toggleSimulation(): void {
    if (isSimulationRunning) {
        stopSimulation();
    } else {
        startSimulation();
    }
}

export function stopSimulation(): void {
    if (simTimer !== null) { clearTimeout(simTimer); simTimer = null; }
    isSimulationRunning = false;
    setSimUI(false);
    if (simProgressBar) simProgressBar.style.width = "0%";
    if (simProgressWrap) simProgressWrap.style.display = "none";
    showToast("Simulación detenida.", "info");
}

function startSimulation(): void {
    if (steps.length === 0) return;
    isSimulationRunning = true;
    setSimUI(true);

    if (simProgressWrap) simProgressWrap.style.display = "";
    if (simProgressBar) simProgressBar.style.width = "0%";

    const totalMs = steps.reduce((acc, s) => acc + s.tiempo, 0);
    let elapsed = 0;
    let stepIdx = 0;

    const runStep = (): void => {
        if (!isSimulationRunning || stepIdx >= steps.length) {
            stopSimulation();
            if (stepIdx >= steps.length) showToast("Simulación completada.", "success");
            return;
        }

        const step = steps[stepIdx]!;
        const pct = totalMs > 0 ? Math.round((elapsed / totalMs) * 100) : 0;
        if (simProgressBar) {
            simProgressBar.style.width = `${pct}%`;
            simProgressBar.setAttribute("aria-valuenow", String(pct));
        }

        // Highlight current row and timeline node
        document.querySelectorAll<HTMLElement>("#table-body tr").forEach((tr, i) => {
            tr.classList.toggle("sim-active", i === stepIdx);
        });
        document.querySelectorAll<HTMLElement>(".tl-node").forEach((node, i) => {
            node.classList.toggle("sim-active", i === stepIdx);
        });

        elapsed += step.tiempo;
        stepIdx++;
        simTimer = setTimeout(runStep, step.tiempo);
    };

    runStep();
}

function setSimUI(running: boolean): void {
    if (iconPlay) iconPlay.style.display = running ? "none" : "";
    if (iconStop) iconStop.style.display = running ? "" : "none";
    if (btnPlayLabel) btnPlayLabel.textContent = running ? "Detener" : "Simular";
    if (btnPlay) btnPlay.setAttribute("aria-label", running ? "Detener simulación" : "Iniciar simulación");
}
