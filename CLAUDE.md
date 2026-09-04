# Claude Coding Guidelines

## Build & Testing Commands

- Run all tests: `python3 -m pytest tests/`
- Run specific test file: `python3 -m pytest tests/test_config.py`
- Run specific test:
  `python3 -m pytest tests/test_config.py::test_config_default_initialization`
- Run data validator: `python3 validate_data.py`
- Run main processor: `MPLBACKEND=Agg python3 seatek_processor.py`
- Code linting: `flake8 src/ tests/`
- Type checking: `mypy src/`
- CI mirrors these commands on pull requests and pushes to `main` (see
  `.github/workflows/python-tests.yml`)

Use `python3` (not `python`) — `python` is often missing from PATH in Cloud/CI
environments.

## Code Style Guidelines

- **Formatting**: Follow PEP 8; line length of 88 characters (Black-compatible)
- **Imports**: Group as standard library, third-party, local imports; sort
  alphabetically
- **Types**: Use type hints for all function parameters and return values
- **Naming**: Classes use PascalCase; functions/variables use snake_case;
  constants use UPPER_SNAKE_CASE
- **Documentation**: Google-style docstrings with Args/Returns sections
- **Error Handling**: Use specific exception types; log errors with context;
  provide meaningful error messages
- **Architecture**: Follow dependency injection pattern; single responsibility
  principle
- **Testing**: Write unit tests for all components; mock external dependencies

<!-- gitnexus:start -->

# GitNexus — Code Intelligence

This project is indexed by GitNexus as
**Hydrograph_Versus_Seatek_Sensors_Project** (641 symbols, 1024 relationships,
25 execution flows).

> Index stale? Run `node .gitnexus/run.cjs analyze --index-only` from the
> project root — it auto-selects an available runner. No `.gitnexus/run.cjs`
> yet? Bootstrap with `npx`, `bunx`, or `pnpm dlx` — e.g.
> `bunx gitnexus@latest analyze` (npm 11 npx crash; #1939).

## Always Do

- **MUST run impact analysis before editing.** Use
  `impact({target: "symbolName", direction: "upstream"})` (MCP) or
  `node .gitnexus/run.cjs impact "symbolName" --direction upstream --repo .`
  (CLI fallback); report callers, processes, and risk. Never substitute grep for
  graph analysis.
- **MUST analyze graph changes before committing.** Use
  `detect_changes({scope: "all"})` (MCP) or
  `node .gitnexus/run.cjs detect-changes --scope all --repo .` (CLI fallback).
  `partial: true` or `truncated: true` is not a clean check — a zero means
  unseen, not unaffected; re-run it. For regression review:
  `detect_changes({scope: "compare", base_ref: "main"})` or
  `node .gitnexus/run.cjs detect-changes --scope compare --base-ref "main" --repo .`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before
  proceeding with edits.
- **MUST treat `risk: UNKNOWN` as unresolved, not as low.** An empty caller set
  is not evidence the symbol is unused — it can also mean the callers are not
  resolvable by the index (plain-object property access, dynamic dispatch,
  cross-language calls). `impact` pairs `UNKNOWN` with a `riskNote` saying so.
  Confirm with a text search before treating the symbol as safe to change or
  delete; do not proceed on the strength of a zero.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find
  execution flows instead of grepping. It returns process-grouped results ranked
  by relevance.
- When you need full context on a specific symbol — callers, callees, which
  execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings
  (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method before MCP/CLI impact analysis.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis, and never
  read `UNKNOWN` as an all-clear — it means the walk could not answer, which is
  the one verdict that requires confirming by other means.
- NEVER rename symbols with find-and-replace — use `rename` which understands
  the call graph.
- NEVER commit before MCP/CLI graph change analysis.

## Resources

| Resource                                                                  | Use for                                  |
| ------------------------------------------------------------------------- | ---------------------------------------- |
| `gitnexus://repo/Hydrograph_Versus_Seatek_Sensors_Project/context`        | Codebase overview, check index freshness |
| `gitnexus://repo/Hydrograph_Versus_Seatek_Sensors_Project/clusters`       | All functional areas                     |
| `gitnexus://repo/Hydrograph_Versus_Seatek_Sensors_Project/processes`      | All execution flows                      |
| `gitnexus://repo/Hydrograph_Versus_Seatek_Sensors_Project/process/{name}` | Step-by-step execution trace             |

## CLI

| Task                                                    | Read this skill file                                               |
| ------------------------------------------------------- | ------------------------------------------------------------------ |
| Understand architecture / "How does X work?"            | `.claude/skills/gitnexus-exploring/SKILL.md`                       |
| Blast radius / "What breaks if I change X?"             | `.claude/skills/gitnexus-impact-analysis/SKILL.md`                 |
| Trace bugs / "Why is X failing?"                        | `.claude/skills/gitnexus-debugging/SKILL.md`                       |
| Rename / extract / split / refactor                     | `.claude/skills/gitnexus-refactoring/SKILL.md`                     |
| Tools, resources, schema reference                      | `.claude/skills/gitnexus-guide/SKILL.md`                           |
| Index, status, clean, wiki CLI commands                 | `.claude/skills/gitnexus-cli/SKILL.md`                             |
| Work in the Tests area (78 symbols)                     | `.claude/skills/gitnexus-area-tests/SKILL.md`                      |
| Work in the Data area (26 symbols)                      | `.claude/skills/gitnexus-area-data/SKILL.md`                       |
| Work in the Visualization area (12 symbols)             | `.claude/skills/gitnexus-area-visualization/SKILL.md`              |
| Work in the Hydrograph_seatek_analysis area (8 symbols) | `.claude/skills/gitnexus-area-hydrograph-seatek-analysis/SKILL.md` |
| Work in the Cluster_14 area (6 symbols)                 | `.claude/skills/gitnexus-area-cluster-14/SKILL.md`                 |

<!-- gitnexus:end -->

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues via the `gh` CLI (Linear syncs downstream
from GitHub). See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical triage roles, label strings equal to role names; the pre-existing
`wontfix` label is reused as-is. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root, created
lazily by `/domain-modeling`. See `docs/agents/domain.md`.
