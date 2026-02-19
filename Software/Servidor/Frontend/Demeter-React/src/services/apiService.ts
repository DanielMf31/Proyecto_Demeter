import { CommandPayload, CommandResponse, DiscoveryResponse } from '../types';

const API_BASE = '/api';

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
};
