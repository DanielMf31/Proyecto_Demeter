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
                <span className={`px-1 font-mono text-[10px] font-black ${p.value ? 'text-green-600' : 'text-slate-400'
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
        <div className="bg-white border border-slate-300 rounded-none overflow-hidden">
            <div className="bg-slate-100 px-3 py-1.5 border-b border-slate-300 flex items-center justify-between">
                <h3 className="text-[10px] font-mono font-black text-slate-600 uppercase tracking-widest">Raw Data Stream</h3>
                <span className="text-[9px] font-mono text-slate-400">Total Records: {data.length}</span>
            </div>
            <div className="ag-theme-balham w-full h-[300px]">
                <AgGridReact
                    rowData={data}
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    pagination={true}
                    paginationPageSize={20}
                    rowHeight={28}
                    headerHeight={32}
                />
            </div>
        </div>
    );
};
