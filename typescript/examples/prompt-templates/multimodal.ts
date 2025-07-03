import { llm } from 'mirascope';

const imagePromptTemplate = llm.promptTemplate<{
  bookCover: llm.Image | string | Uint8Array;
}>`
  What book is this? {{ bookCover:image }}
`;

const audioPromptTemplate = llm.promptTemplate<{
  audio: llm.Audio | string | Uint8Array;
}>`
  Analyze this audio recording: {{ audio:audio }}
`;

const videoPromptTemplate = llm.promptTemplate<{
  video: llm.Video | string | Uint8Array;
}>`
  Summarize this video: {{ video:video }}
`;

const documentPromptTemplate = llm.promptTemplate<{
  doc: llm.Document | string | Uint8Array;
}>`
  Review this document: {{ doc:document }}
`;

const imagesPromptTemplate = llm.promptTemplate<{
  covers: Array<llm.Image | string | Uint8Array>;
}>`
  Compare these book covers: {{ covers:images }}
`;

const audiosPromptTemplate = llm.promptTemplate<{
  clips: Array<llm.Audio | string | Uint8Array>;
}>`
  Compare these audio clips: {{ clips:audios }}
`;

const videosPromptTemplate = llm.promptTemplate<{
  clips: Array<llm.Video | string | Uint8Array>;
}>`
  Do these video clips remind you of any book? {{ clips:videos }}
`;

const documentsPromptTemplate = llm.promptTemplate<{
  docs: Array<llm.Document | string | Uint8Array>;
}>`
  Review these documents: {{ docs:documents }}
`;

const mixedMediaPromptTemplate = llm.promptTemplate<{
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
