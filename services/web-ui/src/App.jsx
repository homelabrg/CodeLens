import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/common/MainLayout';
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailsPage from './pages/ProjectDetailsPage';
import RepositoriesPage from './pages/RepositoriesPage';
import AnalysesPage from './pages/AnalysisPage';
import AnalysisDetailsPage from './pages/AnalysisDetailsPage';  
import SettingsPage from './pages/SettingsPage';
import NotFoundPage from './pages/NotFoundPage';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import NewAnalysisPage from './pages/NewAnalysisPage';
import AnalysisResultsPage from './pages/AnalysisResultsPage';
import AnalysisHistoryPage from './pages/AnalysisHistoryPage';
import AnalysisComparePage from './pages/AnalysisComparePage';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <MainLayout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailsPage />} />
            <Route path="/repositories" element={<RepositoriesPage />} />
            <Route path="/analysis" element={<AnalysesPage />} />
            {/* <Route path="/analysis/:analysisId" element={<AnalysisDetailsPage />} /> */}
            <Route path="/analysis/new" element={<NewAnalysisPage />} />
            <Route path="/analysis/:analysisId" element={<AnalysisResultsPage />} />
            <Route path="/analysis/compare" element={<AnalysisComparePage />} />
            <Route path="/repositories/:repositoryId/analyses" element={<AnalysisHistoryPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </MainLayout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
