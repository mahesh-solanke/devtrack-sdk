import React from 'react';

function KPICards({ stats }) {
  const formatNumber = (n) => {
    if (n === null || n === undefined || isNaN(n)) return '–';
    return Number(n).toLocaleString();
  };

  const formatMs = (n) => {
    if (n === null || n === undefined || isNaN(n)) return '–';
    return `${Number(n).toFixed(2)} ms`;
  };

  const formatPercent = (n) => {
    if (n === null || n === undefined || isNaN(n)) return '–';
    return `${Number(n).toFixed(2)}%`;
  };

  const summary = stats?.summary || {};
  const totalRequests = summary.total_requests ?? stats?.total;
  const uniqueEndpoints = summary.unique_endpoints;
  const avgDuration = summary.avg_duration_ms;
  const successCount = summary.success_count;
  const errorCount = summary.error_count;

  let errorRate = null;
  if (typeof totalRequests === 'number' && totalRequests > 0 && typeof errorCount === 'number') {
    errorRate = (errorCount / totalRequests) * 100;
  }

  const kpis = [
    {
      label: 'Total Requests',
      value: formatNumber(totalRequests),
      sub: `Success: ${formatNumber(successCount)}, Error: ${formatNumber(errorCount)}`,
    },
    {
      label: 'Unique Endpoints',
      value: formatNumber(uniqueEndpoints),
      sub: 'Observed in this sample',
    },
    {
      label: 'Average Latency',
      value: formatMs(avgDuration),
      sub: 'From DevTrack summary',
      accent: true,
    },
    {
      label: 'Error Rate',
      value: formatPercent(errorRate),
      sub: 'error_count / total_requests',
      danger: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 mb-3">
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          className="rounded-xl p-3 bg-gradient-to-br from-cyan-500/10 to-transparent border border-gray-800 flex flex-col gap-1 min-h-[68px]"
        >
          <div className="text-xs text-gray-400">{kpi.label}</div>
          <div
            className={`text-lg font-medium font-mono ${
              kpi.accent ? 'text-indigo-400' : kpi.danger ? 'text-red-400' : 'text-gray-200'
            }`}
          >
            {kpi.value}
          </div>
          <div className="text-xs text-gray-400">{kpi.sub}</div>
        </div>
      ))}
    </div>
  );
}

export default KPICards;

