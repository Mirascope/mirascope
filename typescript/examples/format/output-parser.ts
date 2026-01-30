/**
 * Example using OutputParser for custom output formats.
 *
 * Shows how to use defineOutputParser() to handle non-JSON formats
 * like XML, CSV, or any custom format.
 *
 * Run with: bun run example examples/format/output-parser.ts
 */
import { llm } from 'mirascope';

// Define the target type
interface Person {
  name: string;
  age: number;
  occupation: string;
  city: string;
}

// Create an OutputParser for XML format
const xmlPersonParser = llm.defineOutputParser<Person>({
  formattingInstructions: `
Respond only with valid XML in this exact format:
<person>
  <name>Full Name</name>
  <age>Number</age>
  <occupation>Job Title</occupation>
  <city>City Name</city>
</person>
Do not include any text before or after the XML.
`.trim(),

  parser: (response) => {
    const text = response.text();

    // Simple XML parsing (in production, use a proper XML parser)
    const nameMatch = text.match(/<name>([^<]+)<\/name>/);
    const ageMatch = text.match(/<age>(\d+)<\/age>/);
    const occupationMatch = text.match(/<occupation>([^<]+)<\/occupation>/);
    const cityMatch = text.match(/<city>([^<]+)<\/city>/);

    return {
      name: nameMatch?.[1] ?? 'Unknown',
      age: parseInt(ageMatch?.[1] ?? '0', 10),
      occupation: occupationMatch?.[1] ?? 'Unknown',
      city: cityMatch?.[1] ?? 'Unknown',
    };
  },
});

// Create a call using the custom output parser
// Use defineCall<VarsType>()({...}) to specify variables type while inferring format type.
const generatePerson = llm.defineCall<{ description: string }>()({
  model: 'anthropic/claude-haiku-4-5',
  maxTokens: 512,
  format: xmlPersonParser,
  template: ({ description }) =>
    `Generate a fictional person who ${description}.`,
});

const response = await generatePerson({
  description: 'is a software engineer living in a major tech hub',
});

const person = response.parse();

console.log('Generated Person (from XML):');
console.log('============================\n');
console.log(`Name: ${person.name}`);
console.log(`Age: ${person.age}`);
console.log(`Occupation: ${person.occupation}`);
console.log(`City: ${person.city}`);

console.log('\n--- Raw Response ---');
console.log(response.text());
