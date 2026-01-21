import { llm } from 'mirascope';

const message: llm.Message = { role: 'user', content: "Hi! What's 2+2?" };
const reply: llm.Message = { role: 'assistant', content: 'Hi back! 2+2 is 4.' };

const systemMessage: llm.Message = {
  role: 'system',
  content: 'You are a librarian who gives concise book recommendations.',
};
const userMessage: llm.Message = {
  role: 'user',
  content: 'Can you recommend a good fantasy book?',
};
const assistantMessage: llm.Message = {
  role: 'assistant',
  content: 'Consider "The Name of the Wind" by Patrick Rothfuss.',
};
