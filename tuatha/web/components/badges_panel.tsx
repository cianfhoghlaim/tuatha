// tuatha.web.components.badges_panel — the student's rung-5 complete badge ledger.
import { useEffect, useState } from "react";
import type { Phase4BadgeRecord } from "../hono-api/types";

export function BadgesPanel({ student_id }: { student_id: string }) {
  const [badges, setBadges] = useState<Phase4BadgeRecord[]>([]);
  useEffect(() => {
    (async () => {
      const r = await fetch(`/api/badges/${student_id}`);
      const d = await r.json();
      setBadges(d.data ?? []);
    })();
  }, [student_id]);
  return (
    <div>
      <h3>Badges ledger</h3>
      {badges.length === 0
        ? <em>no rung-5-complete badges yet</em>
        : <ul>{badges.map((b, i) => (
            <li key={i}>{b.subject} {b.level} (rung5={b.rung5_root.slice(0, 12)}...)</li>
          ))}</ul>}
    </div>
  );
}
