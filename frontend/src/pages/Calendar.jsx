import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  ChevronLeft, 
  ChevronRight,
  Plus,
  Clock,
  Users,
  MapPin,
  Video,
  Calendar as CalendarIcon,
  RefreshCw
} from 'lucide-react';
import { getCalendarEvents, createEvent, deleteEvent } from '@/services/calendar';
import { transformEvents } from '@/utils/dataTransform';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import EmptyState from '@/components/EmptyState';
import CreateEventModal from '@/components/CreateEventModal';

const Calendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedDateForEvent, setSelectedDateForEvent] = useState(null);

  // Fetch calendar events
  const fetchEvents = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);

      const eventsData = await getCalendarEvents({ days_ahead: 30 });
      const transformed = transformEvents(eventsData.normalized || []);
      
      setCalendarEvents(transformed);
      setLoading(false);

    } catch (err) {
      console.error('Error fetching events:', err);
      setError(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(() => {
      fetchEvents(false);
    }, 60000);
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchEvents(false);
    setRefreshing(false);
  };

  const handleCreateEvent = async (eventData) => {
    try {
      console.log('Creating event:', eventData);
      await createEvent(eventData);
      console.log('✅ Event created successfully');
      
      // Refresh events
      await fetchEvents(false);
      
      alert('Event created successfully!');
    } catch (err) {
      console.error('Error creating event:', err);
      alert('Failed to create event. Please try again.');
      throw err;
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!confirm('Are you sure you want to delete this event?')) {
      return;
    }

    try {
      await deleteEvent(eventId);
      console.log('✅ Event deleted successfully');
      
      // Refresh events
      await fetchEvents(false);
      
      alert('Event deleted successfully!');
    } catch (err) {
      console.error('Error deleting event:', err);
      alert('Failed to delete event. Please try again.');
    }
  };

  const handleDayClick = (day) => {
    const clickedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    setSelectedDate(clickedDate);
    setSelectedDateForEvent(clickedDate);
    setIsCreateModalOpen(true);
  };

  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    return { daysInMonth, startingDayOfWeek };
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentDate);

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const isToday = (day) => {
    const today = new Date();
    return day === today.getDate() &&
           currentDate.getMonth() === today.getMonth() &&
           currentDate.getFullYear() === today.getFullYear();
  };

  const isSelectedDate = (day) => {
    return day === selectedDate.getDate() &&
           currentDate.getMonth() === selectedDate.getMonth() &&
           currentDate.getFullYear() === selectedDate.getFullYear();
  };

  const getEventsForDate = (day) => {
    const dateToCheck = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    return calendarEvents.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === dateToCheck.toDateString();
    });
  };

  const getEventsForSelectedDate = () => {
    return calendarEvents.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === selectedDate.toDateString();
    });
  };

  const days = [];
  for (let i = 0; i < startingDayOfWeek; i++) {
    days.push(<div key={`empty-${i}`} className="h-24 p-2 bg-gray-50"></div>);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dayEvents = getEventsForDate(day);
    const isSelected = isSelectedDate(day);
    const isTodayDate = isToday(day);

    days.push(
      <div
        key={day}
        onClick={() => handleDayClick(day)}
        className={`h-24 p-2 border border-gray-200 cursor-pointer transition-colors ${
          isSelected ? 'bg-primary/10 border-primary' : 'hover:bg-gray-50 hover:border-blue-300'
        }`}
        title="Click to create event"
      >
        <div className={`text-sm font-semibold mb-1 ${
          isTodayDate ? 'bg-primary text-white w-6 h-6 flex items-center justify-center rounded-full' : 'text-gray-900'
        }`}>
          {day}
        </div>
        <div className="space-y-1">
          {dayEvents.slice(0, 2).map(event => (
            <div
              key={event.id}
              className={`text-xs p-1 rounded truncate ${
                event.type === 'meeting' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
              }`}
            >
              {event.title}
            </div>
          ))}
          {dayEvents.length > 2 && (
            <div className="text-xs text-gray-500">+{dayEvents.length - 2} more</div>
          )}
        </div>
      </div>
    );
  }

  const selectedDateEvents = getEventsForSelectedDate();

  if (loading) {
    return <LoadingSpinner message="Loading calendar..." fullPage />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={() => fetchEvents(true)} fullPage />;
  }

  return (
    <div className="p-8 bg-gray-50 h-full">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendar</h1>
          <p className="text-gray-500 mt-1">
            Manage your schedule and events ({calendarEvents.length} events)
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Event
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar View */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-2xl">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="icon" onClick={previousMonth}>
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => {
                  setCurrentDate(new Date());
                  setSelectedDate(new Date());
                }}>
                  Today
                </Button>
                <Button variant="outline" size="icon" onClick={nextMonth}>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 gap-0 mb-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="text-center text-sm font-semibold text-gray-600 p-2">
                  {day}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-0 border-t border-l border-gray-200">
              {days}
            </div>
          </CardContent>
        </Card>

        {/* Events Sidebar */}
        <div className="space-y-6">
          {/* Selected Date Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {selectedDate.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric'
                })}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedDateEvents.length > 0 ? (
                <div className="space-y-4">
                  {selectedDateEvents.map(event => (
                    <div key={event.id} className="p-4 rounded-lg border border-gray-200 bg-white hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{event.title}</h4>
                        <Badge variant={event.type === 'meeting' ? 'default' : 'secondary'}>
                          {event.type}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="w-4 h-4 mr-2" />
                          {new Date(event.date).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit',
                            hour12: true
                          })} ({event.duration})
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Users className="w-4 h-4 mr-2" />
                          {event.attendees.length} attendees
                        </div>
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <Button variant="outline" size="sm" className="w-full">
                          <Video className="w-4 h-4 mr-2" />
                          Join Meeting
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <CalendarIcon className="w-12 h-12 mx-auto mb-3" />
                  <p className="text-sm">No events scheduled</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Events */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Upcoming Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {calendarEvents
                  .filter(event => new Date(event.date) >= new Date())
                  .sort((a, b) => new Date(a.date) - new Date(b.date))
                  .slice(0, 5)
                  .map(event => (
                    <div 
                      key={event.id}
                      className="p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <div className="flex items-start justify-between mb-1">
                        <p className="text-sm font-medium text-gray-900 line-clamp-1">{event.title}</p>
                        <Badge 
                          variant="outline" 
                          className={event.type === 'meeting' ? 'bg-blue-50' : 'bg-purple-50'}
                        >
                          {event.type}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500">
                        {new Date(event.date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">This Week</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Events</span>
                  <span className="text-lg font-bold text-gray-900">{calendarEvents.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Meetings</span>
                  <span className="text-lg font-bold text-blue-600">
                    {calendarEvents.filter(e => e.type === 'meeting').length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Presentations</span>
                  <span className="text-lg font-bold text-purple-600">
                    {calendarEvents.filter(e => e.type === 'presentation').length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Event Modal */}
      <CreateEventModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateEvent}
        selectedDate={selectedDateForEvent}
      />
    </div>
  );
};

export default Calendar;

