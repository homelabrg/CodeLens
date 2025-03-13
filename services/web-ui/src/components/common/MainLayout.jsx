// services/web-ui/src/components/common/MainLayout.jsx
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  FiHome, 
  FiFolder, 
  FiGithub, 
  FiBarChart2, 
  FiSettings,
  FiMenu,
  FiX
} from 'react-icons/fi';

const MainLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  
  // Navigation items
  const navItems = [
    { path: '/', icon: <FiHome size={20} />, label: 'Dashboard' },
    { path: '/projects', icon: <FiFolder size={20} />, label: 'Projects' },
    { path: '/repositories', icon: <FiGithub size={20} />, label: 'Repositories' },
    { path: '/analysis', icon: <FiBarChart2 size={20} />, label: 'Analysis' },
    { path: '/settings', icon: <FiSettings size={20} />, label: 'Settings' }
  ];
  
  // Toggle sidebar for mobile view
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  // Close sidebar on navigation (mobile)
  const closeSidebarOnMobile = () => {
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-20 bg-black bg-opacity-50 md:hidden"
          onClick={toggleSidebar}
        />
      )}
      
      {/* Sidebar */}
      <div 
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0 md:static md:z-auto
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <Link to="/" className="flex items-center" onClick={closeSidebarOnMobile}>
            <span className="text-xl font-bold text-blue-600">CodeLens</span>
          </Link>
          <button 
            className="md:hidden text-gray-500 hover:text-gray-700"
            onClick={toggleSidebar}
          >
            <FiX size={24} />
          </button>
        </div>
        
        {/* Navigation */}
        <nav className="px-4 py-6">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`
                    flex items-center px-4 py-3 rounded-lg transition-colors
                    ${location.pathname === item.path 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'}
                  `}
                  onClick={closeSidebarOnMobile}
                >
                  {item.icon}
                  <span className="ml-3">{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        
        {/* Footer */}
        <div className="absolute bottom-0 w-full p-4 border-t">
          <div className="text-xs text-gray-500">
            <div>CodeLens v0.1.0</div>
            <div className="mt-1">AI-Powered Documentation</div>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between h-16 px-6 bg-white border-b">
          <button 
            className="text-gray-500 md:hidden"
            onClick={toggleSidebar}
          >
            <FiMenu size={24} />
          </button>
          
          <div className="flex items-center ml-auto">
            {/* Additional header content like profile, notifications, etc. can go here */}
            <a 
              href="https://github.com/yourusername/codelens" 
              target="_blank" 
              rel="noopener noreferrer"
              className="px-4 py-2 text-sm text-gray-700 hover:text-blue-600"
            >
              GitHub
            </a>
          </div>
        </header>
        
        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;