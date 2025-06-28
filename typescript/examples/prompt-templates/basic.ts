import { llm } from 'mirascope';

const specPromptTemplate = llm.definePromptTemplate<{ genre: string }>`
  [SYSTEM] You are a helpful librarian.
  [USER] Recommend a {{ genre }} book.
`;

const contentPromptTemplate = llm.definePromptTemplate(
  (genre: string) => `Recommend a ${genre} book`
);

const contentSequencePromptTemplate = llm.definePromptTemplate(
  (genre: string) => [
    "I'm looking for a book",
    `Can you recommend one in ${genre}?`,
  ]
);

const messagesPromptTemplate = llm.definePromptTemplate((genre: string) => [
  llm.messages.system('You are a helpful librarian.'),
  llm.messages.user(`I'm looking for a ${genre} book`),
]);
