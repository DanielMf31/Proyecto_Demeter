import React, { useState } from 'react';
import { SensorData, MetricType } from '../../types';
import { ScientificToolbar } from './ScientificToolbar';
import { ScientificChart } from './ScientificChart';
import { DataTable } from './DataTable';

interface ScientificDataVisualizerProps {
    data: SensorData[];
}

export const ScientificDataVisualizer: React.FC<ScientificDataVisualizerProps> = ({ data }) => {
    const [metric, setMetric] = useState<MetricType>('temperatura');

    return (
        <div className="flex flex-col gap-1 bg-slate-300 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-800 shadow-none rounded-none">
            {/* Top Section: Analysis Toolbar */}
            <section className="bg-slate-50 dark:bg-slate-900 p-4">
                <ScientificToolbar selected={metric} onChange={setMetric} />
            </section>

            {/* Mid Section: Telemetry Graph */}
            <section className="bg-white dark:bg-slate-900 p-6">
                <div className="flex items-center gap-3 mb-4 px-1">
                    <div className="w-2 h-5 bg-slate-800 dark:bg-blue-600"></div>
                    <h4 className="text-lg font-mono font-black text-slate-800 dark:text-white uppercase tracking-widest">Telemetry_Engine_Plot</h4>
                </div>
                <div className="h-[450px]">
                    <ScientificChart data={data} metric={metric} />
                </div>
            </section>

            {/* Bottom Section: Raw Buffer Table */}
            <section className="bg-white dark:bg-slate-900 p-6">
                <div className="flex items-center gap-3 mb-4 px-1">
                    <div className="w-2 h-5 bg-slate-800 dark:bg-blue-600"></div>
                    <h4 className="text-lg font-mono font-black text-slate-800 dark:text-white uppercase tracking-widest">Memory_Allocation_Buffer_Table</h4>
                </div>
                <DataTable data={data} />
            </section>

            {/* Footer Info */}
            <div className="bg-slate-100 dark:bg-slate-800/50 px-6 py-2 flex items-center justify-between">
                <span className="text-sm font-mono text-slate-500 font-bold tracking-tight">K_SYS_ID: DEMETER_SCADA_NODE_01</span>
                <span className="text-sm font-mono text-slate-500 font-bold tracking-tight">SYSTEM_TIME_STAMP: {new Date().toISOString()}</span>
            </div>
        </div>
    );
};
