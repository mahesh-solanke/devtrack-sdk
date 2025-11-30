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
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

function TrafficOverview({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || !data.length) return;

    const labels = data.map((item) => {
      const date = new Date(item.time_bucket);
      return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    });

    const requestCounts = data.map((item) => item.request_count || 0);

    const chartData = {
      labels,
      datasets: [
        {
          label: 'Requests',
          data: requestCounts,
          borderColor: 'rgb(79, 70, 229)',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
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
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} requests`,
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

  if (!data || !data.length) {
    return (
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-sm font-medium text-gray-200">Traffic Overview</h2>
          <span className="text-xs text-gray-400">Requests over time</span>
        </div>
        <div className="text-sm text-gray-400 text-center py-3">
          No traffic data available. Trigger some requests to see the chart.
        </div>
      </div>
    );
  }

  const labels = data.map((item) => {
    const date = new Date(item.time_bucket);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
    });
  });

  const requestCounts = data.map((item) => item.request_count || 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Requests',
        data: requestCounts,
        borderColor: 'rgb(79, 70, 229)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
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
          label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} requests`,
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
        },
        grid: { color: 'rgba(31,41,55,0.5)' },
      },
    },
  };

  return (
    <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-sm font-medium text-gray-200">Traffic Overview</h2>
        <span className="text-xs text-gray-400">Requests over time</span>
      </div>
      <div className="h-[120px]">
        <Line ref={chartRef} data={chartData} options={options} />
      </div>
    </div>
  );
}

export default TrafficOverview;

