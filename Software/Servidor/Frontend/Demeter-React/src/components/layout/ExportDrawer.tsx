import React, { useState, useEffect } from 'react';
import { Download, X, Loader2, FileSpreadsheet, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../../store/AuthContext';
import { Button } from '../ui/button';

interface ExportDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportDrawer: React.FC<ExportDrawerProps> = ({ isOpen, onClose }) => {
  const { token } = useAuth();
  const [isExporting, setIsExporting] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<'idle' | 'queued' | 'started' | 'finished' | 'failed'>('idle');
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [errorMSG, setErrorMSG] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  // Start Export Job
  const handleStartExport = async () => {
    setIsExporting(true);
    setStatus('queued');
    setErrorMSG(null);
    setDownloadUrl(null);

    try {
      const response = await fetch(`${API_URL}/export/plants`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Fallo al iniciar el motor de exportación');

      const data = await response.json();
      setJobId(data.job_id);

    } catch (err) {
      setErrorMSG(err instanceof Error ? err.message : 'Error desconocido');
      setIsExporting(false);
      setStatus('failed');
    }
  };

  // Polling Effect
  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const checkStatus = async () => {
      if (!jobId) return;

      try {
        const response = await fetch(`${API_URL}/export/status/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) throw new Error('Error limitando el estado');

        const data = await response.json();
        setStatus(data.status);

        if (data.status === 'finished') {
          // Convert string to absolute URL if it is relative
          const baseUrl = API_URL.replace(/\/api\/?$/, '');
          const fullDownloadUrl = data.download_url?.startsWith('http')
            ? data.download_url
            : `${baseUrl}${data.download_url?.startsWith('/') ? '' : '/'}${data.download_url}`;

          setDownloadUrl(fullDownloadUrl);
          setIsExporting(false);

          // Automatically trigger download
          if (fullDownloadUrl) {
            window.location.href = fullDownloadUrl;
          }
        } else if (data.status === 'failed') {
          setErrorMSG(data.error || 'La exportación asíncrona ha fallado en el Worker.');
          setIsExporting(false);
        }

      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    if (isExporting && jobId) {
      intervalId = setInterval(checkStatus, 2000); // Poll every 2 seconds
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isExporting, jobId, token, API_URL]);

  return (
    <>
      {/* Overlay backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Drawer panel */}
      <div
        className={`fixed inset-y-0 right-0 z-50 w-full max-w-sm bg-slate-900 border-l border-slate-800 shadow-2xl transform transition-transform duration-300 ease-in-out flex flex-col ${isOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
      >
        <div className="flex items-center justify-between p-6 border-b border-slate-800 bg-slate-900/50">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
            Exportación Avanzada
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 flex-1 overflow-y-auto">
          <div className="space-y-6">

            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4">
              <h3 className="text-sm font-medium text-slate-300 mb-2">Rango de datos a descargar</h3>
              <select className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none">
                <option value="24h">Últimas 24h (Datos de Prueba)</option>
                <option value="7d" disabled>Últimos 7 días</option>
                <option value="30d" disabled>Último mes</option>
              </select>
            </div>

            <div className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-4 flex gap-3">
              <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <div className="text-sm text-blue-300">
                El motor asíncrono calculará automáticamente el <strong>VPD</strong> (Déficit de Presión de Vapor) y la <strong>Temperatura de Bulbo Húmedo</strong> e incluirá gráficas multi-nodo en el paquete Zip.
              </div>
            </div>

            {/* Status Flow */}
            {status !== 'idle' && (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4">

                <div className="flex items-center gap-3">
                  {status === 'finished' ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  ) : status === 'failed' ? (
                    <AlertCircle className="w-5 h-5 text-red-400" />
                  ) : (
                    <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
                  )}
                  <span className="text-sm font-medium text-slate-200">
                    {status === 'queued' && 'Encolando tarea en el Worker...'}
                    {status === 'started' && 'Procesando datos y dibujando gráficas...'}
                    {status === 'finished' && '¡Exportación completada exitosamente!'}
                    {status === 'failed' && 'La exportación ha fallado.'}
                  </span>
                </div>

                {errorMSG && (
                  <div className="text-xs text-red-400 bg-red-950/30 p-3 rounded border border-red-900/30">
                    {errorMSG}
                  </div>
                )}

              </div>
            )}

          </div>
        </div>

        <div className="p-6 border-t border-slate-800 bg-slate-900/80 backdrop-blur-md">
          {!downloadUrl ? (
            <Button
              onClick={handleStartExport}
              disabled={isExporting}
              className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20"
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generando Informe...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Confirmar Exportación
                </>
              )}
            </Button>
          ) : (
            <div className="space-y-3">
              <Button
                onClick={() => window.location.href = downloadUrl}
                className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
              >
                <Download className="w-4 h-4" />
                Descargar de Nuevo
              </Button>
              <Button
                onClick={() => { setStatus('idle'); setDownloadUrl(null); }}
                variant="outline"
                className="w-full border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                Nueva Exportación
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};
