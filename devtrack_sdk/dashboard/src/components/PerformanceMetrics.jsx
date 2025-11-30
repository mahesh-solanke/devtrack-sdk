import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function PerformanceMetrics({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data?.latency_over_time || !data.latency_over_time.length) return;

    const labels = data.latency_over_time.map((item) => {
      const date = new Date(item.time_bucket);
      return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    });

    const p50 = data.latency_over_time.map((item) => item.p50 || 0);
    const p95 = data.latency_over_time.map((item) => item.p95 || 0);
    const p99 = data.latency_over_time.map((item) => item.p99 || 0);

    const chartData = {
      labels,
      datasets: [
        {
          label: 'p50',
          data: p50,
          borderColor: 'rgb(79, 70, 229)',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2,
        },
        {
          label: 'p95',
          data: p95,
          borderColor: 'rgb(249, 115, 115)',
          backgroundColor: 'rgba(249, 115, 115, 0.1)',
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2,
        },
        {
          label: 'p99',
          data: p99,
          borderColor: 'rgb(251, 146, 60)',
          backgroundColor: 'rgba(251, 146, 60, 0.1)',
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2,
        },
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      plugins: {
        legend: {
          labels: { color: '#e5e7eb', font: { size: 11 } },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} ms`,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: '#9ca3af',
            maxRotation: 45,
            minRotation: 0,
            autoSkip: true,
            maxTicksLimit: 12,
            font: { size: 10 },
          },
          grid: { color: 'rgba(55,65,81,0.4)' },
        },
        y: {
          beginAtZero: true,
          ticks: {
            color: '#9ca3af',
            font: { size: 10 },
            callback: (value) => `${value} ms`,
          },
          grid: { color: 'rgba(31,41,55,0.5)' },
        },
      },
    };

    if (chartRef.current) {
      chartRef.current.data = chartData;
      chartRef.current.options = options;
      chartRef.current.update('none');
    }
  }, [data]);

  const formatMs = (n) => {
    if (n === null || n === undefined || isNaN(n)) return '–';
    return `${Number(n).toFixed(2)} ms`;
  };

  const overall = data?.overall_stats || {};

  if (!data || !data.latency_over_time?.length) {
    return (
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-medium text-gray-200">Performance Metrics</h2>
          <span className="text-xs text-gray-400">p50/p95/p99 latency over time</span>
        </div>
        <div className="text-sm text-gray-400 text-center py-3">
          No performance data available.
        </div>
      </div>
    );
  }

  const labels = data.latency_over_time.map((item) => {
    const date = new Date(item.time_bucket);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  });

  const p50 = data.latency_over_time.map((item) => item.p50 || 0);
  const p95 = data.latency_over_time.map((item) => item.p95 || 0);
  const p99 = data.latency_over_time.map((item) => item.p99 || 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'p50',
        data: p50,
        borderColor: 'rgb(79, 70, 229)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 2,
      },
      {
        label: 'p95',
        data: p95,
        borderColor: 'rgb(249, 115, 115)',
        backgroundColor: 'rgba(249, 115, 115, 0.1)',
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 2,
      },
      {
        label: 'p99',
        data: p99,
        borderColor: 'rgb(251, 146, 60)',
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    plugins: {
      legend: {
        labels: { color: '#e5e7eb', font: { size: 11 } },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)} ms`,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#9ca3af',
          maxRotation: 45,
          minRotation: 0,
          autoSkip: true,
          maxTicksLimit: 12,
          font: { size: 10 },
        },
        grid: { color: 'rgba(55,65,81,0.4)' },
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#9ca3af',
          font: { size: 10 },
          callback: (value) => `${value} ms`,
        },
        grid: { color: 'rgba(31,41,55,0.5)' },
      },
    },
  };

  return (
    <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-medium text-gray-200">Performance Metrics</h2>
        <span className="text-xs text-gray-400">p50/p95/p99 latency over time</span>
      </div>
      <div className="h-[120px]">
        <Line ref={chartRef} data={chartData} options={options} />
      </div>
      <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-400">
        <span>
          Overall p50: <span className="font-mono text-indigo-400">{formatMs(overall.p50)}</span>
        </span>
        <span>
          Overall p95: <span className="font-mono text-indigo-400">{formatMs(overall.p95)}</span>
        </span>
        <span>
          Overall p99: <span className="font-mono text-indigo-400">{formatMs(overall.p99)}</span>
        </span>
        <span>
          Overall avg: <span className="font-mono text-indigo-400">{formatMs(overall.avg)}</span>
        </span>
      </div>
    </div>
  );
}

export default PerformanceMetrics;

