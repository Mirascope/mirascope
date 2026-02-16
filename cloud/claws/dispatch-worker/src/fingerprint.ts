/**
 * Deploy fingerprint — generates a human-readable label for each deployment.
 *
 * Uses build-time injected values (__BUILD_TIMESTAMP__, __GIT_SHA__) when
 * available, falling back to runtime values for local development.
 */

const ADJECTIVES = [
  "sparkling",
  "crimson",
  "silent",
  "golden",
  "swift",
  "ancient",
  "blazing",
  "cosmic",
  "dancing",
  "eager",
  "fierce",
  "gentle",
  "hidden",
  "icy",
  "jolly",
  "keen",
  "luminous",
  "mystic",
  "noble",
  "opaque",
  "patient",
  "quiet",
  "radiant",
  "stellar",
  "tender",
  "umbral",
  "vivid",
  "wistful",
  "xenial",
  "yielding",
  "zealous",
  "amber",
  "bold",
  "calm",
  "dusky",
  "emerald",
  "frosty",
  "gusty",
  "hazy",
  "iron",
  "jade",
  "kindled",
  "lunar",
  "mellow",
  "nimble",
  "ochre",
  "plucky",
  "quartz",
  "rustic",
  "sapphire",
] as const;

const ANIMALS = [
  "eagle",
  "fox",
  "otter",
  "hawk",
  "dingo",
  "ibis",
  "panda",
  "lynx",
  "raven",
  "cobra",
  "bison",
  "crane",
  "drake",
  "finch",
  "gecko",
  "heron",
  "impala",
  "jackal",
  "koala",
  "lemur",
  "marten",
  "newt",
  "osprey",
  "puffin",
  "quail",
  "robin",
  "shrike",
  "toucan",
  "urchin",
  "viper",
  "walrus",
  "xerus",
  "yak",
  "zebu",
  "axolotl",
  "badger",
  "condor",
  "dugong",
  "ermine",
  "falcon",
  "grouse",
  "hoopoe",
  "iguana",
  "jaybird",
  "kiwi",
  "lark",
  "myna",
  "narwhal",
  "ocelot",
  "pelican",
] as const;

/** Simple hash: sum of char codes. */
function simpleHash(input: string): number {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash += input.charCodeAt(i);
  }
  return hash;
}

declare const __BUILD_TIMESTAMP__: string | undefined;
declare const __GIT_SHA__: string | undefined;

interface DeployFingerprint {
  label: string;
  timestamp: string;
  sha: string;
  display: string;
}

function getFingerprint(): DeployFingerprint {
  const timestamp =
    typeof __BUILD_TIMESTAMP__ !== "undefined"
      ? __BUILD_TIMESTAMP__
      : new Date().toISOString();
  const sha = typeof __GIT_SHA__ !== "undefined" ? __GIT_SHA__ : "dev";

  const hash = simpleHash(timestamp + sha);
  const adjective = ADJECTIVES[hash % ADJECTIVES.length];
  const animal = ANIMALS[hash % ANIMALS.length];
  const label = `${adjective} ${animal}`;

  return {
    label,
    timestamp,
    sha,
    display: `${label} — ${timestamp} (${sha})`,
  };
}

/** Computed once on import. */
export const BUILD_FINGERPRINT: DeployFingerprint = getFingerprint();
