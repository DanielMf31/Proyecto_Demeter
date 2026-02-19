import React, { useState } from 'react';
import { usePlannerStore } from '../../store/usePlannerStore';
import { useDeviceStore } from '../../store/useDeviceStore';
import {
    Plus,
    Play,
    Trash2,
    Copy,
    Clock,
    Settings2,
    ListOrdered
} from 'lucide-react';
import { PlannerStep } from '../../types';

export const SequencePlanner: React.FC = () => {
    const { steps, addStep, removeStep, duplicateStep, executeSequence, clearSteps, isExecuting } = usePlannerStore();
    useDeviceStore();

    const [form, setForm] = useState<Omit<PlannerStep, 'id'>>({
        pin: '',
        estado: 'ON',
        tiempo: 1000
    });

    const handleAdd = (e: React.FormEvent) => {
        e.preventDefault();
        if (!form.pin) return;
        addStep(form);
    };

    const getPinLabel = (pin: string) => {
        if (pin === 'WAIT') return '⏸ PAUSE';

        // Simple fallback logic for logical pin label
        const isPump = parseInt(pin, 10) <= 4;
        return isPump ? `PUMP_0${pin}` : `VALVE_0${parseInt(pin, 10) - 4}`;
    };

    return (
        <div className="flex flex-col gap-6 animate-in fade-in duration-500 pb-20">
            {/* Header / Actions */}
            <div className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-800">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-2 h-5 bg-blue-600"></div>
                    <div>
                        <h2 className="font-mono text-xs font-black text-slate-800 dark:text-white uppercase">Sequence_Architect_v2</h2>
                        <p className="font-mono text-[9px] text-slate-500 uppercase">Buffer_Status: [{steps.length}/100_STEPS]</p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={clearSteps}
                        className="px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 font-mono text-[10px] font-black uppercase text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10 transition-all"
                    >
                        [ CLEAR_BUFFER ]
                    </button>
                    <button
                        onClick={executeSequence}
                        disabled={isExecuting || steps.length === 0}
                        className="flex items-center gap-2 px-6 py-1.5 bg-blue-600 text-white font-mono text-[10px] font-black uppercase hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 shadow-none border border-blue-900"
                    >
                        <Play size={12} />
                        {isExecuting ? "EXECUTING..." : "[ COMMIT_&_EXECUTE ]"}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Form Section */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <section className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 p-4">
                        <div className="flex items-center gap-2 mb-4">
                            <Settings2 size={14} className="text-blue-500" />
                            <h3 className="font-mono text-[10px] font-black text-slate-900 dark:text-white uppercase">Command_Constructor</h3>
                        </div>

                        <form onSubmit={handleAdd} className="space-y-4">
                            <div>
                                <label className="block font-mono text-[9px] text-slate-500 uppercase mb-1">Select_Peripheral</label>
                                <select
                                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-xs p-2 rounded-none dark:text-slate-200"
                                    value={form.pin}
                                    onChange={e => setForm({ ...form, pin: e.target.value })}
                                    required
                                >
                                    <option value="">-- SELECT --</option>
                                    <option value="WAIT">PAUSE (WAIT)</option>
                                    <optgroup label="PUMPS">
                                        <option value="1">PUMP_01</option>
                                        <option value="2">PUMP_02</option>
                                        <option value="3">PUMP_03</option>
                                        <option value="4">PUMP_04</option>
                                    </optgroup>
                                    <optgroup label="VALVES">
                                        <option value="5">VALVE_01</option>
                                        <option value="6">VALVE_02</option>
                                        <option value="7">VALVE_03</option>
                                        <option value="8">VALVE_04</option>
                                    </optgroup>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block font-mono text-[9px] text-slate-500 uppercase mb-1">Action</label>
                                    <select
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-xs p-2 rounded-none dark:text-slate-200"
                                        value={form.estado}
                                        onChange={e => setForm({ ...form, estado: e.target.value as any })}
                                        disabled={form.pin === 'WAIT'}
                                    >
                                        <option value="ON">ON</option>
                                        <option value="OFF">OFF</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block font-mono text-[9px] text-slate-500 uppercase mb-1">Duration (ms)</label>
                                    <input
                                        type="number"
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 font-mono text-xs p-2 rounded-none dark:text-slate-200"
                                        value={form.tiempo}
                                        onChange={e => setForm({ ...form, tiempo: parseInt(e.target.value) })}
                                        min="1"
                                        required
                                    />
                                </div>
                            </div>

                            <button type="submit" className="w-full flex items-center justify-center gap-2 py-2 bg-slate-900 dark:bg-blue-600 text-white font-mono text-[10px] font-black uppercase hover:bg-black transition-all border border-slate-900">
                                <Plus size={14} />
                                [ PUSH_TO_BUFFER ]
                            </button>
                        </form>
                    </section>
                </div>

                {/* Table Section */}
                <div className="lg:col-span-8">
                    <section className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 flex flex-col h-full min-h-[400px]">
                        <div className="flex items-center justify-between p-3 border-b border-slate-200 dark:border-slate-800">
                            <div className="flex items-center gap-2">
                                <ListOrdered size={14} className="text-blue-500" />
                                <h3 className="font-mono text-[10px] font-black text-slate-900 dark:text-white uppercase tracking-widest">Exec_Sequence_Stack</h3>
                            </div>
                            <span className="font-mono text-[9px] text-slate-400">OFFSET: 0x00</span>
                        </div>

                        <div className="flex-1 overflow-auto">
                            {steps.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center p-12 text-slate-400">
                                    <Clock size={40} strokeWidth={1} className="mb-4 opacity-20" />
                                    <p className="font-mono text-[10px] uppercase">Wait_State: Buffer_Empty</p>
                                </div>
                            ) : (
                                <table className="w-full border-collapse">
                                    <thead>
                                        <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                            <th className="p-2 font-mono text-[9px] text-slate-500 uppercase text-left w-12">PTR</th>
                                            <th className="p-2 font-mono text-[9px] text-slate-500 uppercase text-left">Target</th>
                                            <th className="p-2 font-mono text-[9px] text-slate-500 uppercase text-center w-20">Mode</th>
                                            <th className="p-2 font-mono text-[9px] text-slate-500 uppercase text-right w-24">Delay</th>
                                            <th className="p-2 font-mono text-[9px] text-slate-500 uppercase text-center w-24">Ops</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                        {steps.map((step, i) => (
                                            <tr key={step.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 group">
                                                <td className="p-2 font-mono text-[10px] text-slate-400">0x{i.toString(16).padStart(2, '0')}</td>
                                                <td className="p-2 font-mono text-[10px] font-bold dark:text-slate-300">{getPinLabel(step.pin)}</td>
                                                <td className="p-2 text-center">
                                                    <span className={`px-1.5 py-0.5 font-mono text-[9px] font-black border ${step.estado === 'ON' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                                        step.estado === 'OFF' ? 'bg-slate-100 text-slate-600 border-slate-300' :
                                                            'bg-amber-50 text-amber-700 border-amber-200'
                                                        }`}>
                                                        {step.estado}
                                                    </span>
                                                </td>
                                                <td className="p-2 font-mono text-[10px] text-right text-slate-600 dark:text-slate-400">{step.tiempo}ms</td>
                                                <td className="p-2">
                                                    <div className="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button onClick={() => duplicateStep(step.id)} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500"><Copy size={12} /></button>
                                                        <button onClick={() => removeStep(step.id)} className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500"><Trash2 size={12} /></button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>

                        {steps.length > 0 && (
                            <div className="p-2 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between font-mono text-[9px] uppercase">
                                <span className="text-slate-500">Total_Time: {steps.reduce((acc, s) => acc + s.tiempo, 0)}ms</span>
                                <span className="text-blue-600 font-bold">EndOfFile_Reached</span>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
};
