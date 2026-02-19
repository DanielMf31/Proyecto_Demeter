import { create } from 'zustand';

interface UIState {
    isAISidebarOpen: boolean;
    toggleAISidebar: () => void;
    setAISidebarOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
    isAISidebarOpen: false,
    toggleAISidebar: () => set((state) => ({ isAISidebarOpen: !state.isAISidebarOpen })),
    setAISidebarOpen: (open) => set({ isAISidebarOpen: open }),
}));
