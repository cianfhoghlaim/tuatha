// tuatha/baml/anam_xmen.baml
//
// The British Isles Formative Assessment MMO — X-Men: Evolution capture pipeline.
// Description-only extraction (per the tuatha skill: shippable=false invariant).
//
// One BAML class + 3 enums + 1 BAML function:
//   • XmenScene           — typed description of one X-Men scene still
//   • XmenPowerClass      — Alpha / Beta / Omega / Unknown
//   • XmenTeam            — XMen / Brotherhood / XFactor / Independents / Humans / Unknown
//   • XmenParticleMotion  — RadialBurst / DirectedJet / AmbientAura / Transformation / Absorption / Unknown
//   • ExtractXmenScene    — the canonical VLM extractor (molmo2-8b)

class XmenPowerUsage {
  ability_name       string                          @description("Canonical ability name, e.g. 'optic blast', 'weather control'")
  power_class        XmenPowerClass
  effect_text        string                          @description("English-only effect description; cite visual evidence only")
  color_hex          string                          @description("Dominant particle/icon color as #RRGGBB")
  particle_motion    XmenParticleMotion
  trigger            string?                         @description("What triggers the ability (if visible)")
  consequence        string?                         @description("What happens as a result (if visible)")
}

class XmenScene {
  scene_id              string                       @description("Deterministic: 'xmen:<SxxExx>:<mm:ss>:<character>:<ability>'")
  character             string                       @description("One of the full X-Men: Evolution roster; 'Unknown' if not identified")
  team                  XmenTeam
  ability_name          string?                      @description("The canonical ability name from the character")
  power_class           XmenPowerClass
  work                  string                       @description("'X-Men: Evolution (2000-2003)'")
  medium                string                       @description("'animation'")
  language              string                       @description("'en' (English only per 2026-08-27 change)")
  episode               string                       @description("e.g. 'S01E05'")
  timestamp             string                       @description("mm:ss within the episode")
  source_url            string                       @description("S3 path to the source frame")
  captured_at           string                       @description("ISO-8601 UTC timestamp")
  powers                XmenPowerUsage[]
  visual_grammar        string?                      @description("composition, shot type, motion lines, camera, silhouette")
  palette               string?                      @description("dominant + accent + emissive hex")
  vfx_vocabulary        string?                      @description("particle class, density, trail, dissipation")
  narrative_beat        string?                      @description("arc position + beat significance")
  transferability       string?                      @description("in_game_mechanic + anam_cost")
  provenance_sha256     string
  shippable             bool                         @description("ALWAYS false — the G7 shippable invariant")
}

enum XmenPowerClass {
  Alpha
  Beta
  Omega
  Unknown
}

enum XmenTeam {
  XMen
  Brotherhood
  XFactor
  Independents
  Humans
  Unknown
}

enum XmenParticleMotion {
  RadialBurst
  DirectedJet
  AmbientAura
  Transformation
  Absorption
  Unknown
}

class BoundingBox {
  x_min           float  @description("Normalized 0-1, top-left origin")
  y_min           float
  x_max           float
  y_max           float
}

// The X-Men scene client — routed via MODEL_REGISTRY ocr_vision:xmen_scene
// (the new role added by the 2026-08-27 centralized-model-registry delta).

client<llm> XmenSceneClient {
  provider      "openai-generic"
  base_url      env.LLAMASWAP_URL
  api_key       env.LLAMASWAP_API_KEY
  model_name    env.VISION_MODEL_XMEN       // resolves to MODEL_REGISTRY ocr_vision:xmen_scene
  max_tokens    1024
  temperature   0.0
}

// The canonical X-Men: Evolution character roster (30+ characters).
// Embedded in the prompt to give the VLM maximum context for
// character identification + ability mapping.

const XMEN_ROSTER = """
X-MEN TEAM:
  Cyclops (Scott Summers)            — optic blast (Alpha)
  Jean Grey (Marvel Girl)            — telepathy + telekinesis (Omega)
  Wolverine (Logan)                  — adamantium claws + healing (Beta)
  Storm (Ororo Munroe)               — weather manipulation (Omega)
  Rogue (Anna Marie)                 — power absorption via touch (Beta)
  Beast (Hank McCoy)                 — superhuman agility + transformation (Beta)
  Shadowcat (Kitty Pryde)            — intangibility / phasing (Beta)
  Nightcrawler (Kurt Wagner)         — teleportation + stealth (Beta)
  Spyke (Evan Daniels)               — spike protrusions + geo-leaping (Beta)

BROTHERHOOD OF MUTANTS:
  Mystique (Raven Darkhölme)         — shapeshifting (Beta)
  Toad (Mortimer Toynbee)            — tongue + wall-crawling (Beta)
  Avalanche (Dominic Petros)         — seismic vibration (Beta)
  Blob (Fred Dukes)                  — super-mass + immovability (Beta)
  Pyro (St. John Allerdyce)          — fire manipulation (needs source) (Beta)
  Magneto (Erik Lehnsherr)           — magnetism + metal manipulation (Omega)
  Sabretooth (Victor Creed)          — claws + super senses (Season 2) (Beta)

XFACTOR (Season 2+):
  Multiple Man (Jamie Madrox)        — duplication (Beta)
  Polaris (Lorna Dane)               — magnetism (Magneto's daughter) (Beta)
  Wolfsbane (Rahne Sinclair)         — lycanthropy transformation (Beta)
  Forge                              — technopathy / machine creation (Beta)

INDEPENDENTS:
  Professor X (Charles Xavier)       — telepathy (Omega)
  Gambit (Remy LeBeau)               — kinetic charge + card throwing (Beta)
  Scarlet Witch (cameo Season 2)     — reality warping (Omega)
  Quicksilver (cameo Season 2)       — super-speed (Alpha)
"""

// The canonical X-Men scene extractor.

function ExtractXmenScene(image: image) -> XmenScene {
  client XmenSceneClient
  prompt #"
    You are a precise visual animation analyst for X-Men: Evolution
    (Marvel Animation, 2000-2003, 52 episodes).

    {{ XMEN_ROSTER }}

    Extract a typed XmenScene from this frame. Identify:

    1. CHARACTER: name the character visible. If multiple
       characters are visible, choose the character whose
       power is being demonstrated (the VFX carrier).

    2. ABILITY: list every mutant ability visible in the
       frame. For each, cite the canonical ability name +
       the mutation class (Alpha / Beta / Omega) + the
       visual effect + the dominant colour + the particle
       motion (RadialBurst / DirectedJet / AmbientAura /
       Transformation / Absorption).

    3. SCENE METADATA: the episode (S01E05), the timestamp
       (mm:ss), the visual composition, the palette, the
       VFX vocabulary, the narrative beat.

    4. EVIDENCE: every claim MUST be visible in the frame.
       NEVER invent powers or abilities not visually
       demonstrated.

    LANGUAGE: English only. The character names + ability
    names are canonical; do not translate.

    Return an XmenScene matching the schema.
  "#
}

// Test cases (run via `baml-cli test` per the BAML skill).

test xmen_cyclops_optic_blast {
  functions [ExtractXmenScene]
  input {
    image "xmen_cyclops_optic_blast_S01E05_15_32.png"
  }
  output {
    scene_id "xmen:S01E05:15:32:cyclops:optic_blast"
    character "Cyclops"
    team XmenTeam::XMen
    ability_name "optic blast"
    power_class XmenPowerClass::Alpha
    color_hex "#FF0000"
    particle_motion XmenParticleMotion::DirectedJet
    episode "S01E05"
    language "en"
    shippable false
  }
}

test xmen_storm_weather_control {
  functions [ExtractXmenScene]
  input {
    image "xmen_storm_weather_S02E12_08_45.png"
  }
  output {
    scene_id "xmen:S02E12:08:45:storm:weather_control"
    character "Storm"
    team XmenTeam::XMen
    ability_name "weather control"
    power_class XmenPowerClass::Omega
    color_hex "#FFFFFF"
    particle_motion XmenParticleMotion::AmbientAura
    episode "S02E12"
    language "en"
    shippable false
  }
}

test xmen_jean_grey_telepathy {
  functions [ExtractXmenScene]
  input {
    image "xmen_jean_telepathy_S03E07_22_18.png"
  }
  output {
    scene_id "xmen:S03E07:22:18:jean_grey:telepathy"
    character "Jean Grey"
    team XmenTeam::XMen
    ability_name "telepathy"
    power_class XmenPowerClass::Omega
    color_hex "#FF69B4"
    particle_motion XmenParticleMotion::AmbientAura
    episode "S03E07"
    language "en"
    shippable false
  }
}
