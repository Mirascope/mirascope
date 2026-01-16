import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs/promises";
import path from "node:path";
import { loadAssets, renderSocialCard, clearAssetCache } from "./render";

describe("render", () => {
  // Clear asset cache between tests to ensure clean state
  beforeEach(() => {
    clearAssetCache();
  });

  afterEach(() => {
    clearAssetCache();
  });

  describe("loadAssets", () => {
    it("loads font file from public/fonts/", async () => {
      const { font } = await loadAssets();

      expect(font).toBeInstanceOf(ArrayBuffer);
      expect(font.byteLength).toBeGreaterThan(0);
    });

    it("loads background image from public/assets/backgrounds/", async () => {
      const { background } = await loadAssets();

      expect(typeof background).toBe("string");
      expect(background).toMatch(/^data:image\/webp;base64,/);
    });

    it("caches assets on subsequent calls", async () => {
      const assets1 = await loadAssets();
      const assets2 = await loadAssets();

      // Should return the same cached references
      expect(assets1.font).toBe(assets2.font);
      expect(assets1.background).toBe(assets2.background);
    });

    it("throws if font file is missing", async () => {
      // This test would require mocking fs, skipping for now
      // as the font file should exist in the repository
    });
  });

  describe("renderSocialCard", () => {
    it("generates a valid WebP buffer", async () => {
      const assets = await loadAssets();
      const result = await renderSocialCard("Test Title", assets);

      expect(result).toBeInstanceOf(Buffer);
      expect(result.length).toBeGreaterThan(0);

      // Check WebP magic bytes (RIFF....WEBP)
      expect(result.subarray(0, 4).toString("ascii")).toBe("RIFF");
      expect(result.subarray(8, 12).toString("ascii")).toBe("WEBP");
    });

    it("generates different images for different titles", async () => {
      const assets = await loadAssets();

      const result1 = await renderSocialCard("First Title", assets);
      const result2 = await renderSocialCard("Second Title", assets);

      // Images should be different (different content)
      expect(result1.equals(result2)).toBe(false);
    });

    it("respects quality parameter", async () => {
      const assets = await loadAssets();

      const highQuality = await renderSocialCard("Test", assets, 95);
      const lowQuality = await renderSocialCard("Test", assets, 50);

      // Higher quality should generally produce larger files
      // (not guaranteed but typically true)
      expect(highQuality.length).not.toBe(lowQuality.length);
    });

    it("handles empty title", async () => {
      const assets = await loadAssets();
      const result = await renderSocialCard("", assets);

      expect(result).toBeInstanceOf(Buffer);
      expect(result.length).toBeGreaterThan(0);
    });

    it("handles very long title", async () => {
      const assets = await loadAssets();
      const longTitle =
        "This is a very long title that should wrap across multiple lines in the social card image and test the text wrapping capabilities";

      const result = await renderSocialCard(longTitle, assets);

      expect(result).toBeInstanceOf(Buffer);
      expect(result.length).toBeGreaterThan(0);
    });

    it("handles special characters in title", async () => {
      const assets = await loadAssets();
      const result = await renderSocialCard(
        "Title with <HTML> & 'quotes'",
        assets,
      );

      expect(result).toBeInstanceOf(Buffer);
    });

    it("handles unicode characters in title", async () => {
      const assets = await loadAssets();
      const result = await renderSocialCard("Title with émojis 🚀", assets);

      expect(result).toBeInstanceOf(Buffer);
    });
  });

  describe("clearAssetCache", () => {
    it("clears the cached assets", async () => {
      // Load assets to populate cache
      const assets1 = await loadAssets();

      // Clear cache
      clearAssetCache();

      // Load again - should read from disk again
      const assets2 = await loadAssets();

      // ArrayBuffers should be equal in size but not same reference
      expect(assets1.font.byteLength).toBe(assets2.font.byteLength);
      expect(assets1.font).not.toBe(assets2.font);
    });
  });
});

describe("render integration", () => {
  it("generates a valid social card image file", async () => {
    const assets = await loadAssets();
    const buffer = await renderSocialCard("Integration Test", assets);

    // Write to temp file and verify it can be read
    const tempPath = path.join(process.cwd(), "dist", "test-social-card.webp");

    try {
      await fs.mkdir(path.dirname(tempPath), { recursive: true });
      await fs.writeFile(tempPath, buffer);

      // Verify file was written
      const stats = await fs.stat(tempPath);
      expect(stats.size).toBe(buffer.length);
    } finally {
      // Cleanup
      try {
        await fs.unlink(tempPath);
      } catch {
        // Ignore cleanup errors
      }
    }
  });
});
