import React, { useState } from 'react';
import {
    Database,
    Download,
    FileArchive,
    Info,
    Sparkles
} from 'lucide-react';
import { ScientificDataVisualizer } from '../dashboard/ScientificDataVisualizer';
import { ManualControl } from '../dashboard/ManualControl';
import { SequencePlanner } from '../dashboard/SequencePlanner';
import { AISidebar } from '../ai/AISidebar';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { useUIStore } from '../../store/useUIStore';
import { generateMockSensorData, MOCK_SUMMARY } from '../../mocks/sensorData';

export const ExperimentDashboard: React.FC = () => {
    const [data] = useState(generateMockSensorData());
    const { toggleAISidebar, currentView } = useUIStore();

    const renderViewContent = () => {
        switch (currentView) {
            case 'DATAVIZ':
                return <ScientificDataVisualizer data={data} />;
            case 'MANUAL':
                return <ManualControl />;
            case 'PLANNER':
                return <SequencePlanner />;
            default:
                return <ScientificDataVisualizer data={data} />;
        }
    };

    return (
        <div className="flex bg-white dark:bg-slate-950 transition-colors duration-200">
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
                                        <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 font-mono text-xs font-bold border border-green-300 dark:border-green-800">RUNNING</span>
                                    </div>
                                    <div className="flex items-center gap-6 text-sm font-mono text-slate-500 mt-2 uppercase">
                                        <span>Ref_ID: {MOCK_SUMMARY.id}</span>
                                        <span>Start_Sync: {MOCK_SUMMARY.fecha_inicio}</span>
                                        <span className="flex items-center gap-1.5 text-blue-600 dark:text-blue-400"><Info size={14} /> Kernel_v4.2.1-lts</span>
                                    </div>
                                </div>
                            </div>

                            <div className="hidden xl:flex gap-2">
                                <button className="flex items-center gap-3 px-5 py-2.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-xs font-mono font-bold hover:bg-slate-50 dark:hover:bg-slate-800 dark:text-slate-300 transition-colors">
                                    <Download size={16} /> EXPORT_RAW_DATA
                                </button>
                                <button className="flex items-center gap-3 px-5 py-2.5 bg-slate-900 dark:bg-blue-600 text-white text-xs font-mono font-bold hover:bg-black dark:hover:bg-blue-700 transition-colors border border-slate-900 dark:border-blue-700">
                                    <FileArchive size={16} /> DOWNLOAD_BUNDLE
                                </button>
                            </div>
                        </div>

                        {/* Summary View KPIs (Only in DATAVIZ) */}
                        {currentView === 'DATAVIZ' && (
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                                <div className="border-2 border-slate-300 dark:border-slate-800 p-6 bg-slate-50 dark:bg-slate-900 flex items-center justify-between">
                                    <div>
                                        <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">AVG_TEMPERATURE</p>
                                        <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white">24.85<span className="text-xl">°C</span></h3>
                                    </div>
                                    <div className="text-xs font-mono text-green-600 bg-green-50 dark:bg-green-900/10 px-2 py-0.5 border border-green-200 dark:border-green-800">+2.4%</div>
                                </div>
                                <div className="border-2 border-slate-300 dark:border-slate-800 p-6 bg-slate-50 dark:bg-slate-900 flex items-center justify-between">
                                    <div>
                                        <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">MAX_HUMIDITY</p>
                                        <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white">68.21<span className="text-xl">%</span></h3>
                                    </div>
                                    <div className="text-xs font-mono text-red-600 bg-red-50 dark:bg-red-900/10 px-2 py-0.5 border border-red-200 dark:border-red-800">-1.2%</div>
                                </div>
                                <div className="border-2 border-slate-300 dark:border-slate-800 p-6 bg-slate-50 dark:bg-slate-900">
                                    <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">VALVE_SYSTEM_STATUS</p>
                                    <h3 className="text-4xl font-mono font-black text-slate-900 dark:text-white uppercase">STABLE_v1</h3>
                                </div>
                                <div className="border-2 border-slate-300 dark:border-slate-800 p-6 bg-slate-50 dark:bg-slate-900 flex items-center justify-between">
                                    <div>
                                        <p className="text-xs font-mono font-bold text-slate-500 uppercase mb-1">ACTIVE_ALERTS</p>
                                        <h3 className="text-4xl font-mono font-black text-red-700 dark:text-red-500">0{MOCK_SUMMARY.alertas_activas}</h3>
                                    </div>
                                    <div className="w-4 h-4 bg-red-600 animate-pulse"></div>
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
        </div>
    );
};
