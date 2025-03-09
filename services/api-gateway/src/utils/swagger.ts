// services/api-gateway/src/utils/serviceProxy.ts
import { Request, Response, NextFunction } from 'express';
import proxy from 'express-http-proxy';
import { URL } from 'url';

interface ProxyOptions {
  serviceUrl: string;
  pathRewrite?: Record<string, string>;
}

export function proxyRequest(req: Request, res: Response, next: NextFunction, options: ProxyOptions) {
  const { serviceUrl, pathRewrite } = options;
  
  // Apply path rewrite if specified
  let proxyReqPathResolver;
  if (pathRewrite) {
    proxyReqPathResolver = (req: Request) => {
      let path = req.url;
      Object.keys(pathRewrite).forEach((key) => {
        path = path.replace(new RegExp(key), pathRewrite[key]);
      });
      return path;
    };
  }
  
  // Create proxy middleware
  const proxyMiddleware = proxy(serviceUrl, {
    proxyReqPathResolver,
    proxyErrorHandler: (err, res, next) => {
      console.error(`Proxy error: ${err.message}`);
      if (res.headersSent) {
        return next(err);
      }
      
      // Standard error response
      res.status(500).json({
        error: 'Service unavailable',
        message: 'The requested service is currently unavailable.',
      });
    },
  });
  
  // Apply proxy middleware
  return proxyMiddleware(req, res, next);
}

// services/api-gateway/src/utils/swagger.ts
import { Express } from 'express';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

export function configureSwagger(app: Express) {
  const options = {
    definition: {
      openapi: '3.0.0',
      info: {
        title: 'CodeLens API',
        version: '1.0.0',
        description: 'API documentation for CodeLens',
      },
      servers: [
        {
          url: '/api/v1',
          description: 'API v1',
        },
      ],
    },
    apis: ['./src/routes/*.ts'],
  };
  
  const specs = swaggerJsdoc(options);
  
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));
}