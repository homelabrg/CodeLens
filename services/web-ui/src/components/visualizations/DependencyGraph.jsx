import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

const DependencyGraph = ({ dependencyData }) => {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Get container dimensions on mount and window resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height: Math.max(500, height) });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  // Process dependency data
  useEffect(() => {
    if (!dependencyData || !svgRef.current || dimensions.width === 0) return;

    // Parse the dependency diagram if it's in mermaid format
    // For this example, we'll simulate parsing mermaid and create a nodes/links structure
    const parsedData = parseDependencyData(dependencyData);
    
    if (!parsedData) return;

    renderGraph(parsedData);
  }, [dependencyData, dimensions]);

  // Parse dependency data from various formats
  const parseDependencyData = (data) => {
    // If data is already in the correct format, return it
    if (data.nodes && data.links) {
      return data;
    }
    
    // For this example, we'll use a simple parsing approach
    // In practice, you might need a more robust parser depending on the format of your data
    
    try {
      // If the data contains a dependency_graph field with a mermaid diagram
      if (data.dependency_graph && typeof data.dependency_graph === 'string') {
        return parseMermaidDiagram(data.dependency_graph);
      }
      
      // If data is an array of dependencies
      if (data.dependencies && Array.isArray(data.dependencies)) {
        return parseDependencyArray(data.dependencies);
      }
      
      // Fallback to demo data
      return createDemoData();
    } catch (error) {
      console.error('Error parsing dependency data:', error);
      return createDemoData();
    }
  };

  // Simple mermaid graph parser (TD, LR format)
  const parseMermaidDiagram = (mermaidCode) => {
    const nodes = new Set();
    const links = [];
    
    // Extract graph definition
    const graphContent = mermaidCode.replace(/^.*graph\s+(TD|LR|RL|BT)/m, '').trim();
    
    // Match lines like "A --> B"
    const linkRegex = /([A-Za-z0-9_]+)\s*--?>?\s*([A-Za-z0-9_]+)/g;
    let match;
    
    while ((match = linkRegex.exec(graphContent)) !== null) {
      const source = match[1];
      const target = match[2];
      
      nodes.add(source);
      nodes.add(target);
      links.push({ source, target });
    }
    
    // Match node definitions like "A[Module A]"
    const nodeRegex = /([A-Za-z0-9_]+)\[([^\]]+)\]/g;
    const nodeLabels = {};
    
    while ((match = nodeRegex.exec(graphContent)) !== null) {
      const id = match[1];
      const label = match[2];
      nodeLabels[id] = label;
    }
    
    return {
      nodes: Array.from(nodes).map(id => ({ 
        id, 
        label: nodeLabels[id] || id 
      })),
      links
    };
  };
  
  // Parse array of dependency objects
  const parseDependencyArray = (dependencies) => {
    const nodes = new Set();
    const links = [];
    
    dependencies.forEach(dep => {
      const source = dep.source;
      const target = dep.target;
      
      if (source && target) {
        nodes.add(source);
        nodes.add(target);
        links.push({ source, target });
      }
    });
    
    return {
      nodes: Array.from(nodes).map(id => ({ id, label: id })),
      links
    };
  };
  
  // Create demo data for preview
  const createDemoData = () => {
    return {
      nodes: [
        { id: 'api', label: 'API Module' },
        { id: 'db', label: 'Database' },
        { id: 'auth', label: 'Authentication' },
        { id: 'ui', label: 'User Interface' },
        { id: 'utils', label: 'Utilities' },
        { id: 'models', label: 'Data Models' }
      ],
      links: [
        { source: 'api', target: 'db' },
        { source: 'api', target: 'auth' },
        { source: 'ui', target: 'api' },
        { source: 'api', target: 'models' },
        { source: 'ui', target: 'utils' },
        { source: 'models', target: 'db' },
        { source: 'auth', target: 'db' }
      ]
    };
  };

  // Render the graph with D3
  const renderGraph = (graphData) => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = dimensions.width;
    const height = dimensions.height;

    // Create force simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force('link', d3.forceLink(graphData.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(50));

    // Create the container group
    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Create the links
    const link = g.append('g')
      .selectAll('line')
      .data(graphData.links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)');

    // Define arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Module color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create the nodes
    const node = g.append('g')
      .selectAll('.node')
      .data(graphData.nodes)
      .enter().append('g')
      .attr('class', 'node')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add circles for the nodes
    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => color(d.id))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5);

    // Add labels to the nodes
    node.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '.3em')
      .attr('fill', '#fff')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .text(d => d.id);

    // Add title for hover info
    node.append('title')
      .text(d => d.label || d.id);

    // Update positions in the simulation
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6" ref={containerRef}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium">Dependency Graph</h3>
        <div className="text-sm text-gray-500">
          <span className="mr-4">Scroll to zoom</span>
          <span>Drag to move nodes</span>
        </div>
      </div>
      
      <svg 
        ref={svgRef} 
        width={dimensions.width} 
        height={dimensions.height}
        className="border rounded bg-gray-50"
      />
      
      <div className="mt-4 text-sm text-gray-600">
        <p>This graph shows the dependencies between components in the codebase. 
        Each node represents a module, and arrows indicate dependencies.</p>
      </div>
    </div>
  );
};

export default DependencyGraph;