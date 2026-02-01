import { describe, expect, it, vi } from "vitest";

import { Audio, inferAudioType, MAX_AUDIO_SIZE } from "@/llm/content/audio";

describe("Audio", () => {
  describe("type shape", () => {
    it("has correct type discriminator", () => {
      // WAV magic bytes
      const wavData = new Uint8Array([
        0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45,
      ]);
      const audio = Audio.fromBytes(wavData);
      expect(audio.type).toBe("audio");
    });
  });

  describe("fromBytes", () => {
    it("creates audio from WAV bytes", () => {
      // WAV: RIFF....WAVE
      const wavData = new Uint8Array([
        0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45,
      ]);
      const audio = Audio.fromBytes(wavData);
      expect(audio.type).toBe("audio");
      expect(audio.source.type).toBe("base64_audio_source");
      expect(audio.source.mimeType).toBe("audio/wav");
    });

    it("creates audio from MP3 bytes (ID3 header)", () => {
      // MP3 with ID3 tag
      const mp3Data = new Uint8Array([
        0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const audio = Audio.fromBytes(mp3Data);
      expect(audio.source.mimeType).toBe("audio/mp3");
    });

    it("creates audio from MP3 bytes (frame sync)", () => {
      // MP3 frame sync: FF FB
      const mp3Data = new Uint8Array([
        0xff, 0xfb, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const audio = Audio.fromBytes(mp3Data);
      expect(audio.source.mimeType).toBe("audio/mp3");
    });

    it("creates audio from AIFF bytes", () => {
      // AIFF: FORM....AIFF
      const aiffData = new Uint8Array([
        0x46, 0x4f, 0x52, 0x4d, 0x00, 0x00, 0x00, 0x00, 0x41, 0x49, 0x46, 0x46,
      ]);
      const audio = Audio.fromBytes(aiffData);
      expect(audio.source.mimeType).toBe("audio/aiff");
    });

    it("creates audio from OGG bytes", () => {
      // OGG: OggS
      const oggData = new Uint8Array([
        0x4f, 0x67, 0x67, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const audio = Audio.fromBytes(oggData);
      expect(audio.source.mimeType).toBe("audio/ogg");
    });

    it("creates audio from FLAC bytes", () => {
      // FLAC: fLaC
      const flacData = new Uint8Array([
        0x66, 0x4c, 0x61, 0x43, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const audio = Audio.fromBytes(flacData);
      expect(audio.source.mimeType).toBe("audio/flac");
    });

    it("creates audio from AAC bytes", () => {
      // AAC ADTS: FF Fx
      const aacData = new Uint8Array([
        0xff, 0xf1, 0x50, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const audio = Audio.fromBytes(aacData);
      expect(audio.source.mimeType).toBe("audio/aac");
    });

    it("throws on oversized audio", () => {
      const bigData = new Uint8Array(MAX_AUDIO_SIZE + 1);
      expect(() => Audio.fromBytes(bigData)).toThrow(/exceeds maximum/);
    });

    it("respects custom maxSize", () => {
      const smallLimit = 100;
      const data = new Uint8Array(101);
      expect(() => Audio.fromBytes(data, smallLimit)).toThrow(
        /exceeds maximum/,
      );
    });
  });

  describe("download", () => {
    it("downloads and creates audio from URL", async () => {
      // WAV magic bytes
      const wavData = new Uint8Array([
        0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45,
      ]);

      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: true,
          arrayBuffer: () => Promise.resolve(wavData.buffer),
        }),
      );

      const audio = await Audio.download("https://example.com/audio.wav");
      expect(audio.type).toBe("audio");
      expect(audio.source.type).toBe("base64_audio_source");

      vi.unstubAllGlobals();
    });

    it("throws on failed download", async () => {
      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: false,
          status: 404,
          statusText: "Not Found",
        }),
      );

      await expect(
        Audio.download("https://example.com/missing.wav"),
      ).rejects.toThrow(/Failed to download audio: 404 Not Found/);

      vi.unstubAllGlobals();
    });
  });
});

describe("inferAudioType", () => {
  it("detects WAV", () => {
    const data = new Uint8Array([
      0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45,
    ]);
    expect(inferAudioType(data)).toBe("audio/wav");
  });

  it("detects MP3 with ID3", () => {
    const data = new Uint8Array([
      0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/mp3");
  });

  it("detects MP3 frame sync (FB)", () => {
    const data = new Uint8Array([
      0xff, 0xfb, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/mp3");
  });

  it("detects MP3 frame sync (FA)", () => {
    const data = new Uint8Array([
      0xff, 0xfa, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/mp3");
  });

  it("detects MP3 frame sync (F3)", () => {
    const data = new Uint8Array([
      0xff, 0xf3, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/mp3");
  });

  it("detects MP3 frame sync (F2)", () => {
    const data = new Uint8Array([
      0xff, 0xf2, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/mp3");
  });

  it("detects AIFF", () => {
    const data = new Uint8Array([
      0x46, 0x4f, 0x52, 0x4d, 0x00, 0x00, 0x00, 0x00, 0x41, 0x49, 0x46, 0x46,
    ]);
    expect(inferAudioType(data)).toBe("audio/aiff");
  });

  it("detects OGG", () => {
    const data = new Uint8Array([
      0x4f, 0x67, 0x67, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/ogg");
  });

  it("detects FLAC", () => {
    const data = new Uint8Array([
      0x66, 0x4c, 0x61, 0x43, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/flac");
  });

  it("detects AAC", () => {
    const data = new Uint8Array([
      0xff, 0xf1, 0x50, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferAudioType(data)).toBe("audio/aac");
  });

  it("throws on data too small", () => {
    const data = new Uint8Array([0x52, 0x49]);
    expect(() => inferAudioType(data)).toThrow(/too small/);
  });

  it("throws on unsupported type", () => {
    const data = new Uint8Array([
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b,
    ]);
    expect(() => inferAudioType(data)).toThrow(/Unsupported audio type/);
  });
});

describe("MAX_AUDIO_SIZE", () => {
  it("is 25MB", () => {
    expect(MAX_AUDIO_SIZE).toBe(25 * 1024 * 1024);
  });
});
