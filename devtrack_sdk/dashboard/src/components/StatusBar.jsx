import React from 'react';

function StatusBar({ isOnline, lastUpdated, apiUrl }) {
  const formatTime = (date) => {
    if (!date) return '–';
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="flex flex-wrap justify-between items-center gap-2 mb-4 p-3 rounded-xl bg-indigo-500/10 border border-gray-700">
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <div
          className={`w-2 h-2 rounded-full ${
            isOnline ? 'bg-green-500' : 'bg-red-500'
          } ${isOnline ? 'shadow-[0_0_10px_rgba(74,222,128,0.8)]' : 'shadow-[0_0_10px_rgba(248,113,113,0.8)]'}`}
        />
        <span>{isOnline ? 'Connected' : 'Disconnected'}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <span>Endpoint:</span>
        <code className="text-xs font-mono max-w-xs truncate">{apiUrl}</code>
        <span>|</span>
        <span>Last updated: {formatTime(lastUpdated)}</span>
      </div>
    </div>
  );
}

export default StatusBar;

