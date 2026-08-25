// tuatha.education.components.mastery — the rung-5-complete mastery unlock view.
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

export function Mastery({ student_id, subject }: { student_id: string; subject: string }) {
  const [progress, setProgress] = useState<{ lo_code: string; rung5_root: string }[]>([]);
  const m = useMutation({
    mutationFn: async () => {
      // Production: GET /api/mastery/:student_id via the Hono backend
      const r = await fetch(`/api/mastery/${student_id}`);
      const d = await r.json();
      setProgress(d.data ?? []);
      return d;
    },
  });
  return (
    <div>
      <h3>mastery: {subject}</h3>
      <button onClick={() => m.mutate()} disabled={m.isPending}>
        {m.isPending ? "loading..." : "load mastery"}
      </button>
      <ul>
        {progress.map((p, i) => (
          <li key={i}>rung 5 unlocked: {p.lo_code} (rung5={p.rung5_root.slice(0, 12)}…)</li>
        ))}
      </ul>
    </div>
  );
}
