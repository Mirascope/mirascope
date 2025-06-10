#!/usr/bin/env bun

import fs from 'fs';
import path from 'path';
import type { SectionSpec, DocSpec, FullDocsSpec } from '../node_modules/@mirascope/docs-viewer/src/lib/content/spec';

function flattenApiMeta(): void {
  const apiMetaPath = path.join(process.cwd(), '.docs-content/docs/api/_meta.json');
  const mainMetaPath = path.join(process.cwd(), '.docs-content/docs/_meta.json');
  
  if (!fs.existsSync(apiMetaPath)) {
    console.log('No API meta file found, skipping API navigation merge');
    return;
  }

  // Read the generated API meta
  const apiMeta: SectionSpec = JSON.parse(fs.readFileSync(apiMetaPath, 'utf-8'));
  
  // Navigate to the deeply nested API items: api.children[0].children[0].children[0].children
  // Structure: api -> experimental -> v2 -> llm -> [actual API items]
  let apiItems: DocSpec[] = [];
  
  try {
    const experimental = apiMeta.children?.find(child => child.slug === 'experimental');
    const v2 = experimental?.children?.find(child => child.slug === 'v2');
    const llm = v2?.children?.find(child => child.slug === 'llm');
    apiItems = llm?.children || [];
  } catch (e) {
    console.error('Could not extract API items from nested structure:', e);
    return;
  }

  if (apiItems.length === 0) {
    console.log('No API items found in the nested structure');
    return;
  }

  // Add index item at the beginning if it doesn't exist
  const hasIndex = apiItems.some(item => item.slug === 'index');
  if (!hasIndex) {
    apiItems.unshift({
      slug: 'index',
      label: 'Overview',
    });
  }

  // Create a flattened API section
  const flatApiSection: SectionSpec = {
    slug: "api",
    label: "API Reference",
    weight: 1,
    children: apiItems
  };

  // Read and update the main meta file
  const mainMeta: FullDocsSpec = JSON.parse(fs.readFileSync(mainMetaPath, 'utf-8'));
  
  // Add API section to the first product's sections
  if (mainMeta[0] && mainMeta[0].sections) {
    mainMeta[0].sections.push(flatApiSection);
  }
  
  // Write back the merged meta file
  fs.writeFileSync(mainMetaPath, JSON.stringify(mainMeta, null, 2));
  console.log(`Merged ${apiItems.length} API items into main navigation`);
}

// Run the merge
flattenApiMeta();