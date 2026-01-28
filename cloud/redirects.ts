/**
 * Programmatic redirects for Cloudflare Workers.
 *
 * Note: Cloudflare Pages `_redirects` file doesn't work with Workers deployments.
 * All redirects must be handled programmatically in the fetch handler.
 */

type RedirectStatus = 301 | 302;

// =============================================================================
// Simple Redirects (exact path match)
// =============================================================================

const simpleRedirects: Record<string, { to: string; status: RedirectStatus }> =
  {
    "/discord-invite": { to: "https://discord.gg/gZMNYR4zEs", status: 301 },
    "/slack-invite": { to: "/discord-invite", status: 302 },
    "/docs/mirascope/getting-started/quickstart": {
      to: "/docs/v1/guides/getting-started/quickstart",
      status: 301,
    },
    // Exact path matches for legacy docs sections (without trailing slash)
    "/docs/mirascope": { to: "/docs/v1", status: 301 },
    "/docs/mirascope/learn": { to: "/docs/v1/learn", status: 301 },
    "/docs/mirascope/guides": { to: "/docs/v1/guides", status: 301 },
    "/docs/mirascope/api": { to: "/docs/v1/api", status: 301 },
  };

// =============================================================================
// Legacy Underscore Paths (redirects old underscore URLs to hyphenated versions)
// =============================================================================

const underscorePaths = [
  // Agents
  "tutorials/agents/blog_writing_agent",
  "tutorials/agents/documentation_agent",
  "tutorials/agents/local_chat_with_codebase",
  "tutorials/agents/localized_agent",
  "tutorials/agents/qwant_search_agent_with_sources",
  "tutorials/agents/sql_agent",
  "tutorials/agents/web_search_agent",
  // Evals
  "tutorials/evals/evaluating_documentation_agent",
  "tutorials/evals/evaluating_sql_agent",
  "tutorials/evals/evaluating_web_search_agent",
  // Getting Started
  "tutorials/getting_started/dynamic_configuration_and_chaining",
  "tutorials/getting_started/structured_outputs",
  "tutorials/getting_started/tools_and_agents",
  // LangGraph vs Mirascope
  "tutorials/langgraph_vs_mirascope/quickstart",
  // More Advanced
  "tutorials/more_advanced/code_generation_and_execution",
  "tutorials/more_advanced/document_segmentation",
  "tutorials/more_advanced/extract_from_pdf",
  "tutorials/more_advanced/extraction_using_vision",
  "tutorials/more_advanced/generating_captions",
  "tutorials/more_advanced/generating_synthetic_data",
  "tutorials/more_advanced/knowledge_graph",
  "tutorials/more_advanced/llm_validation_with_retries",
  "tutorials/more_advanced/named_entity_recognition",
  "tutorials/more_advanced/o1_style_thinking",
  "tutorials/more_advanced/pii_scrubbing",
  "tutorials/more_advanced/query_plan",
  "tutorials/more_advanced/removing_semantic_duplicates",
  "tutorials/more_advanced/search_with_sources",
  "tutorials/more_advanced/speech_transcription",
  "tutorials/more_advanced/support_ticket_routing",
  "tutorials/more_advanced/text_classification",
  "tutorials/more_advanced/text_summarization",
  "tutorials/more_advanced/text_translation",
  // Prompt Engineering - Chaining Based
  "tutorials/prompt_engineering/chaining_based/chain_of_verification",
  "tutorials/prompt_engineering/chaining_based/decomposed_prompting",
  "tutorials/prompt_engineering/chaining_based/demonstration_ensembling",
  "tutorials/prompt_engineering/chaining_based/diverse",
  "tutorials/prompt_engineering/chaining_based/least_to_most",
  "tutorials/prompt_engineering/chaining_based/mixture_of_reasoning",
  "tutorials/prompt_engineering/chaining_based/prompt_paraphrasing",
  "tutorials/prompt_engineering/chaining_based/reverse_chain_of_thought",
  "tutorials/prompt_engineering/chaining_based/self_consistency",
  "tutorials/prompt_engineering/chaining_based/self_refine",
  "tutorials/prompt_engineering/chaining_based/sim_to_m",
  "tutorials/prompt_engineering/chaining_based/skeleton_of_thought",
  "tutorials/prompt_engineering/chaining_based/step_back",
  "tutorials/prompt_engineering/chaining_based/system_to_attention",
  // Prompt Engineering - Text Based
  "tutorials/prompt_engineering/text_based/chain_of_thought",
  "tutorials/prompt_engineering/text_based/common_phrases",
  "tutorials/prompt_engineering/text_based/contrastive_chain_of_thought",
  "tutorials/prompt_engineering/text_based/emotion_prompting",
  "tutorials/prompt_engineering/text_based/plan_and_solve",
  "tutorials/prompt_engineering/text_based/rephrase_and_respond",
  "tutorials/prompt_engineering/text_based/rereading",
  "tutorials/prompt_engineering/text_based/role_prompting",
  "tutorials/prompt_engineering/text_based/self_ask",
  "tutorials/prompt_engineering/text_based/tabular_chain_of_thought",
  "tutorials/prompt_engineering/text_based/thread_of_thought",
  // Provider Specific
  "learn/provider_specific/anthropic",
  "learn/provider_specific/openai",
] as const;

/** Convert underscore path to hyphenated docs path */
const toHyphenatedDocsPath = (path: string): string => {
  const hyphenated = path.replace(/_/g, "-");
  if (path.startsWith("tutorials/")) {
    return `/docs/v1/guides/${hyphenated.slice("tutorials/".length)}`;
  }
  if (path.startsWith("learn/")) {
    return `/docs/v1/learn/${hyphenated.slice("learn/".length)}`;
  }
  return `/${hyphenated}`;
};

// =============================================================================
// Prefix Redirects (splat/wildcard patterns, order matters - specific first)
// =============================================================================

const prefixRedirects: Array<{
  prefix: string;
  to: string;
  status: RedirectStatus;
}> = [
  // todo(sebastian): do we still need these?
  // External legacy redirects (must be before /api/* catch-all)
  {
    prefix: "/integrations/",
    to: "https://legacy.mirascope.com/integrations/",
    status: 301,
  },
  {
    prefix: "/api/integrations/",
    to: "https://legacy.mirascope.com/api/integrations/",
    status: 301,
  },

  // Section redirects (trailing slash ensures path boundary matching)
  { prefix: "/docs/mirascope/", to: "/docs/v1/", status: 301 },
  { prefix: "/docs/mirascope/learn/", to: "/docs/v1/learn/", status: 301 },
  { prefix: "/docs/mirascope/guides/", to: "/docs/v1/guides/", status: 301 },
  { prefix: "/docs/mirascope/api/", to: "/docs/v1/api/", status: 301 },
  { prefix: "/post/", to: "/blog/", status: 301 },
];

// =============================================================================
// Main Handler
// =============================================================================

/**
 * Check if the request path should be redirected.
 * Returns the redirect result or null if no redirect applies.
 */
export const handleRedirect = (request: Request): Response | null => {
  const url = new URL(request.url);
  const pathname = url.pathname;

  // 0. Normalize trailing slashes (except root) with 301 for SEO
  if (pathname !== "/" && pathname.endsWith("/")) {
    const normalized = pathname.slice(0, -1) + url.search;
    return Response.redirect(new URL(normalized, url.origin).toString(), 301);
  }

  // 1. Check simple exact matches
  const simple = simpleRedirects[pathname];
  if (simple) {
    const destination = simple.to.startsWith("/")
      ? new URL(simple.to, url.origin).toString()
      : simple.to;
    return Response.redirect(destination, simple.status);
  }

  // 2. Check underscore paths (with or without trailing content)
  for (const underscorePath of underscorePaths) {
    const oldPath = `/${underscorePath}`;
    if (pathname === oldPath || pathname.startsWith(oldPath + "/")) {
      const destination = new URL(
        toHyphenatedDocsPath(underscorePath),
        url.origin,
      ).toString();
      return Response.redirect(destination, 301);
    }
  }

  // 3. Check prefix redirects (order matters)
  for (const { prefix, to, status } of prefixRedirects) {
    if (pathname.startsWith(prefix)) {
      const splat = pathname.slice(prefix.length);
      const destination = to.startsWith("http")
        ? to + splat
        : new URL(to + splat, url.origin).toString();
      return Response.redirect(destination, status);
    }
  }

  return null;
};
