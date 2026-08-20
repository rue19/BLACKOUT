import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
});

export interface SimulateRequest {
  targetType: 'person' | 'source' | 'document';
  targetId: string;
}

export interface SimulateResponse {
  orphanedClaims: Array<{ id: string; text_summary: string }>;
  unverifiableDecisions: Array<{ id: string; title: string }>;
  atRiskSystems: Array<{ id: string; name: string }>;
  resilienceScoreBefore: number;
  resilienceScoreAfter: number;
}

export interface RecoveryAction {
  action: string;
  description: string;
  claimsRestored: number;
  claimsCovered: string[];
}

export interface RecoverResponse {
  plan: RecoveryAction[];
}

export interface GraphData {
  nodes: Array<{ id: string; label: string; properties: Record<string, unknown> }>;
  edges: Array<{ source: string; target: string; type: string }>;
}

export interface ResilienceResponse {
  score: number;
  breakdown: Record<string, unknown>;
}

export const simulate = (request: SimulateRequest) =>
  api.post<SimulateResponse>('/simulate', request);

export interface RecoverRequest {
  targetType: 'person' | 'source' | 'document';
  targetId: string;
}

export const recover = (request: RecoverRequest) =>
  api.post<RecoverResponse>('/recover', request);

export const getGraph = (scope: 'full' | 'affected' = 'full') =>
  api.get<GraphData>('/graph', { params: { scope } });

export const getResilience = () =>
  api.get<ResilienceResponse>('/resilience');

export const getCrossTraining = (personId: string) =>
  api.get(`/cross-training/${personId}`);
