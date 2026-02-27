import { readFileSync } from "node:fs";
import { extname } from "node:path";

import { uint8ArrayToBase64 } from "@/llm/content/image";

/**
 * MIME types for text-based documents.
 */
export type DocumentTextMimeType =
  | "application/json"
  | "text/plain"
  | "application/x-javascript"
  | "text/javascript"
  | "application/x-python"
  | "text/x-python"
  | "text/html"
  | "text/css"
  | "text/xml"
  | "text/rtf";

/**
 * MIME types for binary documents (base64 encoded).
 */
export type DocumentBase64MimeType = "application/pdf";

/**
 * Document data encoded as base64 (for binary formats like PDF).
 */
export type Base64DocumentSource = {
  readonly type: "base64_document_source";

  /** The document data, as a base64 encoded string. */
  readonly data: string;

  /** The media type of the document (e.g. application/pdf). */
  readonly mediaType: DocumentBase64MimeType;
};

/**
 * Document data as plain text.
 */
export type TextDocumentSource = {
  readonly type: "text_document_source";

  /** The document data, as plain text. */
  readonly data: string;

  /** The media type of the document (e.g. text/plain, text/csv). */
  readonly mediaType: DocumentTextMimeType;
};

/**
 * Document referenced by URL.
 */
export type URLDocumentSource = {
  readonly type: "url_document_source";

  /** The url of the document (e.g. https://example.com/paper.pdf). */
  readonly url: string;
};

/**
 * Document content for a message.
 *
 * Documents can be included in user messages for models that support them.
 * Supports text documents (JSON, plain text, code) and binary documents (PDF).
 */
export type Document = {
  readonly type: "document";

  readonly source:
    | Base64DocumentSource
    | TextDocumentSource
    | URLDocumentSource;
};

/**
 * Extension to MIME type mapping for documents.
 */
const EXTENSION_TO_MIME_TYPE: Record<
  string,
  DocumentTextMimeType | DocumentBase64MimeType
> = {
  ".pdf": "application/pdf",
  ".json": "application/json",
  ".txt": "text/plain",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".py": "text/x-python",
  ".html": "text/html",
  ".htm": "text/html",
  ".css": "text/css",
  ".xml": "text/xml",
  ".rtf": "text/rtf",
};

/**
 * Text-based MIME types that should be read as UTF-8 text.
 */
const TEXT_MIME_TYPES = new Set<string>([
  "application/json",
  "text/plain",
  "application/x-javascript",
  "text/javascript",
  "application/x-python",
  "text/x-python",
  "text/html",
  "text/css",
  "text/xml",
  "text/rtf",
]);

/**
 * Infer document MIME type from file extension.
 *
 * @throws Error if extension is not recognized
 */
export function mimeTypeFromExtension(
  ext: string,
): DocumentTextMimeType | DocumentBase64MimeType {
  const mimeType = EXTENSION_TO_MIME_TYPE[ext.toLowerCase()];
  if (!mimeType) {
    throw new Error(`Unsupported document file extension: ${ext}`);
  }
  return mimeType;
}

/**
 * Infer document MIME type from magic bytes.
 * Currently only detects PDF (%PDF header).
 *
 * @returns The MIME type if detected, null otherwise
 */
export function inferDocumentType(
  data: Uint8Array,
): DocumentBase64MimeType | null {
  // PDF: starts with %PDF (0x25 0x50 0x44 0x46)
  if (
    data.length >= 4 &&
    data[0] === 0x25 &&
    data[1] === 0x50 &&
    data[2] === 0x44 &&
    data[3] === 0x46
  ) {
    return "application/pdf";
  }
  return null;
}

/**
 * Check if a MIME type is text-based.
 */
function isTextMimeType(
  mimeType: DocumentTextMimeType | DocumentBase64MimeType,
): mimeType is DocumentTextMimeType {
  return TEXT_MIME_TYPES.has(mimeType);
}

/**
 * Factory methods for creating Document instances.
 */
export const Document = {
  /**
   * Create a Document from a URL reference.
   *
   * @param url - The URL of the document
   * @param _options - Options (download is a no-op for now)
   */
  fromUrl: (url: string, _options?: { download?: boolean }): Document => ({
    type: "document",
    source: { type: "url_document_source", url },
  }),

  /**
   * Create a Document from raw bytes.
   *
   * @param data - The raw bytes of the document
   * @param options - Optional mimeType override
   * @throws Error if MIME type cannot be inferred
   */
  fromBytes: (
    data: Uint8Array,
    options?: { mimeType?: DocumentTextMimeType | DocumentBase64MimeType },
  ): Document => {
    const mimeType = options?.mimeType ?? inferDocumentType(data);
    if (!mimeType) {
      throw new Error(
        "Cannot infer document type from bytes. Please provide a mimeType option.",
      );
    }

    if (isTextMimeType(mimeType)) {
      const text = new TextDecoder().decode(data);
      return {
        type: "document",
        source: {
          type: "text_document_source",
          data: text,
          mediaType: mimeType,
        },
      };
    }

    const base64 = uint8ArrayToBase64(data);
    return {
      type: "document",
      source: {
        type: "base64_document_source",
        data: base64,
        mediaType: mimeType,
      },
    };
  },

  /**
   * Create a Document from a file path.
   *
   * @param filePath - Path to the document file
   * @param options - Optional mimeType override
   * @throws Error if MIME type cannot be inferred from extension
   */
  fromFile: (
    filePath: string,
    options?: { mimeType?: DocumentTextMimeType | DocumentBase64MimeType },
  ): Document => {
    const ext = extname(filePath);
    const mimeType = options?.mimeType ?? mimeTypeFromExtension(ext);

    if (isTextMimeType(mimeType)) {
      const text = readFileSync(filePath, "utf-8");
      return {
        type: "document",
        source: {
          type: "text_document_source",
          data: text,
          mediaType: mimeType,
        },
      };
    }

    const data = readFileSync(filePath);
    const base64 = uint8ArrayToBase64(new Uint8Array(data));
    return {
      type: "document",
      source: {
        type: "base64_document_source",
        data: base64,
        mediaType: mimeType,
      },
    };
  },
};
