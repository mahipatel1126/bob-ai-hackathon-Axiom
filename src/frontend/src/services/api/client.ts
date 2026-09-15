/**
 * ChainGuard AI - API Client Abstraction Layer
 * 
 * Supports both Mock Data mode (default for development/demo)
 * and Live Backend mode (when Person 1's FastAPI/Flask server is running).
 * 
 * To connect to real backend:
 * Set VITE_USE_MOCK=false and VITE_API_BASE_URL=http://localhost:8000 in .env.local
 */

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
  fallbackMockData?: T
): Promise<T> {
  if (USE_MOCK && fallbackMockData !== undefined) {
    // Simulate realistic asynchronous network latency (80ms - 200ms)
    await new Promise((resolve) => setTimeout(resolve, 120));
    return fallbackMockData;
  }

  try {
    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error [${response.status}]: ${response.statusText}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    console.warn(`[ChainGuard API] Request to ${endpoint} failed. Falling back to mock data if available.`, error);
    if (fallbackMockData !== undefined) {
      return fallbackMockData;
    }
    throw error;
  }
}

export { USE_MOCK, API_BASE_URL };
