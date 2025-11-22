import React, { useState, useEffect, useCallback } from 'react';
import KPICards from './components/KPICards';
import TrafficOverview from './components/TrafficOverview';
import ErrorTrends from './components/ErrorTrends';
import PerformanceMetrics from './components/PerformanceMetrics';
import ConsumerSegmentation from './components/ConsumerSegmentation';
import RequestLogs from './components/RequestLogs';
import StatusBar from './components/StatusBar';
import { fetchStats, fetchTraffic, fetchErrors, fetchPerf, fetchConsumers } from './services/api';

function App() {
  const [stats, setStats] = useState(null);
  const [traffic, setTraffic] = useState([]);
  const [errors, setErrors] = useState(null);
  const [perf, setPerf] = useState(null);
  const [consumers, setConsumers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsOnline(true);

    try {
      const timestamp = new Date().getTime();
      const [statsData, trafficData, errorsData, perfData, consumersData] = await Promise.all([
        fetchStats(timestamp),
        fetchTraffic(timestamp),
        fetchErrors(timestamp),
        fetchPerf(timestamp),
        fetchConsumers(timestamp),
      ]);

      setStats(statsData);
      setTraffic(trafficData?.traffic || []);
      setErrors(errorsData);
      setPerf(perfData);
      setConsumers(consumersData?.segments || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError(err.message || 'Failed to fetch data');
      setIsOnline(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    if (refreshInterval <= 0) return;

    const timer = setInterval(() => {
      loadData();
    }, refreshInterval);

    return () => clearInterval(timer);
  }, [refreshInterval, loadData]);

  const handleRefresh = () => {
    loadData();
  };

  const handleRefreshIntervalChange = (e) => {
    setRefreshInterval(Number(e.target.value));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-950 to-gray-950 text-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-br from-slate-900/90 to-slate-900/95 rounded-2xl border border-gray-800 p-6 shadow-2xl backdrop-blur-xl">
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
            <div>
              <div className="text-xs uppercase tracking-wider text-gray-400 mb-1">
                DevTrack • Live Metrics
              </div>
              <div className="flex items-baseline gap-2">
                <h1 className="text-3xl font-semibold">API Health Dashboard</h1>
                <span className="text-xs px-2 py-1 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/40">
                  Auto-refresh
                </span>
              </div>
              <p className="text-sm text-gray-400 mt-1">
                Consumes DevTrack JSON stats and visualizes traffic, latency, and errors in real time.
                <br />
                Point this to your <code className="text-xs font-mono">/__devtrack__/stats</code> endpoint.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 items-center">
              <select
                value={refreshInterval}
                onChange={handleRefreshIntervalChange}
                className="px-3 py-1.5 rounded-full border border-slate-600 bg-slate-900/90 text-gray-200 text-sm outline-none focus:border-indigo-500"
              >
                <option value={5000}>5s</option>
                <option value={10000}>10s</option>
                <option value={30000}>30s</option>
                <option value={60000}>60s</option>
                <option value={0}>Pause</option>
              </select>
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="px-4 py-1.5 rounded-full bg-indigo-600 text-gray-100 text-sm font-medium hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                ⟳ Refresh now
              </button>
            </div>
          </div>

          {/* Status Bar */}
          <StatusBar
            isOnline={isOnline}
            lastUpdated={lastUpdated}
            apiUrl={window.API_URL || '/__devtrack__/stats'}
          />

          {/* Error Box */}
          {error && (
            <div className="mt-2 p-2 rounded-lg bg-red-900/20 border border-red-500/50 text-red-200 text-sm">
              {error}
            </div>
          )}

          {/* KPI Cards */}
          <KPICards stats={stats} />

          {/* Traffic Overview */}
          <TrafficOverview data={traffic} />

          {/* Error Trends */}
          <ErrorTrends data={errors} />

          {/* Performance Metrics */}
          <PerformanceMetrics data={perf} />

          {/* Consumer Segmentation */}
          <ConsumerSegmentation data={consumers} />

          {/* Request Logs */}
          <RequestLogs stats={stats} loading={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;

