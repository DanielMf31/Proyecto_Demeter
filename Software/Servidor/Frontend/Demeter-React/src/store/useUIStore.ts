import { create } from 'zustand';
import { ViewType } from '../types';

interface UIState {
    isAISidebarOpen: boolean;
    currentView: ViewType;
    toggleAISidebar: () => void;
    setAISidebarOpen: (open: boolean) => void;
    setCurrentView: (view: ViewType) => void;
}

export const useUIStore = create<UIState>((set) => ({
    isAISidebarOpen: false,
    currentView: 'DATAVIZ',
    toggleAISidebar: () => set((state) => ({ isAISidebarOpen: !state.isAISidebarOpen })),
    setAISidebarOpen: (open) => set({ isAISidebarOpen: open }),
    setCurrentView: (view) => set({ currentView: view }),
}));
