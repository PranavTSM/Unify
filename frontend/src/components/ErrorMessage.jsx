import React from 'react';
import {AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from './ui/Button';

/**
 * Error Message Component
 * Displays error messages with optional retry action
 */
const ErrorMessage = ({ 
  error, 
  onRetry = null, 
  title = 'Something went wrong',
  fullPage = false 
}) => {
  const containerClass = fullPage
    ? 'fixed inset-0 flex items-center justify-center bg-gray-50 z-50'
    : 'flex items-center justify-center py-12';

  const errorMessage = error?.message || error?.detail || error || 'An unexpected error occurred';

  return (
    <div className={containerClass}>
      <div className="text-center max-w-md mx-auto px-4">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600 mb-6">{errorMessage}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;

