/**
 * Calendar API Service
 * 
 * Functions for fetching and managing calendar events
 */

import api from './api';

/**
 * Get unified calendar events
 * @param {Object} params - Query parameters
 * @returns {Promise} Calendar events
 */
export const getCalendarEvents = async (params = {}) => {
  const {
    days_ahead = 30,
    include_raw = false
  } = params;

  const response = await api.get('/unified/calendar', {
    params: {
      days_ahead,
      include_raw
    }
  });

  return response.data;
};

/**
 * Get events for a specific date range
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date
 * @returns {Promise} Filtered events
 */
export const getEventsForDateRange = async (startDate, endDate) => {
  // Calculate days ahead from today to end date
  const today = new Date();
  const daysAhead = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));
  
  const data = await getCalendarEvents({ days_ahead: Math.max(daysAhead, 1) });
  
  // Filter events within the date range
  const filtered = {
    ...data,
    normalized: data.normalized.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate >= startDate && eventDate <= endDate;
    })
  };
  
  return filtered;
};

/**
 * Get events for a specific date
 * @param {Date} date - Target date
 * @returns {Promise} Events for the date
 */
export const getEventsForDate = async (date) => {
  const startOfDay = new Date(date);
  startOfDay.setHours(0, 0, 0, 0);
  
  const endOfDay = new Date(date);
  endOfDay.setHours(23, 59, 59, 999);
  
  return getEventsForDateRange(startOfDay, endOfDay);
};

/**
 * Get today's events
 * @returns {Promise} Today's events
 */
export const getTodayEvents = async () => {
  const data = await getCalendarEvents({ days_ahead: 1 });
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  // Filter to today only
  const filtered = {
    ...data,
    normalized: data.normalized.filter(event => {
      const eventDate = new Date(event.start);
      return eventDate >= today && eventDate < tomorrow;
    })
  };
  
  return filtered;
};

/**
 * Get upcoming events (next 7 days)
 * @returns {Promise} Upcoming events
 */
export const getUpcomingEvents = async () => {
  return getCalendarEvents({ days_ahead: 7 });
};

/**
 * Create a new calendar event
 * @param {Object} eventData - Event details
 * @returns {Promise} Created event
 */
export const createEvent = async (eventData) => {
  const {
    summary,
    description,
    location,
    start,
    end,
    attendees = [],
    reminders,
    calendarId = 'primary'
  } = eventData;

  const payload = {
    summary,
    start: {
      dateTime: start,
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    },
    end: {
      dateTime: end,
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    }
  };

  if (description) payload.description = description;
  if (location) payload.location = location;
  if (attendees.length > 0) {
    payload.attendees = attendees.map(email => ({ email }));
  }
  if (reminders) payload.reminders = reminders;

  const response = await api.post(`/mcp/calendars/${calendarId}/events`, payload);
  return response.data;
};

/**
 * Update an existing event
 * @param {String} eventId - Event ID
 * @param {Object} updates - Fields to update
 * @returns {Promise} Updated event
 */
export const updateEvent = async (eventId, updates, calendarId = 'primary') => {
  const response = await api.patch(`/mcp/calendars/${calendarId}/events/${eventId}`, updates);
  return response.data;
};

/**
 * Delete an event
 * @param {String} eventId - Event ID
 * @param {String} calendarId - Calendar ID
 * @returns {Promise} Deletion result
 */
export const deleteEvent = async (eventId, calendarId = 'primary') => {
  const response = await api.delete(`/mcp/calendars/${calendarId}/events/${eventId}`);
  return response.data;
};

/**
 * Quick add event using natural language
 * @param {String} text - Natural language description (e.g., "Meeting with John tomorrow at 3pm")
 * @param {String} calendarId - Calendar ID
 * @returns {Promise} Created event
 */
export const quickAddEvent = async (text, calendarId = 'primary') => {
  const response = await api.post(`/mcp/calendars/${calendarId}/events/quickAdd`, { text });
  return response.data;
};

