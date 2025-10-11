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

