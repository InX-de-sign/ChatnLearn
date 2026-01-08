// Configuration for API endpoints
// Update this after deploying to Railway
const API_CONFIG = {
    // Local development
    local: {
        ws: 'ws://localhost:8000',
        http: 'http://localhost:8000'
    },
    // Production (update with your Railway URL after deployment)
    production: {
        ws: 'wss://your-app.railway.app',
        http: 'https://your-app.railway.app'
    }
};

// Auto-detect environment
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const config = isProduction ? API_CONFIG.production : API_CONFIG.local;

// Export for use in HTML files
window.API_URL = config.http;
window.WS_URL = config.ws;
