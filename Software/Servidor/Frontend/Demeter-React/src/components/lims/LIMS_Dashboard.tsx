import React, { useState, useEffect, useMemo } from 'react';
import {
    TestTubes, CheckCircle2, FlaskConical, Microscope, Plus, X, Activity, Info,
    Search, ChevronUp, ChevronDown, SlidersHorizontal, Leaf, PlusCircle
} from 'lucide-react';
import { apiService } from '../../services/apiService';
import { Plant, PlantSortKey, SortDirection } from '../../types';
import { PlantDetailView } from './PlantDetailView';

const SPECIES_CONFIG: Record<string, { emoji: string; color: string; darkColor: string }> = {
    'Solanum lycopersicum': { emoji: '🍅', color: 'bg-red-100 text-red-800 border-red-300', darkColor: 'dark:bg-red-900/30 dark:text-red-300 dark:border-red-800' },
    'Solanum tuberosum': { emoji: '🥔', color: 'bg-amber-100 text-amber-800 border-amber-300', darkColor: 'dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800' },
    'Lactuca sativa': { emoji: '🥬', color: 'bg-green-100 text-green-800 border-green-300', darkColor: 'dark:bg-green-900/30 dark:text-green-300 dark:border-green-800' },
    'Solanum melongena': { emoji: '🍆', color: 'bg-purple-100 text-purple-800 border-purple-300', darkColor: 'dark:bg-purple-900/30 dark:text-purple-300 dark:border-purple-800' },
};
const getS = (e: string) => SPECIES_CONFIG[e] || { emoji: '🌱', color: 'bg-slate-100 text-slate-800 border-slate-300', darkColor: 'dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700' };

const BLANK_PLANT = {
    name: '', identificador_fisico: '', especie_variedad: 'Solanum lycopersicum',
    fecha_siembra: new Date().toISOString().split('T')[0], estado_vital: 'Activa', node_id: '',
    sustrato: '', variedad: '', ubicacion: '', ce_objetivo: '', ph_objetivo: '', iluminacion: '',
};

export const LIMS_Dashboard: React.FC = () => {
    const [plants, setPlants] = useState<Plant[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const [searchQuery, setSearchQuery] = useState('');
    const [speciesFilter, setSpeciesFilter] = useState<string>('ALL');
    const [sortKey, setSortKey] = useState<PlantSortKey>('name');
    const [sortDir, setSortDir] = useState<SortDirection>('asc');
    const [detailPlant, setDetailPlant] = useState<Plant | null>(null);

    // Cart experiment
    const [isCartOpen, setIsCartOpen] = useState(false);
    const [expName, setExpName] = useState('');
    const [expDesc, setExpDesc] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Add plant
    const [isAddOpen, setIsAddOpen] = useState(false);
    const [addForm, setAddForm] = useState(BLANK_PLANT);
    const [isAdding, setIsAdding] = useState(false);

    const [notification, setNotification] = useState<{ msg: string; ok: boolean } | null>(null);

    useEffect(() => { fetchData(); }, []);

    const fetchData = async () => {
        setIsLoading(true);
        const data = await apiService.fetchPlants();
        if (data) setPlants(data);
        setIsLoading(false);
    };

    const showNotif = (msg: string, ok: boolean) => {
        setNotification({ msg, ok });
        setTimeout(() => setNotification(null), 4000);
    };

    const uniqueSpecies = useMemo(() => Array.from(new Set(plants.map(p => p.especie_variedad))), [plants]);

    const filteredPlants = useMemo(() => {
        let r = [...plants];
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            r = r.filter(p => p.name.toLowerCase().includes(q) || p.identificador_fisico.toLowerCase().includes(q));
        }
        if (speciesFilter !== 'ALL') r = r.filter(p => p.especie_variedad === speciesFilter);
        r.sort((a, b) => {
            let c = 0;
            if (sortKey === 'name') c = a.name.localeCompare(b.name);
            else if (sortKey === 'especie_variedad') c = a.especie_variedad.localeCompare(b.especie_variedad);
            else if (sortKey === 'fecha_siembra') c = a.fecha_siembra.localeCompare(b.fecha_siembra);
            return sortDir === 'asc' ? c : -c;
        });
        return r;
    }, [plants, searchQuery, speciesFilter, sortKey, sortDir]);

    const toggleSel = (id: number, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
    };

    const handleCardClick = async (plant: Plant) => {
        const d = await apiService.fetchPlantDetail(plant.id);
        if (d) setDetailPlant(d);
    };

    const handlePlantUpdated = (updated: Plant) => {
        setPlants(prev => prev.map(p => p.id === updated.id ? updated : p));
        setDetailPlant(updated);
        showNotif(`'${updated.name}' actualizada correctamente`, true);
    };

    const handleCreateExperiment = async () => {
        if (!expName.trim()) { showNotif('El nombre del experimento es requerido', false); return; }
        if (!selectedIds.length) { showNotif('Selecciona al menos una planta', false); return; }
        setIsSubmitting(true);
        const res = await apiService.generateExperiment(expName, expDesc, selectedIds);
        setIsSubmitting(false);
        if (res) {
            showNotif(`Experimento '${res.name}' creado exitosamente!`, true);
            setSelectedIds([]); setExpName(''); setExpDesc(''); setIsCartOpen(false);
        } else {
            showNotif('Error al generar el experimento', false);
        }
    };

    const handleAddPlant = async () => {
        if (!addForm.name.trim() || !addForm.identificador_fisico.trim()) {
            showNotif('Nombre e ID físico son requeridos', false); return;
        }
        setIsAdding(true);
        const payload = {
            name: addForm.name,
            identificador_fisico: addForm.identificador_fisico,
            especie_variedad: addForm.especie_variedad,
            fecha_siembra: addForm.fecha_siembra,
            estado_vital: addForm.estado_vital,
            node_id: Number(addForm.node_id) || 0,
            metadata_cientifica: {
                variedad: addForm.variedad,
                sustrato: addForm.sustrato,
                ubicacion: addForm.ubicacion,
                ce_objetivo: Number(addForm.ce_objetivo) || null,
                ph_objetivo: Number(addForm.ph_objetivo) || null,
                iluminacion: addForm.iluminacion,
            },
        };
        const res = await apiService.createPlant(payload as any);
        setIsAdding(false);
        if (res) {
            setPlants(prev => [...prev, res]);
            showNotif(`Planta '${res.name}' registrada!`, true);
            setIsAddOpen(false);
            setAddForm(BLANK_PLANT);
        } else {
            showNotif('Error al registrar la planta (¿ID físico duplicado?)', false);
        }
    };

    const toggleSort = (key: PlantSortKey) => {
        if (sortKey === key) setSortDir(p => p === 'asc' ? 'desc' : 'asc');
        else { setSortKey(key); setSortDir('asc'); }
    };
    const SI = ({ k }: { k: PlantSortKey }) => sortKey !== k ? null : sortDir === 'asc' ? <ChevronUp size={16} /> : <ChevronDown size={16} />;

    const inputCls = "w-full bg-slate-50 dark:bg-slate-950 border-2 border-slate-300 dark:border-slate-800 px-4 py-3 text-lg font-mono text-slate-900 dark:text-white outline-none focus:border-blue-500";
    const labelCls = "block text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-2";

    return (
        <div className="w-full relative h-[calc(100vh-160px)] flex flex-col">
            {notification && (
                <div className={`absolute top-0 right-0 m-4 p-5 z-50 border-l-4 shadow-lg ${notification.ok ? 'bg-green-100 border-green-500 text-green-800' : 'bg-red-100 border-red-500 text-red-800'}`}>
                    <p className="font-mono font-bold text-base">{notification.msg}</p>
                </div>
            )}

            {/* ── Header ── */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-4xl font-mono font-black text-slate-800 dark:text-white uppercase tracking-tight flex items-center gap-3">
                        <Microscope size={36} className="text-blue-500" />
                        Catálogo LIMS
                    </h2>
                    <p className="text-lg font-mono text-slate-500 dark:text-slate-400 mt-1">
                        {filteredPlants.length} plantas · Click para detalles · Checkbox para experimentos
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {/* Add Plant */}
                    <button onClick={() => setIsAddOpen(true)}
                        className="flex items-center gap-2 px-6 py-4 font-mono font-black text-base border-2 border-green-600 bg-green-600 text-white hover:bg-green-700 transition-all shadow-md">
                        <PlusCircle size={22} /> AÑADIR PLANTA
                    </button>
                    {/* Cart */}
                    <button onClick={() => setIsCartOpen(true)} disabled={!selectedIds.length}
                        className={`flex items-center gap-2 px-6 py-4 font-mono font-black text-base border-2 transition-all
                            ${selectedIds.length ? 'bg-blue-600 border-blue-700 text-white hover:bg-blue-700 shadow-xl' : 'bg-slate-200 border-slate-300 text-slate-400 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-500 cursor-not-allowed'}`}>
                        <FlaskConical size={22} /> CARRITO ({selectedIds.length})
                    </button>
                </div>
            </div>

            {/* ── Search & Filter Bar ── */}
            <div className="flex flex-wrap items-center gap-4 mb-6 bg-white dark:bg-slate-900 p-5 border border-slate-300 dark:border-slate-800">
                <div className="flex items-center gap-3 flex-1 min-w-[260px] bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 px-4 py-3">
                    <Search size={22} className="text-slate-400" />
                    <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
                        placeholder="Buscar por nombre o ID físico..."
                        className="flex-1 bg-transparent text-lg font-mono text-slate-800 dark:text-white outline-none placeholder-slate-400" />
                </div>
                <div className="flex items-center gap-2">
                    <SlidersHorizontal size={20} className="text-slate-400" />
                    <select value={speciesFilter} onChange={e => setSpeciesFilter(e.target.value)}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-white font-mono text-base border border-slate-300 dark:border-slate-700 px-4 py-3 outline-none focus:border-blue-500 cursor-pointer">
                        <option value="ALL">Todas las Especies</option>
                        {uniqueSpecies.map(sp => <option key={sp} value={sp}>{getS(sp).emoji} {sp}</option>)}
                    </select>
                </div>
                <div className="flex gap-2">
                    {([['name', 'Nombre A-Z'], ['especie_variedad', 'Especie'], ['fecha_siembra', 'Fecha']] as [PlantSortKey, string][]).map(([key, label]) => (
                        <button key={key} onClick={() => toggleSort(key)}
                            className={`flex items-center gap-1.5 px-4 py-3 font-mono text-sm font-bold border-2 transition-colors
                                ${sortKey === key ? 'bg-blue-600 text-white border-blue-700' : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700 hover:border-blue-400'}`}>
                            {label} <SI k={key} />
                        </button>
                    ))}
                </div>
            </div>

            {/* ── Plant Grid ── */}
            {isLoading ? (
                <div className="flex-1 flex justify-center items-center"><Activity className="animate-spin text-blue-500" size={48} /></div>
            ) : (
                <div className="flex-1 overflow-y-auto overflow-x-hidden pr-2">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 content-start pb-24">
                        {filteredPlants.map(plant => {
                            const isSel = selectedIds.includes(plant.id);
                            const sp = getS(plant.especie_variedad);
                            return (
                                <div key={plant.id} onClick={() => handleCardClick(plant)}
                                    className={`relative cursor-pointer transition-all duration-200 border-2 p-7 group flex flex-col gap-5
                                        ${isSel ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 shadow-lg ring-2 ring-blue-500'
                                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-blue-400 hover:shadow-xl shadow-sm'}`}>
                                    <div className="absolute top-5 right-5" onClick={e => toggleSel(plant.id, e)}>
                                        <div className={`w-8 h-8 border-2 flex items-center justify-center transition-colors
                                            ${isSel ? 'bg-blue-600 border-blue-600 text-white' : 'border-slate-300 dark:border-slate-600 bg-slate-100 dark:bg-slate-800 hover:border-blue-400'}`}>
                                            {isSel && <CheckCircle2 size={20} />}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3 flex-wrap">
                                        <span className={`px-3 py-1.5 text-base font-mono font-bold border ${sp.color} ${sp.darkColor}`}>
                                            {sp.emoji} {plant.especie_variedad.split(' ').pop()}
                                        </span>
                                        <span className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-3 py-1 text-base font-mono font-bold">
                                            {plant.identificador_fisico}
                                        </span>
                                    </div>
                                    <h3 className="text-2xl font-mono font-black text-slate-900 dark:text-white tracking-tight leading-snug pr-8">
                                        {plant.name}
                                    </h3>
                                    <div className="flex items-center gap-5 text-base font-mono text-slate-500">
                                        <span className="flex items-center gap-2"><Leaf size={16} />{plant.estado_vital}</span>
                                        <span>📅 {plant.fecha_siembra}</span>
                                    </div>
                                    <div className="w-full h-px bg-slate-200 dark:bg-slate-800" />
                                    <div className="space-y-3">
                                        {Object.entries(plant.metadata_cientifica).slice(0, 3).map(([k, v]) => (
                                            <div key={k} className="flex justify-between items-center gap-4">
                                                <span className="text-sm font-mono font-bold text-slate-400 uppercase tracking-wider">{k.replace(/_/g, ' ')}</span>
                                                <span className="text-base font-mono font-bold text-slate-700 dark:text-slate-300 text-right">{String(v)}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="text-sm font-mono text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity text-center pt-1">
                                        Ver detalles completos →
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* ── Plant Detail ── */}
            {detailPlant && (
                <PlantDetailView plant={detailPlant} onClose={() => setDetailPlant(null)} onUpdated={handlePlantUpdated} />
            )}

            {/* ── Add Plant Modal ── */}
            {isAddOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4 overflow-y-auto py-6">
                    <div className="w-full max-w-2xl bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 shadow-2xl">
                        <div className="p-7 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-950">
                            <h3 className="font-mono font-black text-2xl text-slate-900 dark:text-white flex items-center gap-3">
                                <PlusCircle className="text-green-500" size={28} /> Nueva Planta LIMS
                            </h3>
                            <button onClick={() => setIsAddOpen(false)} className="text-slate-400 hover:text-slate-800 dark:hover:text-white"><X size={28} /></button>
                        </div>
                        <div className="p-7 space-y-5 overflow-y-auto max-h-[70vh]">
                            <div className="grid grid-cols-2 gap-5">
                                {[
                                    { key: 'name', label: 'Nombre *', type: 'text', placeholder: 'Tomate Cherry-006' },
                                    { key: 'identificador_fisico', label: 'ID Físico *', type: 'text', placeholder: 'TOM-006' },
                                    { key: 'fecha_siembra', label: 'Fecha Siembra', type: 'date', placeholder: '' },
                                    { key: 'node_id', label: 'Node ID', type: 'number', placeholder: '21' },
                                ].map(({ key, label, type, placeholder }) => (
                                    <div key={key}>
                                        <label className={labelCls}>{label}</label>
                                        <input type={type} placeholder={placeholder}
                                            value={addForm[key as keyof typeof addForm]}
                                            onChange={e => setAddForm(p => ({ ...p, [key]: e.target.value }))}
                                            className={inputCls} />
                                    </div>
                                ))}
                                <div>
                                    <label className={labelCls}>Especie</label>
                                    <select value={addForm.especie_variedad}
                                        onChange={e => setAddForm(p => ({ ...p, especie_variedad: e.target.value }))}
                                        className={inputCls}>
                                        {Object.keys(SPECIES_CONFIG).map(s => <option key={s} value={s}>{s}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className={labelCls}>Estado Vital</label>
                                    <select value={addForm.estado_vital}
                                        onChange={e => setAddForm(p => ({ ...p, estado_vital: e.target.value }))}
                                        className={inputCls}>
                                        {['Activa', 'Cosechada', 'Muerta', 'En Espera'].map(s => <option key={s}>{s}</option>)}
                                    </select>
                                </div>
                            </div>

                            <div className="pt-2">
                                <p className="text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-4">Metadata Científica (Opcional)</p>
                                <div className="grid grid-cols-2 gap-5">
                                    {[
                                        { key: 'variedad', label: 'Variedad', placeholder: 'Cherry' },
                                        { key: 'sustrato', label: 'Sustrato', placeholder: 'Fibra de Coco' },
                                        { key: 'ubicacion', label: 'Ubicación', placeholder: 'Invernadero A - Mesa 1' },
                                        { key: 'iluminacion', label: 'Iluminación', placeholder: 'LED 600W' },
                                        { key: 'ce_objetivo', label: 'CE Objetivo (ms/cm)', placeholder: '2.0' },
                                        { key: 'ph_objetivo', label: 'pH Objetivo', placeholder: '5.8' },
                                    ].map(({ key, label, placeholder }) => (
                                        <div key={key}>
                                            <label className={labelCls}>{label}</label>
                                            <input type="text" placeholder={placeholder}
                                                value={addForm[key as keyof typeof addForm]}
                                                onChange={e => setAddForm(p => ({ ...p, [key]: e.target.value }))}
                                                className={inputCls} />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        <div className="p-7 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex justify-end gap-4">
                            <button onClick={() => setIsAddOpen(false)}
                                className="px-6 py-3 font-mono text-base font-bold border-2 border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                CANCELAR
                            </button>
                            <button onClick={handleAddPlant} disabled={isAdding}
                                className="flex items-center gap-3 px-8 py-3 font-mono text-base font-black bg-green-600 text-white hover:bg-green-700 transition-colors disabled:opacity-50">
                                {isAdding ? <Activity className="animate-spin" size={20} /> : <PlusCircle size={20} />}
                                REGISTRAR PLANTA
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Cart Dialog ── */}
            {isCartOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
                    <div className="w-full max-w-2xl bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 shadow-2xl">
                        <div className="p-7 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-950">
                            <h3 className="font-mono font-black text-2xl text-slate-900 dark:text-white flex items-center gap-3">
                                <TestTubes className="text-blue-500" size={28} /> Nuevo Experimento
                            </h3>
                            <button onClick={() => setIsCartOpen(false)} className="text-slate-400 hover:text-slate-800 dark:hover:text-white"><X size={28} /></button>
                        </div>
                        <div className="p-7 space-y-5">
                            <div>
                                <label className={labelCls}>Nombre del Ensayo</label>
                                <input type="text" value={expName} onChange={e => setExpName(e.target.value)}
                                    placeholder="Ej: Ensayo de Estrés Hídrico V2" className={inputCls} />
                            </div>
                            <div>
                                <label className={labelCls}>Descripción (Opcional)</label>
                                <textarea value={expDesc} onChange={e => setExpDesc(e.target.value)} rows={3}
                                    className={`${inputCls} resize-none`} />
                            </div>
                            <div className="bg-blue-50 dark:bg-blue-900/20 p-5 border border-blue-200 dark:border-blue-800/50">
                                <p className="text-base font-mono text-blue-800 dark:text-blue-300 flex items-center gap-3">
                                    <Info size={20} />
                                    Se enlazarán <strong>{selectedIds.length} plantas</strong> seleccionadas.
                                </p>
                            </div>
                        </div>
                        <div className="p-7 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex justify-end gap-4">
                            <button onClick={() => setIsCartOpen(false)}
                                className="px-6 py-3 font-mono text-base font-bold border-2 border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
                                CANCELAR
                            </button>
                            <button onClick={handleCreateExperiment} disabled={isSubmitting || !expName.trim()}
                                className="flex items-center gap-3 px-8 py-3 font-mono text-base font-black bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50">
                                {isSubmitting ? <Activity className="animate-spin" size={20} /> : <Plus size={20} />}
                                GENERAR EXPERIMENTO
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
