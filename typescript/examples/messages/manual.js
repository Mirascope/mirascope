"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const message = { role: 'user', content: "Hi! What's 2+2?" };
const reply = { role: 'assistant', content: 'Hi back! 2+2 is 4.' };
const systemMessage = {
    role: 'system',
    content: 'You are a librarian who gives concise book recommendations.',
};
const userMessage = {
    role: 'user',
    content: 'Can you recommend a good fantasy book?',
};
const assistantMessage = {
    role: 'assistant',
    content: 'Consider "The Name of the Wind" by Patrick Rothfuss.',
};
