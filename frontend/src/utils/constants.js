export const ACTIVITY_STATUS = {
  MOTION_DETECTED: 'MOTION_DETECTED',
  NO_MOTION: 'NO_MOTION',
  INACTIVITY_THRESHOLD_EXCEEDED: 'INACTIVITY_THRESHOLD_EXCEEDED',
};

export const METRIC_TYPES = [
  { id: 'heart_rate', label: 'Heart Rate', unit: 'BPM', icon: 'Heart' },
  { id: 'steps', label: 'Daily Steps', unit: 'steps', icon: 'Footprints' },
  { id: 'sleep', label: 'Sleep Quality', unit: 'hours', icon: 'Moon' },
  { id: 'spo2', label: 'Blood Oxygen', unit: '%', icon: 'Activity' },
];

export const SOS_STATUS = {
  OPEN: 'OPEN',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  RESOLVED: 'RESOLVED',
};
