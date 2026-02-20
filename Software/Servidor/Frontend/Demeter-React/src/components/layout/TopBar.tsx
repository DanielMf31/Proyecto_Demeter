import React from 'react';
import { Moon, Sun, Search, Bell, Settings, Terminal as TerminalIcon } from 'lucide-react';
import { useThemeStore } from '../../store/useThemeStore';

export const TopBar: React.FC = () => {
    const { isDarkMode, toggleTheme } = useThemeStore();

    return (
        <nav className="h-16 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-300 flex items-center justify-between px-6 border-b border-slate-300 dark:border-slate-800 select-none transition-colors duration-200">
            <div className="flex items-center gap-8 h-full">
                <div className="flex items-center gap-3 px-4 h-full border-r border-slate-300 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                    <TerminalIcon size={20} className="text-blue-500" />
                    <span className="font-mono text-sm font-black tracking-tight uppercase">Demeter_Terminal</span>
                </div>

                <div className="hidden lg:flex items-center gap-4 bg-slate-100 dark:bg-slate-800 px-4 py-2 rounded-none border border-slate-300 dark:border-slate-700">
                    <Search size={16} className="text-slate-400" />
                    <input
                        type="text"
                        placeholder="RUN_QUERY_ENGINE..."
                        className="bg-transparent border-none focus:ring-0 text-sm font-mono w-64 text-slate-800 dark:text-slate-200 placeholder:text-slate-500 uppercase"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button
                    onClick={toggleTheme}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-300 dark:hover:border-slate-700 transition-all"
                    title={isDarkMode ? "SWITCH_MODE_LIGHT" : "SWITCH_MODE_DARK"}
                >
                    {isDarkMode ? <Sun size={20} className="text-orange-400" /> : <Moon size={20} className="text-indigo-400" />}
                </button>
                <div className="h-6 w-px bg-slate-300 dark:bg-slate-700"></div>
                <div className="flex items-center gap-4">
                    <Bell size={18} className="hover:text-blue-500 cursor-pointer transition-colors" />
                    <Settings size={18} className="hover:text-blue-500 cursor-pointer transition-colors" />
                    <div className="bg-slate-900 dark:bg-blue-900/30 text-white dark:text-blue-300 text-xs font-mono font-bold px-3 py-1.5 border border-slate-700 dark:border-blue-500/30">
                        OP_ADMIN
                    </div>
                </div>
            </div>
        </nav>
    );
};
