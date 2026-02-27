import React, { ButtonHTMLAttributes } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'outline' | 'ghost' | 'link';
    size?: 'default' | 'sm' | 'lg' | 'icon';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className = '', variant = 'default', size = 'default', ...props }, ref) => {
        let baseStyles = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50';

        let variants = {
            default: 'bg-emerald-500 text-slate-950 hover:bg-emerald-500/90 shadow',
            outline: 'border border-slate-700 bg-transparent shadow-sm hover:bg-slate-800 hover:text-slate-100',
            ghost: 'hover:bg-slate-800 hover:text-slate-100',
            link: 'text-emerald-500 underline-offset-4 hover:underline'
        };

        let sizes = {
            default: 'h-9 px-4 py-2',
            sm: 'h-8 px-3 text-xs',
            lg: 'h-10 px-8',
            icon: 'h-9 w-9'
        };

        const combinedClassName = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;

        return (
            <button
                ref={ref}
                className={combinedClassName}
                {...props}
            />
        );
    }
);

Button.displayName = 'Button';
