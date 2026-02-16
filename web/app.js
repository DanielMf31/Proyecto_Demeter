const API_URL = "/api/command";
const logConsole = document.getElementById("log-console");

function log(message) {
    const time = new Date().toLocaleTimeString();
    const line = document.createElement("div");
    line.textContent = `[${time}] ${message}`;
    logConsole.prepend(line);
}

async function sendCommand(pin) {
    const statusIdx = `status-${pin}`;
    const indicator = document.getElementById(statusIdx);

    // Simple toggle logic state local to UI for visual feedback
    const isCurrentlyActive = indicator.classList.contains("active");
    const nextAction = isCurrentlyActive ? "OFF" : "ON";

    log(`Sending command: PIN ${pin} -> ${nextAction}`);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                pin: pin,
                action: nextAction,
                target_id: 1
            })
        });

        if (response.ok) {
            log(`Success: Pin ${pin} command sent`);
            indicator.classList.toggle("active");
        } else {
            const err = await response.text();
            log(`Error: ${response.status} - ${err}`);
        }
    } catch (error) {
        log(`Network Error: ${error.message}`);
    }
}
