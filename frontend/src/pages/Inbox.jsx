import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  Search, 
  Mail, 
  Paperclip, 
  Reply, 
  Forward, 
  MoreVertical,
  Archive,
  Trash2,
  Star,
  RefreshCw,
  Sparkles,
  X,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import { getAllMessages, getAISummaryBySource } from '@/services/inbox';
import { transformMessages } from '@/utils/dataTransform';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';
import EmptyState from '@/components/EmptyState';

const Inbox = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [allMessages, setAllMessages] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [expandedSources, setExpandedSources] = useState({ gmail: true, outlook: true, teams: true });
  const navigate = useNavigate();

  const filters = ['All', 'Gmail', 'Teams', 'Outlook'];

  // Fetch messages from API
  const fetchMessages = async (showLoader = true) => {
    try {
      console.log('🔄 Inbox: Starting fetch messages...');
      if (showLoader) setLoading(true);
      setError(null);

      console.log('📡 Inbox: Calling getAllMessages instead of getUnifiedInbox...');
      // Use getAllMessages to get ALL messages (not just priority/unread)
      const messagesData = await getAllMessages({ max_per_source: 20 });
      console.log('✅ Inbox: Got all messages:', messagesData);

      // Get all normalized messages
      const combined = messagesData.normalized || [];
      console.log('📦 Inbox: All messages count:', combined.length);

      // Deduplicate by ID
      const uniqueMessages = Array.from(
        new Map(combined.map(m => [m.id, m])).values()
      );
      console.log('✨ Inbox: Unique messages after dedup:', uniqueMessages.length);

      const transformed = transformMessages(uniqueMessages);
      console.log('🔄 Inbox: Transformed messages:', transformed.length);
      
      // Debug: Count by category
      const categoryCount = {};
      transformed.forEach(msg => {
        const cat = msg.category || 'Unknown';
        categoryCount[cat] = (categoryCount[cat] || 0) + 1;
      });
      console.log('📊 Inbox: Messages by category:', categoryCount);
      console.log('📋 Inbox: Sample transformed messages:', transformed.slice(0, 3));
      
      setAllMessages(transformed);
      
      // Auto-select first message if none selected
      if (!selectedMessage && transformed.length > 0) {
        setSelectedMessage(transformed[0]);
      }
      
      setLoading(false);
      console.log('✅ Inbox: Fetch complete!');
    } catch (err) {
      console.error('❌ Inbox: Error fetching messages:', err);
      console.error('❌ Error details:', {
        message: err.message,
        response: err.response,
        stack: err.stack
      });
      setError(err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchMessages(false);
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchMessages(false);
    setRefreshing(false);
  };

  const handleAISummary = async () => {
    try {
      setSummaryLoading(true);
      setShowSummary(true);
      const data = await getAISummaryBySource({ max_per_source: 20, mode: 'executive' });
      setSummaryData(data);
    } catch (err) {
      console.error('Error fetching AI summary:', err);
      setError(err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const toggleSourceExpanded = (source) => {
    setExpandedSources(prev => ({
      ...prev,
      [source]: !prev[source]
    }));
  };

  const getSourceIcon = (source) => {
    const icons = {
      gmail: '📧',
      outlook: '📨',
      teams: '💬'
    };
    return icons[source] || '📬';
  };

  const parseSummary = (summary) => {
    if (!summary) return { overview: '', bullets: [] };
    
    const lines = summary.split('\n').filter(line => line.trim());
    const overview = lines[0]?.replace(/^Overview:\s*/i, '').trim() || '';
    
    const bullets = lines
      .slice(1)
      .filter(line => line.match(/^[•\-\*\d\.]/))
      .map(line => line.replace(/^[•\-\*\d\.\s]+/, '').trim())
      .filter(Boolean);
    
    return { overview, bullets: bullets.length > 0 ? bullets : [] };
  };

  // Filter messages by category and search
  const filteredMessages = allMessages.filter(m => {
    // Filter by category (case-insensitive)
    if (activeFilter !== 'All' && m.category?.toLowerCase() !== activeFilter.toLowerCase()) {
      return false;
    }
    
    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      return (
        m.subject?.toLowerCase().includes(query) ||
        m.sender?.toLowerCase().includes(query) ||
        m.content?.toLowerCase().includes(query) ||
        m.preview?.toLowerCase().includes(query)
      );
    }
    
    return true;
  });

  // Debug filtered messages
  React.useEffect(() => {
    if (allMessages.length > 0) {
      console.log('🔍 Filter Debug:', {
        activeFilter,
        totalMessages: allMessages.length,
        filteredCount: filteredMessages.length,
        byCategory: {
          All: allMessages.length,
          Gmail: allMessages.filter(m => m.category?.toLowerCase() === 'gmail').length,
          Outlook: allMessages.filter(m => m.category?.toLowerCase() === 'outlook').length,
          Teams: allMessages.filter(m => m.category?.toLowerCase() === 'teams').length
        }
      });
    }
  }, [activeFilter, allMessages, filteredMessages.length]);

  const handleViewDetails = () => {
    navigate(`/details/${selectedMessage.id}`);
  };

  if (loading) {
    return <LoadingSpinner message="Loading inbox..." fullPage />;
  }

  if (error) {
    return <ErrorMessage error={error} onRetry={() => fetchMessages(true)} fullPage />;
  }

  return (
    <div className="flex h-full bg-white">
      {/* Messages List */}
      <div className="w-96 border-r border-gray-200 flex flex-col">
        {/* Search and Filters */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input 
              placeholder="Search messages..." 
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex space-x-2">
            {filters.map(filter => (
              <Button
                key={filter}
                variant={activeFilter === filter ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter(filter)}
                className="flex-1"
              >
                {filter}
              </Button>
            ))}
          </div>
        </div>

        {/* Message List Header */}
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">
            Inbox ({filteredMessages.length})
          </h2>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleAISummary}
              disabled={summaryLoading}
              className="bg-gradient-to-r from-purple-500 to-blue-500 text-white border-0 hover:from-purple-600 hover:to-blue-600"
            >
              {summaryLoading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4 mr-2" />
              )}
              AI Summary
            </Button>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {filteredMessages.length === 0 ? (
            <EmptyState type={searchQuery ? 'search' : 'inbox'} />
          ) : (
            filteredMessages.map((message) => (
            <div
              key={message.id}
              onClick={() => setSelectedMessage(message)}
              className={`p-4 border-b border-gray-200 cursor-pointer transition-colors ${
                selectedMessage?.id === message.id
                  ? 'bg-blue-50 border-l-4 border-l-primary'
                  : 'hover:bg-gray-50'
              } ${!message.read ? 'bg-blue-50/30' : ''}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-medium text-sm">
                    {message.avatar}
                  </div>
                  <div>
                    <p className={`text-sm font-semibold text-gray-900 ${!message.read ? 'font-bold' : ''}`}>
                      {message.sender}
                    </p>
                    <p className="text-xs text-gray-500">{formatDate(message.time)}</p>
                  </div>
                </div>
                {!message.read && (
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                )}
              </div>
              <p className={`text-sm font-medium text-gray-900 mb-1 ${!message.read ? 'font-semibold' : ''}`}>
                {message.subject}
              </p>
              <p className="text-sm text-gray-600 line-clamp-2">{message.preview}</p>
              <div className="flex items-center mt-2 space-x-2">
                {message.hasAttachment && (
                  <Badge variant="outline" className="text-xs">
                    <Paperclip className="w-3 h-3 mr-1" />
                    Attachment
                  </Badge>
                )}
                <Badge variant="secondary" className="text-xs">
                  {message.category}
                </Badge>
              </div>
            </div>
          )))}
        </div>

        {/* Compose Button */}
        <div className="p-4 border-t border-gray-200">
          <Button className="w-full">
            <Mail className="w-4 h-4 mr-2" />
            Compose
          </Button>
        </div>
      </div>

      {/* AI Summary Panel */}
      {showSummary && (
        <div className="w-96 border-l border-gray-200 flex flex-col bg-white overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-purple-500 to-blue-500 text-white flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <h3 className="font-semibold">AI Summary</h3>
            </div>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => setShowSummary(false)}
              className="text-white hover:bg-white/20"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {summaryLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <RefreshCw className="w-8 h-8 animate-spin text-purple-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Generating AI summaries...</p>
                </div>
              </div>
            ) : summaryData ? (
              <div className="space-y-4">
                <div className="text-sm text-gray-600 mb-4">
                  <p className="font-medium">Total: {summaryData.total_messages} messages</p>
                  <p className="text-xs text-gray-500">20 messages per source</p>
                </div>

                {['gmail', 'outlook', 'teams'].map(source => {
                  const sourceData = summaryData.summaries_by_source?.[source];
                  if (!sourceData) return null;

                  const messageCount = sourceData.message_count || 0;
                  const isExpanded = expandedSources[source];

                  return (
                    <div key={source} className="border border-gray-200 rounded-lg overflow-hidden">
                      <button
                        onClick={() => toggleSourceExpanded(source)}
                        className="w-full p-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition-colors"
                      >
                        <div className="flex items-center space-x-2">
                          <span className="text-xl">{getSourceIcon(source)}</span>
                          <span className="font-semibold text-gray-900 capitalize">{source}</span>
                          <Badge variant="secondary" className="text-xs">
                            {messageCount}
                          </Badge>
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-gray-500" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-500" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="p-4 bg-white">
                          {messageCount === 0 ? (
                            <p className="text-sm text-gray-500 italic">{sourceData.summary}</p>
                          ) : (
                            <>
                              {(() => {
                                const parsed = parseSummary(sourceData.summary);
                                return (
                                  <>
                                    {/* Overview */}
                                    {parsed.overview && (
                                      <div className="mb-4 p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-100">
                                        <p className="text-sm font-medium text-gray-800 leading-relaxed">
                                          {parsed.overview}
                                        </p>
                                      </div>
                                    )}

                                    {/* Bullet Points */}
                                    {parsed.bullets && parsed.bullets.length > 0 && (
                                      <div className="space-y-2 mb-4">
                                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                          Key Points
                                        </p>
                                        {parsed.bullets.map((bullet, idx) => (
                                          <div 
                                            key={idx} 
                                            className="flex items-start space-x-3 p-2 rounded hover:bg-gray-50 transition-colors"
                                          >
                                            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center text-xs font-bold mt-0.5">
                                              {idx + 1}
                                            </span>
                                            <span className="text-sm text-gray-700 flex-1 leading-relaxed">
                                              {bullet}
                                            </span>
                                          </div>
                                        ))}
                                      </div>
                                    )}

                                    {/* Recent Messages Preview */}
                                    {sourceData.messages && sourceData.messages.length > 0 && (
                                      <div className="pt-3 border-t border-gray-100">
                                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                          Recent Messages
                                        </p>
                                        <div className="space-y-2">
                                          {sourceData.messages.slice(0, 3).map((msg, idx) => (
                                            <div 
                                              key={idx} 
                                              className="p-2 bg-gray-50 rounded-lg border border-gray-100 hover:border-purple-200 hover:bg-purple-50/30 transition-all cursor-pointer"
                                            >
                                              <div className="flex items-start justify-between mb-1">
                                                <p className="text-xs font-semibold text-gray-900 flex-1 truncate">
                                                  {msg.subject}
                                                </p>
                                                {!msg.is_read && (
                                                  <span className="ml-2 w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1"></span>
                                                )}
                                              </div>
                                              <p className="text-xs text-gray-500 truncate">
                                                {msg.sender}
                                              </p>
                                              {msg.importance_score >= 0.7 && (
                                                <Badge variant="destructive" className="text-xs mt-1">
                                                  High Priority
                                                </Badge>
                                              )}
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </>
                                );
                              })()}
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Click "AI Summary" to generate summaries</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Message Preview */}
      <div className="flex-1 flex flex-col">
        {selectedMessage ? (
          <>
            {/* Message Header */}
            <div className="p-6 border-b border-gray-200 bg-white">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center font-medium text-lg">
                    {selectedMessage.avatar}
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-1">
                      {selectedMessage.sender}
                    </h2>
                    <p className="text-lg text-gray-700 font-medium mb-2">
                      {selectedMessage.subject}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(selectedMessage.time).toLocaleString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="icon">
                  <MoreVertical className="w-5 h-5" />
                </Button>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={handleViewDetails}>
                  <Mail className="w-4 h-4 mr-2" />
                  View Full Details
                </Button>
                <Button variant="outline" size="sm">
                  <Reply className="w-4 h-4 mr-2" />
                  Reply
                </Button>
                <Button variant="outline" size="sm">
                  <Forward className="w-4 h-4 mr-2" />
                  Forward
                </Button>
                <div className="flex-1"></div>
                <Button variant="ghost" size="icon">
                  <Star className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Archive className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Message Content */}
            <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
              <div className="max-w-3xl bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {selectedMessage.content}
                </p>
              </div>
            </div>

            {/* Reply Box */}
            <div className="p-4 border-t border-gray-200 bg-white">
              <div className="flex items-center space-x-2">
                <Input 
                  placeholder="Reply to Alice Johnson..." 
                  className="flex-1"
                />
                <Button variant="ghost" size="icon">
                  <Paperclip className="w-4 h-4" />
                </Button>
                <Button>
                  Send
                </Button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Mail className="w-16 h-16 mx-auto mb-4" />
              <p className="text-lg">Select a message to read</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Inbox;

