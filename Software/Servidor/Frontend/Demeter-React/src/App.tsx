import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ExperimentDashboard } from './components/layout/ExperimentDashboard';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ExperimentDashboard />
    </QueryClientProvider>
  );
}

export default App;
