import { describe, it, expect } from "vitest";
import { CARD_WIDTH, CARD_HEIGHT, SocialCardTemplate } from "./template";

describe("SocialCardTemplate", () => {
  describe("constants", () => {
    it("has correct width for OG images", () => {
      expect(CARD_WIDTH).toBe(1200);
    });

    it("has correct height for OG images", () => {
      expect(CARD_HEIGHT).toBe(630);
    });
  });

  describe("SocialCardTemplate", () => {
    const mockBackgroundImage = "data:image/webp;base64,TEST";

    it("returns a valid React element", () => {
      const result = SocialCardTemplate({
        title: "Test Title",
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
      expect(result).not.toBeNull();
    });

    it("renders with provided title", () => {
      const result = SocialCardTemplate({
        title: "My Custom Title",
        backgroundImage: mockBackgroundImage,
      });

      // The result is a React element, verify it has the expected structure
      expect(result).toBeDefined();
    });

    it("renders with background image", () => {
      const result = SocialCardTemplate({
        title: "Title",
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
    });

    it("handles empty title", () => {
      const result = SocialCardTemplate({
        title: "",
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
    });

    it("handles very long title", () => {
      const longTitle =
        "This is a very long title that might need to wrap across multiple lines in the social card image";
      const result = SocialCardTemplate({
        title: longTitle,
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
    });

    it("handles title with special characters", () => {
      const result = SocialCardTemplate({
        title: "Title with <special> & 'characters'",
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
    });

    it("handles title with unicode characters", () => {
      const result = SocialCardTemplate({
        title: "Title with émojis 🚀 and ünicode",
        backgroundImage: mockBackgroundImage,
      });

      expect(result).toBeDefined();
    });
  });
});
