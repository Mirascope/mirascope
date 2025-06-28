import { llm } from 'mirascope';
import { readFileSync } from 'fs';

const historyPromptTemplate = llm.definePromptTemplate<{
  history: llm.Message[];
}>`
  [SYSTEM] You are a summarization agent. Your job is to summarize long discussions.
  [MESSAGES] {{ history }}
  [USER] Please summarize our conversation, and recommend a book based on this chat.
`;

const templateContent = readFileSync('book_recommendation.txt', 'utf-8');

const fileBasedPromptTemplate = llm.definePromptTemplate<{
  genre: string;
}>`${templateContent}`;
