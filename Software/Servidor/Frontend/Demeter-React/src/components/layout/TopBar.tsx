import React from 'react';
import { Moon, Sun, Search, Bell, Settings, Terminal as TerminalIcon } from 'lucide-react';
import { useThemeStore } from '../../store/useThemeStore';

export const TopBar: React.FC = () => {
    const { isDarkMode, toggleTheme } = useThemeStore();

    return (
        <nav className="h-12 bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-300 flex items-center justify-between px-4 border-b border-slate-300 dark:border-slate-800 select-none transition-colors duration-200">
            <div className="flex items-center gap-6 h-full">
                <div className="flex items-center gap-2 px-3 h-full border-r border-slate-300 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                    <TerminalIcon size={14} className="text-blue-500" />
                    <span className="font-mono text-[10px] font-black tracking-tighter uppercase">Demeter_Terminal</span>
                </div>

                <div className="hidden md:flex items-center gap-3 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-sm border border-slate-300 dark:border-slate-700">
                    <Search size={12} className="text-slate-400" />
                    <input
                        type="text"
                        placeholder="RUN_QUERY..."
                        className="bg-transparent border-none focus:ring-0 text-[10px] font-mono w-48 text-slate-800 dark:text-slate-200 placeholder:text-slate-500 uppercase"
                    />
                </div>
            </div>

            <div className="flex items-center gap-4">
                <button
                    onClick={toggleTheme}
                    className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-sm border border-transparent hover:border-slate-300 dark:hover:border-slate-700 transition-all"
                    title={isDarkMode ? "SWITCH_MODE_LIGHT" : "SWITCH_MODE_DARK"}
                >
                    {isDarkMode ? <Sun size={14} className="text-orange-400" /> : <Moon size={14} className="text-indigo-400" />}
                </button>
                <div className="h-4 w-px bg-slate-300 dark:bg-slate-700"></div>
                <div className="flex items-center gap-3">
                    <Bell size={14} className="hover:text-blue-500 cursor-pointer transition-colors" />
                    <Settings size={14} className="hover:text-blue-500 cursor-pointer transition-colors" />
                    <div className="bg-slate-900 dark:bg-blue-900/30 text-white dark:text-blue-300 text-[10px] font-mono font-bold px-2 py-1 border border-slate-700 dark:border-blue-500/30">
                        OP_ADMIN
                    </div>
                </div>
            </div>
        </nav>
    );
};
