import { llm } from 'mirascope';

const simplePromptTemplate = llm.definePromptTemplate`
  Please recommend a book
`;

const genrePromptTemplate = llm.definePromptTemplate<{ genre: string }>`
  Please recommend a {{ genre }} book
`;

type Book = {
  title: string;
  author: string;
};

const bookPromptTemplate = llm.definePromptTemplate<{ book: Book }>`
  Recommend a book like {{ book.title }} by {{ book.author }}.
`;

const multilinePromptTemplate = llm.definePromptTemplate<{ genre: string }>`
  Please recommend a {{ genre }} book.
  Include the title, author, and a brief description.
  Format your response as a numbered list.
`;

// BAD - inconsistent indentation
const badIndentationPromptTemplate = llm.definePromptTemplate`
  [USER] First line
  Second line with different indentation
`;

// GOOD - consistent indentation
const goodIndentationPromptTemplate = llm.definePromptTemplate`
  [USER]
  First line
  Second line with same indentation
`;
