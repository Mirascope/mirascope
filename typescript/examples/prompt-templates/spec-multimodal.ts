import { llm } from 'mirascope';

const imagePromptTemplate = llm.definePromptTemplate<{
  bookCover: llm.Image | string | Uint8Array;
}>`
  What book is this? {{ bookCover:image }}
`;

const audioPromptTemplate = llm.definePromptTemplate<{
  audio: llm.Audio | string | Uint8Array;
}>`
  Analyze this audio recording: {{ audio:audio }}
`;

const videoPromptTemplate = llm.definePromptTemplate<{
  video: llm.Video | string | Uint8Array;
}>`
  Summarize this video: {{ video:video }}
`;

const documentPromptTemplate = llm.definePromptTemplate<{
  doc: llm.Document | string | Uint8Array;
}>`
  Review this document: {{ doc:document }}
`;

const imagesPromptTemplate = llm.definePromptTemplate<{
  covers: Array<llm.Image | string | Uint8Array>;
}>`
  Compare these book covers: {{ covers:images }}
`;

const audiosPromptTemplate = llm.definePromptTemplate<{
  clips: Array<llm.Audio | string | Uint8Array>;
}>`
  Compare these audio clips: {{ clips:audios }}
`;

const videosPromptTemplate = llm.definePromptTemplate<{
  clips: Array<llm.Video | string | Uint8Array>;
}>`
  Do these video clips remind you of any book? {{ clips:videos }}
`;

const documentsPromptTemplate = llm.definePromptTemplate<{
  docs: Array<llm.Document | string | Uint8Array>;
}>`
  Review these documents: {{ docs:documents }}
`;

const mixedMediaPromptTemplate = llm.definePromptTemplate<{
  cover: llm.Image | string | Uint8Array;
  narration: llm.Audio | string | Uint8Array;
  docs: Array<llm.Document | string | Uint8Array>;
}>`
  Analyze this multimedia presentation:
  - Cover image: {{ cover:image }}
  - Audio narration: {{ narration:audio }}
  - Supporting documents: {{ docs:documents }}
  What is the main theme?
`;
