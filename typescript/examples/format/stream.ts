/**
 * Streaming structured output example.
 *
 * Demonstrates using structuredStream() to get partial typed objects
 * as they stream in from the LLM.
 *
 * Run with: bun run example examples/format/stream.ts
 */
import { z } from 'zod';
import { llm } from 'mirascope';

// Define a Zod schema for the structured output
const MovieReviewSchema = z.object({
  title: z.string().describe('The title of the movie'),
  year: z.number().describe('The year the movie was released'),
  director: z.string().describe('The director of the movie'),
  rating: z.number().describe('Your rating from 1-10'),
  pros: z.array(z.string()).describe('Positive aspects of the movie'),
  cons: z.array(z.string()).describe('Negative aspects of the movie'),
  verdict: z.string().describe('Your overall verdict on the movie'),
});

type MovieReview = z.infer<typeof MovieReviewSchema>;

// Create a streaming call with format option
// Use defineCall<VarsType>()({...}) to specify variables type while inferring format type.
const reviewMovie = llm.defineCall<{ movie: string }>()({
  model: 'anthropic/claude-haiku-4-5',
  maxTokens: 1024,
  format: MovieReviewSchema,
  template: ({ movie }) =>
    `Write a detailed review of the movie "${movie}". Be thorough but concise.`,
});

// Stream the response and get partial objects as they arrive
const response = await reviewMovie.stream({ movie: 'The Matrix' });

console.log('Streaming Movie Review:');
console.log('======================\n');

// Use structuredStream() to get partial typed objects
for await (const partial of response.structuredStream()) {
  // Clear console and show current state
  console.clear();
  console.log('Streaming Movie Review (live):');
  console.log('==============================\n');

  if (partial.title) console.log(`Title: ${partial.title}`);
  if (partial.year) console.log(`Year: ${partial.year}`);
  if (partial.director) console.log(`Director: ${partial.director}`);
  if (partial.rating) console.log(`Rating: ${partial.rating}/10`);
  if (partial.pros && partial.pros.length > 0) {
    console.log('\nPros:');
    for (const pro of partial.pros) {
      if (pro) console.log(`  + ${pro}`);
    }
  }
  if (partial.cons && partial.cons.length > 0) {
    console.log('\nCons:');
    for (const con of partial.cons) {
      if (con) console.log(`  - ${con}`);
    }
  }
  if (partial.verdict) console.log(`\nVerdict: ${partial.verdict}`);
}

// Get final parsed result
const review = response.parse();
console.log('\n\n--- Final Review ---');
console.log(JSON.stringify(review, null, 2));
