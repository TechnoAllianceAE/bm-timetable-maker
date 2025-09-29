import { Request, Response, NextFunction } from 'express';
import Joi, { Schema } from 'joi';

type RequestPart = 'body' | 'query' | 'params';

type SchemaConfig = Partial<Record<RequestPart, Schema>>;

export const validateRequest = (schemas: SchemaConfig) => {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      (Object.keys(schemas) as RequestPart[]).forEach((key) => {
        const schema = schemas[key];
        if (!schema) return;
        const { error, value } = schema.validate((req as any)[key], {
          abortEarly: false,
          stripUnknown: true
        });

        if (error) {
          throw new Error(error.details.map((detail) => detail.message).join(', '));
        }

        (req as any)[key] = value;
      });

      next();
    } catch (error: any) {
      res.status(400).json({ message: error.message || 'Invalid request payload' });
    }
  };
};
