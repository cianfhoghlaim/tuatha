// tuatha.web.components.realm_canvas — the chamber-viewport renderer.
//
// Per the build plan's Hades-framing: each chamber = one question, each
// run = one formative session. This is the 2D viewport that renders the
// chamber + the agent's response + the proof panel.
import { useState, useEffect } from "react";
import { AgentChat } from "./agent_chat";
import { ProofViewer } from "./proof_viewer";

export function RealmCanvas({ student_id, subject, pdf_path, source_page }:
  { student_id: string; subject: string; pdf_path: string; source_page: number }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr" }}>
      <div>
        <h2>chamber: {subject} p.{source_page}</h2>
        <AgentChat student_id={student_id} subject={subject} />
      </div>
      <div>
        <h2>source page</h2>
        <ProofViewer pdf_path={pdf_path} source_page={source_page}
                     answer="(question text rendered from rung-1)" />
      </div>
    </div>
  );
}
