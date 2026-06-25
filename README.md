# VLA Research

A Windows-only local research suite for Vision-Language-Action (VLA) model
acceleration and hardware/software co-design.

The repository combines:

- A Codex `vla-research` skill
- A local MCP server with five research-memory tools
- A CLI fallback
- An empty JSON/Markdown research-memory template
- PowerShell installation and uninstallation scripts
- Optional integration with `academic-research-suite`

The runtime uses only the Python standard library.

## Features

- Search and maintain a structured VLA paper matrix
- Extract latency, control Hz, energy, power, cost, memory, platform, batch
  size, and success-rate evidence
- Maintain reading queues, taxonomy notes, hardware mappings, and gap tables
- Perform intensive or skim paper reading
- Automatically route broader academic work to an optional research-method
  skill
- Keep evidence, architectural inference, and research hypotheses separate

## Requirements

- Windows 10 or Windows 11
- Windows PowerShell 5.1 or PowerShell 7+
- Python 3.10+
- Codex with local skills and MCP server support

## Installation

Clone the repository and run:

```powershell
Set-Location .\vla-research
.\scripts\install.ps1
```

Defaults:

- Skill: `%USERPROFILE%\.codex\skills\vla-research`
- Memory: `%USERPROFILE%\Documents\vla-research-memory`

Use custom paths when needed:

```powershell
.\scripts\install.ps1 `
  -MemoryPath "E:\Research\vla-memory" `
  -CodexHome "$env:USERPROFILE\.codex" `
  -PythonCommand "python"
```

The installer:

1. Installs the Python package for the current user.
2. Copies the Codex skill.
3. Initializes missing research-memory files.
4. Preserves all existing research data.
5. Prints the MCP configuration block.
6. Runs CLI smoke checks.

The installer does not modify `config.toml`.

## MCP Configuration

Add the block printed by the installer to:

`%CODEX_HOME%\config.toml`

Typical configuration:

```toml
[mcp_servers.vla_research]
command = "C:\\path\\to\\python.exe"
args = ["-m", "vla_research.server"]
startup_timeout_sec = 30

[mcp_servers.vla_research.env]
PYTHONUTF8 = "1"
VLA_RESEARCH_MEMORY = "C:\\path\\to\\vla-research-memory"
```

Restart Codex or open a new session after updating the configuration.

The MCP server exposes:

- `search_papers`
- `get_paper`
- `add_or_update_paper`
- `list_gaps`
- `recommend_next_reading`

## CLI

```powershell
python -m vla_research.cli search "action generation"
python -m vla_research.cli get T01
python -m vla_research.cli gaps --priority high
python -m vla_research.cli recommend --focus "FPGA action generation"
```

Set a custom memory location:

```powershell
$env:VLA_RESEARCH_MEMORY = "E:\Research\vla-memory"
```

## Example Prompts

Direct VLA workflows:

```text
Use $vla-research to search my local memory for action-generation accelerators.
```

```text
Use $vla-research to skim this VLA paper and extract all reported hardware metrics.
```

```text
Use $vla-research to update this paper record and explain whether it changes the gap table.
```

Research-method workflows:

```text
Use $vla-research to refine a thesis question on batch-1 closed-loop VLA acceleration.
```

```text
Use $vla-research to conduct a literature review of action-generation acceleration and synthesize conflicting evidence.
```

## Academic Research Suite

`academic-research-suite` is optional. When installed, the skill automatically
uses it for research-question scoping, systematic literature work, multi-paper
synthesis, citation verification, paper writing, review, and experiment
planning.

This repository does not bundle or modify ARS content. ARS has its own license
and installation process. Without ARS, `vla-research` continues with a reduced
workflow and states which advanced research stages were omitted.

## Research Memory

The memory is user-owned and transparent:

```text
papers/index.json
gaps/gap-table.json
state/reading-queue.json
state/research-state.md
taxonomy/
matrices/metrics-schema.md
pdfs/
```

The distributed template contains no papers, gaps, or private research
conclusions.

Initialize another memory manually:

```powershell
.\scripts\initialize-memory.ps1 -MemoryPath "E:\Research\another-vla-memory"
```

## Upgrade

Pull the new version and update the package and skill:

```powershell
git pull
.\scripts\install.ps1 -ForceSkillUpdate
```

Existing memory files are preserved.

## Uninstall

Remove the installed skill and Python package while preserving research data:

```powershell
.\scripts\uninstall.ps1
```

Remove a specific memory only with explicit confirmation through parameters:

```powershell
.\scripts\uninstall.ps1 `
  -RemoveMemory `
  -MemoryPath "E:\Research\vla-memory"
```

The script validates resolved deletion targets before recursive removal.

## Privacy

Do not commit:

- Research paper PDFs or rendered pages
- Extracted full-text paper content
- Personal paper matrices, reading notes, or research-state files
- Codex configuration containing local paths
- API keys or private artifacts

The repository ignores PDFs and a repository-local `research-memory/`
directory. A privacy test also scans the release tree for known private
signatures.

Only store and process paper files you are legally allowed to access. This
project does not grant redistribution rights for third-party research papers.

## Testing

Run the Python suite:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python -m unittest discover -s .\tests -v
```

Run the complete release validation after installation:

```powershell
.\scripts\validate.ps1
```

Tests use temporary Codex and memory directories. They do not modify the real
Codex home or Documents directory.

## Contributing

Keep runtime dependencies minimal, add tests before behavior changes, and never
commit copyrighted papers or private research data.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
