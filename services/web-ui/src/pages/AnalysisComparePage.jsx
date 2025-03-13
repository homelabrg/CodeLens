// src/pages/AnalysisComparePage.jsx
import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  FiArrowLeft, 
  FiFileText, 
  FiCode, 
  FiPackage, 
  FiGitBranch, 
  FiArrowRight,
  FiChevronUp,
  FiChevronDown,
  FiAlertCircle
} from 'react-icons/fi';
import apiService from '../utils/api';

const AnalysisComparePage = () => {
  const [searchParams] = useSearchParams();
  const analysisIds = searchParams.get('ids')?.split(',') || [];
  
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    languages: true,
    dependencies: false,
    code: false,
    architecture: false
  });
  
  useEffect(() => {
    const fetchAnalyses = async () => {
      if (analysisIds.length !== 2) {
        setError(new Error('Please select two analyses to compare'));
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        
        const results = await Promise.all(
          analysisIds.map(id => apiService.analysis.getAnalysisResults(id))
        );
        
        setAnalyses(results.map(result => result.data));
        setError(null);
      } catch (err) {
        setError(err);
        console.error('Error fetching analyses for comparison:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalyses();
  }, [analysisIds]);
  
  // Toggle section expansion
  const toggleSection = (section) => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section]
    });
  };
  
  // Helper to format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Helper to get analysis age difference
  const getAgeDifference = () => {
    if (analyses.length !== 2) return null;
    
    const date1 = new Date(analyses[0].created_at);
    const date2 = new Date(analyses[1].created_at);
    const diffTime = Math.abs(date2 - date1);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (diffDays > 0) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
    } else {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
    }
  };
  
  // Compare language distributions
  const compareLanguages = () => {
    if (analyses.length !== 2) return [];
    
    const languages = new Set();
    analyses.forEach(analysis => {
      if (analysis.code?.language_distribution) {
        Object.keys(analysis.code.language_distribution).forEach(lang => {
          languages.add(lang);
        });
      }
    });
    
    return Array.from(languages).map(language => {
      const counts = analyses.map(analysis => 
        analysis.code?.language_distribution?.[language] || 0
      );
      
      const percentages = analyses.map(analysis => {
        if (!analysis.code?.language_distribution?.[language] || !analysis.file_count) return 0;
        return ((analysis.code.language_distribution[language] / analysis.file_count) * 100).toFixed(1);
      });
      
      const diff = counts[1] - counts[0];
      
      return {
        language,
        counts,
        percentages,
        diff
      };
    }).sort((a, b) => {
      // Sort by absolute difference, then by first analysis count
      const absDiffA = Math.abs(a.diff);
      const absDiffB = Math.abs(b.diff);
      if (absDiffA !== absDiffB) return absDiffB - absDiffA;
      return b.counts[0] - a.counts[0];
    });
  };
  
  if (loading) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
        <p className="text-gray-500">Loading analyses for comparison...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">Error loading analyses</p>
        <p className="text-sm text-gray-500">{error.message}</p>
        <Link to="/repositories" className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
          <FiArrowLeft className="mr-2" /> Back to Repositories
        </Link>
      </div>
    );
  }
  
  if (analyses.length !== 2) {
    return (
      <div className="p-8 text-center">
        <FiAlertCircle className="mx-auto h-12 w-12 text-yellow-400" />
        <h3 className="mt-2 text-lg font-medium text-gray-900">Invalid Comparison</h3>
        <p className="mt-1 text-sm text-gray-500">Please select exactly two analyses to compare.</p>
        <div className="mt-6">
          <Link to="/repositories" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
            <FiArrowLeft className="mr-2" /> Back to Repositories
          </Link>
        </div>
      </div>
    );
  }
  
  // Get comparison data
  const languageComparison = compareLanguages();
  const ageDifference = getAgeDifference();
  
  return (
    <div>
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Analysis Comparison</h1>
          <Link to={`/repositories/${analyses[0].project_id}/analyses`} className="text-blue-600 hover:text-blue-800 flex items-center">
            <FiArrowLeft className="mr-1" /> Back to Analysis History
          </Link>
        </div>
        <p className="text-gray-600 mt-2">
          Comparing analyses from {formatDate(analyses[0].created_at)} and {formatDate(analyses[1].created_at)} 
          <span className="ml-1 text-gray-500">
            ({ageDifference} apart)
          </span>
        </p>
      </div>
      
      {/* Summary Section */}
      <div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
        <div 
          className="p-4 border-b bg-gray-50 flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('summary')}
        >
          <h2 className="text-lg font-medium">Summary Comparison</h2>
          {expandedSections.summary ? <FiChevronUp /> : <FiChevronDown />}
        </div>
        
        {expandedSections.summary && (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FiFileText className="text-blue-500 mr-2" />
                    <span className="text-sm font-medium">Files Analyzed</span>
                  </div>
                </div>
                <div className="flex items-center mt-2 justify-between">
                  <p className="text-xl font-bold">{analyses[0].file_count || 0}</p>
                  <div className="flex items-center">
                    <FiArrowRight className="text-gray-400 mx-2" />
                    <p className="text-xl font-bold">{analyses[1].file_count || 0}</p>
                  </div>
                </div>
                {analyses[0].file_count !== analyses[1].file_count && (
                  <p className={`text-sm mt-1 ${analyses[1].file_count > analyses[0].file_count ? 'text-green-600' : 'text-red-600'}`}>
                    {analyses[1].file_count > analyses[0].file_count ? '+' : ''}{analyses[1].file_count - analyses[0].file_count} files
                  </p>
                )}
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FiCode className="text-yellow-500 mr-2" />
                    <span className="text-sm font-medium">Languages</span>
                  </div>
                </div>
                <div className="flex items-center mt-2 justify-between">
                  <p className="text-xl font-bold">
                    {analyses[0].languages?.length || 0}
                  </p>
                  <div className="flex items-center">
                    <FiArrowRight className="text-gray-400 mx-2" />
                    <p className="text-xl font-bold">
                      {analyses[1].languages?.length || 0}
                    </p>
                  </div>
                </div>
                {analyses[0].languages?.length !== analyses[1].languages?.length && (
                  <p className={`text-sm mt-1 ${analyses[1].languages?.length > analyses[0].languages?.length ? 'text-green-600' : 'text-red-600'}`}>
                    {analyses[1].languages?.length > analyses[0].languages?.length ? '+' : ''}
                    {(analyses[1].languages?.length || 0) - (analyses[0].languages?.length || 0)} languages
                  </p>
                )}
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FiPackage className="text-purple-500 mr-2" />
                    <span className="text-sm font-medium">Dependencies</span>
                  </div>
                </div>
                <div className="flex items-center mt-2 justify-between">
                  <p className="text-xl font-bold">
                    {analyses[0].dependencies?.analyzed_files?.length || 0}
                  </p>
                  <div className="flex items-center">
                    <FiArrowRight className="text-gray-400 mx-2" />
                    <p className="text-xl font-bold">
                      {analyses[1].dependencies?.analyzed_files?.length || 0}
                    </p>
                  </div>
                </div>
                {(analyses[0].dependencies?.analyzed_files?.length || 0) !== (analyses[1].dependencies?.analyzed_files?.length || 0) && (
                  <p className={`text-sm mt-1 ${
                    (analyses[1].dependencies?.analyzed_files?.length || 0) > (analyses[0].dependencies?.analyzed_files?.length || 0) 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {(analyses[1].dependencies?.analyzed_files?.length || 0) > (analyses[0].dependencies?.analyzed_files?.length || 0) ? '+' : ''}
                    {(analyses[1].dependencies?.analyzed_files?.length || 0) - (analyses[0].dependencies?.analyzed_files?.length || 0)} dependencies
                  </p>
                )}
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <FiGitBranch className="text-green-500 mr-2" />
                    <span className="text-sm font-medium">Repository</span>
                  </div>
                </div>
                <div className="mt-2">
                  <p className="text-md font-medium truncate" title={analyses[0].project_name || "Unknown"}>
                    {analyses[0].project_name || "Unknown"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Languages Section */}
      <div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
        <div 
          className="p-4 border-b bg-gray-50 flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('languages')}
        >
          <h2 className="text-lg font-medium">Language Changes</h2>
          {expandedSections.languages ? <FiChevronUp /> : <FiChevronDown />}
        </div>
        
        {expandedSections.languages && (
          <div className="p-6">
            {languageComparison.length > 0 ? (
              <div className="space-y-4">
                {languageComparison.map(item => (
                  <div key={item.language} className="border-b pb-4">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-medium">{item.language}</h3>
                      <div className={`text-sm font-medium ${
                        item.diff > 0 ? 'text-green-600' : item.diff < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {item.diff > 0 ? '+' : ''}{item.diff} files
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Before</p>
                        <p className="text-lg font-bold">{item.counts[0]} files ({item.percentages[0]}%)</p>
                        <div className="mt-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-600 rounded-full" 
                            style={{ width: `${item.percentages[0]}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-500">After</p>
                        <p className="text-lg font-bold">{item.counts[1]} files ({item.percentages[1]}%)</p>
                        <div className="mt-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-600 rounded-full" 
                            style={{ width: `${item.percentages[1]}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No language data available for comparison.</p>
            )}
          </div>
        )}
      </div>
      
      {/* Code Quality Section */}
      <div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
        <div 
          className="p-4 border-b bg-gray-50 flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('code')}
        >
          <h2 className="text-lg font-medium">Code Quality Changes</h2>
          {expandedSections.code ? <FiChevronUp /> : <FiChevronDown />}
        </div>
        
        {expandedSections.code && (
          <div className="p-6">
            {analyses.some(a => a.code?.file_summaries) ? (
              <div>
                <h3 className="font-medium mb-4">Key File Changes</h3>
                <div className="space-y-4">
                  {/* Compare files present in both analyses */}
                  {Object.keys(analyses[0].code?.file_summaries || {})
                    .filter(file => analyses[1].code?.file_summaries?.[file])
                    .slice(0, 5)
                    .map(file => (
                      <div key={file} className="border p-4 rounded-lg">
                        <h4 className="font-medium mb-2 break-all">{file}</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-gray-500">Before:</p>
                            <p className="text-sm mt-1 line-clamp-3">{analyses[0].code?.file_summaries[file].substring(0, 150)}...</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-500">After:</p>
                            <p className="text-sm mt-1 line-clamp-3">{analyses[1].code?.file_summaries[file].substring(0, 150)}...</p>
                          </div>
                        </div>
                      </div>
                    ))
                  }
                  
                  {/* Files only in the newer analysis */}
                  <div className="mt-6">
                    <h4 className="font-medium mb-2">New Files</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.keys(analyses[1].code?.file_summaries || {})
                        .filter(file => !analyses[0].code?.file_summaries?.[file])
                        .slice(0, 6)
                        .map(file => (
                          <div key={file} className="p-3 bg-green-50 border border-green-200 rounded">
                            <p className="text-sm font-medium break-all">{file}</p>
                          </div>
                        ))
                      }
                    </div>
                  </div>
                  
                  {/* Files only in the older analysis */}
                  <div className="mt-6">
                    <h4 className="font-medium mb-2">Removed Files</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.keys(analyses[0].code?.file_summaries || {})
                        .filter(file => !analyses[1].code?.file_summaries?.[file])
                        .slice(0, 6)
                        .map(file => (
                          <div key={file} className="p-3 bg-red-50 border border-red-200 rounded">
                            <p className="text-sm font-medium break-all">{file}</p>
                          </div>
                        ))
                      }
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No code quality data available for comparison.</p>
            )}
          </div>
        )}
      </div>
      
      {/* Dependencies Section */}
      <div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
        <div 
          className="p-4 border-b bg-gray-50 flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('dependencies')}
        >
          <h2 className="text-lg font-medium">Dependency Changes</h2>
          {expandedSections.dependencies ? <FiChevronUp /> : <FiChevronDown />}
        </div>
        
        {expandedSections.dependencies && (
          <div className="p-6">
            {analyses.some(a => a.dependencies?.dependency_graph) ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium mb-2">Before</h3>
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                      {analyses[0].dependencies?.dependency_graph || 'No dependency graph available'}
                    </pre>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-2">After</h3>
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                      {analyses[1].dependencies?.dependency_graph || 'No dependency graph available'}
                    </pre>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="font-medium mb-2">Dependency Files</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Before ({analyses[0].dependencies?.analyzed_files?.length || 0} files)</h4>
                      <ul className="text-sm space-y-1 bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                        {analyses[0].dependencies?.analyzed_files?.map((file, index) => (
                          <li key={index} className="truncate" title={file}>{file}</li>
                        )) || <li className="text-gray-500">No analyzed files</li>}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">After ({analyses[1].dependencies?.analyzed_files?.length || 0} files)</h4>
                      <ul className="text-sm space-y-1 bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                        {analyses[1].dependencies?.analyzed_files?.map((file, index) => (
                          <li key={index} className="truncate" title={file}>{file}</li>
                        )) || <li className="text-gray-500">No analyzed files</li>}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No dependency data available for comparison.</p>
            )}
          </div>
        )}
      </div>
      
      {/* Architecture Section */}
      <div className="bg-white rounded-lg shadow mb-6 overflow-hidden">
        <div 
          className="p-4 border-b bg-gray-50 flex justify-between items-center cursor-pointer"
          onClick={() => toggleSection('architecture')}
        >
          <h2 className="text-lg font-medium">Architecture Changes</h2>
          {expandedSections.architecture ? <FiChevronUp /> : <FiChevronDown />}
        </div>
        
        {expandedSections.architecture && (
          <div className="p-6">
            {analyses.some(a => a.architecture?.architecture_diagram) ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium mb-2">Before</h3>
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                      {analyses[0].architecture?.architecture_diagram || 'No architecture diagram available'}
                    </pre>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-2">After</h3>
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                      {analyses[1].architecture?.architecture_diagram || 'No architecture diagram available'}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No architecture data available for comparison.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );

};

export default AnalysisComparePage;
