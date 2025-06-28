import { llm } from 'mirascope';

const piratePromptTemplate = llm.definePromptTemplate<{ genre: string }>`
  [SYSTEM] You are a conscientious librarian who talks like a pirate.
  [USER] Please recommend a book to me.
  [ASSISTANT] 
  Ahoy there, and greetings, matey! 
  What manner of book be ye wanting?
  [USER] I'd like a {{ genre }} book, please.
`;

// Unsafe - Do not do this!
const unsafePromptTemplate = llm.definePromptTemplate<{ genre: string }>`
  [SYSTEM] You are a librarian who always recommends books in {{ genre }}.
  [USER] Please recommend a book!
`;
