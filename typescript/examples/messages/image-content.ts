/**
 * Image content example.
 *
 * Demonstrates including images in messages for multimodal models.
 *
 * Run with: bun run example examples/messages/image-content.ts
 */
import { llm } from "mirascope";

// Image from URL (provider downloads directly)
const imageUrl = llm.Image.fromUrl("https://example.com/photo.jpg");

// Image downloaded and encoded as base64
// const imageDownloaded = await llm.Image.download("https://example.com/photo.jpg");

// Image from raw bytes
// const imageBytes = llm.Image.fromBytes(new Uint8Array([...]));

// Include image in a message
const message = llm.messages.user(["What's in this image?", imageUrl]);

console.log(message);
