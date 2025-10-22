import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  TrendingUp, 
  TrendingDown, 
  Mail, 
  Send, 
  Clock,
  CheckCircle2,
  AlertCircle,
  Users
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import { getUnifiedInbox } from '@/services/inbox';
import { getTodayEvents } from '@/services/calendar';
import { transformMessages, transformEvents, calculateDashboardStats } from '@/utils/dataTransform';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardStats, setDashboardStats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [todayEvents, setTodayEvents] = useState([]);

  const fetchDashboardData = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);

      // Fetch inbox and today's events in parallel
      const [inboxData, eventsData] = await Promise.all([
        getUnifiedInbox({ max_per_source: 20 }),
        getTodayEvents()
      ]);

      // Transform messages
      const allMessages = [
        ...(inboxData.priority_messages || []),
        ...(inboxData.unread_messages || [])
      ];
      
      // Deduplicate by ID
      const uniqueMessages = Array.from(
        new Map(allMessages.map(m => [m.id, m])).values()
      );
      
      const transformedMessages = transformMessages(uniqueMessages);
      
      // Transform events
      const transformedEvents = transformEvents(eventsData.normalized || []);

      // Calculate stats
      const stats = calculateDashboardStats(inboxData);

      setDashboardStats(stats);
      setMessages(transformedMessages.slice(0, 5)); // Top 5 recent
      setTodayEvents(transformedEvents);
      if (showLoader) setLoading(false);

    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err);
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(true);
    
    // Auto-refresh every 2 minutes in background (without showing loader)
    const interval = setInterval(() => fetchDashboardData(false), 120000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." fullPage />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={fetchDashboardData} fullPage />;
  }

  const StatCard = ({ title, value, change, trend, icon: Icon }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <h3 className="text-2xl font-bold mt-2">{value}</h3>
            <p className={`text-sm mt-2 flex items-center ${
              trend === 'up' ? 'text-green-600' : 'text-blue-600'
            }`}>
              {trend === 'up' ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              {change} from last week
            </p>
          </div>
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
            <Icon className="w-6 h-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const icons = [Mail, AlertCircle, Send, Clock];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-2">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {dashboardStats.map((stat, index) => (
          <StatCard 
            key={stat.title} 
            {...stat} 
            icon={icons[index]}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Messages */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-xl">Recent Messages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {messages.slice(0, 5).map((message) => (
                <div 
                  key={message.id} 
                  className="flex items-start space-x-4 p-4 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-gray-100"
                >
                  <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-medium flex-shrink-0">
                    {message.avatar}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">{message.sender}</p>
                        <p className="text-sm font-medium text-gray-700 mt-1">{message.subject}</p>
                        <p className="text-sm text-gray-500 mt-1 line-clamp-1">{message.preview}</p>
                      </div>
                      <span className="text-xs text-gray-500 ml-4">{formatDate(message.time)}</span>
                    </div>
                    {!message.read && (
                      <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Today's Schedule */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Today's Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {todayEvents.length > 0 ? (
                todayEvents.map((event) => (
                  <div key={event.id} className="p-4 rounded-lg border border-gray-200 bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{event.title}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {new Date(event.date).toLocaleTimeString('en-US', { 
                            hour: 'numeric', 
                            minute: '2-digit',
                            hour12: true 
                          })}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{event.duration}</p>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        event.type === 'meeting' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                      }`}>
                        {event.type}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>No events scheduled for today</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-xl">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <button 
              onClick={() => navigate('/inbox')}
              className="p-4 rounded-lg border-2 border-primary bg-primary text-white hover:bg-primary/90 transition-colors text-center"
            >
              <Mail className="w-6 h-6 mx-auto mb-2" />
              <p className="text-sm font-medium">View All Messages</p>
            </button>
            <button 
              onClick={() => navigate('/calendar')}
              className="p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 transition-colors text-center"
            >
              <Users className="w-6 h-6 mx-auto mb-2 text-gray-600" />
              <p className="text-sm font-medium text-gray-700">View Calendar</p>
            </button>
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 transition-colors text-center">
              <CheckCircle2 className="w-6 h-6 mx-auto mb-2 text-gray-600" />
              <p className="text-sm font-medium text-gray-700">View Tasks</p>
              <p className="text-xs text-gray-500 mt-1">Coming Soon</p>
            </button>
            <button className="p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 transition-colors text-center">
              <Clock className="w-6 h-6 mx-auto mb-2 text-gray-600" />
              <p className="text-sm font-medium text-gray-700">Time Tracking</p>
              <p className="text-xs text-gray-500 mt-1">Coming Soon</p>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

