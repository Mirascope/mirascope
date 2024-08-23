# Changelog

## [v1.0.2](https://github.com/Mirascope/mirascope/releases/tag/v1.0.2) - 2024-08-22

## What's Changed
* docs: update theme, logo, and migration guide by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/431](https://github.com/Mirascope/mirascope/pull/431)
* docs: typo and missing args in docstring by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/430](https://github.com/Mirascope/mirascope/pull/430)
* docs: update migration guide re: statelessness by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/434](https://github.com/Mirascope/mirascope/pull/434)
* fix: ruff target python version to py310 by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/435](https://github.com/Mirascope/mirascope/pull/435)
* fix: avoid unnecessary function definitions by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/436](https://github.com/Mirascope/mirascope/pull/436)
* fix: ignore overload in coverage by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/437](https://github.com/Mirascope/mirascope/pull/437)
* fix: remove `# pragma: no cover` from all abstractmethod by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/438](https://github.com/Mirascope/mirascope/pull/438)
* switch from poetry to uv and add pre-commit hooks by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/439](https://github.com/Mirascope/mirascope/pull/439)
* Add ruff rules by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/442](https://github.com/Mirascope/mirascope/pull/442)
* docs: update setup guide for uv by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/440](https://github.com/Mirascope/mirascope/pull/440)
* docs: update response models docs to have few-shot examples section by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/443](https://github.com/Mirascope/mirascope/pull/443)
* docs: add built-in types section to response models docs by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/444](https://github.com/Mirascope/mirascope/pull/444)
* added langgraph quickstart mirascope version by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/441](https://github.com/Mirascope/mirascope/pull/441)
* docs: update response model docs and fix a few issues here and there by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/446](https://github.com/Mirascope/mirascope/pull/446)
* fix: issue with  getting kwargs with model_dump by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/447](https://github.com/Mirascope/mirascope/pull/447)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.1...v1.0.2](https://github.com/Mirascope/mirascope/compare/v1.0.1...v1.0.2)

## [v1.0.1](https://github.com/Mirascope/mirascope/releases/tag/v1.0.1) - 2024-08-18

## What's Changed
* fix: structured streaming + json mode bug (and a typo) by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/429](https://github.com/Mirascope/mirascope/pull/429)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.0...v1.0.1](https://github.com/Mirascope/mirascope/compare/v1.0.0...v1.0.1)

## [v1.0.0](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0) - 2024-08-17

## What's Changed
* Add ToolKit for new interface by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/340](https://github.com/Mirascope/mirascope/pull/340)
* Learn: philosophy by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/343](https://github.com/Mirascope/mirascope/pull/343)
* added initial work to fix/clean up tool streaming by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/346](https://github.com/Mirascope/mirascope/pull/346)
* fix: tools (sync vs. async) + streaming (cost tracking and linting) by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/351](https://github.com/Mirascope/mirascope/pull/351)
* feat: beta rag by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/352](https://github.com/Mirascope/mirascope/pull/352)
* Multimodal Support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/353](https://github.com/Mirascope/mirascope/pull/353)
* Structured streaming updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/354](https://github.com/Mirascope/mirascope/pull/354)
* Multimodal audio support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/355](https://github.com/Mirascope/mirascope/pull/355)
* Test `mirascope.core.base`: 100% coverages by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/357](https://github.com/Mirascope/mirascope/pull/357)
* Test core openai by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/358](https://github.com/Mirascope/mirascope/pull/358)
* fixed pyright errors and reorganized integrations, and added tests for integrations by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/356](https://github.com/Mirascope/mirascope/pull/356)
* Anthropic tests by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/360](https://github.com/Mirascope/mirascope/pull/360)
* fix: add test openai api key so client creation doesn't fail by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/361](https://github.com/Mirascope/mirascope/pull/361)
* tests: gemini and updates call_response and call_response_chunk interfaces to remain consistent across providers by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/362](https://github.com/Mirascope/mirascope/pull/362)
* Update message params + LiteLLM updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/363](https://github.com/Mirascope/mirascope/pull/363)
* Cohere tests by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/364](https://github.com/Mirascope/mirascope/pull/364)
* Remaining Core Tests For 100% Coverage by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/365](https://github.com/Mirascope/mirascope/pull/365)
* Minor BaseTool (and corresponding provider tool) updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/366](https://github.com/Mirascope/mirascope/pull/366)
* fix: remaining issues with imports, ensuring that optional imports are truly optional by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/367](https://github.com/Mirascope/mirascope/pull/367)
* Mistral cost tracking update by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/368](https://github.com/Mirascope/mirascope/pull/368)
* Readme updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/369](https://github.com/Mirascope/mirascope/pull/369)
* fix: issue with gemini returning a proto object for lists when using tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/370](https://github.com/Mirascope/mirascope/pull/370)
* Further test prompt template parser by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/373](https://github.com/Mirascope/mirascope/pull/373)
* Initial cookbook templates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/375](https://github.com/Mirascope/mirascope/pull/375)
* Construct call response from Stream by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/374](https://github.com/Mirascope/mirascope/pull/374)
* Blog writing agent recipe by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/377](https://github.com/Mirascope/mirascope/pull/377)
* fixed some bugs and finalized logfire by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/378](https://github.com/Mirascope/mirascope/pull/378)
* fix: attempt 1 at fixing workflows so they can act as checks by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/379](https://github.com/Mirascope/mirascope/pull/379)
* Beta openai structured outputs by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/381](https://github.com/Mirascope/mirascope/pull/381)
* Documentation by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/382](https://github.com/Mirascope/mirascope/pull/382)
* chore: adding initial finalized chaining examples for review by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/376](https://github.com/Mirascope/mirascope/pull/376)
* updated tenacity integration by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/380](https://github.com/Mirascope/mirascope/pull/380)
* docs: update text classification cookbook recipe by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/384](https://github.com/Mirascope/mirascope/pull/384)
* added pdf extraction cookbook by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/383](https://github.com/Mirascope/mirascope/pull/383)
* added web scraping cookbook by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/385](https://github.com/Mirascope/mirascope/pull/385)
* Documentation by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/389](https://github.com/Mirascope/mirascope/pull/389)
* docs: streams by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/391](https://github.com/Mirascope/mirascope/pull/391)
* docs: tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/392](https://github.com/Mirascope/mirascope/pull/392)
* docs: dynamic configuration by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/394](https://github.com/Mirascope/mirascope/pull/394)
* docs: chaining by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/395](https://github.com/Mirascope/mirascope/pull/395)
* docs: json mode by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/396](https://github.com/Mirascope/mirascope/pull/396)
* docs: response model by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/397](https://github.com/Mirascope/mirascope/pull/397)
* docs: output parsers by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/398](https://github.com/Mirascope/mirascope/pull/398)
* docs: evals by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/399](https://github.com/Mirascope/mirascope/pull/399)
* docs: async by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/400](https://github.com/Mirascope/mirascope/pull/400)
* docs: agents + random fixes by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/401](https://github.com/Mirascope/mirascope/pull/401)
* docs: learn index by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/402](https://github.com/Mirascope/mirascope/pull/402)
* Documentation by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/403](https://github.com/Mirascope/mirascope/pull/403)
* added knowledge graph cookbook by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/390](https://github.com/Mirascope/mirascope/pull/390)
* Documentation by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/404](https://github.com/Mirascope/mirascope/pull/404)
* docs: tenacity by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/406](https://github.com/Mirascope/mirascope/pull/406)
* docs: finalize existing integration docs and examples by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/407](https://github.com/Mirascope/mirascope/pull/407)
* docs: help and contributing finalization by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/408](https://github.com/Mirascope/mirascope/pull/408)
* docs: get started guide + changelog + litellm minor fix by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/409](https://github.com/Mirascope/mirascope/pull/409)
* chore: update poetry lock by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/411](https://github.com/Mirascope/mirascope/pull/411)
* fix: BasePrompt not working with additional decorators by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/413](https://github.com/Mirascope/mirascope/pull/413)
* added extraction using vision by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/412](https://github.com/Mirascope/mirascope/pull/412)
* added code generation by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/405](https://github.com/Mirascope/mirascope/pull/405)
* fix typing for integration decorators outfacing by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/415](https://github.com/Mirascope/mirascope/pull/415)
* docs: API Reference by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/416](https://github.com/Mirascope/mirascope/pull/416)
* docs: learn <-> api reference linking + improvements by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/419](https://github.com/Mirascope/mirascope/pull/419)
* added query plan by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/420](https://github.com/Mirascope/mirascope/pull/420)
* added pii scrubbing by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/414](https://github.com/Mirascope/mirascope/pull/414)
* added document segmentation cookbook by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/417](https://github.com/Mirascope/mirascope/pull/417)
* removed semantic duplicates by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/421](https://github.com/Mirascope/mirascope/pull/421)
* added support ticket routing by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/418](https://github.com/Mirascope/mirascope/pull/418)
* added speech transcription by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/422](https://github.com/Mirascope/mirascope/pull/422)
* made updates to docs by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/423](https://github.com/Mirascope/mirascope/pull/423)
* V1 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/425](https://github.com/Mirascope/mirascope/pull/425)

## New Contributors
* [@koxudaxi](https://github.com/koxudaxi) made their first contribution in [https://github.com/Mirascope/mirascope/pull/340](https://github.com/Mirascope/mirascope/pull/340)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.18.3...v1.0.0](https://github.com/Mirascope/mirascope/compare/v0.18.3...v1.0.0)

## [v0.18.3](https://github.com/Mirascope/mirascope/releases/tag/v0.18.3) - 2024-08-11

## What's Changed
* Fix openai breaking change by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/387](https://github.com/Mirascope/mirascope/pull/387)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.18.2...v0.18.3](https://github.com/Mirascope/mirascope/compare/v0.18.2...v0.18.3)

## [v1.0.0-b6](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0-b6) - 2024-08-09

## What's Changed
* fix: issue with gemini returning a proto object for lists when using tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/370](https://github.com/Mirascope/mirascope/pull/370)
* Further test prompt template parser by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/373](https://github.com/Mirascope/mirascope/pull/373)
* Initial cookbook templates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/375](https://github.com/Mirascope/mirascope/pull/375)
* Construct call response from Stream by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/374](https://github.com/Mirascope/mirascope/pull/374)
* Blog writing agent recipe by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/377](https://github.com/Mirascope/mirascope/pull/377)
* fixed some bugs and finalized logfire by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/378](https://github.com/Mirascope/mirascope/pull/378)
* fix: attempt 1 at fixing workflows so they can act as checks by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/379](https://github.com/Mirascope/mirascope/pull/379)
* Beta openai structured outputs by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/381](https://github.com/Mirascope/mirascope/pull/381)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.0-b5...v1.0.0-b6](https://github.com/Mirascope/mirascope/compare/v1.0.0-b5...v1.0.0-b6)

## [v1.0.0-b5](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0-b5) - 2024-08-02

## What's Changed
* Test `mirascope.core.base`: 100% coverages by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/357](https://github.com/Mirascope/mirascope/pull/357)
* Test core openai by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/358](https://github.com/Mirascope/mirascope/pull/358)
* fixed pyright errors and reorganized integrations, and added tests for integrations by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/356](https://github.com/Mirascope/mirascope/pull/356)
* Anthropic tests by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/360](https://github.com/Mirascope/mirascope/pull/360)
* fix: add test openai api key so client creation doesn't fail by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/361](https://github.com/Mirascope/mirascope/pull/361)
* tests: gemini and updates call_response and call_response_chunk interfaces to remain consistent across providers by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/362](https://github.com/Mirascope/mirascope/pull/362)
* Update message params + LiteLLM updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/363](https://github.com/Mirascope/mirascope/pull/363)
* Cohere tests by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/364](https://github.com/Mirascope/mirascope/pull/364)
* Remaining Core Tests For 100% Coverage by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/365](https://github.com/Mirascope/mirascope/pull/365)
* Minor BaseTool (and corresponding provider tool) updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/366](https://github.com/Mirascope/mirascope/pull/366)
* fix: remaining issues with imports, ensuring that optional imports are truly optional by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/367](https://github.com/Mirascope/mirascope/pull/367)
* Mistral cost tracking update by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/368](https://github.com/Mirascope/mirascope/pull/368)
* Readme updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/369](https://github.com/Mirascope/mirascope/pull/369)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.0-b4...v1.0.0-b5](https://github.com/Mirascope/mirascope/compare/v1.0.0-b4...v1.0.0-b5)

## [v1.0.0-b4](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0-b4) - 2024-07-19

## What's Changed
* added initial work to fix/clean up tool streaming by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/346](https://github.com/Mirascope/mirascope/pull/346)
* fix: tools (sync vs. async) + streaming (cost tracking and linting) by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/351](https://github.com/Mirascope/mirascope/pull/351)
* feat: beta rag by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/352](https://github.com/Mirascope/mirascope/pull/352)
* Multimodal Support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/353](https://github.com/Mirascope/mirascope/pull/353)
* Structured streaming updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/354](https://github.com/Mirascope/mirascope/pull/354)
* Multimodal audio support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/355](https://github.com/Mirascope/mirascope/pull/355)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.0-b3...v1.0.0-b4](https://github.com/Mirascope/mirascope/compare/v1.0.0-b3...v1.0.0-b4)

## [v0.18.2](https://github.com/Mirascope/mirascope/releases/tag/v0.18.2) - 2024-07-16

## What's Changed
* updated pinecone version by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/350](https://github.com/Mirascope/mirascope/pull/350)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.18.1...v0.18.2](https://github.com/Mirascope/mirascope/compare/v0.18.1...v0.18.2)

## [v1.0.0-b3](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0-b3) - 2024-07-08

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v1.0.0-b1...v1.0.0-b3](https://github.com/Mirascope/mirascope/compare/v1.0.0-b1...v1.0.0-b3)

## [v1.0.0-b1](https://github.com/Mirascope/mirascope/releases/tag/v1.0.0-b1) - 2024-06-29

## What's Changed
* Add ToolKit for new interface by [@koxudaxi](https://github.com/koxudaxi) in [https://github.com/Mirascope/mirascope/pull/340](https://github.com/Mirascope/mirascope/pull/340)
* Learn: philosophy by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/343](https://github.com/Mirascope/mirascope/pull/343)

## New Contributors
* [@koxudaxi](https://github.com/koxudaxi) made their first contribution in [https://github.com/Mirascope/mirascope/pull/340](https://github.com/Mirascope/mirascope/pull/340)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.17.0...v1.0.0-b1](https://github.com/Mirascope/mirascope/compare/v0.17.0...v1.0.0-b1)

## [v0.18.1](https://github.com/Mirascope/mirascope/releases/tag/v0.18.1) - 2024-06-29

- Fix issue with Gemini extraction using tools where `Literal` and `Enum` were missing the `{"format": "enum"}` setting

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.18.0...v0.18.1](https://github.com/Mirascope/mirascope/compare/v0.18.0...v0.18.1)

## [v0.18.0](https://github.com/Mirascope/mirascope/releases/tag/v0.18.0) - 2024-06-18

## What's Changed
* GCP Wrapper by [@VVoruganti](https://github.com/VVoruganti) in [https://github.com/Mirascope/mirascope/pull/338](https://github.com/Mirascope/mirascope/pull/338)
* Adding weaviate integration by [@aowen14](https://github.com/aowen14) in [https://github.com/Mirascope/mirascope/pull/339](https://github.com/Mirascope/mirascope/pull/339)

## New Contributors
* [@VVoruganti](https://github.com/VVoruganti) made their first contribution in [https://github.com/Mirascope/mirascope/pull/338](https://github.com/Mirascope/mirascope/pull/338)
* [@aowen14](https://github.com/aowen14) made their first contribution in [https://github.com/Mirascope/mirascope/pull/339](https://github.com/Mirascope/mirascope/pull/339)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.17.0...v0.18.0](https://github.com/Mirascope/mirascope/compare/v0.17.0...v0.18.0)

## [v0.17.0](https://github.com/Mirascope/mirascope/releases/tag/v0.17.0) - 2024-06-15

## What's Changed
* docs: add more chaining examples by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/301](https://github.com/Mirascope/mirascope/pull/301)
* feat: updated mirascope logfire span data for custom panels by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/302](https://github.com/Mirascope/mirascope/pull/302)
* fixed comments mentioned in issue [#293](https://github.com/Mirascope/mirascope/issues/293) by [@tvj15](https://github.com/tvj15) in [https://github.com/Mirascope/mirascope/pull/303](https://github.com/Mirascope/mirascope/pull/303)
* Fix dependency issue by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/306](https://github.com/Mirascope/mirascope/pull/306)
* Convenience for generating the assistant message parameter from the response of a call by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/308](https://github.com/Mirascope/mirascope/pull/308)
* feat: otel llm updates by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/307](https://github.com/Mirascope/mirascope/pull/307)
* feat: add  to call response types by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/310](https://github.com/Mirascope/mirascope/pull/310)
* fix: moved tags in logfire so they show up in ui by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/314](https://github.com/Mirascope/mirascope/pull/314)
* docs: updated writing_prompts docs and added additional examples by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/315](https://github.com/Mirascope/mirascope/pull/315)
* feat: streaming classes for additional streaming convenience by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/317](https://github.com/Mirascope/mirascope/pull/317)
* docs: fix typos and bad examples, added new example by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/316](https://github.com/Mirascope/mirascope/pull/316)
* feat: streaming content and tools together by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/329](https://github.com/Mirascope/mirascope/pull/329)
* docs: added multiple examples and docs updates to chat history by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/323](https://github.com/Mirascope/mirascope/pull/323)
* docs: updated retrying docs and added some basic examples by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/324](https://github.com/Mirascope/mirascope/pull/324)
* docs: updated examples for extraction and docs by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/325](https://github.com/Mirascope/mirascope/pull/325)
* docs: updated dynamic call/extraction generation examples and docs by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/326](https://github.com/Mirascope/mirascope/pull/326)
* docs: example usage with flask, django, and instructor, and tool calls by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/328](https://github.com/Mirascope/mirascope/pull/328)
* docs: updated docs and examples with v0.17 changes by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/330](https://github.com/Mirascope/mirascope/pull/330)
* feat: add name and description classmethods + call method to BaseTool by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/331](https://github.com/Mirascope/mirascope/pull/331)
* docs: added streaming example to chat history by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/333](https://github.com/Mirascope/mirascope/pull/333)
* feat: add a  class for organizing tools under a single namespace by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/334](https://github.com/Mirascope/mirascope/pull/334)
* docs: show how to use examples with tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/336](https://github.com/Mirascope/mirascope/pull/336)
* Feat: tool message parameter creation utilities for response types and stream types by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/337](https://github.com/Mirascope/mirascope/pull/337)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.16.1...v0.17.0](https://github.com/Mirascope/mirascope/compare/v0.16.1...v0.17.0)

## [v0.16.1](https://github.com/Mirascope/mirascope/releases/tag/v0.16.1) - 2024-06-05

## What's Changed
* fix: tool.args issue by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/300](https://github.com/Mirascope/mirascope/pull/300)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.16.0...v0.16.1](https://github.com/Mirascope/mirascope/compare/v0.16.0...v0.16.1)

## [v0.16.0](https://github.com/Mirascope/mirascope/releases/tag/v0.16.0) - 2024-06-04

## What's Changed
* feat: Track costs for streaming with OpenAI by [@tvj15](https://github.com/tvj15) in [https://github.com/Mirascope/mirascope/pull/282](https://github.com/Mirascope/mirascope/pull/282)
* feat: added util functions create_extractor and create_call by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/286](https://github.com/Mirascope/mirascope/pull/286)
* fix: issue where using AzureOpenAI required OPENAI_API_KEY by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/297](https://github.com/Mirascope/mirascope/pull/297)

## New Contributors
* [@tvj15](https://github.com/tvj15) made their first contribution in [https://github.com/Mirascope/mirascope/pull/282](https://github.com/Mirascope/mirascope/pull/282)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.15.2...v0.16.0](https://github.com/Mirascope/mirascope/compare/v0.15.2...v0.16.0)

## [v0.15.2](https://github.com/Mirascope/mirascope/releases/tag/v0.15.2) - 2024-06-03

## What's Changed
* Fix handle callbacks async by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/295](https://github.com/Mirascope/mirascope/pull/295)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.15.1...v0.15.2](https://github.com/Mirascope/mirascope/compare/v0.15.1...v0.15.2)

## [v0.15.1](https://github.com/Mirascope/mirascope/releases/tag/v0.15.1) - 2024-05-30

## What's Changed
* Fix HyperDX docs by [@MikeShi42](https://github.com/MikeShi42) in [https://github.com/Mirascope/mirascope/pull/288](https://github.com/Mirascope/mirascope/pull/288)
* fix: dependency issue.  by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/291](https://github.com/Mirascope/mirascope/pull/291)

## New Contributors
* [@MikeShi42](https://github.com/MikeShi42) made their first contribution in [https://github.com/Mirascope/mirascope/pull/288](https://github.com/Mirascope/mirascope/pull/288)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.15.0...v0.15.1](https://github.com/Mirascope/mirascope/compare/v0.15.0...v0.15.1)

## [v0.15.0](https://github.com/Mirascope/mirascope/releases/tag/v0.15.0) - 2024-05-30

## What's Changed
* chore: updated chaining docs to match video flow by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/277](https://github.com/Mirascope/mirascope/pull/277)
* Feature/with otel by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/280](https://github.com/Mirascope/mirascope/pull/280)
* Update README.md with details on pip install for zsh by [@wcbudz](https://github.com/wcbudz) in [https://github.com/Mirascope/mirascope/pull/283](https://github.com/Mirascope/mirascope/pull/283)
* docs: added mirascope evaluations section and code example by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/284](https://github.com/Mirascope/mirascope/pull/284)
* Support for AnthropicBedrock and AzureOpenAI by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/285](https://github.com/Mirascope/mirascope/pull/285)
* fix: issue with streaming where AzureOpenAI would not accept stream_options by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/287](https://github.com/Mirascope/mirascope/pull/287)

## New Contributors
* [@wcbudz](https://github.com/wcbudz) made their first contribution in [https://github.com/Mirascope/mirascope/pull/283](https://github.com/Mirascope/mirascope/pull/283)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.14.1...v0.15.0](https://github.com/Mirascope/mirascope/compare/v0.14.1...v0.15.0)

## [v0.15.0-b2](https://github.com/Mirascope/mirascope/releases/tag/v0.15.0-b2) - 2024-05-29

## What's Changed
* docs: added mirascope evaluations section and code example by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/284](https://github.com/Mirascope/mirascope/pull/284)
* Support for AnthropicBedrock and AzureOpenAI by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/285](https://github.com/Mirascope/mirascope/pull/285)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.15.0-b1...v0.15.0-b2](https://github.com/Mirascope/mirascope/compare/v0.15.0-b1...v0.15.0-b2)

## [v0.15.0-b1](https://github.com/Mirascope/mirascope/releases/tag/v0.15.0-b1) - 2024-05-28

## What's Changed
* chore: updated chaining docs to match video flow by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/277](https://github.com/Mirascope/mirascope/pull/277)
* Feature/with otel by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/280](https://github.com/Mirascope/mirascope/pull/280)
* Update README.md with details on pip install for zsh by [@wcbudz](https://github.com/wcbudz) in [https://github.com/Mirascope/mirascope/pull/283](https://github.com/Mirascope/mirascope/pull/283)

## New Contributors
* [@wcbudz](https://github.com/wcbudz) made their first contribution in [https://github.com/Mirascope/mirascope/pull/283](https://github.com/Mirascope/mirascope/pull/283)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.14.1...v0.15.0-b1](https://github.com/Mirascope/mirascope/compare/v0.14.1...v0.15.0-b1)

## [v0.14.1](https://github.com/Mirascope/mirascope/releases/tag/v0.14.1) - 2024-05-23

## What's Changed
* Add Support for Llama3 Models in groq_api_calculate_cost Function by [@Khaleelhabeeb](https://github.com/Khaleelhabeeb) in [https://github.com/Mirascope/mirascope/pull/272](https://github.com/Mirascope/mirascope/pull/272)
* chore: run ruff format on the codebase by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/275](https://github.com/Mirascope/mirascope/pull/275)

## New Contributors
* [@Khaleelhabeeb](https://github.com/Khaleelhabeeb) made their first contribution in [https://github.com/Mirascope/mirascope/pull/272](https://github.com/Mirascope/mirascope/pull/272)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.14.0...v0.14.1](https://github.com/Mirascope/mirascope/compare/v0.14.0...v0.14.1)

## [v0.14.0](https://github.com/Mirascope/mirascope/releases/tag/v0.14.0) - 2024-05-21

## What's Changed
* Added reusable wrapper and implemented reusable wrapper for logfire (and other ops providers) by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/244](https://github.com/Mirascope/mirascope/pull/244)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.5...v0.14.0](https://github.com/Mirascope/mirascope/compare/v0.13.5...v0.14.0)

## [v0.13.5](https://github.com/Mirascope/mirascope/releases/tag/v0.13.5) - 2024-05-21

## What's Changed
* fix: issue where you couldn't pass in the tool call without a follow-up user message by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/267](https://github.com/Mirascope/mirascope/pull/267)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.4...v0.13.5](https://github.com/Mirascope/mirascope/compare/v0.13.4...v0.13.5)

## [v0.13.4](https://github.com/Mirascope/mirascope/releases/tag/v0.13.4) - 2024-05-21

## What's Changed
* Fix chat history for tool calls by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/263](https://github.com/Mirascope/mirascope/pull/263)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.3...v0.13.4](https://github.com/Mirascope/mirascope/compare/v0.13.3...v0.13.4)

## [v0.13.3](https://github.com/Mirascope/mirascope/releases/tag/v0.13.3) - 2024-05-18

## What's Changed
* docs: update tools doc code to work properly by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/253](https://github.com/Mirascope/mirascope/pull/253)
* fix: unnecessary prevention of tool calls for finish reason by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/257](https://github.com/Mirascope/mirascope/pull/257)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.2...v0.13.3](https://github.com/Mirascope/mirascope/compare/v0.13.2...v0.13.3)

## [v0.13.2](https://github.com/Mirascope/mirascope/releases/tag/v0.13.2) - 2024-05-16

## What's Changed
* docs: update example names to be more clear by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/248](https://github.com/Mirascope/mirascope/pull/248)
* docs: clean up docs that are separate to be individual docs with sections by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/249](https://github.com/Mirascope/mirascope/pull/249)
* fix: fix issue with empty messages array injection by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/252](https://github.com/Mirascope/mirascope/pull/252)
* Fix print statement of task_details by [@off6atomic](https://github.com/off6atomic) in [https://github.com/Mirascope/mirascope/pull/250](https://github.com/Mirascope/mirascope/pull/250)

## New Contributors
* [@off6atomic](https://github.com/off6atomic) made their first contribution in [https://github.com/Mirascope/mirascope/pull/250](https://github.com/Mirascope/mirascope/pull/250)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.1...v0.13.2](https://github.com/Mirascope/mirascope/compare/v0.13.1...v0.13.2)

## [v0.13.1](https://github.com/Mirascope/mirascope/releases/tag/v0.13.1) - 2024-05-15

## What's Changed
* bugfix: property in messages called 3 times by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/246](https://github.com/Mirascope/mirascope/pull/246)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.13.0...v0.13.1](https://github.com/Mirascope/mirascope/compare/v0.13.0...v0.13.1)

## [v0.13.0](https://github.com/Mirascope/mirascope/releases/tag/v0.13.0) - 2024-05-14

## What's Changed
* docs: update docs and issue templates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/235](https://github.com/Mirascope/mirascope/pull/235)
* feat: added langfuse integration by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/231](https://github.com/Mirascope/mirascope/pull/231)
* fix: use tenacity when retries > 1 instead of always  by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/237](https://github.com/Mirascope/mirascope/pull/237)
* feat: added cost tracking for openai and cost tracking doc by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/239](https://github.com/Mirascope/mirascope/pull/239)
* chore: update docs to make it more clear what prompt template is doing by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/241](https://github.com/Mirascope/mirascope/pull/241)
* Chaining and retries docs updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/243](https://github.com/Mirascope/mirascope/pull/243)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.12.3...v0.13.0](https://github.com/Mirascope/mirascope/compare/v0.12.3...v0.13.0)

## [v0.13.0-beta](https://github.com/Mirascope/mirascope/releases/tag/v0.13.0-beta) - 2024-05-13

## What's Changed
* docs: update docs and issue templates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/235](https://github.com/Mirascope/mirascope/pull/235)
* feat: added langfuse integration by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/231](https://github.com/Mirascope/mirascope/pull/231)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.12.3...v0.13.0-beta](https://github.com/Mirascope/mirascope/compare/v0.12.3...v0.13.0-beta)

## [v0.12.3](https://github.com/Mirascope/mirascope/releases/tag/v0.12.3) - 2024-05-10

## What's Changed
* fix: allow non-role keywords to be parsed as part of the actual role keyword by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/233](https://github.com/Mirascope/mirascope/pull/233)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.12.2...v0.12.3](https://github.com/Mirascope/mirascope/compare/v0.12.2...v0.12.3)

## [v0.12.2](https://github.com/Mirascope/mirascope/releases/tag/v0.12.2) - 2024-05-09

## What's Changed
* fix: anthropic json mode tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/230](https://github.com/Mirascope/mirascope/pull/230)
* fix: issue with GPT returning an assistant message tool call instead of an actual tool call :( by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/229](https://github.com/Mirascope/mirascope/pull/229)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.12.1...v0.12.2](https://github.com/Mirascope/mirascope/compare/v0.12.1...v0.12.2)

## [v0.12.1](https://github.com/Mirascope/mirascope/releases/tag/v0.12.1) - 2024-05-09

## What's Changed
* fix: updated streaming to behave like instrument_openai by logfire by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/213](https://github.com/Mirascope/mirascope/pull/213)
* chore: contributing updates by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/217](https://github.com/Mirascope/mirascope/pull/217)
* fix: issue with not properly setting messages from extractor in temp call by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/223](https://github.com/Mirascope/mirascope/pull/223)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.12.0...v0.12.1](https://github.com/Mirascope/mirascope/compare/v0.12.0...v0.12.1)

## [v0.12.0](https://github.com/Mirascope/mirascope/releases/tag/v0.12.0) - 2024-05-07

## What's Changed
* feat: better retries by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/208](https://github.com/Mirascope/mirascope/pull/208)
* Logfire updates for tool calls by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/211](https://github.com/Mirascope/mirascope/pull/211)
* feat: add retry for calls/stream by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/210](https://github.com/Mirascope/mirascope/pull/210)
* chore: updated docs with retries by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/212](https://github.com/Mirascope/mirascope/pull/212)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.5...v0.12.0](https://github.com/Mirascope/mirascope/compare/v0.11.5...v0.12.0)

## [v0.11.5](https://github.com/Mirascope/mirascope/releases/tag/v0.11.5) - 2024-05-02

## What's Changed
* Fix extract properties by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/207](https://github.com/Mirascope/mirascope/pull/207)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.4...v0.11.5](https://github.com/Mirascope/mirascope/compare/v0.11.4...v0.11.5)

## [v0.11.4](https://github.com/Mirascope/mirascope/releases/tag/v0.11.4) - 2024-05-01

## What's Changed
* bugfix: fix logfire hierarchy & gemini by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/206](https://github.com/Mirascope/mirascope/pull/206)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.3...v0.11.4](https://github.com/Mirascope/mirascope/compare/v0.11.3...v0.11.4)

## [v0.11.3](https://github.com/Mirascope/mirascope/releases/tag/v0.11.3) - 2024-04-30

## What's Changed
* bugfix: added __all__ to __init__.py to fix reportPrivateImportUsage by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/205](https://github.com/Mirascope/mirascope/pull/205)
* Expose `with_logfire` from mirascope.logfire by [@barapa](https://github.com/barapa) in [https://github.com/Mirascope/mirascope/pull/202](https://github.com/Mirascope/mirascope/pull/202)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.2...v0.11.3](https://github.com/Mirascope/mirascope/compare/v0.11.2...v0.11.3)

## [v0.11.2](https://github.com/Mirascope/mirascope/releases/tag/v0.11.2) - 2024-04-30

## What's Changed
* Additional support for all providers to show up nicely in the Logfire UI by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/204](https://github.com/Mirascope/mirascope/pull/204)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.1...v0.11.2](https://github.com/Mirascope/mirascope/compare/v0.11.1...v0.11.2)

## [v0.11.1](https://github.com/Mirascope/mirascope/releases/tag/v0.11.1) - 2024-04-30

## What's Changed
* fix: properties not getting copied over to TempCall from extractor by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/201](https://github.com/Mirascope/mirascope/pull/201)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.11.0...v0.11.1](https://github.com/Mirascope/mirascope/compare/v0.11.0...v0.11.1)

## [v0.11.0](https://github.com/Mirascope/mirascope/releases/tag/v0.11.0) - 2024-04-30

## What's Changed
* docs: fix typo in llama_index.md by [@eltociear](https://github.com/eltociear) in [https://github.com/Mirascope/mirascope/pull/194](https://github.com/Mirascope/mirascope/pull/194)
* feat: added cohere embeddings and updated openai embeddings by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/195](https://github.com/Mirascope/mirascope/pull/195)
* Update docs and examples by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/196](https://github.com/Mirascope/mirascope/pull/196)
* chore: add 3.12 to test workflow by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/128](https://github.com/Mirascope/mirascope/pull/128)
* feat: logfire integration by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/198](https://github.com/Mirascope/mirascope/pull/198)

## New Contributors
* [@eltociear](https://github.com/eltociear) made their first contribution in [https://github.com/Mirascope/mirascope/pull/194](https://github.com/Mirascope/mirascope/pull/194)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.10.0...v0.11.0](https://github.com/Mirascope/mirascope/compare/v0.10.0...v0.11.0)

## [v0.10.0](https://github.com/Mirascope/mirascope/releases/tag/v0.10.0) - 2024-04-18

## What's Changed
* feat: enable easier injection of list attributes and properties by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/177](https://github.com/Mirascope/mirascope/pull/177)
* feat: rag by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/176](https://github.com/Mirascope/mirascope/pull/176)
* Feat: Streaming Tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/178](https://github.com/Mirascope/mirascope/pull/178)
* fet: weave rag by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/180](https://github.com/Mirascope/mirascope/pull/180)
* Cohere support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/181](https://github.com/Mirascope/mirascope/pull/181)
* chore: rag docs by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/182](https://github.com/Mirascope/mirascope/pull/182)
* Additional tool streaming support for Anthropic by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/184](https://github.com/Mirascope/mirascope/pull/184)
* feat: rag by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/183](https://github.com/Mirascope/mirascope/pull/183)
* chore: remove CLI with new release of separate package by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/186](https://github.com/Mirascope/mirascope/pull/186)
* feat: added pinecone vectorstore by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/185](https://github.com/Mirascope/mirascope/pull/185)
* feat: added cost tracking to each provider except Gemini by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/187](https://github.com/Mirascope/mirascope/pull/187)
* Docs updates in prep for v0.10 release by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/188](https://github.com/Mirascope/mirascope/pull/188)
* Docs updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/191](https://github.com/Mirascope/mirascope/pull/191)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.9.1...v0.10.0](https://github.com/Mirascope/mirascope/compare/v0.9.1...v0.10.0)

## [v0.9.1](https://github.com/Mirascope/mirascope/releases/tag/v0.9.1) - 2024-04-05

## What's Changed
* bugfix: added missing groq call to cli by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/175](https://github.com/Mirascope/mirascope/pull/175)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.9.0...v0.9.1](https://github.com/Mirascope/mirascope/compare/v0.9.0...v0.9.1)

## [v0.9.0](https://github.com/Mirascope/mirascope/releases/tag/v0.9.0) - 2024-04-05

## What's Changed
* Feat: Groq Support by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/174](https://github.com/Mirascope/mirascope/pull/174)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.8.4...v0.9.0](https://github.com/Mirascope/mirascope/compare/v0.8.4...v0.9.0)

## [v0.8.4](https://github.com/Mirascope/mirascope/releases/tag/v0.8.4) - 2024-04-05

## What's Changed
* chore: update Anthropic tools to use new beta tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/173](https://github.com/Mirascope/mirascope/pull/173)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.8.3...v0.8.4](https://github.com/Mirascope/mirascope/compare/v0.8.3...v0.8.4)

## [v0.8.3](https://github.com/Mirascope/mirascope/releases/tag/v0.8.3) - 2024-04-04

## What's Changed
* Fix errors and openai dict by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/172](https://github.com/Mirascope/mirascope/pull/172)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.8.2...v0.8.3](https://github.com/Mirascope/mirascope/compare/v0.8.2...v0.8.3)

## [v0.8.2](https://github.com/Mirascope/mirascope/releases/tag/v0.8.2) - 2024-04-02

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.8.1...v0.8.2](https://github.com/Mirascope/mirascope/compare/v0.8.1...v0.8.2)

## [v0.8.1](https://github.com/Mirascope/mirascope/releases/tag/v0.8.1) - 2024-03-30

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.8.0...v0.8.1](https://github.com/Mirascope/mirascope/compare/v0.8.0...v0.8.1)

## [v0.8.0](https://github.com/Mirascope/mirascope/releases/tag/v0.8.0) - 2024-03-30

## What's Changed
* Feat: Integrate Weave with Mirascope by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/171](https://github.com/Mirascope/mirascope/pull/171)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.7.4...v0.8.0](https://github.com/Mirascope/mirascope/compare/v0.7.4...v0.8.0)

## [v0.7.4](https://github.com/Mirascope/mirascope/releases/tag/v0.7.4) - 2024-03-27

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.7.1...v0.7.4](https://github.com/Mirascope/mirascope/compare/v0.7.1...v0.7.4)

## [v0.7.1](https://github.com/Mirascope/mirascope/releases/tag/v0.7.1) - 2024-03-26

## What's Changed
* docs: include missing API reference docs by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/160](https://github.com/Mirascope/mirascope/pull/160)
* Update anthropic dependency to latest (`^0.21.3`) by [@barapa](https://github.com/barapa) in [https://github.com/Mirascope/mirascope/pull/164](https://github.com/Mirascope/mirascope/pull/164)
* Merge pull request [#164](https://github.com/Mirascope/mirascope/issues/164) from barapa/main by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/165](https://github.com/Mirascope/mirascope/pull/165)
* Dev by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/166](https://github.com/Mirascope/mirascope/pull/166)

## New Contributors
* [@barapa](https://github.com/barapa) made their first contribution in [https://github.com/Mirascope/mirascope/pull/164](https://github.com/Mirascope/mirascope/pull/164)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.7.0...v0.7.1](https://github.com/Mirascope/mirascope/compare/v0.7.0...v0.7.1)

## [v0.7.0](https://github.com/Mirascope/mirascope/releases/tag/v0.7.0) - 2024-03-24

## What's Changed
* fix: typo in example name by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/154](https://github.com/Mirascope/mirascope/pull/154)
* feat: wandb support model agnostic mixin class by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/158](https://github.com/Mirascope/mirascope/pull/158)
* chore: added CLI example by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/156](https://github.com/Mirascope/mirascope/pull/156)
* Release v0.7 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/159](https://github.com/Mirascope/mirascope/pull/159)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.6.2...v0.7.0](https://github.com/Mirascope/mirascope/compare/v0.6.2...v0.7.0)

## [v0.6.2](https://github.com/Mirascope/mirascope/releases/tag/v0.6.2) - 2024-03-20

## What's Changed
* docs: updates to docs and examples by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/152](https://github.com/Mirascope/mirascope/pull/152)
* Docs / Examples Updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/153](https://github.com/Mirascope/mirascope/pull/153)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.6.1...v0.6.2](https://github.com/Mirascope/mirascope/compare/v0.6.1...v0.6.2)

## [v0.6.1](https://github.com/Mirascope/mirascope/releases/tag/v0.6.1) - 2024-03-19

## What's Changed
* v0.6.1 fixes by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/151](https://github.com/Mirascope/mirascope/pull/151)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.6.0...v0.6.1](https://github.com/Mirascope/mirascope/compare/v0.6.0...v0.6.1)

## [v0.6.0](https://github.com/Mirascope/mirascope/releases/tag/v0.6.0) - 2024-03-19

## What's Changed
* fix(docs): mismatch between example output and dump output by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/145](https://github.com/Mirascope/mirascope/pull/145)
* feat: mistral with extractors, still missing stream_async test by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/146](https://github.com/Mirascope/mirascope/pull/146)
* Anthropic Function Calling Support Fixes by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/148](https://github.com/Mirascope/mirascope/pull/148)
* Fix extract async by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/147](https://github.com/Mirascope/mirascope/pull/147)
* Release v0.6 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/149](https://github.com/Mirascope/mirascope/pull/149)
* chore: v0.6 release stuff by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/150](https://github.com/Mirascope/mirascope/pull/150)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.5.0...v0.6.0](https://github.com/Mirascope/mirascope/compare/v0.5.0...v0.6.0)

## [v0.5.0](https://github.com/Mirascope/mirascope/releases/tag/v0.5.0) - 2024-03-15

## What's Changed
* Anthropic tools by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/142](https://github.com/Mirascope/mirascope/pull/142)
* Release v0.5 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/143](https://github.com/Mirascope/mirascope/pull/143)
* chore: bump version number by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/144](https://github.com/Mirascope/mirascope/pull/144)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.4.0...v0.5.0](https://github.com/Mirascope/mirascope/compare/v0.4.0...v0.5.0)

## [v0.4.0](https://github.com/Mirascope/mirascope/releases/tag/v0.4.0) - 2024-03-15

## What's Changed
* Update README.md by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/132](https://github.com/Mirascope/mirascope/pull/132)
* feat: AnthropicPrompt and related convenience. NO TOOLS. by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/133](https://github.com/Mirascope/mirascope/pull/133)
* cherry pick from main by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/136](https://github.com/Mirascope/mirascope/pull/136)
* Feat: Async for Gemini and Anthropic by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/137](https://github.com/Mirascope/mirascope/pull/137)
* BREAKING: Interface changes for v0.4 to incorporate recent feedback by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/138](https://github.com/Mirascope/mirascope/pull/138)
* BREAKING: Release v0.4 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/139](https://github.com/Mirascope/mirascope/pull/139)
* fix(docs): link issues in schema and update wrongly indented code blocks by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/140](https://github.com/Mirascope/mirascope/pull/140)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.3.1...v0.4.0](https://github.com/Mirascope/mirascope/compare/v0.3.1...v0.4.0)

## [v0.3.1](https://github.com/Mirascope/mirascope/releases/tag/v0.3.1) - 2024-03-08

## What's Changed
* fix: issue with including some call params that shouldn't be included… by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/135](https://github.com/Mirascope/mirascope/pull/135)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.3.0...v0.3.1](https://github.com/Mirascope/mirascope/compare/v0.3.0...v0.3.1)

## [v0.3.0](https://github.com/Mirascope/mirascope/releases/tag/v0.3.0) - 2024-03-08

## What's Changed
* Coverage: initial push to get to 100% by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/64](https://github.com/Mirascope/mirascope/pull/64)
* feat: added remove command to mirascope cli by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/65](https://github.com/Mirascope/mirascope/pull/65)
* Cookbook Recipe: SQuAD Extraction by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/66](https://github.com/Mirascope/mirascope/pull/66)
* Update llm_convenience_wrappers.md by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/68](https://github.com/Mirascope/mirascope/pull/68)
* fix: missing $defs in tool schema by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/69](https://github.com/Mirascope/mirascope/pull/69)
* chore: add start/end time to async + tests + minor tweaks by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/72](https://github.com/Mirascope/mirascope/pull/72)
* feat: prompt completion dump to json by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/67](https://github.com/Mirascope/mirascope/pull/67)
* Update pydantic_prompts.md by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/70](https://github.com/Mirascope/mirascope/pull/70)
* feat: auto tag version when using mirascope cli add command by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/74](https://github.com/Mirascope/mirascope/pull/74)
* fix: lint issues with using enums without  wrapper by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/76](https://github.com/Mirascope/mirascope/pull/76)
* Bugfix/auto tag non prompts by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/79](https://github.com/Mirascope/mirascope/pull/79)
* refactor: move prompts for rag example back into rag prompt folder by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/80](https://github.com/Mirascope/mirascope/pull/80)
* fix: removed the jinja template that's not supposed to be there by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/81](https://github.com/Mirascope/mirascope/pull/81)
* fix: github issue 75, CLI error for variables outside prompt by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/77](https://github.com/Mirascope/mirascope/pull/77)
* Docstrings PR by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/73](https://github.com/Mirascope/mirascope/pull/73)
* Feature/test add command by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/78](https://github.com/Mirascope/mirascope/pull/78)
* added tests for status by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/83](https://github.com/Mirascope/mirascope/pull/83)
* added tests for use by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/85](https://github.com/Mirascope/mirascope/pull/85)
* fix: prompt messages to return openai types by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/82](https://github.com/Mirascope/mirascope/pull/82)
* Update README.md by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/86](https://github.com/Mirascope/mirascope/pull/86)
* added tests for init command by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/87](https://github.com/Mirascope/mirascope/pull/87)
* added coverage for tests using async generators by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/90](https://github.com/Mirascope/mirascope/pull/90)
* Back Merge v0.2.4 README updates into Dev by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/92](https://github.com/Mirascope/mirascope/pull/92)
* Update README.md to make it more clear that you can write the messages array yourself if you'd prefer by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/93](https://github.com/Mirascope/mirascope/pull/93)
* feat: cookbook/examples restructure by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/88](https://github.com/Mirascope/mirascope/pull/88)
* Update CONTRIBUTING.md by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/95](https://github.com/Mirascope/mirascope/pull/95)
* Merge pull request [#95](https://github.com/Mirascope/mirascope/issues/95) from Mirascope/willbakst-patch-1 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/96](https://github.com/Mirascope/mirascope/pull/96)
* added missing tests for command utils, added functional function pars… by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/94](https://github.com/Mirascope/mirascope/pull/94)
* Include `_call_params: CallParams` attribute in `Prompt` by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/98](https://github.com/Mirascope/mirascope/pull/98)
* feat: classify example using extract by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/97](https://github.com/Mirascope/mirascope/pull/97)
* added 3 examples for langchain using mirascope by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/99](https://github.com/Mirascope/mirascope/pull/99)
* fix: remove deprecation warning when using tools with prompt for extr… by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/101](https://github.com/Mirascope/mirascope/pull/101)
* fix: renamed folders in rag so as not to duplicate in cookbook by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/102](https://github.com/Mirascope/mirascope/pull/102)
* fix: include completion in returned BaseModel from call to extract by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/103](https://github.com/Mirascope/mirascope/pull/103)
* Enable setting `call_params` like you would for `model_config` without it appearing in the construction of the prompt. by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/104](https://github.com/Mirascope/mirascope/pull/104)
* Mirascope messages by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/105](https://github.com/Mirascope/mirascope/pull/105)
* fix: use ClassVar instead of PromptConfig so we don't need to ignore warnings by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/106](https://github.com/Mirascope/mirascope/pull/106)
* Cookbook wandb by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/100](https://github.com/Mirascope/mirascope/pull/100)
* feat: examples added to parser docstrings.  by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/108](https://github.com/Mirascope/mirascope/pull/108)
* chore: added basic example for validation by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/109](https://github.com/Mirascope/mirascope/pull/109)
* added langsmith cookbook examples and walkthrough by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/107](https://github.com/Mirascope/mirascope/pull/107)
* feat: WandB prompt (initial gutcheck) by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/110](https://github.com/Mirascope/mirascope/pull/110)
* feat: wandb walkthrough markdown by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/111](https://github.com/Mirascope/mirascope/pull/111)
* feat: basic support for Gemini by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/112](https://github.com/Mirascope/mirascope/pull/112)
* feat: OpenAIPrompt class similar to GeminiPrompt by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/113](https://github.com/Mirascope/mirascope/pull/113)
* Extract additional types by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/114](https://github.com/Mirascope/mirascope/pull/114)
* docs: update README with new edits. by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/117](https://github.com/Mirascope/mirascope/pull/117)
* chore: updated examples to use new creation from prompt by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/116](https://github.com/Mirascope/mirascope/pull/116)
* chore: remove print statement by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/119](https://github.com/Mirascope/mirascope/pull/119)
* Fix bug with manually setting call params by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/120](https://github.com/Mirascope/mirascope/pull/120)
* bugfix: fix autocompletion not working by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/123](https://github.com/Mirascope/mirascope/pull/123)
* fix: issue with missing start/end time and handling excepts for end t… by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/122](https://github.com/Mirascope/mirascope/pull/122)
* Wandb regen by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/121](https://github.com/Mirascope/mirascope/pull/121)
* Update cookbook by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/124](https://github.com/Mirascope/mirascope/pull/124)
* fix: replace called_once with assert_called_once by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/127](https://github.com/Mirascope/mirascope/pull/127)
* chore: update langsmith examples by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/125](https://github.com/Mirascope/mirascope/pull/125)
* chore: update squad cookbook to use v0.3 updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/126](https://github.com/Mirascope/mirascope/pull/126)
* bugfix: tags not working by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/129](https://github.com/Mirascope/mirascope/pull/129)
* docs: update concepts pages with new drafts for v0.3 release by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/130](https://github.com/Mirascope/mirascope/pull/130)
* Merge Dev -> Main for v0.3 release by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/131](https://github.com/Mirascope/mirascope/pull/131)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.2.4...v0.3.0](https://github.com/Mirascope/mirascope/compare/v0.2.4...v0.3.0)

## [v0.2.4](https://github.com/Mirascope/mirascope/releases/tag/v0.2.4) - 2024-02-23

## What's Changed
* Release/v0.2.4 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/91](https://github.com/Mirascope/mirascope/pull/91)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.2.3...v0.2.4](https://github.com/Mirascope/mirascope/compare/v0.2.3...v0.2.4)

## [v0.2.3](https://github.com/Mirascope/mirascope/releases/tag/v0.2.3) - 2024-02-11

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.2.2...v0.2.3](https://github.com/Mirascope/mirascope/compare/v0.2.2...v0.2.3)

## [v0.2.2](https://github.com/Mirascope/mirascope/releases/tag/v0.2.2) - 2024-02-06

## What's Changed
* rag cookbook example markdown by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/52](https://github.com/Mirascope/mirascope/pull/52)
* fix: dependabot issues with FastAPI and Starlette packages by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/62](https://github.com/Mirascope/mirascope/pull/62)
* fix: bump up FastAPI version in cookbook requirements-fastapi.txt by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/63](https://github.com/Mirascope/mirascope/pull/63)
* fix: incorrect inclusion of `tool_call` in `OpenAITool.tool_schema` by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/61](https://github.com/Mirascope/mirascope/pull/61)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.2.1...v0.2.2](https://github.com/Mirascope/mirascope/compare/v0.2.1...v0.2.2)

## [v0.2.1](https://github.com/Mirascope/mirascope/releases/tag/v0.2.1) - 2024-02-03

## What's Changed
* docs: remove old docs and point to new basic examples by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/57](https://github.com/Mirascope/mirascope/pull/57)
* fix: issue with all extra + readme for zsh users by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/58](https://github.com/Mirascope/mirascope/pull/58)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.2.0...v0.2.1](https://github.com/Mirascope/mirascope/compare/v0.2.0...v0.2.1)

## [v0.2.0](https://github.com/Mirascope/mirascope/releases/tag/v0.2.0) - 2024-02-03

## What's Changed
* chore(deps): bump jinja2 from 3.1.2 to 3.1.3 by [@dependabot](https://github.com/dependabot) in [https://github.com/Mirascope/mirascope/pull/22](https://github.com/Mirascope/mirascope/pull/22)
* feat: add initial OpenAITool Pydantic model by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/23](https://github.com/Mirascope/mirascope/pull/23)
* Make using tools easy with OpenAITool and Function -> OpenAITool automatic conversion by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/24](https://github.com/Mirascope/mirascope/pull/24)
* Tools review changes by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/25](https://github.com/Mirascope/mirascope/pull/25)
* feat: basic rag cookbook example using local embeddings by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/26](https://github.com/Mirascope/mirascope/pull/26)
* feat: OpenAIChat Extraction + String Prompts by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/29](https://github.com/Mirascope/mirascope/pull/29)
* Rag pinecone by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/30](https://github.com/Mirascope/mirascope/pull/30)
* removed debug statement from pinecone_embeddings.py by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/31](https://github.com/Mirascope/mirascope/pull/31)
* feat: added async openai client by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/28](https://github.com/Mirascope/mirascope/pull/28)
* docs: add templates for issues by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/34](https://github.com/Mirascope/mirascope/pull/34)
* Initial prep work for streaming tools more conveniently by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/33](https://github.com/Mirascope/mirascope/pull/33)
* bugfix: fixed various bugs regarding mirascope cli by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/41](https://github.com/Mirascope/mirascope/pull/41)
* Feature/mirascope cli autocomplete by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/42](https://github.com/Mirascope/mirascope/pull/42)
* Feat: Enable using `base_url` with convenience wrappers for things like proxies by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/49](https://github.com/Mirascope/mirascope/pull/49)
* feat: add **kwargs to chat client wrappers for passthrough by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/50](https://github.com/Mirascope/mirascope/pull/50)
* Readme updates by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/44](https://github.com/Mirascope/mirascope/pull/44)
* Rag refactor by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/43](https://github.com/Mirascope/mirascope/pull/43)
* TOOL message type for Prompt by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/51](https://github.com/Mirascope/mirascope/pull/51)
* feat: added basic tools parsing by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/48](https://github.com/Mirascope/mirascope/pull/48)
* final rag changes by [@brianpark0126](https://github.com/brianpark0126) in [https://github.com/Mirascope/mirascope/pull/54](https://github.com/Mirascope/mirascope/pull/54)
* feat: Added AsyncOpenAIToolParser by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/53](https://github.com/Mirascope/mirascope/pull/53)
* Update pydantic_prompts.md by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/55](https://github.com/Mirascope/mirascope/pull/55)

## New Contributors
* [@dependabot](https://github.com/dependabot) made their first contribution in [https://github.com/Mirascope/mirascope/pull/22](https://github.com/Mirascope/mirascope/pull/22)
* [@brianpark0126](https://github.com/brianpark0126) made their first contribution in [https://github.com/Mirascope/mirascope/pull/26](https://github.com/Mirascope/mirascope/pull/26)

**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.1.3...v0.2.0](https://github.com/Mirascope/mirascope/compare/v0.1.3...v0.2.0)

## [v0.1.3](https://github.com/Mirascope/mirascope/releases/tag/v0.1.3) - 2024-01-11

## What's Changed
* fix: add py.typed to all submodules so that mypy analyzes them. by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/21](https://github.com/Mirascope/mirascope/pull/21)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.1.2...v0.1.3](https://github.com/Mirascope/mirascope/compare/v0.1.2...v0.1.3)

## [v0.1.2](https://github.com/Mirascope/mirascope/releases/tag/v0.1.2) - 2024-01-10

## What's Changed
* Update mkdocs tracking by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/19](https://github.com/Mirascope/mirascope/pull/19)
* chore: update GA tag in mkdocs.yml, add py.typed for mypy, and bump v… by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/20](https://github.com/Mirascope/mirascope/pull/20)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.1.1...v0.1.2](https://github.com/Mirascope/mirascope/compare/v0.1.1...v0.1.2)

## [v0.1.1](https://github.com/Mirascope/mirascope/releases/tag/v0.1.1) - 2024-01-03

## What's Changed
* fixed various typos from docs examples by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/16](https://github.com/Mirascope/mirascope/pull/16)
* Added type hint for messages when using [@messages](https://github.com/messages) decorator by [@brenkao](https://github.com/brenkao) in [https://github.com/Mirascope/mirascope/pull/17](https://github.com/Mirascope/mirascope/pull/17)
* chore: bump version number v0.1.0 -> v0.1.1 by [@willbakst](https://github.com/willbakst) in [https://github.com/Mirascope/mirascope/pull/18](https://github.com/Mirascope/mirascope/pull/18)


**Full Changelog**: [https://github.com/Mirascope/mirascope/compare/v0.1.0...v0.1.1](https://github.com/Mirascope/mirascope/compare/v0.1.0...v0.1.1)

## [v0.1.0](https://github.com/Mirascope/mirascope/releases/tag/v0.1.0) - 2023-12-31

Initial release!

