/**
 * API Configuration
 * 
 * Centralized configuration for all API endpoints and settings
 */

// API Base URLs
export const API_CONFIG = {
  // Aggregator service (primary API)
  AGGREGATOR_URL: import.meta.env.VITE_AGGREGATOR_URL || 'http://localhost:8001',
  
  // LLM service (direct access if needed)
  LLM_SERVICE_URL: import.meta.env.VITE_LLM_SERVICE_URL || 'http://localhost:8002',
  
  // MCP server (usually not accessed directly from frontend)
  MCP_SERVER_URL: import.meta.env.VITE_MCP_SERVER_URL || 'http://localhost:8000',
};

// Request timeouts (milliseconds)
export const TIMEOUTS = {
  DEFAULT: 30000,    // 30 seconds
  AI_FEATURES: 60000, // 60 seconds for AI operations
  UPLOAD: 120000,    // 2 minutes for file uploads
};

// Polling intervals (milliseconds)
export const POLLING = {
  INBOX_REFRESH: 30000,     // 30 seconds
  CALENDAR_REFRESH: 60000,  // 60 seconds
  STATUS_CHECK: 10000,      // 10 seconds
};

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  DEFAULT_MAX_PER_SOURCE: 20,
};

// Feature flags
export const FEATURES = {
  AI_SUMMARIZATION: true,
  ACTION_EXTRACTION: true,
  AUTO_REFRESH: true,
  REAL_TIME_UPDATES: false, // WebSocket support (future)
};

// Display settings
export const DISPLAY = {
  PREVIEW_LENGTH: 150,        // Characters for message preview
  MAX_ATTACHMENT_SIZE: 10485760, // 10MB in bytes
  DATE_FORMAT: 'MMM dd, yyyy',
  TIME_FORMAT: 'h:mm a',
};

export default API_CONFIG;

