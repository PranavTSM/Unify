/**
 * Message Actions API Service
 * Handles mark as read, star, archive, delete, snooze operations
 */

import api from './api';

/**
 * Perform action on a single message
 */
export const performMessageAction = async (messageId, source, action) => {
  try {
    const response = await api.post('/messages/action', {
      message_id: messageId,
      source: source,
      action: action
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to ${action} message:`, error);
    throw error;
  }
};

/**
 * Mark message as read
 */
export const markAsRead = (messageId, source) => {
  return performMessageAction(messageId, source, 'mark_read');
};

/**
 * Mark message as unread
 */
export const markAsUnread = (messageId, source) => {
  return performMessageAction(messageId, source, 'mark_unread');
};

/**
 * Star a message
 */
export const starMessage = (messageId, source) => {
  return performMessageAction(messageId, source, 'star');
};

/**
 * Unstar a message
 */
export const unstarMessage = (messageId, source) => {
  return performMessageAction(messageId, source, 'unstar');
};

/**
 * Archive a message
 */
export const archiveMessage = (messageId, source) => {
  return performMessageAction(messageId, source, 'archive');
};

/**
 * Delete a message
 */
export const deleteMessage = (messageId, source) => {
  return performMessageAction(messageId, source, 'delete');
};

/**
 * Perform bulk action on multiple messages
 */
export const performBulkAction = async (messageIds, source, action) => {
  try {
    const response = await api.post('/messages/bulk-action', {
      message_ids: messageIds,
      source: source,
      action: action
    });
    return response.data;
  } catch (error) {
    console.error(`Failed bulk ${action}:`, error);
    throw error;
  }
};

/**
 * Snooze a message
 */
export const snoozeMessage = async (messageId, options = {}) => {
  try {
    const response = await api.post('/messages/snooze', {
      message_id: messageId,
      snooze_until: options.until,
      snooze_minutes: options.minutes
    });
    return response.data;
  } catch (error) {
    console.error('Failed to snooze message:', error);
    throw error;
  }
};

/**
 * Get snoozed messages
 */
export const getSnoozedMessages = async () => {
  try {
    const response = await api.get('/messages/snoozed');
    return response.data;
  } catch (error) {
    console.error('Failed to get snoozed messages:', error);
    throw error;
  }
};

/**
 * Unsnooze a message
 */
export const unsnoozeMessage = async (messageId) => {
  try {
    const response = await api.delete(`/messages/snooze/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to unsnooze message:', error);
    throw error;
  }
};

/**
 * Search messages
 */
export const searchMessages = async (query, sources = null, maxResults = 50) => {
  try {
    const params = { query, max_results: maxResults };
    if (sources && sources.length > 0) {
      params.sources = sources;
    }
    
    const response = await api.get('/search', { params });
    return response.data;
  } catch (error) {
    console.error('Failed to search messages:', error);
    throw error;
  }
};

/**
 * Get analytics stats
 */
export const getAnalytics = async () => {
  try {
    const response = await api.get('/analytics/stats');
    return response.data;
  } catch (error) {
    console.error('Failed to get analytics:', error);
    throw error;
  }
};

