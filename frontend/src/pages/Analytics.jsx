/**
 * Analytics Dashboard Page
 * Displays inbox statistics and insights
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { 
  TrendingUp, 
  Mail, 
  BarChart3, 
  PieChart, 
  Users,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { getAnalytics } from '../services/actions';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const Analytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalytics = async (showLoader = true) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);
      
      const data = await getAnalytics();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    
    // Auto-refresh every 2 minutes
    const interval = setInterval(() => {
      fetchAnalytics(false);
    }, 120000);
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAnalytics(false);
  };

  if (loading) {
    return <LoadingSpinner message="Loading analytics..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={() => fetchAnalytics()} />;
  }

  const {
    total_messages = 0,
    unread_count = 0,
    by_source = {},
    by_priority = {},
    read_percentage = 0
  } = stats || {};

  const sourceData = Object.entries(by_source).map(([source, count]) => ({
    name: source,
    value: count,
    percentage: ((count / total_messages) * 100).toFixed(1)
  }));

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Insights into your unified inbox</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{total_messages}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all sources
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unread</CardTitle>
            <AlertCircle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{unread_count}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {((unread_count / total_messages) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Read Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{read_percentage.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Messages processed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Priority</CardTitle>
            <TrendingUp className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{by_priority.high || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Requires attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Source */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Messages by Source
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {sourceData.map((item, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium capitalize">{item.name}</span>
                    <span className="text-sm text-gray-600">{item.value} ({item.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* By Priority */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="w-5 h-5 mr-2" />
              Priority Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-red-600">High Priority</span>
                  <span className="text-sm text-gray-600">{by_priority.high || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-red-600 h-2 rounded-full"
                    style={{ 
                      width: `${((by_priority.high || 0) / total_messages * 100).toFixed(1)}%` 
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-yellow-600">Medium Priority</span>
                  <span className="text-sm text-gray-600">{by_priority.medium || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-600 h-2 rounded-full"
                    style={{ 
                      width: `${((by_priority.medium || 0) / total_messages * 100).toFixed(1)}%` 
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-600">Low Priority</span>
                  <span className="text-sm text-gray-600">{by_priority.low || 0}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ 
                      width: `${((by_priority.low || 0) / total_messages * 100).toFixed(1)}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Insights & Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {unread_count > 20 && (
              <div className="flex items-start p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-900">High Unread Count</p>
                  <p className="text-sm text-yellow-700">
                    You have {unread_count} unread messages. Consider using bulk actions to process them efficiently.
                  </p>
                </div>
              </div>
            )}

            {by_priority.high > 0 && (
              <div className="flex items-start p-3 bg-red-50 border border-red-200 rounded-lg">
                <TrendingUp className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">High Priority Items</p>
                  <p className="text-sm text-red-700">
                    You have {by_priority.high} high priority messages requiring attention.
                  </p>
                </div>
              </div>
            )}

            {read_percentage > 80 && (
              <div className="flex items-start p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5" />
                <div>
                  <p className="font-medium text-green-900">Great Job!</p>
                  <p className="text-sm text-green-700">
                    You're staying on top of your inbox with a {read_percentage.toFixed(1)}% read rate.
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;

