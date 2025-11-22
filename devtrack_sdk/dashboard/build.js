// Post-build script to inject API URLs into the built HTML
import { readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const distPath = join(__dirname, 'dist');
const indexPath = join(distPath, 'index.html');

try {
  let html = readFileSync(indexPath, 'utf-8');
  
  // Inject script tags to set API URLs (will be replaced by FastAPI)
  const apiScript = `
    <script>
      // API URLs - will be replaced by FastAPI at runtime
      window.API_URL = window.API_URL || '/__devtrack__/stats';
      window.TRAFFIC_API_URL = window.TRAFFIC_API_URL || '/__devtrack__/metrics/traffic';
      window.ERRORS_API_URL = window.ERRORS_API_URL || '/__devtrack__/metrics/errors';
      window.PERF_API_URL = window.PERF_API_URL || '/__devtrack__/metrics/perf';
      window.CONSUMERS_API_URL = window.CONSUMERS_API_URL || '/__devtrack__/consumers';
    </script>
  `;
  
  // Insert before closing </head> tag
  html = html.replace('</head>', `${apiScript}</head>`);
  
  writeFileSync(indexPath, html, 'utf-8');
  console.log('✓ Injected API URL placeholders into index.html');
} catch (error) {
  console.error('Failed to inject API URLs:', error);
  process.exit(1);
}

