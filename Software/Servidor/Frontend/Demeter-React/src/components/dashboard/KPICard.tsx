import React from 'react';
import { LucideIcon } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface KPICardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    color?: 'blue' | 'green' | 'red' | 'orange';
}

const colorStyles = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    orange: 'bg-orange-50 text-orange-600',
};

export const KPICard: React.FC<KPICardProps> = ({ title, value, icon: Icon, trend, color = 'blue' }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-soft">
            <div className="flex items-center justify-between mb-4">
                <div className={cn("p-2.5 rounded-xl", colorStyles[color])}>
                    <Icon size={22} />
                </div>
                {trend && (
                    <span className={cn(
                        "text-xs font-medium px-2 py-1 rounded-full",
                        trend.isPositive ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"
                    )}>
                        {trend.isPositive ? '+' : ''}{trend.value}%
                    </span>
                )}
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
            </div>
        </div>
    );
};
