import { llm } from 'mirascope';

const recommend_book_prompt: llm.Prompt = [
  llm.messages.user('Recommend a book'),
];

const recommend_fantasy_book_prompt: llm.Prompt = [
  llm.messages.user('Recommend a fantasy book'),
];

const recommend_scifi_book_prompt: llm.Prompt = [
  llm.messages.user('Recommend a science fiction book'),
];

const recommend_genre_prompt_template = llm.definePromptTemplate(
  (genre: string) => [llm.messages.user(`Recommend a ${genre} book`)]
);

const recommend_genre_prompt_template_from_spec = llm.definePromptTemplate<{
  genre: string;
}>`Recommend a {{ genre }} book`;
