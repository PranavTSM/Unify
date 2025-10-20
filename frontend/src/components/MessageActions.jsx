/**
 * Message Actions Component
 * Quick action buttons for messages
 */

import React, { useState } from 'react';
import { 
  Mail, MailOpen, Star, Archive, Trash2, Clock, 
  MoreVertical, Check 
} from 'lucide-react';
import {
  markAsRead,
  markAsUnread,
  starMessage,
  unstarMessage,
  archiveMessage,
  deleteMessage,
  snoozeMessage
} from '../services/actions';

const MessageActions = ({ message, onActionComplete, compact = false }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showSnoozeMenu, setShowSnoozeMenu] = useState(false);

  const handleAction = async (actionFn, actionName) => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await actionFn(message.id, message.category);
      console.log(`✓ ${actionName} completed`);
      if (onActionComplete) {
        onActionComplete(actionName);
      }
    } catch (error) {
      console.error(`✗ ${actionName} failed:`, error);
      alert(`Failed to ${actionName}. Please try again.`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSnooze = async (minutes) => {
    if (isProcessing) return;
    
    setIsProcessing(true);
    try {
      await snoozeMessage(message.id, { minutes });
      console.log(`✓ Snoozed for ${minutes} minutes`);
      setShowSnoozeMenu(false);
      if (onActionComplete) {
        onActionComplete('snooze');
      }
    } catch (error) {
      console.error('✗ Snooze failed:', error);
      alert('Failed to snooze message. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-1">
        <button
          onClick={() => handleAction(message.is_read ? markAsUnread : markAsRead, 'toggle read')}
          className="p-1.5 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
          disabled={isProcessing}
          title={message.is_read ? "Mark as unread" : "Mark as read"}
        >
          {message.is_read ? <Mail className="w-4 h-4" /> : <MailOpen className="w-4 h-4" />}
        </button>
        
        <button
          onClick={() => handleAction(message.starred ? unstarMessage : starMessage, 'toggle star')}
          className={`p-1.5 rounded hover:bg-gray-100 transition-colors disabled:opacity-50 ${message.starred ? 'text-yellow-500' : ''}`}
          disabled={isProcessing}
          title={message.starred ? "Unstar" : "Star"}
        >
          <Star className={`w-4 h-4 ${message.starred ? 'fill-current' : ''}`} />
        </button>
        
        <button
          onClick={() => handleAction(archiveMessage, 'archive')}
          className="p-1.5 rounded hover:bg-gray-100 transition-colors disabled:opacity-50"
          disabled={isProcessing}
          title="Archive"
        >
          <Archive className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => handleAction(message.is_read ? markAsUnread : markAsRead, 'toggle read')}
        className="flex items-center px-3 py-1.5 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm"
        disabled={isProcessing}
      >
        {message.is_read ? <Mail className="w-4 h-4 mr-1.5" /> : <MailOpen className="w-4 h-4 mr-1.5" />}
        {message.is_read ? 'Mark Unread' : 'Mark Read'}
      </button>
      
      <button
        onClick={() => handleAction(message.starred ? unstarMessage : starMessage, 'toggle star')}
        className={`flex items-center px-3 py-1.5 bg-white border rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm ${
          message.starred ? 'border-yellow-500 text-yellow-600' : 'border-gray-300'
        }`}
        disabled={isProcessing}
      >
        <Star className={`w-4 h-4 mr-1.5 ${message.starred ? 'fill-current' : ''}`} />
        {message.starred ? 'Starred' : 'Star'}
      </button>
      
      <div className="relative">
        <button
          onClick={() => setShowSnoozeMenu(!showSnoozeMenu)}
          className="flex items-center px-3 py-1.5 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm"
        >
          <Clock className="w-4 h-4 mr-1.5" />
          Snooze
        </button>
        
        {showSnoozeMenu && (
          <div className="absolute top-full mt-1 right-0 bg-white border border-gray-200 rounded-md shadow-lg z-10 min-w-[160px]">
            <button
              onClick={() => handleSnooze(60)}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm"
            >
              1 hour
            </button>
            <button
              onClick={() => handleSnooze(240)}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm"
            >
              4 hours
            </button>
            <button
              onClick={() => handleSnooze(1440)}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 text-sm"
            >
              Tomorrow
            </button>
          </div>
        )}
      </div>
      
      <button
        onClick={() => {
          if (confirm('Are you sure you want to archive this message?')) {
            handleAction(archiveMessage, 'archive');
          }
        }}
        className="flex items-center px-3 py-1.5 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 text-sm"
        disabled={isProcessing}
      >
        <Archive className="w-4 h-4 mr-1.5" />
        Archive
      </button>
      
      <button
        onClick={() => {
          if (confirm('Are you sure you want to delete this message?')) {
            handleAction(deleteMessage, 'delete');
          }
        }}
        className="flex items-center px-3 py-1.5 bg-white border border-red-300 text-red-600 rounded-md hover:bg-red-50 transition-colors disabled:opacity-50 text-sm"
        disabled={isProcessing}
      >
        <Trash2 className="w-4 h-4 mr-1.5" />
        Delete
      </button>
    </div>
  );
};

export default MessageActions;

