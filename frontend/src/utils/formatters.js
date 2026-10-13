import { format, formatDistanceToNow, parseISO } from 'date-fns';

export const formatDate = (dateString, pattern = 'MMM d, yyyy') => {
  if (!dateString) return 'N/A';
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return format(date, pattern);
  } catch (e) {
    return dateString;
  }
};

export const formatTime = (dateString) => {
  return formatDate(dateString, 'h:mm a');
};

export const formatRelativeTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (e) {
    return dateString;
  }
};
