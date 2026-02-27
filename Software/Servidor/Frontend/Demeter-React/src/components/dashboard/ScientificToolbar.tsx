import React from 'react';
import { MetricType } from '../../types';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

interface ScientificToolbarProps {
    selected: MetricType;
    onChange: (metric: MetricType) => void;
}

export const ScientificToolbar: React.FC<ScientificToolbarProps> = ({ selected, onChange }) => {
    return (
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 p-2 rounded-none shadow-none transition-colors">
            <div className="flex -space-x-px">
                <button
                    onClick={() => onChange('temperatura')}
                    className={cn(
                        "px-6 py-2.5 text-lg font-mono font-bold border transition-colors uppercase tracking-tight",
                        selected === 'temperatura'
                            ? "bg-slate-700 text-white border-slate-700 dark:bg-blue-600 dark:border-blue-600 z-10"
                            : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700 dark:hover:bg-slate-800"
                    )}
                >
                    [ MODE: TEMPERATURE_STREAM ]
                </button>
                <button
                    onClick={() => onChange('humedad')}
                    className={cn(
                        "px-6 py-2.5 text-lg font-mono font-bold border transition-colors uppercase tracking-tight",
                        selected === 'humedad'
                            ? "bg-slate-700 text-white border-slate-700 dark:bg-blue-600 dark:border-blue-600 z-10"
                            : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700 dark:hover:bg-slate-800"
                    )}
                >
                    [ MODE: HUMIDITY_STREAM ]
                </button>
                <button
                    onClick={() => onChange('vpd')}
                    className={cn(
                        "px-6 py-2.5 text-lg font-mono font-bold border transition-colors uppercase tracking-tight",
                        selected === 'vpd'
                            ? "bg-slate-700 text-white border-slate-700 dark:bg-blue-600 dark:border-blue-600 z-10"
                            : "bg-white text-slate-600 border-slate-300 hover:bg-slate-50 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700 dark:hover:bg-slate-800"
                    )}
                >
                    [ MODE: VPD_STREAM ]
                </button>
            </div>
            <div className="ml-auto flex items-center gap-6 px-6 border-l border-slate-300 dark:border-slate-700">
                <span className="text-base font-mono font-black text-slate-400 uppercase tracking-widest">Scientific Viz Engine</span>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-600 shadow-[0_0_8px_rgba(22,163,74,0.5)]"></div>
                    <span className="text-sm font-mono text-slate-500 font-bold">LIVE_TELEMETRY</span>
                </div>
            </div>
        </div>
    );
};
