// tuatha.education.components.tutor — the persistent tutor session.
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

export function Tutor({ student_id, subject }: { student_id: string; subject: string }) {
  const [history, setHistory] = useState<{ ask: string; reply: string; rung5: string }[]>([]);
  const [input, setInput] = useState("");
  const m = useMutation({
    mutationFn: async (prompt: string) => {
      const r = await fetch("/api/agent/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id, subject, prompt }),
      });
      const d = await r.json();
      return d.data;
    },
    onSuccess: (data) => {
      setHistory(h => [...h, { ask: input,
        reply: data?.reply_en ?? "(no reply)",
        rung5: data?.provenance?.rung5_root ?? "0".repeat(64) }]);
    },
  });
  return (
    <div>
      <h3>tutor: {subject}</h3>
      {history.map((r, i) => (
        <div key={i}>
          <p><strong>ask:</strong> {r.ask}</p>
          <p><strong>reply:</strong> {r.reply}</p>
          <p style={{ fontSize: 10 }}>rung5: {r.rung5}</p>
        </div>
      ))}
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={() => m.mutate(input)} disabled={m.isPending}>
        {m.isPending ? "..." : "ask"}
      </button>
    </div>
  );
}
