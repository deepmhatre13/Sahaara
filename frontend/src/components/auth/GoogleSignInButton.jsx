import React, { useEffect, useRef, useState, useCallback } from 'react';
import toast from 'react-hot-toast';
import useAuth from '../../hooks/useAuth';
import { ensureGoogleIdentity, setCredentialHandler } from '../../auth/googleIdentity';
import { getApiErrorMessage } from '../../utils/apiError';

/**
 * Renders the official Google Identity Services button.
 *
 * Initialization is delegated to the module-level `googleIdentity` helper so
 * `google.accounts.id.initialize()` runs exactly once per client ID, even under
 * React StrictMode double-invocation and repeated mount/unmount on navigation.
 */
export const GoogleSignInButton = ({ text = 'Sign in with Google' }) => {
  const { loginWithGoogle } = useAuth();
  const googleBtnRef = useRef(null);
  // Always call the latest loginWithGoogle from the (stable) credential handler.
  const loginWithGoogleRef = useRef(loginWithGoogle);
  loginWithGoogleRef.current = loginWithGoogle;
  const [status, setStatus] = useState('loading'); // 'loading' | 'ready' | 'unavailable'

  const handleCredentialResponse = useCallback(async (response) => {
    if (!response?.credential) return;
    try {
      await loginWithGoogleRef.current(response.credential);
      toast.success('Signed in with Google!');
    } catch (err) {
      // Google failures stay isolated: show a message, never crash the page.
      toast.error(getApiErrorMessage(err, 'Google sign-in failed. Please try again.'));
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    // Route credentials from Google into this component's handler.
    const unregisterHandler = setCredentialHandler(handleCredentialResponse);

    const renderButton = async () => {
      if (!clientId) {
        if (!cancelled) setStatus('unavailable');
        return;
      }
      try {
        const identity = await ensureGoogleIdentity(clientId);
        if (cancelled) return;

        const button = googleBtnRef.current;
        if (!button) return;

        button.replaceChildren();
        identity.renderButton(button, {
          theme: 'outline',
          size: 'large',
          width: button.offsetWidth || 280,
          text: text.includes('Sign up') ? 'signup_with' : 'signin_with',
          shape: 'pill',
          logo_alignment: 'left',
        });
        setStatus('ready');
      } catch (err) {
        // Missing config, script blocked, origin not allowed, etc.
        console.warn('[Sahaara] Google Sign-In is unavailable:', err?.message || err);
        if (!cancelled) setStatus('unavailable');
      }
    };

    renderButton();

    return () => {
      cancelled = true;
      unregisterHandler();
      // Remove only the rendered iframe nodes; do NOT re-initialize or destroy
      // the shared GSI instance so remounts stay cheap and warning-free.
      googleBtnRef.current?.replaceChildren();
    };
  }, [text, handleCredentialResponse]);

  // While GSI is loading we render the target div so `renderButton` has a home;
  // it simply stays empty for the brief load window.
  if (status === 'unavailable') {
    return (
      <div
        className="w-full text-center py-2 px-3 border border-dashed border-[#DDE3E8] rounded-xl text-xs text-[#8A97A5]"
        role="status"
      >
        Google Sign-In is currently unavailable. Please use email and password.
      </div>
    );
  }

  return (
    <div className="w-full flex justify-center my-2">
      {status === 'loading' && (
        <div className="text-xs text-[#8A97A5] py-2" role="status">
          Loading Google Sign-In…
        </div>
      )}
      <div ref={googleBtnRef} className="w-full flex justify-center" />
    </div>
  );
};

export default GoogleSignInButton;

