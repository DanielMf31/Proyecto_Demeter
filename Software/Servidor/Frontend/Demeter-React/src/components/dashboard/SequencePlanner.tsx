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
        <div className="flex flex-col gap-10 animate-in fade-in duration-500 pb-20">
            {/* Header / Actions */}
            <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 border-2 border-slate-300 dark:border-slate-800">
                <div className="flex items-center gap-4 px-3">
                    <div className="w-3 h-8 bg-blue-600"></div>
                    <div>
                        <h2 className="font-mono text-lg font-black text-slate-800 dark:text-white uppercase tracking-tighter">Sequence_Architect_v2</h2>
                        <p className="font-mono text-xs text-slate-500 uppercase">Buffer_Status: [{steps.length}/100_STEPS_ALLOCATED]</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={clearSteps}
                        className="px-5 py-2.5 bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-700 font-mono text-xs font-black uppercase text-red-600 hover:bg-red-50 dark:hover:bg-red-900/10 transition-all"
                    >
                        [ CLEAR_BUFFER ]
                    </button>
                    <button
                        onClick={executeSequence}
                        disabled={isExecuting || steps.length === 0}
                        className="flex items-center gap-3 px-8 py-2.5 bg-blue-600 text-white font-mono text-xs font-black uppercase hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 shadow-none border-2 border-blue-900"
                    >
                        <Play size={18} />
                        {isExecuting ? "EXECUTING_STACK..." : "[ COMMIT_&_EXECUTE ]"}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
                {/* Form Section */}
                <div className="xl:col-span-4 flex flex-col gap-8">
                    <section className="bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 p-6">
                        <div className="flex items-center gap-3 mb-6">
                            <Settings2 size={20} className="text-blue-500" />
                            <h3 className="font-mono text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Command_Constructor</h3>
                        </div>

                        <form onSubmit={handleAdd} className="space-y-6">
                            <div>
                                <label className="block font-mono text-xs text-slate-500 uppercase mb-2">Select_Peripheral_Target</label>
                                <select
                                    className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-700 font-mono text-base p-3 rounded-none dark:text-slate-200 focus:border-blue-500 outline-none"
                                    value={form.pin}
                                    onChange={e => setForm({ ...form, pin: e.target.value })}
                                    required
                                >
                                    <option value="">-- SYSTEM_SELECT --</option>
                                    <option value="WAIT">PAUSE_INSTRUCTION (WAIT)</option>
                                    <optgroup label="PUMP_CLUSTER">
                                        <option value="1">PUMP_UNIT_01</option>
                                        <option value="2">PUMP_UNIT_02</option>
                                        <option value="3">PUMP_UNIT_03</option>
                                        <option value="4">PUMP_UNIT_04</option>
                                    </optgroup>
                                    <optgroup label="VALVE_CLUSTER">
                                        <option value="5">VALVE_UNIT_01</option>
                                        <option value="6">VALVE_UNIT_02</option>
                                        <option value="7">VALVE_UNIT_03</option>
                                        <option value="8">VALVE_UNIT_04</option>
                                    </optgroup>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                                <div>
                                    <label className="block font-mono text-xs text-slate-500 uppercase mb-2">Op_Mode</label>
                                    <select
                                        className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-700 font-mono text-base p-3 rounded-none dark:text-slate-200 focus:border-blue-500 outline-none"
                                        value={form.estado}
                                        onChange={e => setForm({ ...form, estado: e.target.value as any })}
                                        disabled={form.pin === 'WAIT'}
                                    >
                                        <option value="ON">LOGIC_HIGH (ON)</option>
                                        <option value="OFF">LOGIC_LOW (OFF)</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block font-mono text-xs text-slate-500 uppercase mb-2">Duration (ms)</label>
                                    <input
                                        type="number"
                                        className="w-full bg-slate-50 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-700 font-mono text-base p-3 rounded-none dark:text-slate-200 focus:border-blue-500 outline-none"
                                        value={form.tiempo}
                                        onChange={e => setForm({ ...form, tiempo: parseInt(e.target.value) })}
                                        min="1"
                                        required
                                    />
                                </div>
                            </div>

                            <button type="submit" className="w-full flex items-center justify-center gap-3 py-4 bg-slate-900 dark:bg-blue-600 text-white font-mono text-sm font-black uppercase hover:bg-black dark:hover:bg-blue-700 transition-all border-2 border-slate-900 dark:border-blue-700 shadow-lg">
                                <Plus size={20} />
                                [ PUSH_TO_BUFFER_STACK ]
                            </button>
                        </form>
                    </section>
                </div>

                {/* Table Section */}
                <div className="xl:col-span-8">
                    <section className="bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 flex flex-col h-full min-h-[500px]">
                        <div className="flex items-center justify-between p-4 border-b-2 border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
                            <div className="flex items-center gap-3">
                                <ListOrdered size={20} className="text-blue-500" />
                                <h3 className="font-mono text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Execution_Sequence_Stack</h3>
                            </div>
                            <span className="font-mono text-xs text-slate-400">MEMORY_BLOCK: 0x00A1</span>
                        </div>

                        <div className="flex-1 overflow-auto">
                            {steps.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center p-20 text-slate-400">
                                    <Clock size={64} strokeWidth={1} className="mb-6 opacity-20" />
                                    <p className="font-mono text-sm uppercase tracking-widest">Wait_State: Buffer_Ready_For_Data</p>
                                </div>
                            ) : (
                                <table className="w-full border-collapse">
                                    <thead>
                                        <tr className="bg-slate-50 dark:bg-slate-800/50 border-b-2 border-slate-200 dark:border-slate-800">
                                            <th className="p-4 font-mono text-xs text-slate-500 uppercase text-left w-20">PTR</th>
                                            <th className="p-4 font-mono text-xs text-slate-500 uppercase text-left">Instruction_Target</th>
                                            <th className="p-4 font-mono text-xs text-slate-500 uppercase text-center w-32">Logic_Mode</th>
                                            <th className="p-4 font-mono text-xs text-slate-500 uppercase text-right w-32">Delay_ms</th>
                                            <th className="p-4 font-mono text-xs text-slate-500 uppercase text-center w-32">Ops</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y-2 divide-slate-100 dark:divide-slate-800">
                                        {steps.map((step, i) => (
                                            <tr key={step.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 group transition-colors">
                                                <td className="p-4 font-mono text-sm text-slate-400">0x{i.toString(16).padStart(4, '0')}</td>
                                                <td className="p-4 font-mono text-base font-bold dark:text-slate-200">{getPinLabel(step.pin)}</td>
                                                <td className="p-4 text-center">
                                                    <span className={`px-3 py-1 font-mono text-xs font-black border-2 ${step.estado === 'ON' ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-900/50' :
                                                        step.estado === 'OFF' ? 'bg-slate-100 text-slate-600 border-slate-300 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700' :
                                                            'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-900/50'
                                                        }`}>
                                                        {step.estado}
                                                    </span>
                                                </td>
                                                <td className="p-4 font-mono text-base text-right font-bold text-slate-600 dark:text-slate-300">{step.tiempo}ms</td>
                                                <td className="p-4">
                                                    <div className="flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button onClick={() => duplicateStep(step.id)} title="DUPLICATE_STEP" className="p-2 hover:bg-white dark:hover:bg-slate-700 border border-transparent hover:border-slate-200 dark:hover:border-slate-600 text-slate-500 transition-all"><Copy size={16} /></button>
                                                        <button onClick={() => removeStep(step.id)} title="DELETE_STEP" className="p-2 hover:bg-red-50 dark:hover:bg-red-900/40 border border-transparent hover:border-red-200 dark:hover:border-red-900/60 text-red-500 transition-all"><Trash2 size={16} /></button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>

                        {steps.length > 0 && (
                            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 border-t-2 border-slate-200 dark:border-slate-800 flex items-center justify-between font-mono text-xs uppercase tracking-widest">
                                <span className="text-slate-500">Estimated_Sequence_Runtime: <span className="text-slate-900 dark:text-white font-black">{steps.reduce((acc, s) => acc + s.tiempo, 0)}ms</span></span>
                                <span className="text-blue-600 dark:text-blue-400 font-bold animate-pulse">EndOfStack_Reached_Successfully</span>
                            </div>
                        )}
                    </section>
                </div>
            </div>
        </div>
    );
};
