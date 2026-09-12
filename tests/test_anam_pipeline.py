"""Tests for the ANAM capture pipeline.

The pipeline needs a live Lance namespace and a vision model to do
anything, so these tests cover the parts that can go wrong silently
without either: the table namespace tuatha is allowed to write, the
BAML contract, and the ``shippable: false`` invariant that keeps
copyrighted frames out of the repository.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
BAML = REPO / "tuatha" / "baml" / "anam_capture.baml"
SOURCES = REPO / "tuatha" / "sources" / "anam"
COCOINDEX = REPO / "tuatha" / "cocoindex" / "anam"

SOURCE_IDS = ("hades", "comic", "gba")


@pytest.fixture(scope="module")
def manifests() -> dict[str, dict]:
    return {
        name: yaml.safe_load((SOURCES / name / "source.yaml").read_text())
        for name in SOURCE_IDS
    }


class TestNamespaceOwnership:
    """tuatha writes only `cianfhoghlaim.tuatha.*`. See corpus/CONTRACT.md.

    Both repos share one Lance namespace, so nothing but this check
    stops an ANAM App from writing over the education corpus.
    """

    def test_every_app_writes_inside_the_tuatha_namespace(self):
        from tuatha.cocoindex.anam import ANAM_TABLES

        for app, table in ANAM_TABLES.items():
            assert table.startswith("cianfhoghlaim.tuatha."), (
                f"App {app} writes {table}, which is outside the namespace "
                "tuatha owns"
            )

    def test_declared_tables_match_the_app_modules(self):
        from tuatha.cocoindex.anam import ANAM_TABLES

        declared = set(ANAM_TABLES.values())
        found = set()
        for module in COCOINDEX.glob("*.py"):
            for line in module.read_text().splitlines():
                if line.startswith("TABLE_NAME = "):
                    found.add(line.split("=", 1)[1].strip().strip('"'))
        assert found == declared, (
            "the table names declared in __init__ have drifted from the "
            f"App modules: {found ^ declared}"
        )

    def test_the_join_reads_the_three_source_tables(self):
        from tuatha.cocoindex.anam import ANAM_SOURCE_TABLES, ANAM_TABLES

        assert set(ANAM_SOURCE_TABLES) == set(ANAM_TABLES.values()) - {
            "cianfhoghlaim.tuatha.anam_particles"
        }


class TestShippableInvariant:
    """No copyrighted frame, panel or page may enter the repository."""

    def test_every_source_declares_shippable_false(self, manifests):
        for name, manifest in manifests.items():
            assert manifest["shippable"] is False, (
                f"{name} must declare shippable: false — the descriptor is "
                "description-only and the pixels stay in the private volume"
            )

    def test_every_source_carries_legal_notes(self, manifests):
        for name, manifest in manifests.items():
            notes = manifest.get("legal_notes", "")
            assert len(notes.strip()) > 100, f"{name} has no substantive legal_notes"

    def test_every_source_names_a_rights_holder(self, manifests):
        for name, manifest in manifests.items():
            holder = manifest["source"].get("rights_holder", "")
            assert holder, f"{name} names no rights holder"
            assert holder != "Wikipedia Foundation", (
                f"{name} must name the original publisher, not an aggregator"
            )

    def test_raw_capture_stays_in_the_private_bucket(self, manifests):
        for name, manifest in manifests.items():
            bucket = manifest["ingest"]["raw_bucket"]
            assert bucket.startswith("s3://cianfhoghlaim-tuatha-raw/"), (
                f"{name} writes raw capture to {bucket}, outside the private volume"
            )

    def test_thumbnails_are_bounded(self, manifests):
        # An unbounded thumbnail is a full-resolution frame by another name.
        for name, manifest in manifests.items():
            max_px = manifest["extraction"]["thumbnail_max_px"]
            assert 0 < max_px <= 1024, f"{name} thumbnail_max_px={max_px} is not bounded"


class TestSourceManifests:
    def test_each_manifest_targets_its_own_lance_table(self, manifests):
        from tuatha.cocoindex.anam import ANAM_TABLES

        for name, manifest in manifests.items():
            table = manifest["outputs"]["lance_table"]
            assert table in ANAM_TABLES.values(), (
                f"{name} targets {table}, which no App writes"
            )

    def test_each_manifest_names_a_flow_that_exists(self, manifests):
        from tuatha.cocoindex.anam import ANAM_TABLES

        for name, manifest in manifests.items():
            flow = manifest["extraction"]["flow"]
            assert flow in ANAM_TABLES, f"{name} names unknown flow {flow}"

    def test_model_is_resolved_not_hardcoded(self, manifests):
        for name, manifest in manifests.items():
            model = manifest["extraction"]["vision_model"]
            assert model.startswith("${"), (
                f"{name} hardcodes vision_model={model}; it must resolve through "
                "the role registry so a deployment can override it"
            )

    def test_declared_env_vars_are_declared_roles(self, manifests):
        from tuatha.models import ROLES

        known = {spec.env_var for spec in ROLES.values()}
        for name, manifest in manifests.items():
            var = manifest["extraction"]["vision_model"].strip("${}")
            assert var in known, (
                f"{name} references ${{{var}}}, which no role in "
                "tuatha.models.registry declares"
            )


class TestColorAnchorMetric:
    """The ANAM colour-anchor gate.

    The claim this measures is that ANAM colours are *derived* from real
    sources rather than chosen. The measurement is what makes that claim
    falsifiable, so it has to be a real one — it previously returned a
    hardcoded 0.92 and reported WARN on both branches of its severity
    conditional, meaning it could neither fail nor tell the truth.
    """

    @staticmethod
    def _measure(pairs, **kw):
        from tuatha.dagster.anam import measure_color_anchor

        return measure_color_anchor(pairs, **kw)

    def test_identical_colours_score_perfectly(self):
        result = self._measure([("#00CED1", "#00CED1")] * 5)
        assert result["score"] == 1.0
        assert result["max_delta_e"] == pytest.approx(0.0)

    def test_wildly_drifted_colours_fail(self):
        # Turquoise mapped to red is not a derivation.
        result = self._measure([("#00CED1", "#FF0000")] * 5)
        assert result["score"] == 0.0
        assert result["max_delta_e"] > 100

    def test_score_is_the_fraction_within_threshold(self):
        pairs = [("#00CED1", "#00CED1")] * 3 + [("#00CED1", "#FF0000")] * 1
        assert self._measure(pairs)["score"] == pytest.approx(0.75)

    def test_no_rows_scores_zero_not_one(self):
        # A vacuous pass is how a broken join gets promoted.
        result = self._measure([])
        assert result["score"] == 0.0
        assert result["evaluated"] == 0

    def test_malformed_colours_count_against_the_score(self):
        # Rows the metric cannot parse must not be quietly dropped from
        # the denominator, or a pipeline emitting garbage scores 1.0.
        pairs = [("#00CED1", "#00CED1"), ("not-a-colour", "#00CED1")]
        result = self._measure(pairs)
        assert result["malformed"] == 1
        assert result["score"] == pytest.approx(0.5)

    def test_threshold_is_adjustable(self):
        pairs = [("#00CED1", "#00BFDF")]
        assert self._measure(pairs, threshold=1.0)["score"] == 0.0
        assert self._measure(pairs, threshold=50.0)["score"] == 1.0

    def test_the_declared_threshold_is_perceptually_meaningful(self):
        from tuatha.dagster.anam import ANAM_DELTA_E_THRESHOLD
        from tuatha.theming.color import DELTA_E_PERCEPTIBLE

        # The gate permits visible drift toward the ANAM palette; it is
        # not asking for an imperceptible match.
        assert ANAM_DELTA_E_THRESHOLD > DELTA_E_PERCEPTIBLE


class TestColorSpace:
    def test_malformed_hex_raises_rather_than_defaulting_to_black(self):
        from tuatha.theming.color import hex_to_rgb

        # Returning (0, 0, 0) would make a parse failure look like a
        # deliberate colour choice, and the gate would then score it.
        for bad in ("", "#12345", "rgb(1,2,3)", "#GGGGGG"):
            with pytest.raises(ValueError):
                hex_to_rgb(bad)

    def test_known_lab_anchors(self):
        from tuatha.theming.color import rgb_to_lab

        lightness, a_star, b_star = rgb_to_lab((255, 255, 255))
        assert lightness == pytest.approx(100.0, abs=0.5)
        assert a_star == pytest.approx(0.0, abs=0.5)
        assert b_star == pytest.approx(0.0, abs=0.5)
        assert rgb_to_lab((0, 0, 0))[0] == pytest.approx(0.0, abs=0.5)

    def test_delta_e_is_symmetric(self):
        from tuatha.theming.color import delta_e

        assert delta_e("#00CED1", "#4B0082") == pytest.approx(
            delta_e("#4B0082", "#00CED1")
        )

    def test_accepts_hex_with_or_without_hash(self):
        from tuatha.theming.color import hex_to_rgb

        assert hex_to_rgb("#00CED1") == hex_to_rgb("00CED1")


@pytest.fixture(scope="module")
def baml() -> str:
    return BAML.read_text()


class TestDagsterGraph:
    """The asset graph must actually build.

    Two failure modes here are silent until deploy: a `Config` subclass
    that Dagster cannot resolve (which happens whenever the module uses
    postponed annotation evaluation), and an asset whose upstream
    dependency does not exist.
    """

    @staticmethod
    def _defs():
        import tuatha.dagster.anam as anam

        from dagster import (
            Definitions,
            load_asset_checks_from_modules,
            load_assets_from_modules,
        )

        assets = load_assets_from_modules([anam])
        checks = load_asset_checks_from_modules([anam])
        return Definitions(assets=assets, asset_checks=checks), assets, checks

    def test_definitions_build(self):
        defs, _, _ = self._defs()
        assert defs is not None

    def test_the_three_capture_groups_are_populated(self):
        _, assets, _ = self._defs()
        groups: dict[str, set[str]] = {}
        for ad in assets:
            for key in ad.keys:
                groups.setdefault(ad.group_names_by_key[key], set()).add(
                    key.to_user_string()
                )
        assert groups["tuatha_capture"] == {
            "hades_raw_captures",
            "comic_raw_pages",
            "gba_raw_frames",
            "xmen_raw_scenes",        # added 2026-08-27 (X-Men: Evolution corpus)
        }
        assert groups["tuatha_embed"] == {
            "hades_boons_embedded",
            "comic_particles_embedded",
            "gba_magic_embedded",
            "xmen_scenes_embedded",    # added 2026-08-27
        }
        assert groups["tuatha_join"] == {"anam_particles_v1"}

    def test_the_ragas_check_guards_the_join(self):
        _, _, checks = self._defs()
        specs = [s for c in checks for s in c.check_specs]
        assert [s.name for s in specs] == ["ragas_anam_color_anchor"]
        assert specs[0].asset_key.to_user_string() == "anam_particles_v1"

    def test_cocoindex_runs_from_this_repo(self, tmp_path, monkeypatch):
        # The cocoindex CLI cwd used to be a hardcoded absolute path to
        # the cianfhoghlaim monorepo; the Apps live here now.
        import tuatha.dagster.anam as anam

        assert (pathlib.Path(anam._repo_root()) / "pyproject.toml").exists()
        monkeypatch.setenv("TUATHA_REPO_ROOT", str(tmp_path))
        assert anam._repo_root() == str(tmp_path)


class TestBamlContract:

    @pytest.mark.parametrize(
        "cls", ["HadesBoon", "ComicParticleFrame", "GbaMagicSystem", "AnamParticle"]
    )
    def test_declares_the_four_record_classes(self, baml, cls):
        assert f"class {cls} {{" in baml

    @pytest.mark.parametrize(
        "fn",
        [
            "ExtractHadesBoon",
            "ExtractComicParticle",
            "ExtractGbaMagic",
            "MapToAnamParticle",
        ],
    )
    def test_declares_the_extraction_functions(self, baml, fn):
        assert f"function {fn}(" in baml

    def test_clients_resolve_models_from_the_environment(self, baml):
        # A literal model name in a BAML client cannot be overridden by
        # a deployment, which is how model choice drifts out of the
        # registry.
        for var in (
            "env.VISION_MODEL_HADES",
            "env.VISION_MODEL_COMIC",
            "env.VISION_MODEL_GBA",
        ):
            assert var in baml

    def test_ships_test_cases(self, baml):
        assert baml.count("test ") >= 3, "the BAML contract has no test fixtures"
