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
  RefreshCw
} from 'lucide-react';
import { formatDate } from '@/lib/utils';
import { getAllMessages } from '@/services/inbox';
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
          <Button 
            variant="ghost" 
            size="icon"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
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

