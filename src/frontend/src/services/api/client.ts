/**
 * ChainGuard AI - API Client Abstraction Layer
 * 
 * Supports both Mock Data mode (default for development/demo)
 * and Live Backend mode (when Person 1's FastAPI/Flask server is running).
 * 
 * To connect to real backend:
 * Set VITE_USE_MOCK=false and VITE_API_BASE_URL=http://localhost:8000 in .env.local
 */

const FORCE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
  fallbackMockData?: T
): Promise<T> {
  if (FORCE_MOCK && fallbackMockData !== undefined) {
    await new Promise((resolve) => setTimeout(resolve, 80));
    return fallbackMockData;
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const url = `${API_BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API Error [${response.status}]: ${response.statusText}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (fallbackMockData !== undefined) {
      return fallbackMockData;
    }
    throw error;
  }
}

export { FORCE_MOCK as USE_MOCK, API_BASE_URL };

