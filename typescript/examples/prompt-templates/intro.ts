import { llm } from 'mirascope';

// Functional Style
function recommendGenre(genre: string) {
  return `Recommend a ${genre} book`;
}

// Template Style
const recommendGenreTemplate = llm.promptTemplate<{
  genre: string;
}>`Recommend a {{ genre }} book`;
