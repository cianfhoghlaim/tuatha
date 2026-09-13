## MODIFIED Requirements

### Requirement: Celtic asset generation via ANAM capture pipeline

The system SHALL provide a Celtic asset generation pipeline that
extracts graphics from 3 corpora — **Hades boons** (game),
**X-Men powers** (animation), and **Avatar elemental bending**
(animation) — via dedicated VLMs, emits typed BAML records
describing the power system per source, and maps each record to
a Celtic Tuatha Dé deity + a turquoise/blue particle palette.

#### Scenario: Hades boon extraction

- **GIVEN** a Hades gameplay screenshot showing a boon icon
  (`s3://cianfhoghlaim-tuatha-raw/hades/<run_id>/keyframes/`)
- **WHEN** the `ExtractHadesBoon(image)` BAML function runs via
  the VLM default `qwen3-vl-8b` (resolved through
  `MODEL_REGISTRY.resolve("ocr_vision", "hades_boon")`)
- **THEN** the function returns a `HadesBoon` record with
  `boon_id`, `god`, `tier` (Common/Rare/Epic/Legendary/Duo),
  `slot`, `effect_text`, `color_hex`, `particle_motion`,
  `ui_position`, `run_id`, `frame_index`, `captured_at`
- **AND** the `MapToAnamParticle(source, source_payload)` join
  maps the boon to an `AnamParticle` with a Celtic-deity name
  (e.g. `Athena → Danu`, `Zeus → Taranis`,
  `Poseidon → Manannán`)
- **AND** the row writes to the Lance table
  `cianfhoghlaim.tuatha.hades.boons`

#### Scenario: X-Men: Evolution scene extraction

- **GIVEN** an X-Men: Evolution (2000-2003, Marvel Animation)
  episode still showing a mutant power usage
  (`s3://cianfhoghlaim-tuatha-raw/xmen/<episode>/keyframes/`)
- **WHEN** the `ExtractXmenScene(image)` BAML function runs via
  the VLM default `molmo2-8b` (resolved through
  `MODEL_REGISTRY.resolve("ocr_vision", "xmen_scene")`)
- **THEN** the function returns an `XmenScene` record with
  `scene_id`, `character` (one of the full 30+ character
  roster: Cyclops, Jean Grey, Wolverine, Storm, Rogue, Beast,
  Shadowcat, Nightcrawler, Spyke, Mystique, Toad, Avalanche,
  Blob, Pyro, Magneto, Sabretooth, Multiple Man, Polaris,
  Wolfsbane, Forge, Professor X, Gambit, Scarlet Witch cameo,
  Quicksilver cameo), `team` (XMen / Brotherhood / XFactor /
  Independents / Humans / Unknown), `ability_name`,
  `power_class` (Alpha / Beta / Omega / Unknown), `effect_text`,
  `color_hex`, `particle_motion` (RadialBurst / DirectedJet /
  AmbientAura / Transformation / Absorption / Unknown),
  `episode`, `timestamp`
- **AND** the `MapToAnamParticle(source, source_payload)` join
  maps the power to an `AnamParticle` with a Celtic-deity name
  (e.g. `Cyclops → Taranis`, `Storm → Manannán/Taranis`,
  `Wolverine → Cernunnos`, `Mystique → TheMorrígan`)
- **AND** the row writes to the Lance table
  `cianfhoghlaim.tuatha.xmen.scenes`

#### Scenario: Avatar elemental bending extraction

- **GIVEN** an Avatar: The Last Airbender episode still showing
  an elemental bending usage
  (`s3://cianfhoghlaim-tuatha-raw/avatar/<episode>/keyframes/`)
- **WHEN** the `ExtractAnimationDescriptor(image)` BAML function
  runs via the VLM default `molmo2-8b`
- **THEN** the function returns a `MediaDescriptor` with
  `power_event.element ∈ {air, water, fire, earth, spirit}`,
  `palette` (dominant + accent + emissive hex),
  `vfx_vocabulary` (particle class / density / trail /
  dissipation), `narrative_beat`
- **AND** the `MapToAnamParticle(source, source_payload)` join
  maps the element to an `AnamParticle` with a Celtic-deity
  name (e.g. `air → TheMorrígan`, `water → Manannán`,
  `fire → Taranis`, `earth → TheDagda`, `spirit → Danu`)
- **AND** the row writes to the Lance table
  `cianfhoghlaim.tuatha.avatar.scenes`

#### Scenario: Cross-source join + ΔE CIE76 colour anchor gate

- **GIVEN** the 3 Lance tables
  (`cianfhoghlaim.tuatha.{hades.boons, xmen.scenes,
  avatar.scenes}`) populated with source rows
- **WHEN** the `anam_particles_v1` Dagster asset runs
- **THEN** the cross-source join produces rows in
  `cianfhoghlaim.tuatha.anam.particles`
- **AND** the `@asset_check ragas_anam_color_anchor` (or the
  ADK `AnamColorAnchorTrajectoryEvaluator` after the 2026-08-27
  change) measures ΔE CIE76 between each source's
  `color_hex` and the derived `anam_color_hex`
- **AND** rows with ΔE > 8.0 are flagged for review (min_score
  ≥ 0.85 to pass)
