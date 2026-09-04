# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a Python scientific data processing tool for analyzing river bed
dynamics. It processes Seatek sensor data alongside hydrograph measurements and
generates visualizations. No external services, databases, or Docker containers
are required.

### Running commands

Standard commands are documented in `CLAUDE.md`. Key references:

- **Tests**: `python3 -m pytest tests/`
- **Lint**: `flake8 src/ tests/`
- **Type check**: `mypy src/`
- **Run processor**: `python3 seatek_processor.py`
- **Run validator**: `python3 validate_data.py`

### Non-obvious caveats

- Use `python3` (not `python`) as the command — `python` is not available on the
  PATH in this environment.
- Set `MPLBACKEND=Agg` when running the processor or validator to avoid
  matplotlib display errors in the headless environment.
- `python3 -m pytest tests/` now runs the full maintained suite including
  `tests/visualization/`. Legacy trees (`tests/data_processing`, `tests/utils`,
  `tests/enhanced_test_suite.py`) and the broken notebook have been removed.
- The Excel data files (`data/raw/*.xlsx`, `data/processed/*.xlsx`) are
  gitignored. The applications will report errors about missing data files —
  this is expected behavior. Unit tests mock all data dependencies and pass
  without real data files.
- To run the processor end-to-end without polluting the repo, set
  `HYDROGRAPH_BASE_DIR` to a scratch directory and place input data there. The
  processor reads `<base>/data/raw/Data_Summary.xlsx` (columns `River_Mile`,
  `Y_Offset`, `Num_Sensors`), `<base>/data/raw/Hydrograph_Seatek_Data.xlsx`
  (sheets named `RM_*` with `Time (Seconds)`, `Year`, `Sensor_*`,
  `Hydrograph (Lagged)`), and `<base>/data/processed/RM_*.xlsx` (same
  per-river-mile columns), then writes PNG charts to `<base>/output/charts/`.
  Example:
  `MPLBACKEND=Agg HYDROGRAPH_BASE_DIR=/tmp/hydro_demo python3 seatek_processor.py`.
- `$HOME/.local/bin` must be on `PATH` for `flake8`, `mypy`, `black`, `pytest`
  CLI commands to work. Consider adding `black .` to the "Running commands"
  section if it's part of the standard workflow.
- PR and `main` CI runs `pytest` + `flake8` + `mypy` (blocking). See
  `.github/workflows/python-tests.yml`.

### CodeScene review/salvage trigger

During automated PR review or salvage sessions, if CodeScene is red on a PR,
post:

```bash
/cs-agent skill:fix-code-health-degradations
```

Then wait for that run to complete before final defer/salvage disposition.

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
