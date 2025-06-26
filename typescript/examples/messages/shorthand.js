"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const mirascope_1 = require("mirascope");
const systemMessage = mirascope_1.llm.messages.system('You are a helpful librarian who recommends books.');
const userMessage = mirascope_1.llm.messages.user('Can you recommend a good fantasy book?');
const assistantMessage = mirascope_1.llm.messages.assistant('I recommend "The Name of the Wind" by Patrick Rothfuss.');
