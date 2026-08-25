// tuatha.web.components.proof_viewer — the demonstrable-proof surface.
// Per the build plan: a chamber's button says "open the source page" and
// the modal renders the rung-1 PDF page region that grounded the answer.
import { useState } from "react";
import { EvidenceLadder } from "./evidence_ladder";

export function ProofViewer({ pdf_path, source_page, answer }:
  { pdf_path: string; source_page: number; answer: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <p>{answer}</p>
      <button onClick={() => setOpen(!open)}>
        {open ? "hide proof" : "show proof (source page)"}
      </button>
      {open && <EvidenceLadder pdf_path={pdf_path} source_page={source_page} />}
    </div>
  );
}
