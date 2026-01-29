import { llm } from 'mirascope';

const recommendBook = llm.defineCall<{ genre: string }>({
  model: 'anthropic/claude-haiku-4-5',
  maxTokens: 1024,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

const response = await recommendBook({ genre: 'fantasy' });
console.log(response.text());
