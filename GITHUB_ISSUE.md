### Description

GPD's current export pipeline (`/gpd:export`) produces static HTML with MathJax and LaTeX scaffolds — great for documents, but there's no way to visually explore the structure of a research project interactively. The `/gpd:graph` command outputs Mermaid/ASCII diagrams that are useful in the terminal but can't be navigated, zoomed, or shared as standalone artifacts.

This proposal adds a new `--format interactive` option to `/gpd:export` that generates a self-contained HTML file with an interactive Three.js force-directed dependency graph and a research progress dashboard. Zero server required — it's a single HTML file you can open in any browser or share with collaborators.

### Use Case

- **Navigating complex projects:** A 10+ phase research project is hard to reason about from ROADMAP.md alone. An interactive graph lets you click phases, see what flows between them, and identify bottlenecks at a glance.
- **Sharing with collaborators:** Drop a single HTML file in an email or Slack — no LaTeX compilation, no Mermaid renderer needed.
- **Progress tracking:** Visual progress dashboard with phase completion, verification status, and critical path highlighting.
- **Presentations:** Open the export in a browser during a group meeting to walk through the research structure.

### Proposed Solution

**New export format: `interactive`**

```bash
/gpd:export --format interactive
```

Generates `exports/interactive.html` — a standalone file (~30KB) embedding:

1. **3D Force-Directed Dependency Graph (Three.js)**
   - Nodes = phases, color-coded by status (complete/partial/planned/empty, matching GPD's existing palette from `ui-brand.md`)
   - Edges = provides/requires flows (solid) and convention affects (dashed)
   - Hover on nodes → shows phase name, one-liner, key results, verification status
   - Click nodes → expands a detail panel with equations (MathJax-rendered), key files, provides/requires lists
   - Edge labels show what flows between phases
   - Critical path highlighted with a distinct edge color
   - Camera orbit + zoom + pan

2. **Progress Dashboard Sidebar**
   - Overall project progress bar
   - Per-phase completion table with status symbols (matching GPD's ✓/◆/○ conventions)
   - Verification summary (passed/warning/failed counts)
   - Gap analysis alerts (unmet requires, orphaned provides)

3. **Dark/Light Theme Toggle** — defaults to dark (aligns with terminal-native GPD users)

**Technical approach:**
- Three.js loaded from CDN (with integrity hash), everything else inline
- Graph layout via a simple force-directed simulation (no D3 dependency — pure Three.js)
- MathJax loaded from CDN for equation rendering in the detail panel
- Responsive — works on mobile for on-the-go review
- All project data embedded as a JSON blob in a `<script>` tag — no external data files

**Files changed:**
- `src/gpd/commands/export.md` — add `interactive` to the format table and checkpoint menu
- `src/gpd/specs/workflows/export.md` — add `generate_interactive` step
- `src/gpd/specs/templates/interactive-export.html` — the HTML template (new file)
- Tests for the new format

### Alternatives Considered

- **D3.js 2D graph:** Simpler, but less visually distinctive and less aligned with physics visualization conventions. Three.js is already in the ecosystem for scientific visualization.
- **Mermaid with pan/zoom wrapper:** Limited interactivity — can't attach data to nodes or customize rendering.
- **Separate MCP server:** Heavier infrastructure; a standalone HTML file is more portable and requires no running server.

### Additional Context

This contribution follows the existing export workflow architecture exactly — same data collection (SUMMARY.md frontmatter, ROADMAP.md phases, VERIFICATION.md results), same commit policy (text exports committed, no binaries), same success criteria pattern. The interactive format is additive and doesn't change any existing behavior.

The colorblind-safe palette from `figure-generation-templates.md` (Wong 2011, Nature Methods) is reused for phase status colors to maintain visual consistency across GPD's output.
