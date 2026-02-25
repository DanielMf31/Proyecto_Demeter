import React, { useState, useEffect, useMemo } from 'react';
import { BarChart3, Table2, FlaskConical, Info, X, Activity, Calendar, Filter, Pencil, Save, XCircle } from 'lucide-react';
import { Plant, PlantTelemetryRecord, SensorData, MetricType } from '../../types';
import { apiService } from '../../services/apiService';
import { ScientificChart } from '../dashboard/ScientificChart';
import { DataTable } from '../dashboard/DataTable';
import { ScientificToolbar } from '../dashboard/ScientificToolbar';

interface PlantDetailViewProps {
    plant: Plant;
    onClose: () => void;
    onUpdated?: (updated: Plant) => void;
}

type SubTab = 'charts' | 'tables' | 'experiments' | 'info';
type FilterView = 'ALL' | 'LAST_30' | 'LAST_7' | 'SPECIFIC_DAY';

const ESTADOS = ['Activa', 'Cosechada', 'Muerta', 'En Espera'];

export const PlantDetailView: React.FC<PlantDetailViewProps> = ({ plant, onClose, onUpdated }) => {
    const [activeTab, setActiveTab] = useState<SubTab>('charts');
    const [telemetry, setTelemetry] = useState<PlantTelemetryRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [metric, setMetric] = useState<MetricType>('temperatura');
    const [filterView, setFilterView] = useState<FilterView>('LAST_30');
    const [specificDate, setSpecificDate] = useState<string>(new Date().toISOString().split('T')[0]);

    // Edit state
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [saveNotif, setSaveNotif] = useState<{ msg: string; ok: boolean } | null>(null);
    const [editForm, setEditForm] = useState({
        name: plant.name,
        especie_variedad: plant.especie_variedad,
        fecha_siembra: plant.fecha_siembra,
        estado_vital: plant.estado_vital,
        node_id: String(plant.node_id),
    });
    const [metaForm, setMetaForm] = useState<Record<string, string>>(
        Object.fromEntries(Object.entries(plant.metadata_cientifica).map(([k, v]) => [k, String(v)]))
    );

    useEffect(() => {
        setIsLoading(true);
        apiService.fetchPlantTelemetry(plant.id).then(data => {
            if (data) setTelemetry(data);
            setIsLoading(false);
        });
    }, [plant.id]);

    const sensorData: SensorData[] = useMemo(() => {
        return telemetry.map(r => {
            const T = r.temperature; const RH = r.humidity;
            const svp = 0.61078 * Math.exp((17.27 * T) / (T + 237.3));
            const vpd = svp - svp * (RH / 100.0);
            return { timestamp: r.timestamp, temperatura: T, humedad: RH, vpd } as SensorData;
        });
    }, [telemetry]);

    const filteredData = useMemo(() => {
        if (!sensorData.length) return [];
        if (filterView === 'LAST_30') {
            const latest = new Date(sensorData[sensorData.length - 1].timestamp);
            const ago = new Date(latest); ago.setDate(latest.getDate() - 30);
            return sensorData.filter(d => new Date(d.timestamp) >= ago);
        }
        if (filterView === 'LAST_7') {
            const latest = new Date(sensorData[sensorData.length - 1].timestamp);
            const ago = new Date(latest); ago.setDate(latest.getDate() - 7);
            return sensorData.filter(d => new Date(d.timestamp) >= ago);
        }
        if (filterView === 'SPECIFIC_DAY') return specificDate ? sensorData.filter(d => d.timestamp.startsWith(specificDate)) : sensorData;
        return sensorData;
    }, [sensorData, filterView, specificDate]);

    const handleSave = async () => {
        setIsSaving(true);
        const payload: Partial<Plant> = {
            name: editForm.name,
            especie_variedad: editForm.especie_variedad,
            fecha_siembra: editForm.fecha_siembra,
            estado_vital: editForm.estado_vital,
            node_id: Number(editForm.node_id),
            metadata_cientifica: Object.fromEntries(
                Object.entries(metaForm).map(([k, v]) => {
                    const num = Number(v);
                    return [k, isNaN(num) || v.trim() === '' ? v : num];
                })
            ),
        };
        const updated = await apiService.updatePlant(plant.id, payload);
        setIsSaving(false);
        if (updated) {
            setSaveNotif({ msg: '✓ Cambios guardados correctamente', ok: true });
            setIsEditing(false);
            onUpdated?.(updated);
        } else {
            setSaveNotif({ msg: '✗ Error al guardar los cambios', ok: false });
        }
        setTimeout(() => setSaveNotif(null), 3000);
    };

    const tabs: { key: SubTab; label: string; Icon: any }[] = [
        { key: 'charts', label: 'Gráficas', Icon: BarChart3 },
        { key: 'tables', label: 'Tablas', Icon: Table2 },
        { key: 'experiments', label: 'Experimentos', Icon: FlaskConical },
        { key: 'info', label: 'Información', Icon: Info },
    ];

    const inputCls = "w-full bg-white dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-600 px-4 py-2.5 text-lg font-mono text-slate-900 dark:text-white outline-none focus:border-blue-500 transition";
    const labelCls = "block text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5";

    const TimeFilter = () => (
        <div className="flex items-center gap-3 bg-slate-100 dark:bg-slate-800 p-3 border border-slate-300 dark:border-slate-700">
            <Filter size={20} className="text-slate-500 shrink-0" />
            <select value={filterView} onChange={e => setFilterView(e.target.value as FilterView)}
                className="bg-white dark:bg-slate-900 text-slate-800 dark:text-white font-mono text-base border border-slate-300 dark:border-slate-700 px-4 py-2.5 outline-none focus:border-blue-500">
                <option value="ALL">6 Meses (Todo)</option>
                <option value="LAST_30">Últimos 30 Días</option>
                <option value="LAST_7">Últimos 7 Días</option>
                <option value="SPECIFIC_DAY">Día Específico</option>
            </select>
            {filterView === 'SPECIFIC_DAY' && (
                <div className="flex items-center gap-2">
                    <Calendar size={20} className="text-slate-500" />
                    <input type="date" value={specificDate} onChange={e => setSpecificDate(e.target.value)}
                        className="bg-white dark:bg-slate-900 text-slate-800 dark:text-white font-mono text-base border border-slate-300 dark:border-slate-700 px-4 py-2.5 outline-none focus:border-blue-500 [color-scheme:light] dark:[color-scheme:dark]" />
                </div>
            )}
            <span className="text-base font-mono font-bold text-slate-500 ml-auto">{filteredData.length.toLocaleString()} REGISTROS</span>
        </div>
    );

    return (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-4 pb-4 overflow-y-auto px-2">
            {/* Very wide modal */}
            <div className="w-full max-w-[95vw] bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 shadow-2xl flex flex-col">

                {/* Save notification */}
                {saveNotif && (
                    <div className={`px-6 py-3 text-base font-mono font-bold tracking-tight ${saveNotif.ok ? 'bg-green-100 text-green-800 border-b-2 border-green-400' : 'bg-red-100 text-red-800 border-b-2 border-red-400'}`}>
                        {saveNotif.msg}
                    </div>
                )}

                {/* ─── Header ─── */}
                <div className="p-8 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex items-start justify-between gap-4">
                    <div className="flex-1">
                        <div className="flex items-center gap-4 mb-3 flex-wrap">
                            <span className="bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-4 py-1.5 text-lg font-mono font-bold">
                                {plant.identificador_fisico}
                            </span>
                            <span className={`px-3 py-1 text-sm font-mono font-bold border ${plant.estado_vital === 'Activa'
                                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-300 dark:border-green-800'
                                : 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-300 dark:border-amber-800'}`}>
                                {plant.estado_vital}
                            </span>
                        </div>
                        <h2 className="text-4xl font-mono font-black text-slate-900 dark:text-white tracking-tight">{plant.name}</h2>
                        <p className="text-xl font-mono italic text-slate-500 mt-2">{plant.especie_variedad}</p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                        <button
                            onClick={() => { setActiveTab('info'); setIsEditing(true); }}
                            className="flex items-center gap-2 px-5 py-3 font-mono font-bold text-base bg-amber-500 hover:bg-amber-600 text-white transition-colors"
                        >
                            <Pencil size={20} /> EDITAR
                        </button>
                        <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-800 dark:hover:text-white transition-colors">
                            <X size={34} />
                        </button>
                    </div>
                </div>

                {/* ─── Body ─── */}
                <div className="flex flex-1 overflow-hidden min-h-[600px]">

                    {/* Left KPI sidebar — wider */}
                    <div className="w-[420px] border-r border-slate-200 dark:border-slate-800 p-7 space-y-6 bg-slate-50/50 dark:bg-slate-950/50 overflow-y-auto shrink-0">
                        {[
                            { label: 'Fecha Siembra', value: plant.fecha_siembra },
                            { label: 'Node ID', value: `#${plant.node_id}` },
                        ].map(({ label, value }) => (
                            <div key={label}>
                                <p className="text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">{label}</p>
                                <p className="text-2xl font-mono font-bold text-slate-800 dark:text-white">{value}</p>
                            </div>
                        ))}

                        <div className="w-full h-px bg-slate-200 dark:bg-slate-800" />

                        <div>
                            <p className="text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">Data Points</p>
                            <p className="text-3xl font-mono font-black text-slate-800 dark:text-white">
                                {isLoading ? '...' : telemetry.length.toLocaleString()}
                            </p>
                            <p className="text-base font-mono text-slate-500 mt-0.5">6 meses de datos</p>
                        </div>
                        {sensorData.length > 0 && <>
                            <div>
                                <p className="text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">Temp. Media</p>
                                <p className="text-3xl font-mono font-black text-red-600 dark:text-red-400">
                                    {(sensorData.reduce((a, c) => a + c.temperatura, 0) / sensorData.length).toFixed(1)}°C
                                </p>
                            </div>
                            <div>
                                <p className="text-sm font-mono font-bold text-slate-400 uppercase tracking-widest mb-1">Hum. Media</p>
                                <p className="text-3xl font-mono font-black text-blue-600 dark:text-blue-400">
                                    {(sensorData.reduce((a, c) => a + c.humedad, 0) / sensorData.length).toFixed(1)}%
                                </p>
                            </div>
                        </>}

                        <div className="w-full h-px bg-slate-200 dark:bg-slate-800" />

                        {Object.entries(plant.metadata_cientifica).map(([key, val]) => (
                            <div key={key}>
                                <p className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">{key.replace(/_/g, ' ')}</p>
                                <p className="text-lg font-mono font-semibold text-slate-700 dark:text-slate-300 mt-0.5">{String(val)}</p>
                            </div>
                        ))}
                    </div>

                    {/* Right tabs */}
                    <div className="flex-1 flex flex-col overflow-hidden">
                        {/* Tab bar */}
                        <div className="flex border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
                            {tabs.map(({ key, label, Icon }) => (
                                <button key={key} onClick={() => { setActiveTab(key); if (key !== 'info') setIsEditing(false); }}
                                    className={`flex items-center gap-3 px-8 py-5 font-mono text-base font-bold uppercase tracking-tight transition-colors border-b-2
                                        ${activeTab === key
                                            ? 'text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400 bg-white dark:bg-slate-900'
                                            : 'text-slate-500 border-transparent hover:text-slate-700 dark:hover:text-slate-300 hover:bg-white/50 dark:hover:bg-slate-900/50'}`}>
                                    <Icon size={22} />{label}
                                </button>
                            ))}
                        </div>

                        {/* Tab content */}
                        <div className="flex-1 overflow-y-auto p-7">
                            {isLoading && (activeTab === 'charts' || activeTab === 'tables') ? (
                                <div className="flex justify-center items-center h-64">
                                    <Activity className="animate-spin text-blue-500" size={52} />
                                </div>
                            ) : (
                                <>
                                    {activeTab === 'charts' && (
                                        <div className="space-y-5">
                                            <ScientificToolbar selected={metric} onChange={setMetric} />
                                            <TimeFilter />
                                            <div className="h-[440px]"><ScientificChart data={filteredData} metric={metric} /></div>
                                        </div>
                                    )}

                                    {activeTab === 'tables' && (
                                        <div className="space-y-5">
                                            <TimeFilter />
                                            <DataTable data={filteredData} />
                                        </div>
                                    )}

                                    {activeTab === 'experiments' && (
                                        <div className="space-y-5">
                                            <h3 className="text-lg font-mono font-bold text-slate-500 uppercase tracking-widest">Experimentos Asociados</h3>
                                            {plant.experiments && plant.experiments.length > 0 ? (
                                                <div className="space-y-4">
                                                    {plant.experiments.map(exp => (
                                                        <div key={exp.id} className="border-2 border-slate-200 dark:border-slate-700 p-6 bg-white dark:bg-slate-950">
                                                            <div className="flex justify-between items-start gap-4">
                                                                <div>
                                                                    <h4 className="text-2xl font-mono font-black text-slate-900 dark:text-white">{exp.name}</h4>
                                                                    <p className="text-lg font-mono text-slate-500 mt-1">{exp.description}</p>
                                                                </div>
                                                                <span className="text-base font-mono text-slate-400 bg-slate-100 dark:bg-slate-800 px-4 py-2 shrink-0">
                                                                    {new Date(exp.created_at).toLocaleDateString()}
                                                                </span>
                                                            </div>
                                                            <div className="mt-4 flex flex-wrap gap-6 text-base font-mono text-slate-400">
                                                                <span>ID: <strong className="text-slate-700 dark:text-slate-300">{exp.id}</strong></span>
                                                                <span><strong className="text-slate-700 dark:text-slate-300">{exp.plants?.length || 0}</strong> plantas</span>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-20 text-slate-400 font-mono">
                                                    <FlaskConical size={56} className="mx-auto mb-4 opacity-30" />
                                                    <p className="text-xl">Sin experimentos asociados</p>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* INFO / EDIT TAB */}
                                    {activeTab === 'info' && (
                                        <div className="space-y-7">
                                            {/* Edit / Save bar */}
                                            <div className="flex items-center justify-between">
                                                <h3 className="text-lg font-mono font-bold text-slate-500 uppercase tracking-widest">
                                                    {isEditing ? '✏️  Modo Edición' : 'Datos de la Planta'}
                                                </h3>
                                                {!isEditing ? (
                                                    <button onClick={() => setIsEditing(true)}
                                                        className="flex items-center gap-2 px-5 py-2.5 font-mono font-bold text-base bg-amber-500 hover:bg-amber-600 text-white transition-colors">
                                                        <Pencil size={18} /> Editar Datos
                                                    </button>
                                                ) : (
                                                    <div className="flex gap-3">
                                                        <button onClick={() => setIsEditing(false)}
                                                            className="flex items-center gap-2 px-5 py-2.5 font-mono font-bold text-base border-2 border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                                                            <XCircle size={18} /> Cancelar
                                                        </button>
                                                        <button onClick={handleSave} disabled={isSaving}
                                                            className="flex items-center gap-2 px-6 py-2.5 font-mono font-bold text-base bg-green-600 hover:bg-green-700 text-white transition-colors disabled:opacity-50">
                                                            {isSaving ? <Activity className="animate-spin" size={18} /> : <Save size={18} />}
                                                            Guardar Cambios
                                                        </button>
                                                    </div>
                                                )}
                                            </div>

                                            {/* Core Fields */}
                                            <div className="grid grid-cols-2 gap-5">
                                                {[
                                                    { key: 'name', label: 'Nombre Planta', type: 'text' },
                                                    { key: 'especie_variedad', label: 'Especie / Variedad', type: 'text' },
                                                    { key: 'fecha_siembra', label: 'Fecha de Siembra', type: 'date' },
                                                    { key: 'node_id', label: 'Node ID', type: 'number' },
                                                ].map(({ key, label, type }) => (
                                                    <div key={key} className="border-2 border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-950">
                                                        <label className={labelCls}>{label}</label>
                                                        {isEditing ? (
                                                            <input type={type} value={editForm[key as keyof typeof editForm]}
                                                                onChange={e => setEditForm(prev => ({ ...prev, [key]: e.target.value }))}
                                                                className={inputCls} />
                                                        ) : (
                                                            <p className="text-xl font-mono font-bold text-slate-800 dark:text-white">
                                                                {editForm[key as keyof typeof editForm]}
                                                            </p>
                                                        )}
                                                    </div>
                                                ))}

                                                {/* Estado vital */}
                                                <div className="border-2 border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-950">
                                                    <label className={labelCls}>Estado Vital</label>
                                                    {isEditing ? (
                                                        <select value={editForm.estado_vital}
                                                            onChange={e => setEditForm(prev => ({ ...prev, estado_vital: e.target.value }))}
                                                            className={inputCls}>
                                                            {ESTADOS.map(s => <option key={s} value={s}>{s}</option>)}
                                                        </select>
                                                    ) : (
                                                        <p className="text-xl font-mono font-bold text-slate-800 dark:text-white">{editForm.estado_vital}</p>
                                                    )}
                                                </div>

                                                {/* ID (read-only) */}
                                                <div className="border-2 border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-950">
                                                    <label className={labelCls}>ID Registro</label>
                                                    <p className="text-xl font-mono font-bold text-slate-400">{plant.id}</p>
                                                </div>
                                            </div>

                                            {/* Metadata Científica */}
                                            <div>
                                                <h4 className="text-lg font-mono font-bold text-slate-500 uppercase tracking-widest mb-4">Metadata Científica</h4>
                                                <div className="grid grid-cols-2 gap-5">
                                                    {Object.entries(metaForm).map(([key, val]) => (
                                                        <div key={key} className="border-2 border-slate-200 dark:border-slate-800 p-5 bg-white dark:bg-slate-950">
                                                            <label className={labelCls}>{key.replace(/_/g, ' ')}</label>
                                                            {isEditing ? (
                                                                <input type="text" value={val}
                                                                    onChange={e => setMetaForm(prev => ({ ...prev, [key]: e.target.value }))}
                                                                    className={inputCls} />
                                                            ) : (
                                                                <p className="text-xl font-mono font-bold text-slate-800 dark:text-white">{val}</p>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
