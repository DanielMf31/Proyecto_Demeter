import type { PlannerStep } from "./types/demeter_types.js";

// ── State ──────────────────────────────────────────────────────────────────
export let steps: PlannerStep[] = [];
export let nextId = 1;

const MAX_HISTORY = 50;
const undoStack: PlannerStep[][] = [];
const redoStack: PlannerStep[][] = [];

// ── Setters ────────────────────────────────────────────────────────────────
export function setSteps(newSteps: PlannerStep[]): void {
    steps = newSteps;
}

export function setNextId(id: number): void {
    nextId = id;
}

export function pushStep(step: PlannerStep): void {
    steps.push(step);
}

// ── History ────────────────────────────────────────────────────────────────
export function saveSnapshot(): void {
    undoStack.push(JSON.parse(JSON.stringify(steps)) as PlannerStep[]);
    if (undoStack.length > MAX_HISTORY) undoStack.shift();
    redoStack.length = 0;
}

export function canUndo(): boolean { return undoStack.length > 0; }
export function canRedo(): boolean { return redoStack.length > 0; }

export function undo(): PlannerStep[] | null {
    if (!canUndo()) return null;
    redoStack.push(JSON.parse(JSON.stringify(steps)) as PlannerStep[]);
    steps = undoStack.pop()!;
    nextId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    return steps;
}

export function redo(): PlannerStep[] | null {
    if (!canRedo()) return null;
    undoStack.push(JSON.parse(JSON.stringify(steps)) as PlannerStep[]);
    steps = redoStack.pop()!;
    nextId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    return steps;
}
