import { llm } from 'mirascope';

const specPromptTemplate = llm.promptTemplate<{ genre: string }>`
  [SYSTEM] You are a helpful librarian.
  [USER] Recommend a {{ genre }} book.
`;

const contentPromptTemplate = llm.promptTemplate(
  ({ genre }: { genre: string }) => `Recommend a ${genre} book`
);

const contentSequencePromptTemplate = llm.promptTemplate(
  ({ genre }: { genre: string }) => [
    "I'm looking for a book",
    `Can you recommend one in ${genre}?`,
  ]
);

const messagesPromptTemplate = llm.promptTemplate(
  ({ genre }: { genre: string }) => [
    llm.messages.system('You are a helpful librarian.'),
    llm.messages.user(`I'm looking for a ${genre} book`),
  ]
);
