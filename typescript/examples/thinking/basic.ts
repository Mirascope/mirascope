import { llm } from "mirascope";

const solve = llm.defineCall<{ problem: string }>({
  model: "google/gemini-2.5-flash",
  thinking: { level: "high", includeThoughts: true },
  template: ({ problem }) => problem,
});

const response = await solve({
  problem: "What is the first prime number that contains 42 as a substring?",
});
console.log(response.pretty());
