// services/api-gateway/src/config.ts
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, '../.env') });

export interface Config {
  nodeEnv: string;
  port: number;
  corsOrigins: string[];
  sourceCodeServiceUrl: string;
  documentationServiceUrl: string;
  logLevel: string;
}

export function loadConfig(): Config {
  return {
    nodeEnv: process.env.NODE_ENV || 'development',
    port: parseInt(process.env.PORT || '8080', 10),
    corsOrigins: process.env.CORS_ORIGINS 
      ? process.env.CORS_ORIGINS.split(',') 
      : ['*'],
    sourceCodeServiceUrl: process.env.SOURCE_CODE_SERVICE_URL || 'http://source-code-service:8000',
    documentationServiceUrl: process.env.DOCUMENTATION_SERVICE_URL || 'http://documentation-service:8000',
    logLevel: process.env.LOG_LEVEL || 'info',
  };
}

// Export singleton instance
export const config = loadConfig();