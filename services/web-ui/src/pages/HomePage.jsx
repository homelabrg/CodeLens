import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Quick actions card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link 
              to="/repositories" 
              className="flex items-center justify-center p-4 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Clone Repository
            </Link>
            <Link 
              to="/projects" 
              className="flex items-center justify-center p-4 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
            >
              Upload Files
            </Link>
            <Link 
              to="/analyses" 
              className="flex items-center justify-center p-4 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition-colors"
            >
              View Analyses
            </Link>
            <Link 
              to="/settings" 
              className="flex items-center justify-center p-4 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Settings
            </Link>
          </div>
        </div>

        {/* Welcome card */}
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-lg shadow p-6">
          <h2 className="text-xl font-medium mb-3">Welcome to CodeLens</h2>
          <p className="mb-6">
            Generate comprehensive documentation for your code with AI-powered analysis.
          </p>
          <div className="mt-auto">
            <a 
              href="https://github.com/yourusername/codelens" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>

      {/* Recent activity placeholder */}
      <div className="mt-8">
        <h2 className="text-lg font-medium mb-4">Recent Activity</h2>
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
          No recent activity. Start by cloning a repository or uploading files.
        </div>
      </div>
    </div>
  );
};

export default HomePage;