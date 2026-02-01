/**
 * AAP Server - TypeScript Definitions v2.5.0
 */

import { Router, Request, Response, NextFunction } from 'express';

// ============== Constants ==============

export const BATCH_SIZE: 5;
export const MAX_RESPONSE_TIME_MS: 8000;
export const CHALLENGE_EXPIRY_MS: 60000;

// ============== Challenges ==============

export type ChallengeType = 
  | 'nlp_math' 
  | 'nlp_logic' 
  | 'nlp_extract' 
  | 'nlp_count'
  | 'nlp_transform' 
  | 'nlp_multistep' 
  | 'nlp_pattern' 
  | 'nlp_analysis';

export interface Challenge {
  id: number;
  type: ChallengeType;
  challenge_string: string;
}

export interface ChallengeResult {
  type: ChallengeType;
  challenge_string: string;
  validate: (solution: string) => boolean;
  expected: any;
}

export interface BatchChallengeResult {
  challenges: Challenge[];
  validators: ((solution: string) => boolean)[];
  expected: any[];
}

export interface BatchValidationResult {
  passed: number;
  total: number;
  allPassed: boolean;
  results: { id: number; valid: boolean }[];
}

export function getTypes(): ChallengeType[];
export function generate(nonce: string, type?: ChallengeType): ChallengeResult;
export function generateBatch(nonce: string, count?: number): BatchChallengeResult;
export function validateBatch(validators: ((s: string) => boolean)[], solutions: any[]): BatchValidationResult;
export function validate(type: ChallengeType, nonce: string, solution: string): boolean;

// ============== Middleware ==============

export interface VerificationResult {
  verified: boolean;
  role?: 'AI_AGENT';
  publicId?: string;
  batchResult?: BatchValidationResult;
  responseTimeMs?: number;
  checks: VerificationChecks;
  timing?: { client: number; server: number };
  error?: string;
}

export interface VerificationChecks {
  inputValid: boolean;
  challengeExists: boolean;
  notExpired: boolean;
  solutionsExist: boolean;
  solutionsValid: boolean;
  responseTimeValid: boolean;
  signatureValid: boolean;
}

export interface MiddlewareOptions {
  challengeExpiryMs?: number;
  maxResponseTimeMs?: number;
  batchSize?: number;
  minPassCount?: number;
  onVerified?: (result: VerificationResult, req: Request) => void;
  onFailed?: (error: { error: string; checks: VerificationChecks }, req: Request) => void;
}

export function aapMiddleware(options?: MiddlewareOptions): (router: Router) => Router;
export function createRouter(options?: MiddlewareOptions): Promise<Router>;

// ============== Rate Limiting ==============

export interface RateLimiterOptions {
  windowMs?: number;
  max?: number;
  message?: string;
}

export function createRateLimiter(options?: RateLimiterOptions): (req: Request, res: Response, next: NextFunction) => void;

export interface FailureLimiter {
  middleware: (req: Request, res: Response, next: NextFunction) => void;
  recordFailure: (req: Request) => void;
  clearFailures: (req: Request) => void;
}

export function createFailureLimiter(options?: RateLimiterOptions): FailureLimiter;

// ============== Errors ==============

export const ErrorCodes: {
  CHALLENGE_NOT_FOUND: 'CHALLENGE_NOT_FOUND';
  CHALLENGE_EXPIRED: 'CHALLENGE_EXPIRED';
  MISSING_SOLUTIONS: 'MISSING_SOLUTIONS';
  INVALID_SOLUTIONS_COUNT: 'INVALID_SOLUTIONS_COUNT';
  SOLUTION_VALIDATION_FAILED: 'SOLUTION_VALIDATION_FAILED';
  RESPONSE_TOO_SLOW: 'RESPONSE_TOO_SLOW';
  INVALID_SIGNATURE: 'INVALID_SIGNATURE';
  INVALID_REQUEST: 'INVALID_REQUEST';
  RATE_LIMITED: 'RATE_LIMITED';
};

export function createError(code: keyof typeof ErrorCodes, extra?: object): object;
export function sendError(code: keyof typeof ErrorCodes, res: Response, extra?: object): void;

// ============== Logger ==============

export function setLogLevel(level: 'debug' | 'info' | 'warn' | 'error'): void;
export function debug(message: string, data?: object): void;
export function info(message: string, data?: object): void;
export function warn(message: string, data?: object): void;
export function error(message: string, data?: object): void;
export function logVerification(result: VerificationResult, req?: Request): void;
export function logChallenge(nonce: string, batchSize: number): void;
