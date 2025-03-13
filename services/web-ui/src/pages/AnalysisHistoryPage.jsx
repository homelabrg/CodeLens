// src/pages/AnalysisHistoryPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  FiClock, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiFileText, 
  FiCode, 
  FiEye, 
  FiBarChart, 
  FiFilter, 
  FiRefreshCw,
  FiArrowRight
} from 'react-icons/fi';
import apiService from '../utils/api';

const AnalysisHistoryPage = () => {
  const { repositoryId } = useParams();
  const navigate = useNavigate();
  
  const [repository, setRepository] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    type: 'all'
  });
  const [selectedAnalyses, setSelectedAnalyses] = useState([]);
  const [sortBy, setSortBy] = useState('date-desc');

  // Fetch repository and its analyses
  useEffect(() => {
    const fetchRepositoryAndAnalyses = async () => {
        try {
          setLoading(true);
          
          // Get repository details
          const repoResponse = await apiService.repository.getRepository(repositoryId);
          setRepository(repoResponse.data);
          
          // Get all projects first
          const projectsResponse = await apiService.project.listProjects();
          
          // Extract owner/repo name for matching
          const repoName = `${repoResponse.data.owner}/${repoResponse.data.repo}`;
          
          // Find all projects that match this repository name
          const matchingProjects = projectsResponse.data.filter(project => 
            project.name === repoName || project.name.includes(repoName)
          );
          
          if (matchingProjects.length === 0) {
            setError(new Error('No projects found for this repository'));
            setLoading(false);
            return;
          }
          
          // Fetch analyses for each matching project
          const analysesPromises = matchingProjects.map(project => 
            apiService.analysis.listProjectAnalyses(project.id)
          );
          
          const analysesResponses = await Promise.all(analysesPromises);
          
          // Combine all analyses from all matching projects
          const allAnalyses = analysesResponses.flatMap(response => response.data);
          
          setAnalyses(allAnalyses);
          
          setError(null);
        } catch (err) {
          setError(err);
          console.error('Error fetching data:', err);
        } finally {
          setLoading(false);
        }
      };
    
    fetchRepositoryAndAnalyses();
  }, [repositoryId]);

  // Apply filters and sorting
  const getFilteredAndSortedAnalyses = () => {
    // Filter analyses
    let filtered = [...analyses];
    
    if (filters.status !== 'all') {
      filtered = filtered.filter(analysis => analysis.status === filters.status);
    }
    
    if (filters.dateRange !== 'all') {
      const now = new Date();
      let startDate = new Date();
      
      switch (filters.dateRange) {
        case 'today':
          startDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          startDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(now.getMonth() - 1);
          break;
        default:
          startDate = new Date(0); // Beginning of time
      }
      
      filtered = filtered.filter(analysis => {
        const analysisDate = new Date(analysis.created_at);
        return analysisDate >= startDate;
      });
    }
    
    if (filters.type !== 'all') {
      filtered = filtered.filter(analysis => 
        analysis.analysis_types && analysis.analysis_types.includes(filters.type)
      );
    }
    
    // Sort analyses
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date-asc':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'date-desc':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'status':
          return a.status.localeCompare(b.status);
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });
    
    return filtered;
  };

  const filteredAnalyses = getFilteredAndSortedAnalyses();
  
  // Handle toggling analysis selection for comparison
  const toggleAnalysisSelection = (analysisId) => {
    if (selectedAnalyses.includes(analysisId)) {
      setSelectedAnalyses(selectedAnalyses.filter(id => id !== analysisId));
    } else {
      // Limit to 2 selections for comparison
      if (selectedAnalyses.length < 2) {
        setSelectedAnalyses([...selectedAnalyses, analysisId]);
      } else {
        // Replace the oldest selection
        setSelectedAnalyses([selectedAnalyses[1], analysisId]);
      }
    }
  };
  
  // Handle comparing selected analyses
  const handleCompare = () => {
    if (selectedAnalyses.length === 2) {
      navigate(`/analysis/compare?ids=${selectedAnalyses.join(',')}`);
    }
  };
  
  // Render status badge
  const renderStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <FiCheckCircle className="mr-1" />
            Completed
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <FiAlertCircle className="mr-1" />
            Failed
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <FiRefreshCw className="mr-1 animate-spin" />
            In Progress
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <FiClock className="mr-1" />
            Pending
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {status}
          </span>
        );
    }
  };
  
  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
        <p className="text-gray-500">Loading analysis history...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">Error loading analysis history</p>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Analysis History</h1>
        {repository && (
          <p className="text-gray-600">
            Repository: <span className="font-medium">{repository.owner}/{repository.repo}</span>
          </p>
        )}
      </div>
      
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status-filter"
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="all">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="pending">Pending</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="date-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Date Range
            </label>
            <select
              id="date-filter"
              value={filters.dateRange}
              onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">Last 7 Days</option>
              <option value="month">Last 30 Days</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Analysis Type
            </label>
            <select
              id="type-filter"
              value={filters.type}
              onChange={(e) => setFilters({...filters, type: e.target.value})}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="all">All Types</option>
              <option value="code">Code</option>
              <option value="dependencies">Dependencies</option>
              <option value="business">Business</option>
              <option value="architecture">Architecture</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              id="sort-by"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              <option value="date-desc">Date (Newest First)</option>
              <option value="date-asc">Date (Oldest First)</option>
              <option value="status">Status</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilters({status: 'all', dateRange: 'all', type: 'all'})}
              className="ml-2 px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Comparison bar - shows when analyses are selected */}
      {selectedAnalyses.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-blue-800">
                {selectedAnalyses.length} {selectedAnalyses.length === 1 ? 'analysis' : 'analyses'} selected
              </span>
              <div className="flex items-center mt-1">
                {selectedAnalyses.map((id, index) => {
                  const analysis = analyses.find(a => a.analysis_id === id);
                  return (
                    <div key={id} className="flex items-center">
                      {index > 0 && <FiArrowRight className="mx-2 text-blue-400" />}
                      <span className="px-2 py-1 bg-white rounded text-xs border border-blue-200">
                        {new Date(analysis?.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div>
              <button
                onClick={handleCompare}
                disabled={selectedAnalyses.length !== 2}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  selectedAnalyses.length === 2
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <FiBarChart className="inline-block mr-1" />
                Compare Analyses
              </button>
              <button
                onClick={() => setSelectedAnalyses([])}
                className="ml-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Clear Selection
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Analysis list */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-medium">Analysis History</h2>
        </div>
        
        {filteredAnalyses.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500">No analyses found matching your filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Select
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Types
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Files
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAnalyses.map((analysis) => (
                  <tr key={analysis.analysis_id} className={selectedAnalyses.includes(analysis.analysis_id) ? 'bg-blue-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedAnalyses.includes(analysis.analysis_id)}
                        onChange={() => toggleAnalysisSelection(analysis.analysis_id)}
                        disabled={analysis.status !== 'completed' && !selectedAnalyses.includes(analysis.analysis_id)}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(analysis.created_at).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderStatusBadge(analysis.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-wrap gap-1">
                        {analysis.analysis_types?.map((type) => (
                          <span key={type} className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                            {type}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {analysis.file_count ? (
                        <div className="flex items-center">
                          <FiFileText className="mr-1" />
                          {analysis.file_count} files
                        </div>
                      ) : (
                        'N/A'
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {analysis.status === 'completed' ? (
                        <Link
                        to={`/analysis/${analysis.id}`}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                        <FiEye className="inline-block mr-1" />
                        View
                        </Link>
                    ) : (
                        <span className="text-gray-400 mr-3 cursor-not-allowed">
                        <FiEye className="inline-block mr-1" />
                        View
                        </span>
                    )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisHistoryPage;