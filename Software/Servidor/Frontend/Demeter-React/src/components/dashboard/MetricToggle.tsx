import React from 'react';
import { Thermometer, Droplets } from 'lucide-react';
import { MetricType } from '../../types';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

interface MetricToggleProps {
    selected: MetricType;
    onChange: (metric: MetricType) => void;
}

export const MetricToggle: React.FC<MetricToggleProps> = ({ selected, onChange }) => {
    return (
        <div className="inline-flex p-1 bg-slate-100 rounded-2xl border border-slate-200 shadow-inner">
            <button
                onClick={() => onChange('temperatura')}
                className={cn(
                    "flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-200",
                    selected === 'temperatura'
                        ? "bg-white text-orange-600 shadow-soft scale-100"
                        : "text-slate-500 hover:text-slate-700 hover:bg-slate-50/50"
                )}
            >
                <Thermometer size={18} className={selected === 'temperatura' ? "animate-pulse" : ""} />
                Temperatura
            </button>
            <button
                onClick={() => onChange('humedad')}
                className={cn(
                    "flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all duration-200",
                    selected === 'humedad'
                        ? "bg-white text-blue-600 shadow-soft scale-100"
                        : "text-slate-500 hover:text-slate-700 hover:bg-slate-50/50"
                )}
            >
                <Droplets size={18} className={selected === 'humedad' ? "animate-pulse" : ""} />
                Humedad
            </button>
        </div>
    );
};
