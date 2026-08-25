// tuatha.web.components.evidence_ladder — the 5-rung provenance inspector.
// Per G7: every artefact carries rung 1 (document) + rung 2 (location)
// + rung 3 (extraction) + rung 4 (evaluation) + rung 5 (anchor).
import { useState, useEffect } from "react";

export function EvidenceLadder({ pdf_path, source_page }: { pdf_path: string; source_page: number }) {
  const [rungs, setRungs] = useState<any[]>([]);
  useEffect(() => {
    (async () => {
      // In production: walk all 5 rungs via the Phase 1 DuckDB
      const r = await fetch(`/api/curriculum/${encodeURIComponent("Ireland")}`);
      const d = await r.json();
      setRungs((d.data ?? []).filter((x: any) => x.source_url === pdf_path && x.source_page === source_page));
    })();
  }, [pdf_path, source_page]);
  return (
    <div>
      <h4>Evidence ladder for {pdf_path.split("/").pop()} p.{source_page}</h4>
      <ol>
        {rungs.map((r, i) => (
          <li key={i}>rung {r.rung}: <a href={r.source_url}>{r.source_url.split("/").pop()} p.{r.source_page}</a></li>
        ))}
      </ol>
    </div>
  );
}
