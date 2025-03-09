import { Request, Response } from 'express';

export function routeNotFound(req: Request, res: Response) {
  res.status(404).json({
    error: {
      code: 'ROUTE_NOT_FOUND',
      message: `Route not found: ${req.method} ${req.path}`,
    },
  });
}
