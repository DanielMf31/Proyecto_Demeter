import React, { useState } from 'react';
import {
    Terminal,
    Cpu,
    Database,
    Settings,
    Bell,
    Search,
    Download,
    FileArchive,
    Calendar,
    Sparkles,
    Info
} from 'lucide-react';
import { KPICard } from '../dashboard/KPICard';
import { ScientificDataVisualizer } from '../dashboard/ScientificDataVisualizer';
import { AISidebar } from '../ai/AISidebar';
import { useUIStore } from '../../store/useUIStore';
import { generateMockSensorData, MOCK_SUMMARY } from '../../mocks/sensorData';

export const ExperimentDashboard: React.FC = () => {
    const [data] = useState(generateMockSensorData());
    const { toggleAISidebar } = useUIStore();

    return (
        <div className="min-h-screen bg-white text-slate-800 font-sans selection:bg-slate-200">
            {/* Scientific Header / Command Bar */}
            <nav className="h-12 bg-slate-900 text-slate-300 flex items-center justify-between px-4 border-b border-slate-700 select-none">
                <div className="flex items-center gap-6 h-full">
                    <div className="flex items-center gap-2 px-2 h-full border-r border-slate-700 bg-slate-800">
                        <Terminal size={14} className="text-blue-400" />
                        <span className="font-mono text-xs font-bold tracking-tighter text-white">DEMETER_CORE_v2.0</span>
                    </div>

                    <div className="flex items-center gap-4 text-[10px] font-mono font-bold uppercase tracking-widest">
                        <a href="#" className="hover:text-white transition-colors text-white">Dashboard</a>
                        <a href="#" className="hover:text-white transition-colors">Nodes_List</a>
                        <a href="#" className="hover:text-white transition-colors">Config_Sys</a>
                        <a href="#" className="hover:text-white transition-colors">Logs_Engine</a>
                    </div>
                </div>

                <div className="flex items-center gap-4 h-full">
                    <div className="flex items-center bg-slate-800 px-2 py-1 rounded-sm border border-slate-700">
                        <Search size={12} className="text-slate-500" />
                        <input
                            type="text"
                            placeholder="QUICK_SEARCH..."
                            className="bg-transparent border-none focus:ring-0 text-[10px] font-mono ml-2 w-40 text-slate-300 placeholder:text-slate-600"
                        />
                    </div>
                    <div className="h-4 w-px bg-slate-700"></div>
                    <div className="flex items-center gap-3">
                        <Bell size={14} className="hover:text-white cursor-pointer" />
                        <Settings size={14} className="hover:text-white cursor-pointer" />
                        <div className="flex items-center gap-2 ml-2 px-2 py-1 bg-blue-900/30 border border-blue-500/30 rounded-sm">
                            <Cpu size={12} className="text-blue-400" />
                            <span className="text-[10px] font-mono font-bold text-blue-300">ADMIN_LOCAL</span>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="p-6 max-w-full">
                {/* Top Info Strip */}
                <div className="flex items-center justify-between border-b border-slate-300 pb-4 mb-6">
                    <div className="flex items-center gap-4">
                        <div className="bg-slate-100 p-2 border border-slate-300 rounded-none">
                            <Database size={24} className="text-slate-600" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-2xl font-mono font-black tracking-tight text-slate-900 uppercase">
                                    {MOCK_SUMMARY.nombre}
                                </h1>
                                <span className="px-1.5 py-0.5 bg-green-100 text-green-800 font-mono text-[9px] font-bold border border-green-300">RUNNING</span>
                            </div>
                            <div className="flex items-center gap-4 text-[10px] font-mono text-slate-500 mt-1 uppercase">
                                <span>Ref_ID: {MOCK_SUMMARY.id}</span>
                                <span>Start_Sync: {MOCK_SUMMARY.fecha_inicio}</span>
                                <span className="flex items-center gap-1 text-blue-600"><Info size={10} /> Kernel_v4.2.1-lts</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-1">
                        <button className="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-300 text-xs font-mono font-bold hover:bg-slate-50 rounded-none">
                            <Download size={14} /> EXPORT_RAW
                        </button>
                        <button className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 text-white text-xs font-mono font-bold hover:bg-slate-900 rounded-none">
                            <FileArchive size={14} /> DOWNLOAD_BUNDLE
                        </button>
                    </div>
                </div>

                {/* Dense KPI Strip */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="border border-slate-300 p-3 bg-slate-50 flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-mono font-bold text-slate-500 uppercase">AVG_TEMP</p>
                            <h3 className="text-xl font-mono font-black text-slate-900">24.85<span className="text-sm">°C</span></h3>
                        </div>
                        <div className="text-[10px] font-mono text-green-600 bg-green-50 px-1 border border-green-200">+2.4%</div>
                    </div>
                    <div className="border border-slate-300 p-3 bg-slate-50 flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-mono font-bold text-slate-500 uppercase">MAX_HUM</p>
                            <h3 className="text-xl font-mono font-black text-slate-900">68.21<span className="text-sm">%</span></h3>
                        </div>
                        <div className="text-[10px] font-mono text-red-600 bg-red-50 px-1 border border-red-200">-1.2%</div>
                    </div>
                    <div className="border border-slate-300 p-3 bg-slate-50">
                        <p className="text-[10px] font-mono font-bold text-slate-500 uppercase">VALVE_SYSTEM</p>
                        <h3 className="text-xl font-mono font-black text-slate-900 uppercase">STABLE_v1</h3>
                    </div>
                    <div className="border border-slate-300 p-3 bg-slate-50 flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-mono font-bold text-slate-500 uppercase">ACTIVE_ALERTS</p>
                            <h3 className="text-xl font-mono font-black text-red-700">0{MOCK_SUMMARY.alertas_activas}</h3>
                        </div>
                        <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></div>
                    </div>
                </div>

                {/* Main Scientific Visualization Wrapper */}
                <ScientificDataVisualizer data={data} />
            </main>

            {/* Industrial Floating Button */}
            <button
                onClick={toggleAISidebar}
                className="fixed bottom-6 right-6 flex items-center gap-2 px-4 py-3 bg-slate-900 text-white font-mono font-bold text-xs rounded-none border-t-2 border-blue-500 shadow-2xl hover:bg-black transition-all z-40 uppercase tracking-widest"
            >
                <Sparkles size={16} />
                Initialize_AI_Core
            </button>

            {/* AI Sidebar */}
            <AISidebar />
        </div>
    );
};
