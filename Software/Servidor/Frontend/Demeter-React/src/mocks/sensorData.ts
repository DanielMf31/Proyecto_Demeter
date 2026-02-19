import { SensorData } from '../types';
import { subHours, format } from 'date-fns';

export const generateMockSensorData = (): SensorData[] => {
    const data: SensorData[] = [];
    const now = new Date();

    for (let i = 24; i >= 0; i--) {
        const time = subHours(now, i);
        data.push({
            timestamp: format(time, "yyyy-MM-dd HH:mm:ss"),
            temperatura: 20 + Math.random() * 10,
            humedad: 40 + Math.random() * 30,
            estado_riego: Math.random() > 0.8,
        });
    }
    return data;
};

export const MOCK_SUMMARY = {
    id: 'exp-001',
    nombre: 'Cultivo de Tomate - Invernadero 1',
    fecha_inicio: '2026-02-01',
    alertas_activas: 2
};
