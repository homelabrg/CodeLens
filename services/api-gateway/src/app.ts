// services/api-gateway/src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { json, urlencoded } from 'body-parser';
import { errorHandler } from './middleware/errorHandler';
import { routeNotFound } from './middleware/routeNotFound';
import { requestLogger } from './middleware/requestLogger';
import { healthCheckRouter } from './routes/healthCheck';
import { apiRouter } from './routes/api';
import { configureSwagger } from './utils/swagger';

export const createApp = () => {
  const app = express();

  // Middleware
  app.use(helmet());
  app.use(cors());
  app.use(compression());
  app.use(json({ limit: '10mb' }));
  app.use(urlencoded({ extended: true, limit: '10mb' }));
  app.use(requestLogger);

  // Routes
  app.use('/health', healthCheckRouter);
  app.use('/api', apiRouter);

  // Swagger API documentation
  configureSwagger(app);

  // Error handling
  app.use(routeNotFound);
  app.use(errorHandler);

  return app;
};