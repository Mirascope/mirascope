# Mirascope’s Philosophy

When we first started building with LLMs, we struggled to find the right tooling. Every library had it’s own unique quirks, but they all shared one key aspect that never sat well with me — magic.

One downstream effect of this documentation is that any Mirascope functionality you use is clearly explained right there where you’re using it. What’s happening “under-the-hood” should be in plain sight.

Don’t get me wrong. Magic can be cool. Really cool sometimes. But it often gets in the way. Especially when LLMs are already magical enough.

What we wanted was a set of building blocks so that we could build our own tools easily. We wanted the annoying little things to just work so we could focus on items with higher value-add. But we didn’t want to buy-in to an all-or-nothing framework only to inevitably rip it all out when some assumptions they made were wrong for our use-case. Instead, we wanted convenience around the core modules of building with LLMs with full access to any nitty-gritty details as necessary.

When done right, this isn’t magic — but it *feels* like magic. This is the core of our philosophy.

## 1. No Magic

This starts with editor support and clear, up-to-date documentation. I’m talking about autocomplete with detailed docstrings. Lint errors that prevent nasty and annoying bugs. The things we’ve come to expect from our development environments. We rely on these tools to engineer effectively and efficiently. If you rarely need to read our docs, we’re doing our job right.

Furthermore, the functionality itself should not obscure any of the underlying functionality supported by the LLM provider’s API. Instead it should make using such functionality simple and seamless.

## 2. Convenient, Not Convoluted

Abstractions are useful, but they can quickly become bloat. As systems become more complex, too many abstractions get in your way. They often make it difficult or impossible to do what you want. You have to work around the abstractions, which is often hacky.

At Mirascope, we try our best to limit what we abstract. Building with Mirascope will feel convenient. It will feel like we take care of all the things you don’t want to think about so you can focus on the meat of your problem — the stuff you’re excited to build.

## 3. Modular and Pythonic

We also wanted to minimize what you need to learn to build with LLMs, and the things you *do* need to learn should be familiar and feel like writing the Python you’re already used to writing.

Everything “AI” is moving too quickly for “all-or-nothing” frameworks. It should be easy to slot in whatever module we want — especially raw Python.

We don’t want a framework. We want a toolkit. We want building blocks.

## 4. Colocation

Colocation defines the boundaries of our modules. We try our best to limit our classes such they they contain and colocate anything that can impact the results of using that class. Everything that can impact the results should be versioned together. Things like the prompt template, temperature, model, and other call parameters. When extracting structured information, the schema to be extracted should be colocated with the call for extracting it. The prompt template for that extraction should be engineered to best extract that schema. It should all be versioned together.

## 5. Extensible

We’re building a toolkit, not a framework. Mirascope hopes to make building *your own AI tools* as delightful as possible. This is similar in spirit to something like [shadcn](https://ui.shadcn.com/).
