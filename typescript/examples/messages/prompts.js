"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const mirascope_1 = require("mirascope");
const oneShot = [mirascope_1.llm.messages.user("What's a good book to read?")];
const systemAndUser = [
    mirascope_1.llm.messages.system('You are a librarian who recommends contemporary young-adult fantasy novels.'),
    mirascope_1.llm.messages.user("What's a good book to read?"),
];
const multiTurn = [
    mirascope_1.llm.messages.system('You are a librarian who recommends contemporary young-adult fantasy novels.'),
    mirascope_1.llm.messages.user("What's a good book to read?"),
    mirascope_1.llm.messages.assistant('I recommend Name of the Wind, by Patrick Rothfuss'),
    mirascope_1.llm.messages.user("I've already read it! Can you suggest something else with magic and music?"),
];
const multiParticipant = [
    mirascope_1.llm.messages.user('I need help finding research materials'),
    mirascope_1.llm.messages.assistant("I can help you get started. What's your research topic?", 'ConciergeAgent'),
    mirascope_1.llm.messages.user("I'm researching climate change impacts on agriculture"),
    mirascope_1.llm.messages.assistant('For academic sources on climate and agriculture, I recommend starting with...', 'LibrarianAgent'),
];
