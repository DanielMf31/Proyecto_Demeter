import React, { useState } from 'react';
import { X, Send, Sparkles, User, Bot } from 'lucide-react';
import { useUIStore } from '../../store/useUIStore';
import { Message } from '../../types';

export const AISidebar: React.FC = () => {
    const { isAISidebarOpen, setAISidebarOpen } = useUIStore();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: '¡Hola! Soy tu asistente Demeter AI. He analizado los datos de las últimas 24 horas. ¿Quieres saber algo específico sobre el experimento?',
            sender: 'ai',
            timestamp: new Date(),
        }
    ]);
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text: input,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages([...messages, userMsg]);
        setInput('');

        // Simulate AI response
        setTimeout(() => {
            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                text: 'He detectado que la humedad ha bajado un 5% en la última hora mientras la temperatura subía. Podría ser un buen momento para revisar el sistema de riego.',
                sender: 'ai',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, aiMsg]);
        }, 1000);
    };

    if (!isAISidebarOpen) return null;

    return (
        <>
            <div
                className="fixed inset-0 bg-slate-900/10 backdrop-blur-sm z-40"
                onClick={() => setAISidebarOpen(false)}
            />
            <div className="fixed top-0 right-0 h-full w-[400px] bg-white shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-300">
                <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-blue-600 text-white rounded-lg">
                            <Sparkles size={20} />
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800">Demeter AI</h3>
                            <p className="text-xs text-green-600 font-medium">Analizando datos en tiempo real</p>
                        </div>
                    </div>
                    <button
                        onClick={() => setAISidebarOpen(false)}
                        className="p-2 hover:bg-slate-200 rounded-lg transition-colors"
                    >
                        <X size={20} className="text-slate-500" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
                        >
                            <div className={`p-2 rounded-lg h-fit ${msg.sender === 'ai' ? 'bg-blue-50 text-blue-600' : 'bg-slate-100 text-slate-600'
                                }`}>
                                {msg.sender === 'ai' ? <Bot size={18} /> : <User size={18} />}
                            </div>
                            <div className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${msg.sender === 'ai'
                                    ? 'bg-blue-50/50 text-slate-700 rounded-tl-none border border-blue-100/50'
                                    : 'bg-slate-900 text-white rounded-tr-none'
                                }`}>
                                {msg.text}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="p-6 border-t border-slate-100">
                    <div className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Pregunta sobre los datos..."
                            className="w-full pl-4 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-sm"
                        />
                        <button
                            onClick={handleSend}
                            className="absolute right-2 top-1.5 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            <Send size={18} />
                        </button>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-3 text-center">
                        Demeter AI puede cometer errores. Verifica la información crítica.
                    </p>
                </div>
            </div>
        </>
    );
};
