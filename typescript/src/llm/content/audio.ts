/**
 * Supported audio MIME types.
 */
export type AudioMimeType =
  | 'audio/wav'
  | 'audio/mp3'
  | 'audio/aiff'
  | 'audio/aac'
  | 'audio/ogg'
  | 'audio/flac';

/**
 * Audio data encoded as base64.
 */
export type Base64AudioSource = {
  readonly type: 'base64_audio_source';

  /** The audio data, as a base64 encoded string. */
  readonly data: string;

  /** The mime type of the audio (e.g. audio/mp3). */
  readonly mimeType: AudioMimeType;
};

/**
 * Audio content for a message.
 *
 * Audio can be included in user messages for multimodal models that support it.
 */
export type Audio = {
  readonly type: 'audio';

  readonly source: Base64AudioSource;
};

/** Maximum audio size in bytes (25MB) */
export const MAX_AUDIO_SIZE = 25 * 1024 * 1024;

/**
 * Infer the MIME type of audio from its magic bytes.
 *
 * @throws Error if the audio type cannot be determined
 */
export function inferAudioType(data: Uint8Array): AudioMimeType {
  if (data.length < 12) {
    throw new Error(
      'Audio data too small to determine type (minimum 12 bytes)'
    );
  }

  // WAV: starts with RIFF....WAVE
  if (
    data[0] === 0x52 &&
    data[1] === 0x49 &&
    data[2] === 0x46 &&
    data[3] === 0x46 &&
    data[8] === 0x57 &&
    data[9] === 0x41 &&
    data[10] === 0x56 &&
    data[11] === 0x45
  ) {
    return 'audio/wav';
  }

  // MP3: starts with ID3 or 0xFF 0xFB (frame sync)
  if (
    (data[0] === 0x49 && data[1] === 0x44 && data[2] === 0x33) ||
    (data[0] === 0xff &&
      (data[1] === 0xfb ||
        data[1] === 0xfa ||
        data[1] === 0xf3 ||
        data[1] === 0xf2))
  ) {
    return 'audio/mp3';
  }

  // AIFF: starts with FORM....AIFF
  if (
    data[0] === 0x46 &&
    data[1] === 0x4f &&
    data[2] === 0x52 &&
    data[3] === 0x4d &&
    data[8] === 0x41 &&
    data[9] === 0x49 &&
    data[10] === 0x46 &&
    data[11] === 0x46
  ) {
    return 'audio/aiff';
  }

  // OGG: starts with OggS
  if (
    data[0] === 0x4f &&
    data[1] === 0x67 &&
    data[2] === 0x67 &&
    data[3] === 0x53
  ) {
    return 'audio/ogg';
  }

  // FLAC: starts with fLaC
  if (
    data[0] === 0x66 &&
    data[1] === 0x4c &&
    data[2] === 0x61 &&
    data[3] === 0x43
  ) {
    return 'audio/flac';
  }

  // AAC: starts with ADTS sync word 0xFFF (first 12 bits)
  // Safe to use ! - we validated length >= 12 above
  if (data[0] === 0xff && (data[1]! & 0xf0) === 0xf0) {
    return 'audio/aac';
  }

  throw new Error('Unsupported audio type');
}

/**
 * Convert a Uint8Array to a base64 string.
 */
function uint8ArrayToBase64(data: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < data.length; i++) {
    binary += String.fromCharCode(data[i]!);
  }
  return btoa(binary);
}

/**
 * Factory methods for creating Audio instances.
 */
export const Audio = {
  /**
   * Download audio from a URL and encode as base64.
   *
   * @throws Error if download fails or audio exceeds maxSize
   */
  download: async (url: string, maxSize = MAX_AUDIO_SIZE): Promise<Audio> => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(
        `Failed to download audio: ${response.status} ${response.statusText}`
      );
    }
    const buffer = await response.arrayBuffer();
    return Audio.fromBytes(new Uint8Array(buffer), maxSize);
  },

  /**
   * Create Audio from raw bytes.
   *
   * @throws Error if data exceeds maxSize or type cannot be inferred
   */
  fromBytes: (data: Uint8Array, maxSize = MAX_AUDIO_SIZE): Audio => {
    if (data.length > maxSize) {
      throw new Error(
        `Audio size (${data.length} bytes) exceeds maximum (${maxSize} bytes)`
      );
    }
    const mimeType = inferAudioType(data);
    const base64 = uint8ArrayToBase64(data);
    return {
      type: 'audio',
      source: { type: 'base64_audio_source', data: base64, mimeType },
    };
  },
};
