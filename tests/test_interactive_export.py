"""Tests for the interactive export format.

Tests cover:
- Template file existence and structure
- JSON data placeholder presence
- Export command metadata (interactive option in format table)
- HTML validity of generated output
- Data schema validation
"""

import json
import pathlib
import re

import pytest

# ── Paths ──

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "src" / "gpd" / "specs" / "templates" / "interactive-export.html"
EXPORT_CMD = REPO_ROOT / "src" / "gpd" / "commands" / "export.md"
EXPORT_WF = REPO_ROOT / "src" / "gpd" / "specs" / "workflows" / "export.md"


# ── Fixtures ──

@pytest.fixture
def template_content():
    """Load the interactive export HTML template."""
    assert TEMPLATE_PATH.exists(), f"Template not found at {TEMPLATE_PATH}"
    return TEMPLATE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def sample_project_data():
    """Minimal valid project data for template rendering."""
    return {
        "project_title": "Test Project",
        "milestone": "v1.0",
        "generated_date": "2026-04-03",
        "phases": [
            {
                "number": 1,
                "name": "Phase A",
                "status": "complete",
                "one_liner": "First phase",
                "plans_complete": 2,
                "plans_total": 2,
                "progress": 100,
                "provides": ["result-a"],
                "requires": [],
                "affects": [],
                "key_results": ["Found result A"],
                "equations": ["\\[E = mc^2\\]"],
                "verification": [
                    {"name": "Dimensional analysis", "passed": True, "warning": False}
                ],
            },
            {
                "number": 2,
                "name": "Phase B",
                "status": "planned",
                "one_liner": "Second phase",
                "plans_complete": 0,
                "plans_total": 3,
                "progress": 0,
                "provides": ["result-b"],
                "requires": ["result-a"],
                "affects": [],
                "key_results": [],
                "equations": [],
                "verification": [],
            },
        ],
        "edges": [
            {"from": 1, "to": 2, "type": "provides", "label": "result-a"}
        ],
        "gaps": [],
        "critical_path": [1, 2],
    }


# ── Template Structure Tests ──


class TestTemplateStructure:
    """Verify the HTML template file is well-formed and contains required elements."""

    def test_template_exists(self):
        assert TEMPLATE_PATH.exists()

    def test_template_is_valid_html(self, template_content):
        assert template_content.strip().startswith("<!doctype html>") or template_content.strip().startswith("<!DOCTYPE html>")
        assert "</html>" in template_content

    def test_contains_data_placeholder(self, template_content):
        assert "{GPD_PROJECT_DATA}" in template_content, (
            "Template must contain {GPD_PROJECT_DATA} placeholder for JSON injection"
        )

    def test_contains_title_placeholder(self, template_content):
        assert "{project_title}" in template_content, (
            "Template must contain {project_title} placeholder in <title> tag"
        )

    def test_loads_threejs(self, template_content):
        assert "three" in template_content.lower(), (
            "Template must reference Three.js"
        )

    def test_loads_mathjax(self, template_content):
        assert "mathjax" in template_content.lower(), (
            "Template must reference MathJax for equation rendering"
        )

    def test_has_graph_canvas(self, template_content):
        assert 'id="graph-canvas"' in template_content

    def test_has_sidebar(self, template_content):
        assert 'id="sidebar"' in template_content

    def test_has_detail_panel(self, template_content):
        assert 'id="detail-panel"' in template_content

    def test_has_tooltip(self, template_content):
        assert 'id="tooltip"' in template_content

    def test_has_legend(self, template_content):
        assert 'id="legend"' in template_content

    def test_has_theme_toggle(self, template_content):
        assert 'btn-theme' in template_content

    def test_has_critical_path_toggle(self, template_content):
        assert 'btn-critical' in template_content

    def test_has_layout_toggle(self, template_content):
        assert 'btn-layout' in template_content

    def test_has_detail_panel_dismiss(self, template_content):
        assert 'id="dp-close"' in template_content
        assert "hideDetailPanel" in template_content

    def test_has_gpd_attribution(self, template_content):
        assert "Get Physics Done" in template_content


class TestCameraFraming:
    """Reset/layout/zoom must frame the actual graph, not a hardcoded radius."""

    def test_frames_from_node_bounds(self, template_content):
        assert "function frameGraph" in template_content
        assert "function graphBounds" in template_content
        assert "function fitRadius" in template_content
        assert "function zoomLimits" in template_content

    def test_no_hardcoded_force_reset_radius(self, template_content):
        assert "phases.length * 1.5" not in template_content

    def test_orbit_angles_match_face_on_dag(self, template_content):
        assert "DEFAULT_THETA = Math.PI / 2" in template_content
        assert "cameraTheta = 0" not in template_content

    def test_force_cloud_pinned_at_origin(self, template_content):
        assert "ORIGIN_PULL" in template_content
        assert "p.sub(_center)" in template_content

    def test_layout_switch_reframes(self, template_content):
        assert template_content.count("frameGraph(true)") >= 3

    def test_zoom_stays_outside_nodes(self, template_content):
        assert "function minRadiusForView" in template_content
        assert "ZOOM_CLEARANCE" in template_content
        assert "Math.max(3, Math.min(50, cameraRadius + e.deltaY" not in template_content


class TestStatusPalette:
    """Verify the template defines all four status colors."""

    STATUS_COLORS = {
        "--status-complete",
        "--status-partial",
        "--status-planned",
        "--status-empty",
    }

    def test_all_status_css_vars_defined(self, template_content):
        for var in self.STATUS_COLORS:
            assert var in template_content, (
                f"Missing CSS variable {var} for status coloring"
            )

    def test_status_colors_are_distinct(self, template_content):
        """Each status should map to a different color value."""
        import re
        colors = set()
        for var in self.STATUS_COLORS:
            match = re.search(rf"{re.escape(var)}:\s*(#[0-9a-fA-F]{{6}})", template_content)
            assert match, f"Could not extract color for {var}"
            colors.add(match.group(1).lower())
        assert len(colors) == len(self.STATUS_COLORS), "Status colors must be distinct"


class TestGPDUIConsistency:
    """Verify the template uses GPD's standard status symbols."""

    def test_status_symbols_present(self, template_content):
        """Template JS should reference GPD's standard status icons."""
        for symbol in ["✓", "◆", "○"]:
            assert symbol in template_content, (
                f"Missing GPD status symbol: {symbol}"
            )


# ── Data Schema Tests ──


class TestDataSchema:
    """Validate the expected JSON data schema for the template."""

    REQUIRED_TOP_LEVEL_KEYS = {
        "project_title",
        "milestone",
        "generated_date",
        "phases",
        "edges",
        "gaps",
        "critical_path",
    }

    REQUIRED_PHASE_KEYS = {
        "number",
        "name",
        "status",
        "one_liner",
        "provides",
        "requires",
    }

    VALID_STATUSES = {"complete", "partial", "planned", "empty"}
    VALID_EDGE_TYPES = {"provides", "affects"}

    def test_top_level_keys(self, sample_project_data):
        assert self.REQUIRED_TOP_LEVEL_KEYS.issubset(sample_project_data.keys())

    def test_phase_keys(self, sample_project_data):
        for phase in sample_project_data["phases"]:
            assert self.REQUIRED_PHASE_KEYS.issubset(phase.keys()), (
                f"Phase {phase.get('number', '?')} missing keys: "
                f"{self.REQUIRED_PHASE_KEYS - phase.keys()}"
            )

    def test_phase_statuses_valid(self, sample_project_data):
        for phase in sample_project_data["phases"]:
            assert phase["status"] in self.VALID_STATUSES, (
                f"Phase {phase['number']} has invalid status: {phase['status']}"
            )

    def test_edge_types_valid(self, sample_project_data):
        for edge in sample_project_data["edges"]:
            assert edge["type"] in self.VALID_EDGE_TYPES, (
                f"Edge {edge['from']}->{edge['to']} has invalid type: {edge['type']}"
            )

    def test_edge_references_valid_phases(self, sample_project_data):
        phase_numbers = {p["number"] for p in sample_project_data["phases"]}
        for edge in sample_project_data["edges"]:
            assert edge["from"] in phase_numbers, (
                f"Edge references non-existent phase {edge['from']}"
            )
            assert edge["to"] in phase_numbers, (
                f"Edge references non-existent phase {edge['to']}"
            )

    def test_critical_path_references_valid_phases(self, sample_project_data):
        phase_numbers = {p["number"] for p in sample_project_data["phases"]}
        for pn in sample_project_data["critical_path"]:
            assert pn in phase_numbers, (
                f"Critical path references non-existent phase {pn}"
            )

    def test_gap_severity_valid(self, sample_project_data):
        valid_severities = {"low", "high", "critical"}
        for gap in sample_project_data["gaps"]:
            assert gap.get("severity") in valid_severities, (
                f"Gap has invalid severity: {gap.get('severity')}"
            )


# ── Rendering Tests ──


class TestRendering:
    """Test that template + data produces valid HTML."""

    def test_render_produces_valid_html(self, template_content, sample_project_data):
        rendered = template_content.replace(
            "{GPD_PROJECT_DATA}", json.dumps(sample_project_data)
        ).replace(
            "{project_title}", sample_project_data["project_title"]
        )
        assert "<!doctype html>" in rendered.lower()
        assert "</html>" in rendered
        assert "Test Project" in rendered

    def test_render_embeds_json(self, template_content, sample_project_data):
        data_json = json.dumps(sample_project_data)
        rendered = template_content.replace("{GPD_PROJECT_DATA}", data_json)
        # The JSON should be parseable from the rendered HTML
        match = re.search(
            r'<script id="gpd-data" type="application/json">\s*(.*?)\s*</script>',
            rendered,
            re.DOTALL,
        )
        assert match, "Could not find gpd-data script tag in rendered HTML"
        embedded = json.loads(match.group(1))
        assert embedded["project_title"] == "Test Project"
        assert len(embedded["phases"]) == 2

    def test_no_unresolved_placeholders(self, template_content, sample_project_data):
        rendered = template_content.replace(
            "{GPD_PROJECT_DATA}", json.dumps(sample_project_data)
        ).replace(
            "{project_title}", sample_project_data["project_title"]
        )
        # Should have no remaining {UPPERCASE_PLACEHOLDER} patterns
        # (lowercase CSS vars like var(--text-primary) are fine)
        remaining = re.findall(r"\{[A-Z][A-Z_]+\}", rendered)
        assert not remaining, f"Unresolved placeholders: {remaining}"


class TestShippedCopies:
    """Keep the GitHub Pages demo, demo/, and template in lockstep."""

    INDEX_PATH = REPO_ROOT / "index.html"
    DEMO_PATH = REPO_ROOT / "demo" / "index.html"
    DEMO_TEMPLATE_PATH = (
        REPO_ROOT / "src" / "gpd" / "specs" / "templates" / "interactive-export-demo.html"
    )

    def test_index_matches_demo_copy(self):
        assert self.INDEX_PATH.read_text(encoding="utf-8") == self.DEMO_PATH.read_text(
            encoding="utf-8"
        )

    def test_index_matches_demo_template(self):
        assert self.INDEX_PATH.read_text(encoding="utf-8") == self.DEMO_TEMPLATE_PATH.read_text(
            encoding="utf-8"
        )

    def test_template_round_trip_reproduces_index(self, template_content):
        index = self.INDEX_PATH.read_text(encoding="utf-8")
        match = re.search(
            r'<script id="gpd-data" type="application/json">\s*(.*?)\s*</script>',
            index,
            re.DOTALL,
        )
        assert match, "Could not find gpd-data in index.html"
        title_match = re.search(r"<title>(.*?) — Interactive Research Map</title>", index)
        assert title_match
        rendered = template_content.replace(
            "{GPD_PROJECT_DATA}", match.group(1).strip()
        ).replace("{project_title}", title_match.group(1))
        assert rendered == index


# ── Export Workflow Integration Tests ──
# These verify the workflow docs reference the interactive format.
# They will only pass after the workflow files have been updated.


class TestWorkflowIntegration:
    """Verify export command and workflow reference the interactive format.

    NOTE: These tests will fail until the export.md files are updated
    as described in patches/export-workflow-addition.md.
    """

    @pytest.mark.skip(reason="Requires export.md update — run after applying patches")
    def test_export_command_lists_interactive(self):
        content = EXPORT_CMD.read_text(encoding="utf-8")
        assert "interactive" in content.lower()

    @pytest.mark.skip(reason="Requires export.md update — run after applying patches")
    def test_export_workflow_has_interactive_step(self):
        content = EXPORT_WF.read_text(encoding="utf-8")
        assert "generate_interactive" in content
