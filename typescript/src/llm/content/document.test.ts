import { describe, expect, it, vi } from "vitest";

import { Document } from "@/llm/content/document";
import {
  inferDocumentType,
  mimeTypeFromExtension,
} from "@/llm/content/document";

// PDF magic bytes: %PDF
const PDF_MAGIC_BYTES = new Uint8Array([0x25, 0x50, 0x44, 0x46, 0x2d, 0x31]);

describe("inferDocumentType", () => {
  it("detects PDF from magic bytes", () => {
    expect(inferDocumentType(PDF_MAGIC_BYTES)).toBe("application/pdf");
  });

  it("returns null for unknown bytes", () => {
    const unknown = new Uint8Array([0x00, 0x01, 0x02, 0x03]);
    expect(inferDocumentType(unknown)).toBeNull();
  });

  it("returns null for data shorter than 4 bytes", () => {
    const short = new Uint8Array([0x25, 0x50]);
    expect(inferDocumentType(short)).toBeNull();
  });
});

describe("mimeTypeFromExtension", () => {
  it("maps .pdf to application/pdf", () => {
    expect(mimeTypeFromExtension(".pdf")).toBe("application/pdf");
  });

  it("maps .txt to text/plain", () => {
    expect(mimeTypeFromExtension(".txt")).toBe("text/plain");
  });

  it("maps .json to application/json", () => {
    expect(mimeTypeFromExtension(".json")).toBe("application/json");
  });

  it("maps .js to text/javascript", () => {
    expect(mimeTypeFromExtension(".js")).toBe("text/javascript");
  });

  it("maps .mjs to text/javascript", () => {
    expect(mimeTypeFromExtension(".mjs")).toBe("text/javascript");
  });

  it("maps .py to text/x-python", () => {
    expect(mimeTypeFromExtension(".py")).toBe("text/x-python");
  });

  it("maps .html to text/html", () => {
    expect(mimeTypeFromExtension(".html")).toBe("text/html");
  });

  it("maps .htm to text/html", () => {
    expect(mimeTypeFromExtension(".htm")).toBe("text/html");
  });

  it("maps .css to text/css", () => {
    expect(mimeTypeFromExtension(".css")).toBe("text/css");
  });

  it("maps .xml to text/xml", () => {
    expect(mimeTypeFromExtension(".xml")).toBe("text/xml");
  });

  it("maps .rtf to text/rtf", () => {
    expect(mimeTypeFromExtension(".rtf")).toBe("text/rtf");
  });

  it("is case-insensitive", () => {
    expect(mimeTypeFromExtension(".PDF")).toBe("application/pdf");
  });

  it("throws for unsupported extension", () => {
    expect(() => mimeTypeFromExtension(".docx")).toThrow(
      "Unsupported document file extension: .docx",
    );
  });
});

describe("Document", () => {
  describe("fromUrl", () => {
    it("creates URLDocumentSource", () => {
      const doc = Document.fromUrl("https://example.com/doc.pdf");
      expect(doc).toEqual({
        type: "document",
        source: {
          type: "url_document_source",
          url: "https://example.com/doc.pdf",
        },
      });
    });

    it("accepts download option (no-op)", () => {
      const doc = Document.fromUrl("https://example.com/doc.pdf", {
        download: true,
      });
      expect(doc.source.type).toBe("url_document_source");
    });
  });

  describe("fromBytes", () => {
    it("creates Base64DocumentSource for PDF bytes", () => {
      const doc = Document.fromBytes(PDF_MAGIC_BYTES);
      expect(doc.type).toBe("document");
      expect(doc.source.type).toBe("base64_document_source");
      if (doc.source.type === "base64_document_source") {
        expect(doc.source.mediaType).toBe("application/pdf");
        // base64 of PDF_MAGIC_BYTES
        expect(doc.source.data).toBe(
          btoa(String.fromCharCode(...PDF_MAGIC_BYTES)),
        );
      }
    });

    it("creates TextDocumentSource with explicit text mimeType", () => {
      const text = new TextEncoder().encode("Hello, world!");
      const doc = Document.fromBytes(text, { mimeType: "text/plain" });
      expect(doc.type).toBe("document");
      expect(doc.source.type).toBe("text_document_source");
      if (doc.source.type === "text_document_source") {
        expect(doc.source.data).toBe("Hello, world!");
        expect(doc.source.mediaType).toBe("text/plain");
      }
    });

    it("creates Base64DocumentSource with explicit PDF mimeType", () => {
      const data = new Uint8Array([0x00, 0x01, 0x02]);
      const doc = Document.fromBytes(data, { mimeType: "application/pdf" });
      expect(doc.source.type).toBe("base64_document_source");
    });

    it("throws for unknown bytes without mimeType", () => {
      const unknown = new Uint8Array([0x00, 0x01, 0x02, 0x03]);
      expect(() => Document.fromBytes(unknown)).toThrow(
        "Cannot infer document type from bytes",
      );
    });
  });

  describe("fromFile", () => {
    it("creates Base64DocumentSource for PDF file", () => {
      // Use a mock to avoid filesystem dependency
      vi.mock("node:fs", async (importOriginal) => {
        const actual = await importOriginal<typeof import("node:fs")>();
        return {
          ...actual,
          readFileSync: vi.fn((path: string, encoding?: BufferEncoding) => {
            if (path === "/test/doc.pdf" && encoding === undefined) {
              return Buffer.from(PDF_MAGIC_BYTES);
            }
            if (path === "/test/doc.txt" && encoding === "utf-8") {
              return "Hello, text!";
            }
            if (path === "/test/doc.json" && encoding === "utf-8") {
              return '{"key": "value"}';
            }
            if (path === "/test/override.xyz" && encoding === undefined) {
              return Buffer.from(PDF_MAGIC_BYTES);
            }
            return actual.readFileSync(
              path,
              encoding as BufferEncoding | undefined,
            );
          }),
        };
      });

      // Re-import to get the mocked version
      const doc = Document.fromFile("/test/doc.pdf");
      expect(doc.type).toBe("document");
      expect(doc.source.type).toBe("base64_document_source");
      if (doc.source.type === "base64_document_source") {
        expect(doc.source.mediaType).toBe("application/pdf");
      }
    });

    it("creates TextDocumentSource for .txt file", () => {
      const doc = Document.fromFile("/test/doc.txt");
      expect(doc.type).toBe("document");
      expect(doc.source.type).toBe("text_document_source");
      if (doc.source.type === "text_document_source") {
        expect(doc.source.data).toBe("Hello, text!");
        expect(doc.source.mediaType).toBe("text/plain");
      }
    });

    it("creates TextDocumentSource for .json file", () => {
      const doc = Document.fromFile("/test/doc.json");
      expect(doc.source.type).toBe("text_document_source");
      if (doc.source.type === "text_document_source") {
        expect(doc.source.mediaType).toBe("application/json");
      }
    });

    it("uses explicit mimeType override", () => {
      const doc = Document.fromFile("/test/override.xyz", {
        mimeType: "application/pdf",
      });
      expect(doc.source.type).toBe("base64_document_source");
      if (doc.source.type === "base64_document_source") {
        expect(doc.source.mediaType).toBe("application/pdf");
      }
    });

    it("throws for unsupported file extension", () => {
      expect(() => Document.fromFile("/test/doc.docx")).toThrow(
        "Unsupported document file extension",
      );
    });
  });
});
