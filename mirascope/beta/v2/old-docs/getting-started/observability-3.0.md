---
icon: telescope
---

# Observability 3.0

> AI Engineers simultaneously program in all 3 paradigms. It's a bit 😵‍💫
>
> — Andrej Karpathy

We highly recommend instrumenting any project that you're working on from the beginning.

If you don't trace and version everything, how will you determine if your changes are actually improving the system?

## Lilypad

With [Lilypad](https://app.gitbook.com/o/ezvv8NDXZ8o1gG96RwYr/s/pGMXFubFyptiiuRdVj0d/), you can get observability and versioning in two lines of code:

<pre class="language-python"><code class="lang-python">import lilypad
from mirascope import llm

<strong>lilypad.configure()
</strong>
<strong>@lilypad.trace(versioning="automatic")
</strong>@llm.generation()
def recommend_book(genre: str) -> list[llm.Message]:
    return [
        llm.User(f"Recommend a {genre} book"),
    ]
    
with llm.model("openai:gpt-4o"):
    response: llm.Response = recommend_book("fantasy")
    print(response.content)
    # > Certainly! I recommend "The Name of the Wind" by...
</code></pre>

You can also [annotate](https://app.gitbook.com/s/pGMXFubFyptiiuRdVj0d/evaluation/annotations) your data and run [experiments](https://app.gitbook.com/s/pGMXFubFyptiiuRdVj0d/experiments) to determine if your changes are actually improving the system.

