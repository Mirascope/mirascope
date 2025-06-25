/**
 * @fileoverview The `Image` content class.
 */

/**
 * Image content for a message.
 *
 * Images can be included in messages to provide visual context. This can be
 * used for both input (e.g., user uploading an image) and output (e.g., model
 * generating an image).
 */
export type Image = {
  /** The content type identifier */
  type: 'image';

  /** A unique identifier for this image content. This is useful for tracking and referencing generated images. */
  id?: string;

  /** The image data, which can be a URL, file path, base64-encoded string, or binary data. */
  data: string | Uint8Array;

  /** The MIME type of the image, e.g., 'image/png', 'image/jpeg'. */
  mimeType:
    | 'image/png'
    | 'image/jpeg'
    | 'image/webp'
    | 'image/gif'
    | 'image/heic'
    | 'image/heif';
};
