import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
    isDarkMode: boolean;
    toggleTheme: () => void;
    setTheme: (isDark: boolean) => void;
}

export const useThemeStore = create<ThemeState>()(
    persist(
        (set) => ({
            isDarkMode: false,
            toggleTheme: () => set((state) => {
                const next = !state.isDarkMode;
                if (next) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                return { isDarkMode: next };
            }),
            setTheme: (isDark) => {
                if (isDark) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                set({ isDarkMode: isDark });
            },
        }),
        {
            name: 'demeter-theme-storage',
        }
    )
);
