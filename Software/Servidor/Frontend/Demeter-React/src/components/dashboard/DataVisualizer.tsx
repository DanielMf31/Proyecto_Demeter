import React, { useState } from 'react';
import { SensorData, MetricType } from '../../types';
import { MetricToggle } from './MetricToggle';
import { SensorChart } from './SensorChart';
import { DataTable } from './DataTable';
import { Table as TableIcon } from 'lucide-react';

interface DataVisualizerProps {
    data: SensorData[];
}

export const DataVisualizer: React.FC<DataVisualizerProps> = ({ data }) => {
    const [metric, setMetric] = useState<MetricType>('temperatura');

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Visualizer Header with Toggle */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-2 bg-white/40 backdrop-blur-sm rounded-3xl border border-white/60 shadow-sm">
                <div className="flex items-center gap-3 px-4">
                    <div className="p-2 bg-white rounded-xl shadow-sm border border-slate-100 italic font-black text-blue-600">
                        DV
                    </div>
                    <div>
                        <h4 className="font-bold text-slate-800 text-sm">Laboratorio de Datos</h4>
                        <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tighter">Análisis Paramétrico</p>
                    </div>
                </div>

                <MetricToggle selected={metric} onChange={setMetric} />

                <div className="hidden lg:flex items-center gap-2 px-6 border-l border-slate-200">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Sincronizado</span>
                </div>
            </div>

            {/* Main Chart Section */}
            <section className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-100 to-orange-100 rounded-[2rem] blur opacity-20 group-hover:opacity-30 transition duration-1000"></div>
                <div className="relative">
                    <SensorChart data={data} metric={metric} />
                </div>
            </section>

            {/* Table Section with Heading */}
            <section className="pt-4">
                <div className="flex items-center gap-2 mb-6 ml-2">
                    <div className="p-2 bg-slate-900 text-white rounded-lg shadow-soft">
                        <TableIcon size={18} />
                    </div>
                    <h3 className="text-xl font-black text-slate-900 tracking-tight">Explorador de Registros</h3>
                </div>
                <DataTable data={data} />
            </section>
        </div>
    );
};
