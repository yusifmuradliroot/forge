# Changelog

## [Unreleased]

## [0.3.0]
- REMOVED `ai_confuse`: decoys/fake notes are bloat — minimalism is now a hard principle
- Pipeline is now `strip_comments → mangle → string_crypt`, output stays minimal

## [0.2.0]
- `mangle`: conservative scope-aware local rename (68KB orbit.js: syntax OK)
- `string_crypt`: XOR-hex strings + runtime stub, node-verified identical output
- `ai_confuse`: fake banner + decoy functions, append-only
- Docs: DESIGN, TUTORIAL, CLI, FAQ, pass catalog

## [0.1.0]
- Pipeline CLI (`tools/forge.py`) with pass registry
- First pass: `strip_comments` (string-aware, fixture-verified)
- Repo infra: AGENTS.md + AI/, README, VERSION, tests
