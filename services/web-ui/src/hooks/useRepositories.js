import { useState, useEffect, useCallback } from 'react';
import apiService from '../utils/api';
import { useApi } from './useApi';

/**
 * Hook for working with GitHub repositories
 */
export function useRepositories() {
  const [repositories, setRepositories] = useState([]);
  const { loading, error, callApi } = useApi();

  // Load repositories on mount
  useEffect(() => {
    fetchRepositories();
  }, []);

  // Fetch all repositories
  const fetchRepositories = useCallback(() => {
    callApi(
      apiService.repository.listRepositories,
      (data) => setRepositories(data || []),
    );
  }, [callApi]);

  // Get a single repository
  const getRepository = useCallback((repositoryId) => {
    return callApi(
      () => apiService.repository.getRepository(repositoryId)
    );
  }, [callApi]);

  // Clone a repository
  const cloneRepository = useCallback((url, branch = 'main') => {
    return callApi(
      () => apiService.repository.cloneRepository({ repository_url: url, branch }),
      (data) => {
        // Add the new repository to the list
        fetchRepositories();
        return data;
      }
    );
  }, [callApi, fetchRepositories]);

  // Delete a repository
  const deleteRepository = useCallback((repositoryId) => {
    return callApi(
      () => apiService.repository.deleteRepository(repositoryId),
      () => {
        // Remove the repository from the list
        setRepositories(prev => prev.filter(repo => repo.id !== repositoryId));
      }
    );
  }, [callApi]);

  return {
    repositories,
    loading,
    error,
    fetchRepositories,
    getRepository,
    cloneRepository,
    deleteRepository
  };
}