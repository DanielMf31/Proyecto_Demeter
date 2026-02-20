import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-balham.css';
import { SensorData } from '../../types';
import { ColDef } from 'ag-grid-community';

interface DataTableProps {
    data: SensorData[];
}

export const DataTable: React.FC<DataTableProps> = ({ data }) => {
    const columnDefs = useMemo<ColDef[]>(() => [
        {
            field: 'timestamp',
            headerName: 'TIMESTAMP [UTC]',
            flex: 2,
            sortable: true,
            filter: true,
            cellClass: 'font-mono text-[11px]'
        },
        {
            field: 'temperatura',
            headerName: 'TEMP [°C]',
            flex: 1,
            valueFormatter: (p) => p.value.toFixed(2),
            cellClass: 'font-mono text-[11px] text-right text-red-700'
        },
        {
            field: 'humedad',
            headerName: 'HUM [%]',
            flex: 1,
            valueFormatter: (p) => p.value.toFixed(2),
            cellClass: 'font-mono text-[11px] text-right text-blue-700'
        },
        {
            field: 'estado_riego',
            headerName: 'VALVE_STATE',
            flex: 1,
            cellRenderer: (p: any) => (
                <span className={`px-2 py-0.5 font-mono text-xs font-black border-2 ${p.value ? 'bg-green-100 text-green-700 border-green-300' : 'bg-slate-100 text-slate-400 border-slate-200'
                    }`}>
                    {p.value ? '[ ACTIVE ]' : '[ CLOSED ]'}
                </span>
            )
        }
    ], []);

    const defaultColDef = useMemo(() => ({
        resizable: true,
        sortable: true
    }), []);

    return (
        <div className="bg-white dark:bg-slate-900 border-2 border-slate-300 dark:border-slate-800 rounded-none overflow-hidden">
            <div className="bg-slate-100 dark:bg-slate-800 px-5 py-3 border-b-2 border-slate-300 dark:border-slate-800 flex items-center justify-between">
                <h3 className="text-xs font-mono font-black text-slate-600 dark:text-slate-400 uppercase tracking-widest">Memory_Buffer_Data_Stream</h3>
                <span className="text-xs font-mono text-slate-400">TOTAL_RECORDS: {data.length}</span>
            </div>
            <div className="ag-theme-balham w-full h-[500px]">
                <AgGridReact
                    rowData={data}
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    pagination={true}
                    paginationPageSize={10}
                    rowHeight={40}
                    headerHeight={44}
                />
            </div>
        </div>
    );
};
