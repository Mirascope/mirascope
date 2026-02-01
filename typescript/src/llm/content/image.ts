/**
 * Supported image MIME types.
 */
export type ImageMimeType =
  | 'image/png'
  | 'image/jpeg'
  | 'image/webp'
  | 'image/gif'
  | 'image/heic'
  | 'image/heif';

/**
 * Image data encoded as base64.
 */
export type Base64ImageSource = {
  readonly type: 'base64_image_source';

  /** The image data, as a base64 encoded string. */
  readonly data: string;

  /** The mime type of the image (e.g. image/png). */
  readonly mimeType: ImageMimeType;
};

/**
 * Image referenced by URL.
 */
export type URLImageSource = {
  readonly type: 'url_image_source';

  /** The url of the image (e.g. https://example.com/image.png). */
  readonly url: string;
};

/**
 * Image content for a message.
 *
 * Images can be included in user messages for multimodal models.
 * The source can be either base64-encoded data or a URL reference.
 */
export type Image = {
  readonly type: 'image';

  readonly source: Base64ImageSource | URLImageSource;
};

/** Maximum image size in bytes (20MB) */
export const MAX_IMAGE_SIZE = 20 * 1024 * 1024;

/**
 * Infer the MIME type of an image from its magic bytes.
 *
 * @throws Error if the image type cannot be determined
 */
export function inferImageType(data: Uint8Array): ImageMimeType {
  if (data.length < 12) {
    throw new Error(
      'Image data too small to determine type (minimum 12 bytes)'
    );
  }

  // JPEG: starts with 0xFF 0xD8 0xFF
  if (data[0] === 0xff && data[1] === 0xd8 && data[2] === 0xff) {
    return 'image/jpeg';
  }

  // PNG: starts with 0x89 PNG\r\n\x1a\n
  if (
    data[0] === 0x89 &&
    data[1] === 0x50 &&
    data[2] === 0x4e &&
    data[3] === 0x47 &&
    data[4] === 0x0d &&
    data[5] === 0x0a &&
    data[6] === 0x1a &&
    data[7] === 0x0a
  ) {
    return 'image/png';
  }

  // GIF: starts with GIF87a or GIF89a
  if (
    data[0] === 0x47 &&
    data[1] === 0x49 &&
    data[2] === 0x46 &&
    data[3] === 0x38 &&
    (data[4] === 0x37 || data[4] === 0x39) &&
    data[5] === 0x61
  ) {
    return 'image/gif';
  }

  // WebP: starts with RIFF....WEBP
  if (
    data[0] === 0x52 &&
    data[1] === 0x49 &&
    data[2] === 0x46 &&
    data[3] === 0x46 &&
    data[8] === 0x57 &&
    data[9] === 0x45 &&
    data[10] === 0x42 &&
    data[11] === 0x50
  ) {
    return 'image/webp';
  }

  // HEIC/HEIF: check ftyp box at offset 4
  if (
    data[4] === 0x66 &&
    data[5] === 0x74 &&
    data[6] === 0x79 &&
    data[7] === 0x70
  ) {
    // Check subtype at offset 8-11 (safe - we validated length >= 12)
    const subtype = String.fromCharCode(
      data[8]!,
      data[9]!,
      data[10]!,
      data[11]!
    );
    if (subtype === 'heic' || subtype === 'heix') {
      return 'image/heic';
    }
    if (['mif1', 'msf1', 'hevc', 'hevx'].includes(subtype)) {
      return 'image/heif';
    }
  }

  throw new Error('Unsupported image type');
}

/**
 * Convert a Uint8Array to a base64 string.
 */
export function uint8ArrayToBase64(data: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < data.length; i++) {
    binary += String.fromCharCode(data[i]!);
  }
  return btoa(binary);
}

/**
 * Factory methods for creating Image instances.
 */
export const Image = {
  /**
   * Create an Image from a URL reference (no download).
   */
  fromUrl: (url: string): Image => ({
    type: 'image',
    source: { type: 'url_image_source', url },
  }),

  /**
   * Download an image from a URL and encode as base64.
   *
   * @throws Error if download fails or image exceeds maxSize
   */
  download: async (url: string, maxSize = MAX_IMAGE_SIZE): Promise<Image> => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(
        `Failed to download image: ${response.status} ${response.statusText}`
      );
    }
    const buffer = await response.arrayBuffer();
    return Image.fromBytes(new Uint8Array(buffer), maxSize);
  },

  /**
   * Create an Image from raw bytes.
   *
   * @throws Error if data exceeds maxSize or type cannot be inferred
   */
  fromBytes: (data: Uint8Array, maxSize = MAX_IMAGE_SIZE): Image => {
    if (data.length > maxSize) {
      throw new Error(
        `Image size (${data.length} bytes) exceeds maximum (${maxSize} bytes)`
      );
    }
    const mimeType = inferImageType(data);
    const base64 = uint8ArrayToBase64(data);
    return {
      type: 'image',
      source: { type: 'base64_image_source', data: base64, mimeType },
    };
  },
};
