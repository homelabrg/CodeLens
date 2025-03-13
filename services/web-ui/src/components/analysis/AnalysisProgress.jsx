import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const statusMap = {
  pending: { color: '#F59E0B', label: 'Pending' },
  running: { color: '#3B82F6', label: 'Running' },
  analyzing_code: { color: '#3B82F6', label: 'Analyzing Code' },
  analyzing_dependencies: { color: '#3B82F6', label: 'Analyzing Dependencies' },
  analyzing_business: { color: '#3B82F6', label: 'Analyzing Business Logic' },
  analyzing_architecture: { color: '#3B82F6', label: 'Analyzing Architecture' },
  completed: { color: '#10B981', label: 'Completed' },
  failed: { color: '#EF4444', label: 'Failed' }
};

const AnalysisProgress = ({ analysisId, onComplete }) => {
  const [analysisStatus, setAnalysisStatus] = useState({
    status: 'pending',
    progress: 0,
    error: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Don't poll if analysis is completed or failed
    if (analysisStatus.status === 'completed' || analysisStatus.status === 'failed') {
      if (onComplete) {
        onComplete(analysisStatus);
      }
      return;
    }

    const fetchStatus = async () => {
      try {
        const response = await axios.get(`/api/v1/source-code/analysis/analysis/${analysisId}`);
        setAnalysisStatus({
          status: response.data.status,
          progress: response.data.progress,
          error: response.data.error
        });
        setLoading(false);
      } catch (error) {
        console.error('Error fetching analysis status:', error);
        setAnalysisStatus(prev => ({
          ...prev,
          error: 'Failed to fetch analysis status'
        }));
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchStatus();

    // Set up polling
    const interval = setInterval(fetchStatus, 5000);

    // Clean up
    return () => clearInterval(interval);
  }, [analysisId, analysisStatus.status, onComplete]);

  const getStatusInfo = (status) => {
    return statusMap[status] || { color: '#6B7280', label: 'Unknown' };
  };

  const { color, label } = getStatusInfo(analysisStatus.status);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (analysisStatus.error && analysisStatus.status === 'failed') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-red-800">Analysis Failed</h3>
        <p className="mt-2 text-sm text-red-700">{analysisStatus.error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium">Analysis Progress</h3>
        <span
          className="px-3 py-1 rounded-full text-sm font-medium"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {label}
        </span>
      </div>

      <div className="flex items-center space-x-8">
        <div className="w-24 h-24">
          <CircularProgressbar
            value={analysisStatus.progress}
            text={`${analysisStatus.progress}%`}
            styles={buildStyles({
              pathColor: color,
              textColor: color,
              trailColor: '#F3F4F6'
            })}
          />
        </div>

        <div className="flex-1">
          <div className="space-y-3">
            {['code', 'dependencies', 'business', 'architecture'].map((type) => (
              <div key={type} className="flex items-center">
                <div className="w-32 text-sm font-medium">{type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div className="flex-1">
                  <div className="bg-gray-200 rounded-full h-2.5">
                    <div
                      className="h-2.5 rounded-full"
                      style={{
                        width: `${analysisStatus.status.includes(type) || analysisStatus.status === 'completed' ? 100 : 0}%`,
                        backgroundColor: color
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {analysisStatus.status === 'completed' && (
        <div className="mt-4 p-3 bg-green-50 text-green-800 rounded-md">
          <p className="text-sm">Analysis completed successfully! You can now view the results.</p>
        </div>
      )}
    </div>
  );
};

export default AnalysisProgress;