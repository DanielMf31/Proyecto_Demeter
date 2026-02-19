const LS_KEY = "demeter_theme";

export function initTheme(): void {
    const saved = localStorage.getItem(LS_KEY) ?? "dark";
    document.documentElement.setAttribute("data-theme", saved);
}

export function toggleTheme(): void {
    const current = document.documentElement.getAttribute("data-theme") ?? "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem(LS_KEY, next);
}
