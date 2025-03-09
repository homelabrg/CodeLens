// services/api-gateway/src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { StatusCodes } from 'http-status-codes';

export interface AppError extends Error {
  statusCode?: number;
  code?: string;
}

export function errorHandler(
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
) {
  const statusCode = err.statusCode || StatusCodes.INTERNAL_SERVER_ERROR;
  const message = err.message || 'Something went wrong';
  const code = err.code || 'INTERNAL_ERROR';
  
  console.error(`Error: ${message}`, {
    code,
    statusCode,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });
  
  res.status(statusCode).json({
    error: {
      code,
      message,
    },
  });
}

// services/api-gateway/src/middleware/routeNotFound.ts
import { Request, Response } from 'express';
import { StatusCodes } from 'http-status-codes';

export function routeNotFound(req: Request, res: Response) {
  res.status(StatusCodes.NOT_FOUND).json({
    error: {
      code: 'ROUTE_NOT_FOUND',
      message: `Route not found: ${req.method} ${req.path}`,
    },
  });
}

// services/api-gateway/src/middleware/requestLogger.ts
import { Request, Response, NextFunction } from 'express';
import morgan from 'morgan';

// Create custom format
const morganFormat = ':method :url :status - :response-time ms';

// Create middleware
export const requestLogger = morgan(morganFormat, {
  stream: {
    write: (message: string) => {
      console.log(message.trim());
    },
  },
});