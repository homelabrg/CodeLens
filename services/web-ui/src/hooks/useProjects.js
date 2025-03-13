import { useState, useEffect, useCallback } from 'react';
import apiService from '../utils/api';
import { useApi } from './useApi';

/**
 * Hook for working with projects
 */
export function useProjects() {
  const [projects, setProjects] = useState([]);
  const { loading, error, callApi } = useApi();

  // Load projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Fetch all projects
  const fetchProjects = useCallback(() => {
    callApi(
      apiService.project.listProjects,
      (data) => setProjects(data || []),
    );
  }, [callApi]);

  // Rest of the hook implementation...
  
  return {
    projects,
    loading,
    error,
    fetchProjects
  };
}