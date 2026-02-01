/**
 * Custom error types for Molt Trader SDK
 */

export class MoltTraderError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'MoltTraderError';
  }
}

export class AuthenticationError extends MoltTraderError {
  constructor(message: string = 'Invalid or missing API key') {
    super(message, 'AUTHENTICATION_ERROR', 401);
    this.name = 'AuthenticationError';
  }
}

export class InsufficientFundsError extends MoltTraderError {
  constructor(message: string = 'Insufficient buying power') {
    super(message, 'INSUFFICIENT_FUNDS', 400);
    this.name = 'InsufficientFundsError';
  }
}

export class PositionNotFoundError extends MoltTraderError {
  constructor(positionId: string) {
    super(`Position ${positionId} not found`, 'POSITION_NOT_FOUND', 404);
    this.name = 'PositionNotFoundError';
  }
}

export class InvalidSymbolError extends MoltTraderError {
  constructor(symbol: string) {
    super(`Invalid symbol: ${symbol}`, 'INVALID_SYMBOL', 400);
    this.name = 'InvalidSymbolError';
  }
}

export class NetworkError extends MoltTraderError {
  constructor(message: string = 'Network request failed') {
    super(message, 'NETWORK_ERROR', 0);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends MoltTraderError {
  constructor(
    public field: string,
    public reason: string
  ) {
    super(`Validation failed on ${field}: ${reason}`, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}
