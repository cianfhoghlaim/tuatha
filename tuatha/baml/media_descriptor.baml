// tuatha/baml/media_descriptor.baml — the 5-class media descriptor contracts.
//
// One function per medium (comic / prose / animation / gameplay /
// official_document). Each takes a tuple of rung-1+2 evidence + a rung-3
// DuckDB row + an optional exemplar excerpt, and emits a typed MediaDescriptor
// that satisfies the G7 (every row has source_url + sha256 + page + subject)
// and the G11 (every lore artefact has >=1 citation) contracts.
//
// Used by the 10-tool agents/media_intel/media_descriptor_agent.py.

client minimax

class MediaDescriptor {
  work         string
  medium       string
  language     string
  source_url   string
  source_page  int
  provenance_sha256 string
  provenance_page   int
  rung3_excerpt  string
  power_event      string
  visual_grammar   string
  palette          string
  vfx_vocabulary   string
  narrative_beat   string
  transferability  string
  shippable        bool       // always false per Evidence Ladder invariant
}


function ExtractComicDescriptor(
  image_b64: string,
  caption_text: string,
  source_url: string,
  source_page: int,
  rung1_sha256: string,
  rung2_excerpt: string,
) -> MediaDescriptor {
  client minimax
  prompt #"
    You are the canonical BAML extractor for comic panels.
    Given the panel image (base64) and caption text:
    {{ caption_text }}
    from source URL {{ source_url }} page {{ source_page }} with rung-1
    sha256 {{ rung1_sha256 }} and rung-2 excerpt:
    {{ rung2_excerpt }}
    return a MediaDescriptor with work, medium='comic', language, source_url,
    source_page, provenance_sha256, provenance_page, rung3_excerpt,
    power_event, visual_grammar, palette, vfx_vocabulary,
    narrative_beat, transferability, shippable=false.
  "#
}

function ExtractProseDescriptor(
  text: string,
  source_url: string,
  source_paragraph: int,
  rung1_sha256: string,
  rung2_excerpt: string,
) -> MediaDescriptor {
  client minimax
  prompt #"
    You are the canonical BAML extractor for prose passages.
    Given the text:
    {{ text }}
    from source URL {{ source_url }} paragraph {{ source_paragraph }} with rung-1
    sha256 {{ rung1_sha256 }} and rung-2 excerpt:
    {{ rung2_excerpt }}
    return a MediaDescriptor with work, medium='prose', language, source_url,
    source_paragraph (as source_page), provenance_sha256, provenance_page,
    rung3_excerpt, power_event, visual_grammar, palette, vfx_vocabulary,
    narrative_beat, transferability, shippable=false.
  "#
}

function ExtractAnimationDescriptor(
  image_b64: string,
  audio_b64: string?,
  subtitle: string?,
  source_url: string,
  source_frame: int,
  rung1_sha256: string,
  rung2_excerpt: string,
) -> MediaDescriptor {
  client minimax
  prompt #"
    You are the canonical BAML extractor for animation frames.
    Given the frame image (base64) with audio (base64, optional) and subtitle:
    {{ subtitle }}
    from source URL {{ source_url }} frame {{ source_frame }} with rung-1
    sha256 {{ rung1_sha256 }} and rung-2 excerpt:
    {{ rung2_excerpt }}
    return a MediaDescriptor with work, medium='animation', language,
    source_url, source_frame (as source_page), provenance_sha256,
    provenance_page, rung3_excerpt, power_event, visual_grammar, palette,
    vfx_vocabulary, narrative_beat, transferability, shippable=false.
  "#
}

function ExtractGameplayDescriptor(
  image_b64: string,
  session_log: string,
  source_url: string,
  source_timestamp: string,
  rung1_sha256: string,
  rung2_excerpt: string,
) -> MediaDescriptor {
  client minimax
  prompt #"
    You are the canonical BAML extractor for gameplay screenshots.
    Given the frame image (base64) and session log:
    {{ session_log }}
    from source URL {{ source_url }} timestamp {{ source_timestamp }} with
    rung-1 sha256 {{ rung1_sha256 }} and rung-2 excerpt:
    {{ rung2_excerpt }}
    return a MediaDescriptor with work, medium='gameplay', language,
    source_url, source_page (epoch ms from timestamp), provenance_sha256,
    provenance_page, rung3_excerpt, power_event, visual_grammar, palette,
    vfx_vocabulary, narrative_beat, transferability, shippable=false.
  "#
}

function ExtractOfficialDocumentDescriptor(
  pdf_pages: string,
  metadata: string,
  source_url: string,
  source_timestamp: string,
  rung1_sha256: string,
  rung2_excerpt: string,
) -> MediaDescriptor {
  client minimax
  prompt #"
    You are the canonical BAML extractor for official documents.
    Given the PDF pages:
    {{ pdf_pages }}
    with metadata:
    {{ metadata }}
    from source URL {{ source_url }} fetched at {{ source_timestamp }} with
    rung-1 sha256 {{ rung1_sha256 }} and rung-2 excerpt:
    {{ rung2_excerpt }}
    return a MediaDescriptor with work, medium='official', language,
    source_url, source_page, provenance_sha256, provenance_page,
    rung3_excerpt, power_event, visual_grammar, palette, vfx_vocabulary,
    narrative_beat, transferability, shippable=false.
  "#
}
