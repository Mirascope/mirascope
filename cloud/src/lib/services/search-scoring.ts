import { type ContentMeta, type DocMeta } from "../content/content";

// Raw search result from Pagefind before weighting
export interface RawSearchResult {
  title: string;
  excerpt: string;
  url: string;
  section: string;
  score: number; // Original score from Pagefind
  meta?: ContentMeta; // Optional content metadata if found
}

// Final search result after weighting has been applied
export interface SearchResultItem {
  title: string;
  excerpt: string;
  url: string;
  section: string;
  rawScore: number; // Original score from Pagefind
  weight: number; // Weight applied based on content type
  score: number; // Final score (rawScore × weight)
  meta: ContentMeta; // Content metadata (required)
}

// Configuration for search scoring
export interface ScoringConfig {
  titleBoostMultiplier: number;
  contentTypeWeights: {
    blog: number;
    policy: number;
    dev: number;
    docs: number;
  };
}

// Default scoring configuration
export const DEFAULT_SCORING_CONFIG: ScoringConfig = {
  titleBoostMultiplier: 2.0,
  contentTypeWeights: {
    blog: 0.33,
    policy: 0.25,
    dev: 0, // Effectively removes from results
    docs: 1.0, // Multiplied by DocMeta searchWeight if available
  },
};

/**
 * Handles all search result scoring and ranking logic
 */
export class SearchScorer {
  constructor(private config: ScoringConfig = DEFAULT_SCORING_CONFIG) {}

  /**
   * Get the search weight for a content item based on its metadata
   *
   * Applies different weights according to content type (see scoring config)
   */
  getContentWeight(meta: ContentMeta | undefined): number {
    // If no metadata, use default weight
    if (!meta) return 1.0;

    // Determine weight based on content type
    switch (meta.type) {
      case "blog":
        return this.config.contentTypeWeights.blog;
      case "policy":
        return this.config.contentTypeWeights.policy;
      case "dev":
        return this.config.contentTypeWeights.dev;
      case "docs":
        // For docs, use the searchWeight from DocMeta
        const docMeta = meta as DocMeta;
        return docMeta.searchWeight * this.config.contentTypeWeights.docs;
      default:
        return 1.0;
    }
  }

  /**
   * Calculate title boost based on query-title term overlap
   *
   * Uses simple stemming to handle variations like "call" vs "calls"
   * Splits on both spaces and dots for API-style titles like "mirascope.core.azure"
   */
  calculateTitleBoost(query: string, title: string): number {
    const queryTerms = this.tokenizeAndStem(query);
    const titleTerms = this.tokenizeAndStem(title);

    if (queryTerms.length === 0) return 1.0;

    // Count how many query terms have matches in the title
    const matchingTerms = queryTerms.filter((queryTerm) =>
      titleTerms.some((titleTerm) => queryTerm === titleTerm),
    ).length;

    // Calculate coverage ratio
    const coverageRatio = matchingTerms / queryTerms.length;

    // Apply boost: 1 + (coverage × multiplier)
    return 1 + coverageRatio * this.config.titleBoostMultiplier;
  }

  /**
   * Tokenize text and apply simple stemming
   * Splits on spaces and dots, converts to lowercase, removes common suffixes
   */
  private tokenizeAndStem(text: string): string[] {
    return text
      .toLowerCase()
      .split(/[\s.]+/)
      .filter((token) => token.length > 0)
      .map((token) => this.simpleStem(token));
  }

  /**
   * Apply simple stemming by removing common English suffixes
   */
  private simpleStem(word: string): string {
    return word.replace(/(?:ing|ed|er|est|s)$/i, "");
  }

  /**
   * Apply custom scoring logic to search results
   *
   * Transforms raw search results into weighted and boosted search results:
   * 1. Filters out results without metadata
   * 2. Applies content-type-specific weights
   * 3. Applies title-based boosting
   * 4. Sorts by final weighted score
   */
  scoreAndRankResults(
    rawResults: RawSearchResult[],
    query: string,
  ): SearchResultItem[] {
    // Filter out results without metadata
    const resultsWithMeta = rawResults.filter(
      (result) => result.meta !== undefined,
    );

    // Transform raw results into weighted results
    const weightedResults: SearchResultItem[] = resultsWithMeta.map(
      (rawResult) => {
        // Get content type weight (meta is guaranteed to exist from the filter above)
        const weight = this.getContentWeight(rawResult.meta);
        const titleBoost = this.calculateTitleBoost(query, rawResult.title);
        const rawScore = rawResult.score;

        // Calculate the final score with both content weight and title boost
        const score = rawScore * weight * titleBoost;

        // Create the weighted result with all required fields
        return {
          title: rawResult.title,
          excerpt: rawResult.excerpt,
          url: rawResult.url,
          section: rawResult.section,
          rawScore: rawScore,
          weight: weight,
          score: score,
          meta: rawResult.meta!, // Non-null assertion is safe due to the filter above
        };
      },
    );

    // Filter out items with zero weight or score
    const filteredItems = weightedResults.filter((item) => item.score > 0);

    // Sort by adjusted score (highest first)
    const sortedItems = filteredItems.sort((a, b) => b.score - a.score);

    return sortedItems;
  }
}
