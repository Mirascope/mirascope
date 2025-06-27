import { llm } from 'mirascope';

const recommendGenrePromptTemplate = llm.promptTemplate(
  ({ genre }: { genre: string }) => `Please recommend a ${genre} book`
);

const analyzeImagePromptTemplate = llm.promptTemplate(({ image }: { image: llm.Image }) => [
  'Please recommend a book, based on the themes in this image:',
  image,
]);

const recommendBookPiratePromptTemplate = llm.promptTemplate(
  ({ genre }: { genre: string }) => [
    llm.messages.system('You are a librarian who always talks like a pirate'),
    llm.messages.user(`I want to read a ${genre} book!`),
  ]
);

const recommendGenreAgeAppropriatePromptTemplate = llm.promptTemplate(
  ({ genre, age }: { genre: string; age: number }) => `
    Please recommend a ${genre} book that would be appropriate for a ${age}-year-old reader.
    Include the title, author, and a brief description.
    Make sure the content is age-appropriate and engaging.
    `
);

const piratePromptTemplate = llm.promptTemplate(({ genre }: { genre: string }) => [
  llm.messages.system(
    'You are a conscientious librarian who talks like a pirate.'
  ),
  llm.messages.user('Please recommend a book to me.'),
  llm.messages.assistant(`
    Ahoy there, and greetings, matey!
    What manner of book be ye wanting?
  `),
  llm.messages.user(`I'd like a ${genre} book, please.`),
]);

const imagePromptTemplate = llm.promptTemplate(
  ({ bookCover }: { bookCover: llm.Image }) => ['What book is this?', bookCover]
);

const audioPromptTemplate = llm.promptTemplate(({ audio }: { audio: llm.Audio }) => [
  'Analyze this audio recording:',
  audio,
]);

const videosPromptTemplate = llm.promptTemplate(({ clips }: { clips: llm.Video[] }) => [
  'Do these video clips remind you of any book?',
  ...clips,
]);

const mixedMediaPromptTemplate = llm.promptTemplate(
  ({
    cover,
    narration,
    docs,
  }: {
    cover: llm.Image;
    narration: llm.Audio;
    docs: llm.Document[];
  }) => [
    `
    Analyze this multimedia presentation:
    - Cover image:
    `,
    cover,
    '- Audio narration:',
    narration,
    '- Supporting documents:',
    ...docs,
    'What is the main theme?',
  ]
);

const historyPromptTemplate = llm.promptTemplate(
  ({ history }: { history: llm.Message[] }) => [
    llm.messages.system(
      'You are a summarization agent. Your job is to summarize long discussions.'
    ),
    ...history,
    llm.messages.user(
      'Please summarize our conversation, and recommend a book based on this chat.'
    ),
  ]
);
