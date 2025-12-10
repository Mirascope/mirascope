/**
 * Script to fetch GitHub repository stats (stars, latest version)
 * Run with: bun run scripts/fetch-github-stats.ts
 */

import fs from "fs";
import path from "path";
import https from "https";

// The repositories to fetch data for
const REPOS = ["Mirascope/mirascope", "Mirascope/lilypad"];

interface RepoStats {
  stars: number;
  latestVersion: string;
}

/**
 * Fetches data from a GitHub API endpoint
 */
async function fetchFromGitHub(endpoint: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const headers: Record<string, string> = {
      "User-Agent": "Mirascope-Website-Build-Script",
    };

    // Use GitHub token from environment if available (for higher rate limits)
    if (process.env.GITHUB_TOKEN) {
      headers["Authorization"] = `token ${process.env.GITHUB_TOKEN}`;
    }

    const options = {
      hostname: "api.github.com",
      path: endpoint,
      headers,
    };

    const req = https
      .get(options, (res) => {
        let data = "";

        // Check for rate limiting or other error status codes
        if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
          return reject(
            new Error(`GitHub API returned status code ${res.statusCode}: ${res.statusMessage}`)
          );
        }

        res.on("data", (chunk) => {
          data += chunk;
        });

        res.on("end", () => {
          try {
            const parsed = JSON.parse(data);

            // Check for error message in the response
            if (parsed.message && parsed.documentation_url) {
              return reject(
                new Error(`GitHub API error: ${parsed.message} (${parsed.documentation_url})`)
              );
            }

            resolve(parsed);
          } catch (e) {
            reject(new Error(`Failed to parse GitHub API response: ${e}`));
          }
        });
      })
      .on("error", (err) => {
        reject(err);
      });

    // Set a timeout to avoid hanging requests
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error("GitHub API request timed out"));
    });
  });
}

/**
 * Get repository stats (stars, latest version)
 */
async function getRepoStats(repo: string): Promise<RepoStats> {
  // Get repository info (including stars)
  const repoData = await fetchFromGitHub(`/repos/${repo}`);

  // Get latest release
  const releases = await fetchFromGitHub(`/repos/${repo}/releases`);

  // Find the latest non-prerelease version
  let latestVersion = "v0.0.0";
  if (releases && Array.isArray(releases) && releases.length > 0) {
    const stableReleases = releases.filter((r: any) => !r.prerelease);
    if (stableReleases.length > 0) {
      latestVersion = stableReleases[0].tag_name;
    } else {
      latestVersion = releases[0].tag_name;
    }
  }

  return {
    stars: repoData.stargazers_count,
    latestVersion,
  };
}

async function main() {
  const results: Record<string, { stars: number; version: string }> = {};

  // Fetch data for each repo
  for (const repo of REPOS) {
    console.log(`Fetching data for ${repo}...`);
    const stats = await getRepoStats(repo);

    // Extract product name from repo (e.g., "Mirascope/mirascope" -> "mirascope")
    const product = repo.split("/")[1].toLowerCase();

    results[product] = {
      stars: stats.stars,
      version: stats.latestVersion,
    };
  }

  // Write results to a JSON file
  const outputPath = path.join(__dirname, "..", "src", "lib", "constants", "github-stats.json");
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));

  console.log(`GitHub stats written to ${outputPath}`);
  console.log(results);
}

main().catch((error) => {
  console.error("Error fetching GitHub stats:", error);
  process.exit(1);
});
