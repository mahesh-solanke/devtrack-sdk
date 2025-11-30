import React, { useState, useEffect, useMemo } from 'react';

// Column name mapping for better display
const COLUMN_NAMES = {
  id: 'ID',
  path: 'Path',
  path_pattern: 'Path Pattern',
  method: 'Method',
  status_code: 'Status',
  timestamp: 'Timestamp',
  client_ip: 'Client IP',
  duration_ms: 'Duration',
  user_agent: 'User Agent',
  referer: 'Referer',
  query_params: 'Query Params',
  path_params: 'Path Params',
  request_body: 'Request Body',
  response_size: 'Response Size',
  user_id: 'User ID',
  role: 'Role',
  trace_id: 'Trace ID',
  client_identifier: 'Client Identifier',
};

// Default fields to display in the table (in order)
// Only these fields will be shown in the table
const DEFAULT_DISPLAY_FIELDS = [
  'id',
  'timestamp',
  'method',
  'status_code',
  'path',
  'duration_ms',
  'client_ip',
  'user_id',
  'trace_id',
  'created_at',
];

function RequestLogs({ stats, loading }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterMethod, setFilterMethod] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [selectedEntry, setSelectedEntry] = useState(null);

  // Load filter state from localStorage
  useEffect(() => {
    const savedSearch = localStorage.getItem('devtrack_search');
    const savedMethod = localStorage.getItem('devtrack_method');
    const savedStatus = localStorage.getItem('devtrack_status');

    if (savedSearch) setSearchTerm(savedSearch);
    if (savedMethod) setFilterMethod(savedMethod);
    if (savedStatus) setFilterStatus(savedStatus);
  }, []);

  // Save filter state to localStorage
  const saveFilterState = () => {
    localStorage.setItem('devtrack_search', searchTerm);
    localStorage.setItem('devtrack_method', filterMethod);
    localStorage.setItem('devtrack_status', filterStatus);
  };

  useEffect(() => {
    saveFilterState();
  }, [searchTerm, filterMethod, filterStatus]);

  const entries = stats?.entries || [];

  const filteredEntries = useMemo(() => {
    return entries.filter((entry) => {
      // Search filter - search across all fields
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const searchTermStr = searchTerm;
        
        // Check if search term matches any field in the entry
        const matchesSearch = Object.keys(entry).some((key) => {
          const value = entry[key];
          if (value === null || value === undefined) {
            return false;
          }
          
          // Handle different value types
          if (typeof value === 'string') {
            return value.toLowerCase().includes(searchLower);
          }
          if (typeof value === 'number') {
            return String(value).includes(searchTermStr);
          }
          if (typeof value === 'object') {
            // For objects, stringify and search
            try {
              return JSON.stringify(value).toLowerCase().includes(searchLower);
            } catch {
              return false;
            }
          }
          
          // For other types, convert to string and search
          return String(value).toLowerCase().includes(searchLower);
        });

        if (!matchesSearch) return false;
      }

      // Method filter
      if (filterMethod && entry.method !== filterMethod) {
        return false;
      }

      // Status filter
      if (filterStatus) {
        const status = entry.status_code;
        if (filterStatus === '2xx' && (!status || status < 200 || status >= 300)) {
          return false;
        }
        if (filterStatus === '4xx' && (!status || status < 400 || status >= 500)) {
          return false;
        }
        if (filterStatus === '5xx' && (!status || status < 500)) {
          return false;
        }
      }

      return true;
    });
  }, [entries, searchTerm, filterMethod, filterStatus]);

  const clearFilters = () => {
    setSearchTerm('');
    setFilterMethod('');
    setFilterStatus('');
    localStorage.removeItem('devtrack_search');
    localStorage.removeItem('devtrack_method');
    localStorage.removeItem('devtrack_status');
  };

  const formatTimestamp = (ts) => {
    if (!ts) return '–';
    try {
      const date = new Date(ts);
      return date.toLocaleString();
    } catch {
      return String(ts);
    }
  };

  const formatMs = (n) => {
    if (n === null || n === undefined || isNaN(n)) return '–';
    return `${Number(n).toFixed(2)} ms`;
  };

  const formatValue = (key, value) => {
    if (value === null || value === undefined) return '–';
    
    if (key === 'timestamp' || key === 'created_at') {
      return formatTimestamp(value);
    }
    
    if (key === 'duration_ms' || key === 'duration') {
      return formatMs(value);
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    
    return String(value);
  };

  const handleIdClick = (entry, event) => {
    // Check if user wants to open in new window (Ctrl/Cmd + Click or middle mouse button)
    if (event.ctrlKey || event.metaKey || event.button === 1) {
      openInNewWindow(entry);
      return;
    }
    // Default: open modal
    setSelectedEntry(entry);
  };

  const openInNewWindow = (entry) => {
    // Create a new tab with the entry details
    const newWindow = window.open('', '_blank');
    if (!newWindow) {
      // If popup blocked, fallback to modal
      setSelectedEntry(entry);
      return;
    }

    // Build HTML content
    const fieldsHtml = Object.keys(entry).map(key => {
      const value = entry[key];
      let displayValue;
      let valueClass = '';
      
      if (value === null || value === undefined) {
        displayValue = '–';
      } else if (key === 'timestamp' || key === 'created_at') {
        try {
          displayValue = new Date(value).toLocaleString();
        } catch {
          displayValue = String(value);
        }
      } else if (key === 'duration_ms') {
        displayValue = Number(value).toFixed(2) + ' ms';
      } else if (key === 'status_code') {
        const status = Number(value);
        if (status >= 200 && status < 300) valueClass = 'status-2xx';
        else if (status >= 400 && status < 500) valueClass = 'status-4xx';
        else if (status >= 500) valueClass = 'status-5xx';
        displayValue = value;
      } else if (typeof value === 'object') {
        displayValue = JSON.stringify(value, null, 2);
      } else {
        displayValue = String(value);
      }
      
      const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const isJson = typeof value === 'object' && value !== null;
      
      // Escape HTML
      const escapedDisplay = String(displayValue)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
      
      const escapedValue = isJson 
        ? '<pre>' + escapedDisplay + '</pre>'
        : escapedDisplay;
      
      return '<div class="field">' +
        '<div class="field-label">' + label + '</div>' +
        '<div class="field-value ' + valueClass + '">' + escapedValue + '</div>' +
        '</div>';
    }).join('');

    const entryId = entry.id || 'N/A';
    const html = '<!DOCTYPE html>' +
      '<html>' +
      '<head>' +
      '<title>Request Details - ID: ' + entryId + '</title>' +
      '<style>' +
      '* { margin: 0; padding: 0; box-sizing: border-box; }' +
      'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }' +
      '.container { max-width: 1200px; margin: 0 auto; }' +
      'h1 { color: #f1f5f9; margin-bottom: 10px; font-size: 24px; }' +
      '.subtitle { color: #94a3b8; margin-bottom: 30px; font-size: 14px; }' +
      '.field { border-bottom: 1px solid #1e293b; padding: 15px 0; }' +
      '.field:last-child { border-bottom: none; }' +
      '.field-label { font-size: 11px; text-transform: uppercase; color: #64748b; margin-bottom: 8px; letter-spacing: 0.5px; font-weight: 600; }' +
      '.field-value { font-size: 14px; color: #e2e8f0; word-break: break-word; }' +
      '.field-value pre { background: #020617; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px; font-family: "Courier New", monospace; border: 1px solid #1e293b; white-space: pre-wrap; }' +
      '.status-2xx { color: #4ade80; }' +
      '.status-4xx { color: #fbbf24; }' +
      '.status-5xx { color: #f87171; }' +
      '</style>' +
      '</head>' +
      '<body>' +
      '<div class="container">' +
      '<h1>Request Details</h1>' +
      '<div class="subtitle">Log ID: ' + entryId + '</div>' +
      fieldsHtml +
      '</div>' +
      '</body>' +
      '</html>';

    try {
      newWindow.document.open();
      newWindow.document.write(html);
      newWindow.document.close();
    } catch (error) {
      console.error('Failed to write to new window:', error);
      // Fallback to modal
      setSelectedEntry(entry);
    }
  };

  const closeModal = () => {
    setSelectedEntry(null);
  };

  if (!entries.length) {
    return (
      <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
        <div className="flex items-center justify-between mb-1.5">
          <h2 className="text-sm font-medium text-gray-200">Request Logs</h2>
          <span className="text-xs px-2 py-1 rounded-full border border-slate-600 text-gray-400">
            0 records
          </span>
        </div>
        <div className="text-sm text-gray-400 text-center py-3">
          No records returned from API.
        </div>
      </div>
    );
  }

  // Get fields to display - only show fields in DEFAULT_DISPLAY_FIELDS
  const availableKeys = Array.from(
    entries.reduce((set, entry) => {
      if (entry && typeof entry === 'object') {
        Object.keys(entry).forEach((k) => {
          // Skip client_identifier_hash column
          if (k !== 'client_identifier_hash') {
            set.add(k);
          }
        });
      }
      return set;
    }, new Set())
  );

  // Only show fields in DEFAULT_DISPLAY_FIELDS that exist in the data (strict filtering)
  const keys = DEFAULT_DISPLAY_FIELDS.filter(key => availableKeys.includes(key));

  return (
    <div className="mt-1.5 mb-2 rounded-xl border border-gray-700 bg-teal-500/5 p-3">
      <div className="flex items-center justify-between mb-1.5">
        <h2 className="text-sm font-medium text-gray-200">Request Logs</h2>
        <span className="text-xs px-2 py-1 rounded-full border border-slate-600 text-gray-400">
          {filteredEntries.length} record{filteredEntries.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Filters */}
      <div className="mb-2.5 flex flex-wrap gap-2 items-center">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search logs..."
          className="flex-1 min-w-[200px] px-2.5 py-1.5 rounded-lg border border-slate-600 bg-slate-900/90 text-gray-200 text-sm outline-none focus:border-indigo-500"
        />
        <select
          value={filterMethod}
          onChange={(e) => setFilterMethod(e.target.value)}
          className="px-2.5 py-1.5 rounded-lg border border-slate-600 bg-slate-900/90 text-gray-200 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">All Methods</option>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
          <option value="PATCH">PATCH</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-2.5 py-1.5 rounded-lg border border-slate-600 bg-slate-900/90 text-gray-200 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">All Status</option>
          <option value="2xx">2xx Success</option>
          <option value="4xx">4xx Client Error</option>
          <option value="5xx">5xx Server Error</option>
        </select>
        <button
          onClick={clearFilters}
          className="px-3 py-1.5 text-sm rounded-lg border border-slate-600 bg-slate-900/90 text-gray-200 hover:bg-slate-800 transition-colors"
        >
          Clear Filters
        </button>
      </div>

      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
          <div className="w-3 h-3 border-2 border-slate-600 border-t-indigo-500 rounded-full animate-spin" />
          <span>Fetching latest data…</span>
        </div>
      )}

      {/* Table */}
      <div className="overflow-auto max-h-80">
        <table className="w-full text-xs border-collapse">
          <thead className="bg-slate-900/90">
            <tr>
              {keys.map((key) => (
                <th key={key} className="text-left p-1.5 text-gray-400 font-medium">
                  {COLUMN_NAMES[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredEntries.length === 0 ? (
              <tr>
                <td colSpan={keys.length} className="p-3 text-center text-gray-400">
                  No records match the current filters.
                </td>
              </tr>
            ) : (
              filteredEntries.map((entry, idx) => (
                <tr key={idx} className="hover:bg-gray-800/50 border-b border-gray-800">
                  {keys.map((key) => {
                    let val = entry[key];
                    let displayValue;
                    
                    if (val === null || val === undefined) {
                      displayValue = '–';
                    } else if (typeof val === 'object') {
                      // For objects, show a summary instead of full JSON
                      if (Array.isArray(val)) {
                        displayValue = `[${val.length} items]`;
                      } else if (Object.keys(val).length === 0) {
                        displayValue = '{}';
                      } else {
                        displayValue = `{${Object.keys(val).length} keys}`;
                      }
                    } else if (key === 'timestamp' || key === 'created_at') {
                      displayValue = formatTimestamp(val);
                    } else if (key === 'duration_ms') {
                      displayValue = formatMs(val);
                    } else if (key === 'status_code') {
                      // Color code status codes
                      const status = Number(val);
                      let statusClass = 'text-gray-300';
                      if (status >= 200 && status < 300) {
                        statusClass = 'text-green-400';
                      } else if (status >= 400 && status < 500) {
                        statusClass = 'text-yellow-400';
                      } else if (status >= 500) {
                        statusClass = 'text-red-400';
                      }
                      displayValue = <span className={statusClass}>{val}</span>;
                    } else {
                      displayValue = String(val);
                    }
                    
                    // Make id clickable
                    const isId = key === 'id';
                    const cellContent = isId ? (
                      <button
                        onClick={(e) => handleIdClick(entry, e)}
                        onMouseDown={(e) => {
                          // Handle middle mouse button
                          if (e.button === 1) {
                            e.preventDefault();
                            openInNewWindow(entry);
                          }
                        }}
                        className="text-indigo-400 hover:text-indigo-300 underline cursor-pointer font-mono text-xs"
                        title="Click to view details | Ctrl/Cmd+Click to open in new window"
                      >
                        {displayValue}
                      </button>
                    ) : (
                      <span className="text-xs">{displayValue}</span>
                    );
                    
                    return (
                      <td key={key} className="p-1.5 text-gray-300">
                        {cellContent}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedEntry && (
        <div
          className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
          onClick={closeModal}
        >
          <div
            className="bg-slate-900 rounded-xl border border-gray-700 max-w-4xl w-full max-h-[90vh] overflow-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-slate-900 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-200">
                  Request Details
                </h3>
                <p className="text-xs text-gray-400 mt-1">
                  Log ID: {selectedEntry.id || 'N/A'}
                </p>
              </div>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-200 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">
              <div className="space-y-4">
                {Object.keys(selectedEntry).map((key) => {
                  const value = selectedEntry[key];
                  const formattedValue = formatValue(key, value);
                  const isJson = typeof value === 'object' && value !== null;
                  
                  return (
                    <div key={key} className="border-b border-gray-800 pb-3 last:border-0">
                      <div className="text-xs font-medium text-gray-400 mb-1 uppercase tracking-wide">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-sm text-gray-200">
                        {isJson ? (
                          <pre className="bg-slate-950 p-3 rounded-lg overflow-x-auto text-xs font-mono">
                            {formattedValue}
                          </pre>
                        ) : (
                          <div className="font-mono break-words">{formattedValue}</div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-slate-900 border-t border-gray-700 px-6 py-4 flex justify-end gap-2">
              <button
                onClick={() => openInNewWindow(selectedEntry)}
                className="px-4 py-2 bg-slate-700 text-gray-100 rounded-lg hover:bg-slate-600 transition-colors text-sm font-medium"
              >
                Open in New Tab
              </button>
              <button
                onClick={closeModal}
                className="px-4 py-2 bg-indigo-600 text-gray-100 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RequestLogs;

