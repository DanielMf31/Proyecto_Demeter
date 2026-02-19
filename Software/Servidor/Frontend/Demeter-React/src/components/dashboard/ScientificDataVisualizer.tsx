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
        <div className="flex flex-col gap-[1px] bg-slate-300 border border-slate-300 shadow-none rounded-none">
            {/* Top Section: Analysis Toolbar */}
            <section className="bg-slate-50 p-2">
                <ScientificToolbar selected={metric} onChange={setMetric} />
            </section>

            {/* Mid Section: Telemetry Graph */}
            <section className="bg-white p-3">
                <div className="flex items-center gap-2 mb-2 px-1">
                    <div className="w-1 h-3 bg-slate-800"></div>
                    <h4 className="text-[10px] font-mono font-black text-slate-800 uppercase">Telemetry_Engine_Plot_v1.0</h4>
                </div>
                <ScientificChart data={data} metric={metric} />
            </section>

            {/* Bottom Section: Raw Buffer Table */}
            <section className="bg-white p-3">
                <div className="flex items-center gap-2 mb-2 px-1">
                    <div className="w-1 h-3 bg-slate-800"></div>
                    <h4 className="text-[10px] font-mono font-black text-slate-800 uppercase">Memory_Buffer_Table</h4>
                </div>
                <DataTable data={data} />
            </section>

            {/* Footer Info */}
            <div className="bg-slate-100 px-4 py-1 flex items-center justify-between">
                <span className="text-[9px] font-mono text-slate-400">SYS_ID: DEMETER_SCADA_NODE_01</span>
                <span className="text-[9px] font-mono text-slate-400">STAMP: {new Date().toISOString()}</span>
            </div>
        </div>
    );
};
