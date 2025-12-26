from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 82,
                "output_tokens": 396,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=396, prompt_tokens=82, total_tokens=478, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 478,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is an acclaimed fantasy novel that kicks off the \\"Kingkiller Chronicle\\" series. The story is narrated by the protagonist, Kvothe, who recounts his life tale over the course of three days.\\n\\n**Plot Overview:**\\n- **The setting transitions between two main periods**: Kvothe\'s present, where he lives under the alias Kote as a quiet innkeeper, and his past filled with adventure, talent, and tragedy.\\n- **Young Kvothe** is the son of the Edema Ruh, a group of traveling performers. He shows prodigious skills in music and academics from an early age.\\n- **Tragedy strikes** when Kvothe’s parents are murdered by an enigmatic group known as the Chandrian, setting him on a quest to uncover the truth about them.\\n- **Living on the streets** of Tarbean after losing his family, Kvothe uses his shrewdness and unmatched abilities for survival, eventually finding his way to the prestigious University to study sympathy, an arcane science akin to magic.\\n- At the University, **Kvothe navigates academic rivalry** and discovers his profound musical talent, earning fame with his lute.\\n- He builds important alliances, meets his enigmatic love interest Denna, and learns more about his mysterious foes.\\n\\n**Key Themes:**\\n- The pursuit of knowledge and truth.\\n- The power of names and storytelling.\\n- The complexities of heroism and reputation.\\n\\n**Narrative Style:**\\n- The novel is rich in vivid detail and poetic language, drawing readers deeply into Kvothe\'s world.\\n- It blends personal memoir with high fantasy, weaving in elements of mystery and romance.\\n\\nOverall, \\"The Name of the Wind\\" presents a coming-of-age epic centered around a complex character trying to understand his place in a vast, enchanted world."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": '{"summary":"\\"The Name of the Wind\\" by Patrick Rothfuss is an acclaimed fantasy novel that kicks off the \\"Kingkiller Chronicle\\" series. The story is narrated by the protagonist, Kvothe, who recounts his life tale over the course of three days.\\n\\n**Plot Overview:**\\n- **The setting transitions between two main periods**: Kvothe\'s present, where he lives under the alias Kote as a quiet innkeeper, and his past filled with adventure, talent, and tragedy.\\n- **Young Kvothe** is the son of the Edema Ruh, a group of traveling performers. He shows prodigious skills in music and academics from an early age.\\n- **Tragedy strikes** when Kvothe’s parents are murdered by an enigmatic group known as the Chandrian, setting him on a quest to uncover the truth about them.\\n- **Living on the streets** of Tarbean after losing his family, Kvothe uses his shrewdness and unmatched abilities for survival, eventually finding his way to the prestigious University to study sympathy, an arcane science akin to magic.\\n- At the University, **Kvothe navigates academic rivalry** and discovers his profound musical talent, earning fame with his lute.\\n- He builds important alliances, meets his enigmatic love interest Denna, and learns more about his mysterious foes.\\n\\n**Key Themes:**\\n- The pursuit of knowledge and truth.\\n- The power of names and storytelling.\\n- The complexities of heroism and reputation.\\n\\n**Narrative Style:**\\n- The novel is rich in vivid detail and poetic language, drawing readers deeply into Kvothe\'s world.\\n- It blends personal memoir with high fantasy, weaving in elements of mystery and romance.\\n\\nOverall, \\"The Name of the Wind\\" presents a coming-of-age epic centered around a complex character trying to understand his place in a vast, enchanted world."}',
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 82,
                "output_tokens": 568,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=568, prompt_tokens=82, total_tokens=650, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 650,
            },
            "from_call_args": {
                "author": "Patrick Rothfuss",
                "title": "The Name of the Wind",
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary":"\\"The Name of the Wind\\" is the first book in \\"The Kingkiller Chronicle\\" series by Patrick Rothfuss. It follows the story of Kvothe, an enigmatic musician, magician, and adventurer, recounting his life from childhood to his teenage years spent at the University, a renowned school of magic and arcane studies.\\n\\n### Overview:\\n\\n- **Protagonist:**\\n  Kvothe, a gifted and talented individual with a tragic past, starts his journey as a member of a traveling troupe of performers. The book is narrated from Kvothe\'s perspective as he reflects on his past, intertwined with his current life as an innkeeper hiding under a different name.\\n\\n- **Significant Themes:**\\n  The narrative delves into themes of identity, loss, and the pursuit of knowledge and power. It also explores the interplay between fact and fiction, as Kvothe attempts to set the record straight against the myths that have grown around his name.\\n\\n- **Plot Highlights:**\\n  - The story begins with Kvothe\'s idyllic life with his family in a traveling group known as the Edema Ruh.\\n  - Tragedy strikes when the troupe is massacred by mythical creatures known as the Chandrian, setting Kvothe on a path of revenge.\\n  - His quest for knowledge leads him to the University, where he studies magic and tries to uncover the truth behind the enigmatic Chandrian.\\n  - Throughout his time at the University, Kvothe faces numerous challenges, from rivalries with other students to financial woes, and a forbidden love interest.\\n  - The narrative is interspersed with glimpses into Kvothe\'s current life running an inn, suggesting a mysterious decline from his youthful potential.\\n\\n- **Setting:**\\n  A richly developed fantasy world that blends elements of medieval academia, folklore, and distinctive magical systems.\\n\\n### Character Development:\\n\\n- \\n**Kvothe:** Proved to be a cunning and resourceful protagonist with a tragic backstory that serves as his motivation. His intelligence and charm endear him to some, while his fiery temper and impulsiveness make enemies of others.\\n\\n- \\n**Supporting Characters:**\\n  Include friends, mentors, and adversaries at the University, forming a diverse tapestry of interactions that shape Kvothe\'s journey.\\n\\n### Conclusion:\\n  The book ends without fully resolving the mysteries of Kvothe\'s past or his motivations in the present, setting the stage for the continuation of his saga in the subsequent volumes of the series.\\n\\nOverall, \\"The Name of the Wind\\" is an enthralling tale that combines lyrical storytelling with a deeply immersive world, leaving readers eager to unravel the truths behind Kvothe\'s legendary deeds."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message={
                        "content": '{"summary":"\\"The Name of the Wind\\" is the first book in \\"The Kingkiller Chronicle\\" series by Patrick Rothfuss. It follows the story of Kvothe, an enigmatic musician, magician, and adventurer, recounting his life from childhood to his teenage years spent at the University, a renowned school of magic and arcane studies.\\n\\n### Overview:\\n\\n- **Protagonist:**\\n  Kvothe, a gifted and talented individual with a tragic past, starts his journey as a member of a traveling troupe of performers. The book is narrated from Kvothe\'s perspective as he reflects on his past, intertwined with his current life as an innkeeper hiding under a different name.\\n\\n- **Significant Themes:**\\n  The narrative delves into themes of identity, loss, and the pursuit of knowledge and power. It also explores the interplay between fact and fiction, as Kvothe attempts to set the record straight against the myths that have grown around his name.\\n\\n- **Plot Highlights:**\\n  - The story begins with Kvothe\'s idyllic life with his family in a traveling group known as the Edema Ruh.\\n  - Tragedy strikes when the troupe is massacred by mythical creatures known as the Chandrian, setting Kvothe on a path of revenge.\\n  - His quest for knowledge leads him to the University, where he studies magic and tries to uncover the truth behind the enigmatic Chandrian.\\n  - Throughout his time at the University, Kvothe faces numerous challenges, from rivalries with other students to financial woes, and a forbidden love interest.\\n  - The narrative is interspersed with glimpses into Kvothe\'s current life running an inn, suggesting a mysterious decline from his youthful potential.\\n\\n- **Setting:**\\n  A richly developed fantasy world that blends elements of medieval academia, folklore, and distinctive magical systems.\\n\\n### Character Development:\\n\\n- \\n**Kvothe:** Proved to be a cunning and resourceful protagonist with a tragic backstory that serves as his motivation. His intelligence and charm endear him to some, while his fiery temper and impulsiveness make enemies of others.\\n\\n- \\n**Supporting Characters:**\\n  Include friends, mentors, and adversaries at the University, forming a diverse tapestry of interactions that shape Kvothe\'s journey.\\n\\n### Conclusion:\\n  The book ends without fully resolving the mysteries of Kvothe\'s past or his motivations in the present, setting the stage for the continuation of his saga in the subsequent volumes of the series.\\n\\nOverall, \\"The Name of the Wind\\" is an enthralling tale that combines lyrical storytelling with a deeply immersive world, leaving readers eager to unravel the truths behind Kvothe\'s legendary deeds."}',
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary":"**The Name of the Wind** by Patrick Rothfuss is the first book in the Kingkiller Chronicle series. It is a captivating fantasy novel that recounts the life story of Kvothe, a mysterious and legendary figure known for his remarkable prowess in magic, music, and adventure. \\n\\n---\\n\\n### Plot Overview:\\n\\n- **The Frame Narrative:**  \\nSet in the Waystone Inn, the novel begins with Chronicler, a traveling scribe, seeking to record the true story of the infamous hero Kvothe, who has been living under the guise as an innkeeper named Kote. Reluctantly, Kvothe agrees to tell his life story over the course of three days.\\n\\n- **Kvothe\'s Childhood:**  \\nKvothe grows up as part of a troupe of traveling performers known as the Edema Ruh, with his parents and learns the art of performance, storytelling, and music from an early age. His life takes a tragic turn when his family is brutally murdered by the enigmatic group known as the Chandrian.\\n\\n- **Life on the Streets:**  \\nAfter the massacre, a destitute Kvothe wanders the city of Tarbean, surviving as a street urchin by his wits. This period in his life is marked by hardship, but it also shapes his resourcefulness and resilience.\\n\\n- **University Days:**  \\nEventually, Kvothe makes his way to the prestigious University, where he seeks knowledge of magic to avenge his family. Here he quickly establishes himself as an exceptional student, particularly in the fields of Sympathy (this world\'s form of magic) and music. However, he struggles with bureaucracy, rivalry with fellow student Ambrose, and his own impetuous nature.\\n\\n- **Encounters with Denna:**  \\nThroughout his journey, Kvothe is often beguiled by Denna, a talented and elusive young woman whose path frequently crosses with his. Their complicated relationship adds depth to Kvothe\'s personal development and quest.\\n\\n- **Myths and Mysteries:**  \\nAs Kvothe narrates his tale, readers are introduced to a world rich in legends, folklore, and magical creatures. His quest for the truth about the Chandrian forms the backdrop against which personal growth, friendship, and self-discovery unfold.\\n\\n---\\n\\n### Themes:\\n- The power of names and stories \\n- The search for identity and purpose \\n- The intersection between myth and reality\\n\\n**The Name of the Wind** is both an epic and introspective tale that has captivated readers with its lyrical prose, rich world-building, and intricate narrative. Rothfuss weaves a compelling story of triumph, tragedy, and enduring mystery, laying the groundwork for a multifaceted saga."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 82,
                "output_tokens": 577,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 659,
            },
            "n_chunks": 579,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:completions",
            "provider_model_name": "gpt-4o:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Summarize the book The Name of the Wind by Patrick Rothfuss."
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"summary":"**Title:** The Name of the Wind\\n\\n**Author:** Patrick Rothfuss\\n\\n**Summary:**\\n\\n\\"The Name of the Wind\\" is a captivating fantasy novel that introduces readers to the multifaceted journey of Kvothe, an enigmatic, brilliant, and tragically flawed protagonist. Told through a first-person narrative, the story unfolds as Kvothe, now living under the plain guise of an innkeeper named Kote, recounts the tale of his fascinating and tumultuous past to a chronicler seeking to capture his life story.\\n\\n**The Narrative Arc:**\\n\\n1. **Early Beginnings:**\\n   - Kvothe is raised by a troupe of traveling performers, the Edema Ruh, who nurture his early talents in storytelling, music, and wit. His idyllic life is shattered by the slaughter of his family at the hands of the mysterious meddlers known as the Chandrian.\\n   \\n2. **Survival on the Streets:**\\n   - Traumatized and alone, young Kvothe survives on the streets of the bustling city of Tarbean, relying on his resourcefulness, intelligence, and a poetic heart.\\n   \\n3. **Quest for Knowledge:**\\n   - Driven by a desperate need for answers and a resolute determination to avenge his family, Kvothe ventures to the University, an esteemed institution of magic and learning. Amidst the academic challenges, he often clashes with arrogant and wealthy rivals.\\n\\n4. **Intricate Magic and Shaping Destiny:**\\n   - At the University, Kvothe becomes a master in the arts of sympathy—a unique form of magic. He earns recognition for his musical talent, instrumental in winning his way and making unexpected alliances and enemies.\\n\\n5. **The Enigma of Denna:**\\n   - Throughout his tale, Kvothe\'s path intertwines with Denna, a beautiful and elusive woman. Their complicated relationship depicts the themes of unattainable love and fleeting connections.\\n\\n6. **Encounters and Legends:**\\n   - Kvothe\'s adventures grow mythic, as he tackles puzzles about the Chandrian and begins unraveling ancient myths surrounding the name of the wind—a potent force he seeks to harness.\\n\\nThe book is masterfully woven with lyrical prose, filled with intrigue, emotion, and innovation in world-building. Rothfuss intricately layers Kvothe\'s life across an expansive realm, combining elements of mystery, magic, and character development to present a memorable start to the \\"Kingkiller Chronicle\\" series."}'
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:completions",
                    provider_model_name="gpt-4o:completions",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "Book",
                "description": "A book with title, author, and summary.",
                "schema": {
                    "description": "A book with title, author, and summary.",
                    "properties": {"summary": {"title": "Summary", "type": "string"}},
                    "required": ["summary"],
                    "title": "Book",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [],
            "usage": {
                "input_tokens": 82,
                "output_tokens": 525,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 607,
            },
            "n_chunks": 527,
        }
    }
)
