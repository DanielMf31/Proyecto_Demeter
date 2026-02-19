import React from 'react';
import { LayoutDashboard, Hand, ListTree, Activity } from 'lucide-react';
import { useUIStore } from '../../store/useUIStore';
import { ViewType } from '../../types';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

export const Sidebar: React.FC = () => {
    const { currentView, setCurrentView } = useUIStore();

    const navItems: { type: ViewType; label: string; Icon: any }[] = [
        { type: 'DATAVIZ', label: 'ANALYTICS', Icon: LayoutDashboard },
        { type: 'MANUAL', label: 'MANUAL_CTRL', Icon: Hand },
        { type: 'PLANNER', label: 'SEQ_PLANNER', Icon: ListTree },
    ];

    return (
        <aside className="w-16 md:w-48 bg-slate-900 dark:bg-black flex flex-col border-r border-slate-800 dark:border-slate-900 transition-all duration-300 select-none">
            <div className="p-4 border-b border-slate-800 flex items-center gap-3 bg-slate-800/50">
                <Activity size={20} className="text-blue-500 animate-pulse shrink-0" />
                <span className="hidden md:block font-mono text-[10px] font-black text-slate-400 uppercase tracking-widest">Demeter OS</span>
            </div>

            <nav className="flex-1 p-2 space-y-1">
                {navItems.map(({ type, label, Icon }) => (
                    <button
                        key={type}
                        onClick={() => setCurrentView(type)}
                        className={cn(
                            "w-full flex items-center gap-3 px-3 py-3 md:py-2.5 transition-all duration-200 group relative",
                            currentView === type
                                ? "bg-blue-600 text-white shadow-lg"
                                : "text-slate-400 hover:text-white hover:bg-slate-800"
                        )}
                        title={label}
                    >
                        <Icon size={18} className={cn("shrink-0", currentView === type ? "scale-110" : "group-hover:scale-110 transition-transform")} />
                        <span className="hidden md:block font-mono text-xs font-bold tracking-tight uppercase">
                            {label}
                        </span>
                        {currentView === type && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-white md:hidden"></div>
                        )}
                    </button>
                ))}
            </nav>

            <div className="p-4 border-t border-slate-800 bg-slate-800/30">
                <div className="hidden md:block text-[9px] font-mono text-slate-500 uppercase leading-tight">
                    System_Kernel: v4.2.1<br />
                    Status: [STABLE]
                </div>
            </div>
        </aside>
    );
};
