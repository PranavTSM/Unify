/**
 * Create Event Modal Component
 * Modal for creating new calendar events
 */

import React, { useState } from 'react';
import { X, Calendar, Clock, MapPin, Users, FileText } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const CreateEventModal = ({ isOpen, onClose, onSubmit, selectedDate = null }) => {
  const [formData, setFormData] = useState({
    summary: '',
    description: '',
    location: '',
    start: selectedDate ? formatDateForInput(selectedDate, '09:00') : '',
    end: selectedDate ? formatDateForInput(selectedDate, '10:00') : '',
    attendees: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function formatDateForInput(date, time = '09:00') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}T${time}`;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.summary.trim()) {
      setError('Event title is required');
      return;
    }

    if (!formData.start || !formData.end) {
      setError('Start and end times are required');
      return;
    }

    if (new Date(formData.start) >= new Date(formData.end)) {
      setError('End time must be after start time');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const eventData = {
        summary: formData.summary,
        description: formData.description,
        location: formData.location,
        start: new Date(formData.start).toISOString(),
        end: new Date(formData.end).toISOString(),
        attendees: formData.attendees
          .split(',')
          .map(email => email.trim())
          .filter(email => email.length > 0),
      };

      await onSubmit(eventData);
      
      // Reset form
      setFormData({
        summary: '',
        description: '',
        location: '',
        start: '',
        end: '',
        attendees: '',
      });
      
      onClose();
    } catch (err) {
      console.error('Error creating event:', err);
      setError(err.message || 'Failed to create event');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">Create New Event</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Event Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-2" />
              Event Title *
            </label>
            <Input
              type="text"
              name="summary"
              value={formData.summary}
              onChange={handleChange}
              placeholder="e.g., Team Meeting"
              required
              className="w-full"
            />
          </div>

          {/* Start Time */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-2" />
                Start Time *
              </label>
              <Input
                type="datetime-local"
                name="start"
                value={formData.start}
                onChange={handleChange}
                required
                className="w-full"
              />
            </div>

            {/* End Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-2" />
                End Time *
              </label>
              <Input
                type="datetime-local"
                name="end"
                value={formData.end}
                onChange={handleChange}
                required
                className="w-full"
              />
            </div>
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="w-4 h-4 inline mr-2" />
              Location
            </label>
            <Input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="e.g., Conference Room A, or Zoom link"
              className="w-full"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FileText className="w-4 h-4 inline mr-2" />
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Add meeting agenda, notes, or details..."
              rows="4"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Attendees */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Users className="w-4 h-4 inline mr-2" />
              Attendees
            </label>
            <Input
              type="text"
              name="attendees"
              value={formData.attendees}
              onChange={handleChange}
              placeholder="email1@example.com, email2@example.com"
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple emails with commas</p>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isSubmitting ? 'Creating...' : 'Create Event'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEventModal;

