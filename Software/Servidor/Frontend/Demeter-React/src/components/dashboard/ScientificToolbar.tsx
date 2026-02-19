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
        <div className="flex items-center bg-slate-100 border border-slate-300 p-1 rounded-sm shadow-none">
            <div className="flex -space-x-px">
                <button
                    onClick={() => onChange('temperatura')}
                    className={cn(
                        "px-4 py-1.5 text-xs font-mono font-bold border border-slate-300 transition-colors uppercase tracking-tight",
                        selected === 'temperatura'
                            ? "bg-slate-700 text-white border-slate-700 z-10"
                            : "bg-white text-slate-600 hover:bg-slate-50"
                    )}
                >
                    [ MODE: TEMP ]
                </button>
                <button
                    onClick={() => onChange('humedad')}
                    className={cn(
                        "px-4 py-1.5 text-xs font-mono font-bold border border-slate-300 transition-colors uppercase tracking-tight",
                        selected === 'humedad'
                            ? "bg-slate-700 text-white border-slate-700 z-10"
                            : "bg-white text-slate-600 hover:bg-slate-50"
                    )}
                >
                    [ MODE: HUM ]
                </button>
            </div>
            <div className="ml-auto flex items-center gap-4 px-4 border-l border-slate-300">
                <span className="text-[10px] font-mono font-black text-slate-400 uppercase tracking-widest">Scientific Viz v1.0</span>
                <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 bg-green-600"></div>
                    <span className="text-[10px] font-mono text-slate-500">LIVE_STREAM</span>
                </div>
            </div>
        </div>
    );
};
