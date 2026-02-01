import { describe, expect, it, vi } from "vitest";

import {
  Image,
  inferImageType,
  MAX_IMAGE_SIZE,
  uint8ArrayToBase64,
} from "@/llm/content/image";

describe("Image", () => {
  describe("type shape", () => {
    it("has correct type discriminator", () => {
      const img = Image.fromUrl("https://example.com/img.png");
      expect(img.type).toBe("image");
    });
  });

  describe("fromUrl", () => {
    it("creates image from URL", () => {
      const img = Image.fromUrl("https://example.com/photo.jpg");
      expect(img.type).toBe("image");
      expect(img.source.type).toBe("url_image_source");
      if (img.source.type === "url_image_source") {
        expect(img.source.url).toBe("https://example.com/photo.jpg");
      }
    });
  });

  describe("fromBytes", () => {
    it("creates image from PNG bytes", () => {
      // PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A + padding
      const pngData = new Uint8Array([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x00,
      ]);
      const img = Image.fromBytes(pngData);
      expect(img.type).toBe("image");
      expect(img.source.type).toBe("base64_image_source");
      if (img.source.type === "base64_image_source") {
        expect(img.source.mimeType).toBe("image/png");
        expect(img.source.data).toBe(uint8ArrayToBase64(pngData));
      }
    });

    it("creates image from JPEG bytes", () => {
      // JPEG magic bytes: FF D8 FF + padding
      const jpegData = new Uint8Array([
        0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
      ]);
      const img = Image.fromBytes(jpegData);
      if (img.source.type === "base64_image_source") {
        expect(img.source.mimeType).toBe("image/jpeg");
      }
    });

    it("creates image from GIF bytes", () => {
      // GIF89a magic bytes
      const gifData = new Uint8Array([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      ]);
      const img = Image.fromBytes(gifData);
      if (img.source.type === "base64_image_source") {
        expect(img.source.mimeType).toBe("image/gif");
      }
    });

    it("creates image from WebP bytes", () => {
      // WebP: RIFF....WEBP
      const webpData = new Uint8Array([
        0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x45, 0x42, 0x50,
      ]);
      const img = Image.fromBytes(webpData);
      if (img.source.type === "base64_image_source") {
        expect(img.source.mimeType).toBe("image/webp");
      }
    });

    it("throws on oversized image", () => {
      const bigData = new Uint8Array(MAX_IMAGE_SIZE + 1);
      expect(() => Image.fromBytes(bigData)).toThrow(/exceeds maximum/);
    });

    it("respects custom maxSize", () => {
      const smallLimit = 100;
      const data = new Uint8Array(101);
      expect(() => Image.fromBytes(data, smallLimit)).toThrow(
        /exceeds maximum/,
      );
    });
  });

  describe("download", () => {
    it("downloads and creates image from URL", async () => {
      // PNG magic bytes
      const pngData = new Uint8Array([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x00,
      ]);

      vi.stubGlobal(
        "fetch",
        vi.fn().mockResolvedValue({
          ok: true,
          arrayBuffer: () => Promise.resolve(pngData.buffer),
        }),
      );

      const img = await Image.download("https://example.com/image.png");
      expect(img.type).toBe("image");
      expect(img.source.type).toBe("base64_image_source");

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
        Image.download("https://example.com/missing.png"),
      ).rejects.toThrow(/Failed to download image: 404 Not Found/);

      vi.unstubAllGlobals();
    });
  });
});

describe("inferImageType", () => {
  it("detects PNG", () => {
    const data = new Uint8Array([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferImageType(data)).toBe("image/png");
  });

  it("detects JPEG", () => {
    const data = new Uint8Array([
      0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
    ]);
    expect(inferImageType(data)).toBe("image/jpeg");
  });

  it("detects GIF87a", () => {
    const data = new Uint8Array([
      0x47, 0x49, 0x46, 0x38, 0x37, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferImageType(data)).toBe("image/gif");
  });

  it("detects GIF89a", () => {
    const data = new Uint8Array([
      0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]);
    expect(inferImageType(data)).toBe("image/gif");
  });

  it("detects WebP", () => {
    const data = new Uint8Array([
      0x52, 0x49, 0x46, 0x46, 0x00, 0x00, 0x00, 0x00, 0x57, 0x45, 0x42, 0x50,
    ]);
    expect(inferImageType(data)).toBe("image/webp");
  });

  it("detects HEIC", () => {
    // ftyp at offset 4, heic at offset 8
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x69, 0x63,
    ]);
    expect(inferImageType(data)).toBe("image/heic");
  });

  it("detects HEIC (heix)", () => {
    // ftyp at offset 4, heix at offset 8
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x69, 0x78,
    ]);
    expect(inferImageType(data)).toBe("image/heic");
  });

  it("detects HEIF (mif1)", () => {
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x6d, 0x69, 0x66, 0x31,
    ]);
    expect(inferImageType(data)).toBe("image/heif");
  });

  it("detects HEIF (msf1)", () => {
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x6d, 0x73, 0x66, 0x31,
    ]);
    expect(inferImageType(data)).toBe("image/heif");
  });

  it("detects HEIF (hevc)", () => {
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x76, 0x63,
    ]);
    expect(inferImageType(data)).toBe("image/heif");
  });

  it("detects HEIF (hevx)", () => {
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x76, 0x78,
    ]);
    expect(inferImageType(data)).toBe("image/heif");
  });

  it("throws on unknown ftyp subtype", () => {
    // ftyp at offset 4, unknown subtype at offset 8
    const data = new Uint8Array([
      0x00, 0x00, 0x00, 0x00, 0x66, 0x74, 0x79, 0x70, 0x78, 0x78, 0x78, 0x78,
    ]);
    expect(() => inferImageType(data)).toThrow("Unsupported image type");
  });

  it("throws on data too small", () => {
    const data = new Uint8Array([0x89, 0x50]);
    expect(() => inferImageType(data)).toThrow(/too small/);
  });

  it("throws on unsupported type", () => {
    const data = new Uint8Array([
      0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b,
    ]);
    expect(() => inferImageType(data)).toThrow(/Unsupported image type/);
  });
});

describe("uint8ArrayToBase64", () => {
  it("converts empty array", () => {
    const data = new Uint8Array([]);
    expect(uint8ArrayToBase64(data)).toBe("");
  });

  it("converts simple data", () => {
    // "Hello" in bytes
    const data = new Uint8Array([72, 101, 108, 108, 111]);
    expect(uint8ArrayToBase64(data)).toBe("SGVsbG8=");
  });

  it("handles binary data", () => {
    const data = new Uint8Array([0, 255, 128, 64, 32]);
    const base64 = uint8ArrayToBase64(data);
    expect(base64).toBeTruthy();
    expect(typeof base64).toBe("string");
  });
});

describe("MAX_IMAGE_SIZE", () => {
  it("is 20MB", () => {
    expect(MAX_IMAGE_SIZE).toBe(20 * 1024 * 1024);
  });
});
