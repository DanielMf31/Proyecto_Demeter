import React, { useState } from 'react';
import { useAuth } from '../../store/AuthContext';
import { Terminal, Lock, User as UserIcon } from 'lucide-react';
import { Button } from '../ui/button'; // Assuming shadcn UI Button exists

export const LoginPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            if (!response.ok) {
                throw new Error('Credenciales incorrectas');
            }

            const data = await response.json();
            login(data.access_token);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error al conectar al servidor');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl mix-blend-screen" />
                <div className="absolute bottom-0 right-1/4 w-[30rem] h-[30rem] bg-emerald-500/10 rounded-full blur-3xl mix-blend-screen" />
            </div>

            <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="flex justify-center flex-col items-center">
                    <div className="h-16 w-16 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl flex items-center justify-center mb-6">
                        <Terminal className="h-8 w-8 text-emerald-400" />
                    </div>
                    <h2 className="mt-2 text-center text-3xl font-bold tracking-tight text-white">
                        Plataforma Demeter
                    </h2>
                    <p className="mt-2 text-center text-sm text-slate-400">
                        Node Analytics & Remote Execution
                    </p>
                </div>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="bg-slate-900 border border-slate-800 py-8 px-4 shadow-2xl sm:rounded-2xl sm:px-10">
                    <form className="space-y-6" onSubmit={handleLogin}>
                        <div>
                            <label className="block text-sm font-medium text-slate-300">
                                Usuario
                            </label>
                            <div className="mt-1 relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <UserIcon className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full pl-10 bg-slate-950 border border-slate-800 rounded-lg py-2 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent sm:text-sm transition-all"
                                    placeholder="admin"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300">
                                Contraseña
                            </label>
                            <div className="mt-1 relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full pl-10 bg-slate-950 border border-slate-800 rounded-lg py-2 text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent sm:text-sm transition-all"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="text-red-400 text-sm text-center bg-red-950/30 py-2 rounded-lg border border-red-900/50">
                                {error}
                            </div>
                        )}

                        <div>
                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-black bg-emerald-400 hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 focus:ring-offset-slate-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                            </Button>
                        </div>
                    </form>

                    {import.meta.env.DEV && (
                        <div className="mt-4 pt-4 border-t border-slate-800">
                            <Button
                                type="button"
                                onClick={() => {
                                    setUsername('admin');
                                    setPassword('admin');
                                    const formData = new URLSearchParams();
                                    formData.append('username', 'admin');
                                    formData.append('password', 'admin');
                                    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
                                    setIsLoading(true);
                                    fetch(`${API_URL}/auth/login`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                                        body: formData.toString(),
                                    })
                                        .then(res => res.json())
                                        .then(data => { login(data.access_token); })
                                        .catch(() => setError('Dev login failed'))
                                        .finally(() => setIsLoading(false));
                                }}
                                disabled={isLoading}
                                className="w-full flex justify-center py-2 px-4 border border-amber-800/50 rounded-lg shadow-sm text-xs font-medium text-amber-400 bg-amber-950/30 hover:bg-amber-950/50 transition-colors disabled:opacity-50"
                            >
                                Dev: Auto-login (admin)
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
