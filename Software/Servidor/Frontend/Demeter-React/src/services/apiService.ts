import { CommandPayload, CommandResponse, DiscoveryResponse } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiService = {
    async postCommand(cmd: CommandPayload): Promise<CommandResponse | null> {
        try {
            const response = await fetch(`${API_BASE}/command`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
            const response = await fetch(`${API_BASE}/devices`);
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
            const token = localStorage.getItem('demeter_token');
            const headers: Record<string, string> = {};

            // Si el token existe (el usuario hizo login), se adjunta
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_BASE}/history/node/${nodeId}?days=${days}`, {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) throw new Error("Failed to fetch node history");
            return await response.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    }
};
