/**
 * @fileoverview The `Audio` content class.
 */

/**
 * Audio content for a message.
 *
 * Audio can be included in messages for voice or sound-based interactions.
 */
export type Audio = {
  /** The content type identifier */
  type: 'audio';

  /** A unique identifier for this audio content. This is useful for tracking and referencing generated audio. */
  id?: string;

  /** The audio data, which can be a URL, file path, base64-encoded string, or binary data. */
  data: string | Uint8Array;

  /** The transcript of the audio, if available. This is useful for accessibility and search. */
  transcript?: string;

  /** The MIME type of the audio, e.g., 'audio/mp3', 'audio/wav'. */
  mimeType:
    | 'audio/wav'
    | 'audio/mp3'
    | 'audio/aiff'
    | 'audio/aac'
    | 'audio/ogg'
    | 'audio/flac';
};
