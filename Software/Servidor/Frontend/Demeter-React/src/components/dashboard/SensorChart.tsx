import React from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { SensorData, MetricType } from '../../types';

interface SensorChartProps {
    data: SensorData[];
    metric: MetricType;
}

const metricConfigs = {
    temperatura: {
        color: '#f97316', // Orange 500
        gradient: 'url(#colorTemp)',
        name: 'Temperatura',
        unit: '°C'
    },
    humedad: {
        color: '#3b82f6', // Blue 500
        gradient: 'url(#colorHum)',
        name: 'Humedad',
        unit: '%'
    }
};

export const SensorChart: React.FC<SensorChartProps> = ({ data, metric }) => {
    const config = metricConfigs[metric];

    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-soft h-[500px] flex flex-col">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h3 className="text-lg font-bold text-slate-800">
                        Tendencia de {config.name}
                    </h3>
                    <p className="text-sm text-slate-500">Lecturas de las últimas 24 horas</p>
                </div>
                <div className="text-right">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Unidad</span>
                    <p className="text-xl font-black text-slate-900">{config.unit}</p>
                </div>
            </div>

            <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#f97316" stopOpacity={0.15} />
                                <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorHum" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis
                            dataKey="timestamp"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                            tickFormatter={(str) => str.split(' ')[1].substring(0, 5)}
                            minTickGap={30}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                            domain={['auto', 'auto']}
                        />
                        <Tooltip
                            contentStyle={{
                                borderRadius: '16px',
                                border: 'none',
                                boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
                            }}
                            formatter={(value: any) => [`${parseFloat(value).toFixed(1)}${config.unit}`, config.name]}
                        />
                        <Area
                            type="monotone"
                            dataKey={metric}
                            stroke={config.color}
                            strokeWidth={4}
                            fillOpacity={1}
                            fill={config.gradient}
                            animationDuration={1000}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
