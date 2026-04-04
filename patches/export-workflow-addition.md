# Export Workflow Addition: `generate_interactive` step

This step should be inserted into `src/gpd/specs/workflows/export.md` between the existing
`generate_zip` step and the `report` step.

## Changes to `determine_format` step

Add `interactive` to the format table and checkpoint menu:

```
| Argument                                  | Format           |
| ----------------------------------------- | ---------------- |
| `--format html` or `html`                 | HTML only        |
| `--format latex` or `latex`               | LaTeX only       |
| `--format zip` or `zip`                   | ZIP only         |
| `--format interactive` or `interactive`   | Interactive only  |
| `--format all` or `all`                   | All formats      |
| (none)                                    | Ask user         |
```

Checkpoint menu becomes:

```
1. **html**         -- Standalone HTML with MathJax equations and structured results
2. **latex**        -- LaTeX document scaffold ready for journal submission
3. **zip**          -- Reproducibility package (scripts, data, derivations, README)
4. **interactive**  -- Interactive 3D research map with dependency graph (Three.js)
5. **all**          -- Generate all formats
```

## New step: `generate_interactive`

```xml
<step name="generate_interactive">
**If format is `interactive` or `all`:**

Build the JSON data blob from collected results and write `exports/interactive.html`.

### Build Project Data JSON

Construct a JSON object with this schema:

```json
{
  "project_title": "{project_title}",
  "milestone": "{milestone_name}",
  "generated_date": "{YYYY-MM-DD}",
  "phases": [
    {
      "number": 1,
      "name": "{phase name}",
      "status": "complete|partial|planned|empty",
      "one_liner": "{from SUMMARY.md}",
      "plans_complete": 3,
      "plans_total": 3,
      "progress": 100,
      "provides": ["result-a", "result-b"],
      "requires": ["input-x"],
      "affects": ["convention-y"],
      "key_results": ["Result description 1", "Result description 2"],
      "equations": ["\\\\[H = \\\\frac{p^2}{2m} + V(x)\\\\]"],
      "verification": [
        {"name": "Dimensional analysis", "passed": true, "warning": false},
        {"name": "Gauge invariance", "passed": false, "warning": true}
      ]
    }
  ],
  "edges": [
    {
      "from": 1,
      "to": 2,
      "type": "provides",
      "label": "result-a"
    },
    {
      "from": 1,
      "to": 3,
      "type": "affects",
      "label": "metric-signature"
    }
  ],
  "gaps": [
    {
      "severity": "high",
      "description": "Phase 3 requires \"coupling-constants\" but nothing provides it"
    }
  ],
  "critical_path": [1, 2, 4, 5]
}
```

**Phase status mapping:**
- `complete` -- all plans have matching SUMMARY artifacts
- `partial` -- some plans complete
- `planned` -- plans exist but none executed
- `empty` -- no plans created yet

**Edge construction:**
- For each phase pair where Phase A provides X and Phase B requires X: add edge `{from: A, to: B, type: "provides", label: X}`
- For each ROADMAP dependency: add edge `{from: dep, to: phase, type: "provides", label: "dependency"}`
- For each phase pair where Phase A affects convention Y used by Phase B: add edge `{from: A, to: B, type: "affects", label: Y}`
- Deduplicate: if ROADMAP dependency and provides/requires create same edge, keep one

**Gap detection:** (same logic as graph workflow)
- Unmet requires: phase requires X but nothing provides X → severity: high
- Orphaned provides: phase provides X but nothing uses X → severity: low
- Missing phase: depends on non-existent phase → severity: high
- Circular dependency → severity: critical

**Critical path:** Topological sort + longest path from any root to any leaf.

### Write the HTML

1. Read the template from `{GPD_INSTALL_DIR}/templates/interactive-export.html`
2. JSON-serialize the project data
3. Replace `{GPD_PROJECT_DATA}` placeholder with the serialized JSON
4. Replace `{project_title}` in the HTML `<title>` tag with the actual project title
5. Write to `exports/interactive.html`

</step>
```

## Changes to `report` step

Add the interactive format to the report table:

```
| exports/interactive.html | {size} | Interactive 3D map |
```

Add to the Notes section:

```
- **Interactive:** Open in any modern browser. Requires internet for Three.js and MathJax CDN.
  Click and drag to orbit. Scroll to zoom. Click phases for details.
```

## Changes to `commit_exports` step

Add `exports/interactive.html` to the commit file list:

```bash
for path in exports/results.html exports/results.tex exports/results.bib exports/interactive.html; do
```
