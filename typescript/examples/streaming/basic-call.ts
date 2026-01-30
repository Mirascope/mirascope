import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-5-mini",
  template: ({ genre }) => `Recommend a ${genre} book`,
});

const response = await recommendBook.stream({ genre: "fantasy " });

process.stdout.write("Streaming: ");
for await (const text of response.textStream()) {
  process.stdout.write(text);
}
console.log("\n");
