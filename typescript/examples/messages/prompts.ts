import { llm } from 'mirascope';

const oneShot: llm.Prompt = [llm.messages.user("What's a good book to read?")];

const systemAndUser: llm.Prompt = [
  llm.messages.system(
    'You are a librarian who recommends contemporary young-adult fantasy novels.'
  ),
  llm.messages.user("What's a good book to read?"),
];

const multiTurn: llm.Prompt = [
  llm.messages.system(
    'You are a librarian who recommends contemporary young-adult fantasy novels.'
  ),
  llm.messages.user("What's a good book to read?"),
  llm.messages.assistant('I recommend Name of the Wind, by Patrick Rothfuss'),
  llm.messages.user(
    "I've already read it! Can you suggest something else with magic and music?"
  ),
];

const multiParticipant = [
  llm.messages.user('I need help finding research materials'),
  llm.messages.assistant(
    "I can help you get started. What's your research topic?",
    'ConciergeAgent'
  ),
  llm.messages.user("I'm researching climate change impacts on agriculture"),
  llm.messages.assistant(
    'For academic sources on climate and agriculture, I recommend starting with...',
    'LibrarianAgent'
  ),
];
