import { create } from 'zustand';
import { DiscoveryConfig, makeSetGpio } from '../types';
import { apiService } from '../services/apiService';

interface DeviceState {
    devices: DiscoveryConfig;
    activeDevices: Set<string>; // ID format: 'pump-1', 'valve-5'
    status: 'online' | 'pending' | 'offline';
    isLoading: boolean;
    refreshDevices: () => Promise<void>;
    toggleDevice: (type: 'pump' | 'valve', id: string) => Promise<void>;
}

export const useDeviceStore = create<DeviceState>((set, get) => ({
    devices: {},
    activeDevices: new Set(),
    status: 'pending',
    isLoading: false,

    refreshDevices: async () => {
        set({ isLoading: true });
        const res = await apiService.fetchDevices();
        if (res) {
            set({ devices: res.devices, status: res.status, isLoading: false });
        } else {
            set({ status: 'offline', isLoading: false });
        }
    },

    toggleDevice: async (type, id) => {
        const { devices, activeDevices } = get();
        const config = devices[type]?.[id];
        if (!config) return;

        const idInt = parseInt(id, 10);
        const logicalPin = type === 'pump' ? idInt : idInt + 4;
        const key = `${type}-${id}`;
        const isCurrentlyActive = activeDevices.has(key);
        const nextState = !isCurrentlyActive;

        const cmd = makeSetGpio(logicalPin, nextState ? 1 : 0);
        const res = await apiService.postCommand(cmd);

        if (res && res.status !== 'error') {
            const newActive = new Set(activeDevices);
            if (nextState) {
                newActive.add(key);
            } else {
                newActive.delete(key);
            }
            set({ activeDevices: newActive });
        }
    },
}));
