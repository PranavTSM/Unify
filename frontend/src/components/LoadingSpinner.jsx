import React from 'react';
import { Loader2 } from 'lucide-react';

/**
 * Loading Spinner Component
 * Displays a centered loading indicator
 */
const LoadingSpinner = ({ message = 'Loading...', fullPage = false }) => {
  const containerClass = fullPage 
    ? 'fixed inset-0 flex items-center justify-center bg-white/80 z-50'
    : 'flex items-center justify-center py-12';

  return (
    <div className={containerClass}>
      <div className="text-center">
        <Loader2 className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
        <p className="text-gray-600 font-medium">{message}</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;

