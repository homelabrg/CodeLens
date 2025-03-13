import React, { useState } from 'react';
import { useRepositories } from '../hooks/useRepositories';
import { Link } from 'react-router-dom';
import { FiGithub, FiPlus, FiTrash2, FiExternalLink } from 'react-icons/fi';

const RepositoriesPage = () => {
  const { repositories, loading, error, cloneRepository, deleteRepository } = useRepositories();
  const [newRepoUrl, setNewRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [isCloning, setIsCloning] = useState(false);
  const [cloneError, setCloneError] = useState(null);

  const handleCloneRepository = async (e) => {
    e.preventDefault();
    setIsCloning(true);
    setCloneError(null);
    
    try {
      await cloneRepository(newRepoUrl, branch);
      setNewRepoUrl('');
      setBranch('main');
    } catch (err) {
      setCloneError(err.message || 'Failed to clone repository');
    } finally {
      setIsCloning(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">GitHub Repositories</h1>
      
      {/* Clone Repository Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">Clone Repository</h2>
        <form onSubmit={handleCloneRepository} className="space-y-4">
          <div>
            <label htmlFor="repository-url" className="block text-sm font-medium text-gray-700 mb-1">
              GitHub Repository URL
            </label>
            <input
              id="repository-url"
              type="text"
              value={newRepoUrl}
              onChange={(e) => setNewRepoUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="w-full p-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          
          <div>
            <label htmlFor="branch" className="block text-sm font-medium text-gray-700 mb-1">
              Branch
            </label>
            <input
              id="branch"
              type="text"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              className="w-full p-2 border border-gray-300 rounded-md"
            />
          </div>
          
          {cloneError && (
            <div className="text-red-600 text-sm p-2 bg-red-50 rounded-md">
              {cloneError}
            </div>
          )}
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isCloning}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center"
            >
              {isCloning ? (
                <>
                  <span className="mr-2">Cloning...</span>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                </>
              ) : (
                <>
                  <FiPlus className="mr-2" /> Clone Repository
                </>
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Repository List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-medium">Your Repositories</h2>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mb-2"></div>
            <p className="text-gray-500">Loading repositories...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <p className="text-red-500">Error loading repositories</p>
            <p className="text-sm text-gray-500">{error.message}</p>
          </div>
        ) : repositories.length === 0 ? (
          <div className="p-8 text-center">
            <FiGithub className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-500">No repositories cloned yet</p>
            <p className="text-sm text-gray-400">Use the form above to clone a repository</p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {repositories.map((repo) => (
              <li key={repo.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">{repo.owner}/{repo.repo}</h3>
                    <p className="text-sm text-gray-500">Branch: {repo.branch}</p>
                    <div className="flex items-center mt-1">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        repo.status === 'ready' 
                          ? 'bg-green-100 text-green-800' 
                          : repo.status === 'failed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {repo.status}
                      </span>
                      {repo.languages && (
                        <span className="ml-2 text-xs text-gray-500">
                          {repo.languages.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    {repo.status === 'ready' && (
                      
                      <>
                        <Link
                          to={`/analysis/new?repositoryId=${repo.id}`}
                          className="p-2 text-blue-600 hover:text-blue-800"
                          title="Analyze Repository"
                        >
                          Analyze
                        </Link>
                        <Link
                          to={`/repositories/${repo.id}/analyses`}
                          className="p-2 text-blue-600 hover:text-blue-800"
                          title="View Analysis History"
                        >
                          History
                        </Link>
                      </>
                    )}
                    <a
                      href={repo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 text-gray-500 hover:text-gray-700"
                      title="Open in GitHub"
                    >
                      <FiExternalLink />
                    </a>
                    <button
                      onClick={() => deleteRepository(repo.id)}
                      className="p-2 text-red-600 hover:text-red-800"
                      title="Delete Repository"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default RepositoriesPage;