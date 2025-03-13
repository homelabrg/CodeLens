/**
 * Custom hook for making API calls with loading and error states
 * @returns {Object} API utility functions and state
 */
import { useState, useCallback } from 'react';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Make an API call and handle loading/error states
   * @param {Function} apiCall - API function to call
   * @param {Function} onSuccess - Callback for successful response
   * @param {Function} onError - Optional callback for error handling
   */
  const callApi = useCallback(async (apiCall, onSuccess, onError) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall();
      if (onSuccess) {
        onSuccess(response.data);
      }
      return response.data;
    } catch (err) {
      setError(err);
      if (onError) {
        onError(err);
      }
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, callApi };
}
