/**
 * Inbox API Service
 * 
 * Functions for fetching and managing inbox messages
 */

import api from './api';

/**
 * Get unified inbox with priority messages, unread, and events
 * @param {Object} params - Query parameters
 * @returns {Promise} Unified inbox data
 */
export const getUnifiedInbox = async (params = {}) => {
  const {
    max_per_source = 20,
    days_ahead = 3,
    priority_threshold = 0.6,
    include_raw = false
  } = params;

  console.log('📨 Calling /unified/inbox with params:', {
    max_per_source,
    days_ahead,
    priority_threshold,
    include_raw
  });

  const response = await api.get('/unified/inbox', {
    params: {
      max_per_source,
      days_ahead,
      priority_threshold,
      include_raw
    }
  });

  console.log('✅ /unified/inbox response:', response.data);
  console.log('📊 Messages count:', {
    priority: response.data.priority_messages?.length || 0,
    unread: response.data.unread_messages?.length || 0,
    events: response.data.upcoming_events?.length || 0
  });

  return response.data;
};

/**
 * Get all messages from all sources
 * @param {Object} params - Query parameters
 * @returns {Promise} All messages
 */
export const getAllMessages = async (params = {}) => {
  const {
    max_per_source = 20,
    include_raw = false,
    min_score = null
  } = params;

  const response = await api.get('/unified/messages', {
    params: {
      max_per_source,
      include_raw,
      ...(min_score && { min_score })
    }
  });

  return response.data;
};

/**
 * Search messages by query
 * @param {String} query - Search query
 * @param {Object} params - Additional parameters
 * @returns {Promise} Filtered messages
 */
export const searchMessages = async (query, params = {}) => {
  // For now, we'll get all messages and filter client-side
  // TODO: Add server-side search endpoint
  const data = await getAllMessages(params);
  
  if (!query || query.trim() === '') {
    return data;
  }

  const searchLower = query.toLowerCase();
  const filtered = {
    ...data,
    normalized: data.normalized.filter(msg => 
      msg.subject?.toLowerCase().includes(searchLower) ||
      msg.body?.toLowerCase().includes(searchLower) ||
      msg.sender?.name?.toLowerCase().includes(searchLower) ||
      msg.sender?.email?.toLowerCase().includes(searchLower)
    )
  };

  return filtered;
};

/**
 * Get message by ID
 * @param {String} messageId - Message ID
 * @returns {Promise} Message details
 */
export const getMessageById = async (messageId) => {
  // Get all messages and find the specific one
  // TODO: Add server endpoint for single message
  const data = await getAllMessages();
  const message = data.normalized.find(msg => msg.id === messageId);
  
  if (!message) {
    throw new Error(`Message ${messageId} not found`);
  }
  
  return message;
};

