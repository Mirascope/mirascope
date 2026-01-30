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
 * Factory methods for creating Document instances.
 *
 * Note: These are stubs that throw NotImplementedError.
 * Full implementation is deferred to a later phase.
 */
export const Document = {
  /**
   * Create a Document from a URL reference.
   *
   * @throws Error (not implemented)
   */
  fromUrl: (_url: string, _options?: { download?: boolean }): Document => {
    throw new Error("Document.fromUrl is not yet implemented");
  },

  /**
   * Create a Document from raw bytes.
   *
   * @throws Error (not implemented)
   */
  fromBytes: (
    _data: Uint8Array,
    _options?: { mimeType?: DocumentTextMimeType | DocumentBase64MimeType },
  ): Document => {
    throw new Error("Document.fromBytes is not yet implemented");
  },
};
