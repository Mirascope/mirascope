import { describe, expect, it } from 'vitest';

import { Document } from '@/llm/content/document';

describe('Document', () => {
  describe('fromUrl', () => {
    it('throws not implemented error', () => {
      expect(() => Document.fromUrl('https://example.com/doc.pdf')).toThrow(
        'Document.fromUrl is not yet implemented'
      );
    });

    it('throws with download option', () => {
      expect(() =>
        Document.fromUrl('https://example.com/doc.pdf', { download: true })
      ).toThrow('Document.fromUrl is not yet implemented');
    });
  });

  describe('fromBytes', () => {
    it('throws not implemented error', () => {
      const data = new Uint8Array([0x25, 0x50, 0x44, 0x46]); // PDF magic bytes
      expect(() => Document.fromBytes(data)).toThrow(
        'Document.fromBytes is not yet implemented'
      );
    });

    it('throws with mimeType option', () => {
      const data = new Uint8Array([0x25, 0x50, 0x44, 0x46]);
      expect(() =>
        Document.fromBytes(data, { mimeType: 'application/pdf' })
      ).toThrow('Document.fromBytes is not yet implemented');
    });
  });
});
