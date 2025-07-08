from mirascope import llm

text_chunks = [
    llm.TextChunk(type="text_chunk", delta="I"),
    llm.TextChunk(type="text_chunk", delta="recommend"),
    llm.TextChunk(type="text_chunk", delta="reading"),
    llm.TextChunk(type="text_chunk", delta="Mistborn."),
]
