// tuatha.web.components.agent_chat — the canonical subject-agent chat surface.
// Per the Hades framing: each "run" is a chamber, each "turn" is a question.
// Each message carries its rung-1 sha256 + rung-5 root in the response header.
import { useState } from "react";
import type { Phase4ChatResponse, Phase4ChatRequest } from "../hono-api/types";

export function AgentChat({ student_id, subject }: { student_id: string; subject: string }) {
  const [input, setInput] = useState("");
  const [reply, setReply] = useState<Phase4ChatResponse | null>(null);
  const send = async () => {
    const body: Phase4ChatRequest = { student_id, subject, prompt: input };
    const r = await fetch("/api/agent/chat", { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    setReply(await r.json());
  };
  return (
    <div>
      <h3>{subject} chamber (chat)</h3>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={send}>ask</button>
      {reply?.data && (
        <pre>
          EN: {reply.data.reply_en}
GA: {reply.data.reply_ga}
          {"

"}Provenance: rung1={reply.data.provenance.rung1_sha256}
          {"
"}rung5={reply.data.provenance.rung5_root}
        </pre>
      )}
    </div>
  );
}
