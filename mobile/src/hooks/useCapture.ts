import { useState, useEffect, useCallback } from 'react';
import * as ScreenCapture from '../modules/ScreenCapture';

type Status = 'idle' | 'starting' | 'active' | 'stopping' | 'error';

interface UseCaptureResult {
  status: Status;
  errorMessage: string | null;
  start: (host: string, port?: number) => Promise<void>;
  stop: () => Promise<void>;
}

/**
 * Hook that manages the screen capture lifecycle.
 * Handles native events and exposes a clean async API.
 */
export function useCapture(): UseCaptureResult {
  const [status, setStatus] = useState<Status>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const statusSub = ScreenCapture.onStatusChange(({ isActive }) => {
      setStatus(isActive ? 'active' : 'idle');
    });

    const errorSub = ScreenCapture.onError(({ message }) => {
      setErrorMessage(message);
      setStatus('error');
    });

    return () => {
      statusSub.remove();
      errorSub.remove();
    };
  }, []);

  const start = useCallback(async (host: string, port?: number) => {
    setErrorMessage(null);
    setStatus('starting');
    try {
      await ScreenCapture.startCapture(host, port);
    } catch (e: any) {
      setErrorMessage(e?.message ?? 'Unknown error');
      setStatus('error');
    }
  }, []);

  const stop = useCallback(async () => {
    setStatus('stopping');
    try {
      await ScreenCapture.stopCapture();
    } catch (e: any) {
      setErrorMessage(e?.message ?? 'Unknown error');
      setStatus('error');
    }
  }, []);

  return { status, errorMessage, start, stop };
}
