import path from "path";
import { glob } from "glob";
import { processMDXContent } from "@/src/lib/content";
import { preprocessMdx } from "@/src/lib/content/mdx-preprocessing";

interface ValidationError {
  type: string;
  message: string;
  line?: number;
  column?: number;
  context?: string;
}

interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

async function validateMDXSyntax(
  content: string,
  filePath: string,
): Promise<ValidationResult> {
  try {
    await processMDXContent(content, { path: filePath });
    return { isValid: true, errors: [] };
  } catch (error) {
    return {
      isValid: false,
      errors: [
        {
          type: "mdx-syntax",
          message: error instanceof Error ? error.message : String(error),
        },
      ],
    };
  }
}

function validateAbsoluteUrls(content: string): ValidationResult {
  const errors: ValidationError[] = [];
  const lines = content.split("\n");
  const urlPattern = /https:\/\/mirascope\.com[^\]"\s)]*/g;

  const allowedAbsoluteUrls = [
    "https://mirascope.com/discord-invite",
    "https://mirascope.com/privacy",
    "https://mirascope.com/",
  ];

  for (let i = 0; i < lines.length; i++) {
    const matches = lines[i].match(urlPattern);
    if (matches) {
      for (const match of matches) {
        if (allowedAbsoluteUrls.includes(match)) {
          continue;
        }

        errors.push({
          type: "absolute-url",
          message: `Absolute Mirascope URL found: "${match}". Use relative URLs instead.`,
          line: i + 1,
          context: lines[i].trim(),
        });
      }
    }
  }

  return { isValid: errors.length === 0, errors };
}

async function validateMdxFile(filePath: string): Promise<ValidationResult> {
  try {
    const { content } = preprocessMdx(filePath);

    const syntaxResult = await validateMDXSyntax(content, filePath);
    const urlsResult = validateAbsoluteUrls(content);

    const allErrors = [...syntaxResult.errors, ...urlsResult.errors];

    return {
      isValid: allErrors.length === 0,
      errors: allErrors,
    };
  } catch (error) {
    return {
      isValid: false,
      errors: [
        {
          type: "preprocessing",
          message: error instanceof Error ? error.message : String(error),
        },
      ],
    };
  }
}

async function validateMdxDirectory(
  dirPath: string,
): Promise<{ file: string; result: ValidationResult }[]> {
  const pattern = path.join(dirPath, "**/*.mdx");
  const files = await glob(pattern, { nodir: true });

  const results: { file: string; result: ValidationResult }[] = [];

  for (const file of files) {
    const result = await validateMdxFile(file);
    results.push({ file, result });
  }

  return results;
}

async function main() {
  const args = process.argv.slice(2);
  const targetPath = args[0] || "content";

  console.log(`Validating MDX files in ${targetPath}...`);

  const results = await validateMdxDirectory(targetPath);
  const errors = results.filter((r) => !r.result.isValid);

  for (const { result } of results) {
    if (result.isValid) {
      process.stdout.write(".");
    } else {
      process.stdout.write("X");
    }
  }

  console.log(`\n\nChecked ${results.length} files`);

  if (errors.length > 0) {
    console.error(`\n❌ Found ${errors.length} MDX files with errors:\n`);

    for (const { file, result } of errors) {
      const relativePath = path.relative(process.cwd(), file);
      console.error(`\n❌ ${relativePath}`);

      const syntaxErrors = result.errors.filter((e) => e.type === "mdx-syntax");
      const urlErrors = result.errors.filter((e) => e.type === "absolute-url");

      if (urlErrors.length > 0) {
        console.error(`\n  Found ${urlErrors.length} absolute URL issues:`);
        for (const err of urlErrors) {
          console.error(`  → Line ${err.line}: ${err.message}`);
          if (err.context) {
            console.error(`    Context: ${err.context}`);
          }
        }
      }

      if (syntaxErrors.length > 0) {
        console.error(`\n  Found ${syntaxErrors.length} MDX syntax issues:`);
        for (const err of syntaxErrors) {
          console.error(`  → ${err.message}`);
        }
      }

      console.error("\n---");
    }

    console.error("\n❌ MDX validation failed. Please fix the errors above.");
    process.exit(1);
  } else {
    console.log("\n🎉 All MDX files are valid!");
  }
}

main().catch((error) => {
  console.error("Validation failed with error:", error);
  process.exit(1);
});
