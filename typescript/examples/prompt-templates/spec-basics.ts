import { llm } from 'mirascope';

const simplePromptTemplate = llm.promptTemplate`
  Please recommend a book
`;

const genrePromptTemplate = llm.promptTemplate<{ genre: string }>`
  Please recommend a {{ genre }} book
`;

type Book = {
  title: string;
  author: string;
};

const bookPromptTemplate = llm.promptTemplate<{ book: Book }>`
  Recommend a book like {{ book.title }} by {{ book.author }}.
`;

const multilinePromptTemplate = llm.promptTemplate<{ genre: string }>`
  Please recommend a {{ genre }} book.
  Include the title, author, and a brief description.
  Format your response as a numbered list.
`;

// BAD - inconsistent indentation
const badIndentationPromptTemplate = llm.promptTemplate`
  [USER] First line
  Second line with different indentation
`;

// GOOD - consistent indentation
const goodIndentationPromptTemplate = llm.promptTemplate`
  [USER]
  First line
  Second line with same indentation
`;
