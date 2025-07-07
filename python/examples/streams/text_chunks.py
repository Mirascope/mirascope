from mirascope import llm

text_chunks = [
    llm.TextChunk(type="text_chunk", delta="I", partial="I"),
    llm.TextChunk(type="text_chunk", delta="recommend", partial="I recommend"),
    llm.TextChunk(type="text_chunk", delta="reading", partial="I recommend reading"),
    llm.TextChunk(
        type="text_chunk",
        delta="Mistborn.",
        partial="I recommend reading Mistborn.",
    ),
]
