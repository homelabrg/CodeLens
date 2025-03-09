import { Router } from 'express';
import proxy from 'express-http-proxy';
import { config } from '../config';

export const sourceCodeRouter = Router();

// Proxy requests to the source-code-service
sourceCodeRouter.all('/*', proxy(config.sourceCodeServiceUrl, {
  proxyReqPathResolver: (req) => {
    return req.url.replace(/^\/api\/v1\/source-code/, '');
  }
}));
