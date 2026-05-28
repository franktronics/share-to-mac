import { NativeModules, NativeEventEmitter } from 'react-native';

const { ScreenCaptureModule } = NativeModules;
const emitter = new NativeEventEmitter(ScreenCaptureModule);

export type CaptureStatus = {
  isActive: boolean;
};

export type CaptureError = {
  message: string;
};

export const DEFAULT_PORT = 5005;

/**
 * Starts screen capture and streams frames to the given host via UDP.
 */
export function startCapture(host: string, port: number = DEFAULT_PORT): Promise<void> {
  return ScreenCaptureModule.startCapture(host, port);
}

/**
 * Stops the ongoing screen capture session.
 */
export function stopCapture(): Promise<void> {
  return ScreenCaptureModule.stopCapture();
}

/**
 * Subscribes to capture status changes (started / stopped).
 */
export function onStatusChange(callback: (status: CaptureStatus) => void) {
  return emitter.addListener('onCaptureStatusChange', callback);
}

/**
 * Subscribes to capture errors emitted by the native module.
 */
export function onError(callback: (error: CaptureError) => void) {
  return emitter.addListener('onCaptureError', callback);
}
