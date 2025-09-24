/**
 * Utility functions for processing text content with @mentions and URLs
 */

/**
 * Processes text to make @mentions and URLs clickable
 * @param {string} text - The raw text to process
 * @param {Array} users - Array of user objects to match @mentions against
 * @returns {string} HTML string with clickable links
 */
export function processTextLinks(text, users = []) {
  if (!text) return '';

  let processedText = text;

  // Create a map of usernames to user IDs for quick lookup
  const userMap = {};
  users.forEach(user => {
    userMap[user.username.toLowerCase()] = user.id;
  });

  // Process @mentions - match @username pattern
  processedText = processedText.replace(/@([a-zA-Z0-9_]+)/g, (match, username) => {
    const userId = userMap[username.toLowerCase()];
    if (userId) {
      return `<a href="#/dashboard/${userId}" class="mention-link">@${username}</a>`;
    }
    return match; // Return unprocessed if user not found
  });

  // Process URLs - match http/https URLs
  processedText = processedText.replace(/(https?:\/\/[^\s]+)/g, (match) => {
    return `<a href="${match}" target="_blank" rel="noopener noreferrer" class="external-link">${match}</a>`;
  });

  return processedText;
}

/**
 * Gets all users that are relevant to a trip (creator + participants)
 * @param {Object} trip - Trip object with creator and participants
 * @returns {Array} Array of user objects
 */
export function getTripUsers(trip) {
  const users = [];

  if (trip.creator) {
    users.push(trip.creator);
  }

  if (trip.participants) {
    users.push(...trip.participants);
  }

  return users;
}

/**
 * Gets all users that are relevant to a stage (creator + trip participants)
 * @param {Object} stage - Stage object with creator
 * @param {Object} trip - Trip object with participants
 * @returns {Array} Array of user objects
 */
export function getStageUsers(stage, trip) {
  const users = [];

  if (stage.creator) {
    users.push(stage.creator);
  }

  if (trip) {
    if (trip.creator) {
      users.push(trip.creator);
    }
    if (trip.participants) {
      users.push(...trip.participants);
    }
  }

  // Remove duplicates based on user ID
  const uniqueUsers = users.filter((user, index, self) =>
    index === self.findIndex(u => u.id === user.id)
  );

  return uniqueUsers;
}