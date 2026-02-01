/**
 * AAP Client - TypeScript Definitions v2.5.0
 */

import { Identity, PublicIdentity } from 'aap-agent-core';

// ============== Types ==============

export interface Challenge {
  id: number;
  type: string;
  challenge_string: string;
}

export interface BatchChallenge {
  nonce: string;
  challenges: Challenge[];
  batchSize: number;
  timestamp: number;
  expiresAt: number;
  maxResponseTimeMs: number;
}

export interface Proof {
  solution: string;
  signature: string;
  publicKey: string;
  publicId: string;
  nonce: string;
  timestamp: number;
  responseTimeMs: number;
  protocol: 'AAP';
  version: '2.5.0';
}

export interface BatchProof {
  solutions: string[];
  signature: string;
  publicKey: string;
  publicId: string;
  nonce: string;
  timestamp: number;
  responseTimeMs: number;
  protocol: 'AAP';
  version: '2.5.0';
}

export type LLMCallback = (challengeString: string, nonce?: string, type?: string) => Promise<string>;
export type BatchLLMCallback = (prompt: string) => Promise<string>;

// ============== Prover ==============

export interface ProverOptions {
  identity?: Identity;
  storagePath?: string;
}

export class Prover {
  constructor(options?: ProverOptions);
  getIdentity(): PublicIdentity;
  generateProof(challenge: { challenge_string: string; nonce: string; type?: string }, solutionOrCallback?: string | LLMCallback): Promise<Proof>;
  generateBatchProof(challengeBatch: BatchChallenge, llmCallback?: BatchLLMCallback): Promise<BatchProof>;
  solve(challengeString: string, nonce: string, type: string): string;
  sign(data: string): { data: string; signature: string; publicId: string; timestamp: number };
}

// ============== Client ==============

export interface AAPClientOptions {
  serverUrl?: string;
  storagePath?: string;
  llmCallback?: LLMCallback | BatchLLMCallback;
}

export interface VerificationResult {
  verified: boolean;
  role?: 'AI_AGENT';
  publicId?: string;
  batchResult?: {
    passed: number;
    total: number;
    allPassed: boolean;
    results: { id: number; valid: boolean }[];
  };
  responseTimeMs?: number;
  checks?: Record<string, boolean>;
  timing?: { client: number; server: number };
  error?: string;
  challenge?: BatchChallenge;
  proof?: {
    solution?: string;
    solutions?: string[];
    responseTimeMs: number;
    publicId: string;
  };
}

export interface HealthCheckResult {
  healthy: boolean;
  status?: string;
  protocol?: 'AAP';
  version?: string;
  mode?: 'batch';
  batchSize?: number;
  maxResponseTimeMs?: number;
  challengeTypes?: string[];
  error?: string;
}

export class AAPClient {
  constructor(options?: AAPClientOptions);
  getIdentity(): PublicIdentity;
  verify(serverUrl?: string, solutionOrCallback?: string | LLMCallback | BatchLLMCallback): Promise<VerificationResult>;
  checkHealth(serverUrl?: string): Promise<HealthCheckResult>;
  getChallenge(serverUrl?: string): Promise<BatchChallenge>;
  submitProof(serverUrl: string, proof: Proof | BatchProof): Promise<VerificationResult>;
  sign(data: string): { data: string; signature: string; publicId: string; timestamp: number };
}

export function createClient(options?: AAPClientOptions): AAPClient;

export { Prover };
export default AAPClient;
