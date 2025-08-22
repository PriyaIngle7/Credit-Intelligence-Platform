import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CompanyDetail from './pages/CompanyDetail';
import CreditScores from './pages/CreditScores';
import DataIngestion from './pages/DataIngestion';
import ModelPerformance from './pages/ModelPerformance';

import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/company/:ticker" element={<CompanyDetail />} />
              <Route path="/credit-scores" element={<CreditScores />} />
              <Route path="/data-ingestion" element={<DataIngestion />} />
              <Route path="/model-performance" element={<ModelPerformance />} />
            </Routes>
          </Layout>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 