# GitHub-Ready VLA Research Design

## Objective

Create a Windows-only, Apache-2.0 licensed repository that packages the
`vla-research` Codex skill, its local MCP server, CLI fallback, an empty
research-memory template, PowerShell lifecycle scripts, and tests.

The repository must be safe to publish. It must not contain the author's paper
PDFs, personal research records, private research thesis, machine-specific
paths, or copied Academic Research Suite (ARS) content.

## Repository Location

Develop the public package in an isolated repository that contains no private
research workspace files or installed-skill state.

## Architecture

Use a single repository with five bounded components:

1. `skill/vla-research/`: Codex domain adapter and fallback CLI.
2. `src/vla_research/`: Standard-library Python research memory and MCP server.
3. `research-memory-template/`: Empty, reusable research-memory structure.
4. `scripts/`: Windows PowerShell installation, initialization, validation, and
   uninstallation commands.
5. `tests/`: Unit, protocol, installation, and privacy-boundary tests.

The research memory remains the source of truth. The MCP server is a thin
JSON-RPC interface over that memory. The skill controls task routing and
research behavior. ARS remains an optional external companion skill.

## Proposed Structure

```text
vla-research/
|-- .gitignore
|-- LICENSE
|-- NOTICE
|-- README.md
|-- pyproject.toml
|-- skill/
|   `-- vla-research/
|       |-- SKILL.md
|       |-- agents/
|       |   `-- openai.yaml
|       |-- references/
|       |   |-- academic-research-integration.md
|       |   `-- memory-contract.md
|       `-- scripts/
|           `-- vla_memory_cli.py
|-- src/
|   `-- vla_research/
|       |-- __init__.py
|       |-- memory.py
|       `-- server.py
|-- research-memory-template/
|   |-- gaps/
|   |   `-- gap-table.json
|   |-- matrices/
|   |   `-- metrics-schema.md
|   |-- papers/
|   |   `-- index.json
|   |-- pdfs/
|   |   `-- README.md
|   |-- state/
|   |   |-- reading-queue.json
|   |   `-- research-state.md
|   `-- taxonomy/
|       |-- hardware-mapping.md
|       `-- vla-acceleration-taxonomy.md
|-- scripts/
|   |-- initialize-memory.ps1
|   |-- install.ps1
|   |-- uninstall.ps1
|   `-- validate.ps1
|-- tests/
|   |-- test_install_scripts.py
|   |-- test_mcp_server.py
|   |-- test_privacy_boundary.py
|   `-- test_research_memory.py
`-- docs/
    `-- superpowers/
        |-- plans/
        `-- specs/
```

## Skill Behavior

The public skill preserves the verified local behavior:

- Handle single-paper search, reading, metric extraction, and memory updates
  directly.
- Automatically use `academic-research-suite` for research-question scoping,
  systematic literature work, multi-paper synthesis, citation verification,
  academic writing, review, and experiment planning.
- Continue with a transparent reduced workflow if ARS is unavailable.
- Keep publication existence, source acquisition, claim verification, and
  metric verification as separate evidence dimensions.

The public skill must use environment-driven or repository-relative paths. It
must not mention author-specific profile or workspace paths.

## Runtime Configuration

Use these environment variables:

- `VLA_RESEARCH_MEMORY`: absolute path to the user's research memory.
- `VLA_RESEARCH_REPO`: optional absolute path to the installed repository
  checkout when needed by helper scripts.
- `CODEX_HOME`: optional Codex home override; default to
  `%USERPROFILE%\.codex`.

Resolution rules:

1. Prefer an explicitly supplied script parameter.
2. Then use the corresponding environment variable.
3. Then use a documented Windows default.

The default research memory is:

`%USERPROFILE%\Documents\vla-research-memory`

The default skill installation directory is:

`%CODEX_HOME%\skills\vla-research`

## Python Package

Use Python 3.10 or newer and the standard library for runtime code. Package the
MCP server as `vla_research.server` and expose a console entry point:

```text
vla-research-mcp = vla_research.server:main
```

The MCP server must expose:

- `search_papers`
- `get_paper`
- `add_or_update_paper`
- `list_gaps`
- `recommend_next_reading`

The CLI fallback imports the installed Python package instead of modifying
`sys.path` to point at a private workspace.

## Installation

`scripts/install.ps1` accepts:

```powershell
.\scripts\install.ps1 `
  [-MemoryPath <absolute-path>] `
  [-CodexHome <absolute-path>] `
  [-PythonCommand <command-or-path>] `
  [-ForceSkillUpdate]
```

Installation behavior:

1. Verify Windows PowerShell or PowerShell 7 and Python 3.10+.
2. Install the local Python package for the current user.
3. Copy `skill/vla-research` into the selected Codex skills directory.
4. Initialize the memory from `research-memory-template` without overwriting
   existing files.
5. Print a complete TOML block that invokes the resolved Python executable
   with `-m vla_research.server`, avoiding reliance on the user Scripts PATH.
6. Run a CLI and MCP smoke test.
7. Tell the user to restart or open a new Codex session.

The installer must not edit `%CODEX_HOME%\config.toml` automatically. Printing
the exact block avoids corrupting unrelated user configuration.

Repeated installation must be idempotent:

- Existing research data is never overwritten.
- The skill is updated only when absent or `-ForceSkillUpdate` is supplied.
- Python package installation may be repeated safely.

## Memory Initialization

`scripts/initialize-memory.ps1` accepts a destination path and copies only
missing template files. Empty JSON files must contain valid top-level arrays.
Markdown templates should contain field guidance without personal research
claims.

The template may contain clearly fictional records only inside tests. The
distributed runtime template remains empty.

## Uninstallation

`scripts/uninstall.ps1` removes the installed skill and Python package only
after displaying the resolved targets. It does not remove the research memory
unless the user supplies a separate explicit `-RemoveMemory` switch.

Before recursive deletion, resolve and verify every target:

- Skill target must be exactly a `vla-research` child under the resolved Codex
  skills directory.
- Memory target must match the explicit `-MemoryPath` supplied by the user.
- Never delete the repository checkout.

## Documentation

The root `README.md` is user-facing repository documentation and must include:

- Purpose and feature summary.
- Windows prerequisites.
- Installation and MCP registration.
- Example prompts for direct VLA work and ARS-assisted work.
- Memory schema overview.
- Upgrade and uninstall commands.
- Privacy and copyright guidance.
- ARS optional-dependency notice.
- Testing and contribution instructions.

The skill directory itself does not contain a second README.

## Licensing

License original repository content under Apache License 2.0.

Include:

- `LICENSE`: complete Apache-2.0 text.
- `NOTICE`: project copyright and a statement that ARS is an optional,
  separately licensed dependency whose content is not bundled.

Do not copy ARS prompts, templates, agents, or workflow files.

Research papers and PDFs remain third-party copyrighted materials and must not
be committed. The README and `.gitignore` must state this clearly.

## Privacy Boundary

The public repository must reject or exclude:

- Author-specific Windows profile paths
- Author-specific private workspace paths
- Personal paper IDs and records from the current private corpus
- Current gap IDs and research-state conclusions
- PDF, rendered page, and extracted full-text files
- Python caches, test caches, local virtual environments, and generated cards
- Codex configuration containing user-specific paths

A privacy-boundary test scans tracked source and documentation files for these
patterns.

## Testing

Use `unittest` for Python runtime tests and PowerShell subprocess tests.

Required checks:

1. Research memory creates and reads an empty template.
2. Search, update, gap filtering, and reading recommendations work.
3. MCP initialization, tool listing, successful calls, and unknown-tool errors
   work.
4. CLI commands work against a temporary memory.
5. Memory initialization preserves existing files.
6. Installer resolves custom Codex and memory paths in a temporary directory.
7. Uninstaller refuses unsafe targets.
8. Repository privacy scan finds no private paths, personal records, or PDFs.
9. Skill `quick_validate.py` passes.
10. `scripts/validate.ps1` runs the full test and smoke-test suite.

Tests must not modify the real Codex home, user Documents directory, global
Python environment, or current private VLA workspace.

## Error Handling

- Missing Python or unsupported Python version: stop with an actionable message.
- Invalid JSON in memory: report the exact file and preserve it unchanged.
- Missing ARS: continue with the skill's documented reduced workflow.
- Existing memory: preserve every existing file and report skipped template
  files.
- Existing skill without `-ForceSkillUpdate`: leave it unchanged and explain
  how to update.
- Failed smoke test: stop installation and report the command that failed;
  never delete user memory as rollback.

## Acceptance Criteria

The package is ready for GitHub when:

- The isolated repository contains the complete structure in this design.
- Apache-2.0 licensing files are present.
- All runtime and script tests pass on Windows.
- The official skill validator passes.
- Installation works in temporary custom paths without touching real user data.
- The MCP server exposes all five tools.
- The empty template initializes successfully.
- No private paths, private research records, paper PDFs, or ARS source content
  are present.
- A clean clone can be installed by following only the root README.
