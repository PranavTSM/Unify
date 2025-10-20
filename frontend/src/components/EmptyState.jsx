import React from 'react';
import { Inbox, Calendar, Mail } from 'lucide-react';

/**
 * Empty State Component
 * Displays when no data is available
 */
const EmptyState = ({ 
  type = 'messages', 
  message = null,
  icon: CustomIcon = null 
}) => {
  // Default messages and icons based on type
  const defaults = {
    messages: {
      icon: Mail,
      message: 'No messages to display',
      subtitle: 'Your inbox is empty or all messages have been filtered out'
    },
    inbox: {
      icon: Inbox,
      message: 'Inbox is empty',
      subtitle: 'You\'re all caught up!'
    },
    calendar: {
      icon: Calendar,
      message: 'No events scheduled',
      subtitle: 'This day is free'
    },
    search: {
      icon: Mail,
      message: 'No results found',
      subtitle: 'Try adjusting your search or filters'
    }
  };

  const config = defaults[type] || defaults.messages;
  const Icon = CustomIcon || config.icon;
  const displayMessage = message || config.message;

  return (
    <div className="flex items-center justify-center py-16">
      <div className="text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{displayMessage}</h3>
        <p className="text-gray-500 text-sm">{config.subtitle}</p>
      </div>
    </div>
  );
};

export default EmptyState;

