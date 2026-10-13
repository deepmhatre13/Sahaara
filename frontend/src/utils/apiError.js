/**
 * Turn an unknown thrown value (axios error, Error, string) into a short,
 * user-facing message. Handles the status codes the auth screens can hit:
 *
 *   401/403 -> authentication error
 *   409     -> conflict (e.g. email already registered)
 *   422     -> validation error (Pydantic returns an array of detail objects)
 *   404     -> not found
 *   5xx     -> server error
 *   no response -> backend unavailable / network error
 *
 * Never returns raw Axios/fetch objects.
 */
const DEFAULT_MESSAGES = {
  400: 'The request was invalid. Please check your details and try again.',
  401: 'Invalid email or password.',
  403: 'You are not allowed to perform this action.',
  404: 'The requested resource was not found.',
  409: 'An account with this email already exists.',
  422: 'Please check the highlighted fields and try again.',
  500: 'The server ran into a problem. Please try again shortly.',
};

// Extract a human message from a FastAPI/Pydantic `detail` payload, which can be
// a string, or an array of {loc, msg, type} validation error objects.
export function extractApiMessage(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (typeof item === 'string') return item;
        const field = Array.isArray(item?.loc)
          ? item.loc.filter((p) => p !== 'body').join('.')
          : null;
        const msg = item?.msg || 'is invalid';
        return field ? `${field}: ${msg}` : msg;
      })
      .filter(Boolean);
    return parts.length ? parts.join('\n') : null;
  }

  if (typeof detail === 'object' && typeof detail.msg === 'string') {
    return detail.msg;
  }

  return null;
}

export function getApiErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  if (!error) return fallback;

  // Our own thrown Errors (e.g. Google init failures).
  if (typeof error === 'string') return error;

  const response = error.response;

  if (!response) {
    // Axios sets `code` for network/timeout failures.
    if (error.code === 'ECONNABORTED') {
      return 'The request timed out. Please try again.';
    }
    if (error.request || error.isAxiosError) {
      return 'Cannot reach the Sahaara server. Please make sure the backend is running.';
    }
    return error.message || fallback;
  }

  const serverMessage = extractApiMessage(response.data?.detail);
  if (serverMessage) return serverMessage;

  if (DEFAULT_MESSAGES[response.status]) return DEFAULT_MESSAGES[response.status];

  if (response.status >= 500) {
    return DEFAULT_MESSAGES[500];
  }

  return response.data?.message || error.message || fallback;
}

export default getApiErrorMessage;