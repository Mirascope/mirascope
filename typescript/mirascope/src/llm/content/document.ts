/**
 * @fileoverview The `Document` content class.
 */

/**
 * Document content for a message.
 *
 * Documents (like PDFs) can be included for the model to analyze or reference.
 */
export type Document = {
  /** The content type identifier */
  type: 'document';

  /** The document data, which can be a URL, file path, base64-encoded string, or binary data. */
  data: string | Uint8Array;

  /** The MIME type of the document, e.g., 'application/pdf'. */
  mimeType:
    | 'application/pdf'
    | 'application/json'
    | 'text/plain'
    | 'application/x-javascript'
    | 'text/javascript'
    | 'application/x-python'
    | 'text/x-python'
    | 'text/html'
    | 'text/css'
    | 'text/xml'
    | 'text/rtf';
};
