import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { PlannerStep, makeExecSequence } from '../types';
import { apiService } from '../services/apiService';

interface PlannerState {
    steps: PlannerStep[];
    nextId: number;
    isExecuting: boolean;
    addStep: (step: Omit<PlannerStep, 'id'>) => void;
    removeStep: (id: number) => void;
    duplicateStep: (id: number) => void;
    updateSteps: (steps: PlannerStep[]) => void;
    executeSequence: () => Promise<void>;
    clearSteps: () => void;
}

export const usePlannerStore = create<PlannerState>()(
    persist(
        (set, get) => ({
            steps: [],
            nextId: 1,
            isExecuting: false,

            addStep: (step) => set((state) => ({
                steps: [...state.steps, { ...step, id: state.nextId }],
                nextId: state.nextId + 1,
            })),

            removeStep: (id) => set((state) => ({
                steps: state.steps.filter((s) => s.id !== id),
            })),

            duplicateStep: (id) => set((state) => {
                const idx = state.steps.findIndex((s) => s.id === id);
                if (idx === -1) return state;
                const copy = { ...state.steps[idx], id: state.nextId };
                const newSteps = [...state.steps];
                newSteps.splice(idx + 1, 0, copy);
                return {
                    steps: newSteps,
                    nextId: state.nextId + 1,
                };
            }),

            updateSteps: (steps) => set({ steps }),

            executeSequence: async () => {
                const { steps } = get();
                if (steps.length === 0) return;

                set({ isExecuting: true });
                const cmd = makeExecSequence(steps);
                const res = await apiService.postCommand(cmd);

                // In a real SCADA system, we might wait for a completion report via WS
                // For now, we'll just reset the executing state after the API call
                set({ isExecuting: false });

                if (res?.status === 'error') {
                    console.error('Sequence execution failed:', res.message);
                }
            },

            clearSteps: () => set({ steps: [], nextId: 1 }),
        }),
        {
            name: 'demeter-planner-storage',
        }
    )
);
