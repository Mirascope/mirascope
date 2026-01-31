# Mirascope Registry

The Mirascope Registry is a collection of reusable AI components (tools, agents, prompts, integrations) that can be installed into your projects using the Mirascope CLI.

## Quick Start

### 1. Initialize your project

Create a `mirascope.json` configuration file:

```bash
# Python
mirascope registry init

# TypeScript
npx mirascope registry init
```

This creates a config file with default paths:

```json
{
  "$schema": "https://mirascope.com/registry/schema/config.json",
  "language": "python",
  "registry": "https://mirascope.com/registry",
  "paths": {
    "tools": "ai/tools",
    "agents": "ai/agents",
    "prompts": "ai/prompts",
    "integrations": "ai/integrations"
  }
}
```

### 2. Browse available items

List all registry items:

```bash
# Python
mirascope registry list

# TypeScript
npx mirascope registry list
```

Filter by type:

```bash
mirascope registry list --type tool
mirascope registry list --type agent
```

Or browse the web UI at [mirascope.com/registry](https://mirascope.com/registry).

### 3. Add items to your project

```bash
# Python
mirascope registry add calculator

# TypeScript
npx mirascope registry add calculator
```

This will:
1. Download the item files from the registry
2. Write them to the configured path (e.g., `ai/tools/calculator.py`)
3. Display any dependencies you need to install

### 4. Install dependencies

After adding items, install any required dependencies:

```bash
# Python (shown after adding)
uv add <dependencies>

# TypeScript (shown after adding)
bun add <dependencies>
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `registry init` | Create mirascope.json config |
| `registry list` | List available items |
| `registry list --type <type>` | Filter by type (tool, agent, prompt, integration) |
| `registry add <item>` | Add item to your project |
| `registry add <item> --path <dir>` | Add to custom directory |
| `registry add <item> --overwrite` | Overwrite existing files |

## Configuration

### mirascope.json

```json
{
  "$schema": "https://mirascope.com/registry/schema/config.json",
  "language": "python",
  "registry": "https://mirascope.com/registry",
  "paths": {
    "tools": "ai/tools",
    "agents": "ai/agents",
    "prompts": "ai/prompts",
    "integrations": "ai/integrations"
  }
}
```

| Field | Description |
|-------|-------------|
| `language` | `"python"` or `"typescript"` |
| `registry` | Base URL for the registry |
| `paths` | Where to install each item type |

## Programmatic Access

The registry is accessible via JSON endpoints:

- **Index**: `https://mirascope.com/r/index.json`
- **Python item**: `https://mirascope.com/r/{name}.python.json`
- **TypeScript item**: `https://mirascope.com/r/{name}.typescript.json`

---

## Local Development & Testing

### Building the Registry

When adding or modifying registry items, rebuild the registry:

```bash
# From repo root
bun run registry:build
```

This generates:
- `cloud/public/r/index.json` - Registry index
- `cloud/public/r/{name}.python.json` - Python items
- `cloud/public/r/{name}.typescript.json` - TypeScript items
- `cloud/public/registry.md` - Static markdown for /registry.md

### Testing Locally

To test the registry CLI against a local dev server:

#### 1. Start the local server

```bash
cd cloud
bun run dev
# Server runs at http://localhost:3000
```

#### 2. Create a test project

```bash
mkdir ~/test-registry && cd ~/test-registry
```

#### 3. Initialize with local registry URL

**Python:**
```bash
# If mirascope is installed from the local repo
cd /path/to/mirascope/python
uv run mirascope registry init --registry http://localhost:3000

# Or manually create mirascope.json
```

**TypeScript:**
```bash
# Run the local CLI directly
cd /path/to/mirascope/typescript
bun run src/cli/main.ts registry init --registry http://localhost:3000
```

#### 4. List items from local registry

**Python:**
```bash
uv run mirascope registry list --registry http://localhost:3000
```

**TypeScript:**
```bash
bun run src/cli/main.ts registry list --registry http://localhost:3000
```

#### 5. Add an item from local registry

**Python:**
```bash
uv run mirascope registry add calculator --registry http://localhost:3000
```

**TypeScript:**
```bash
bun run src/cli/main.ts registry add calculator --registry http://localhost:3000
```

### Testing the Web UI

1. Start the dev server: `cd cloud && bun run dev`
2. Navigate to `http://localhost:3000/registry`
3. Toggle between HUMAN and MACHINE modes using the switcher in the bottom-right
4. Test search and filter functionality
5. Expand cards to see install commands

### Adding New Registry Items

1. Create a new directory under `registry/`:
   ```
   registry/
   └── tools/
       └── my-tool/
           ├── registry-item.json
           ├── my_tool.py
           └── my-tool.ts
   ```

2. Define the item in `registry-item.json`:
   ```json
   {
     "name": "my-tool",
     "type": "registry:tool",
     "title": "My Tool",
     "description": "Description of my tool",
     "version": "1.0.0",
     "categories": ["utility"],
     "mirascope": {
       "python": { "minVersion": "1.0.0" },
       "typescript": { "minVersion": "1.0.0" }
     },
     "files": {
       "python": [
         { "path": "my_tool.py", "target": "my_tool.py" }
       ],
       "typescript": [
         { "path": "my-tool.ts", "target": "my-tool.ts" }
       ]
     },
     "dependencies": {
       "pip": [],
       "npm": []
     },
     "registryDependencies": []
   }
   ```

   **Important**: The `target` should be just the filename (e.g., `my_tool.py`), not a full path. The user's `mirascope.json` config determines where files are installed based on the item type. For example, a `registry:tool` item with `target: "my_tool.py"` will be installed to `ai/tools/my_tool.py` if the user's config has `paths.tools: "ai/tools"`.

3. Add the item to `registry/registry.json`:
   ```json
   {
     "items": [
       { "name": "my-tool", "type": "tool", "path": "tools/my-tool" }
     ]
   }
   ```

4. Build the registry:
   ```bash
   bun run registry:build
   ```

5. Test locally (see above)

## Questions?

Join our community at [mirascope.com/discord-invite](https://mirascope.com/discord-invite) to ask the team directly.
