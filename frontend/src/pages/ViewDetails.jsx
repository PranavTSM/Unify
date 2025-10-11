import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Printer,
  Lightbulb,
  TrendingUp,
  AlertCircle,
  FileText,
  BarChart3,
  Brain,
  CheckCircle2,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { getAllMessages } from '@/services/inbox';
import { getMessageInsights } from '@/services/ai';
import { transformMessages } from '@/utils/dataTransform';
import LoadingSpinner from '@/components/LoadingSpinner';
import ErrorMessage from '@/components/ErrorMessage';

const ViewDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loadingAI, setLoadingAI] = useState(false);
  const [aiError, setAiError] = useState(null);

  // Fetch message details
  const fetchMessage = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get message from location state first (passed from Inbox)
      if (location.state?.message) {
        console.log('✅ Got message from location.state:', location.state.message);
        setSelectedMessage(location.state.message);
        setLoading(false);
        return;
      }

      // Fallback: Fetch from API if no state
      console.log('📡 Fetching message from API, ID:', id);
      const messagesData = await getAllMessages({ max_per_source: 100 });
      const transformed = transformMessages(messagesData.normalized || []);
      
      const message = transformed.find(m => m.id === id);
      
      if (!message) {
        console.error('❌ Message not found, ID:', id);
        setError({ message: 'Message not found' });
        setLoading(false);
        return;
      }

      console.log('✅ Found message:', message);
      setSelectedMessage(message);
      setLoading(false);
      
      // DON'T auto-fetch AI - let user trigger it manually to avoid freezing
      // fetchAIInsights(id);
      
    } catch (err) {
      console.error('❌ Error fetching message:', err);
      setError(err);
      setLoading(false);
    }
  };

  // Fetch AI-powered insights
  const fetchAIInsights = async (messageId) => {
    try {
      setLoadingAI(true);
      setAiError(null);

      const insights = await getMessageInsights(messageId);
      setAiInsights(insights);
      setLoadingAI(false);

    } catch (err) {
      console.error('Error fetching AI insights:', err);
      setAiError(err);
      setLoadingAI(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchMessage();
    }
  }, [id]);

  // Manual AI trigger function
  const handleGenerateAI = async () => {
    if (!id) return;
    fetchAIInsights(id);
  };

  if (loading) {
    return <LoadingSpinner message="Loading message details..." fullPage />;
  }

  if (error || !selectedMessage) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Message Not Found</h2>
          <p className="text-gray-500 mb-4">The message you're looking for doesn't exist.</p>
          <Button onClick={() => navigate('/inbox')}>
            Back to Inbox
          </Button>
        </div>
      </div>
    );
  }

  // Calculate priority level from importance score and context
  const getPriorityLevel = (score) => {
    if (score >= 0.75) return { 
      label: 'High Priority', 
      color: 'text-red-600', 
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    };
    if (score >= 0.5) return { 
      label: 'Medium Priority', 
      color: 'text-yellow-600', 
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    };
    return { 
      label: 'Low Priority', 
      color: 'text-blue-600', 
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    };
  };

  const priority = getPriorityLevel(selectedMessage.importance_score || 0.5);
  
  // Determine context type from source
  const getContextType = (source) => {
    if (source?.toLowerCase().includes('teams')) return 'Teams Chat';
    if (source?.toLowerCase().includes('outlook')) return 'Outlook Email';
    if (source?.toLowerCase().includes('gmail')) return 'Gmail Email';
    return 'Message';
  };

  const insights = [
    {
      title: 'Priority Level',
      value: priority.label,
      description: `Score: ${((selectedMessage.importance_score || 0.5) * 100).toFixed(0)}%`,
      icon: TrendingUp,
      color: priority.color,
      bgColor: priority.bgColor
    },
    {
      title: 'Message Type',
      value: getContextType(selectedMessage.category),
      description: selectedMessage.category || 'Unknown',
      icon: Brain,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Action Required',
      value: aiInsights?.actions?.length > 0 ? `${aiInsights.actions.length} Actions` : 'None',
      description: aiInsights ? 'AI Analyzed' : 'Not analyzed',
      icon: CheckCircle2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Attachments',
      value: selectedMessage.attachments?.length || 0,
      description: selectedMessage.attachments?.length > 0 ? 'Has files' : 'No files',
      icon: BarChart3,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
  ];

  // Use AI-generated summary or fallback
  const summary = aiInsights?.summary || 
    `Message from ${selectedMessage.sender} regarding ${selectedMessage.subject}`;

  // Use AI-generated key points or fallback
  const keyPoints = aiInsights?.bullets || [
    'Message details loading...'
  ];

  // Use AI-generated actions or fallback
  const suggestedActions = aiInsights?.actions || [];

  return (
    <div className="p-8 bg-gray-50 min-h-full">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => navigate('/inbox')}
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Message Details</h1>
            <p className="text-gray-500 mt-1">Comprehensive analysis and insights</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Printer className="w-4 h-4 mr-2" />
            Print
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Full Message */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl mb-2">{selectedMessage.subject}</CardTitle>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="font-medium">From: {selectedMessage.sender}</span>
                    <span>•</span>
                    <span>
                      {new Date(selectedMessage.time).toLocaleString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant={selectedMessage.read ? 'secondary' : 'default'}>
                    {selectedMessage.read ? 'Read' : 'Unread'}
                  </Badge>
                  <Badge variant="outline">{selectedMessage.category}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {selectedMessage.content}
                </p>
              </div>
              {selectedMessage.hasAttachment && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-8 h-8 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">Meeting_Notes.pdf</p>
                      <p className="text-sm text-gray-500">245 KB</p>
                    </div>
                    <Button variant="outline" size="sm" className="ml-auto">
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Summarization */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-primary" />
                  <CardTitle>AI-Powered Summary</CardTitle>
                </div>
                <div className="flex items-center space-x-2">
                  {loadingAI && (
                    <Loader2 className="w-4 h-4 text-primary animate-spin" />
                  )}
                  {!aiInsights && !loadingAI && (
                    <Button 
                      onClick={handleGenerateAI} 
                      size="sm"
                      variant="outline"
                    >
                      <Brain className="w-4 h-4 mr-2" />
                      Generate AI Insights
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {!aiInsights && !loadingAI && !aiError ? (
                <div className="text-center py-12 text-gray-400 border-2 border-dashed border-gray-200 rounded-lg">
                  <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium text-gray-600 mb-2">AI Insights Available</p>
                  <p className="text-sm mb-4">Click "Generate AI Insights" to get summary and action items</p>
                  <Button onClick={handleGenerateAI} variant="default">
                    <Brain className="w-4 h-4 mr-2" />
                    Generate Now
                  </Button>
                </div>
              ) : loadingAI ? (
                <div className="text-center py-8 text-gray-500">
                  <Loader2 className="w-8 h-8 mx-auto mb-3 text-primary animate-spin" />
                  <p>Generating AI summary...</p>
                  <p className="text-xs mt-2 text-gray-400">This may take 2-3 seconds</p>
                </div>
              ) : aiError ? (
                <div className="text-center py-8 text-gray-500">
                  <AlertCircle className="w-8 h-8 mx-auto mb-3 text-yellow-500" />
                  <p>AI features unavailable</p>
                  <p className="text-xs mt-2">LLM service may not be running</p>
                  <Button onClick={handleGenerateAI} variant="outline" size="sm" className="mt-4">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                </div>
              ) : (
                <>
                  <p className="text-gray-700 leading-relaxed mb-4">{summary}</p>
                  {keyPoints && keyPoints.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-900 flex items-center">
                        <Lightbulb className="w-4 h-4 mr-2 text-yellow-500" />
                        Key Points Extracted
                      </h4>
                      <ul className="space-y-2">
                        {keyPoints.map((point, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span className="text-gray-700 text-sm">{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Suggested Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Suggested Actions</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingAI ? (
                <div className="text-center py-8 text-gray-500">
                  <Loader2 className="w-6 h-6 mx-auto mb-2 text-primary animate-spin" />
                  <p className="text-sm">Analyzing message...</p>
                </div>
              ) : suggestedActions && suggestedActions.length > 0 ? (
                <div className="space-y-3">
                  {suggestedActions.map((action, index) => (
                    <div
                      key={index}
                      className="p-4 rounded-lg border-2 border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900 text-sm">
                          {action.description}
                        </h4>
                        <Badge 
                          variant={
                            action.priority === 'high' ? 'destructive' : 
                            action.priority === 'medium' ? 'default' : 'secondary'
                          }
                          className="text-xs"
                        >
                          {action.priority}
                        </Badge>
                      </div>
                      <div className="space-y-1 text-xs text-gray-600">
                        {action.due_date && (
                          <p>📅 Due: {new Date(action.due_date).toLocaleDateString()}</p>
                        )}
                        {action.assignee && (
                          <p>👤 Assignee: {action.assignee}</p>
                        )}
                        {action.category && (
                          <p>🏷️ {action.category}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <CheckCircle2 className="w-8 h-8 mx-auto mb-2" />
                  <p className="text-sm">No action items detected</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Insights Sidebar */}
        <div className="space-y-6">
          {/* Quick Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.map((insight, index) => {
                  const Icon = insight.icon;
                  return (
                    <div 
                      key={index}
                      className={`p-4 rounded-lg ${insight.bgColor} border-2 ${insight.borderColor || 'border-transparent'}`}
                    >
                      <div className="flex items-start space-x-3">
                        <Icon className={`w-5 h-5 ${insight.color} mt-1`} />
                        <div className="flex-1">
                          <p className="text-xs text-gray-600 font-medium mb-1">{insight.title}</p>
                          <p className={`text-lg font-bold ${insight.color}`}>{insight.value}</p>
                          {insight.description && (
                            <p className="text-xs text-gray-500 mt-1">{insight.description}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Message Metadata */}
          <Card>
            <CardHeader>
              <CardTitle>Message Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500 font-medium">Category</p>
                  <p className="text-sm font-semibold text-gray-900 mt-1">{selectedMessage.category}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Received</p>
                  <p className="text-sm font-semibold text-gray-900 mt-1">
                    {new Date(selectedMessage.time).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Attachments</p>
                  <p className="text-sm font-semibold text-gray-900 mt-1">
                    {selectedMessage.hasAttachment ? '1 file' : 'None'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Thread ID</p>
                  <p className="text-sm font-mono text-gray-600 mt-1">#{selectedMessage.id.toString().padStart(6, '0')}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Related Messages */}
          <Card>
            <CardHeader>
              <CardTitle>Related Messages</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-400">
                <FileText className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">Related messages feature coming soon</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ViewDetails;

