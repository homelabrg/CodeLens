// services/web-ui/src/utils/api.js
import axios from 'axios';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1/source-code',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Add request interceptor for authentication (for future use)
apiClient.interceptors.request.use(
  config => {
    // You can add auth tokens here later
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Handle API errors
    const customError = {
      statusCode: error.response?.status || 500,
      message: error.response?.data?.message || error.message || 'Unknown error',
      data: error.response?.data || {},
      originalError: error
    };
    
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('API Error:', customError);
    }
    
    return Promise.reject(customError);
  }
);

// GitHub Repository endpoints
const repositoryApi = {
  // Clone a repository
  cloneRepository: (data) => {
    return apiClient.post('/github/repositories', data);
  },
  
  // Get repository information
  getRepository: (repositoryId) => {
    return apiClient.get(`/github/repositories/${repositoryId}`);
  },
  
  // List all repositories
  listRepositories: () => {
    return apiClient.get('/github/repositories');
  },
  
  // Delete a repository
  deleteRepository: (repositoryId) => {
    return apiClient.delete(`/github/repositories/${repositoryId}`);
  }
};

// Project endpoints
const projectApi = {
  // Upload files for a new project
  uploadFiles: (formData) => {
    return apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  // Get project information
  getProject: (projectId) => {
    return apiClient.get(`/files/projects/${projectId}`);
  },
  
  // List all projects
  listProjects: () => {
    return apiClient.get('/files/projects');
  },
  
  // List files in a project
  listProjectFiles: (projectId) => {
    return apiClient.get(`/files/projects/${projectId}/files`);
  },
  
  // Get file content
  getFileContent: (projectId, filePath) => {
    return apiClient.get(`/files/projects/${projectId}/files/${filePath}`);
  },
  
  // Delete a project
  deleteProject: (projectId) => {
    return apiClient.delete(`/files/projects/${projectId}`);
  }
};

// Analysis endpoints
const analysisApi = {
  // Analyze a code snippet
  analyzeCode: (data) => {
    return apiClient.post('/analysis/code', data);
  },
  
  // Start analysis for a project
  startAnalysis: (projectId, data, fromRepository = false) => {
    return apiClient.post(`/analysis/projects/${projectId}/analyze?from_repository=${fromRepository}`, data);
  },
  
  // Get analysis status
  getAnalysisStatus: (analysisId) => {
    return apiClient.get(`/analysis/analysis/${analysisId}`);
  },
  
  // Get analysis results
  getAnalysisResults: (analysisId) => {
    return apiClient.get(`/analysis/analysis/${analysisId}/results`);
  },
  
  // Get analysis summary
  getAnalysisSummary: (analysisId) => {
    return apiClient.get(`/analysis/analysis/${analysisId}/summary`);
  },
  
  // List all analyses for a project
  listProjectAnalyses: (projectId) => {
    return apiClient.get(`/analysis/projects/${projectId}/analysis`);
  },
  
  // Get latest analysis for a project
  getLatestAnalysis: (projectId, analysisType = null) => {
    let url = `/analysis/projects/${projectId}/analysis/latest`;
    if (analysisType) {
      url += `?analysis_type=${analysisType}`;
    }
    return apiClient.get(url);
  },
  
  // Get analysis results for a project
  getProjectAnalysisResults: (projectId, analysisId = null, analysisType = null) => {
    let url = `/analysis/projects/${projectId}/analysis/results`;
    const params = [];
    
    if (analysisId) {
      params.push(`analysis_id=${analysisId}`);
    }
    
    if (analysisType) {
      params.push(`analysis_type=${analysisType}`);
    }
    
    if (params.length > 0) {
      url += `?${params.join('&')}`;
    }
    
    return apiClient.get(url);
  }
};

// Health check endpoint
const healthApi = {
  checkHealth: () => {
    return apiClient.get('/health');
  }
};

// Export all API services
const apiService = {
  repository: repositoryApi,
  project: projectApi,
  analysis: analysisApi,
  health: healthApi
};

export default apiService;