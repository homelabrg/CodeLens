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
