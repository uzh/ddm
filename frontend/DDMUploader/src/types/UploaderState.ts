export const UPLOADER_STATES = {
  IDLE: 'idle',
  PROCESSING: 'processing',
  DONE: 'done'
} as const;

export type UploaderStates = typeof UPLOADER_STATES[keyof typeof UPLOADER_STATES];
