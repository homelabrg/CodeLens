import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

// Color palette for different programming languages
const LANGUAGE_COLORS = {
  JavaScript: '#f7df1e',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  Java: '#b07219',
  'C#': '#178600',
  'C++': '#f34b7d',
  C: '#555555',
  Go: '#00ADD8',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Swift: '#ffac45',
  Kotlin: '#A97BFF',
  Rust: '#dea584',
  Scala: '#c22d40',
  HTML: '#e34c26',
  CSS: '#563d7c',
  Shell: '#89e051',
  // Add more languages as needed
  Other: '#cccccc' // Default for other languages
};

// Get color for a language
const getLanguageColor = (language) => {
  return LANGUAGE_COLORS[language] || LANGUAGE_COLORS.Other;
};

const LanguageDistributionChart = ({ languageDistribution }) => {
  // If no data is provided, show a placeholder
  if (!languageDistribution || Object.keys(languageDistribution).length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-80 flex items-center justify-center">
        <p className="text-gray-500">No language data available</p>
      </div>
    );
  }

  // Format data for the pie chart
  const chartData = Object.entries(languageDistribution).map(([language, count]) => ({
    name: language,
    value: count,
    color: getLanguageColor(language)
  }));

  // Sort data by value (descending)
  chartData.sort((a, b) => b.value - a.value);

  // Calculate total files
  const totalFiles = chartData.reduce((acc, item) => acc + item.value, 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = ((data.value / totalFiles) * 100).toFixed(1);
      
      return (
        <div className="bg-white p-3 border rounded shadow">
          <p className="font-medium">{data.name}</p>
          <p className="text-sm">{data.value} files ({percentage}%)</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium mb-4">Programming Languages</h3>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              innerRadius={40}
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend layout="vertical" align="right" verticalAlign="middle" />
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 border-t pt-4">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p className="text-gray-600">Total Files</p>
            <p className="font-medium">{totalFiles}</p>
          </div>
          <div>
            <p className="text-gray-600">Languages</p>
            <p className="font-medium">{chartData.length}</p>
          </div>
          <div>
            <p className="text-gray-600">Primary Language</p>
            <p className="font-medium">{chartData[0]?.name || 'None'}</p>
          </div>
          <div>
            <p className="text-gray-600">Primary Language %</p>
            <p className="font-medium">
              {chartData[0] ? ((chartData[0].value / totalFiles) * 100).toFixed(1) + '%' : '0%'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LanguageDistributionChart;