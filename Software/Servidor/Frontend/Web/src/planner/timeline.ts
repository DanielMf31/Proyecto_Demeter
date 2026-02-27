import { steps } from "../state.js";

let timelineTrack: HTMLElement | null = null;
let timelineEmpty: HTMLElement | null = null;
let totalTimeBadge: HTMLElement | null = null;
let btnPlay: HTMLButtonElement | null = null;

export function initTimeline(els: {
    track: HTMLElement;
    empty: HTMLElement;
    totalTimeBadge: HTMLElement;
    btnPlay: HTMLButtonElement;
}): void {
    timelineTrack = els.track;
    timelineEmpty = els.empty;
    totalTimeBadge = els.totalTimeBadge;
    btnPlay = els.btnPlay;
}

export function renderTimeline(): void {
    if (!timelineTrack || !timelineEmpty || !totalTimeBadge || !btnPlay) return;

    if (steps.length === 0) {
        timelineTrack.innerHTML = "";
        timelineTrack.appendChild(timelineEmpty);
        timelineEmpty.style.display = "";
        totalTimeBadge.textContent = "";
        btnPlay.disabled = true;
        return;
    }

    timelineEmpty.style.display = "none";

    const totalMs = steps.reduce((acc, s) => acc + s.tiempo, 0);
    totalTimeBadge.textContent = totalMs >= 1000
        ? `${(totalMs / 1000).toFixed(2)} s total`
        : `${totalMs} ms total`;

    btnPlay.disabled = false;

    const track = timelineTrack;
    const empty = timelineEmpty;

    // Clear old items (keep the empty placeholder)
    const children = Array.from(track.children);
    children.forEach(child => {
        if (child !== empty) child.remove();
    });

    steps.forEach((step, index) => {
        // ── Item Container ──
        const item = document.createElement("div");
        item.className = "tl-item";
        item.dataset["index"] = String(index);

        // ── Node ──
        const node = document.createElement("div");
        const stateClass = step.pin === "WAIT" ? "wait" : (step.estado === "ON" ? "on" : "off");
        node.className = `tl-node ${stateClass}`;

        const pinLabel = step.pin === "WAIT" ? "WAIT" : `PIN ${step.pin}`;
        const stateLabel = step.pin === "WAIT" ? "PAUSA" : step.estado;
        const timeLabel = `${step.tiempo}ms`;

        node.innerHTML = `
            <span class="tl-pin">${pinLabel}</span>
            <span class="tl-state">${stateLabel}</span>
            <span class="tl-time">${timeLabel}</span>
        `;

        item.appendChild(node);
        track.appendChild(item);

        // ── Arrow (except for last item) ──
        if (index < steps.length - 1) {
            const arrow = document.createElement("div");
            arrow.className = "tl-arrow";
            track.appendChild(arrow);
        }
    });
}
