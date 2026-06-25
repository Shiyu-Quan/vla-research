# GitHub-Ready VLA Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows-only, Apache-2.0 licensed, GitHub-ready VLA research suite containing a Codex skill, Python MCP server, CLI, empty research-memory template, PowerShell lifecycle scripts, documentation, and tests.

**Architecture:** Keep the research memory as transparent JSON and Markdown. Package a standard-library Python module as the memory/MCP layer, keep the Codex skill as a portable domain adapter, and use PowerShell scripts to install or remove the suite without overwriting user research data.

**Tech Stack:** Python 3.10+ standard library, `unittest`, MCP stdio JSON-RPC, PowerShell 5.1+, Markdown, JSON, TOML metadata.

---

## File Map

- `src/vla_research/memory.py`: Research-memory storage, query, update, and rendering behavior.
- `src/vla_research/server.py`: MCP protocol and five research tools.
- `src/vla_research/cli.py`: Portable CLI used by the skill fallback.
- `skill/vla-research/`: Codex skill, interface metadata, and research contracts.
- `research-memory-template/`: Empty user-owned memory seed.
- `scripts/*.ps1`: Windows initialization, installation, validation, and uninstallation.
- `tests/`: Runtime, protocol, CLI, lifecycle-script, and privacy tests.

### Task 1: Package Metadata And Research Memory Core

**Files:**
- Create: `pyproject.toml`
- Create: `src/vla_research/__init__.py`
- Create: `src/vla_research/memory.py`
- Create: `tests/test_research_memory.py`

- [ ] **Step 1: Write failing memory tests**

Create tests that instantiate `ResearchMemory` in a temporary directory and
assert:

```python
def test_ensure_creates_empty_memory(self):
    memory = ResearchMemory(self.root)
    memory.ensure()
    self.assertEqual(memory.load_index(), [])
    self.assertEqual(json.loads(memory.gaps_path.read_text(encoding="utf-8")), [])

def test_add_update_search_and_card_rendering(self):
    created = self.memory.add_or_update_paper({
        "id": "T01",
        "title": "Fictional VLA Accelerator",
        "domain": "manipulation",
        "main_technique": "fictional action engine",
        "hardware_relevance": "Test-only record",
        "metrics": {"control_hz": "not_reported"},
        "tags": ["action-generation"],
    })
    self.assertEqual(created["verification_status"], "unverified")
    self.assertEqual(self.memory.search_papers("action engine")[0]["id"], "T01")
    self.assertTrue(Path(created["card_path"]).exists())

def test_invalid_json_names_the_file_without_rewriting_it(self):
    self.memory.ensure()
    self.memory.index_path.write_text("{broken", encoding="utf-8")
    with self.assertRaisesRegex(ValueError, "index.json"):
        self.memory.load_index()
    self.assertEqual(self.memory.index_path.read_text(encoding="utf-8"), "{broken")
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m unittest tests.test_research_memory -v
```

Expected: import failure because `vla_research.memory` does not exist.

- [ ] **Step 3: Implement package metadata and memory core**

Create `pyproject.toml` with:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "vla-research"
version = "0.1.0"
description = "Local VLA hardware/software co-design research memory and MCP server"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "Apache-2.0" }
dependencies = []

[project.scripts]
vla-research = "vla_research.cli:main"
vla-research-mcp = "vla_research.server:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

Implement `ResearchMemory`, `slugify`, explicit UTF-8 JSON loading, file-aware
`ValueError` messages, deterministic sorting, and Markdown card rendering.

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python -m unittest tests.test_research_memory -v
```

Expected: all memory tests pass.

- [ ] **Step 5: Commit**

```powershell
git add pyproject.toml src/vla_research tests/test_research_memory.py
git commit -m "feat: add portable research memory package"
```

### Task 2: MCP Server And CLI

**Files:**
- Create: `src/vla_research/server.py`
- Create: `src/vla_research/cli.py`
- Create: `tests/test_mcp_server.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing MCP and CLI tests**

Test all five tool names, initialization, successful structured content,
unknown-tool protocol errors, and CLI JSON output:

```python
def test_tools_list_exposes_five_tools(self):
    response = handle_message(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        self.memory,
    )
    self.assertEqual(
        {tool["name"] for tool in response["result"]["tools"]},
        {"search_papers", "get_paper", "add_or_update_paper",
         "list_gaps", "recommend_next_reading"},
    )

def test_cli_search_uses_environment_memory(self):
    env = dict(os.environ, VLA_RESEARCH_MEMORY=str(self.root),
               PYTHONPATH=str(SRC_ROOT))
    completed = subprocess.run(
        [sys.executable, "-m", "vla_research.cli", "search", "fictional"],
        env=env, text=True, capture_output=True, check=True,
    )
    self.assertEqual(json.loads(completed.stdout)["results"][0]["id"], "T01")
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python -m unittest tests.test_mcp_server tests.test_cli -v
```

Expected: import failures for missing `server` and `cli`.

- [ ] **Step 3: Implement MCP and CLI**

Implement newline-delimited MCP JSON-RPC with `initialize`, `tools/list`,
`tools/call`, `prompts/list`, and `resources/list`. Resolve memory in this
order:

```python
def default_memory_root() -> Path:
    if value := os.environ.get("VLA_RESEARCH_MEMORY"):
        return Path(value)
    return Path.home() / "Documents" / "vla-research-memory"
```

Implement CLI subcommands `search`, `get`, `gaps`, and `recommend`, returning
UTF-8 JSON.

- [ ] **Step 4: Run tests and verify GREEN**

```powershell
$env:PYTHONPATH = (Resolve-Path .\src)
python -m unittest tests.test_mcp_server tests.test_cli -v
```

Expected: all MCP and CLI tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/vla_research/server.py src/vla_research/cli.py tests
git commit -m "feat: add MCP server and CLI"
```

### Task 3: Empty Research Memory Template

**Files:**
- Create: `research-memory-template/papers/index.json`
- Create: `research-memory-template/gaps/gap-table.json`
- Create: `research-memory-template/state/reading-queue.json`
- Create: `research-memory-template/state/research-state.md`
- Create: `research-memory-template/matrices/metrics-schema.md`
- Create: `research-memory-template/taxonomy/hardware-mapping.md`
- Create: `research-memory-template/taxonomy/vla-acceleration-taxonomy.md`
- Create: `research-memory-template/pdfs/README.md`
- Create: `tests/test_memory_template.py`

- [ ] **Step 1: Write failing template tests**

```python
def test_runtime_json_templates_are_empty_arrays(self):
    for relative in [
        "papers/index.json",
        "gaps/gap-table.json",
        "state/reading-queue.json",
    ]:
        self.assertEqual(json.loads((TEMPLATE / relative).read_text("utf-8")), [])

def test_template_contains_no_pdfs(self):
    self.assertEqual(list(TEMPLATE.rglob("*.pdf")), [])
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.test_memory_template -v
```

Expected: failures because template files do not exist.

- [ ] **Step 3: Create empty template**

Use `[]` for the three JSON stores. Document the metric tuple and empty
taxonomy headings without making claims about specific papers or research gaps.
Explain in `pdfs/README.md` that users may store lawfully obtained PDFs locally
but should not commit them.

- [ ] **Step 4: Run tests and verify GREEN**

```powershell
python -m unittest tests.test_memory_template -v
```

Expected: all template tests pass.

- [ ] **Step 5: Commit**

```powershell
git add research-memory-template tests/test_memory_template.py
git commit -m "feat: add empty research memory template"
```

### Task 4: Portable Codex Skill

**Files:**
- Create: `skill/vla-research/SKILL.md`
- Create: `skill/vla-research/agents/openai.yaml`
- Create: `skill/vla-research/references/memory-contract.md`
- Create: `skill/vla-research/references/academic-research-integration.md`
- Create: `skill/vla-research/scripts/vla_memory_cli.py`
- Create: `tests/test_skill_package.py`

- [ ] **Step 1: Write failing skill package tests**

```python
def test_skill_contains_no_private_paths(self):
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in SKILL_ROOT.rglob("*") if path.is_file()
    )
    self.assertNotRegex(text, PRIVATE_ABSOLUTE_PATH_PATTERN)

def test_skill_routes_complex_research_to_optional_ars(self):
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    self.assertIn("academic-research-suite", text)
    self.assertIn("If Academic Research Suite Is Unavailable", text)

def test_cli_wrapper_imports_package_without_sys_path_mutation(self):
    text = (SKILL_ROOT / "scripts" / "vla_memory_cli.py").read_text("utf-8")
    self.assertNotIn("sys.path.insert", text)
    self.assertIn("vla_research.cli", text)
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.test_skill_package -v
```

Expected: failures because the public skill is absent.

- [ ] **Step 3: Create portable skill**

Adapt the tested local skill while replacing private paths with:

```text
Memory: VLA_RESEARCH_MEMORY or %USERPROFILE%\Documents\vla-research-memory
CLI: python -m vla_research.cli
MCP: vla-research-mcp
```

Keep ARS optional and do not include ARS source content. Make the wrapper:

```python
from vla_research.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run package and official validation**

```powershell
python -m unittest tests.test_skill_package -v
$env:PYTHONUTF8 = "1"
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" `
  ".\skill\vla-research"
```

Expected: tests pass and validator prints `Skill is valid!`.

- [ ] **Step 5: Commit**

```powershell
git add skill tests/test_skill_package.py
git commit -m "feat: package portable VLA research skill"
```

### Task 5: PowerShell Lifecycle Scripts

**Files:**
- Create: `scripts/initialize-memory.ps1`
- Create: `scripts/install.ps1`
- Create: `scripts/uninstall.ps1`
- Create: `tests/test_install_scripts.py`

- [ ] **Step 1: Write failing lifecycle tests**

Run scripts only against temporary directories. Assert that:

```python
def test_initialize_memory_preserves_existing_files(self):
    existing = self.memory / "state" / "research-state.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep me", encoding="utf-8")
    run_pwsh("scripts/initialize-memory.ps1",
             "-MemoryPath", str(self.memory),
             "-TemplatePath", str(TEMPLATE))
    self.assertEqual(existing.read_text(encoding="utf-8"), "keep me")
    self.assertTrue((self.memory / "papers" / "index.json").exists())

def test_install_dry_run_resolves_custom_paths(self):
    completed = run_pwsh(
        "scripts/install.ps1",
        "-MemoryPath", str(self.memory),
        "-CodexHome", str(self.codex_home),
        "-SkipPythonInstall",
        "-SkipSmokeTest",
    )
    self.assertTrue((self.codex_home / "skills" / "vla-research" / "SKILL.md").exists())
    self.assertIn(str(self.memory), completed.stdout)

def test_uninstall_refuses_non_skill_target(self):
    completed = run_pwsh(
        "scripts/uninstall.ps1",
        "-CodexHome", str(self.root),
        "-SkipPythonUninstall",
        check=False,
    )
    self.assertNotEqual(completed.returncode, 0)
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.test_install_scripts -v
```

Expected: failures because scripts do not exist.

- [ ] **Step 3: Implement initialization and installation**

`initialize-memory.ps1` recursively copies missing files and prints `CREATED`
or `SKIPPED`.

`install.ps1`:

- Resolves absolute paths.
- Validates Python 3.10+ unless `-SkipPythonInstall`.
- Installs with `python -m pip install --user <repo>`.
- Copies the skill only when absent or `-ForceSkillUpdate`.
- Calls initialization.
- Prints this TOML shape with escaped Windows paths:

```toml
[mcp_servers.vla_research]
command = "<resolved-python-executable>"
args = ["-m", "vla_research.server"]
startup_timeout_sec = 30

[mcp_servers.vla_research.env]
PYTHONUTF8 = "1"
VLA_RESEARCH_MEMORY = "<resolved-memory-path>"
```

- [ ] **Step 4: Implement guarded uninstallation**

Resolve the skill target as `<CodexHome>\skills\vla-research`. Refuse deletion
unless its parent is exactly the resolved skills directory and its leaf name is
`vla-research`. Remove memory only with both `-RemoveMemory` and an explicit
`-MemoryPath`.

- [ ] **Step 5: Run lifecycle tests and verify GREEN**

```powershell
python -m unittest tests.test_install_scripts -v
```

Expected: all lifecycle tests pass without touching real user directories.

- [ ] **Step 6: Commit**

```powershell
git add scripts tests/test_install_scripts.py
git commit -m "feat: add Windows lifecycle scripts"
```

### Task 6: License, Documentation, Ignore Rules, And Privacy Gate

**Files:**
- Create: `LICENSE`
- Create: `NOTICE`
- Create: `.gitignore`
- Create: `README.md`
- Create: `tests/test_privacy_boundary.py`

- [ ] **Step 1: Write failing privacy and documentation tests**

```python
FORBIDDEN_TEXT = [
    "<author-profile-path>",
    "<private-research-workspace>",
]

def test_repository_has_no_private_signatures_or_pdf_files(self):
    for path in tracked_candidate_files():
        if path.suffix.lower() == ".pdf":
            self.fail(f"PDF must not be published: {path}")
        if path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_TEXT:
                self.assertNotIn(pattern, text, str(path))

def test_readme_documents_install_upgrade_uninstall_and_ars(self):
    text = (ROOT / "README.md").read_text("utf-8")
    for heading in ["Installation", "MCP Configuration", "Upgrade",
                    "Uninstall", "Academic Research Suite", "Privacy"]:
        self.assertIn(heading, text)

def test_apache_license_present(self):
    self.assertIn("Apache License", (ROOT / "LICENSE").read_text("utf-8"))
    self.assertIn("Version 2.0", (ROOT / "LICENSE").read_text("utf-8"))
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
python -m unittest tests.test_privacy_boundary -v
```

Expected: missing README and license failures.

- [ ] **Step 3: Add release documentation and licensing**

Add the complete Apache License 2.0 text. Add a NOTICE that states ARS is an
optional separately licensed dependency and no ARS content is bundled.

Document installation, exact MCP TOML, example prompts, schema, ARS behavior,
privacy, copyright, validation, upgrades, uninstallation, and contribution.

Ignore:

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
*.pdf
research-memory/
*.local.*
```

- [ ] **Step 4: Run tests and verify GREEN**

```powershell
python -m unittest tests.test_privacy_boundary -v
```

Expected: all privacy and documentation checks pass.

- [ ] **Step 5: Commit**

```powershell
git add LICENSE NOTICE README.md .gitignore tests/test_privacy_boundary.py
git commit -m "docs: add public release documentation and license"
```

### Task 7: Validation Script And Clean-Clone Acceptance

**Files:**
- Create: `scripts/validate.ps1`
- Modify: `README.md`
- Test: all `tests/*.py`

- [ ] **Step 1: Write the validation script**

The script must:

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONPATH = (Join-Path $RepoRoot "src")
& $PythonCommand -m unittest discover -s (Join-Path $RepoRoot "tests") -v
& $PythonCommand $QuickValidate (Join-Path $RepoRoot "skill\vla-research")
& $PythonCommand -m vla_research.cli --help
```

Resolve `quick_validate.py` from an optional parameter first, then from
`%CODEX_HOME%\skills\.system\skill-creator\scripts\quick_validate.py`. If it is
not available, stop with a message showing how to supply `-QuickValidatePath`.

- [ ] **Step 2: Run full validation**

```powershell
.\scripts\validate.ps1 -PythonCommand python
```

Expected:

- All unit tests pass.
- Skill validator prints `Skill is valid!`.
- CLI help exits zero.

- [ ] **Step 3: Run temporary installation acceptance**

```powershell
$sandbox = Join-Path $env:TEMP "vla-research-acceptance"
Remove-Item -LiteralPath $sandbox -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $sandbox | Out-Null
.\scripts\install.ps1 `
  -MemoryPath (Join-Path $sandbox "memory") `
  -CodexHome (Join-Path $sandbox "codex") `
  -SkipPythonInstall `
  -SkipSmokeTest
```

Expected: skill and empty memory appear under the temporary sandbox; no real
Codex or Documents files change.

- [ ] **Step 4: Inspect tracked files**

```powershell
git status --short
git ls-files
python -m unittest tests.test_privacy_boundary -v
git ls-files "*.pdf"
```

Expected: no private path matches, no PDFs, and only intentional source files.

- [ ] **Step 5: Commit final validation**

```powershell
git add scripts/validate.ps1 README.md
git commit -m "test: add release validation workflow"
```

- [ ] **Step 6: Final verification**

```powershell
.\scripts\validate.ps1 -PythonCommand python
git status --short
```

Expected: full validation passes and the worktree is clean.
