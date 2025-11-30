import React from 'react';

function ConsumerSegmentation({ data }) {
  if (!data || !data.length) {
    return (
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1.5">
          <h2 className="text-sm font-medium text-gray-200">Consumer Segmentation</h2>
          <span className="text-xs px-2 py-1 rounded-full border border-slate-600 text-gray-400">
            0 clients
          </span>
        </div>
        <div className="text-sm text-gray-400 text-center py-3">No consumer data available.</div>
      </div>
    );
  }

  return (
    <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
      <div className="flex items-center justify-between mb-1.5">
        <h2 className="text-sm font-medium text-gray-200">Consumer Segmentation</h2>
        <span className="text-xs px-2 py-1 rounded-full border border-slate-600 text-gray-400">
          {data.length} client{data.length !== 1 ? 's' : ''}
        </span>
      </div>
      <div className="overflow-auto max-h-64">
        <table className="w-full text-xs border-collapse">
          <thead className="bg-slate-900/90">
            <tr>
              <th className="text-left p-1.5 text-gray-400 font-medium">Client Identifier</th>
              <th className="text-left p-1.5 text-gray-400 font-medium">Requests</th>
              <th className="text-left p-1.5 text-gray-400 font-medium">Avg Latency</th>
              <th className="text-left p-1.5 text-gray-400 font-medium">Error Rate</th>
              <th className="text-left p-1.5 text-gray-400 font-medium">Public IP</th>
            </tr>
          </thead>
          <tbody>
            {data.map((segment, idx) => (
              <tr key={idx} className="hover:bg-gray-800/50 border-b border-gray-800">
                <td className="p-1.5 font-mono text-gray-300 text-xs">
                  {segment.client_identifier || segment.client_identifier_hash || '–'}
                </td>
                <td className="p-1.5 text-gray-300">{segment.request_count || 0}</td>
                <td className="p-1.5 text-gray-300">
                  {segment.avg_latency_ms
                    ? `${Number(segment.avg_latency_ms).toFixed(2)} ms`
                    : '–'}
                </td>
                <td className="p-1.5 text-red-400">
                  {segment.error_rate ? `${segment.error_rate.toFixed(2)}%` : '0.00%'}
                </td>
                <td className="p-1.5 font-mono text-gray-300 text-xs">
                  {segment.latest_ip || '–'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ConsumerSegmentation;

