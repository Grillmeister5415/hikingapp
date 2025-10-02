export function durationToSeconds(duration) {
  if (duration === null || duration === undefined) return 0;
  if (typeof duration === 'number' && !Number.isNaN(duration)) {
    return duration;
  }

  if (typeof duration !== 'string') {
    return 0;
  }

  const value = duration.trim();
  if (!value) return 0;

  const negative = value.startsWith('-');
  const normalized = negative ? value.slice(1).trim() : value;
  let days = 0;
  let hours = 0;
  let minutes = 0;
  let seconds = 0;
  let match;

  // Matches formats like "2 days, 03:15:00"
  if ((match = normalized.match(/^(\d+)\s+day[s]?,\s*(\d{1,2}):(\d{2}):(\d{2})$/i))) {
    [, days, hours, minutes, seconds] = match;
  }
  // Matches formats like "1 00:00:00" (Postgres interval short form)
  else if ((match = normalized.match(/^(\d+)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?$/))) {
    [, days, hours, minutes, seconds = '0'] = match;
  }
  // Matches standard HH:MM or HH:MM:SS strings
  else if ((match = normalized.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/))) {
    [, hours, minutes, seconds = '0'] = match;
  } else {
    return 0;
  }

  const totalSeconds = ((Number(days) * 24 + Number(hours)) * 60 + Number(minutes)) * 60 + Number(seconds);
  return negative ? -totalSeconds : totalSeconds;
}

export function formatDurationHoursMinutes(duration) {
  const totalSeconds = durationToSeconds(duration);
  const sign = totalSeconds < 0 ? '-' : '';
  const absoluteSeconds = Math.abs(totalSeconds);

  const totalHours = Math.floor(absoluteSeconds / 3600);
  const minutes = Math.floor((absoluteSeconds % 3600) / 60);

  return `${sign}${totalHours}h ${minutes}m`;
}

export function formatDurationFromSeconds(seconds) {
  return formatDurationHoursMinutes(seconds);
}
