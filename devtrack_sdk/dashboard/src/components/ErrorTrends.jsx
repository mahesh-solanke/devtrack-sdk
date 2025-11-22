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

function ErrorTrends({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data?.error_trends || !data.error_trends.length) return;

    const labels = data.error_trends.map((item) => {
      const date = new Date(item.time_bucket);
      return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    });

    const errorRates = data.error_trends.map((item) => item.error_rate || 0);

    const chartData = {
      labels,
      datasets: [
        {
          label: 'Error Rate (%)',
          data: errorRates,
          borderColor: 'rgb(249, 115, 115)',
          backgroundColor: 'rgba(249, 115, 115, 0.1)',
          tension: 0.3,
          fill: true,
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
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}%`,
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
          max: 100,
          ticks: {
            color: '#9ca3af',
            font: { size: 10 },
            callback: (value) => `${value}%`,
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

  const topFailing = data?.top_failing_routes || [];

  if (!data || (!data.error_trends?.length && !topFailing.length)) {
    return (
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-medium text-gray-200">Error Trends</h2>
          <span className="text-xs text-gray-400">Failure rates over time</span>
        </div>
        <div className="text-sm text-gray-400 text-center py-3">
          No error data available.
        </div>
      </div>
    );
  }

  const labels = data.error_trends?.map((item) => {
    const date = new Date(item.time_bucket);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  }) || [];

  const errorRates = data.error_trends?.map((item) => item.error_rate || 0) || [];

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Error Rate (%)',
        data: errorRates,
        borderColor: 'rgb(249, 115, 115)',
        backgroundColor: 'rgba(249, 115, 115, 0.1)',
        tension: 0.3,
        fill: true,
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
          label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}%`,
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
        max: 100,
        ticks: {
          color: '#9ca3af',
          font: { size: 10 },
          callback: (value) => `${value}%`,
        },
        grid: { color: 'rgba(31,41,55,0.5)' },
      },
    },
  };

  return (
    <>
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-medium text-gray-200">Error Trends</h2>
          <span className="text-xs text-gray-400">Failure rates over time</span>
        </div>
        {data.error_trends?.length ? (
          <div className="h-[120px]">
            <Line ref={chartRef} data={chartData} options={options} />
          </div>
        ) : (
          <div className="text-sm text-gray-400 text-center py-3">
            No error data available.
          </div>
        )}
      </div>

      {topFailing.length > 0 && (
        <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
          <div className="flex items-center justify-between mb-1.5">
            <h2 className="text-sm font-medium text-gray-200">Top Failing Routes</h2>
            <span className="text-xs px-2 py-1 rounded-full border border-slate-600 text-gray-400">
              {topFailing.length} route{topFailing.length !== 1 ? 's' : ''}
            </span>
          </div>
          <div className="overflow-auto max-h-64">
            <table className="w-full text-xs border-collapse">
              <thead className="bg-slate-900/90">
                <tr>
                  <th className="text-left p-1.5 text-gray-400 font-medium">Route</th>
                  <th className="text-left p-1.5 text-gray-400 font-medium">Errors</th>
                  <th className="text-left p-1.5 text-gray-400 font-medium">Error Rate</th>
                </tr>
              </thead>
              <tbody>
                {topFailing.map((route, idx) => (
                  <tr key={idx} className="hover:bg-gray-800/50 border-b border-gray-800">
                    <td className="p-1.5 font-mono text-gray-300">{route.route || '–'}</td>
                    <td className="p-1.5 text-gray-300">{route.error_count || 0}</td>
                    <td className="p-1.5 text-red-400">
                      {route.error_rate ? `${route.error_rate.toFixed(2)}%` : '–'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}

export default ErrorTrends;

