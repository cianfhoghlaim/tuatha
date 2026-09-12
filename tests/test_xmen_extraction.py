"""Tests for the X-Men: Evolution ANAM extraction (Class F animation).

Added by the 2026-08-27 ANAM capture pipeline port + 3-corpus expansion
change.

Tests:
- BAML schema validation (XmenScene + XmenPowerClass + XmenTeam +
  XmenParticleMotion + XmenPowerUsage classes)
- Lance table namespace ownership (cianfhoghlaim.tuatha.xmen.scenes)
- Shippable invariant (shippable=False always)
- Cross-source join (xmen.scenes → anam.particles via bias_mode='balanced')
- The 30+ character roster is embedded in the BAML prompt
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
BAML_FILE = REPO_ROOT / "tuatha" / "baml" / "anam_xmen.baml"
SOURCE_YAML = (
    REPO_ROOT / "tuatha" / "sources" / "anam" / "xmen_evolution" / "source.yaml"
)
COCO_APP = REPO_ROOT / "tuatha" / "cocoindex" / "anam" / "xmen_scenes.py"


class TestXmenBamlSchema:
    """The BAML schema validation tests."""

    def test_baml_file_exists(self) -> None:
        assert BAML_FILE.exists(), f"Missing BAML file: {BAML_FILE}"

    def test_baml_defines_xmen_scene_class(self) -> None:
        content = BAML_FILE.read_text()
        assert "class XmenScene {" in content
        assert "scene_id" in content
        assert "character" in content
        assert "team" in content
        assert "ability_name" in content
        assert "power_class" in content
        assert "color_hex" in content
        assert "particle_motion" in content
        assert "shippable" in content

    def test_baml_defines_power_class_enum(self) -> None:
        content = BAML_FILE.read_text()
        assert "enum XmenPowerClass {" in content
        assert "Alpha" in content
        assert "Beta" in content
        assert "Omega" in content

    def test_baml_defines_team_enum(self) -> None:
        content = BAML_FILE.read_text()
        assert "enum XmenTeam {" in content
        assert "XMen" in content
        assert "Brotherhood" in content
        assert "XFactor" in content
        assert "Independents" in content

    def test_baml_defines_particle_motion_enum(self) -> None:
        content = BAML_FILE.read_text()
        assert "enum XmenParticleMotion {" in content
        assert "RadialBurst" in content
        assert "DirectedJet" in content
        assert "AmbientAura" in content
        assert "Transformation" in content
        assert "Absorption" in content

    def test_baml_extract_function(self) -> None:
        content = BAML_FILE.read_text()
        assert "function ExtractXmenScene(image: image) -> XmenScene" in content
        assert "client XmenSceneClient" in content
        assert "LANGUAGE: English only" in content

    def test_baml_test_cases_present(self) -> None:
        content = BAML_FILE.read_text()
        assert "test xmen_cyclops_optic_blast" in content
        assert "test xmen_storm_weather_control" in content
        assert "test xmen_jean_grey_telepathy" in content

    def test_baml_full_character_roster(self) -> None:
        content = BAML_FILE.read_text()
        # Spot-check the 30+ character roster
        for character in [
            "Cyclops",
            "Jean Grey",
            "Wolverine",
            "Storm",
            "Rogue",
            "Beast",
            "Shadowcat",
            "Nightcrawler",
            "Spyke",
            "Mystique",
            "Toad",
            "Avalanche",
            "Blob",
            "Pyro",
            "Magneto",
            "Sabretooth",
            "Multiple Man",
            "Polaris",
            "Wolfsbane",
            "Forge",
            "Professor X",
            "Gambit",
            "Scarlet Witch",
            "Quicksilver",
        ]:
            assert character in content, (
                f"Missing character {character!r} in BAML XMEN_ROSTER"
            )


class TestXmenSourceYaml:
    """The source.yaml manifest tests."""

    def test_source_yaml_exists(self) -> None:
        assert SOURCE_YAML.exists(), f"Missing source.yaml: {SOURCE_YAML}"

    def test_source_yaml_shippable_false(self) -> None:
        content = SOURCE_YAML.read_text()
        assert "shippable: false" in content

    def test_source_yaml_has_legal_notes(self) -> None:
        content = SOURCE_YAML.read_text()
        assert "legal_notes:" in content
        assert "Marvel Animation" in content
        assert "Disney+" in content

    def test_source_yaml_no_wikipedia(self) -> None:
        """Per AGENTS.md: never use 'Wikipedia Foundation' as rights_holder."""
        content = SOURCE_YAML.read_text()
        assert "Wikipedia Foundation" not in content

    def test_source_yaml_lance_table(self) -> None:
        content = SOURCE_YAML.read_text()
        assert "cianfhoghlaim.tuatha.xmen.scenes" in content


class TestXmenCocoIndexApp:
    """The CocoIndex App tests."""

    def test_coco_app_exists(self) -> None:
        assert COCO_APP.exists(), f"Missing CocoIndex app: {COCO_APP}"

    def test_coco_app_table_name(self) -> None:
        content = COCO_APP.read_text()
        assert "TABLE_NAME = \"cianfhoghlaim.tuatha.xmen.scenes\"" in content

    def test_coco_app_via_hermes(self) -> None:
        """Per the 2026-08-27 change: Hermes Agent replaces the Swift daemon."""
        content = COCO_APP.read_text()
        assert "Hermes" in content or "hermes_client" in content


class TestXmenCrossSourceJoin:
    """The anam_particles.py cross-source join tests."""

    def test_xmen_added_to_source_tables(self) -> None:
        anam_particles = REPO_ROOT / "tuatha" / "cocoindex" / "anam" / "anam_particles.py"
        content = anam_particles.read_text()
        assert "cianfhoghlaim.tuatha.xmen.scenes" in content

    def test_xmen_bias_mode_balanced(self) -> None:
        anam_particles = REPO_ROOT / "tuatha" / "cocoindex" / "anam" / "anam_particles.py"
        content = anam_particles.read_text()
        assert '"xmen.scenes": "balanced"' in content


class TestXmenDagsterAssets:
    """The Dagster asset tests."""

    def test_dagster_xmen_raw_scenes(self) -> None:
        anam_py = REPO_ROOT / "tuatha" / "dagster" / "anam.py"
        content = anam_py.read_text()
        assert "def xmen_raw_scenes(" in content

    def test_dagster_xmen_scenes_embedded(self) -> None:
        anam_py = REPO_ROOT / "tuatha" / "dagster" / "anam.py"
        content = anam_py.read_text()
        assert "def xmen_scenes_embedded(" in content
        assert "tuatha_xmen_scenes" in content


class TestXmenMediaDescriptorTool:
    """The media_descriptor_agent tests."""

    def test_extract_xmen_descriptor_tool_defined(self) -> None:
        media_agent = (
            REPO_ROOT / "tuatha" / "agents" / "media_intel" / "media_descriptor_agent.py"
        )
        content = media_agent.read_text()
        assert "def extract_xmen_descriptor_tool(" in content

    def test_extract_xmen_in_tools_list(self) -> None:
        media_agent = (
            REPO_ROOT / "tuatha" / "agents" / "media_intel" / "media_descriptor_agent.py"
        )
        content = media_agent.read_text()
        assert '"extract_xmen_descriptor"' in content

    def test_xmen_rights_holder(self) -> None:
        """Per the 2026-08-27 change: rights_holder = Marvel Animation / Disney+."""
        media_agent = (
            REPO_ROOT / "tuatha" / "agents" / "media_intel" / "media_descriptor_agent.py"
        )
        content = media_agent.read_text()
        assert "Marvel Animation / Disney+" in content

    def test_no_wikipedia_rights_holder(self) -> None:
        media_agent = (
            REPO_ROOT / "tuatha" / "agents" / "media_intel" / "media_descriptor_agent.py"
        )
        content = media_agent.read_text()
        assert "Wikipedia Foundation" not in content


class TestXmenNotebookTab:
    """The marimo notebook tab tests."""

    def test_xmen_tab_exists(self) -> None:
        tab = REPO_ROOT / "tuatha" / "notebooks" / "anam" / "tabs" / "xmen_scenes.py"
        assert tab.exists()

    def test_xmen_tab_table_name(self) -> None:
        tab = REPO_ROOT / "tuatha" / "notebooks" / "anam" / "tabs" / "xmen_scenes.py"
        content = tab.read_text()
        assert "TABLE_XMEN" in content
        assert "cianfhoghlaim.tuatha.xmen.scenes" in content

    def test_xmen_tab_celtic_deity_map(self) -> None:
        tab = REPO_ROOT / "tuatha" / "notebooks" / "anam" / "tabs" / "xmen_scenes.py"
        content = tab.read_text()
        assert "Cyclops" in content
        assert "Taranis" in content
        assert "Cernunnos" in content
