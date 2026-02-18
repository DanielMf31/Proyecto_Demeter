const API_URL = "/api/command";
const logConsole = document.getElementById("log-console");

// --- UTILS ---
function log(message, type = "system") {
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement("p");
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${time}] ${message}`;
    logConsole.prepend(entry);
}

// --- NAVIGATION ---
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = link.getAttribute('data-view');

        // Update active class in Nav
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Switch views
        document.querySelectorAll('.view').forEach(view => view.classList.add('hidden'));
        document.getElementById(`${targetView}-view`).classList.remove('hidden');

        log(`Cambiado a vista: ${targetView}`);
    });
});

// --- DASHBOARD CONTROL ---
async function sendCommand(pin, action = 'TOGGLE') {
    const indicator = document.getElementById(`status-${pin}`);
    let finalAction = action;

    if (action === 'TOGGLE') {
        const isCurrentlyActive = indicator.classList.contains("active");
        finalAction = isCurrentlyActive ? "OFF" : "ON";
    }

    log(`Enviando comando: PIN ${pin} -> ${finalAction}`, "command");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pin: pin,
                action: finalAction,
                target_id: 1
            })
        });

        if (response.ok) {
            log(`Éxito: Pin ${pin} command sent`, "system");
            if (finalAction === "ON") indicator.classList.add("active");
            else indicator.classList.remove("active");
        } else {
            const err = await response.text();
            log(`Error: ${response.status} - ${err}`, "error");
        }
    } catch (error) {
        log(`Error de red: ${error.message}`, "error");
    }
}

// --- SEQUENCER LOGIC ---
let steps = [];

function addStep() {
    if (steps.length >= 10) {
        log("Límite de 10 pasos alcanzado", "error");
        return;
    }

    const stepId = Date.now();
    const step = {
        id: stepId,
        pin: 4,
        action: 'ON',
        duration: 1000
    };

    steps.push(step);
    renderSteps();
}

function removeStep(id) {
    steps = steps.filter(s => s.id !== id);
    renderSteps();
}

function updateStep(id, field, value) {
    const step = steps.find(s => s.id === id);
    if (!step) return;

    if (field === 'duration') {
        step.duration = parseInt(value) || 0;
    } else if (field === 'pin') {
        step.pin = parseInt(value);
    } else if (field === 'action') {
        step.action = value;
        // Si es OFF, poner 1ms por defecto si no hay nada
        if (value === 'OFF' && step.duration === 1000) {
            step.duration = 1;
        }
    }
    renderSteps();
}

function renderSteps() {
    const container = document.getElementById("sequence-steps");
    container.innerHTML = "";

    steps.forEach((step, index) => {
        const div = document.createElement("div");
        div.className = "step-row";
        div.innerHTML = `
            <span>Paso ${index + 1}</span>
            <select onchange="updateStep(${step.id}, 'pin', this.value)">
                <option value="4" ${step.pin == 4 ? 'selected' : ''}>Pin 4</option>
                <option value="5" ${step.pin == 5 ? 'selected' : ''}>Pin 5</option>
                <option value="6" ${step.pin == 6 ? 'selected' : ''}>Pin 6</option>
                <option value="7" ${step.pin == 7 ? 'selected' : ''}>Pin 7</option>
            </select>
            <select onchange="updateStep(${step.id}, 'action', this.value)">
                <option value="ON" ${step.action == 'ON' ? 'selected' : ''}>ON</option>
                <option value="OFF" ${step.action == 'OFF' ? 'selected' : ''}>OFF</option>
            </select>
            <input type="number" value="${step.duration}" placeholder="Duración (ms)" 
                   onchange="updateStep(${step.id}, 'duration', this.value)">
            <button class="btn btn-sm btn-danger" onclick="removeStep(${step.id})">×</button>
        `;
        container.appendChild(div);
    });
}

// --- PERSISTENCE ---
function saveCurrentSequence() {
    const name = document.getElementById("sequence-name").value || "Secuencia Sin Nombre";
    if (steps.length === 0) {
        log("No hay pasos para guardar", "error");
        return;
    }

    const sequence = {
        id: Date.now(),
        name: name,
        steps: JSON.parse(JSON.stringify(steps)) // Deep copy
    };

    let saved = JSON.parse(localStorage.getItem("demeter_sequences") || "[]");
    saved.push(sequence);
    localStorage.setItem("demeter_sequences", JSON.stringify(saved));

    log(`Secuencia '${name}' guardada correctamente`);
    document.getElementById("sequence-name").value = "";
    loadSavedSequences();
}

function loadSavedSequences() {
    const container = document.getElementById("saved-sequences");
    const saved = JSON.parse(localStorage.getItem("demeter_sequences") || "[]");

    if (saved.length === 0) {
        container.innerHTML = '<p class="empty-msg">No hay secuencias guardadas.</p>';
        return;
    }

    container.innerHTML = "";
    saved.forEach(seq => {
        const div = document.createElement("div");
        div.className = "saved-item";
        div.innerHTML = `
            <span>${seq.name} (${seq.steps.length} pasos)</span>
            <div>
                <button class="btn btn-sm btn-primary" onclick='runSavedSequence(${JSON.stringify(seq)})'>Ejecutar</button>
                <button class="btn btn-sm btn-danger" onclick="deleteSequence(${seq.id})">×</button>
            </div>
        `;
        container.appendChild(div);
    });
}

function deleteSequence(id) {
    let saved = JSON.parse(localStorage.getItem("demeter_sequences") || "[]");
    saved = saved.filter(s => s.id !== id);
    localStorage.setItem("demeter_sequences", JSON.stringify(saved));
    loadSavedSequences();
}

async function runSavedSequence(seq) {
    log(`Ejecutando secuencia: ${seq.name}`, "command");
    // Formatear para API (SequenceCommand)
    const apiSteps = seq.steps.map(s => ({
        pin: s.pin,
        action: s.action,
        duration: s.duration
    }));

    await sendSequence(apiSteps);
}

async function executeSequence() {
    if (steps.length === 0) {
        log("Crea al menos un paso antes de ejecutar", "error");
        return;
    }

    const apiSteps = steps.map(s => ({
        pin: s.pin,
        action: s.action,
        duration: s.duration
    }));

    await sendSequence(apiSteps);
}

async function sendSequence(stepsList) {
    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                type: "SEQUENCE",
                target_id: 1,
                steps: stepsList
            })
        });

        if (response.ok) {
            log("Secuencia enviada al servidor con éxito", "success");
        } else {
            const err = await response.text();
            log(`Error en secuencia: ${response.status} - ${err}`, "error");
        }
    } catch (e) {
        log(`Error de red: ${e.message}`, "error");
    }
}

// Init
loadSavedSequences();
renderSteps();
