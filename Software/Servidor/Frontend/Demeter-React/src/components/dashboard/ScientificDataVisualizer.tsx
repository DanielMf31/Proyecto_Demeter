import React, { useState, useMemo } from 'react';
import { SensorData, MetricType } from '../../types';
import { ScientificToolbar } from './ScientificToolbar';
import { ScientificChart } from './ScientificChart';
import { DataTable } from './DataTable';
import { Calendar, Filter } from 'lucide-react';

interface ScientificDataVisualizerProps {
    data: SensorData[];
}

type FilterView = 'TODOS' | 'LAST_7' | 'SPECIFIC_DAY';

export const ScientificDataVisualizer: React.FC<ScientificDataVisualizerProps> = ({ data }) => {
    const [metric, setMetric] = useState<MetricType>('temperatura');
    const [filterView, setFilterView] = useState<FilterView>('TODOS');
    const [specificDate, setSpecificDate] = useState<string>(new Date().toISOString().split('T')[0]);

    const filteredData = useMemo(() => {
        if (!data || data.length === 0) return [];
        switch (filterView) {
            case 'TODOS':
                return data;
            case 'LAST_7': {
                const latestDate = new Date(data[data.length - 1].timestamp);
                const sevenDaysAgo = new Date(latestDate);
                sevenDaysAgo.setDate(latestDate.getDate() - 7);
                return data.filter(d => new Date(d.timestamp) >= sevenDaysAgo);
            }
            case 'SPECIFIC_DAY':
                if (!specificDate) return data;
                return data.filter(d => d.timestamp.startsWith(specificDate));
            default:
                return data;
        }
    }, [data, filterView, specificDate]);

    return (
        <div className="flex flex-col gap-1 bg-slate-300 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-800 shadow-none rounded-none">
            {/* Toolbar */}
            <section className="bg-slate-50 dark:bg-slate-900 p-5">
                <ScientificToolbar selected={metric} onChange={setMetric} />
            </section>

            {/* Chart section */}
            <section className="bg-white dark:bg-slate-900 p-7">
                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 mb-6 px-1">
                    <div className="flex items-center gap-3">
                        <div className="w-2 h-7 bg-slate-800 dark:bg-blue-600"></div>
                        <h4 className="text-xl font-mono font-black text-slate-800 dark:text-white uppercase tracking-widest">
                            Telemetry Engine Plot
                        </h4>
                    </div>

                    {/* Time range filter */}
                    <div className="flex items-center gap-3 bg-slate-100 dark:bg-slate-800 p-3 border border-slate-300 dark:border-slate-700">
                        <Filter size={20} className="text-slate-500" />
                        <select
                            value={filterView}
                            onChange={(e) => setFilterView(e.target.value as FilterView)}
                            className="bg-white dark:bg-slate-900 text-slate-800 dark:text-white font-mono text-base border border-slate-300 dark:border-slate-700 px-4 py-2.5 outline-none focus:border-blue-500"
                        >
                            <option value="TODOS">Últimos 30 Días</option>
                            <option value="LAST_7">Últimos 7 Días</option>
                            <option value="SPECIFIC_DAY">Día Específico</option>
                        </select>

                        {filterView === 'SPECIFIC_DAY' && (
                            <div className="flex items-center gap-2">
                                <Calendar size={20} className="text-slate-500" />
                                <input
                                    type="date"
                                    value={specificDate}
                                    onChange={(e) => setSpecificDate(e.target.value)}
                                    className="bg-white dark:bg-slate-900 text-slate-800 dark:text-white font-mono text-base border border-slate-300 dark:border-slate-700 px-4 py-2.5 outline-none focus:border-blue-500 [color-scheme:light] dark:[color-scheme:dark]"
                                />
                            </div>
                        )}
                        <span className="text-base font-mono font-bold text-slate-500 ml-4 hidden md:inline">
                            {filteredData.length.toLocaleString()} REGISTROS
                        </span>
                    </div>
                </div>

                <div className="h-[480px]">
                    <ScientificChart data={filteredData} metric={metric} />
                </div>
            </section>

            {/* Table section */}
            <section className="bg-white dark:bg-slate-900 p-7">
                <div className="flex items-center gap-3 mb-6 px-1">
                    <div className="w-2 h-7 bg-slate-800 dark:bg-blue-600"></div>
                    <h4 className="text-xl font-mono font-black text-slate-800 dark:text-white uppercase tracking-widest">
                        Memory Allocation Buffer Table
                    </h4>
                </div>
                <DataTable data={filteredData} />
            </section>

            {/* Footer */}
            <div className="bg-slate-100 dark:bg-slate-800/50 px-7 py-3 flex items-center justify-between">
                <span className="text-base font-mono text-slate-500 font-bold tracking-tight">K_SYS_ID: DEMETER_SCADA_NODE_01</span>
                <span className="text-base font-mono text-slate-500 font-bold tracking-tight">
                    SYS_TIME: {new Date().toISOString()}
                </span>
            </div>
        </div>
    );
};
