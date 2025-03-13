// Update the MermaidDiagram component
import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { FiCode, FiImage } from 'react-icons/fi';

mermaid.initialize({
  startOnLoad: true,
  theme: 'neutral',
  securityLevel: 'loose',
  fontFamily: 'sans-serif',
  logLevel: 'error',
});

const MermaidDiagram = ({ diagram }) => {
  const mermaidRef = useRef(null);
  const [showCode, setShowCode] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (mermaidRef.current && diagram && !showCode) {
      try {
        // Clear previous content and error
        mermaidRef.current.innerHTML = '';
        setError(null);
        
        // Create a unique ID for this diagram
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        
        // Render the diagram directly (it looks valid)
        mermaid.render(id, diagram).then((result) => {
          mermaidRef.current.innerHTML = result.svg;
        }).catch(err => {
          console.error('Error rendering mermaid diagram:', err);
          setError(err.message || 'Failed to render diagram');
        });
      } catch (err) {
        console.error('Exception while setting up mermaid:', err);
        setError(err.message || 'Failed to setup diagram');
      }
    }
  }, [diagram, showCode]);
  
  return (
    <div className="border rounded bg-white">
      <div className="flex justify-end p-2 border-b bg-gray-50">
        <div className="flex space-x-2">
          <button 
            onClick={() => setShowCode(false)} 
            className={`px-2 py-1 rounded text-sm flex items-center ${!showCode ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            <FiImage className="mr-1" /> Diagram
          </button>
          <button 
            onClick={() => setShowCode(true)} 
            className={`px-2 py-1 rounded text-sm flex items-center ${showCode ? 'bg-blue-100 text-blue-800' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            <FiCode className="mr-1" /> Code
          </button>
        </div>
      </div>
      
      {showCode ? (
        <pre className="p-4 text-sm bg-gray-50 overflow-auto">{diagram}</pre>
      ) : (
        <div className="p-4">
          {error ? (
            <div>
              <p className="text-red-500 mb-2">Error rendering diagram: {error}</p>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-700">The diagram syntax contains errors and cannot be rendered.</p>
                <p className="text-sm text-yellow-700 mt-1">You can view the code by clicking the "Code" button.</p>
              </div>
            </div>
          ) : (
            <div ref={mermaidRef} className="overflow-auto">
              {/* Diagram will be rendered here */}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MermaidDiagram;