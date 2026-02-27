import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TopBar } from './TopBar';
import { useThemeStore } from '../../store/useThemeStore';

// Mock the zustand store
vi.mock('../../store/useThemeStore', () => ({
    useThemeStore: vi.fn(),
}));

describe('TopBar Component', () => {
    it('renders terminal text correctly', () => {
        (useThemeStore as any).mockReturnValue({
            isDarkMode: false,
            toggleTheme: vi.fn(),
        });

        render(<TopBar />);
        expect(screen.getByText('Demeter_Terminal')).toBeInTheDocument();
    });

    it('calls toggleTheme when theme button is clicked', () => {
        const toggleMock = vi.fn();
        (useThemeStore as any).mockReturnValue({
            isDarkMode: false,
            toggleTheme: toggleMock,
        });

        render(<TopBar />);
        const button = screen.getByTitle('SWITCH_MODE_DARK');
        fireEvent.click(button);
        expect(toggleMock).toHaveBeenCalled();
    });
});
