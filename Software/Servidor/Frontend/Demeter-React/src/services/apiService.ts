import { CommandPayload, CommandResponse, DiscoveryResponse, Plant, ExperimentLIMS, PlantTelemetryRecord } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = { ...extra };
    const token = localStorage.getItem('demeter_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
}

export const apiService = {
    async postCommand(cmd: CommandPayload): Promise<CommandResponse | null> {
        try {
            const response = await fetch(`${API_BASE}/command`, {
                method: 'POST',
                headers: authHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify(cmd),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server Error (${response.status})`);
            }

            return await response.json() as CommandResponse;
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    async fetchDevices(): Promise<DiscoveryResponse | null> {
        try {
            const response = await fetch(`${API_BASE}/devices`, { headers: authHeaders() });
            if (!response.ok) {
                throw new Error(`Error fetching devices: ${response.status}`);
            }
            return await response.json() as DiscoveryResponse;
        } catch (error) {
            console.error('Discovery API Error:', error);
            return null;
        }
    },

    async generateAnalysisBundle(experimentId: number = 1): Promise<{ status: string, task_id: string } | null> {
        try {
            const response = await fetch(`${API_BASE}/analysis/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ experimento_id: experimentId })
            });
            if (!response.ok) throw new Error("Failed generating analysis");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async checkAnalysisStatus(taskId: string): Promise<{ status: string, task_id: string, result?: { filename: string }, error?: string } | null> {
        try {
            const response = await fetch(`${API_BASE}/analysis/status/${taskId}`);
            if (!response.ok) throw new Error("Failed checking status");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    getDownloadUrl(filename: string): string {
        return `${API_BASE}/analysis/download/${filename}`;
    },

    async fetchNodeHistory(nodeId: number, days: number = 30): Promise<any[] | null> {
        try {
            const response = await fetch(`${API_BASE}/history/node/${nodeId}?days=${days}`, {
                headers: authHeaders(),
            });

            if (!response.ok) throw new Error("Failed to fetch node history");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    // ─────────────────────────────────────────────────────────────────────────────
    // LIMS ARCHITECTURE (Plants & Experiments)
    // ─────────────────────────────────────────────────────────────────────────────

    async fetchPlants(): Promise<Plant[] | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/plantas`);
            if (!response.ok) throw new Error("Failed fetching plants");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async fetchExperiments(): Promise<ExperimentLIMS[] | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/experimentos`);
            if (!response.ok) throw new Error("Failed fetching experiments");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async generateExperiment(name: string, description: string, plant_ids: number[]): Promise<ExperimentLIMS | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/experimentos/generar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description, plant_ids })
            });
            if (!response.ok) throw new Error("Failed generating experiment");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async fetchPlantDetail(plantId: number): Promise<Plant | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/plantas/${plantId}`);
            if (!response.ok) throw new Error(`Failed fetching plant ${plantId}`);
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async fetchPlantTelemetry(plantId: number): Promise<PlantTelemetryRecord[] | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/plantas/${plantId}/telemetry`);
            if (!response.ok) throw new Error(`Failed fetching telemetry for plant ${plantId}`);
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async updatePlant(plantId: number, data: Partial<Plant>): Promise<Plant | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/plantas/${plantId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`Failed updating plant ${plantId}`);
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async createPlant(data: Omit<Plant, 'id' | 'experiments'>): Promise<Plant | null> {
        try {
            const response = await fetch(`${API_BASE}/lims/plantas`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed creating plant');
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    }
};
