import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { SensorData } from '../../types';
import { ColDef, themeQuartz, colorSchemeDark } from 'ag-grid-community';
import { useThemeStore } from '../../store/useThemeStore';

interface DataTableProps {
    data: SensorData[];
}

export const DataTable: React.FC<DataTableProps> = ({ data }) => {
    const { isDarkMode } = useThemeStore();

    const columnDefs = useMemo<ColDef[]>(() => [
        {
            field: 'timestamp',
            headerName: 'TIMESTAMP [UTC]',
            flex: 2,
            sortable: true,
            filter: true,
            cellClass: 'font-mono text-xl text-slate-800 dark:text-slate-100' // Added explicit white/dark switch
        },
        {
            field: 'temperatura',
            headerName: 'TEMP [°C]',
            flex: 1,
            valueFormatter: (p) => p.value !== undefined ? Number(p.value).toFixed(2) : '--',
            cellClass: 'font-mono text-xl text-right text-red-700 dark:text-red-300' // Brightened to 300
        },
        {
            field: 'humedad',
            headerName: 'HUM [%]',
            flex: 1,
            valueFormatter: (p) => p.value !== undefined ? Number(p.value).toFixed(2) : '--',
            cellClass: 'font-mono text-xl text-right text-blue-700 dark:text-sky-300' // Brightened to 300
        },
        {
            field: 'vpd',
            headerName: 'VPD [kPa]',
            flex: 1,
            valueFormatter: (p) => p.value !== undefined ? Number(p.value).toFixed(2) : '--',
            cellClass: 'font-mono text-xl text-right text-emerald-700 dark:text-emerald-300' // Brightened to 300
        }
    ], []);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true
    }), []);

    const gridTheme = isDarkMode
        ? themeQuartz.withPart(colorSchemeDark).withParams({
            backgroundColor: '#1e293b',       // Tailwind slate-800 (matches chart)
            headerBackgroundColor: '#1e293b', // Tailwind slate-800 (matches chart)
            headerTextColor: '#ffffff'        // White for better contrast
        })
        : themeQuartz.withParams({
            backgroundColor: '#ffffff',       // standard white
            headerBackgroundColor: '#f8fafc', // Tailwind slate-50
            headerTextColor: '#0284c7'        // Tailwind sky-600
        });

    return (
        <div className="bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 rounded-none overflow-hidden transition-colors">
            <div className="bg-slate-100 dark:bg-slate-800 px-5 py-4 border-b-2 border-slate-300 dark:border-slate-800 flex items-center justify-between">
                <h3 className="text-sm font-mono font-black text-slate-600 dark:text-slate-400 uppercase tracking-widest">Memory_Buffer_Data_Stream</h3>
                <span className="text-sm font-mono text-slate-400">TOTAL_RECORDS: {data.length}</span>
            </div>
            <div className="w-full h-[500px]">
                <AgGridReact
                    theme={gridTheme}
                    rowData={data}
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    pagination={true}
                    paginationPageSize={10}
                    paginationPageSizeSelector={[10, 25, 50, 100]}
                    rowHeight={64}
                    headerHeight={68}
                />
            </div>
        </div>
    );
};
