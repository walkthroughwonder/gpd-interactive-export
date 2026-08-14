# GPD Contribution: Interactive Visualization Export

An interactive Three.js research map for [Get Physics Done](https://github.com/psi-oss/get-physics-done).

## What This Adds

A new `--format interactive` option to `/gpd:export` that generates a self-contained HTML file with:

- **3D force-directed dependency graph** — phases as nodes (color-coded by status), edges showing provides/requires/affects flows
- **Interactive exploration** — orbit, zoom, hover for tooltips, click for full detail panels with MathJax equations
- **Progress dashboard** — sidebar with completion tracking, gap analysis, critical path display
- **Dark/light theme** — toggle with a button
- **Critical path highlighting** — isolate the bottleneck chain with one click
- **Colorblind-safe palette** — Wong 2011 (Nature Methods), consistent with GPD's figure-generation-templates.md

Zero dependencies beyond CDN-loaded Three.js and MathJax. Single HTML file, works offline after first load.

## File Map

```
contribution/
├── GITHUB_ISSUE.md                          # Issue text to post on psi-oss/get-physics-done
├── README.md                                # This file
├── demo/
│   └── index.html                           # Working demo with Conformal Bootstrap sample data
├── src/gpd/specs/templates/
│   └── interactive-export.html              # The HTML template (new file for the repo)
├── patches/
│   └── export-workflow-addition.md          # Detailed instructions for modifying export.md
└── tests/
    ├── test_interactive_export.py           # template/structure tests (2 skipped pending workflow update)
    └── test_camera_layout.py                # force-layout / camera framing invariants
```

## How to Submit

### 1. Fork and clone

```bash
gh repo fork psi-oss/get-physics-done --clone
cd get-physics-done
uv sync --dev
source .venv/bin/activate
```

### 2. Create the issue

Post the contents of `GITHUB_ISSUE.md` as a new issue:

```bash
gh issue create \
  --repo psi-oss/get-physics-done \
  --title "[Feature] Interactive visualization export (--format interactive)" \
  --body-file /path/to/contribution/GITHUB_ISSUE.md \
  --label enhancement
```

### 3. Create a feature branch and add the files

```bash
git checkout -b feat/interactive-viz-export

# Add the template
cp contribution/src/gpd/specs/templates/interactive-export.html \
   src/gpd/specs/templates/interactive-export.html

# Add the test
cp contribution/tests/test_interactive_export.py \
   tests/test_interactive_export.py

# Apply the workflow changes described in patches/export-workflow-addition.md
# (manual edits to src/gpd/commands/export.md and src/gpd/specs/workflows/export.md)
```

### 4. Run tests

```bash
uv run pytest tests/test_interactive_export.py -v
uv run pytest tests/ -v  # full suite
uv build
```

### 5. Submit PR

```bash
git add -A
git commit -m "feat: add interactive visualization export format"
git push origin feat/interactive-viz-export

gh pr create \
  --title "feat: add interactive visualization export (--format interactive)" \
  --body "Closes #XX

Adds a new \`--format interactive\` option to \`/gpd:export\` that generates a
self-contained HTML file with an interactive Three.js force-directed dependency
graph and research progress dashboard.

## Changes
- New template: \`src/gpd/specs/templates/interactive-export.html\`
- Updated workflow: \`src/gpd/specs/workflows/export.md\` (new \`generate_interactive\` step)
- Updated command: \`src/gpd/commands/export.md\` (interactive option in format table)
- New tests: \`tests/test_interactive_export.py\`, \`tests/test_camera_layout.py\`

## vNEXT
- Added \`--format interactive\` export: standalone HTML with Three.js 3D dependency graph, 
  progress dashboard, MathJax equations, dark/light theme, and critical path highlighting."
```

### 6. CLA

The CLA Assistant bot will prompt you on the PR. Sign at:
https://cla-assistant.io/psi-oss/get-physics-done
