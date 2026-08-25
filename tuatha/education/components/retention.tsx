// tuatha.education.components.retention — the spaced-repetition scheduler.
//
// Per the build plan's Hades framing: a chamber closes, but the player
// returns. The retention component renders the upcoming review schedule
// from the rung-5 mastery table (Phase 5).
import { useEffect, useState } from "react";

export function Retention({ student_id }: { student_id: string }) {
  const [queue, setQueue] = useState<{ lo_code: string; next_review: string }[]>([]);
  useEffect(() => {
    (async () => {
      // Production: derive from learner_progress + spaced-repetition algorithm
      const today = new Date();
      setQueue([
        { lo_code: "LC-MATHS-LO-2.4", next_review: today.toISOString().slice(0, 10) },
        { lo_code: "LC-ENGLISH-LO-3.2", next_review: today.toISOString().slice(0, 10) },
      ]);
    })();
  }, [student_id]);
  return (
    <div>
      <h3>review queue</h3>
      <ul>{queue.map((r, i) => <li key={i}>{r.lo_code} → review by {r.next_review}</li>)}</ul>
    </div>
  );
}
