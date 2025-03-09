import { Router } from 'express';

export const healthCheckRouter = Router();

healthCheckRouter.get('/', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'api-gateway'
  });
});

healthCheckRouter.get('/readiness', (req, res) => {
  // Eventually check connections to other services
  res.status(200).json({
    status: 'ready',
    timestamp: new Date().toISOString()
  });
});

healthCheckRouter.get('/liveness', (req, res) => {
  res.status(200).json({
    status: 'alive',
    timestamp: new Date().toISOString()
  });
});
