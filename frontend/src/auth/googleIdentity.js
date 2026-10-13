/**
 * Module-level, idempotent wrapper around Google Identity Services (GSI).
 *
 * Why this exists
 * ---------------
 * `google.accounts.id.initialize()` must be called exactly once per client ID.
 * React (especially in StrictMode) runs effects twice on mount and re-mounts
 * components on navigation, and the GSI script loads asynchronously. Calling
 * `initialize()` from a component effect therefore produced:
 *
 *   [GSI_LOGGER]: google.accounts.id.initialize() is called multiple times.
 *
 * This module keeps a single process-wide promise + a single registered
 * callback, so we can safely mount/unmount the sign-in button as many times as
 * we like. No setTimeout, no globals, no removal of StrictMode.
 */

const GSI_SCRIPT_SRC = 'https://accounts.google.com/gsi/client';
const GSI_SCRIPT_ID = 'sahaara-gsi-script';

// Single process-wide initialization state. Kept at module scope so it
// survives component unmount/remount cycles within the same page load.
const state = {
  clientId: null,
  // Promise resolves with the `google.accounts.id` object once ready.
  readyPromise: null,
  // The most recently mounted button that wants credential callbacks.
  onCredential: null,
  // Notified when initialization can never succeed (missing config / script).
  lastError: null,
};

function getGoogleIdentity() {
  return window.google?.accounts?.id ?? null;
}

function loadGsiScript() {
  return new Promise((resolve, reject) => {
    if (getGoogleIdentity()) {
      resolve(getGoogleIdentity());
      return;
    }

    const existing = document.getElementById(GSI_SCRIPT_ID);

    const handleLoad = () => {
      const identity = getGoogleIdentity();
      if (identity) resolve(identity);
      else reject(new Error('Google Identity Services loaded without accounts.id'));
    };
    const handleError = () => reject(new Error('Failed to load Google Identity Services'));

    if (existing) {
      existing.addEventListener('load', handleLoad, { once: true });
      existing.addEventListener('error', handleError, { once: true });
      return;
    }

    const script = document.createElement('script');
    script.id = GSI_SCRIPT_ID;
    script.src = GSI_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.addEventListener('load', handleLoad, { once: true });
    script.addEventListener('error', handleError, { once: true });
    document.head.appendChild(script);
  });
}

/**
 * Initialize GSI exactly once for `clientId` and resolve with the identity API.
 * Repeated calls with the same client ID reuse the same promise and never
 * re-invoke `initialize()`.
 */
export function ensureGoogleIdentity(clientId) {
  if (!clientId) {
    return Promise.reject(new Error('Google client ID is not configured'));
  }

  if (state.clientId && state.clientId !== clientId) {
    return Promise.reject(
      new Error('Google Identity Services already initialized for a different client ID')
    );
  }

  if (!state.readyPromise) {
    state.readyPromise = loadGsiScript()
      .then((identity) => {
        if (state.clientId === clientId) {
          // Another concurrent caller already initialized it.
          return identity;
        }
        identity.initialize({
          client_id: clientId,
          callback: (response) => {
            state.onCredential?.(response);
          },
          // GSI calls this on origin/config problems (e.g. 403 origin not
          // allowed). Swallowing it here keeps a Google failure from throwing
          // an uncaught exception into the React tree.
          error_callback: (error) => {
            const message =
              error?.message || 'Google Sign-In is currently unavailable.';
            state.lastError = message;
            // eslint-disable-next-line no-console
            console.warn('[Sahaara] Google Sign-In error:', error);
          },
        });
        state.clientId = clientId;
        return identity;
      })
      .catch((err) => {
        state.lastError = err?.message || 'Google Sign-In is currently unavailable.';
        // Reset so a later attempt can retry the script load.
        state.readyPromise = null;
        throw err;
      });
  }

  return state.readyPromise;
}

/**
 * Register the active credential handler. Returns a cleanup fn that only clears
 * the handler if it is still the same one (so a fast unmount of an old button
 * does not clobber the newly mounted one).
 */
export function setCredentialHandler(handler) {
  state.onCredential = handler;
  return () => {
    if (state.onCredential === handler) {
      state.onCredential = null;
    }
  };
}

export function getGoogleInitError() {
  return state.lastError;
}