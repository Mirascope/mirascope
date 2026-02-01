/**
 * Audio content example.
 *
 * Demonstrates including audio in messages for multimodal models.
 *
 * Run with: bun run example examples/messages/audio-content.ts
 */
import { llm } from "mirascope";

// Audio downloaded and encoded as base64
// const audio = await llm.Audio.download("https://example.com/recording.mp3");

// Audio from raw bytes
// const audioBytes = llm.Audio.fromBytes(new Uint8Array([...]));

// Include audio in a message (example with placeholder)
const audioPlaceholder = {
  type: "audio" as const,
  source: {
    type: "base64_audio_source" as const,
    data: "...",
    mimeType: "audio/mp3" as const,
  },
};

const message = llm.messages.user([
  "Please transcribe this audio:",
  audioPlaceholder,
]);

console.log(message);
