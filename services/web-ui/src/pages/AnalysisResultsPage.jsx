// src/pages/AnalysisResultsPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiService from '../utils/api';
import { FiFileText, FiAlertCircle, FiCheck, FiPackage, FiCode, FiActivity, FiLayers, FiGitBranch, FiRefreshCw,FiList } from 'react-icons/fi';
import MermaidDiagram from '../components/MermaidDiagram';
import { Link} from 'react-router-dom';


const AnalysisResultsPage = () => {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingResults, setLoadingResults] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Function to fetch analysis status
  const fetchAnalysisStatus = async () => {
    try {
      setLoading(true);
      
      // Get analysis status
      const analysisResponse = await apiService.analysis.getAnalysisStatus(analysisId);
      setAnalysis(analysisResponse.data);
      
      // If analysis is completed, fetch results
      if (analysisResponse.data.status === 'completed' && !results) {
        fetchAnalysisResults();
      }
      
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };
  
  // Function to fetch analysis results
  const fetchAnalysisResults = async () => {
    try {
      setLoadingResults(true);
      
      // Get analysis results
      const resultsResponse = await apiService.analysis.getAnalysisResults(analysisId);
      setResults(resultsResponse.data);
      
      setError(null);
    } catch (err) {
      setError(err);
    } finally {
      setLoadingResults(false);
    }
  };
  
  // Fetch status on component mount and when analysis ID changes
  useEffect(() => {
    fetchAnalysisStatus();
    
    // Poll for updates if analysis is in progress
    let interval;
    if (analysis && ['pending', 'in_progress'].includes(analysis.status)) {
      interval = setInterval(fetchAnalysisStatus, 5000); // Poll every 5 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [analysisId, analysis?.status]);
  
  if (loading && !analysis) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
        <p className="text-gray-500">Loading analysis...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">Error loading analysis</p>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }
  
  if (!analysis) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">Analysis not found</p>
      </div>
    );
  }
  
  // Display in-progress or pending analysis
  if (['pending', 'in_progress'].includes(analysis.status)) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
        <p className="text-lg font-medium mb-2">Analysis in progress...</p>
        <p className="text-gray-500">Status: {analysis.status}</p>
        {analysis.progress > 0 && (
          <div className="w-64 mx-auto mt-4">
            <div className="bg-gray-200 rounded-full h-4 w-full">
              <div 
                className="bg-blue-600 rounded-full h-4" 
                style={{ width: `${analysis.progress}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-1">{analysis.progress}% complete</p>
          </div>
        )}
        <p className="text-gray-500 mt-4">This may take a few minutes depending on the repository size.</p>
      </div>
    );
  }
  
  // Display failed analysis
  if (analysis.status === 'failed') {
    return (
      <div className="p-8 text-center">
        <FiAlertCircle className="text-red-500 h-12 w-12 mx-auto mb-4" />
        <p className="text-lg font-medium mb-2 text-red-500">Analysis failed</p>
        <p className="text-gray-500">{analysis.message || 'An unknown error occurred'}</p>
      </div>
    );
  }
  
  // Render tabs for completed analysis
  const renderTabs = () => {
    return (
      <div className="border-b border-gray-200">
        <nav className="flex space-x-4 overflow-x-auto pb-1">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`py-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'code'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Code Analysis
          </button>
          <button
            onClick={() => setActiveTab('dependencies')}
            className={`py-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'dependencies'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Dependencies
          </button>
          <button
            onClick={() => setActiveTab('architecture')}
            className={`py-4 px-2 border-b-2 font-medium text-sm ${
              activeTab === 'architecture'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Architecture
          </button>
        </nav>
      </div>
    );
  };
  
  // Render different content based on active tab
  const renderTabContent = () => {
    // If results haven't been loaded yet, display loading or fetch button
    if (!results) {
      return (
        <div className="p-8 text-center">
          {loadingResults ? (
            <>
              <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
              <p className="text-gray-500">Loading analysis results...</p>
            </>
          ) : (
            <>
              <p className="text-gray-500 mb-4">Analysis is complete, but detailed results haven't been loaded yet.</p>
              <button
                onClick={fetchAnalysisResults}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center mx-auto"
              >
                <FiRefreshCw className="mr-2" /> Load Results
              </button>
            </>
          )}
        </div>
      );
    }
    
    // If results are loaded, display the selected tab
    switch (activeTab) {
      case 'overview':
        return renderOverviewTab();
      case 'code':
        return renderCodeTab();
      case 'dependencies':
        return renderDependenciesTab();
      case 'architecture':
        return renderArchitectureTab();
      default:
        return renderOverviewTab();
    }
  };
  
  // Overview tab content
  const renderOverviewTab = () => {
    return (
      <div className="space-y-6 py-4">
        {/* Analysis Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Analysis Summary</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center">
                <FiFileText className="text-blue-500 mr-2" />
                <span className="text-sm font-medium">Files Analyzed</span>
              </div>
              <p className="text-2xl font-bold mt-2">{results.file_count || 0}</p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center">
                <FiCode className="text-yellow-500 mr-2" />
                <span className="text-sm font-medium">Languages</span>
              </div>
              <p className="text-2xl font-bold mt-2">{results.languages ? results.languages.length : 0}</p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center">
                <FiGitBranch className="text-purple-500 mr-2" />
                <span className="text-sm font-medium">Repository</span>
              </div>
              <p className="text-2xl font-bold mt-2 truncate" title={results.project_name}>
                {results.project_name || 'Unknown'}
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center">
                <FiCheck className="text-green-500 mr-2" />
                <span className="text-sm font-medium">Status</span>
              </div>
              <p className="text-2xl font-bold mt-2">{results.status || 'Unknown'}</p>
            </div>
          </div>
        </div>
        
        {/* Language Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Language Distribution</h2>
          
          {results.code && results.code.language_distribution ? (
            <div className="space-y-2">
              {Object.entries(results.code.language_distribution).map(([language, count]) => {
                const percentage = ((count / results.file_count) * 100).toFixed(1);
                return (
                  <div key={language} className="flex items-center">
                    <span className="w-24 text-sm">{language}</span>
                    <div className="flex-grow bg-gray-200 rounded-full h-4">
                      <div 
                        className="bg-blue-600 rounded-full h-4" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm">{count} files ({percentage}%)</span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500">No language data available</p>
          )}
        </div>
        
        {/* Analysis Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Analysis Timeline</h2>
          
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="bg-blue-100 text-blue-800 p-2 rounded-full mr-3">
                <FiFileText />
              </div>
              <div>
                <p className="font-medium">Analysis Created</p>
                <p className="text-sm text-gray-500">
                  {results.created_at ? new Date(results.created_at).toLocaleString() : 'Unknown'}
                </p>
              </div>
            </div>
            
            {results.completed_at && (
              <div className="flex items-start">
                <div className="bg-green-100 text-green-800 p-2 rounded-full mr-3">
                  <FiCheck />
                </div>
                <div>
                  <p className="font-medium">Analysis Completed</p>
                  <p className="text-sm text-gray-500">
                    {new Date(results.completed_at).toLocaleString()}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  // Code quality tab content
  const renderCodeTab = () => {
    const codeData = results.code || {};
    const languageSummaries = codeData.language_summaries || {};
    const fileSummaries = codeData.file_summaries || {};
    
    return (
      <div className="space-y-6 py-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Language Insights</h2>
          
          <div className="space-y-4">
            {Object.entries(languageSummaries).map(([language, summary]) => (
              <div key={language} className="border rounded-lg p-4">
                <h3 className="font-medium text-lg mb-2">{language}</h3>
                <p className="text-sm text-gray-700 whitespace-pre-line">{summary}</p>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Key Files Analysis</h2>
          
          <div className="space-y-4">
            {Object.entries(fileSummaries).slice(0, 5).map(([filename, summary]) => (
              <div key={filename} className="border rounded-lg p-4">
                <h3 className="font-medium text-md mb-2 break-all">{filename}</h3>
                <p className="text-sm text-gray-700 whitespace-pre-line">{summary}</p>
              </div>
            ))}
            
            {Object.keys(fileSummaries).length > 5 && (
              <div className="text-center">
                <button 
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  onClick={() => alert("This would show more files")}
                >
                  Show more files ({Object.keys(fileSummaries).length - 5} more)
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  // Dependencies tab content
 // Dependencies tab content
const renderDependenciesTab = () => {
    const dependenciesData = results.dependencies || {};
    const analyzedFiles = dependenciesData.analyzed_files || [];
    
    // Function to detect and process mermaid diagrams in text
    const processMermaidDiagrams = (text) => {
      if (!text) return null;
      
      // Find mermaid diagram blocks
      // This regex matches the ```mermaid block with its content
      const mermaidRegex = /```mermaid\s*([\s\S]*?)```/g;
      let match;
      let lastIndex = 0;
      const elements = [];
      
      // Iterate through all matches
      while ((match = mermaidRegex.exec(text)) !== null) {
        const fullMatch = match[0];
        const diagramContent = match[1].trim();
        const matchIndex = match.index;
        
        // Add text before this match
        if (matchIndex > lastIndex) {
          const textBefore = text.substring(lastIndex, matchIndex);
          if (textBefore.trim()) {
            elements.push(
              <pre key={`text-${lastIndex}`} className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                {textBefore}
              </pre>
            );
          }
        }
        
        // Add the diagram
        elements.push(
          <div key={`diagram-${matchIndex}`} className="my-4">
            <div className="text-xs text-gray-500 mb-1">Mermaid Diagram:</div>
            <MermaidDiagram diagram={diagramContent} />
          </div>
        );
        
        lastIndex = matchIndex + fullMatch.length;
      }
      
      // Add any remaining text after the last match
      if (lastIndex < text.length) {
        const textAfter = text.substring(lastIndex);
        if (textAfter.trim()) {
          elements.push(
            <pre key={`text-${lastIndex}`} className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
              {textAfter}
            </pre>
          );
        }
      }
      
      // If no elements created (no diagrams found), return the original text
      if (elements.length === 0) {
        return (
          <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
            {text}
          </pre>
        );
      }
      
      return elements;
    };
    
    return (
      <div className="space-y-6 py-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Dependencies Analysis</h2>
          
          {dependenciesData.dependencies ? (
            <div className="prose max-w-none">
              {processMermaidDiagrams(dependenciesData.dependencies)}
            </div>
          ) : (
            <p className="text-gray-500">No dependency details available</p>
          )}
        </div>
        
        {dependenciesData.dependency_graph && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Dependency Graph</h2>
            
            <div className="prose max-w-none">
              {processMermaidDiagrams(dependenciesData.dependency_graph)}
            </div>
          </div>
        )}
        
        {analyzedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Analyzed Files</h2>
            
            <ul className="divide-y divide-gray-200">
              {analyzedFiles.map((file, index) => (
                <li key={index} className="py-2">
                  <span className="text-sm text-gray-700">{file}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  // Architecture tab content
  const renderArchitectureTab = () => {
    const architectureData = results.architecture || {};
    
    // Function to detect and process mermaid diagrams in text
    const processMermaidDiagrams = (text) => {
      if (!text) return null;
      
      // Find mermaid diagram blocks
      // This regex matches the ```mermaid block with its content
      const mermaidRegex = /```mermaid\s*([\s\S]*?)```/g;
      let match;
      let lastIndex = 0;
      const elements = [];
      
      console.log('Processing text for mermaid diagrams:', text);
      
      // Iterate through all matches
      while ((match = mermaidRegex.exec(text)) !== null) {
        const fullMatch = match[0];
        const diagramContent = match[1].trim();
        const matchIndex = match.index;
        
        console.log('Found mermaid diagram:', diagramContent);
        
        // Add text before this match
        if (matchIndex > lastIndex) {
          const textBefore = text.substring(lastIndex, matchIndex);
          if (textBefore.trim()) {
            elements.push(
              <pre key={`text-${lastIndex}`} className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
                {textBefore}
              </pre>
            );
          }
        }
        
        // Add the diagram
        elements.push(
          <div key={`diagram-${matchIndex}`} className="my-4">
            <div className="text-xs text-gray-500 mb-1">Mermaid Diagram:</div>
            <MermaidDiagram diagram={diagramContent} />
          </div>
        );
        
        lastIndex = matchIndex + fullMatch.length;
      }
      
      // Add any remaining text after the last match
      if (lastIndex < text.length) {
        const textAfter = text.substring(lastIndex);
        if (textAfter.trim()) {
          elements.push(
            <pre key={`text-${lastIndex}`} className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
              {textAfter}
            </pre>
          );
        }
      }
      
      // If no elements created (no diagrams found), return the original text
      if (elements.length === 0) {
        return (
          <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
            {text}
          </pre>
        );
      }
      
      return elements;
    };
    
    return (
      <div className="space-y-6 py-4">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Architecture Analysis</h2>
          
          {architectureData.architecture_analysis ? (
            <div className="prose max-w-none">
              {processMermaidDiagrams(architectureData.architecture_analysis)}
            </div>
          ) : (
            <p className="text-gray-500">No architecture analysis available</p>
          )}
        </div>
        
        {architectureData.architecture_diagram && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Architecture Diagram</h2>
            
            <div className="prose max-w-none">
              {processMermaidDiagrams(architectureData.architecture_diagram)}
            </div>
          </div>
        )}
        
        {/* Rest of the component remains the same */}
        {architectureData.analyzed_files && architectureData.analyzed_files.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium mb-4">Analyzed Files for Architecture</h2>
            
            <ul className="divide-y divide-gray-200">
              {architectureData.analyzed_files.map((file, index) => (
                <li key={index} className="py-2">
                  <span className="text-sm text-gray-700">{file}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-2xl font-bold">Analysis Results</h1>
        <div className="flex items-center">
        {analysis && (
          <Link 
            to={`/repositories/${analysis.project_id}/analyses`}
            className="mr-3 px-3 py-1 text-sm text-blue-600 hover:text-blue-800 flex items-center"
          >
            <FiList className="mr-1" /> 
            View History
          </Link>
        )}
        {analysis && analysis.status === 'completed' && (
          <button 
            onClick={fetchAnalysisResults}
            disabled={loadingResults}
            className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center text-sm"
          >
            <FiRefreshCw className={`mr-1 ${loadingResults ? 'animate-spin' : ''}`} />
            {loadingResults ? 'Loading...' : 'Refresh Results'}
          </button>
        )}
      </div>
      </div>
      <p className="text-gray-500 mb-6">
        Analysis ID: {analysisId}
        {analysis && analysis.created_at && (
          <span> • Created: {new Date(analysis.created_at).toLocaleString()}</span>
        )}
        {analysis && (
          <span> • Status: <span className="font-medium">{analysis.status}</span></span>
        )}
      </p>
      
      {renderTabs()}
      {renderTabContent()}
    </div>
  );
};

export default AnalysisResultsPage;