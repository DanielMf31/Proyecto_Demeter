import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ExperimentDashboard } from './components/layout/ExperimentDashboard';
import { AuthProvider, useAuth } from './store/AuthContext';
import { LoginPage } from './components/layout/LoginPage';

const queryClient = new QueryClient();

const MainApp: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return <ExperimentDashboard />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MainApp />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
