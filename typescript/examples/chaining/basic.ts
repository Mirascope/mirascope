/**
 * Basic call chaining example.
 *
 * Demonstrates chaining multiple LLM calls where the output of one
 * becomes the input to another.
 *
 * Run with: bun run example examples/chaining/basic.ts
 */
import { llm } from "mirascope";

const summarize = llm.defineCall<{ text: string }>({
  model: "openai/gpt-4o-mini",
  template: ({ text }) => `Summarize this text in one line: \n${text}`,
});

const translate = llm.defineCall<{ text: string; language: string }>({
  model: "openai/gpt-4o-mini",
  template: ({ text, language }) =>
    `Translate this text to ${language}: \n${text}`,
});

const text = `
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them.
`;

// First call: summarize
const summary = await summarize({ text });
console.log(`Summary: ${summary.text()}`);

// Second call: translate the summary
const translation = await translate({
  text: summary.text(),
  language: "french",
});
console.log(`Translation: ${translation.text()}`);
