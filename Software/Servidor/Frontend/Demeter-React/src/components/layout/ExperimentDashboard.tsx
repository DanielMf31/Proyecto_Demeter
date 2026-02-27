import React, { useState, useEffect } from 'react';
import {
    Database,
    Download,
    FileArchive,
    Info,
    Sparkles,
    Activity
} from 'lucide-react';
import { ScientificDataVisualizer } from '../dashboard/ScientificDataVisualizer';
import { ManualControl } from '../dashboard/ManualControl';
import { SequencePlanner } from '../dashboard/SequencePlanner';
import { LIMS_Dashboard } from '../lims/LIMS_Dashboard';
import { AISidebar } from '../ai/AISidebar';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ExportDrawer } from './ExportDrawer';
import { useUIStore } from '../../store/useUIStore';
import { useTelemetry } from '../../hooks/useTelemetry';
import { apiService } from '../../services/apiService';
import { SensorData, ExperimentLIMS } from '../../types';

export const ExperimentDashboard: React.FC = () => {
    const { toggleAISidebar, currentView } = useUIStore();
    const [isExportDrawerOpen, setIsExportDrawerOpen] = useState(false);
    const [selectedNode, setSelectedNode] = useState<number>(1);
    const [historicalData, setHistoricalData] = useState<SensorData[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);

    // Experiment Selector State
    const [experiments, setExperiments] = useState<ExperimentLIMS[]>([]);
    const [selectedExpId, setSelectedExpId] = useState<number | null>(null);

    // Live Telemetry Hook (still running for status)
    const { isConnected } = useTelemetry(50);

    // Fetch experiments on mount
    useEffect(() => {
        apiService.fetchExperiments().then(res => {
            if (res && res.length > 0) {
                setExperiments(res);
                setSelectedExpId(res[0].id);
            }
        });
    }, []);

    const selectedExperiment = experiments.find(e => e.id === selectedExpId);

    // Fetch 30-day metrics when node changes
    useEffect(() => {
        setIsLoadingHistory(true);
        apiService.fetchNodeHistory(selectedNode, 30).then(res => {
            if (res) {
                const processed = res.map(row => {
                    const T = row.temperature;
                    const RH = row.humidity;
                    const svp = 0.61078 * Math.exp((17.27 * T) / (T + 237.3));
                    const avp = svp * (RH / 100.0);
                    const vpd = svp - avp;
                    return {
                        timestamp: row.timestamp,
                        temperatura: T,
                        humedad: RH,
                        vpd: vpd
                    } as SensorData;
                });
                setHistoricalData(processed);
            }
            setIsLoadingHistory(false);
        });
    }, [selectedNode]);

    const handleExportRawData = () => {
        // Mock CSV generation
        const headers = ['timestamp', 'temperatura', 'humedad', 'vpd'];
        const csvContent = "data:text/csv;charset=utf-8,"
            + headers.join(",") + "\n"
            + historicalData.map(row => `${row.timestamp},${row.temperatura.toFixed(2)},${row.humedad.toFixed(2)},${row.vpd?.toFixed(2) || 0}`).join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `demeter_history_planta_${selectedNode}_${Date.now()}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleOpenExportDrawer = () => {
        setIsExportDrawerOpen(true);
    };

    const renderViewContent = () => {
        switch (currentView) {
            case 'DATAVIZ':
                return <ScientificDataVisualizer data={historicalData} />;
            case 'MANUAL':
                return <ManualControl />;
            case 'PLANNER':
                return <SequencePlanner />;
            case 'LIMS_CATALOG':
                return <LIMS_Dashboard />;
            default:
                return <ScientificDataVisualizer data={historicalData} />;
        }
    };

    return (
        <div className="flex bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
            <Sidebar />

            <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
                <TopBar />

                <main className="flex-1 p-10 overflow-y-auto selection:bg-blue-100 dark:selection:bg-blue-900/30">
                    <div className="max-w-[1600px] mx-auto space-y-10">

                        {/* Status Header Strip */}
                        <div className="flex items-center justify-between border-b-2 border-slate-200 dark:border-slate-800 pb-8">
                            <div className="flex items-center gap-6">
                                <div className="bg-slate-100 dark:bg-slate-900 p-4 border border-slate-300 dark:border-slate-800">
                                    <Database size={40} className="text-slate-600 dark:text-slate-400" />
                                </div>
                                <div>
                                    <div className="flex items-center gap-4">
                                        <h1 className="text-4xl font-mono font-black tracking-tight text-slate-900 dark:text-white uppercase">
                                            {selectedExperiment?.name || 'Demeter Dashboard'}
                                        </h1>
                                        <span className={`px-3 py-1 font-mono text-sm font-bold border ${isConnected ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border-green-300 dark:border-green-800' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-800'}`}>
                                            {isConnected ? 'RUNNING' : 'OFFLINE'}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-5 text-base font-mono text-slate-500 mt-3 uppercase flex-wrap">
                                        <span className="flex items-center gap-2">
                                            EXPERIMENTO:
                                            <select
                                                value={selectedExpId || ''}
                                                onChange={(e) => setSelectedExpId(Number(e.target.value))}
                                                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white font-bold text-base px-3 py-1.5 ml-1 outline-none focus:ring-2 focus:ring-blue-500 rounded-none cursor-pointer"
                                            >
                                                {experiments.map(exp => (
                                                    <option key={exp.id} value={exp.id}>{exp.name}</option>
                                                ))}
                                            </select>
                                        </span>
                                        <span className="flex items-center gap-2">
                                            PLANTA:
                                            <select
                                                value={selectedNode}
                                                onChange={(e) => setSelectedNode(Number(e.target.value))}
                                                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white font-bold text-base px-3 py-1.5 ml-1 outline-none focus:ring-2 focus:ring-blue-500 rounded-none cursor-pointer"
                                            >
                                                {(selectedExperiment?.plants || []).map(p => (
                                                    <option key={p.node_id} value={p.node_id}>{p.name}</option>
                                                ))}
                                                {(!selectedExperiment?.plants?.length) && (
                                                    <option value={1}>Planta 1</option>
                                                )}
                                            </select>
                                        </span>
                                        <span className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                                            <Info size={16} /> Kernel_v4.2.1-lts
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="hidden xl:flex gap-3">
                                <button
                                    onClick={handleExportRawData}
                                    className="flex items-center gap-3 px-6 py-3 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-sm font-mono font-bold hover:bg-slate-50 dark:hover:bg-slate-800 dark:text-slate-300 transition-colors"
                                >
                                    <Download size={18} /> EXPORT_CSV
                                </button>
                                <button
                                    onClick={handleOpenExportDrawer}
                                    className="flex items-center gap-3 px-6 py-3 text-white text-sm font-mono font-bold transition-colors border bg-slate-900 border-slate-900 dark:bg-blue-600 dark:border-blue-700 hover:bg-black dark:hover:bg-blue-700"
                                >
                                    <FileArchive size={18} /> BUNDLE
                                </button>
                            </div>
                        </div>

                        {/* Summary View KPIs (Only in DATAVIZ) */}
                        {currentView === 'DATAVIZ' && (
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                <div className="border border-slate-300 dark:border-slate-800 p-8 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-base font-mono font-bold text-slate-500 uppercase mb-2 flex items-center gap-2">
                                        <Activity size={16} /> DATA_POINTS
                                    </p>
                                    <h3 className="text-5xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory ? '...' : historicalData.length}
                                        <span className="text-lg ml-2 text-slate-500 font-normal tracking-tight">/ 30d</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-8 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-base font-mono font-bold text-slate-500 uppercase mb-2">AVG_TEMPERATURE</p>
                                    <h3 className="text-5xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory || !historicalData.length ? '--' : (historicalData.reduce((acc, curr) => acc + curr.temperatura, 0) / historicalData.length).toFixed(1)}
                                        <span className="text-2xl">°C</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-8 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-base font-mono font-bold text-slate-500 uppercase mb-2">AVG_HUMIDITY</p>
                                    <h3 className="text-5xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory || !historicalData.length ? '--' : (historicalData.reduce((acc, curr) => acc + curr.humedad, 0) / historicalData.length).toFixed(1)}
                                        <span className="text-2xl">%</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-8 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
                                    <div>
                                        <p className="text-base font-mono font-bold text-slate-500 uppercase mb-2">PLANTS_IN_EXP</p>
                                        <h3 className="text-5xl font-mono font-black text-red-600 dark:text-red-500">{selectedExperiment?.plants?.length || 0}</h3>
                                    </div>
                                    <div className="w-5 h-5 bg-red-600 animate-pulse rounded-none"></div>
                                </div>
                            </div>
                        )}

                        {/* View Content Wrapper */}
                        <div className="pb-10">
                            {renderViewContent()}
                        </div>
                    </div>
                </main>
            </div>

            {/* AI Call-to-Action */}
            <button
                onClick={toggleAISidebar}
                className="fixed bottom-10 right-10 flex items-center gap-3 px-8 py-5 bg-slate-900 dark:bg-blue-600 text-white font-mono font-bold text-sm border-t-4 border-blue-500 dark:border-white shadow-2xl hover:bg-black dark:hover:bg-blue-700 transition-all z-40 uppercase tracking-widest"
            >
                <Sparkles size={20} />
                Initialize_AI_Core
            </button>

            <AISidebar />
            <ExportDrawer isOpen={isExportDrawerOpen} onClose={() => setIsExportDrawerOpen(false)} />
        </div>
    );
};
