import React, { useEffect } from 'react';
import { useDeviceStore } from '../../store/useDeviceStore';
import { Power, Droplet, Waves, AlertOctagon } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

export const ManualControl: React.FC = () => {
    const { devices, refreshDevices, isLoading, status } = useDeviceStore();

    useEffect(() => {
        refreshDevices();
    }, [refreshDevices]);

    const renderGrid = (type: 'pump' | 'valve') => {
        const group = devices[type];
        if (!group || Object.keys(group).length === 0) {
            return (
                <div className="h-24 flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-800 font-mono text-[10px] text-slate-400">
                    NO_DEVICES_DISCOVERED
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-px bg-slate-300 dark:bg-slate-800 border border-slate-300 dark:border-slate-800">
                {Object.entries(group).map(([id, dev]) => (
                    <div key={id} className="bg-white dark:bg-slate-900 p-4 transition-colors">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className={cn(
                                    "p-2 rounded-none border border-slate-300 dark:border-slate-700 shadow-none transition-colors",
                                    type === 'pump' ? "text-blue-500 bg-blue-50 dark:bg-blue-900/10" : "text-emerald-500 bg-emerald-50 dark:bg-emerald-900/10"
                                )}>
                                    {type === 'pump' ? <Waves size={16} /> : <Droplet size={16} />}
                                </div>
                                <div>
                                    <h4 className="font-mono text-xs font-black text-slate-800 dark:text-slate-200 uppercase tracking-tight">{dev.label}</h4>
                                    <p className="font-mono text-[9px] text-slate-400">ID: {type === 'pump' ? 'P' : 'V'}-0{id}</p>
                                </div>
                            </div>
                            <div className="w-2 h-2 rounded-none bg-slate-300 dark:bg-slate-700"></div>
                        </div>

                        <button className="w-full py-2 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-[10px] font-black uppercase tracking-widest text-slate-600 dark:text-slate-400 hover:bg-slate-900 dark:hover:bg-blue-600 hover:text-white transition-all">
                            [ EXEC_TOGGLE ]
                        </button>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="flex flex-col gap-8 animate-in fade-in duration-500">
            {/* Manual Toolbar */}
            <div className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-800">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-2 h-5 bg-orange-600"></div>
                    <div>
                        <h2 className="font-mono text-xs font-black text-slate-800 dark:text-white uppercase">Manual_Override_Panel</h2>
                        <p className="font-mono text-[9px] text-slate-500 uppercase">Station_Status: [{status}]</p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => refreshDevices()}
                        className="px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 font-mono text-[10px] font-black uppercase text-slate-600 dark:text-slate-400 hover:border-slate-800 transition-all"
                        disabled={isLoading}
                    >
                        {isLoading ? "REFRESHING..." : "[ DISCOVER_DEVICES ]"}
                    </button>
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-red-700 text-white font-mono text-[10px] font-black uppercase hover:bg-red-800 shadow-none border border-red-900">
                        <AlertOctagon size={12} />
                        [ EMERGENCY_STOP ]
                    </button>
                </div>
            </div>

            {/* Pumps Section */}
            <section>
                <div className="flex items-center gap-2 mb-3 ml-1">
                    <Power size={14} className="text-blue-500" />
                    <h3 className="font-mono text-sm font-black text-slate-900 dark:text-white uppercase tracking-tighter">Bomba_System (PUMPS)</h3>
                    <div className="h-px bg-slate-200 dark:bg-slate-800 flex-1 ml-2"></div>
                </div>
                {renderGrid('pump')}
            </section>

            {/* Valves Section */}
            <section>
                <div className="flex items-center gap-2 mb-3 ml-1">
                    <Droplet size={14} className="text-emerald-500" />
                    <h3 className="font-mono text-sm font-black text-slate-900 dark:text-white uppercase tracking-tighter">Valvula_System (VALVES)</h3>
                    <div className="h-px bg-slate-200 dark:bg-slate-800 flex-1 ml-2"></div>
                </div>
                {renderGrid('valve')}
            </section>
        </div>
    );
};
