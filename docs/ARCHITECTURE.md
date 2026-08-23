# tuatha Architecture

The 5-layer architecture for the new tuatha/ sub-project.

## The 5 layers

1. **L1 Ingestion** (DLT): the 40 per-subject DLT sources
   (8 subjects × 5 categories) at `tuatha/dlt/`
2. **L2 Materials** (BAML): the 13 BAML contracts
   (8 qpack_<subject>.baml + 3 hackathon + 1 media_descriptor +
   1 clients) at `tuatha/baml/`
3. **L3 Model Lifecycle** (CocoIndex v1): the 4 CocoIndex apps
   (per_subject + cross_subject + hackathon + media_intel)
4. **L4 Asset Generation** (marimo): the 4 marimo notebooks
   (per-medium + cross-medium + hackathon + media_intel)
5. **L5 Agent Ops** (Google ADK): the 15 ADK agents
   (8 NCCA subject + 3 educational + 4 BIEP hackathon)
   + the 10-tool `media_descriptor_agent`

## The 4 agent types

- The 8 NCCA subject agents (mathematics + applied_mathematics
  + chemistry + geography + history + english + gaeilge +
  computer_science)
- The 3 educational agents (academic_history_agent +
  celtic_grammar_agent + celtic_morphology_agent)
- The 4 BIEP hackathon features (marking_grader +
  adaptive_tutor + equivalency_generator + curriculum_change_sensor)
- The 1 media_intel pipeline (the 10-tool `media_descriptor_agent`)

## The 7 orchestrator modules (at `tuatha/tuatha/`)

- `config.py` — LiteLLM + Langfuse + Cognee + Letta + BAML clients
- `routing.py` — the SubjectAgentWiring factory + 3 wire registries
- `orchestrator.py` — the TuathaOrchestrator (parallel dispatch)
- `operator.py` — the CianfhoghlaimOperator (single-user)
- `cross_subject.py` — the CrossSubjectSpecialist
- `workflows.py` — the 4 per-subject workflow handlers
- The `__init__.py` re-export surface
