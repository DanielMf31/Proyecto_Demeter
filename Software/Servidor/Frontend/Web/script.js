/**
 * Sequence Planner v3 — script.js
 *
 * Modules:
 *  0. Navigation (SPA View Switching)
 *  1. State & History (Undo/Redo)
 *  2. Auto-save (localStorage)
 *  3. Clock
 *  4. Theme Toggle
 *  5. Form Logic (WAIT step, field visibility, Enter key)
 *  6. CRUD: Add / Delete / Duplicate
 *  7. Drag & Drop Reorder
 *  8. Bulk Actions
 *  9. Timeline Render
 * 10. Simulation / Play Mode
 * 11. Global CTA (Enviar Configuración)
 * 12. Manual Control — Card Toggle
 * 13. Toast Notifications
 * 14. Keyboard Shortcuts
 * 15. Init
 */

'use strict';

/* ═══════════════════════════════════════════════════════════════
   0. NAVIGATION — SPA VIEW SWITCHING
   ═══════════════════════════════════════════════════════════════ */

/** Currently active view id: 'planner' | 'manual' */
let activeView = 'planner';

/**
 * Switch between #view-planner and #view-manual.
 * Updates nav-link active state and ARIA attributes.
 */
function switchView(viewId) {
    if (viewId === activeView) return;
    activeView = viewId;

    // Toggle views
    viewPlanner.style.display = viewId === 'planner' ? 'block' : 'none';
    viewManual.style.display = viewId === 'manual' ? 'block' : 'none';

    // Animate the incoming view
    const incoming = viewId === 'planner' ? viewPlanner : viewManual;
    incoming.classList.remove('view-enter');
    // Force reflow to restart animation
    void incoming.offsetWidth;
    incoming.classList.add('view-enter');

    // Update nav links
    navPlanner.classList.toggle('active', viewId === 'planner');
    navManual.classList.toggle('active', viewId === 'manual');
    navPlanner.setAttribute('aria-selected', viewId === 'planner');
    navManual.setAttribute('aria-selected', viewId === 'manual');

    // Show/hide undo-redo (only relevant in planner)
    historyControls.style.display = viewId === 'planner' ? 'flex' : 'none';
    autosaveBadge.style.display = viewId === 'planner' ? 'inline-flex' : 'none';
}

/* ═══════════════════════════════════════════════════════════════
   1. STATE & HISTORY (UNDO / REDO)
   ═══════════════════════════════════════════════════════════════ */

let steps = [];
let nextId = 1;

const undoStack = [];
const redoStack = [];
const MAX_HISTORY = 50;

function saveSnapshot() {
    undoStack.push(JSON.parse(JSON.stringify(steps)));
    if (undoStack.length > MAX_HISTORY) undoStack.shift();
    redoStack.length = 0;
    updateHistoryButtons();
}

function undo() {
    if (undoStack.length === 0) return;
    redoStack.push(JSON.parse(JSON.stringify(steps)));
    steps = undoStack.pop();
    nextId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    rebuildTable();
    persistToStorage();
    showToast('Acción deshecha.', 'info');
    updateHistoryButtons();
}

function redo() {
    if (redoStack.length === 0) return;
    undoStack.push(JSON.parse(JSON.stringify(steps)));
    steps = redoStack.pop();
    nextId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    rebuildTable();
    persistToStorage();
    showToast('Acción rehecha.', 'info');
    updateHistoryButtons();
}

function updateHistoryButtons() {
    btnUndo.disabled = undoStack.length === 0;
    btnRedo.disabled = redoStack.length === 0;
}

/* ═══════════════════════════════════════════════════════════════
   2. AUTO-SAVE (LOCAL STORAGE)
   ═══════════════════════════════════════════════════════════════ */

const LS_KEY = 'sequence-planner-v3';
let saveTimer = null;

function persistToStorage() {
    autosaveBadge.classList.remove('saved');
    autosaveBadge.classList.add('saving');
    const textNode = autosaveBadge.childNodes[autosaveBadge.childNodes.length - 1];
    if (textNode) textNode.textContent = ' Guardando…';

    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        try {
            localStorage.setItem(LS_KEY, JSON.stringify({ steps, nextId }));
        } catch (e) {
            console.warn('Auto-save failed:', e);
        }
        autosaveBadge.classList.remove('saving');
        autosaveBadge.classList.add('saved');
        const tn = autosaveBadge.childNodes[autosaveBadge.childNodes.length - 1];
        if (tn) tn.textContent = ' Guardado';
    }, 600);
}

function loadFromStorage() {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return;
        const data = JSON.parse(raw);
        if (Array.isArray(data.steps)) {
            steps = data.steps;
            nextId = data.nextId || (steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1);
        }
    } catch (e) {
        console.warn('Failed to load from storage:', e);
    }
}

function clearStorage() {
    localStorage.removeItem(LS_KEY);
}

/* ═══════════════════════════════════════════════════════════════
   3. CLOCK
   ═══════════════════════════════════════════════════════════════ */

function updateClock() {
    clockEl.textContent = new Date().toLocaleTimeString('es-ES', {
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

/* ═══════════════════════════════════════════════════════════════
   4. THEME TOGGLE
   ═══════════════════════════════════════════════════════════════ */

function initTheme() {
    const saved = localStorage.getItem('sp-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('sp-theme', next);
}

/* ═══════════════════════════════════════════════════════════════
   5. FORM LOGIC
   ═══════════════════════════════════════════════════════════════ */

function onPinChange() {
    const isWait = selPin.value === 'WAIT';
    groupEstado.classList.toggle('hidden', isWait);
    if (isWait) selEstado.value = '';
    selPin.classList.remove('error');
    selEstado.classList.remove('error');
}

/* ═══════════════════════════════════════════════════════════════
   6. CRUD — ADD / DELETE / DUPLICATE
   ═══════════════════════════════════════════════════════════════ */

function addStep() {
    const pin = selPin.value;
    const estado = selEstado.value;
    const tiempo = inpTiempo.value.trim();
    const isWait = pin === 'WAIT';

    [selPin, selEstado, inpTiempo].forEach(el => el.classList.remove('error'));

    let valid = true;
    if (!pin) { selPin.classList.add('error'); valid = false; }
    if (!isWait && !estado) { selEstado.classList.add('error'); valid = false; }
    if (!tiempo || isNaN(Number(tiempo)) || Number(tiempo) < 1) { inpTiempo.classList.add('error'); valid = false; }

    if (!valid) {
        showToast('Completa todos los campos correctamente.', 'error');
        return;
    }

    saveSnapshot();

    const step = {
        id: nextId++,
        pin,
        estado: isWait ? 'WAIT' : estado,
        tiempo: Number(tiempo)
    };

    steps.push(step);

    const tr = buildRow(step, steps.length - 1);
    tableBody.appendChild(tr);
    updateView();

    requestAnimationFrame(() => { tableScroll.scrollTop = tableScroll.scrollHeight; });

    selPin.value = '';
    selEstado.value = '';
    inpTiempo.value = '';
    groupEstado.classList.remove('hidden');
    selPin.focus();

    persistToStorage();
    showToast(`Paso ${steps.length} añadido — ${isWait ? 'Pausa' : `Pin ${pin} ${estado}`} ${tiempo}ms`, 'success');
}

function deleteStep(id) {
    saveSnapshot();
    steps = steps.filter(s => s.id !== id);
    rebuildTable();
    persistToStorage();
    showToast('Paso eliminado.', 'success');
}

function duplicateStep(id) {
    const src = steps.find(s => s.id === id);
    if (!src) return;

    saveSnapshot();
    const clone = { ...src, id: nextId++ };
    steps.push(clone);

    const tr = buildRow(clone, steps.length - 1);
    tableBody.appendChild(tr);
    updateView();

    requestAnimationFrame(() => { tableScroll.scrollTop = tableScroll.scrollHeight; });
    persistToStorage();
    showToast('Paso duplicado.', 'success');
}

/* ═══════════════════════════════════════════════════════════════
   7. DRAG & DROP REORDER
   ═══════════════════════════════════════════════════════════════ */

let dragSrcIndex = null;

function getRowIndex(tr) {
    return Array.from(tableBody.children).indexOf(tr);
}

function onDragStart(e) {
    dragSrcIndex = getRowIndex(this);
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', dragSrcIndex);
}

function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    tableBody.querySelectorAll('tr').forEach(r => r.classList.remove('drag-over'));
    this.classList.add('drag-over');
}

function onDragLeave() {
    this.classList.remove('drag-over');
}

function onDrop(e) {
    e.preventDefault();
    const targetIndex = getRowIndex(this);
    if (dragSrcIndex === null || dragSrcIndex === targetIndex) return;

    saveSnapshot();
    const [moved] = steps.splice(dragSrcIndex, 1);
    steps.splice(targetIndex, 0, moved);

    rebuildTable();
    persistToStorage();
    showToast('Orden actualizado.', 'success');
}

function onDragEnd() {
    this.classList.remove('dragging');
    tableBody.querySelectorAll('tr').forEach(r => r.classList.remove('drag-over'));
    dragSrcIndex = null;
}

/* ═══════════════════════════════════════════════════════════════
   8. BULK ACTIONS
   ═══════════════════════════════════════════════════════════════ */

function getSelectedIds() {
    return Array.from(tableBody.querySelectorAll('.row-chk:checked'))
        .map(chk => Number(chk.dataset.id));
}

function syncSelectAll() {
    const all = tableBody.querySelectorAll('.row-chk');
    const checked = tableBody.querySelectorAll('.row-chk:checked');
    chkAll.indeterminate = checked.length > 0 && checked.length < all.length;
    chkAll.checked = all.length > 0 && checked.length === all.length;
}

function updateBulkBar() {
    const ids = getSelectedIds();
    if (ids.length > 0) {
        bulkBar.hidden = false;
        bulkInfo.textContent = `${ids.length} paso${ids.length > 1 ? 's' : ''} seleccionado${ids.length > 1 ? 's' : ''}`;
    } else {
        bulkBar.hidden = true;
    }
}

function bulkDelete() {
    const ids = getSelectedIds();
    if (ids.length === 0) return;

    saveSnapshot();
    steps = steps.filter(s => !ids.includes(s.id));
    chkAll.checked = false;
    rebuildTable();
    persistToStorage();
    showToast(`${ids.length} paso${ids.length > 1 ? 's' : ''} eliminado${ids.length > 1 ? 's' : ''}.`, 'success');
}

/* ═══════════════════════════════════════════════════════════════
   9. RENDER HELPERS
   ═══════════════════════════════════════════════════════════════ */

function buildRow(step, index) {
    const tr = document.createElement('tr');
    tr.dataset.id = step.id;
    tr.dataset.index = index;
    tr.draggable = true;

    const isWait = step.pin === 'WAIT' || step.estado === 'WAIT';

    const pinBadge = isWait
        ? `<span class="badge-wait">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        Pausa
      </span>`
        : `<span class="badge-pin">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
        Pin ${step.pin}
      </span>`;

    let estadoBadge;
    if (isWait) {
        estadoBadge = `<span class="badge-wait-state"><span class="badge-dot"></span>—</span>`;
    } else if (step.estado === 'ON') {
        estadoBadge = `<span class="badge-on"><span class="badge-dot"></span>ON</span>`;
    } else {
        estadoBadge = `<span class="badge-off"><span class="badge-dot"></span>OFF</span>`;
    }

    tr.innerHTML = `
    <td class="col-drag">
      <div class="drag-handle" aria-label="Arrastrar para reordenar" title="Arrastrar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="9" y1="5"  x2="9"  y2="19"/>
          <line x1="15" y1="5" x2="15" y2="19"/>
        </svg>
      </div>
    </td>
    <td class="col-check">
      <label class="checkbox-wrap" aria-label="Seleccionar paso ${index + 1}">
        <input type="checkbox" class="row-chk" data-id="${step.id}" />
        <span class="checkmark" aria-hidden="true"></span>
      </label>
    </td>
    <td class="td-step col-num">${String(index + 1).padStart(2, '0')}</td>
    <td>${pinBadge}</td>
    <td>${estadoBadge}</td>
    <td class="td-time">${step.tiempo}<span class="unit">ms</span></td>
    <td class="col-actions">
      <div class="actions-cell">
        <button class="btn-icon duplicate" data-id="${step.id}" aria-label="Duplicar paso ${index + 1}" title="Duplicar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="9" y="9" width="13" height="13" rx="2"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
          </svg>
        </button>
        <button class="btn-icon delete" data-id="${step.id}" aria-label="Eliminar paso ${index + 1}" title="Eliminar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
            <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
          </svg>
        </button>
      </div>
    </td>
  `;

    tr.querySelector('.row-chk').addEventListener('change', () => {
        tr.classList.toggle('selected', tr.querySelector('.row-chk').checked);
        syncSelectAll();
        updateBulkBar();
    });

    tr.querySelector('.btn-icon.duplicate').addEventListener('click', () => duplicateStep(step.id));
    tr.querySelector('.btn-icon.delete').addEventListener('click', () => deleteStep(step.id));

    tr.addEventListener('dragstart', onDragStart);
    tr.addEventListener('dragover', onDragOver);
    tr.addEventListener('dragleave', onDragLeave);
    tr.addEventListener('drop', onDrop);
    tr.addEventListener('dragend', onDragEnd);

    return tr;
}

function rebuildTable() {
    tableBody.innerHTML = '';
    steps.forEach((step, i) => tableBody.appendChild(buildRow(step, i)));
    updateView();
}

function updateView() {
    const hasRows = steps.length > 0;
    emptyState.style.display = hasRows ? 'none' : 'flex';
    tableScroll.style.display = hasRows ? 'block' : 'none';
    rowCount.textContent = steps.length === 1 ? '1 paso' : `${steps.length} pasos`;

    updateBulkBar();
    renderTimeline();
    updateCTA();
}

/* ── Timeline Render ─────────────────────────────────────────── */

function renderTimeline() {
    Array.from(timelineTrack.children).forEach(child => {
        if (child !== timelineEmpty) child.remove();
    });

    if (steps.length === 0) {
        timelineEmpty.style.display = 'flex';
        btnPlay.disabled = true;
        totalTimeBadge.textContent = '';
        return;
    }

    timelineEmpty.style.display = 'none';
    btnPlay.disabled = false;

    const total = steps.reduce((acc, s) => acc + s.tiempo, 0);
    totalTimeBadge.textContent = `Total: ${total}ms`;

    steps.forEach((step, i) => {
        const isWait = step.pin === 'WAIT' || step.estado === 'WAIT';
        const nodeClass = isWait ? 'wait' : (step.estado === 'ON' ? 'on' : 'off');
        const pinLabel = isWait ? '⏸' : `P${step.pin}`;
        const stateLabel = isWait ? 'Pausa' : step.estado;

        const item = document.createElement('div');
        item.className = 'tl-item';
        item.dataset.index = i;

        item.innerHTML = `
      <div class="tl-node ${nodeClass}" title="Paso ${i + 1}: ${stateLabel} ${step.tiempo}ms">
        <span class="tl-pin">${pinLabel}</span>
        <span class="tl-state">${stateLabel}</span>
        <span class="tl-time">${step.tiempo}ms</span>
      </div>
    `;

        timelineTrack.appendChild(item);

        if (i < steps.length - 1) {
            const arrow = document.createElement('div');
            arrow.className = 'tl-arrow';
            arrow.setAttribute('aria-hidden', 'true');
            timelineTrack.appendChild(arrow);
        }
    });
}

/* ═══════════════════════════════════════════════════════════════
   10. SIMULATION / PLAY MODE
   ═══════════════════════════════════════════════════════════════ */

let simRunning = false;
let simAbort = false;
let simTimeouts = [];

function startSimulation() {
    if (steps.length === 0) return;

    simRunning = true;
    simAbort = false;
    simTimeouts = [];

    btnPlay.classList.add('running');
    btnPlay.querySelector('.sim-label').textContent = 'Detener';
    btnPlay.querySelector('.icon-play').style.display = 'none';
    btnPlay.querySelector('.icon-stop').style.display = 'block';

    simProgressWrap.style.display = 'block';
    simProgressBar.style.width = '0%';

    const nodes = timelineTrack.querySelectorAll('.tl-node');
    const total = steps.reduce((acc, s) => acc + s.tiempo, 0);
    let elapsed = 0;

    steps.forEach((step, i) => {
        const activateAt = elapsed;
        const t1 = setTimeout(() => {
            if (simAbort) return;
            nodes.forEach(n => n.classList.remove('sim-active'));
            if (nodes[i]) {
                nodes[i].classList.add('sim-active');
                nodes[i].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        }, activateAt);

        simTimeouts.push(t1);

        const stepStart = elapsed;
        const stepEnd = elapsed + step.tiempo;
        const FPS = 30;
        const interval = 1000 / FPS;
        let t = stepStart;

        const progressInterval = setInterval(() => {
            if (simAbort) { clearInterval(progressInterval); return; }
            t += interval;
            const pct = Math.min((t / total) * 100, 100);
            simProgressBar.style.width = `${pct}%`;
            if (t >= stepEnd) clearInterval(progressInterval);
        }, interval);

        simTimeouts.push(progressInterval);
        elapsed += step.tiempo;
    });

    const endTimeout = setTimeout(() => {
        if (simAbort) return;
        stopSimulation(true);
        showToast('Simulación completada.', 'success');
    }, elapsed);

    simTimeouts.push(endTimeout);
}

function stopSimulation(completed = false) {
    simAbort = true;
    simTimeouts.forEach(t => { clearTimeout(t); clearInterval(t); });
    simTimeouts = [];

    btnPlay.classList.remove('running');
    btnPlay.querySelector('.sim-label').textContent = 'Simular';
    btnPlay.querySelector('.icon-play').style.display = 'block';
    btnPlay.querySelector('.icon-stop').style.display = 'none';

    timelineTrack.querySelectorAll('.tl-node').forEach(n => n.classList.remove('sim-active'));

    if (completed) {
        simProgressBar.style.width = '100%';
        setTimeout(() => {
            simProgressWrap.style.display = 'none';
            simProgressBar.style.width = '0%';
        }, 600);
    } else {
        simProgressWrap.style.display = 'none';
        simProgressBar.style.width = '0%';
    }

    simRunning = false;
}


/* ═══════════════════════════════════════════════════════════════
   11. WEBSOCKET CONNECTION
   ═══════════════════════════════════════════════════════════════ */

let ws = null;
let wsConnected = false;
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL = `${protocol}//${window.location.host}/ws/frontend-web`;

function initWebSocket() {
    console.log('Connecting to WebSocket:', WS_URL);
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log('WebSocket connected');
        wsConnected = true;
        showToast('Conectado al servidor.', 'success');
        // Optional: Send identity or request initial state
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('WS Message:', data);
            if (data.type === 'pong') {
                console.log('Pong received');
            }
            // Future: Handle state updates from server
        } catch (e) {
            console.error('Error parsing WS message:', e);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected. Reconnecting in 3s...');
        wsConnected = false;
        showToast('Conexión perdida. Reconectando...', 'error');
        setTimeout(initWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
    };
}

function sendWebSocketCommand(command, params) {
    if (!wsConnected || !ws) {
        showToast('No hay conexión con el servidor.', 'error');
        return;
    }
    const msg = {
        type: 'command',
        command: command,
        params: params
    };
    ws.send(JSON.stringify(msg));
}

/* ═══════════════════════════════════════════════════════════════
   12. GLOBAL CTA — Enviar Configuración
   ═══════════════════════════════════════════════════════════════ */

function updateCTA() {
    const hasSteps = steps.length > 0;
    btnSend.disabled = !hasSteps;
    ctaHint.textContent = hasSteps
        ? `${steps.length} paso${steps.length > 1 ? 's' : ''} listos para enviar.`
        : 'Añade al menos un paso para enviar la configuración.';
    ctaHint.classList.remove('error-hint');
}

function sendConfiguration() {
    if (steps.length === 0) return;

    const invalid = steps.filter(s => !s.tiempo || s.tiempo < 1);
    if (invalid.length > 0) {
        ctaHint.textContent = `Error: ${invalid.length} paso(s) tienen tiempo inválido (< 1ms).`;
        ctaHint.classList.add('error-hint');
        showToast('Hay pasos con tiempo inválido. Revisa la tabla.', 'error');
        return;
    }

    btnSend.disabled = true;
    btnSendInner.style.display = 'none';
    btnSendLoading.style.display = 'flex';
    ctaHint.textContent = 'Enviando configuración al sistema…';
    ctaHint.classList.remove('error-hint');

    setTimeout(() => {
        btnSend.disabled = false;
        btnSendInner.style.display = 'flex';
        btnSendLoading.style.display = 'none';
        showToast(`✓ Configuración enviada — ${steps.length} pasos registrados.`, 'success');
        clearStorage();
        ctaHint.textContent = 'Configuración enviada correctamente.';
    }, 2000);
}

/* ═══════════════════════════════════════════════════════════════
   12. MANUAL CONTROL — CARD TOGGLE
   ═══════════════════════════════════════════════════════════════ */

/**
 * Toggle a control card between ON and OFF.
 * Updates ARIA, status dot, label, and active counters.
 */
function toggleCard(card) {
    const isOn = card.classList.toggle('is-on');
    const device = card.dataset.device;   // 'pump' | 'valve'
    const id = card.dataset.id;
    const name = card.querySelector('.card-name').textContent;

    // Update ARIA
    card.setAttribute('aria-pressed', isOn);
    card.setAttribute('aria-label', `${name}, estado ${isOn ? 'ON' : 'OFF'}`);

    // Update state label
    card.querySelector('.card-state-label').textContent = isOn ? 'ON' : 'OFF';

    // Update counters
    updateDeviceCount(device);
    updateManualSummary();

    // WebSocket Command
    // Map Pump 1-4 to Pin 4-7
    // NOTE: This is a direct mapping for demonstration.
    if (device === 'pump') {
        const pinMap = { '1': 4, '2': 5, '3': 6, '4': 7 };
        const pin = pinMap[id];
        if (pin) {
            // Strict Schema: GpioCommand
            // { "type": "GPIO_CMD", "target_id": 2, "pin": 4, "action": "ON" }
            const cmd = {
                type: 'GPIO_CMD',
                target_id: 2, // Assuming Node 2 is the Actuator Controller
                pin: pin,
                action: isOn ? 'ON' : 'OFF'
            };

            if (ws && wsConnected) {
                console.log("Sending GPIO_CMD:", cmd);
                ws.send(JSON.stringify(cmd));
            } else {
                showToast('Comando no enviado: Sin conexión WS', 'error');
            }
        }
    }

    showToast(`${name} → ${isOn ? 'ON' : 'OFF'}`, isOn ? 'success' : 'info');
}

/** Update the "X / 4 activas" counter for a device type */
function updateDeviceCount(device) {
    const cards = document.querySelectorAll(`.control-card[data-device="${device}"]`);
    const onCount = document.querySelectorAll(`.control-card[data-device="${device}"].is-on`).length;
    const countEl = document.getElementById(`${device}-active-count`);
    const label = device === 'pump' ? 'activas' : 'activas';

    if (countEl) {
        countEl.textContent = `${onCount} / ${cards.length} ${label}`;
        countEl.classList.toggle('has-active', onCount > 0);
    }
}

/** Update the global "X activos" summary in the manual header */
function updateManualSummary() {
    const totalOn = document.querySelectorAll('.control-card.is-on').length;
    const summaryEl = document.getElementById('manual-active-count');
    const summaryWrap = document.getElementById('manual-status-summary');

    if (summaryEl) summaryEl.textContent = `${totalOn} activo${totalOn !== 1 ? 's' : ''}`;
    if (summaryWrap) summaryWrap.classList.toggle('has-active', totalOn > 0);
}

/** Emergency stop: turn OFF all cards */
function emergencyStop() {
    const allCards = document.querySelectorAll('.control-card.is-on');
    allCards.forEach(card => {
        card.classList.remove('is-on');
        card.setAttribute('aria-pressed', 'false');
        const name = card.querySelector('.card-name').textContent;
        card.setAttribute('aria-label', `${name}, estado OFF`);
        card.querySelector('.card-state-label').textContent = 'OFF';
    });

    updateDeviceCount('pump');
    updateDeviceCount('valve');
    updateManualSummary();

    if (allCards.length > 0) {
        showToast(`Paro de emergencia — ${allCards.length} dispositivo${allCards.length > 1 ? 's' : ''} desactivado${allCards.length > 1 ? 's' : ''}.`, 'error');
    } else {
        showToast('No hay dispositivos activos.', 'info');
    }
}

/* ═══════════════════════════════════════════════════════════════
   13. TOAST NOTIFICATIONS
   ═══════════════════════════════════════════════════════════════ */

const ICONS = {
    success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>`,
    error: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
    info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `${ICONS[type] || ICONS.info}<span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 200ms ease forwards';
        setTimeout(() => toast.remove(), 200);
    }, 2800);
}

/* ═══════════════════════════════════════════════════════════════
   DOM REFS
   ═══════════════════════════════════════════════════════════════ */

// Navigation
const navPlanner = document.getElementById('nav-planner');
const navManual = document.getElementById('nav-manual');
const viewPlanner = document.getElementById('view-planner');
const viewManual = document.getElementById('view-manual');
const historyControls = document.querySelector('.history-controls');

// Planner
const selPin = document.getElementById('sel-pin');
const selEstado = document.getElementById('sel-estado');
const inpTiempo = document.getElementById('inp-tiempo');
const btnAdd = document.getElementById('btn-add');
const groupEstado = document.getElementById('group-estado');
const tableBody = document.getElementById('table-body');
const emptyState = document.getElementById('empty-state');
const tableScroll = document.getElementById('table-scroll');
const rowCount = document.getElementById('row-count');
const chkAll = document.getElementById('chk-all');
const bulkBar = document.getElementById('bulk-bar');
const bulkInfo = document.getElementById('bulk-info');
const btnBulkDel = document.getElementById('btn-bulk-delete');
const timelineTrack = document.getElementById('timeline-track');
const timelineEmpty = document.getElementById('timeline-empty');
const totalTimeBadge = document.getElementById('total-time-badge');
const btnPlay = document.getElementById('btn-play');
const simProgressWrap = document.getElementById('sim-progress-wrap');
const simProgressBar = document.getElementById('sim-progress-bar');
const btnSend = document.getElementById('btn-send');
const btnSendInner = document.getElementById('btn-send-inner');
const btnSendLoading = document.getElementById('btn-send-loading');
const ctaHint = document.getElementById('cta-hint');

// Shared
const themeToggle = document.getElementById('theme-toggle');
const clockEl = document.getElementById('clock');
const btnUndo = document.getElementById('btn-undo');
const btnRedo = document.getElementById('btn-redo');
const autosaveBadge = document.getElementById('autosave-badge');
const toastContainer = document.getElementById('toast-container');

// Manual
const btnEmergency = document.getElementById('btn-emergency');

/* ═══════════════════════════════════════════════════════════════
   14. EVENT LISTENERS
   ═══════════════════════════════════════════════════════════════ */

// Navigation
navPlanner.addEventListener('click', () => switchView('planner'));
navManual.addEventListener('click', () => switchView('manual'));

// Planner form
btnAdd.addEventListener('click', addStep);
selPin.addEventListener('change', onPinChange);

inpTiempo.addEventListener('keydown', e => {
    if (e.key === 'Enter') { e.preventDefault(); addStep(); }
});

[selPin, selEstado, inpTiempo].forEach(el => {
    el.addEventListener('input', () => el.classList.remove('error'));
    el.addEventListener('change', () => el.classList.remove('error'));
});

// Bulk
chkAll.addEventListener('change', () => {
    tableBody.querySelectorAll('.row-chk').forEach(chk => {
        chk.checked = chkAll.checked;
        chk.closest('tr').classList.toggle('selected', chkAll.checked);
    });
    updateBulkBar();
});

btnBulkDel.addEventListener('click', bulkDelete);

// Undo / Redo
btnUndo.addEventListener('click', undo);
btnRedo.addEventListener('click', redo);

// Theme
themeToggle.addEventListener('click', toggleTheme);

// Simulation
btnPlay.addEventListener('click', () => {
    if (simRunning) {
        stopSimulation(false);
        showToast('Simulación detenida.', 'info');
    } else {
        startSimulation();
    }
});

// CTA
btnSend.addEventListener('click', sendConfiguration);

// Manual control cards — event delegation on each cards-grid
document.querySelectorAll('.cards-grid').forEach(grid => {
    grid.addEventListener('click', e => {
        const card = e.target.closest('.control-card');
        if (card) toggleCard(card);
    });
});

// Emergency stop
btnEmergency.addEventListener('click', emergencyStop);

/* ═══════════════════════════════════════════════════════════════
   KEYBOARD SHORTCUTS
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('keydown', e => {
    // Ctrl+Z — Undo
    if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
        return;
    }
    // Ctrl+Y or Ctrl+Shift+Z — Redo
    if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        redo();
        return;
    }
});

/* ═══════════════════════════════════════════════════════════════
   15. INIT
   ═══════════════════════════════════════════════════════════════ */

function init() {
    initTheme();
    loadFromStorage();
    rebuildTable();
    loadFromStorage();
    rebuildTable();
    updateHistoryButtons();
    initWebSocket(); // Start WS connection

    // Clock
    updateClock();
    setInterval(updateClock, 1000);

    // Ensure planner view is active on load
    switchView('planner');
}

init();
