import { Router } from 'express';
import { sourceCodeRouter } from './sourceCode';
import { healthCheckRouter } from './healthCheck';

export const apiRouter = Router();

// API version
apiRouter.use('/v1/source-code', sourceCodeRouter);

// Version route for API information
apiRouter.get('/', (req, res) => {
  res.json({
    name: 'CodeLens API',
    version: '1.0.0',
    description: 'API Gateway for CodeLens Documentation Generator'
  });
});
