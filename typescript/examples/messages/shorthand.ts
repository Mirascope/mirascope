import { llm } from 'mirascope';

const systemMessage = llm.messages.system(
  'You are a helpful librarian who recommends books.'
);
const userMessage = llm.messages.user('Can you recommend a good fantasy book?');
const assistantMessage = llm.messages.assistant(
  'I recommend "The Name of the Wind" by Patrick Rothfuss.'
);
