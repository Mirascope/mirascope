# Mirascope's Philosophy

When we first started building with LLMs, we struggled to find the right tooling. Every library had it’s own unique quirks, but they all shared one key aspect that never sat well with us — magic.

As developers, we rely on abstractions to offset the cumbersome nature of working directly with model providers' API's. Abstractions and their resulting convenience are good! But… it's a slippery slope. In search of "magic," frameworks hide too many features, have too many nested layers, and take things one step too far. What works for a demo suddenly becomes a nightmare for a real project. You find yourself spending more time reading through the framework's API than the model provider's own, searching for a workaround for the shackles that this "magic" has imposed on you.  This isn't what we wanted.

*Low level abstractions. Maximum control. This is our philosophy.*

### Transparency

Being in control starts with transparency, and transparency starts with ease of use. Editor support via autocomplete with detailed docstrings. Clear, up to date documentation and an API reference which draws directly from the source code. Precise typing so linting catches nasty and annoying bugs. *When working with Mirascope, we show you exactly what each piece of code does.*

Transparency also means limiting what we abstract. Calling the LLM, defining tools, extracting structured information — we provide conveniences for the annoying things, but it's never forced. *For any convenience we provide, we will always give you the option of manual implementation with examples in our docs.*

If you do dive into the source code of our conveniences (which you should never have to do if we're doing things right), you will see clearly how we call the model provider's API according to your specification. *You should never have to learn more Mirascope just for the sake of doing what you could have always done in plain Python.*

### Modularity

Everything "AI" is moving too quickly for "all-or-nothing" frameworks. Anything you make with Mirascope should be easy to integrate with the countless other toolkits that offer other, specialized functionalities within the LLM development space.

As an extension of transparency, we make it easy to *use and access* the raw classes from the model provider, whether it's as input or output. This way, Mirascope can seamlessly slot into your workflow anywhere, anytime. *We're not a framework that locks you in.* *We provide simple building blocks that make it easy to build what you want the way you want to.*

### Colocation

By colocation, we mean that we try our best to ensure anything and everything that can impact the quality of your call to an LLM is located together in one place. *Colocation reduces the number of moving parts and makes it easy to control and iterate on the quality of your calls.*

So what are you waiting for? Go give it a shot.
