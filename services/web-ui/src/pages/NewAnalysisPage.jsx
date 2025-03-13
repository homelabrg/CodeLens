// src/pages/NewAnalysisPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import apiService from '../utils/api';

const NewAnalysisPage = () => {
  const { repositoryId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const queryParams = new URLSearchParams(location.search);
  const repoIdFromQuery = queryParams.get('repositoryId');
  
  const [repository, setRepository] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [submitting, setSubmitting] = useState(false);
  
  // Fetch repository details
  useEffect(() => {
    const id = repositoryId || repoIdFromQuery;
    if (!id) {
      setError({ message: 'Repository ID is required' });
      setLoading(false);
      return;
    }
    
    setLoading(true);
    apiService.repository.getRepository(id)
      .then(response => {
        setRepository(response.data);
        setError(null);
      })
      .catch(err => {
        setError(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [repositoryId, repoIdFromQuery]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!repository) return;
    
    setSubmitting(true);
    try {
      const response = await apiService.analysis.startAnalysis(
        repository.id,
        { 
          analysis_type: analysisType,
          // Add other parameters as needed
        },
        true // from repository
      );
      
      // Navigate to analysis results page
      navigate(`/analysis/${response.data.analysis_id}`);
    } catch (err) {
      setError(err);
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
        <p className="text-gray-500">Loading repository information...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">Error loading repository</p>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">New Analysis</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">Repository Information</h2>
        {repository && (
          <div>
            <p className="font-medium">{repository.owner}/{repository.repo}</p>
            <p className="text-sm text-gray-500">Branch: {repository.branch}</p>
          </div>
        )}
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4">Analysis Configuration</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="comprehensive">Comprehensive Analysis</option>
              <option value="quick">Quick Analysis</option>
              <option value="security">Security Scan</option>
              <option value="dependencies">Dependency Analysis</option>
            </select>
          </div>
          
          {/* Add more configuration options as needed */}
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center"
            >
              {submitting ? (
                <>
                  <span className="mr-2">Starting Analysis...</span>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                </>
              ) : (
                'Start Analysis'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAnalysisPage;