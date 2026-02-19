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

    // Remove old segments (keep the empty placeholder)
    const existing = timelineTrack.querySelectorAll(".tl-segment");
    existing.forEach(el => el.remove());

    steps.forEach((step) => {
        const pct = totalMs > 0 ? (step.tiempo / totalMs) * 100 : 0;
        const seg = document.createElement("div");
        seg.className = `tl-segment ${step.pin === "WAIT" ? "tl-wait" : step.estado === "ON" ? "tl-on" : "tl-off"}`;
        seg.style.width = `${Math.max(pct, 2)}%`;
        seg.setAttribute("role", "listitem");

        const label = step.pin === "WAIT"
            ? `⏸ ${step.tiempo} ms`
            : `P${step.pin} ${step.estado} ${step.tiempo} ms`;
        seg.setAttribute("aria-label", label);

        const inner = document.createElement("span");
        inner.className = "tl-label";
        inner.textContent = label;
        seg.appendChild(inner);

        timelineTrack!.appendChild(seg);
    });
}
