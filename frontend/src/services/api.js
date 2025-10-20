/**
 * Base API Client Configuration
 * 
 * Centralized axios instance for all API calls
 */

import axios from 'axios';

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_AGGREGATOR_URL || 'http://localhost:8001';

console.log('🔗 API Base URL:', API_BASE_URL);

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds (increased to prevent timeouts with caching)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - for logging and auth
api.interceptors.request.use(
  (config) => {
    console.log(`📤 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.data || error.message);
    
    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Server error');
          break;
        case 503:
          console.error('Service unavailable');
          break;
        default:
          console.error('API error:', error.response.status);
      }
    } else if (error.request) {
      console.error('No response from server - check if backend is running');
    }
    
    return Promise.reject(error);
  }
);

export default api;

