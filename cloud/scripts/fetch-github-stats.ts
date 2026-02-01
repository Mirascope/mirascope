/**
 * Script to fetch GitHub repository stats (stars, latest version)
 * Run with: bun run fetch-github-stats
 */

import fs from "fs";
import https from "https";
import path from "path";

// The repositories to fetch data for
const REPOS = ["Mirascope/mirascope"];

interface RepoStats {
  stars: number;
  latestVersion: string;
}

/**
 * Fetches data from a GitHub API endpoint
 */
async function fetchFromGitHub(endpoint: string): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const headers: Record<string, string> = {
      "User-Agent": "Mirascope-Build-Script",
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
            new Error(
              `GitHub API returned status code ${res.statusCode}: ${res.statusMessage}`,
            ),
          );
        }

        res.on("data", (chunk) => {
          data += chunk;
        });

        res.on("end", () => {
          try {
            const parsed = JSON.parse(data);

            // Check for error message in the response
            if (
              parsed.message &&
              typeof parsed.documentation_url === "string"
            ) {
              return reject(
                new Error(
                  `GitHub API error: ${parsed.message} (${parsed.documentation_url})`,
                ),
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
  const repoData = (await fetchFromGitHub(`/repos/${repo}`)) as {
    stargazers_count: number;
  };

  // Get latest release
  const releases = (await fetchFromGitHub(`/repos/${repo}/releases`)) as Array<{
    prerelease: boolean;
    tag_name: string;
  }>;

  // Find the latest non-prerelease version
  let latestVersion = "v0.0.0";
  if (releases && Array.isArray(releases) && releases.length > 0) {
    const stableReleases = releases.filter((r) => !r.prerelease);
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
  const outputPath = path.join(
    import.meta.dirname,
    "..",
    "app",
    "lib",
    "github-stats.json",
  );
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2) + "\n");

  console.log(`GitHub stats written to ${outputPath}`);
  console.log(results);
}

main().catch((error) => {
  console.error("Error fetching GitHub stats:", error);
  process.exit(1);
});
