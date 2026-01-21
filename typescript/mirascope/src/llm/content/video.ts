/**
 * @fileoverview The `Video` content class.
 */

/**
 * Video content for a message.
 *
 * Video can be included in messages for video-based interactions.
 */
export type Video = {
  /** The content type identifier */
  type: 'video';

  /** A unique identifier for this video content. This is useful for tracking and referencing generated videos. */
  id?: string;

  /** The video data, which can be a URL, file path, base64-encoded string, or binary data. */
  data: string | Uint8Array;

  /** The transcript of the video, if available. This is useful for accessibility and search. */
  transcript?: string;

  /** The MIME type of the video, e.g., 'video/mp4', 'video/webm'. */
  mimeType:
    | 'video/mp4'
    | 'video/mpeg'
    | 'video/mov'
    | 'video/avi'
    | 'video/x-flv'
    | 'video/mpg'
    | 'video/webm'
    | 'video/wmv'
    | 'video/3gpp';
};
