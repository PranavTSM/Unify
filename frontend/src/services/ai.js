/**
 * AI Features API Service
 * 
 * Functions for AI-powered features: summarization and action extraction
 */

import api from './api';

/**
 * Summarize messages using AI
 * @param {Array} messageIds - Array of message IDs (optional)
 * @param {Object} options - Summarization options
 * @returns {Promise} Summary data
 */
export const summarizeMessages = async (messageIds = null, options = {}) => {
  const {
    mode = 'bullets',
    max_words = 200,
    include_messages = false,
    store_in_memory = false,
    session_id = null
  } = options;

  const payload = {
    mode,
    max_words,
    include_messages,
    store_in_memory,
    ...(session_id && { session_id }),
    ...(messageIds && messageIds.length > 0 && { message_ids: messageIds })
  };

  const response = await api.post('/unified/inbox/summarize', payload);
  return response.data;
};

/**
 * Extract action items from messages using AI
 * @param {Array} messageIds - Array of message IDs (optional)
 * @param {Object} options - Extraction options
 * @returns {Promise} Action items
 */
export const extractActions = async (messageIds = null, options = {}) => {
  const {
    context = '',
    priority_mode = 'hybrid',
    include_messages = false,
    min_priority = null
  } = options;

  const payload = {
    context,
    priority_mode,
    include_messages,
    ...(min_priority && { min_priority }),
    ...(messageIds && messageIds.length > 0 && { message_ids: messageIds })
  };

  const response = await api.post('/unified/inbox/extract-actions', payload);
  return response.data;
};

/**
 * Summarize single message
 * @param {String} messageId - Message ID
 * @param {String} mode - Summary mode (executive/bullets/paragraph)
 * @returns {Promise} Summary data
 */
export const summarizeSingleMessage = async (messageId, mode = 'bullets') => {
  return summarizeMessages([messageId], { mode, max_words: 200 });
};

/**
 * Extract actions from single message
 * @param {String} messageId - Message ID
 * @param {String} context - Additional context
 * @returns {Promise} Action items
 */
export const extractActionsFromMessage = async (messageId, context = '') => {
  return extractActions([messageId], { context, priority_mode: 'hybrid' });
};

/**
 * Get AI insights for a message (summary + actions)
 * @param {String} messageId - Message ID
 * @returns {Promise} Combined insights
 */
export const getMessageInsights = async (messageId) => {
  try {
    const [summaryData, actionsData] = await Promise.all([
      summarizeSingleMessage(messageId, 'bullets'),
      extractActionsFromMessage(messageId, '')
    ]);

    return {
      summary: summaryData.summary,
      bullets: summaryData.bullets,
      actions: actionsData.actions,
      actionSummary: actionsData.summary
    };
  } catch (error) {
    console.error('Error getting message insights:', error);
    throw error;
  }
};

