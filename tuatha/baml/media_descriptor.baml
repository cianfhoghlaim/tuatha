// tuatha.baml.media_descriptor — the canonical BAML functions for the 5-class media descriptor pipeline.

client<llm> litellm_proxy

class MediaDescriptor {
  work string
  medium string
  language string
  source_url string
  source_timestamp string

  power_event string
  visual_grammar string
  palette string
  vfx_vocabulary string
  narrative_beat string
  transferability string
  provenance string

  shippable bool
}

function ExtractComicDescriptor(
  image: string,
  caption_text: string,
  source_url: string,
  source_page: int,
  work: string,
  language: string,
) -> MediaDescriptor {
  client minimax
  prompt #"Extract a 7-axis MediaDescriptor from a comic panel."#
}

function ExtractProseDescriptor(
  text: string,
  source_url: string,
  source_paragraph: int,
  work: string,
  language: string,
) -> MediaDescriptor {
  client minimax
  prompt #"Extract a 7-axis MediaDescriptor from a prose passage."#
}

function ExtractAnimationDescriptor(
  image: string,
  audio: string?,
  subtitle: string?,
  source_url: string,
  source_frame: int,
  work: string,
  language: string,
) -> MediaDescriptor {
  client minimax
  prompt #"Extract a 7-axis MediaDescriptor from an animation frame."#
}

function ExtractGameplayDescriptor(
  image: string,
  session_log: string,
  source_url: string,
  source_timestamp: string,
  work: string,
  language: string,
) -> MediaDescriptor {
  client minimax
  prompt #"Extract a 7-axis MediaDescriptor from a gameplay screenshot."#
}

function ExtractOfficialDocumentDescriptor(
  pdf_page: string,
  metadata: string,
  source_url: string,
  source_timestamp: string,
  work: string,
  language: string,
) -> MediaDescriptor {
  client minimax
  prompt #"Extract a 7-axis MediaDescriptor from an official document."#
}
