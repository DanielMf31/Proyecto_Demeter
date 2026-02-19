import React from 'react';
import Plot from 'react-plotly.js';
import { SensorData, MetricType } from '../../types';

interface ScientificChartProps {
    data: SensorData[];
    metric: MetricType;
}

const config = {
    temperatura: {
        name: 'TEMPERATURA',
        color: '#d62728', // Brick Red
        unit: '°C'
    },
    humedad: {
        name: 'HUMEDAD',
        color: '#1f77b4', // Steel Blue
        unit: '%'
    }
};

export const ScientificChart: React.FC<ScientificChartProps> = ({ data, metric }) => {
    const current = config[metric];

    const xData = data.map(d => d.timestamp);
    const yData = data.map(d => d[metric as keyof SensorData] as number);

    return (
        <div className="bg-white border border-slate-300 rounded-none overflow-hidden h-[400px]">
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
                            line: { width: 1, color: '#fff' }
                        }
                    }
                ]}
                layout={{
                    autosize: true,
                    margin: { t: 30, r: 30, b: 40, l: 50 },
                    showlegend: false,
                    plot_bgcolor: '#ffffff',
                    paper_bgcolor: '#ffffff',
                    xaxis: {
                        gridcolor: '#e5e7eb',
                        zeroline: false,
                        tickfont: { family: 'Monaco, monospace', size: 10, color: '#64748b' },
                        gridwidth: 1,
                    },
                    yaxis: {
                        gridcolor: '#e5e7eb',
                        zeroline: false,
                        tickfont: { family: 'Monaco, monospace', size: 10, color: '#64748b' },
                        gridwidth: 1,
                        title: {
                            text: `[ ${current.name} / ${current.unit} ]`,
                            font: { family: 'Monaco, monospace', size: 10, color: '#94a3b8' }
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
