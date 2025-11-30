// API configuration - will be injected by FastAPI
const API_URL = window.API_URL || '/__devtrack__/stats';
const TRAFFIC_API_URL = window.TRAFFIC_API_URL || '/__devtrack__/metrics/traffic';
const ERRORS_API_URL = window.ERRORS_API_URL || '/__devtrack__/metrics/errors';
const PERF_API_URL = window.PERF_API_URL || '/__devtrack__/metrics/perf';
const CONSUMERS_API_URL = window.CONSUMERS_API_URL || '/__devtrack__/consumers';
const MAX_RECORDS_LIMIT = 100000;

async function fetchWithCacheBust(url, timestamp) {
  const response = await fetch(`${url}?hours=24&_t=${timestamp}`, {
    headers: {
      'Accept': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchStats(timestamp) {
  const url = `${API_URL}?limit=${MAX_RECORDS_LIMIT}&_t=${timestamp}`;
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchTraffic(timestamp) {
  return fetchWithCacheBust(TRAFFIC_API_URL, timestamp);
}

export async function fetchErrors(timestamp) {
  return fetchWithCacheBust(ERRORS_API_URL, timestamp);
}

export async function fetchPerf(timestamp) {
  return fetchWithCacheBust(PERF_API_URL, timestamp);
}

export async function fetchConsumers(timestamp) {
  return fetchWithCacheBust(CONSUMERS_API_URL, timestamp);
}

