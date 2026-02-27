import React, { useEffect } from 'react';
import { useDeviceStore } from '../../store/useDeviceStore';
import { Power, Droplet, Waves, AlertOctagon } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

export const ManualControl: React.FC = () => {
    const { devices, refreshDevices, isLoading, status, toggleDevice, activeDevices } = useDeviceStore();

    useEffect(() => {
        refreshDevices();
    }, [refreshDevices]);

    const renderGrid = (type: 'pump' | 'valve') => {
        const group = devices[type];
        if (!group || Object.keys(group).length === 0) {
            return (
                <div className="h-32 flex items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-800 font-mono text-sm text-slate-400">
                    NO_DEVICES_DISCOVERED_IN_CLUSTER
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(group).map(([id, dev]) => {
                    const key = `${type}-${id}`;
                    const isActive = activeDevices.has(key);

                    return (
                        <div key={id} className="bg-white dark:bg-slate-900 p-6 border-2 border-slate-200 dark:border-slate-800 transition-colors">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-4">
                                    <div className={cn(
                                        "p-3 rounded-none border-2 shadow-none transition-colors",
                                        type === 'pump'
                                            ? (isActive ? "text-white bg-blue-600 border-blue-700" : "text-blue-500 bg-blue-50 dark:bg-blue-900/10 border-slate-200 dark:border-slate-800")
                                            : (isActive ? "text-white bg-emerald-600 border-emerald-700" : "text-emerald-500 bg-emerald-50 dark:bg-emerald-900/10 border-slate-200 dark:border-slate-800")
                                    )}>
                                        {type === 'pump' ? <Waves size={24} /> : <Droplet size={24} />}
                                    </div>
                                    <div>
                                        <h4 className="font-mono text-lg font-black text-slate-800 dark:text-slate-200 uppercase tracking-tighter">{dev.label}</h4>
                                        <p className="font-mono text-xs text-slate-400">PTR: {type === 'pump' ? 'P' : 'V'}_0{id} (GPIO_{dev.physical_pin})</p>
                                    </div>
                                </div>
                                <div className={cn(
                                    "w-3 h-3 rounded-none animate-pulse",
                                    isActive ? "bg-red-600 shadow-[0_0_10px_rgba(220,38,38,0.5)]" : "bg-slate-300 dark:bg-slate-800"
                                )}></div>
                            </div>

                            <button
                                onClick={() => toggleDevice(type, id)}
                                className={cn(
                                    "w-full py-3 border-2 font-mono text-xs font-black uppercase tracking-widest transition-all",
                                    isActive
                                        ? "bg-red-600 text-white border-red-800 hover:bg-red-700"
                                        : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700 hover:bg-slate-900 dark:hover:bg-blue-600 hover:text-white"
                                )}
                            >
                                [ {isActive ? "TERMINATE_FLOW" : "EXEC_INITIATE"} ]
                            </button>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="flex flex-col gap-10 animate-in fade-in duration-500">
            {/* Manual Toolbar */}
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 border-2 border-slate-300 dark:border-slate-800">
                <div className="flex items-center gap-4 px-3">
                    <div className="w-3 h-8 bg-orange-600"></div>
                    <div>
                        <h2 className="font-mono text-lg font-black text-slate-800 dark:text-white uppercase tracking-tighter">Manual_Override_Panel_v2</h2>
                        <p className="font-mono text-xs text-slate-500 uppercase">Station_Status: [{status}]</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => refreshDevices()}
                        className="px-5 py-2.5 bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-700 font-mono text-xs font-black uppercase text-slate-600 dark:text-slate-400 hover:border-slate-800 transition-all"
                        disabled={isLoading}
                    >
                        {isLoading ? "REFRESHING..." : "[ DISCOVER_DEVICES ]"}
                    </button>
                    <button className="flex items-center gap-3 px-5 py-2.5 bg-red-700 text-white font-mono text-xs font-black uppercase hover:bg-red-800 shadow-none border-2 border-red-900">
                        <AlertOctagon size={18} />
                        [ EMERGENCY_TERMINATE ]
                    </button>
                </div>
            </div>

            {/* Pumps Section */}
            <section>
                <div className="flex items-center gap-3 mb-5 ml-1">
                    <Power size={22} className="text-blue-500" />
                    <h3 className="font-mono text-xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">Bomba_Control_Cluster</h3>
                    <div className="h-0.5 bg-slate-200 dark:bg-slate-800 flex-1 ml-4"></div>
                </div>
                {renderGrid('pump')}
            </section>

            {/* Valves Section */}
            <section>
                <div className="flex items-center gap-3 mb-5 ml-1">
                    <Droplet size={22} className="text-emerald-500" />
                    <h3 className="font-mono text-xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">Valvula_Control_Cluster</h3>
                    <div className="h-0.5 bg-slate-200 dark:bg-slate-800 flex-1 ml-4"></div>
                </div>
                {renderGrid('valve')}
            </section>
        </div>
    );
};
