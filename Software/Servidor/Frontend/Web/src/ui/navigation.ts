type ViewId = "planner" | "manual";

let activeView: ViewId = "planner";

interface NavElements {
    viewPlanner: HTMLElement;
    viewManual: HTMLElement;
    navPlanner: HTMLElement;
    navManual: HTMLElement;
    historyControls: HTMLElement;
    autosaveBadge: HTMLElement;
}

let els: NavElements | null = null;

export function initNavigation(elements: NavElements): void {
    els = elements;
}

export function switchView(viewId: ViewId): void {
    if (!els || viewId === activeView) return;
    activeView = viewId;

    els.viewPlanner.style.display = viewId === "planner" ? "block" : "none";
    els.viewManual.style.display = viewId === "manual" ? "block" : "none";

    // Animate incoming view
    const incoming = viewId === "planner" ? els.viewPlanner : els.viewManual;
    incoming.classList.remove("view-enter");
    void incoming.offsetWidth; // force reflow
    incoming.classList.add("view-enter");

    // Update nav links
    els.navPlanner.classList.toggle("active", viewId === "planner");
    els.navManual.classList.toggle("active", viewId === "manual");
    els.navPlanner.setAttribute("aria-selected", String(viewId === "planner"));
    els.navManual.setAttribute("aria-selected", String(viewId === "manual"));

    // Show/hide undo-redo + autosave (only relevant in planner)
    els.historyControls.style.display = viewId === "planner" ? "flex" : "none";
    els.autosaveBadge.style.display = viewId === "planner" ? "inline-flex" : "none";
}

export function getActiveView(): ViewId {
    return activeView;
}
