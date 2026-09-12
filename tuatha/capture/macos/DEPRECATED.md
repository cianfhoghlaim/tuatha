# `tuatha/capture/macos/` — DEPRECATED

> **Status**: DEPRECATED as of 2026-08-27 (per
> `openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`).
> Do NOT add new files to this directory.

## Why deprecated

The Phase-1 Swift capture daemon in
`tuatha-clean/tuatha/capture/macos/` (647 LOC of Swift —
`Package.swift` + `Daemon.swift` + `Capture.swift` +
`Doctor.swift` + `main.swift` + `LaunchAgent/com.ci.tuatha.capture.plist`)
is deprecated for the following reasons:

### 1. Critical drift between README and code

The README advertises *"1fps keyframes + on-change burst HEVC
clips"* with a frame-diff hash + threshold detector. The
actual `Capture.swift:137-176` writes a **JPEG on every
SCStream sample** (~60fps nominal) — the change-detector
threshold logic is **commented but never implemented**.

### 2. Burst HEVC writer is a stub

The `assetWriter: nil` in `RunState` (Capture.swift:35) means
the burst HEVC clips are never actually written. The README
claim is aspirational only.

### 3. No S3 upload code

The "S3 mirror behind Pangolin" path (Pangolin private
resources) is referenced in the README but no Swift code
performs the upload. The Python `tuatha_capture` package
does NOT contain a daemon client.

### 4. Hermes Agent computer-use is the Phase-2 path

Per the `2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/`
change, the Phase-2 capture path is the **Hermes Agent
computer-use API** at `unsloth.cianfhoghlaim.ie:8889`
(replacing the manual Swift capture daemon). The Hermes
stub lives at `tuatha/tuatha/capture/hermes_client.py`.

## What's preserved

- The git history of the Swift daemon (in
  `tuatha-clean/tuatha/capture/macos/` — that repo still
  exists).
- The `LaunchAgent/com.ci.tuatha.capture.plist` (the only
  artifact worth porting if we ever bring the daemon back).
- The `Doctor.swift` (permissions + encoder checks — useful
  as a future macOS-only smoke test).

## Migration path

For Hades capture in the new `tuatha/` repo:

1. **Phase-1 (today)**: Manual capture via the operator
   running Hades + the Hermes Agent observing the window
   (no daemon required).
2. **Phase-2 (Hermes stub)**: `tuatha/tuatha/capture/hermes_client.py`
   — the Hermes Agent computer-use HTTP client. Wire it up
   to a CI-style pipeline that captures frames on demand.
3. **Phase-3 (if Hermes fails)**: Re-implement the Swift
   daemon with the missing change-detector + HEVC writer +
   S3 uploader. This is a 2-week Swift project, NOT
   recommended given Hermes is the canonical Phase-2 path.

## See also

- `tuatha/tuatha/capture/hermes_client.py` — the Hermes
  Agent stub (the new Phase-2 capture path).
- `tuatha-clean/tuatha/capture/macos/README.md` — the
  original README (preserved for context).
- `openspec/changes/2026-08-27-tuatha-anam-capture-pipeline-port-and-xmen-corpus-v1/tasks.md`
  T0.4 — the deprecation task.
