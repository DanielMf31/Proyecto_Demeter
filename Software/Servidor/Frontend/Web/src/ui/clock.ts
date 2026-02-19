let clockEl: HTMLElement | null = null;

export function initClock(el: HTMLElement): void {
    clockEl = el;
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock(): void {
    if (!clockEl) return;
    clockEl.textContent = new Date().toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}
