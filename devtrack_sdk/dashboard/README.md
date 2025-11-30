# DevTrack Dashboard

React + Tailwind CSS dashboard for DevTrack SDK, bundled with Vite and served by FastAPI.

## Overview

The dashboard is built with:
- **React 18** - Component-based UI framework
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Interactive charts for metrics visualization
- **Vite** - Fast build tool and dev server

## Development

### Prerequisites

- Node.js 18+ and npm

### Setup

```bash
cd devtrack_sdk/dashboard
npm install
```

### Run Development Server

```bash
npm run dev
```

This starts Vite's dev server at `http://localhost:5173` with hot module replacement.

**Note:** In development, you'll need to configure the API URLs manually or use a proxy. The production build automatically injects API URLs based on the FastAPI request.

## Building for Production

```bash
cd devtrack_sdk/dashboard
npm install
npm run build
```

The build process:
1. Compiles React components with Vite
2. Bundles JavaScript and CSS
3. Processes Tailwind CSS
4. Outputs optimized files to `devtrack_sdk/dashboard/dist/`
5. Runs `build.js` to inject API URL placeholders

The built files are automatically served by FastAPI at `/__devtrack__/dashboard`.

## Structure

```
dashboard/
├── src/
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # React entry point
│   ├── index.css            # Tailwind CSS imports
│   ├── components/          # React components
│   │   ├── KPICards.jsx
│   │   ├── TrafficOverview.jsx
│   │   ├── ErrorTrends.jsx
│   │   ├── PerformanceMetrics.jsx
│   │   ├── ConsumerSegmentation.jsx
│   │   ├── RequestLogs.jsx
│   │   └── StatusBar.jsx
│   └── services/
│       └── api.js           # API service functions
├── index.html               # HTML entry point
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── package.json            # Node.js dependencies
└── build.js                # Post-build script
```

## API Integration

The dashboard expects the following API endpoints:
- `GET /__devtrack__/stats` - Main stats endpoint
- `GET /__devtrack__/metrics/traffic` - Traffic metrics over time
- `GET /__devtrack__/metrics/errors` - Error trends and top failing routes
- `GET /__devtrack__/metrics/perf` - Performance metrics (p50/p95/p99 latency)
- `GET /__devtrack__/consumers` - Consumer segmentation data

API URLs are automatically injected at runtime by FastAPI based on the request base URL. The FastAPI route:
1. Reads the built `index.html`
2. Injects API URLs as `window` variables
3. Rewrites asset paths to use `/__devtrack__/dashboard/assets/`
4. Serves the modified HTML

## Static Assets

Static assets (JS, CSS, images) are served by FastAPI at:
- `/__devtrack__/dashboard/assets/{file_path}`

The FastAPI route automatically rewrites relative asset paths in the built HTML to use this endpoint.

## Features

- **Real-time Updates**: Auto-refresh with configurable intervals (5s, 10s, 30s, 60s, or pause)
- **KPI Cards**: Total requests, unique endpoints, average latency, error rate
- **Traffic Overview**: Requests over time chart
- **Error Trends**: Error rate trends and top failing routes
- **Performance Metrics**: p50/p95/p99 latency charts and statistics
- **Consumer Segmentation**: Client identification and metrics
- **Request Logs**: Searchable and filterable table with pagination

## Styling

The dashboard uses Tailwind CSS with a custom dark theme:
- Background: Gradient from gray-900 to gray-950
- Cards: Slate-900 with borders and backdrop blur
- Accent: Indigo-500/600
- Charts: Custom color schemes for different metrics

Custom colors are defined in `tailwind.config.js`:
- `devtrack-bg`, `devtrack-card`, `devtrack-accent`, etc.

