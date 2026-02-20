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
import { AISidebar } from '../ai/AISidebar';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ExportDrawer } from './ExportDrawer';
import { useUIStore } from '../../store/useUIStore';
import { MOCK_SUMMARY } from '../../mocks/sensorData';
import { useTelemetry } from '../../hooks/useTelemetry';
import { apiService } from '../../services/apiService';
import { SensorData } from '../../types';

export const ExperimentDashboard: React.FC = () => {
    const { toggleAISidebar, currentView } = useUIStore();
    const [isExportDrawerOpen, setIsExportDrawerOpen] = useState(false);
    const [selectedNode, setSelectedNode] = useState<number>(1);
    const [historicalData, setHistoricalData] = useState<SensorData[]>([]);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);

    // Live Telemetry Hook (still running for status)
    const { isConnected } = useTelemetry(50);

    // Fetch 30-day metrics on mount and when node changes
    useEffect(() => {
        setIsLoadingHistory(true);
        apiService.fetchNodeHistory(selectedNode, 30).then(res => {
            if (res) {
                const processed = res.map(row => {
                    const T = row.temperature;
                    const RH = row.humidity;
                    // Calculate VPD
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
                        <div className="flex items-center justify-between border-b-2 border-slate-200 dark:border-slate-800 pb-6">
                            <div className="flex items-center gap-6">
                                <div className="bg-slate-100 dark:bg-slate-900 p-3 border border-slate-300 dark:border-slate-800">
                                    <Database size={32} className="text-slate-600 dark:text-slate-400" />
                                </div>
                                <div>
                                    <div className="flex items-center gap-3">
                                        <h1 className="text-3xl font-mono font-black tracking-tight text-slate-900 dark:text-white uppercase">
                                            {MOCK_SUMMARY.nombre}
                                        </h1>
                                        <span className={`px-2 py-0.5 font-mono text-xs font-bold border ${isConnected ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 border-green-300 dark:border-green-800' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-300 dark:border-red-800'}`}>
                                            {isConnected ? 'RUNNING' : 'OFFLINE'}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-6 text-sm font-mono text-slate-500 mt-2 uppercase">
                                        <span>Ref_ID: {MOCK_SUMMARY.id}</span>
                                        <span className="flex items-center gap-2">
                                            SELECT_NODE:
                                            <select
                                                value={selectedNode}
                                                onChange={(e) => setSelectedNode(Number(e.target.value))}
                                                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white font-bold px-2 py-1 ml-1 outline-none focus:ring-2 focus:ring-blue-500 rounded-none cursor-pointer"
                                            >
                                                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => (
                                                    <option key={n} value={n}>Planta {n}</option>
                                                ))}
                                            </select>
                                        </span>
                                        <span className="flex items-center gap-1.5 text-blue-600 dark:text-blue-400"><Info size={14} /> Kernel_v4.2.1-lts</span>
                                    </div>
                                </div>
                            </div>

                            <div className="hidden xl:flex gap-2">
                                <button
                                    onClick={handleExportRawData}
                                    className="flex items-center gap-3 px-5 py-2.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-xs font-mono font-bold hover:bg-slate-50 dark:hover:bg-slate-800 dark:text-slate-300 transition-colors"
                                >
                                    <Download size={16} /> EXPORT_RAW_CSV
                                </button>
                                <button
                                    onClick={handleOpenExportDrawer}
                                    className="flex items-center gap-3 px-5 py-2.5 text-white text-xs font-mono font-bold transition-colors border bg-slate-900 border-slate-900 dark:bg-blue-600 dark:border-blue-700 hover:bg-black dark:hover:bg-blue-700"
                                >
                                    <FileArchive size={16} /> DOWNLOAD_BUNDLE
                                </button>
                            </div>
                        </div>

                        {/* Summary View KPIs (Only in DATAVIZ) */}
                        {currentView === 'DATAVIZ' && (
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                <div className="border border-slate-300 dark:border-slate-800 p-6 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1 flex items-center gap-2"><Activity size={12} /> DATA_POINTS_LOADED</p>
                                    <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory ? '...' : historicalData.length}
                                        <span className="text-sm ml-2 text-slate-500 font-normal tracking-tight">/ 30 DAYS</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-6 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">AVG_TEMPERATURE</p>
                                    <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory || !historicalData.length ? '--' : (historicalData.reduce((acc, curr) => acc + curr.temperatura, 0) / historicalData.length).toFixed(1)}
                                        <span className="text-xl">°C</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-6 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                                    <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">AVG_HUMIDITY</p>
                                    <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white mt-2">
                                        {isLoadingHistory || !historicalData.length ? '--' : (historicalData.reduce((acc, curr) => acc + curr.humedad, 0) / historicalData.length).toFixed(1)}
                                        <span className="text-xl">%</span>
                                    </h3>
                                </div>
                                <div className="border border-slate-300 dark:border-slate-800 p-6 bg-white dark:bg-slate-900 shadow-sm flex items-center justify-between">
                                    <div>
                                        <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">SYSTEM_ALERTS</p>
                                        <h3 className="text-4xl font-mono font-black text-red-600 dark:text-red-500">0{MOCK_SUMMARY.alertas_activas}</h3>
                                    </div>
                                    <div className="w-4 h-4 bg-red-600 animate-pulse rounded-none"></div>
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
