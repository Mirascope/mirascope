<p align="center">
    <a href="https://mirascope.com/#mirascope">
        <img src="https://github.com/user-attachments/assets/58b04850-8f30-40a6-be68-96ed2aa9b6d8" />
    </a>
</p>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://mirascope.com/docs/mirascope" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/tree/main/LICENSE"><img src="https://img.shields.io/github/license/Mirascope/mirascope.svg" alt="License"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

## Mirascope v2 Alpha

This branch contains Mirascope v2, which is under active development.

## Monorepo Structure

This project is structured as a monorepo, that conceptually divides into four parts:

- `python/` contains the Python implementation, and examples (in `python/examples`)
- `typescript/` contains the Typescript implementation, and examples (in `typescript/examples`)
- `cloud/` contains the full-stack cloud application (React frontend + Cloudflare Workers backend)
- `docs/` contains the unified cross-language documentation (in `docs/content`), as well as configuration needed to build the docs

For detailed information about the codebase structure, architecture, and design decisions, see [`STRUCTURE.md`](STRUCTURE.md).

## Viewing & Building Documentation

Use `bun run docs:dev` to launch the dev server. Note it does not currently have hot reloading; you'll need to restart it on every change.

Use `bun run docs:build` to build the docs, and `bun run docs:preview` to preview the built docs.

Note that [Bun](http://bun.sh/) must be installed.

The docs are automatically built and previewed on every pull request or push.

## CI and local testing

We currently have four CI jobs:
- codespell: Checks for common misspellings including python, typescript, and docs repos
- python-lint: Linting and typechecking for Python code
- typescript-lint: Linting and typechecking for Typescript code
- cloudflare docs build: Builds and previews the documentation site

You can run `bun run ci` in the root directory to run all CI checks locally. If adding new checks to GitHub CI, please also add it to the ci script in root `package.json` as well.

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This repository uses a multi-license structure:

- **Default**: All code is licensed under the [MIT License](https://github.com/Mirascope/mirascope/tree/main/LICENSE) unless otherwise specified.
- **Cloud Directory**: The `cloud/` directory is licensed under a proprietary license. See [`cloud/LICENSE`](cloud/LICENSE) for details.

Subdirectories may contain their own LICENSE files that take precedence for files within those directories.
