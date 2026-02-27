import React from 'react';
import Plot from 'react-plotly.js';
import { SensorData, MetricType } from '../../types';
import { useThemeStore } from '../../store/useThemeStore';

interface ScientificChartProps {
    data: SensorData[];
    metric: MetricType;
}

const config = {
    temperatura: {
        name: 'TEMPERATURA',
        color: '#ef4444', // Red 500
        unit: '°C'
    },
    humedad: {
        name: 'HUMEDAD',
        color: '#3b82f6', // Blue 500
        unit: '%'
    },
    vpd: {
        name: 'VPD',
        color: '#10b981', // Emerald 500
        unit: 'kPa'
    }
};

export const ScientificChart: React.FC<ScientificChartProps> = ({ data, metric }) => {
    const { isDarkMode } = useThemeStore();
    const current = config[metric];

    // Safety check just in case VPD wasn't calculated for live buffer yet
    const validData = data.filter(d => d[metric as keyof SensorData] !== undefined);

    const xData = validData.map(d => d.timestamp);
    const yData = validData.map(d => Number(d[metric as keyof SensorData]).toFixed(2));

    const bgColor = isDarkMode ? '#0f172a' : '#ffffff';
    const gridColor = isDarkMode ? '#334155' : '#e5e7eb';
    const tickColor = isDarkMode ? '#94a3b8' : '#64748b';

    return (
        <div className={`border rounded-none overflow-hidden h-[400px] transition-colors ${isDarkMode ? 'border-slate-800 bg-slate-900' : 'border-slate-300 bg-white'}`}>
            <Plot
                data={[
                    {
                        x: xData,
                        y: yData,
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: current.name,
                        line: {
                            color: current.color,
                            width: 2,
                            shape: 'linear' // Scientific requirement: no smoothing
                        },
                        marker: {
                            size: 5,
                            symbol: 'square',
                            color: current.color,
                            line: { width: 1, color: isDarkMode ? '#0f172a' : '#fff' }
                        }
                    }
                ]}
                layout={{
                    autosize: true,
                    margin: { t: 50, r: 50, b: 70, l: 80 },
                    showlegend: false,
                    plot_bgcolor: bgColor,
                    paper_bgcolor: bgColor,
                    xaxis: {
                        gridcolor: gridColor,
                        zeroline: false,
                        tickfont: { family: 'Monaco, monospace', size: 20, color: tickColor },
                        gridwidth: 1,
                    },
                    yaxis: {
                        gridcolor: gridColor,
                        zeroline: false,
                        tickfont: { family: 'Monaco, monospace', size: 20, color: tickColor },
                        gridwidth: 1,
                        title: {
                            text: `[ ${current.name} / ${current.unit} ]`,
                            font: { family: 'Monaco, monospace', size: 20, color: tickColor }
                        }
                    },
                    hovermode: 'closest',
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
                config={{
                    displaylogo: false,
                    responsive: true,
                    modeBarButtonsToRemove: ['select2d', 'lasso2d']
                }}
            />
        </div>
    );
};
