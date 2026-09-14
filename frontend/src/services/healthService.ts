import { request } from './apiClient';
import { HealthStatus } from '../types';

export async function fetchHealthStatus(): Promise<HealthStatus> {
  return request<HealthStatus>('/health');
}
