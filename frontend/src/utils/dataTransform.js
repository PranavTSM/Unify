/**
 * Data Transformation Utilities
 * 
 * Transform backend API responses to frontend-compatible formats
 */

/**
 * Get initials from a name
 * @param {String} name - Full name
 * @returns {String} Initials (max 2 chars)
 */
export const getInitials = (name) => {
  if (!name) return '?';
  
  const parts = name.trim().split(' ').filter(p => p.length > 0);
  if (parts.length === 0) return '?';
  
  if (parts.length === 1) {
    return parts[0].substring(0, 2).toUpperCase();
  }
  
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};

/**
 * Format source name for display
 * @param {String} source - Backend source name
 * @returns {String} Display name
 */
export const formatSource = (source) => {
  const sourceMap = {
    'gmail': 'Gmail',
    'outlook': 'Outlook',
    'teams': 'Teams',
    'google_calendar': 'Google Calendar',
    'microsoft_calendar': 'Microsoft Calendar'
  };
  
  return sourceMap[source?.toLowerCase()] || source || 'Unknown';
};

/**
 * Calculate event duration from start and end times
 * @param {String} start - ISO start time
 * @param {String} end - ISO end time
 * @returns {String} Formatted duration (e.g., "30 min", "1 hour", "2h 30m")
 */
export const calculateDuration = (start, end) => {
  if (!start || !end) return 'Unknown';
  
  const startDate = new Date(start);
  const endDate = new Date(end);
  const durationMs = endDate - startDate;
  const durationMin = Math.floor(durationMs / 60000);
  
  if (durationMin < 60) {
    return `${durationMin} min`;
  }
  
  const hours = Math.floor(durationMin / 60);
  const mins = durationMin % 60;
  
  if (mins === 0) {
    return hours === 1 ? '1 hour' : `${hours} hours`;
  }
  
  return `${hours}h ${mins}m`;
};

/**
 * Detect event type from title and metadata
 * @param {String} title - Event title
 * @param {Object} metadata - Event metadata
 * @returns {String} Event type (meeting/presentation/call/etc)
 */
export const detectEventType = (title = '', metadata = {}) => {
  const titleLower = title.toLowerCase();
  
  if (titleLower.includes('presentation') || titleLower.includes('demo') || titleLower.includes('pitch')) {
    return 'presentation';
  }
  
  if (titleLower.includes('standup') || titleLower.includes('sync') || titleLower.includes('1:1')) {
    return 'meeting';
  }
  
  if (titleLower.includes('call') || titleLower.includes('phone')) {
    return 'call';
  }
  
  if (titleLower.includes('review') || titleLower.includes('feedback')) {
    return 'review';
  }
  
  // Default to meeting
  return 'meeting';
};

/**
 * Transform backend message to frontend format
 * @param {Object} apiMessage - Message from backend API
 * @returns {Object} Frontend-compatible message
 */
export const transformMessage = (apiMessage) => {
  const senderName = apiMessage.sender?.name || apiMessage.sender?.email || 'Unknown Sender';
  const body = typeof apiMessage.body === 'string' 
    ? apiMessage.body 
    : apiMessage.body?.content || '';
  
  return {
    id: apiMessage.id,
    sender: senderName,
    senderEmail: apiMessage.sender?.email,
    subject: apiMessage.subject || '(No Subject)',
    preview: body.substring(0, 150) + (body.length > 150 ? '...' : ''),
    content: body,
    time: new Date(apiMessage.timestamp),
    read: apiMessage.is_read !== false, // Default to read if not specified
    hasAttachment: apiMessage.attachments && apiMessage.attachments.length > 0,
    category: formatSource(apiMessage.source),
    avatar: getInitials(senderName),
    importance_score: apiMessage.importance_score || 0.5,
    labels: apiMessage.labels || [],
    attachments: apiMessage.attachments || [],
    
    // Keep original data for reference
    _original: apiMessage
  };
};

/**
 * Transform backend event to frontend format
 * @param {Object} apiEvent - Event from backend API
 * @returns {Object} Frontend-compatible event
 */
export const transformEvent = (apiEvent) => {
  const start = new Date(apiEvent.start);
  const end = new Date(apiEvent.end);
  const duration = calculateDuration(apiEvent.start, apiEvent.end);
  const type = detectEventType(apiEvent.title, apiEvent);
  
  // Extract attendee names
  const attendees = apiEvent.attendees 
    ? apiEvent.attendees.map(a => a.name || a.email || 'Unknown')
    : [];
  
  return {
    id: apiEvent.id,
    title: apiEvent.title || '(No Title)',
    date: start,
    startTime: start,
    endTime: end,
    duration,
    type,
    attendees,
    location: apiEvent.location || null,
    organizer: apiEvent.organizer?.name || apiEvent.organizer?.email,
    description: apiEvent.description || '',
    source: formatSource(apiEvent.source),
    hasConflict: apiEvent.has_conflict || false,
    
    // Keep original data
    _original: apiEvent
  };
};

/**
 * Transform array of messages
 * @param {Array} apiMessages - Array of messages from backend
 * @returns {Array} Array of transformed messages
 */
export const transformMessages = (apiMessages = []) => {
  if (!Array.isArray(apiMessages)) {
    console.warn('transformMessages: expected array, got:', typeof apiMessages);
    return [];
  }
  
  return apiMessages.map(msg => transformMessage(msg));
};

/**
 * Transform array of events
 * @param {Array} apiEvents - Array of events from backend
 * @returns {Array} Array of transformed events
 */
export const transformEvents = (apiEvents = []) => {
  if (!Array.isArray(apiEvents)) {
    console.warn('transformEvents: expected array, got:', typeof apiEvents);
    return [];
  }
  
  return apiEvents.map(event => transformEvent(event));
};

/**
 * Calculate stats from messages
 * @param {Object} inboxData - Unified inbox data from backend
 * @returns {Object} Dashboard statistics
 */
export const calculateDashboardStats = (inboxData) => {
  const allMessages = [
    ...(inboxData.priority_messages || []),
    ...(inboxData.unread_messages || [])
  ];
  
  const uniqueMessages = Array.from(
    new Map(allMessages.map(m => [m.id, m])).values()
  );
  
  const totalMessages = inboxData.summary?.total_messages || uniqueMessages.length;
  const unreadCount = uniqueMessages.filter(m => !m.is_read).length;
  
  // Calculate today's sent (would need additional API endpoint)
  const sentToday = 0; // TODO: Add sent messages endpoint
  
  // Calculate average response time (would need additional data)
  const avgResponseTime = '2.4h'; // TODO: Calculate from metadata
  
  return [
    { 
      title: 'Total Messages', 
      value: totalMessages.toString(), 
      change: '+12%', 
      trend: 'up' 
    },
    { 
      title: 'Unread', 
      value: unreadCount.toString(), 
      change: '-5%', 
      trend: 'down' 
    },
    { 
      title: 'Sent Today', 
      value: sentToday.toString(), 
      change: '+8%', 
      trend: 'up' 
    },
    { 
      title: 'Response Time', 
      value: avgResponseTime, 
      change: '-15%', 
      trend: 'down' 
    },
  ];
};

/**
 * Extract unique messages from inbox data
 * @param {Object} inboxData - Unified inbox data
 * @returns {Array} Unique messages
 */
export const extractUniqueMessages = (inboxData) => {
  const allMessages = [
    ...(inboxData.priority_messages || []),
    ...(inboxData.unread_messages || [])
  ];
  
  // Deduplicate by ID
  const uniqueMap = new Map();
  allMessages.forEach(msg => {
    if (msg.id && !uniqueMap.has(msg.id)) {
      uniqueMap.set(msg.id, msg);
    }
  });
  
  return Array.from(uniqueMap.values());
};

