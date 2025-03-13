// services/web-ui/src/hooks/useAnalysis.js
import { useState, useCallback, useEffect } from 'react';
import apiService from '../utils/api';
import { useApi } from './useApi';

/**
 * Hook for working with code analysis
 */
export function useAnalysis() {
  const { loading, error, callApi } = useApi();
  const [analysisResults, setAnalysisResults] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState(null);
  
  // Start an analysis
  const startAnalysis = useCallback((projectId, analysisTypes = ['code', 'dependencies', 'business', 'architecture'], fromRepository = false) => {
    return callApi(
      () => apiService.analysis.startAnalysis(projectId, { analysis_types: analysisTypes }, fromRepository),
      (data) => {
        setAnalysisStatus({
          analysisId: data.analysis_id,
          status: data.status,
          progress: data.progress
        });
        return data;
      }
    );
  }, [callApi]);

  // Get analysis status
  const getAnalysisStatus = useCallback((analysisId) => {
    return callApi(
      () => apiService.analysis.getAnalysisStatus(analysisId),
      (data) => {
        setAnalysisStatus({
          analysisId: data.id || data.analysis_id,
          status: data.status,
          progress: data.progress
        });
        return data;
      }
    );
  }, [callApi]);

  // Poll analysis status
  const pollAnalysisStatus = useCallback((analysisId, interval = 3000, onComplete) => {
    const poll = setInterval(async () => {
      const status = await getAnalysisStatus(analysisId);
      
      if (status && (status.status === 'completed' || status.status === 'failed')) {
        clearInterval(poll);
        if (onComplete) {
          onComplete(status);
        }
      }
    }, interval);
    
    // Return cleanup function
    return () => clearInterval(poll);
  }, [getAnalysisStatus]);

  // Get analysis results
  const getAnalysisResults = useCallback((analysisId) => {
    return callApi(
      () => apiService.analysis.getAnalysisResults(analysisId),
      (data) => {
        setAnalysisResults(data);
        return data;
      }
    );
  }, [callApi]);

  // Get analysis summary
  const getAnalysisSummary = useCallback((analysisId) => {
    return callApi(
      () => apiService.analysis.getAnalysisSummary(analysisId)
    );
  }, [callApi]);

  // Analyze a code snippet
  const analyzeCode = useCallback((code, language, filename = null) => {
    return callApi(
      () => apiService.analysis.analyzeCode({ code, language, filename })
    );
  }, [callApi]);

  return {
    loading,
    error,
    analysisResults,
    analysisStatus,
    startAnalysis,
    getAnalysisStatus,
    pollAnalysisStatus,
    getAnalysisResults,
    getAnalysisSummary,
    analyzeCode
  };
}