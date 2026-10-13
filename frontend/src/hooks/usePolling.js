import { useEffect, useRef } from 'react';

export const usePolling = (callback, intervalMs = 30000, enabled = true) => {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) return;

    savedCallback.current();

    const id = setInterval(() => {
      savedCallback.current();
    }, intervalMs);

    return () => {
      clearInterval(id);
    };
  }, [intervalMs, enabled]);
};

export default usePolling;
